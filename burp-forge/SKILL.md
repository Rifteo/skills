---
name: burp-forge
description: Full Burp Suite engagement workflow — configures scans for your target type, triages findings by confidence level, and forges confirmed issues into a professional report
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["burp", "burp-suite", "pentest", "web", "workflow", "triage"]
---

# Burp Forge

Burp Suite scans. AuditGuard refines. This skill sequences Burp MCP intelligently, maps Burp's confidence levels to confirmed findings, and produces report-ready output.

**Rule:** Tentative is a hypothesis. Certain is a finding. Everything in between gets manually verified.

## When to Use

- Burp Suite MCP is active and you want a structured web app engagement
- User says "scan this with Burp", "run Burp on X", "test this web app"
- You have Burp scan results and need to turn them into professional findings

## Prerequisites

- Burp Suite Pro must be running with MCP server enabled
- Run `scope-grill` first if authorization and scope are not confirmed
- Ensure target is in Burp's scope before any scanning

---

## Phase 1 — Configure

Select the scan configuration from `references/scan-configurations.md` based on target type and time available:

| Situation | Config to use |
|---|---|
| Full engagement, time available | Comprehensive web scan |
| Quick assessment or bug bounty | Lightweight + manual focus |
| API-only target | API scan config |
| Authenticated app | Crawl with credentials first |

Set scope explicitly in Burp before starting. Out-of-scope traffic must not be scanned.

---

## Phase 2 — Crawl

Before active scanning, crawl the target to map the attack surface:

1. Authenticate with all available test accounts (one per role)
2. Manually browse every feature — Burp captures traffic passively
3. Use Burp's crawler on discovered endpoints
4. Review the site map — flag any endpoints not reached by crawl

**Output:** complete site map, all endpoints, all parameters, all auth flows captured

Do not start active scanning until the crawl is complete — scanning an incomplete site map misses coverage.

---

## Phase 3 — Scan

Run active scanning per the selected configuration.

Scanning order:
1. Unauthenticated endpoints first
2. Low-privilege authenticated endpoints
3. High-privilege / admin endpoints last

Monitor scan progress. If Burp flags a **Certain / High** finding mid-scan, pause and triage it immediately — it may reveal deeper attack paths to add to scope.

---

## Phase 4 — Triage

Apply triage rules from `references/issue-triage.md` to every Burp finding.

Burp rates each issue with two dimensions — use both:

| Burp Confidence | Burp Severity | Decision |
|---|---|---|
| Certain | High / Critical | **CONFIRM** immediately |
| Certain | Medium | **CONFIRM** |
| Certain | Low / Info | **DISCARD** unless it enables another finding |
| Firm | High | **INVESTIGATE** — manual verify required |
| Firm | Medium / Low | **INVESTIGATE** |
| Tentative | Any | **INVESTIGATE** — assume false positive until proven otherwise |

Target: confirm fewer than 30% of Burp's raw issue count. Burp scanners are noisy.

---

## Phase 5 — Manual Verification

For every INVESTIGATE item:

1. Open the issue in Burp — review the request/response evidence
2. Replay the request manually in Repeater with a fresh session
3. Attempt to demonstrate actual impact (extract data, execute payload, confirm bypass)
4. If confirmed: promote to CONFIRM with the Repeater evidence
5. If not confirmed after 2 attempts: DISCARD

---

## Phase 6 — Forge

For each CONFIRMED finding:

1. Export the Burp request/response as the Evidence field
2. Run `finding-writer` to produce the full structured finding
3. Assign a finding ID (F-01, F-02...) in severity order

Burp's issue name is a starting point for the Title — rewrite it to be action-oriented:
- Burp: "Cross-site scripting (reflected)" → Finding: "Reflected XSS in Search Parameter Allows Session Hijacking"

---

## Phase 7 — Deliver

- Full report: run `pentest-report`
- Session handoff: run `engagement-handoff`
- Per-finding fixes: run `remediation-planner`

---

## Rules

- Never report a Tentative finding without manual confirmation
- Always export the raw Burp request/response as evidence — never paraphrase it
- Deduplicate: same vulnerability class on same endpoint = one finding even if Burp logged it multiple times
- Rewrite Burp's generic issue titles into specific, impact-driven titles
- Do not scan out-of-scope targets even if Burp discovers links to them
