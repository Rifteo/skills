---
skill: high-severity-hunter
tested-on: claude CLI (claude-sonnet-4-6)
target: simulated bug bounty program — fintech SaaS with payment processing, multi-tenant architecture, REST API
date: 2026-08-04
---

# Benchmark: high-severity-hunter

> Same target. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Delta |
|---|---|---|---|
| Attack priority derived from target context | No — generic checklist | Yes — derived from payment/SaaS signals | **🟢** |
| Business logic targeted first | No — started with XSS | Yes — payment flows targeted first | **🟢** |
| POC-or-kill enforced | No — theoretical findings surfaced | Yes — only actionable hypotheses | **🟢** |
| Chain thinking applied | No | Yes — every finding evaluated for chain potential | **🟢** |
| Kill list applied (no-impact findings dropped) | No — missing headers included | Yes — noise removed before surfacing | **🟢** |
| Auth position assessed before hunting | No | Yes — multi-account coverage planned | **🟢** |
| Findings ranked by impact on THIS target | No — generic severity ordering | Yes — fintech-specific impact ordering | **🟢** |

---

## Scenario

```
I have a bug bounty target. It is a B2B fintech SaaS — businesses use it
to manage payroll, invoice vendors, and schedule wire transfers.
Multi-tenant architecture. REST API. Auth via JWT. Users have roles:
employee, manager, and org-admin. I have two accounts: one employee
and one manager in the same organization.

Help me start the hunt.
```

---

## Without Skill

**Turn 1**

Prompt:
> I have a bug bounty target. It is a B2B fintech SaaS — payroll, invoices, wire transfers. Multi-tenant. REST API. JWT auth. Roles: employee, manager, org-admin. I have two test accounts. Help me start the hunt.

Response:
```
Here is a systematic approach to testing this target:

**Reconnaissance**
- Enumerate subdomains
- Review the application's functionality by browsing through all features
- Review JS files for hardcoded credentials or API endpoints

**Authentication Testing**
- Test for SQL injection in login fields
- Check for account enumeration via login error messages
- Test password reset flow for predictable tokens

**Session Management**
- Inspect JWT structure — check for algorithm confusion (alg:none)
- Test session fixation

**XSS Testing**
- Test all input fields for reflected and stored XSS
- Check DOM-based XSS in single-page app rendering

**Authorization Testing**
- IDOR on object IDs in API endpoints
- Privilege escalation between roles

**CSRF**
- Check state-changing endpoints for CSRF tokens

**Other Checks**
- Clickjacking on sensitive pages
- Security headers (HSTS, CSP, X-Frame-Options)
- Rate limiting on login

Start with recon, then work through the checklist systematically.
```

**What was missing:**
- No reading of the target — this is a payroll/wire transfer platform with real money and org isolation, and the response treated it identically to a blog
- Business logic never mentioned — the highest-impact class for a payment SaaS was absent
- XSS prioritized before authorization on a B2B financial platform — backwards
- CSRF, clickjacking, and missing headers included despite no demonstrated exploitability — noise
- No multi-account plan — two accounts at different privilege levels are the primary tool for auth testing; the response did not leverage them
- No chain thinking — findings listed as independent items
- No impact framing — "IDOR on object IDs" on a wire transfer platform is potentially Critical; the response gave it equal weight with clickjacking
- Auth position never assessed — what each role can see and do was not mapped before proposing what to attack

---

## With Skill

**Turn 1**

Prompt:
> I have a bug bounty target. It is a B2B fintech SaaS — payroll, invoices, wire transfers. Multi-tenant. REST API. JWT auth. Roles: employee, manager, org-admin. I have two test accounts. Help me start the hunt.

Response:
```
Target read. This is a payroll and wire transfer platform — money moves through
this application. That context sets the entire priority order.

**Auth position:** employee + manager in the same org. That gives us:
- Horizontal coverage: can employee reach manager-only resources?
- Vertical coverage: can either escalate to org-admin?
- Intra-org isolation: can we reach another org's data?
We need an org-admin account or a second org to complete the picture.
Note what is missing and flag it — tenant isolation and admin-level
privilege escalation cannot be fully tested without it.

**Attack queue — derived from this target:**

1. **Business logic in payment flows** — this is the top priority.
   Wire transfers, payroll runs, invoice payments. These are the crown jewels.
   Questions to test: Can a payment be submitted with negative amounts?
   Can a transfer step be skipped or replayed? Can a pending transaction
   be modified after initiation? Can a rate limit or approval step be
   bypassed via concurrent requests? Impact if any of these fail: money
   moves without authorization — Critical.

2. **Authorization on financial objects (IDOR)** — every endpoint that
   references a transaction, invoice, payroll run, or bank account by ID
   is a test. Employee reading manager's salary data, employee initiating
   a transfer they cannot approve, one org reading another org's records.
   Impact: financial data disclosure or unauthorized transactions — High/Critical.

3. **Privilege escalation across roles** — employee → manager → org-admin.
   Every action the manager account performs that the employee account should
   not: test whether the role check is enforced at the API level or only
   in the UI. Mass assignment on any object the user can modify — can a
   user set their own role? Impact: full account takeover or org-admin access.

4. **Account takeover vectors** — ATO on a payroll platform means an attacker
   controls where money goes. JWT flaws, password reset logic, session
   invalidation after role or email change, OAuth/SSO misconfigurations
   if present. Impact: ATO — Critical.

5. **Server-side injection in transaction processing** — any parameter
   that filters transactions, searches records, or identifies payees
   that reaches a database or internal service. Impact: data extraction
   or internal service access.

**What to enumerate before attacking:**
- Every endpoint the manager account can reach that the employee cannot
- Every object reference in API responses: transaction IDs, invoice IDs,
  bank account IDs, org IDs, user IDs, payroll IDs
- Every payment/transfer flow end-to-end — map the full state machine
  before testing whether you can violate it

**Kill immediately — no time:**
- Missing security headers
- CSRF on endpoints already covered by JWT auth
- Rate limiting on non-payment endpoints
- Clickjacking on any page

**First moves by ROI:**
1. Map the full payment/transfer flow with the manager account — capture
   every request, every state transition
2. Test employee account against every manager-visible endpoint — does
   the API enforce the role or only the UI?
3. Attempt concurrent transfer requests from employee and manager simultaneously
   — probe for race conditions before any approval gate
```

**What the skill provided:**
- Target read before any action — this is a money-movement platform, not a blog; the priority order reflects that
- Business logic placed first — the attack class most relevant to a payment SaaS went to the top of the queue, not buried in a generic list
- Auth position assessed against the specific role model — two accounts at different levels mapped to concrete test coverage, gaps noted
- IDOR framed in terms of financial objects, not generic ID parameters — employee reading salary data vs. employee reading a blog post ID are not the same finding
- Kill list applied immediately — noise removed before any time was spent on it
- Every proposed test tied to a specific impact on this target — Critical for unauthorized money movement, High for financial data disclosure
- First moves ranked by ROI on this target, not by a generic sequence
- Chain potential embedded — ATO on a payroll platform → attacker controls where money goes is stated explicitly

---

## What changed

Without the skill the agent produced a generic security checklist — the same list it would produce for a social media app, a healthcare portal, or a document editor. Business logic, the highest-impact class for a financial platform, was never mentioned. XSS was prioritized before authorization. Missing headers and clickjacking were listed alongside critical payment flow risks. With the skill the agent read the target first: this is a payroll and wire transfer platform, money moves through it, and that context drives everything. Business logic went first. Authorization on financial objects went second. The attack queue was derived from what the target does and what breaks it — not from a universal ordering. The two test accounts were immediately mapped to their coverage gaps. The kill list pruned noise before any time was spent on it. The difference is not knowledge — the model knows every attack class in both cases. The difference is priority: knowing where to go first on this specific target versus treating every target the same way.
