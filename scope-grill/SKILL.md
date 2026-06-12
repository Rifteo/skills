---
name: scope-grill
description: Interviews the user about a pentest or audit engagement before any testing begins — capturing target, scope, rules of engagement, auth, and deliverables into a structured brief. Use when starting an engagement that isn't yet scoped, or when a target is described without scope, authorization, or deliverables.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["pentest", "audit", "scope", "planning", "engagement"]
---

# Scope Grill

Before any testing begins, interview the user to build a complete engagement brief. An untested assumption about scope or authorization invalidates findings and creates legal risk.

Ask one question at a time. Wait for the answer before moving on. Provide a recommended answer or example for each question.

## Question Sequence

Ask in this order. Skip a question only if the answer is already obvious from context.

1. **Target** — What is the exact target? (domain, IP range, application name, cloud account)
2. **Authorization** — Do you have written authorization to test this target? (required — do not proceed if no)
3. **Scope** — What is explicitly in scope? What is explicitly out of scope?
4. **Test type** — Black-box (no credentials, no source), grey-box (credentials only), or white-box (full access + source)?
5. **Accounts** — Do you have test accounts? What roles are available? (admin, user, guest, API key?)
6. **Rules of engagement** — Any restrictions? (no DoS, no phishing, no persistence, specific time windows?)
7. **Known stack** — Any known technologies? (framework, language, cloud provider, WAF, CDN?)
8. **Prior work** — Previous pentest reports, known issues, or areas to re-verify?
9. **Deliverables** — What's expected at the end? (findings list, full report, executive summary?) Who is the audience?
10. **Deadline** — When are findings due?

## Output

After all questions are answered, produce a filled **Engagement Brief** using the template in `references/engagement-brief.md`.

Save it as `ENGAGEMENT.md` in the current directory unless the user specifies otherwise.

## Rules

- Do not begin testing until authorization is confirmed
- If the user cannot confirm authorization, stop and explain the risk
- If scope is vague, flag it — an unclear scope is itself a risk
- One question at a time — do not dump the full list at once
