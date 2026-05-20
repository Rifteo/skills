---
skill: bugbounty-reporter
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: bugbounty-reporter

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~1,448 | ~2,277 | **🔴 +57%** |
| Time | 57s | 49s | **🟠 -14%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Write a bug bounty report for an IDOR on /api/orders/{id} — any integer ID returns full order data for any user, no authentication check on ownership
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Write a bug bounty report for an IDOR on /api/orders/{id} — any integer ID returns full order data for any user, no authentication check on ownership

**Response**
```
---

## Title
Insecure Direct Object Reference (IDOR) in `/api/orders/{id}` through Predictable Integer Order ID Leads To Unauthorized Access to Any User's Order Data

---

## Description
An Insecure Direct Object Reference (IDOR) vulnerability exists in the `/api/orders/{id}` endpoint. The application resolves order records by the integer `id` path parameter without verifying that the authenticated user owns the requested order. An attacker with a valid session can enumerate sequential order IDs to read the full order data — including items, shipping address, billing details, and any PII — of any other user on the platform.

---

## Steps to Reproduce

**Requirements:** Two accounts — Account A (victim) and Account B (attacker), both authenticated.

1. Log in as **Account A** (victim) and place an order. Note the order ID returned in the response — for this example, `order_id = 1001`.
2. Log out of Account A. Log in as **Account B** (attacker).
3. As Account B, send the following requ
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `bugbounty-reporter` loaded as context.

#### Turn 1

**Prompt**
> Write a bug bounty report for an IDOR on /api/orders/{id} — any integer ID returns full order data for any user, no authentication check on ownership

**Response**
```
## Pre-Submission Triage Gate

Running all seven checks against the finding:

1. Exploitable right now with a real HTTP request? **YES** — increment the integer ID, done.
2. Impact on accepted-impact list? **YES** — unauthorized data access is a core IDOR impact.
3. Asset in scope? **ASSUMED YES** — proceeding on that basis.
4. Works without unprocurable privilege? **YES** — any authenticated user can do this.
5. Not known/documented behavior? **YES** — this is a broken access control, not a feature.
6. Impact provable beyond "technically possible"? **YES** — you can fetch the victim's data directly.
7. Not on the never-submit list? **YES** — IDOR is standard in-scope.

All seven pass. Writing the report.

---

## Bug Bounty Report

---

### Title

`IDOR in /api/orders/{id} through integer order ID Leads To Unauthorized Access to Any Customer's Full Order Data`

---

### Description

An Insecure Direct Object Reference (IDOR) vulnerability exists in the `/api/orders/{id}` endpoint. The
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. However, without the skill the agent used 829 fewer tokens by producing a shallower, less structured output. With the skill, the agent produced a thorough, fully structured result — the token increase reflects depth, not inefficiency.

With the skill, the agent followed a proven methodology from the first prompt.

---
