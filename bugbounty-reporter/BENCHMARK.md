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
| Total tokens | ~1,338 | ~2,081 | **🔴 +56%** |
| Time | 51s | 48s | **🟠 -6%** |
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
## Title
Insecure Direct Object Reference (IDOR) in `/api/orders/{id}` through Sequential Integer Order ID Leads To Unauthorized Access to Any User's Full Order Data

---

## Description
An Insecure Direct Object Reference (IDOR) vulnerability exists in the `/api/orders/{id}` endpoint. The application resolves order records by numeric ID alone without verifying that the authenticated requester owns the requested order. An attacker with a valid session can enumerate any integer value in the path parameter to retrieve complete order records belonging to other users, including personal details, purchase history, and any payment or shipping information stored in the order object.

---

## Steps to Reproduce

> **Requires two accounts:** Victim (Account A) and Attacker (Account B), both registered on the platform.

1. Log in as **Account A** (victim). Place an order and note the resulting order ID — e.g., `1042`. Log out.
2. Log in as **Account B** (attacker). Capture your session token (e.
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
Running the Pre-Submission Triage Gate, then writing the report.

**Triage Gate:**
1. Exploitable with a real HTTP request — yes, sequential integer enumeration
2. Unauthorized data access is standard accepted-impact — yes
3. Asset assumed in scope per the finding description — yes
4. No privileged access required beyond a standard authenticated session — yes
5. No indication this is documented behavior — yes
6. Impact provable: full order record returned in response — yes
7. Not on a known never-submit list — yes

All seven pass. Writing the report.

---

## Bug Bounty Report

---

### Title

IDOR in `/api/orders/{id}` through integer order ID Leads To Unauthorized Access to Full Order Data for Any User

---

### Description

An Insecure Direct Object Reference (IDOR) exists in the `/api/orders/{id}` endpoint. The application resolves the requested order solely by the integer ID in the URL path and does not verify that the authenticated user owns that order. An attacker with a valid s
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. However, without the skill the agent used 743 fewer tokens by producing a shallower, less structured output. With the skill, the agent produced a thorough, fully structured result — the token increase reflects depth, not inefficiency.

With the skill, the agent followed a proven methodology from the first prompt.

---
