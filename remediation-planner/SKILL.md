---
name: remediation-planner
description: Converts a security finding or vulnerability into a prioritized, step-by-step remediation plan with effort estimates per step. Use when you have a specific finding and need a fix plan — "how do we fix this?". Not for exploiting, scanning, or theoretical questions with no concrete finding.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["remediation", "security", "planning", "findings", "effort"]
---

# Remediation Planner

Given any security finding, vulnerability, or bug description, produce a prioritized, step-by-step remediation plan. Each step includes a title, a concise explanation, and an effort estimate so the team knows what to do and how hard it is.

## When NOT to use

Do NOT apply this skill — respond normally without the remediation plan format — when:
- The user is asking how to **exploit** a vulnerability (use the relevant attack skill instead)
- The user is asking about reconnaissance, scanning, or enumeration
- The user is asking a theoretical/conceptual question with no specific finding to remediate

## Process

1. **Understand the finding** — identify the vulnerability class, root cause, and affected component from the input. If the input is too vague to produce actionable steps, ask one clarifying question.
2. **Order steps by priority** — immediate fixes first (stop the bleeding), then root cause fixes, then hardening to prevent recurrence.
3. **Write each step** — title, max 2-line description, effort label.
4. **Do not over-engineer** — focus on the minimum set of steps needed. Avoid padding with generic security advice unrelated to the finding.

## Effort Scale

| Label | Meaning |
|---|---|
| **Low** | Quick config change, one-line fix, or a well-understood patch — hours to a day |
| **Medium** | Requires code refactoring, moderate testing, or cross-team coordination — days to a week |
| **High** | Architectural change, significant engineering work, or complex coordination — weeks or more |

## Output Format

Use this exact structure. Repeat the step block for each step.

---

**Remediation Plan: [Finding Title]**

**Step [N] — [Short Action Title]**
[What to do and why — maximum 2 lines.]
`Effort: Medium`

---

## Example Output

**Remediation Plan: SQL Injection in /api/search**

**Step 1 — Replace String Concatenation with Parameterized Queries**
Rewrite all database queries using prepared statements or an ORM with parameter binding. Apply across every database-facing function, not just the reported endpoint.
`Effort: Low`

**Step 2 — Add Centralized Input Validation**
Introduce a validation layer that enforces expected types and formats before input reaches the data layer. Use an allowlist approach for structured fields (IDs, enums, dates).
`Effort: Medium`

**Step 3 — Restrict Database User Permissions**
Grant the application's DB user only the permissions it needs (SELECT/INSERT/UPDATE). Remove DROP, CREATE, and admin grants, and create separate read/write roles if the app allows it.
`Effort: Low`

**Step 4 — Deploy a WAF Rule as a Compensating Control**
Add a WAF rule to detect and block common SQL injection patterns while the code fix is being rolled out. This is a temporary measure — not a substitute for Steps 1–3.
`Effort: Medium`

---

## Rules

- Steps must be actionable — a developer should be able to start implementing without follow-up questions
- Keep descriptions to 2 lines maximum — no padding, no restating the problem
- Effort label only — no explanation of why it's that level
- Order matters: immediate/easy wins first, architectural fixes last
- If a step is a temporary compensating control, label it clearly as such
- Do not include unrelated hardening advice — stay focused on the reported finding
- If no concrete remediation exists (e.g. a fundamental design flaw), state that clearly and describe the trade-offs of available mitigations instead
