# Framing Headers Reference

## X-Frame-Options

| Value | Effect | Browser support |
|---|---|---|
| `DENY` | Blocks all framing, including same-origin | All modern browsers |
| `SAMEORIGIN` | Allows framing from same origin only | All modern browsers |
| `ALLOW-FROM uri` | Allows framing from specified URI | **Deprecated** — ignored by Chrome, Firefox, Safari |

> XFO is superseded by CSP `frame-ancestors` in all modern browsers. If both are set, `frame-ancestors` wins.

---

## CSP frame-ancestors

| Value | Effect |
|---|---|
| `frame-ancestors 'none'` | Blocks all framing — equivalent to XFO: DENY |
| `frame-ancestors 'self'` | Same origin only — equivalent to XFO: SAMEORIGIN |
| `frame-ancestors https://trusted.com` | Specific origin allowed |
| `frame-ancestors 'self' https://trusted.com` | Same origin + specific external origin |

Set via: `Content-Security-Policy: frame-ancestors 'none'`

Preferred over XFO — more flexible, better browser support, takes precedence.

---

## Browser Behavior Matrix

| Browser | XFO: DENY | XFO: ALLOW-FROM | CSP frame-ancestors |
|---|---|---|---|
| Chrome | Enforced | Ignored | Enforced |
| Firefox | Enforced | Partially | Enforced |
| Safari | Enforced | Ignored | Enforced |
| Edge | Enforced | Ignored | Enforced |
| IE 11 | Enforced | Enforced | Partial |

---

## JavaScript Frame-Busting Patterns

Weak protection — bypassable with `sandbox` attribute on the iframe.

| Pattern | What it does |
|---|---|
| `if (top !== self) top.location = self.location` | Redirects top window to current page |
| `if (window.top !== window.self) window.top.location.replace(...)` | Same, using replace |
| `if (parent.frames.length > 0) top.location = self.location` | Checks for parent frames |
| `frameElement !== null` | Detects if page is in a frame |

**Bypass**: add `sandbox="allow-scripts allow-forms allow-same-origin"` to the iframe — omitting `allow-top-navigation` blocks all `top.location` navigation.

---

## sandbox Attribute Values

| Value | Effect |
|---|---|
| `allow-scripts` | Enables JS execution in the frame |
| `allow-forms` | Enables form submission |
| `allow-same-origin` | Preserves origin (needed for session cookies) |
| `allow-top-navigation` | Allows JS to navigate top window — **omit this to block frame-busting** |
| `allow-popups` | Allows window.open() |

Minimum needed to load a target page with session: `sandbox="allow-scripts allow-forms allow-same-origin"`

---

## Header Detection Commands

```bash
# Single page check
curl -sI https://target.com/page | grep -i "x-frame-options\|content-security-policy"

# Bulk check across paths
for p in / /settings /delete /transfer /admin; do
  echo -n "$p: "
  curl -sI "https://target.com$p" | grep -i "x-frame-options\|frame-ancestors" | tr -d '\r' || echo "NONE"
done

# Extract only the frame-ancestors directive from CSP
curl -sI https://target.com/ | grep -i "content-security-policy" | grep -o "frame-ancestors[^;]*"
```
