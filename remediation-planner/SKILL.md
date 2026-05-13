---
name: remediation-planner
description: Converts an audit finding into a concrete step-by-step remediation plan with effort estimates and priority
---

# Remediation Planner

When the user provides an audit finding or vulnerability, produce a structured remediation plan that a developer or system owner can act on immediately.

## Output Format

**Finding:** One-line summary of the issue being remediated

**Priority:** Critical / High / Medium / Low — based on exploitability and impact

**Estimated Effort:** Hours / Days / Weeks — realistic estimate for a competent engineer

**Short-Term Fix (Quick Win):**
What can be done immediately to reduce risk — even if it's not the permanent solution. Include specific steps.

**Long-Term Fix (Permanent Solution):**
The proper architectural or code-level fix. Include specific steps, code patterns, or configuration changes where relevant.

**Verification Steps:**
How to confirm the fix was applied correctly — what to test, what output to expect.

**Owner:** Who should implement this — Dev / DevOps / Security / IT / Management

**Dependencies:** Any blockers, prerequisites, or other teams that need to be involved

## Rules

- Be specific — "validate input server-side" is not actionable, "add server-side ownership check before returning /api/orders/{id}" is
- Always provide both a quick win and a permanent fix — security teams need immediate risk reduction while the proper fix is in progress
- If the finding lacks enough detail to write specific steps, ask one clarifying question
- Never suggest security through obscurity as a remediation
