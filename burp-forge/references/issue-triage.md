# Burp Issue Triage Guide

Burp rates every finding on two axes: **Severity** (High/Medium/Low/Info) and **Confidence** (Certain/Firm/Tentative). Use both together — severity alone is not enough.

---

## Triage Decision Matrix

| Confidence | Severity | Decision | Action |
|---|---|---|---|
| Certain | High / Critical | CONFIRM | Write up immediately |
| Certain | Medium | CONFIRM | Write up |
| Certain | Low | DISCARD | Unless it chains to a higher finding |
| Certain | Information | DISCARD | Note only |
| Firm | High | INVESTIGATE | Manual verify in Repeater — expect ~70% confirmation rate |
| Firm | Medium | INVESTIGATE | Manual verify — expect ~50% confirmation rate |
| Firm | Low | DISCARD | Not worth the time |
| Tentative | Any | INVESTIGATE | Assume false positive — only promote if you can reproduce impact |

---

## Common Burp False Positives

These Burp findings are frequently wrong. Verify before reporting.

| Burp Issue | Why it's often a FP | How to verify |
|---|---|---|
| "SQL injection" (Tentative) | Burp detects timing delays that can have other causes | Manually extract a row: `' UNION SELECT NULL,NULL--` |
| "Reflected XSS" | Reflection ≠ execution. WAF may strip on render | Execute `<img src=x onerror=alert(1)>` in browser |
| "CSRF" | Many modern frameworks have CSRF protection Burp doesn't detect | Submit the CSRF PoC manually — does it succeed? |
| "Password submitted over HTTP" | May be a redirect to HTTPS before submission | Check the actual transport, not just the form action |
| "TLS certificate" issues | May be intentional on internal/dev hosts | Confirm it's a production target |
| "Cacheable HTTPS response" | Not a finding without sensitive data in the response | Check response body for actual sensitive content |
| "Path traversal" (Tentative) | Path normalization often blocks this | Attempt to read `/etc/passwd` or `win.ini` |
| "Open redirection" | Burp flags redirects to same domain | Confirm redirect to external domain you control |

---

## Deduplication Rules

Burp logs the same issue multiple times across endpoints. Merge before reporting.

**Same issue, different parameters on same endpoint = one finding**
- `?id=1` and `?user=1` both have SQLi on `/api/search` → one finding, list both parameters

**Same issue, different endpoints = separate findings**
- SQLi on `/api/search` and SQLi on `/api/export` → two findings (different fix required)

**Same issue found by scanner AND by manual testing = one finding**
- Use manual test evidence as primary (more precise), reference Burp scan as secondary confirmation

---

## Rewriting Burp Issue Titles

Burp titles are generic. Rewrite every title before passing to `finding-writer`.

| Burp Title | Rewritten Title |
|---|---|
| Cross-site scripting (reflected) | Reflected XSS in `q` Parameter Allows Session Cookie Theft |
| SQL injection | SQL Injection in `/api/search` Endpoint Allows Full Database Extraction |
| Cross-site request forgery | CSRF on Password Change Endpoint Allows Account Takeover |
| Open redirection (reflected) | Open Redirect on `/login?next=` Enables Phishing via Trusted Domain |
| Cleartext password submission | Login Credentials Transmitted Over Unencrypted HTTP |
| Clickjacking | Missing X-Frame-Options Allows UI Redress on `/transfer` Page |

**Formula:** [Vuln type] in [specific location] [enables/allows/exposes] [concrete impact]
