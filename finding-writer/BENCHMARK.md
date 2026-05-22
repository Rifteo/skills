---
skill: finding-writer
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: finding-writer
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Good | Complete | 🟢 +1 level(s) |
| Turns to complete | 1 | 1 | ⚪ 0 |
| Response tokens | ~855 | ~1,015 | 🔴 +19% |
| Total time | 19s | 22s | 🔴 +14% |
| User effort | Low | Low | ⚪ Low |

## Scenario

Pentester pastes raw Burp capture with no formatting — needs a proper report finding

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded.

### Turn 1

**Prompt**

captured this in burp, i think it's an IDOR but not sure how to write it up for my report:

GET /api/v2/orders/10482/details HTTP/1.1
Host: shop.acmecorp.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzk5In0.xxx

HTTP/1.1 200 OK
{"order_id":10482,"customer_name":"John Smith","email":"jsmith@gmail.com","card_last4":"4242","items":[{"name":"iPhone 15","qty":1,"price":999}],"shipping_address":"123 Main Street, New York NY 10001"}

tested with my account user_99 by changing the ID, works on all IDs. is this serious?

**Response**

Yes, this is a classic IDOR and it's serious. Here's how to think through it and write it up properly.

## Why This Is Confirmed IDOR

Your token `user_99` is successfully returning order data belonging to other customers. The server is **not verifying ownership**, only authentication.

---

## Severity Assessment

I'd rate this **High** (borderline Critical) because:

- PII exposed: full name, email, shipping address
- Payment data exposed: card last4 (minor but reportable)
- Order contents exposed: purchase history
- Sequential IDs make mass enumeration trivial
- No rate limiting mentioned

---

## How to Write It Up

**Title:** Insecure Direct Object Reference (IDOR) in Order Details API Allows Unauthorized Access to Customer PII

**Vulnerability Type:** IDOR / Broken Object Level Authorization (BOLA)

**Severity:** High

**Affected Endpoint:**
```
GET /api/v2/orders/{order_id}/details
```

**Description:**

The order details endpoint fails to verify that the authenticated user owns the requested order. Any authenticated user can access any order by modifying the numeric order ID in the request path.

**Steps to Reproduce:**

1. Authenticate as a legitimate user and capture a valid Bearer token
2. Place or locate an order belonging to your account (e.g., order 10482)
3. Send the following request substituting another user's order ID:
```
GET /api/v2/orders/10481/details HTTP/1.1
Host: shop.acmecorp.com
Authorization: Bearer [your_token]
```
4. Observe that order details for a different customer are returned

**Evidence:**

Request with `user_99` credentials accessing order 10482:
```json
{
  "order_id": 10482,
  "customer_name": "John Smith",
  "email": "jsmith@gmail.com",
  "card_last4": "4242",
  "shipping_address": "123 Main Street, New York NY 10001"
}
```
Note: `user_99` did not place this order.

**Impact:**

An attacker with any valid account can enumerate order IDs and extract PII for all customers including names, email addresses, physical addresses, and

*[truncated]*

## With Skill — 1 turn, complete

Same prompt, with `finding-writer` loaded as system context.

### Turn 1

**Prompt**

captured this in burp, i think it's an IDOR but not sure how to write it up for my report:

GET /api/v2/orders/10482/details HTTP/1.1
Host: shop.acmecorp.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzk5In0.xxx

HTTP/1.1 200 OK
{"order_id":10482,"customer_name":"John Smith","email":"jsmith@gmail.com","card_last4":"4242","items":[{"name":"iPhone 15","qty":1,"price":999}],"shipping_address":"123 Main Street, New York NY 10001"}

tested with my account user_99 by changing the ID, works on all IDs. is this serious?

**Response**

Your instinct is right — this is a classic IDOR. Here's the full write-up:

---

**Title:** Insecure Direct Object Reference (IDOR) on Order Details Endpoint Exposes Customer PII and Payment Data

---

**Severity:** High
*Justification: Any authenticated user can enumerate all customer orders with no additional barrier, exposing PII and partial payment data at scale with trivial effort.*

---

**CVSS:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` — 6.5 (Medium)

*Note: Base score lands at Medium due to no integrity/availability impact, but the business and regulatory impact of bulk PII exposure warrants a High severity rating in context — CVSS alone understates it here.*

---

**Description:**
The `/api/v2/orders/{id}/details` endpoint on `shop.acmecorp.com` does not validate that the authenticated user owns the requested order. Any authenticated user can substitute an arbitrary integer order ID and retrieve the full order record of any other customer. Because order IDs appear to be sequential integers, the entire order history can be enumerated with a simple automated loop.

---

**Evidence:**
Authenticated as `user_99`, the following request was issued by substituting a different customer's order ID:

```
GET /api/v2/orders/10482/details HTTP/1.1
Host: shop.acmecorp.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzk5In0.xxx
```

The server returned a `200 OK` with full order details belonging to a different customer:

```json
{
  "order_id": 10482,
  "customer_name": "John Smith",
  "email": "jsmith@gmail.com",
  "card_last4": "4242",
  "items": [{"name": "iPhone 15", "qty": 1, "price": 999}],
  "shipping_address": "123 Main Street, New York NY 10001"
}
```

Confirmed to work across all tested order IDs. The authenticated user's own order ID was not `10482`.

---

**Impact:**
An authenticated attacker can enumerate all customer orders and harvest:
- **Full names, email addresses, and home addresses** — sufficient for targeted phishing or physica

*[truncated]*

## What changed

Both completed in 1 turn, but the quality on that first turn differed: **Good** without the skill vs **Complete** with it. The skill enforces a consistent methodology from the first prompt.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
