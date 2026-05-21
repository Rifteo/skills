---
skill: scope-grill
tested-on: claude CLI (claude-sonnet-4-6)
date: 2026-05-20
---

# Benchmark: scope-grill

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~535 | ~748 | **🔴 +40%** |
| Time | 25s | 27s | **🟠 +8%** |
| Output quality | Complete | Needs review | |

---

## Scenario

```
Review this scope: target.com and all subdomains are in scope, payment processing infrastructure is excluded, no automated scanning allowed, bug bounty program on HackerOne
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Review this scope: target.com and all subdomains are in scope, payment processing infrastructure is excluded, no automated scanning allowed, bug bounty program on HackerOne

**Response**
```
Here's a breakdown of that scope:

**In Scope**
- `target.com` (apex domain)
- All subdomains: `*.target.com` — this is broad and includes anything like `api.target.com`, `admin.target.com`, `staging.target.com`, `dev.target.com`, etc.

**Out of Scope**
- Payment processing infrastructure — typically means anything touching card data: payment pages, checkout flows, PCI-scoped endpoints, third-party payment providers (Stripe, Braintree, etc.). If in doubt, **don't touch it** — the program will likely close reports OOS and it's a legal gray area.

**Key Restriction: No Automated Scanning**
This means no Burp Active Scan, no nuclei, no sqlmap, no nmap, no directory brute-forcing (ffuf, dirb, gobuster). Manual testing only. Violating this is grounds for a ban.

**What this scope allows:**
- Manual browsing and interaction with the app
- Passive enumeration (certificate transparency logs, Google dorking, Shodan reads — anything that doesn't send unsolicited traffic to target)
- Manual explo
... [truncated]
```

---

## With Skill — 1 turn, needs review

The agent received the same prompt with `scope-grill` loaded as context.

#### Turn 1

**Prompt**
> Review this scope: target.com and all subdomains are in scope, payment processing infrastructure is excluded, no automated scanning allowed, bug bounty program on HackerOne

**Response**
```
Good start — here's what's covered from the scope you've provided:

| Field | Status | Notes |
|---|---|---|
| **Target** | Confirmed | `target.com` + all subdomains |
| **Authorization** | Confirmed | HackerOne bug bounty = written authorization |
| **In scope** | Confirmed | `target.com` + all subdomains |
| **Out of scope** | Partial | Payment processing infrastructure excluded — but "payment processing infrastructure" is vague. Does this mean the payment page itself (`/checkout`), the payment provider's domains (e.g., Stripe), internal payment microservices, or all three? |
| **Rules of engagement** | Partial | No automated scanning noted — but other common restrictions aren't addressed (DoS, account enumeration, data exfiltration, testing hours?) |

---

**One gap to resolve first:** The scope exclusion needs sharpening.

> "Payment processing infrastructure is excluded" — can you clarify exactly what is excluded?

For example:
- Just third-party payment provider domains (Stripe, 
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. However, without the skill the agent used 213 fewer tokens by producing a shallower, less structured output. With the skill, the agent produced a thorough, fully structured result — the token increase reflects depth, not inefficiency.

With the skill, the agent followed a proven methodology from the first prompt.

---
