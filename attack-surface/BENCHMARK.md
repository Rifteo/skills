---
skill: attack-surface
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: attack-surface
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Partial | Good | 🟢 +1 level(s) |
| Turns to complete | 1 | 1 | ⚪ 0 |
| Response tokens | ~4,039 | ~2,562 | 🟢 -37% |
| Total time | 88s | 56s | 🟢 -36% |
| User effort | Low | Low | ⚪ Low |

## Scenario

Pentester starts a graybox engagement, gives context casually — needs a structured attack surface map

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded.

### Turn 1

**Prompt**

starting a graybox pentest on an e-commerce company, they have app.acmecorp.com, a REST API and an admin dashboard. stack is react + nodejs + postgres, JWT RS256 auth with google SSO and MFA. they use stripe for payments, sendgrid for emails and cloudflare in front. iOS/Android mobile app too. where do i start and what's my attack surface?

**Response**

# Gray Box Pentest: ACMECorp E-Commerce Attack Surface

## Initial Orientation

Gray box means you likely have: some API docs, maybe source snippets, valid user accounts, and architecture knowledge. Use all of it - don't pretend you're black box testing.

---

## Attack Surface Map

### 1. Authentication & Session Layer (Start Here)

This is your highest-value target given the complexity.

```
JWT RS256 + Google SSO + MFA = multiple interaction points, each with failure modes
```

**JWT-Specific Attacks:**

```bash
# Algorithm confusion: RS256 → HS256
# Take the public key, sign a token with it as HMAC secret
# Many libraries accept both if misconfigured

# Grab the public key (often exposed)
curl https://app.acmecorp.com/.well-known/jwks.json
curl https://app.acmecorp.com/api/auth/public-key

# Tool: jwt_tool
python3 jwt_tool.py <token> -X a  # algorithm confusion
python3 jwt_tool.py <token> -X s  # self-signed (none algorithm)
python3 jwt_tool.py <token> -I -pc role -pv admin  # claim injection

# Check for 'none' algorithm acceptance
# Decode header, change alg to "none", remove signature, keep trailing dot
echo '{"alg":"none","typ":"JWT"}' | base64 | tr -d '='
```

**SSO-Specific Attacks:**

```
OAuth/OIDC flow attacks:
- redirect_uri validation bypass (subdomain takeover, path traversal)
- state parameter CSRF
- nonce replay
- token leakage via referrer headers
- account linking abuse (link attacker google account to victim)
```

```bash
# Test redirect_uri bypass
https://accounts.google.com/oauth/authorize?
  client_id=XXXXX
  &redirect_uri=https://app.acmecorp.com.evil.com  # subdomain bypass
  &redirect_uri=https://app.acmecorp.com/callback/../evil  # path traversal
  &redirect_uri=https://app.acmecorp.com/callback%2F..%2Fevil

# Check if state is validated (CSRF in OAuth)
# Initiate flow, intercept state param, reuse across sessions
```

**MFA Bypass Vectors:**

```
- Rate limiting on OTP endpoint? (6-digit = 1M combinations)
- Response manipulation (200 vs

*[truncated]*

## With Skill — 1 turn, complete

Same prompt, with `attack-surface` loaded as system context.

### Turn 1

**Prompt**

starting a graybox pentest on an e-commerce company, they have app.acmecorp.com, a REST API and an admin dashboard. stack is react + nodejs + postgres, JWT RS256 auth with google SSO and MFA. they use stripe for payments, sendgrid for emails and cloudflare in front. iOS/Android mobile app too. where do i start and what's my attack surface?

**Response**

# Attack Surface Map — AcmeCorp E-Commerce

**Engagement type:** Gray-box pentest
**Scope confirmed:** app.acmecorp.com + REST API + admin dashboard + mobile apps

---

## Phase 1 — Entry Point Enumeration

### Web Application (`app.acmecorp.com`)

| Component | Type | Auth | Priority | Notes |
|---|---|---|---|---|
| Login / Registration | Auth flow | None | **Critical** | OAuth + MFA — multiple bypass paths |
| Password reset | Auth flow | None | **Critical** | Token predictability, host header injection |
| Google SSO callback | OAuth | None | **Critical** | State param CSRF, redirect_uri manipulation |
| MFA flow | Auth flow | Partial | **High** | Rate limiting, bypass via direct endpoint access |
| Product search / filters | User input | Optional | **High** | SQLi, parameter pollution |
| Checkout / cart | Business logic | Yes | **High** | Price manipulation, coupon abuse, race conditions |
| File upload (product images, avatars) | Upload | Yes | **High** | Extension bypass, path traversal, stored XSS |
| Order history / account pages | IDOR | Yes | **High** | Horizontal privilege escalation |
| Export functions (invoices, reports) | Data access | Yes | **Medium** | SSRF, path traversal, template injection |

### REST API

| Component | Type | Auth | Priority | Notes |
|---|---|---|---|---|
| JWT validation logic | Auth | Bearer (RS256) | **Critical** | Algorithm confusion (`RS256 → HS256`), `kid` header injection, `none` alg |
| `/api/v*/admin/*` routes | Privilege | Bearer | **Critical** | Auth missing on individual routes, mass assignment |
| `/api/v*/users/:id` | IDOR | Bearer | **High** | Sequential IDs, UUID predictability |
| `/api/v*/orders/:id` | IDOR | Bearer | **High** | Cross-user order access |
| GraphQL endpoint (if exists) | API | Bearer | **High** | Introspection enabled, batching attacks |
| Webhook receivers (Stripe, SendGrid) | External input | Signature | **High** | Signature validation bypass, event manipulation |
| Internal/debug endpoints

*[truncated]*

## What changed

Both completed in 1 turn, but the quality on that first turn differed: **Partial** without the skill vs **Good** with it. The skill enforces a consistent methodology from the first prompt.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
