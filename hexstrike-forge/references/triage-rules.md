# Triage Rules

Apply these rules to every HexStrike flag before assigning a confidence label.

---

## Section 1 — Confidence Labels

Assign **CONFIRM-HIGH** when ALL of the following are true:
- A tool produced a positive match (not just a version match or banner grab)
- You manually verified the condition with at least one follow-up request or check
- The impact is directly demonstrable (data returned, callback received, error triggered)

Assign **CONFIRM-MED** when:
- A tool produced a positive match
- Manual verification was blocked (rate limiting, filtered port, auth required)
- The tool match is high-fidelity (specific template condition, not a generic banner or version range)

Assign **INVESTIGATE** when:
- The signal is promising but unconfirmed (version in range, no PoC executed)
- The tool flag is low-fidelity (heuristic, pattern match, wildcard template)
- Manual follow-up is needed but not yet done

Assign **DISCARD** when:
- The flag matches a known false positive pattern (see Section 4)
- The finding is informational with no exploitable attack path
- Three or more tools flagged the same item and none confirmed it

**Deduplication rule:** if multiple tools confirm the same vulnerability on the same endpoint, that is one CONFIRM finding. List all tool evidence under a single evidence ledger entry.

---

## Section 2 — Chain Detection Rules

After triage, scan for these patterns across all CONFIRM and INVESTIGATE items. When a chain is identified, write one finding describing the full path — individual components become evidence items, not separate findings.

| Pattern | Chain type | Escalation |
|---|---|---|
| Two findings on the same service (port/protocol) | Service chain | Combine into one escalated finding |
| Finding A creates the attack position for Finding B | Attack path chain | A is entry point, B is the escalation |
| SSRF + internal service or metadata endpoint exposure | SSRF to pivot | SSRF becomes Critical if internal services are reachable |
| XSS in admin context + CSRF token bypass | Session hijack chain | Stored XSS + CSRF = account takeover path |
| CVE on service + weak or default config on same service | Exploit + misconfiguration | Combined finding with higher impact narrative |
| Open redirect + OAuth authorization flow | OAuth token theft | Redirect steals the auth code mid-flow |
| Subdomain takeover + any auth or session cookie on root domain | Cookie hijack chain | Takeover allows full session capture |
| Information disclosure (stack trace, debug output) + targeted attack vector | Recon-assisted exploitation | Disclosure reduces attacker effort — note in impact |
| Authentication bypass + any privileged action | Privilege escalation chain | Bypass becomes Critical if admin functions are reachable |
| Path traversal + sensitive file exposure | Traversal to exfil | File read becomes Critical if credentials or keys are exposed |

---

## Section 3 — CISA KEV Cross-Reference

After assigning any CVE-based finding a confidence label, check the CISA KEV live catalog:

**Authoritative source:** `https://www.cisa.gov/known-exploited-vulnerabilities-catalog`

Search the CVE ID directly. Do not rely on a static list in this file — the catalog updates continuously.

**If on KEV:**
- Elevate to priority finding regardless of CVSS score
- Add to the finding: `CISA KEV: YES — active exploitation confirmed in the wild`
- Flag separately in the Executive Summary under "Requires Immediate Remediation"
- Note the KEV due date if the target is a US federal agency (CISA mandates patching within the deadline)

---

## Section 4 — Common False Positives

Discard these immediately:

| Category | Flag | Reason |
|---|---|---|
| TLS | SSL certificate self-signed | Informational on internal/dev targets — only finding if in production |
| TLS | SSL certificate expired | Informational — not exploitable on its own |
| Technology | Any technology detection result | Tech detection is fingerprinting, not a vulnerability |
| Headers | X-Frame-Options not set | Only a finding if clickjacking is in scope and the page has sensitive actions |
| Headers | Missing security headers (CSP, HSTS, etc.) | Informational unless the program explicitly accepts header findings |
| Headers | HTTP OPTIONS method enabled | Only a finding if TRACE is enabled or it reveals sensitive methods |
| Cookies | Missing HttpOnly or Secure flag | Only a finding if the cookie is a session token and XSS is confirmed |
| Ports | `open\|filtered` port state from nmap | Ambiguous — do not treat as confirmed open |
| Version | Version number in banner matches vulnerable range | Version in range does not equal confirmed vulnerability — requires PoC |
| Robots.txt | Sensitive paths listed in robots.txt | Informational — confirms paths exist, not that they are exploitable |
| Directory listing | Empty directory listing | No exploitable content = discard |
| CORS | CORS allows all origins (`*`) on a public API | Only a finding if the API carries authenticated data |
| DNS | SPF/DMARC misconfiguration | Email security issue — only in scope if program explicitly accepts it |

---

## Section 5 — Evidence Ledger Format

Create one entry per CONFIRM item as it is found. Do not reconstruct evidence at Phase 4.

```
### EV-001
- Tool: <tool name>
- Check: <CVE ID, template name, or test description>
- Output: <key lines from stdout>
- Timestamp: <ISO 8601>
- Confidence: CONFIRM-HIGH | CONFIRM-MED
- KEV: YES | NO
- Chain: <linked EV-ID if part of a chain, else none>
```

---

## Section 6 — Finding Template (fallback if finding-writer not installed)

```
**Title:** <vuln class> in <component> via <vector> leads to <impact>
**Severity:** Critical | High | Medium | Low
**CVSS 3.1:** <score> (<vector string>)
**CISA KEV:** YES — active exploitation in the wild | NO
**OWASP:** <Top 10 category, e.g. A01:2021 Broken Access Control>
**CWE:** <CWE-ID — name>
**Description:** <what it is and why it is exploitable>
**Evidence:** <tool name, template/check, key lines from stdout>
**Steps to Reproduce:**
1. <step>
2. <step>
**Impact:** <business impact — data exposed, actions possible, blast radius>
**Remediation:** <specific fix with version or config change>
**References:** <CVE link, CWE link, OWASP link>
```
