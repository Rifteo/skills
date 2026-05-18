# Engagement Brief Template

Fill every field. Leave nothing blank — use "Unknown / TBD" if information is unavailable and flag it as a gap.

---

**Engagement Title:** [e.g. "Web Application Pentest — Acme Corp Customer Portal"]
**Date:** [YYYY-MM-DD]
**Tester:** [name or handle]

---

## Target

| Field | Value |
|---|---|
| Primary target | [domain / IP / application name] |
| Additional targets | [subdomains, APIs, mobile app, etc.] |
| Environment | Production / Staging / Dev |

## Authorization

- [ ] Written authorization confirmed
- Authorization reference: [ticket number, email date, contract ref]
- Authorized by: [name, title]

## Scope

**In scope:**
- [list each item]

**Out of scope:**
- [list each item]
- If none specified: flag this — undefined out-of-scope creates risk

## Test Type

- [ ] Black-box (no credentials, no source)
- [ ] Grey-box (test accounts provided, no source)
- [ ] White-box (full access + source code)

## Accounts / Access

| Role | Username | Notes |
|---|---|---|
| [e.g. Admin] | [username] | [e.g. provided by client] |
| [e.g. Regular user] | [username] | [e.g. self-registered] |

## Rules of Engagement

- Max testing hours per day: [or "no restriction"]
- Testing window: [e.g. 09:00–18:00 UTC weekdays only / anytime]
- Prohibited actions: [e.g. no DoS, no phishing, no persistence beyond session]
- Escalation contact: [name + contact for critical findings]

## Known Stack

| Component | Technology | Version |
|---|---|---|
| Frontend | [e.g. React 18] | [if known] |
| Backend | [e.g. Django 4.2] | [if known] |
| Database | [e.g. PostgreSQL 15] | [if known] |
| Cloud | [e.g. AWS us-east-1] | [if known] |
| WAF / CDN | [e.g. Cloudflare] | [if known] |

## Prior Work

- Previous reports: [yes / no — if yes, reference]
- Known issues to retest: [list]
- Areas flagged by client: [list]

## Deliverables

- Format: [full report / findings list / executive summary / verbal debrief]
- Audience: [technical team / CISO / board / all]
- Deadline: [YYYY-MM-DD]
- Submission method: [email / portal / in-person]

## Gaps / Open Questions

List anything that was unclear or not confirmed during scope-grill:

- [ ] [gap 1]
- [ ] [gap 2]
