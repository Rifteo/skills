---
name: engagement-handoff
description: Documents the current state of an active pentest engagement so the next agent session can continue without losing context — findings, coverage, next steps, and open threads
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["pentest", "audit", "handoff", "engagement", "session"]
---

# Engagement Handoff

Create a compact handoff document that captures exactly where the current engagement stands. A fresh agent session reading this file should be able to continue without asking any questions.

Reference existing artifacts (ENGAGEMENT.md, findings already written) rather than duplicating them.

## When to Use

- User says "handoff", "save progress", "pick this up next session", "summarize the engagement"
- Context window is getting long and work needs to continue in a fresh session
- End of a testing day / shift change

## Process

1. **Scan the session** — review all findings identified, tools run, targets tested, and threads opened
2. **Check for ENGAGEMENT.md** — if it exists, reference it; do not repeat scope/target info already there
3. **Capture findings** — list each finding by title + severity; do not rewrite them in full
4. **Map coverage** — what was tested, what was skipped, what was partially tested
5. **List open threads** — suspected vulnerabilities not yet confirmed, areas that need deeper testing, follow-up requests
6. **Write next steps** — ordered list of what to do first in the next session
7. **Save** — write to `HANDOFF.md` in the current directory

## Output Format

Use the template in `references/handoff-template.md`.

## Rules

- Keep it under 100 lines — if it's longer, you're duplicating instead of referencing
- Never include credentials, tokens, or sensitive evidence in the handoff file
- Next steps must be specific enough that the next agent can start without any additional context
- If ENGAGEMENT.md exists, open the handoff with: "Continue from: see ENGAGEMENT.md for scope and target details"
