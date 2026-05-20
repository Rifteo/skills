---
skill: hpp-hunter
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: hpp-hunter

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~3,829 | ~2,007 | **🟡 -48%** |
| Time | 86s | 51s | **🟡 -41%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Test for HTTP parameter pollution on target.com — the checkout endpoint accepts item_id and quantity parameters and aggregates values server-side
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Test for HTTP parameter pollution on target.com — the checkout endpoint accepts item_id and quantity parameters and aggregates values server-side

**Response**
```
# Structured HPP Hunt — target.com Checkout Endpoint

---

## Phase 1: SCOPE

**Assumptions (standard bug bounty scope for a checkout endpoint):**

| Asset | Status |
|---|---|
| `target.com` and subdomains | In scope |
| Checkout/payment flows | In scope — P1 |
| Automated scanning (SQLMap, scanners) | Not allowed |
| DoS, account deletion, data destruction | Never submit |
| Other users' orders without consent | Never submit (use two test accounts) |

**Accepted impacts:** Business logic abuse, price manipulation, order fraud, authentication bypass, PII exposure.

**Gate:** I am allowed to test `target.com`'s checkout endpoint for business logic and injection bugs using manual HTTP requests with two self-owned test accounts; I am not allowed to run automated scanners, cause service disruption, or access other users' data.

---

## Phase 2: RECON

**Subdomain enumeration (methodology):**

```bash
# crt.sh passive cert lookup
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq -r
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `hpp-hunter` loaded as context.

#### Turn 1

**Prompt**
> Test for HTTP parameter pollution on target.com — the checkout endpoint accepts item_id and quantity parameters and aggregates values server-side

**Response**
```
I'll work through the HPP Hunter methodology for the checkout endpoint, focusing on the `item_id` and `quantity` parameters with server-side aggregation behavior.

---

## Phase 1 — Fingerprint Parameter Handling

First, establish the exact aggregation behavior before crafting attacks.

**Baseline request:**
```http
GET /checkout?item_id=1&quantity=2 HTTP/1.1
Host: target.com
```

**Duplicate fingerprint probe:**
```bash
curl -s "https://target.com/checkout?item_id=1&quantity=2&quantity=3" -i
```

Compare the response against these expected behaviors:

| Response shows | Behavior | Attack surface |
|---|---|---|
| `quantity=2` only | First-wins | Inject payload second |
| `quantity=3` only | Last-wins | Inject payload second, legit value first |
| `quantity=2,3` or `5` | Concatenation / sum | WAF splitting, value injection into aggregate |
| Array in body/error | Array | Array-index manipulation |

Since the endpoint **aggregates values server-side**, the most likely behavior is **summ
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
