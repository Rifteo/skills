---
skill: attack-surface
tested-on: claude CLI (claude-sonnet-4-6)
date: 2026-05-20
---

# Benchmark: attack-surface

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~7,336 | ~2,200 | **🟢 -70%** |
| Time | 143s | 54s | **🟢 -62%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Map the attack surface for a fintech SaaS at target.com — public web app, mobile API, OAuth login via Google and GitHub, file upload feature, and webhook integrations
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Map the attack surface for a fintech SaaS at target.com — public web app, mobile API, OAuth login via Google and GitHub, file upload feature, and webhook integrations

**Response**
```
## Phase 1: SCOPE

### In-Scope Assets
| Asset | Type | Notes |
|---|---|---|
| `target.com` | Web app | Primary surface |
| `api.target.com` | Mobile/REST API | iOS + Android clients |
| `*.target.com` | Subdomains | Wildcard assumed |
| OAuth flows | Google + GitHub | Auth surface |
| File upload endpoints | Feature | Likely `/upload`, `/documents` |
| Webhook system | Integration | Inbound + outbound |

### Accepted Impact (Fintech Context)
- Account takeover / authentication bypass
- Payment data exposure (PCI-adjacent)
- Unauthorized access to other users' data (IDOR)
- Financial logic flaws (double-spend, balance manipulation)
- SSRF via webhooks (internal network access)
- Stored XSS on financial dashboards
- File upload leading to RCE or stored XSS

### Never-Submit / Out-of-Scope (assumed standard)
- DoS / DDoS
- Physical attacks
- Social engineering
- Findings on third-party infrastructure (Google, GitHub OAuth providers themselves)
- Rate-limit issues without demonstrated im
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `attack-surface` loaded as context.

#### Turn 1

**Prompt**
> Map the attack surface for a fintech SaaS at target.com — public web app, mobile API, OAuth login via Google and GitHub, file upload feature, and webhook integrations

**Response**
```
## Attack Surface Map — target.com (Fintech SaaS)

---

### Phase 1 — Entry Point Enumeration

**Web Application**
- `target.com` — public marketing/landing page
- `app.target.com` — main authenticated SaaS dashboard
- `admin.target.com` — likely admin panel (common fintech pattern)
- `api.target.com` — backend API (inferred from SaaS + mobile API)
- Login, registration, password reset flows
- File upload feature (statements, KYC docs, exports)
- Search/filter UI components
- Data export endpoints (CSV/PDF — common in fintech)

**Mobile API**
- Mobile-specific API base (may differ from web API — separate versioning, auth logic)
- Certificate pinning bypass surface
- API endpoints exposed via decompiled APK/IPA
- Mobile auth token storage and refresh logic

**OAuth / Auth Flows**
- Google OAuth (`/auth/google`, `/oauth/callback`)
- GitHub OAuth (`/auth/github`, `/oauth/callback`)
- Account linking — existing account + new OAuth provider
- OAuth `state` parameter handling (CSRF protectio
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
