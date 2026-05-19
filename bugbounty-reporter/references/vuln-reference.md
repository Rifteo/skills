# Vulnerability Reference — Risk & Remediation by Class

Quick lookup for Risk statements and Remediation guidance per vulnerability class.

---

## Risk Statements

| Vuln Class | Risk Statement |
|---|---|
| IDOR (read) | An attacker can read [data type] belonging to any user without authorization. |
| IDOR (write/delete) | An attacker can modify or delete [data type] belonging to any user. |
| Stored XSS | Arbitrary JavaScript executes in any visitor's browser — enabling session theft, credential harvesting, or redirection to a phishing page. |
| Reflected XSS | JavaScript executes in the victim's browser via a crafted link — enabling session theft or account takeover with user interaction. |
| SQLi (read) | An attacker can extract the full database contents including credentials, PII, and session tokens. |
| SQLi (write) | An attacker can modify or delete any database record. |
| SSRF | An attacker can reach internal services or cloud metadata endpoints (169.254.169.254), potentially stealing IAM credentials. |
| Auth bypass | An attacker can access any account or admin panel without valid credentials. |
| RCE | An attacker gains full control of the server — code execution, data access, and lateral movement. |
| CSRF | Any state-changing action can be performed silently on behalf of a logged-in victim. |
| Open redirect | Users can be redirected to an attacker-controlled domain via a trusted link, enabling phishing. |
| Clickjacking | Sensitive UI actions can be triggered invisibly by embedding the page in an attacker-controlled iframe. |
| JWT weakness | An attacker can forge arbitrary JWT claims — including elevated roles — by exploiting algorithm confusion or a weak secret. |
| Insecure file upload | An attacker can upload malicious files — enabling stored XSS, path traversal, or server-side execution depending on how files are processed. |
| Business logic | [Describe the specific impact — price manipulation, workflow bypass, etc. — in concrete terms for this finding.] |

---

## Remediation by Class

| Vuln Class | Remediation |
|---|---|
| IDOR | Verify on every request that the authenticated user owns the requested resource. Compare resource `owner_id` against the session user ID at the service layer, not just routing. |
| Stored XSS | Output-encode all user-supplied content before rendering in HTML context. Implement `Content-Security-Policy: script-src 'self'` to block inline execution. |
| Reflected XSS | Output-encode reflected parameters. Add CSP. Avoid rendering user input as HTML. |
| SQLi | Use parameterized queries or prepared statements throughout. Never concatenate user input into SQL strings. |
| SSRF | Allowlist outbound destinations. Block RFC 1918 ranges and link-local (169.254.x.x). Reject non-HTTP(S) schemes in URL parameters. |
| Auth bypass | Enforce session validation and role checks at every protected endpoint — not just the entry route. |
| RCE | Avoid executing user input as system commands. Use safe APIs. Run the application process with least privilege. |
| CSRF | Set `SameSite=Strict` on session cookies. Validate a CSRF token on all state-changing requests. |
| Open redirect | Validate redirect targets against an allowlist of trusted domains. Reject or encode user-supplied URLs. |
| Clickjacking | Add `Content-Security-Policy: frame-ancestors 'none'` and `X-Frame-Options: DENY` to all sensitive pages. |
| JWT weakness | Enforce the expected algorithm server-side — never accept `alg: none`. Use a strong secret (≥256-bit) or asymmetric keys. Validate all claims including `exp` and `aud`. |
| Insecure file upload | Validate file type by content (magic bytes), not extension. Store uploads outside the web root. Serve via a separate domain or CDN with no script execution. |
