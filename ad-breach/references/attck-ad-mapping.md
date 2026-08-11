# MITRE ATT&CK Mapping for Active Directory Findings

Reference for tagging AD Breach findings to MITRE ATT&CK for Enterprise techniques, with severity context and remediation guidance. Use this to fill the ATT&CK column in Phase 9 report tables.

---

## Credential Access

### T1558.001: Golden Ticket
**Finding:** krbtgt hash obtained (via DCSync or LSASS dump on a DC) or evidence of an existing golden ticket in use.
**Severity:** Critical
**Remediation:** Rotate the krbtgt password twice (with replication delay between rotations), audit for anomalous TGTs with implausible lifetimes or unusual group SIDs in the PAC.

### T1558.002: Silver Ticket
**Finding:** Service account NTLM hash obtained and usable to forge service tickets without contacting the KDC.
**Severity:** High
**Remediation:** Rotate the affected service account password, enable Kerberos armoring (FAST) where possible, monitor for TGS-REQ without a preceding AS-REQ from the same principal.

### T1558.003: Kerberoasting
**Finding:** Service account with `servicePrincipalName` set, TGS ticket requested and cracked offline.
**Severity:** Critical if account is privileged, High otherwise
**Remediation:** Use Group Managed Service Accounts (gMSA) with 120+ character random passwords, or enforce AES-only Kerberos encryption and long random passwords on legacy service accounts.

### T1558.004: AS-REP Roasting
**Finding:** Account with `Do not require Kerberos preauthentication` set, AS-REP captured and cracked offline.
**Severity:** Critical if account is privileged, High otherwise
**Remediation:** Re-enable Kerberos pre-authentication on every account unless there is a documented, reviewed reason not to.

### T1552.001: Credentials in Files (GPP cpassword)
**Finding:** `cpassword` attribute found in a Group Policy Preferences XML file on SYSVOL, decryptable with the public Microsoft AES key.
**Severity:** Critical
**Remediation:** Apply MS14-025, delete legacy GPP files containing cpassword, rotate any password ever stored this way.

### T1003.006: DCSync
**Finding:** Principal holds `Replicating Directory Changes` + `Replicating Directory Changes All` extended rights without being a legitimate DC or intentionally delegated (e.g. Azure AD Connect).
**Severity:** Critical
**Remediation:** Remove the replication rights from any non-DC, non-explicitly-authorized principal; audit `4662` events for replication requests from unexpected sources.

### T1003.001: LSASS Memory
**Finding:** Local admin access on a host allows LSASS dumping (`secretsdump.py`, `mimikatz sekurlsa::logonpasswords`) to recover cached credentials.
**Severity:** High
**Remediation:** Enable Credential Guard, restrict local admin sprawl, deploy LSA Protection (RunAsPPL).

---

## Persistence

### T1098: Account Manipulation (dangerous ACEs)
**Finding:** Non-privileged principal holds `GenericAll`/`GenericWrite`/`WriteDacl`/`WriteOwner`/`ForceChangePassword`/`AddMember` on a privileged object.
**Severity:** Critical if target is a Tier-0 object (DA/EA/krbtgt/DC computer), High otherwise
**Remediation:** Remove the excess ACE, implement Tiered Administration, enable AdminSDHolder protection review.

### T1098.001: Additional Cloud/Domain Credentials (Shadow Credentials)
**Finding:** `msDS-KeyCredentialLink` attribute added to a user/computer object by a non-owner, enabling PKINIT authentication without a password change.
**Severity:** Critical
**Remediation:** Audit `msDS-KeyCredentialLink` writes via `5136` directory service change events, restrict write access to this attribute.

### T1207: Rogue Domain Controller (DCShadow)
**Finding:** Evidence of unauthorized DC registration or replication metadata changes not attributable to a legitimate DC.
**Severity:** Critical
**Remediation:** Restrict `Domain Controllers` OU membership, monitor for new `nTDSDSA` objects, alert on replication from unregistered sources.

### T1207: DSRM Account Backdoor
**Finding:** DSRM (Directory Services Restore Mode) local administrator account has `DsrmAdminLogonBehavior` set to allow network logon, and/or its password has been synchronized to a known value.
**Severity:** High
**Remediation:** Set `DsrmAdminLogonBehavior` to 0 (default), rotate the DSRM password regularly and treat it as a Tier-0 credential.

### T1484.002: SID-History Injection
**Finding:** Account has SID History entries pointing to a privileged group (`Domain Admins`, `Enterprise Admins`) outside a documented, time-bound domain migration.
**Severity:** Critical
**Remediation:** Strip unauthorized SID History with `ADSI Edit`/`Set-ADUser -remove`, enable SID Filtering on all trusts.

---

## Privilege Escalation / Lateral Movement

### T1484.001: Group Policy Modification
**Finding:** Writable GPO linked to an OU containing privileged users/computers.
**Severity:** Critical
**Remediation:** Restrict GPO edit rights to Tier-0 admins, audit `5136` events on GPO objects.

### T1187: Forced Authentication Coercion (PetitPotam/PrinterBug/DFSCoerce)
**Finding:** MS-EFSRPC/MS-RPRN/MS-DFSNM endpoints reachable and unpatched, allowing a machine account to be coerced into authenticating to an attacker-controlled listener.
**Severity:** Critical when combined with unconstrained delegation or NTLM relay to AD CS/LDAP
**Remediation:** Disable the print spooler on DCs, patch MS-EFSRPC (KB5005413 mitigations), enable EPA/signing on LDAP and AD CS web enrollment.

### T1134.001: Unconstrained Delegation Abuse
**Finding:** Computer object has `TRUSTED_FOR_DELEGATION` (userAccountControl flag) set, allowing any authenticating principal's TGT to be cached and reused.
**Severity:** Critical
**Remediation:** Migrate to constrained delegation or RBCD, place unconstrained-delegation hosts in the `Protected Users` scope where possible, patch coercion vectors.

### T1134.001: Constrained Delegation / RBCD Abuse
**Finding:** `msDS-AllowedToDelegateTo` set on an account the attacker controls, or `msDS-AllowedToActOnBehalfOfOtherIdentity` writable by the attacker.
**Severity:** High to Critical depending on the delegation target
**Remediation:** Minimize delegation scope, restrict `GenericWrite` on computer objects, monitor S4U2Self/S4U2Proxy usage (event `4769` with delegation flags).

### T1649: Steal or Forge Authentication Certificates (ESC1-ESC8)
**Finding:** AD CS template or CA misconfiguration (see `ad-attack-patterns.md` for the full ESC1-ESC8 table) allows certificate-based impersonation of a privileged account.
**Severity:** Critical
**Remediation:** Reconfigure vulnerable templates (require manager approval, restrict enrollable SAN), remove `EDITF_ATTRIBUTESUBJECTALTNAME2`, enforce HTTPS + Extended Protection for Authentication on CA web enrollment.

### T1550.002: Pass the Hash
**Finding:** NTLM hash obtained (via LSASS dump, SAM dump, or NTDS.dit) usable for authentication without cracking.
**Severity:** High to Critical depending on account privilege
**Remediation:** Enable Credential Guard, restrict NTLM where possible (prefer Kerberos-only), enforce Local Admin Password Solution (LAPS) to prevent hash reuse across hosts.

### T1552.006: LAPS Password Disclosure
**Finding:** Non-privileged principal has read access to `ms-Mcs-AdmPwd` / `msLAPS-Password`.
**Severity:** Critical (local admin on the affected host)
**Remediation:** Restrict the LAPS read ACL to the intended admin group only, audit `4662` for reads of the LAPS attribute.

---

## Discovery

### T1087.002: Domain Account Discovery / BloodHound Collection
**Finding:** Full LDAP enumeration or SharpHound/bloodhound-python collection completed, revealing the domain's attack-path graph.
**Severity:** Informational (this is the assessment methodology, not a target finding). Note if collection was possible with only a low-privileged account, as this indicates no LDAP hardening/deception is in place.
**Remediation:** Consider deploying deception objects (honey users/groups) and monitoring for anomalous LDAP query volume from a single principal (SharpHound/BloodHound detection).

### T1069.002: Domain Trust Discovery
**Finding:** Cross-forest or cross-domain trust enumerated with transitive, bidirectional configuration and SID history enabled.
**Severity:** Medium to High depending on the trusted domain's security posture
**Remediation:** Set trusts to non-transitive where business need allows, enable SID Filter Quarantining on all external/forest trusts.
