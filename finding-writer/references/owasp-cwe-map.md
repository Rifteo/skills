# OWASP Top 10 → CWE Mapping

Quick reference for tagging findings with the correct CWE ID and OWASP category.

## OWASP Top 10 (2021)

| OWASP Category | Common CWEs | Typical Findings |
|---|---|---|
| A01 – Broken Access Control | CWE-284, CWE-285, CWE-639, CWE-862 | IDOR, missing authorization checks, path traversal, privilege escalation |
| A02 – Cryptographic Failures | CWE-311, CWE-312, CWE-326, CWE-327, CWE-328 | Sensitive data in plaintext, weak algorithms (MD5/SHA1), hardcoded secrets |
| A03 – Injection | CWE-89 (SQLi), CWE-79 (XSS), CWE-78 (OS cmd), CWE-917 (EL), CWE-77 | SQL injection, XSS, command injection, SSTI, LDAP injection |
| A04 – Insecure Design | CWE-209, CWE-602, CWE-841 | Missing threat modeling, business logic flaws, insufficient controls by design |
| A05 – Security Misconfiguration | CWE-16, CWE-611, CWE-732 | Default credentials, verbose errors, open cloud storage, XXE, permissive CORS |
| A06 – Vulnerable Components | CWE-1035, CWE-937 | Outdated libraries with known CVEs, unpatched dependencies |
| A07 – Auth & Session Failures | CWE-287, CWE-307, CWE-384, CWE-613 | Weak passwords, missing MFA, session fixation, insecure token storage |
| A08 – Software & Data Integrity | CWE-502, CWE-494, CWE-345 | Insecure deserialization, unsigned updates, CI/CD pipeline injection |
| A09 – Logging & Monitoring Failures | CWE-223, CWE-778 | No audit logs, logs containing sensitive data, no alerting on failures |
| A10 – SSRF | CWE-918 | Internal service access via user-supplied URLs, cloud metadata endpoint access |

## Other Common CWEs

| CWE | Name | Typical Context |
|---|---|---|
| CWE-22 | Path Traversal | File read/write outside intended directory |
| CWE-200 | Information Exposure | Stack traces, internal paths, version banners |
| CWE-352 | CSRF | State-changing requests without anti-CSRF token |
| CWE-400 | Uncontrolled Resource Consumption | Missing rate limiting, ReDoS |
| CWE-434 | Unrestricted File Upload | Uploading webshells or malicious files |
| CWE-601 | Open Redirect | Redirecting users to attacker-controlled URLs |
| CWE-611 | XXE | XML external entity injection |
| CWE-614 | Sensitive Cookie without Secure Flag | Cookie transmitted over HTTP |
| CWE-1004 | Sensitive Cookie without HttpOnly | Cookie accessible via JavaScript |

## Usage

In the **References** field of a finding, format as:

```
CWE-89 | OWASP A03:2021 – Injection
```

Or for a CVE:

```
CVE-2021-44228 | CWE-917 | OWASP A03:2021 – Injection
```
