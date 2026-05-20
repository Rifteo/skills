# References

## Chain Signals

- [chain-signals.md](chain-signals.md) - 17 A→B companion bug mappings and 6 escalation chain examples

## Hunt Workflow

- [hunt-workflow.md](hunt-workflow.md) - 7-phase structured engagement workflow (SCOPE→RECON→RANK→HUNT→VALIDATE→REPORT→CHECKPOINT)

## Disclosed Report Patterns

Patterns extracted from public bug bounty disclosures on HackerOne and Bugcrowd, organized by vulnerability class.

| File | Reports | Coverage |
|---|---|---|
| [xss.md](disclosed-patterns/xss.md) | 174 | Stored, reflected, DOM, sanitizer bypass, CSP evasion, mXSS |
| [rce.md](disclosed-patterns/rce.md) | 67 | Config injection, deserialization, dependency confusion, path traversal |
| [idor.md](disclosed-patterns/idor.md) | 26 | Integer ID, UUID, verb inconsistency, GraphQL, parameter pollution |
| [oauth.md](disclosed-patterns/oauth.md) | 10 | redirect_uri, state CSRF, referrer leakage, token theft |
| [ssrf.md](disclosed-patterns/ssrf.md) | 9 | Cloud metadata, Kubernetes, redirect bypass, protocol confusion |
| [sqli.md](disclosed-patterns/sqli.md) | 8 | Time-based blind, error-based, header injection, WAF bypass |
| [business-logic.md](disclosed-patterns/business-logic.md) | 7 | Price manipulation, rate-limit bypass, verification skip |
| [xxe.md](disclosed-patterns/xxe.md) | 4 | SAML, file upload, OOB exfiltration, SSRF pivot |
| [cache-poison.md](disclosed-patterns/cache-poison.md) | - | Unkeyed headers, web cache deception, smuggling chain |
| [http-smuggling.md](disclosed-patterns/http-smuggling.md) | - | H2.CL, H2.TE, HAProxy, impact chains |
