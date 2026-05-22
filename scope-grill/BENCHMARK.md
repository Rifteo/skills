---
skill: scope-grill
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: scope-grill
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Incomplete | Complete | 🟢 +3 level(s) |
| Turns to complete | 2 | 1 | 🟢 -1 turn(s) |
| Response tokens | ~2,332 | ~165 | 🟢 -93% |
| Total time | 43s | 4s | 🟢 -90% |
| User effort | Medium | Low | 🟢 Low |

## Scenario

Pentester mentions a target casually with no scope, authorization, or rules — the agent must catch what's missing before any testing begins

## Without Skill — 2 turns required

The agent received the prompt with no skill loaded. The first response was incomplete — it took 2 rounds of prompting to reach a usable result.

### Turn 1

**Prompt**

starting a pentest on acmecorp.com, my client said it's fine to go ahead. where do i start?

**Response**

# Penetration Testing: Complete Guide for acmecorp.com

## ⚠️ BEFORE ANYTHING ELSE

---

## Question 1: Do You Actually Have Proper Authorization?

**"My client said it's fine"** is not sufficient. You need:

- [ ] **Signed written contract** with scope explicitly defined
- [ ] **Statement of Work (SOW)** or **Rules of Engagement (ROE)**
- [ ] **Named authorization** - who specifically authorized testing
- [ ] **IP ranges and domains explicitly listed** in writing
- [ ] **Testing windows** agreed upon
- [ ] **Emergency contact/halt procedure** documented
- [ ] **Third party authorization** if their infrastructure is in scope (AWS, Cloudflare, etc.)

**Why this matters legally:**
> Without written authorization, you could be prosecuted under:
> - **US**: Computer Fraud and Abuse Act (CFAA)
> - **UK**: Computer Misuse Act 1990
> - **EU**: Directive 2013/40/EU
> - **AU**: Criminal Code Act 1995

**Do not proceed without a signed document.**

---

## Engagement Brief Template

Before starting, confirm and document:

```
CLIENT:          acmecorp.com
TESTER:          [Your name/company]
AUTHORIZED BY:   [Named individual + title]
SIGNED DATE:     [Date]
TEST WINDOW:     [Start datetime] - [End datetime]
TIMEZONE:        [Explicit timezone]

IN SCOPE:
  - acmecorp.com
  - [Specific subdomains]
  - [IP ranges]
  - [Applications]

OUT OF SCOPE:
  - Third-party services (unless explicitly authorized)
  - Production databases (unless agreed)
  - DoS/DDoS testing (unless agreed)

PERMITTED TESTS:
  - [ ] Web application testing
  - [ ] Network scanning
  - [ ] Social engineering
  - [ ] Physical access
  - [ ] Denial of Service

EMERGENCY CONTACTS:
  Client:   [Name, phone, email]
  Tester:   [Name, phone, email]

DATA HANDLING:
  - How findings are stored
  - How data is destroyed post-engagement
  - Who receives the report
```

---

## Legal Considerations

### Key Legal Risks

| Risk | Mitigation |
|---|---|
| Testing out-of-scope systems | Explicit written scope |
| Shared

*[truncated]*

*Missing sections triggered 1 follow-up prompt(s) before the agent produced a complete result.*

## With Skill — 1 turn, complete

Same prompt, with `scope-grill` loaded as system context.

### Turn 1

**Prompt**

starting a pentest on acmecorp.com, my client said it's fine to go ahead. where do i start?

**Response**

Got it — let's make sure we have everything locked down before touching anything. A verbal "it's fine" from a client isn't the same as written authorization, and that distinction matters legally.

Let's build your engagement brief. I'll ask one question at a time.

---

**Question 1 of 10 — Target**

You mentioned `acmecorp.com` — is that the exact target, or does it include subdomains, related domains, or other infrastructure?

**Example answer:** *"acmecorp.com and all subdomains (*.acmecorp.com), plus the staging environment at staging.acmecorp.com. Their mobile app is out of scope."*

What's the full target?

## What changed

Without the skill, the first response was **Incomplete** — the agent needed **2 turns** and follow-up prompts to fill the gaps. With the skill, the agent delivered a **Complete** answer in **1 turn**.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
