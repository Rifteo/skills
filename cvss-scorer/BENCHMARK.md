---
skill: cvss-scorer
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: cvss-scorer
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Complete | Complete | ⚪ same |
| Turns to complete | 1 | 1 | ⚪ 0 |
| Response tokens | ~539 | ~201 | 🟢 -63% |
| Total time | 18s | 6s | 🟢 -68% |
| User effort | Low | Low | ⚪ Low |

## Scenario

Pentester describes a vuln casually — needs an exact CVSS 3.1 score for the report

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded.

### Turn 1

**Prompt**

found something on an e-commerce API, any logged-in user can see other users' orders just by changing the ID in the URL. no admin required. it exposes full name, email, shipping address and last 4 digits of card. what's the CVSS score for my report?

**Response**

## CVSS v3.1 Scoring for IDOR on Order Data

This is a classic **Insecure Direct Object Reference (IDOR)** / Broken Access Control finding. Let me walk through the vector properly.

---

## Vector Breakdown

| Metric | Value | Reasoning |
|--------|-------|-----------|
| **Attack Vector** | Network (N) | Exploitable remotely via API |
| **Attack Complexity** | Low (L) | Just increment/guess an integer ID |
| **Privileges Required** | Low (L) | Requires valid login, not anonymous |
| **User Interaction** | None (N) | No victim action needed |
| **Scope** | Unchanged (U) | Stays within the application's authorization scope |
| **Confidentiality** | High (H) | Full PII exposed: name, email, address, partial card |
| **Integrity** | None (N) | Read-only as described |
| **Availability** | None (N) | No service disruption |

---

## Score

```
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
```

> **Base Score: 6.5 — MEDIUM**

---

## Considerations That Could Change the Score

**Might push higher:**
- If you can also **modify or cancel** others' orders → Integrity becomes High → ~8.1 High
- If **no auth required** at all → PR:None → 7.5 High

**Contextual notes for your report:**
- OWASP categorizes this as **A01:2021 Broken Access Control** (top of the list)
- The partial card data may trigger **PCI-DSS** notification requirements for the vendor
- Sequential integer IDs make this **trivially enumerable** — worth noting severity beyond pure CVSS

---

## Recommendation to Include in Report

- Implement **server-side ownership validation** on every order endpoint
- Use **non-sequential UUIDs** as an additional layer (not a fix by itself)
- Audit **all object references** across the API surface

Good find — the CVSS score undersells the real-world impact somewhat given the PII exposure.

## With Skill — 1 turn, complete

Same prompt, with `cvss-scorer` loaded as system context.

### Turn 1

**Prompt**

found something on an e-commerce API, any logged-in user can see other users' orders just by changing the ID in the URL. no admin required. it exposes full name, email, shipping address and last 4 digits of card. what's the CVSS score for my report?

**Response**

```
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
Score: 6.5 — Medium
```

> C:H — full name, email, shipping address, and partial card data together constitute sensitive PII. I:N because the endpoint appears read-only. If order cancellation or modification is also exposed via the same broken access control, bump I to H → **8.8 High**.

One thing worth checking before you submit: are the order IDs numeric/sequential or UUIDs? If sequential (1001, 1002…), this is trivially enumerable and the score stands as-is. If UUIDs, AC flips to H → **4.3 Medium** — worth noting in your report either way since it affects exploitability narrative.

## What changed

Both completed in 1 turn, but the quality on that first turn differed: **Complete** without the skill vs **Complete** with it. The skill enforces a consistent methodology from the first prompt.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
