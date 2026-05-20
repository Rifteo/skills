# Vulnerability Chain Signals

When you confirm a finding, always check the companion bugs below before reporting. A low-severity standalone bug that chains to a critical finding is worth more submitted together than as two separate reports.

---

## Signal Table

| Confirmed finding (A) | Check next (B) | Why |
|---|---|---|
| IDOR on GET endpoint | Test PUT/DELETE same path | Read-only IDOR often pairs with write access on the same object |
| Stored XSS | Does an admin or privileged user view it? | Stored XSS viewed by admin = account takeover or CSRF bypass |
| Reflected XSS via parameter | Is there a CSRF token in the response? | Token in DOM + XSS = CSRF bypass, session hijack |
| Open redirect confirmed | Can it be used as OAuth redirect_uri? | redirect_uri bypass via open redirect = auth code theft |
| SSRF with DNS callback | Can it reach internal services (169.254.x, 10.x)? | Blind SSRF upgrades to cloud metadata or internal API access |
| File upload accepted | Test for SSTI/RCE via template extensions | .ssti, .phtml, .php extensions often missed in extension blocklists |
| SQLi confirmed (read) | Test UPDATE/INSERT, stacked queries | Read SQLi frequently pairs with write access |
| Password reset flow | Is the token in the URL? | Token in URL = Referer header leakage to analytics |
| Rate limiting via IP | Try X-Forwarded-For / X-Real-IP rotation | Header-based rate limits are trivially bypassed |
| Exposed S3 bucket listing | Grep JS bundles in bucket for secrets | Public bucket listing + JS bundles = API keys, OAuth secrets |
| Subdomain takeover | Is it used in any CSP, CORS, or OAuth allowlist? | Taken subdomain in allowlist = full CSP bypass or CORS wildcard exploitation |
| CORS misconfiguration | Does it reflect credentials (Access-Control-Allow-Credentials: true)? | Credentialed CORS = session hijack from any reflected origin |
| SAML assertion processing | Test signature wrapping and XXE in assertion | SAML parsers often vulnerable to both simultaneously |
| JWT with alg:HS256 | Is the public key accessible? | Public key as HMAC secret = signature forgery |
| LLM chatbot access | Test indirect prompt injection via user-controlled data | Chatbot reading attacker-controlled content = IDOR or data exfiltration via AI |
| Host header reflection | Test X-Forwarded-Host, X-Host, X-Forwarded-Server | Same reflection, different header = cache poisoning or password reset hijack |
| GraphQL introspection enabled | Enumerate mutations and test authorization on each | Introspection exposes hidden write operations often lacking access control |

---

## Chain Examples

**Chain 1: IDOR to account takeover**
```
GET /api/user/1234/profile → read another user's profile (IDOR)
PUT /api/user/1234/email → change their email (write IDOR)
POST /auth/password-reset → reset with new email → account takeover
```

**Chain 2: Open redirect to OAuth token theft**
```
Confirm open redirect: /redirect?url=https://attacker.com
Find OAuth flow with redirect_uri validation
Use redirect_uri=https://target.com/redirect?url=https://attacker.com
Auth code delivered to attacker via open redirect
```

**Chain 3: Stored XSS to admin account takeover**
```
Store XSS payload in profile field
Admin reviews flagged profile in moderation queue
XSS fires in admin context: fetch /api/admin/create-user
New admin account created with attacker credentials
```

**Chain 4: SSRF to AWS credential theft**
```
SSRF confirmed with DNS callback
Pivot to http://169.254.169.254/latest/meta-data/iam/security-credentials/
Retrieve IAM role name, then fetch credentials
AWS access key + secret = full cloud account compromise
```

**Chain 5: Exposed S3 to secret extraction**
```
S3 bucket listing enabled: s3.amazonaws.com/target-assets/
Download JS bundles from bucket
grep for client_secret, api_key, Authorization
OAuth client secret extracted = impersonate app
```

**Chain 6: Subdomain takeover to CSP bypass**
```
Subdomain takeover on cdn.target.com (unclaimed S3/GitHub Pages)
Check target.com CSP: script-src 'self' cdn.target.com
Host attacker JS on cdn.target.com
CSP allows it - XSS with full script execution on target.com
```

---

## How to Use This Table

1. After confirming any finding, scan the "Confirmed finding" column for your bug type.
2. Run the suggested "Check next" test before writing the report.
3. If the chain confirms, submit the full chain as one report with combined impact - programs pay for the chain, not the parts.
4. If the chain does not confirm, note in the report that companion bugs were tested and ruled out. This strengthens credibility.
