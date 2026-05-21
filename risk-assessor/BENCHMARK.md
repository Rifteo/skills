---
skill: risk-assessor
tested-on: claude CLI (claude-sonnet-4-6)
date: 2026-05-20
---

# Benchmark: risk-assessor

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~2,249 | ~3,895 | **🔴 +73%** |
| Time | 56s | 99s | **🔴 +77%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Assess the business risk of a stored XSS in the admin dashboard of a SaaS platform with 10,000 enterprise customers and SOC2 compliance obligations
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Assess the business risk of a stored XSS in the admin dashboard of a SaaS platform with 10,000 enterprise customers and SOC2 compliance obligations

**Response**
```
## Business Risk Assessment: Stored XSS in SaaS Admin Dashboard

---

### Vulnerability Profile

| Attribute | Value |
|-----------|-------|
| Type | Stored XSS |
| Location | Admin dashboard |
| Persistence | Fires on every admin page load — no further attacker interaction needed |
| Scope | Network-accessible, potentially affects all authenticated admin sessions |

---

### CVSS Estimate

```
AV:N / AC:L / PR:L / UI:R / S:C / C:H / I:H / A:N  →  ~8.8 (High)
```

Scope changes to **C** because a compromised admin session crosses tenant boundaries in a multi-tenant SaaS — one exploited admin account can touch all 10,000 customer environments.

---

### Attack Chain in This Context

```
Attacker plants payload
        ↓
Admin authenticates and views affected page (routine task)
        ↓
Payload executes in admin browser session
        ↓
Options (pick worst-case):
  ├─ Exfiltrate session token → full admin impersonation
  ├─ Silently extract customer data via authenticated API calls
  
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `risk-assessor` loaded as context.

#### Turn 1

**Prompt**
> Assess the business risk of a stored XSS in the admin dashboard of a SaaS platform with 10,000 enterprise customers and SOC2 compliance obligations

**Response**
```
**Vulnerability:** Stored XSS in the admin dashboard of an internet-facing SaaS platform, enabling admin session hijacking and arbitrary JavaScript execution with full administrative privileges

**Attack Surface:** Internet-facing SaaS admin dashboard. An attacker (authenticated low-privilege user or, depending on injection point, unauthenticated via external input such as support tickets or onboarding forms) stores a malicious payload that executes in the browser of any admin who visits the affected page. With 10,000 enterprise customer accounts managed from this surface, admin-level access represents the highest-privilege execution context in the application.

---

**Likelihood:** Medium — Score: 2
- Attack vector: Network
- Exploit availability: Technique is well-documented; stored XSS tooling (BeEF, custom payloads) is widely available; no custom weaponization needed
- Authentication required: Low-privilege — injection point reachable by any authenticated user or potentially extern
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. However, without the skill the agent used 1,646 fewer tokens by producing a shallower, less structured output. With the skill, the agent produced a thorough, fully structured result — the token increase reflects depth, not inefficiency.

With the skill, the agent followed a proven methodology from the first prompt.

---
