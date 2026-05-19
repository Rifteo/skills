# Severity Guide & Platform Notes

---

## Severity Criteria

Don't inflate or deflate — triagers reject both.

| Severity | Typical criteria |
|---|---|
| **Critical** | Unauthenticated RCE, pre-auth SQLi with full DB dump, auth bypass to admin, cloud credential theft via SSRF, account takeover without interaction |
| **High** | Authenticated RCE, stored XSS → ATO, IDOR exposing PII at scale, SSRF reaching internal services, vertical privilege escalation |
| **Medium** | Reflected XSS, IDOR on non-sensitive data, CSRF on sensitive action, horizontal privilege escalation with limited data exposure |
| **Low** | Open redirect, clickjacking on low-value page, missing security header without direct exploitability, verbose error messages |
| **Info** | Best practice issue, no direct exploitability, theoretical risk only |

### Adjustments

Increase severity when:
- Target handles PII, payment data, or health records
- Finding is unauthenticated or pre-auth
- Public PoC or active exploitation exists in the wild

Decrease severity when:
- Exploitation requires a highly privileged starting position
- Compensating controls (MFA, WAF, network segmentation) meaningfully reduce likelihood
- Impact is limited to the attacker's own account

---

## CVSS Quick Reference

Use `scripts/cvss-scorer.py` to compute the full vector. Key metrics:

| Metric | Options | Notes |
|---|---|---|
| AV (Attack Vector) | N/A/L/P | N = network (most common for web) |
| AC (Complexity) | L/H | L = no special conditions required |
| PR (Privileges Required) | N/L/H | N = unauthenticated |
| UI (User Interaction) | N/R | R = victim must click a link |
| S (Scope) | U/C | C = impact crosses security boundaries |
| C/I/A | N/L/H | Confidentiality, Integrity, Availability impact |

---

## Duplicate Check

Check before submitting — duplicates waste everyone's time and damage your reputation.

1. Search the program's disclosed reports on the platform for your vulnerability class and endpoint
2. Search the program's Hall of Fame / resolved reports if accessible
3. On HackerOne: use the "similar reports" suggestion shown during submission
4. On Bugcrowd: check the VRT for known excluded issue types
5. If uncertain: submit anyway but note "I checked for duplicates and found none"

---

## Platform Notes

| Platform | Key notes |
|---|---|
| **HackerOne** | Markdown supported. Attach screenshots inline. CVSS optional but appreciated. Use the "Impact" field for the Risk section. |
| **Bugcrowd** | Map your finding to a VRT (Vulnerability Rating Taxonomy) category — include it in your title or description. Severity is set by the program, not you. |
| **Intigriti** | Has structured fields: Description, Reproduction, Impact, Recommendation — keep each section focused. CVSS score field present. |
| **YesWeHack** | Fill the CVSS score field. Use the "Proof" field for your PoC. Clear reproduction steps are weighted heavily in triage. |
| **Private programs** | Follow their template if provided. When in doubt, use this skill's structure — it covers all standard fields. |

---

## Common Rejection Reasons

Fix these before submitting:

| Rejection reason | Prevention |
|---|---|
| Can't reproduce | Add a fresh curl command. Test your own steps in a clean session before submitting. |
| Duplicate | Do the duplicate check above. |
| Out of scope | Re-read the program's scope list. Asset must be explicitly in scope. |
| Not a vulnerability | Self-XSS, clickjacking on logout page, missing headers with no exploit path — check program's exclusion list. |
| Insufficient impact | Add a concrete attack scenario. "Could lead to" is weak — "allows an attacker to read all customer PII" is strong. |
| N/A — HttpOnly blocks XSS | State what IS achievable: DOM manipulation, phishing, redirect, keylogging without cookies. |
