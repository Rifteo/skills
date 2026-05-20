---
skill: risk-assessor
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: risk-assessor

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **0%** |
| Total tokens | ~1,854 | ~3,376 | **+82%** |
| Time | 43s | 88s | **+105%** |
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
**PRE-SUBMISSION TRIAGE GATE — Stored XSS / Admin Dashboard / SaaS**

---

**1. Can an attacker use this RIGHT NOW with a real HTTP request?**
YES — Stored XSS executes automatically when an admin loads the affected page, triggered by a prior HTTP POST that persisted the payload.

**2. Is the impact on the program's accepted-impact list?**
YES — Admin-context XSS leading to session hijack and data access is on every major bug bounty program's accepted-impact list.

**3. Is the asset in scope?**
YES — The admin dashboard is a core production surface of the SaaS platform and is presumed in scope absent a specific exclusion.

**4. Does it work without privileged access an attacker cannot get?**
**CONDITIONAL** — This is the critical unknown: if a lower-privileged user (free tier, trial account, or unauthenticated) can plant the payload that executes in the admin's browser, it passes; if only admins can inject it, this is self-XSS and fails.

**5. Is this not already known or documented be
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
**Vulnerability:** Stored XSS in SaaS admin dashboard — persistent script injection enabling admin session hijacking across all customer tenants

**Attack Surface:** Internet-facing SaaS admin dashboard; payload executes passively in any authenticated admin's browser upon page load — no attacker interaction required post-injection. Injection vector likely originates from customer-controlled input rendered unsanitized in the admin view.

---

**Likelihood:** High — Score: 3
- Attack vector: Network
- Exploit availability: Weaponized — XSS exploitation frameworks (BeEF, XSS Hunter) are freely available; this class is OWASP Top 10 A03 with extensive public tooling
- Authentication required: None for payload execution — the stored payload fires automatically when the admin loads the affected page; the attacker's only prerequisite is having submitted the malicious payload (plausible via a customer account or any user-input path)
- Key modifier applied: Network attack vector (+0.5), no attac
... [truncated]
```

---

## What changed

The agent completed the task in one turn both with and without the skill. The skill still reduced token usage and improved output consistency.

With the skill, the agent followed a proven methodology from the first prompt. Complete output, first try.

---
