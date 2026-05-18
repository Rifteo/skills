---
name: vuln-diagnose
description: Builds a deterministic, reproducible proof-of-concept for a suspected vulnerability before writing a finding — eliminates false positives and produces airtight evidence
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["pentest", "exploit", "poc", "validation", "evidence"]
---

# Vulnerability Diagnose

A suspected vulnerability is not a finding. Before writing anything, build a deterministic reproduction case. If you cannot reproduce it reliably, you cannot report it.

Inspired by the principle: *a fast, deterministic, agent-runnable pass/fail signal is a superpower.*

## When to Use

- User has a hunch or a partially-confirmed vulnerability
- Tool output flagged something but it needs manual validation
- User wants to confirm a finding before writing it up
- User says "I think there's an IDOR here", "this looks like XSS", "not sure if this is exploitable"

## Process

### Step 1 — State the Hypothesis

Write one sentence: "I believe [vulnerability type] exists at [endpoint/component] because [observed behaviour]."

This is the claim. Everything that follows either confirms or disproves it.

### Step 2 — Build the Feedback Loop

Create the minimal test case that produces a binary YES/NO answer:
- An HTTP request that succeeds when it shouldn't
- A payload that executes when it shouldn't
- A response that contains data it shouldn't

The test must be:
- **Reproducible** — same result every time
- **Minimal** — only the essential input, no noise
- **Unambiguous** — pass is clearly different from fail

If you can't build this test case, the hypothesis is not testable yet. Stop and gather more information.

### Step 3 — Test Alternate Explanations

Before confirming, rule out:
- Caching (replay the request — is the result fresh?)
- Rate limiting (does it fail on the 5th attempt?)
- Session dependency (does it work with a fresh session?)
- Race conditions (does it fail on a second run?)

### Step 4 — Confirm the Impact

Actually demonstrate the worst-case impact:
- For data access: retrieve data belonging to another user
- For XSS: execute `alert(document.domain)` or exfiltrate a cookie
- For SQLi: extract a row from a table not intended to be accessible
- For privilege escalation: perform an admin action with a user token

A confirmed impact requires evidence (HTTP request + response, screenshot, extracted data).

### Step 5 — Document

Produce a **Minimal Reproduction Case**:

```
Vulnerability: [type]
Endpoint: [METHOD] [URL]
Precondition: [e.g., logged in as user A]

Request:
[exact HTTP request]

Response:
[relevant snippet proving the issue]

Confirmed impact: [what was demonstrated]
Reproducible: YES / NO (notes if flaky)
```

Then pass this to `finding-writer` to produce the full finding.

## Rules

- No exploit, no finding — Shannon's rule. If you cannot demonstrate impact, downgrade to "suspected" and label it clearly
- Never report a finding based on tool output alone without manual confirmation
- If the test is flaky (fails intermittently), investigate root cause before reporting
- One hypothesis per session — do not stack unconfirmed vulnerabilities
