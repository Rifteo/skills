---
skill: bugbounty-reporter
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: bugbounty-reporter
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Partial | Complete | 🟢 +2 level(s) |
| Turns to complete | 1 | 1 | ⚪ 0 |
| Response tokens | ~726 | ~1,767 | 🔴 +143% |
| Total time | 19s | 37s | 🔴 +95% |
| User effort | Low | Low | ⚪ Low |

## Scenario

Bug hunter found an IDOR, shares raw evidence casually — needs a triage-ready HackerOne report

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded.

### Turn 1

**Prompt**

found an IDOR on an e-commerce site in their hackerone program. i can access other customers' invoices just by changing the ID in the URL:

GET /api/v2/invoices/8841/download
Authorization: Bearer my_token

the response gives me the name, email, address, and last 4 digits of another user's card. i iterated from 8841 to 8800, works on all 41. sequential IDs.

how do i write the report for hackerone? severity high

**Response**

# HackerOne IDOR Report: Invoice Access

This is a solid find. Here's how to write a clear, professional report.

---

## Report Structure

### Title
`IDOR in /api/v2/invoices/{id}/download allows unauthorized access to customer PII`

---

### Vulnerability Type
Insecure Direct Object Reference (IDOR)

### Severity
**High** - reasonable given PII exposure. CVSS would be roughly 7.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)

---

### Summary
```
Authenticated users can access any customer invoice by 
manipulating the invoice ID parameter. Sequential IDs 
make enumeration trivial. Each invoice exposes name, 
email, physical address, and partial card number.
```

---

### Steps to Reproduce
```
1. Create account and obtain any valid invoice ID
   (visible in normal app flow)

2. Send request with a different user's invoice ID:

GET /api/v2/invoices/8800/download HTTP/1.1
Host: [target]
Authorization: Bearer [your_token]

3. Response returns another user's:
   - Full name
   - Email address  
   - Billing/shipping address
   - Last 4 digits of payment card

4. Increment ID across any range to enumerate at scale
```

---

### Impact
```
- PII exposure for potentially all customers
   (sequential IDs suggest full database is accessible)
- No rate limiting observed during testing
- Data sufficient for phishing/social engineering
- May have PCI DSS and GDPR implications for the company
- Estimated exposure: if IDs reach ~8841, thousands 
  of records potentially accessible
```

---

### What to Include as Attachments
- Burp Suite screenshot of your request/response
- Screenshot showing YOUR account vs the accessed invoice
  (proves cross-account access)
- Redact most of the victim PII in screenshots - show enough
  to prove the bug, not the full data

---

## Important Notes on Your Testing

**Stop at 41 requests** - you did the right thing. Document that you:
- Limited testing to confirm the vulnerability
- Did not store the PII you accessed
- Reported promptly

Mention this e

*[truncated]*

## With Skill — 1 turn, complete

Same prompt, with `bugbounty-reporter` loaded as system context.

### Turn 1

**Prompt**

found an IDOR on an e-commerce site in their hackerone program. i can access other customers' invoices just by changing the ID in the URL:

GET /api/v2/invoices/8841/download
Authorization: Bearer my_token

the response gives me the name, email, address, and last 4 digits of another user's card. i iterated from 8841 to 8800, works on all 41. sequential IDs.

how do i write the report for hackerone? severity high

**Response**

# Bug Bounty Report — HackerOne Submission

---

## Pre-Submission Triage Gate

| Check | Result |
|---|---|
| Exploitable now with a real HTTP request? | ✅ Yes |
| Impact on accepted-impact list (PII, data exposure)? | ✅ Yes |
| Asset in scope? | ✅ Assumed — confirm before submitting |
| Works without attacker-unattainable privileges? | ✅ Any authenticated customer |
| Not known/documented behavior? | ✅ Yes |
| Impact proved beyond "technically possible"? | ✅ 41 real invoices confirmed |
| Not on never-submit list? | ✅ Assumed — confirm before submitting |

All seven pass. Proceeding.

---

## Report

---

### Title

```
IDOR in api/v2/invoices/{id}/download through Sequential Integer ID Leads To
Unauthorized Access to Customer PII and Partial Payment Data
```

---

### Description

An Insecure Direct Object Reference (IDOR) vulnerability exists in the `/api/v2/invoices/{id}/download` endpoint. The API performs no authorization check to verify that the authenticated user owns the requested invoice — it only validates that a bearer token is present, not that the token belongs to the invoice owner. Any authenticated customer can iterate the sequential integer invoice ID to download invoices belonging to other customers, exposing their full name, email address, physical address, and last four digits of their payment card.

---

### Steps to Reproduce

**Setup required:** One registered customer account with a valid session token.

1. Log in to the application as a normal customer account. Obtain your bearer token from any authenticated API request.

2. Note your own invoice ID from your account dashboard (in this case, `8841`).

3. Send the following request, substituting your bearer token:

```http
GET /api/v2/invoices/8841/download HTTP/1.1
Host: [TARGET HOST]
Authorization: Bearer [YOUR_TOKEN]
```

4. Confirm the response returns your own invoice. Note the structure.

5. Decrement the ID and repeat:

```http
GET /api/v2/invoices/8840/download HTTP/1.1
Host: [TARGET

*[truncated]*

## What changed

Both completed in 1 turn, but the quality on that first turn differed: **Partial** without the skill vs **Complete** with it. The skill enforces a consistent methodology from the first prompt.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
