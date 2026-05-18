---
name: hexstrike-forge
description: Full HexStrike engagement workflow — sequences the right tools for your target type, kills false positives, and forges confirmed findings into a professional report
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["hexstrike", "pentest", "workflow", "triage", "automation"]
---

# HexStrike Forge

HexStrike executes. AuditGuard refines. This skill sequences HexStrike's 150+ tools intelligently, then filters noise down to confirmed, report-ready findings.

**Rule:** No exploit, no finding. Every output from HexStrike gets triaged before it becomes a finding.

## When to Use

- HexStrike MCP is active and you want a structured engagement, not random tool runs
- User says "pentest this", "run HexStrike on X", "find vulnerabilities in Y"
- You have raw HexStrike output and need to turn it into professional findings

## Prerequisites

- HexStrike MCP must be connected
- Run `scope-grill` first if authorization and scope are not confirmed

---

## Phase 1 — Orient

Identify the target type and load the matching playbook from `references/tool-sequences.md`:

| Target type | Signals |
|---|---|
| Web application | URL, HTTP, login page, web UI |
| API | JSON endpoints, REST/GraphQL, API keys |
| Network / infrastructure | IP range, ports, services, internal hosts |
| Cloud | AWS/GCP/Azure, S3 buckets, IAM, metadata |

If the target type is unclear, ask one question before proceeding.

---

## Phase 2 — Strike

Follow the tool sequence for the identified target type exactly as defined in `references/tool-sequences.md`.

**Sequencing rules:**
- Passive tools always run before active tools
- Authenticated tests only run after unauthenticated tests
- Stop and triage after each phase before running the next — do not batch all phases at once

---

## Phase 3 — Triage

After each phase, apply triage rules from `references/triage-rules.md` to every HexStrike output.

For each flagged item, make a binary decision:

- **CONFIRM** — evidence proves exploitability → pass to Phase 4
- **INVESTIGATE** — promising but not yet proven → note as open thread, do not report yet
- **DISCARD** — false positive or informational with no attack path → discard silently

Target triage ratio: confirm fewer than 20% of raw flags. If you're confirming more than that, your triage is too loose.

---

## Phase 4 — Forge

For each CONFIRMED finding:

1. Run `finding-writer` to produce the full structured finding
2. Assign a finding ID (F-01, F-02...) in order of severity

Do not write up INVESTIGATE items. They go into the open threads section of `engagement-handoff`.

---

## Phase 5 — Deliver

When all phases are complete:

- If the user needs a full report: run `pentest-report`
- If the session needs to continue later: run `engagement-handoff`
- If findings need remediation plans: run `remediation-planner` per finding

---

## Rules

- Never report a HexStrike finding without manual triage — tool flags are hypotheses, not facts
- Never run active exploitation phases without confirmed authorization from `scope-grill`
- Deduplicate: if three tools flag the same endpoint for the same issue, that is one finding
- Keep the user informed at each phase transition — state what was found before moving on
