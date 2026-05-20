---
skill: cvss-scorer
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: cvss-scorer

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~2,380 | ~619 | **🟢 -74%** |
| Time | 46s | 20s | **🟢 -57%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Compute CVSS 3.1 score for an unauthenticated IDOR that exposes full financial records of any user via sequential integer ID enumeration on a public API
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Compute CVSS 3.1 score for an unauthenticated IDOR that exposes full financial records of any user via sequential integer ID enumeration on a public API

**Response**
```
## CVSS 3.1 Score: Unauthenticated IDOR — Financial Record Exposure

### Metric Selection

| Metric | Value | Rationale |
|--------|-------|-----------|
| **Attack Vector (AV)** | Network (N) | Public API, reachable over the internet |
| **Attack Complexity (AC)** | Low (L) | Sequential integer enumeration — no special conditions, no race, no brute-force threshold |
| **Privileges Required (PR)** | None (N) | Unauthenticated; zero account needed |
| **User Interaction (UI)** | None (N) | Fully automated; victim action not required |
| **Scope (S)** | Unchanged (U) | Attacker stays within the same security authority (the application and its DB); no pivot to a separate component |
| **Confidentiality (C)** | High (H) | Full financial records — PII, account balances, transaction history; complete loss of confidentiality for affected objects |
| **Integrity (I)** | None (N) | Read-only exposure as described |
| **Availability (A)** | None (N) | No disruption to service |

---

### Calculat
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `cvss-scorer` loaded as context.

#### Turn 1

**Prompt**
> Compute CVSS 3.1 score for an unauthenticated IDOR that exposes full financial records of any user via sequential integer ID enumeration on a public API

**Response**
```
```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
Score: 7.5 — High
```

All metrics are unambiguous from the description:

- **AV:N** — public API, reachable over the internet
- **AC:L** — sequential integer IDs, trivially enumerable
- **PR:N** — unauthenticated
- **UI:N** — direct server-side IDOR, no victim interaction needed
- **S:U** — IDOR stays within the application's security scope
- **C:H** — full financial records constitute highly sensitive data
- **I:N / A:N** — read-only exposure, no write or disruption implied
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
