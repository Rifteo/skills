---
name: hexstrike-forge
description: Full HexStrike engagement workflow — sequences the right tools for your target type, kills false positives, and forges confirmed findings into a professional report. Use when the HexStrike MCP is active and you want a structured engagement, or you have raw HexStrike output to turn into findings.
license: MIT
metadata:
  version: "1.2.0"
  author: AuditGuard
  tags: ["hexstrike", "pentest", "workflow", "triage", "automation"]
---

# HexStrike Forge

HexStrike executes. AuditGuard refines. This skill sequences HexStrike tools intelligently, filters noise down to confirmed findings, and assembles a professional report.

**Rule:** No exploit, no finding. Every HexStrike output is a hypothesis until triage confirms it.

## Startup

### 1. Scope gate
Run `scope-grill` skill if installed (`npx auditguard-skills add scope-grill` to install). If not installed, ask these three questions before any active testing and do not proceed until all are answered:

1. Do you have written authorization to test this target?
2. What is in scope and what is explicitly out of scope?
3. Any restrictions? (no DoS, time windows, excluded hosts?)

If authorization cannot be confirmed, stop. Do not proceed.

### 2. Tool pre-check
Call `server_health`. Diff available tools against the phases in `references/tool-sequences.md` for the identified target type. Note any capability gaps upfront — do not discover them mid-engagement.

### 3. Output rule
Strip ANSI escape codes and extract `stdout` from every tool response before reading it. See `references/known-tool-bugs.md` for handling broken or misbehaving tools.

### 4. Multi-target
If the user provides multiple targets (IP range, list of domains, CIDR block): run Phase 1 across all targets first, consolidate the target map, then run phases 2–4 in sequence. Do not run a full engagement per target in isolation — cross-target findings (e.g. same CVE on multiple hosts) count as one finding with multiple affected assets.

---

## Phase 1 — Orient

Run a port scan on top 100 ports. Derive target type from what is open. Load the matching sequence from `references/tool-sequences.md`.

| Signal | Target type |
|---|---|
| Port 80/443, web service, domain name | Web application |
| JSON endpoints, `/api/`, REST, GraphQL | API |
| IP range, ports 22/25/445/3389, no web UI | Network / infrastructure |
| S3 URLs, cloud provider headers, metadata endpoints | Cloud |
| Mobile app + backend URL, thick client traffic | Mobile / thick client |

If ambiguous across two types, run both. If the target is unresponsive (all ports filtered, no response), document it, note possible WAF/CDN, and attempt a DNS and passive recon pass before concluding.

**WAF/CDN detection:** if HTTP responses show inconsistent behavior, Cloudflare/Akamai/Fastly headers, or payloads are silently dropped — note the WAF/CDN, adapt the scan sequence to use lower-noise tools first, and flag WAF presence in the engagement summary.

---

## Phase 2 — Strike

Follow the capability sequence for the target type from `references/tool-sequences.md`.

- Passive before active
- Unauthenticated before authenticated
- Triage after each capability phase before moving to the next
- If a tool times out with partial output, triage what was returned — do not discard
- If a port changes state mid-engagement, wait 60s and retry once before marking inconclusive

---

## Phase 3 — Triage

Apply rules from `references/triage-rules.md` to every flag. Assign each item: **CONFIRM-HIGH**, **CONFIRM-MED**, **INVESTIGATE**, or **DISCARD**.

Target: fewer than 20% of raw flags become CONFIRM. If confirming more, triage is too loose.

After triage:
- Cross-reference every confirmed CVE against CISA KEV (`references/triage-rules.md` section 3)
- Run chain detection (`references/triage-rules.md` section 2)
- Log every CONFIRM item in the evidence ledger (`references/triage-rules.md` section 5)

---

## Phase 4 — Forge

**Authenticated gate:** before authenticated tests, surface explicitly: *"Authenticated testing requires credentials. Provide them to continue, or type SKIP."* Do not silently skip.

For each CONFIRM-HIGH and CONFIRM-MED finding:
1. Assign finding ID (F-01, F-02 ...) in descending severity order
2. Write up using `finding-writer` skill if installed — it produces a full structured pentest finding (`npx auditguard-skills add finding-writer` to install). If not installed, use the template in `references/triage-rules.md` section 6.

INVESTIGATE items go into open threads in the handoff — not findings.

---

## Phase 5 — Deliver

Choose based on what the user needs:

- **Full report** → `pentest-report` skill if installed (`npx auditguard-skills add pentest-report`) — it assembles a complete professional report. If not installed, produce: Executive Summary → Risk Summary (finding count by severity, KEV flags) → Findings sorted by CVSS → Open Threads → Appendix (tool output).
- **Continue later** → `engagement-handoff` skill if installed (`npx auditguard-skills add engagement-handoff`) — it produces a structured handoff document. If not installed, produce: confirmed scope, evidence ledger, open threads with next steps, retest date, and any credentials or context the next session needs.
- **Remediation plans** → `remediation-planner` skill per finding if installed (`npx auditguard-skills add remediation-planner`) — it produces prioritized fix plans. If not installed, for each finding produce: immediate action (hours), short-term fix (days), long-term hardening (weeks), and a verification step to confirm the fix.
- **Quick brief** → no sub-skill needed. Produce 5 lines: scope, test duration, finding count by severity, highest-risk finding title, recommended immediate action.

Executive Summary must always include: total findings by severity, KEV findings flagged separately, any chains discovered, and one sentence on overall risk posture.

---

## Rules

- Never report without triage — flags are hypotheses
- Never run active phases without confirmed scope from `scope-grill`
- Deduplicate: same endpoint + same issue from multiple tools = one finding
- If a tool is broken, apply the rule from `references/known-tool-bugs.md` — never retry a broken invocation
- Keep the user informed at every phase transition
