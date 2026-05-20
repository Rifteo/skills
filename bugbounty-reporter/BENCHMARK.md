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
| Total tokens | ~2,335 | ~2,128 | **🟠 -9%** |
| Time | 54s | 48s | **🟠 -11%** |
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
**Pre-Submission Triage Gate — all 7 pass.** Writing the report now.

---

## Bug Bounty Report

---

### Title

**IDOR in `/api/orders/{id}` through Sequential Integer ID Leads To Unauthorized Full Order Data Exposure Across All Users**

---

### Description

An Insecure Direct Object Reference (IDOR) vulnerability exists in the `/api/orders/{id}` endpoint. The application resolves order records by integer ID without verifying that the requesting user owns the referenced order. An authenticated attacker can enumerate any valid integer ID to retrieve the full order details — including personal information, shipping address, item contents, and payment summary — of any other user on the platform.

---

### Steps to Reproduce

**Prerequisites:** Two accounts — Attacker (Account A) and Victim (Account B). Victim must have placed at least one order.

1. Log in as **Account B** (Victim) and place an order. Note the order ID returned in the response (e.g., `1042`).
2. Log out. Log in as **Acc
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

**Gate check:**
1. Exploitable with a real HTTP request? YES — change integer in path
2. Impact on accepted list? YES — unauthorized data access
3. Asset in scope? ASSUMED YES
4. No privileged access required? YES — any authenticated user
5. Not known/documented behavior? ASSUMED YES
6. Impact provable? YES — response contains real data
7. Not on never-submit list? ASSUMED YES

All seven pass. Writing the report now.

---

## Bug Bounty Report

---

### Title

IDOR in `/api/orders/{id}` through Integer Order ID Leads To Unauthorized Access to Full Customer Order Data

---

### Description

An Insecure Direct Object Reference (IDOR) exists in the `GET /api/orders/{id}` endpoint. The application returns complete order records based solely on the integer ID in the URL path without verifying that the requesting user owns the order. An attacker with a valid session can enumerate sequential order IDs to read any customer's ful
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
