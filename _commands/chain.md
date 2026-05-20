Given this confirmed finding: $ARGUMENTS

Check the chain signal table below and identify every companion bug worth testing. For each match, state what to test and why it chains.

## Signal Table

| Confirmed (A) | Check next (B) |
|---|---|
| IDOR on GET endpoint | Test PUT/DELETE same path |
| Stored XSS | Does an admin or privileged user view it? |
| Reflected XSS via parameter | Is there a CSRF token in the response? |
| Open redirect confirmed | Can it be used as OAuth redirect_uri? |
| SSRF with DNS callback | Can it reach internal services (169.254.x, 10.x)? |
| File upload accepted | Test for SSTI/RCE via template extensions |
| SQLi confirmed (read) | Test UPDATE/INSERT, stacked queries |
| Password reset flow | Is the token in the URL? |
| Rate limiting via IP | Try X-Forwarded-For / X-Real-IP rotation |
| Exposed S3 bucket listing | Grep JS bundles in bucket for secrets |
| Subdomain takeover | Is it used in any CSP, CORS, or OAuth allowlist? |
| CORS misconfiguration | Does it reflect credentials (Access-Control-Allow-Credentials: true)? |
| SAML assertion processing | Test signature wrapping and XXE in assertion |
| JWT with alg:HS256 | Is the public key accessible? |
| LLM chatbot access | Test indirect prompt injection via user-controlled data |
| Host header reflection | Test X-Forwarded-Host, X-Host, X-Forwarded-Server |
| GraphQL introspection enabled | Enumerate mutations and test authorization on each |

For each matching signal: describe the exact test to run, what a positive result looks like, and what the combined severity would be if the chain confirms.
