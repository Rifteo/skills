---
name: finding-writer
description: Converts raw pentest notes, logs, or observations into a structured audit finding ready for a security report
license: MIT
metadata:
  version: "0.0.1"
  author: AuditGuard
  tags: ["pentest", "audit", "security", "findings", "reporting"]
---

# Finding Writer

Convert raw pentest notes, log snippets, vulnerability descriptions, or any unstructured observation into a complete, report-ready audit finding.

## When to Use

- User pastes raw notes, tool output, or a quick observation from a pentest
- User describes a vulnerability and needs it structured for a report
- User has a log snippet or HTTP request/response that reveals a security issue
- User wants to turn a single-line note into a client-deliverable write-up

## Process

1. **Parse Input**: Identify the vulnerability class, affected component, and any evidence provided
2. **Clarify if Needed**: If the input is ambiguous or missing critical context, ask ONE clarifying question before proceeding — do not stall
3. **Assess Severity**: Score based on actual exploitability and impact in context, not just the vulnerability class — see `references/severity-guide.md`. Run `scripts/cvss-scorer.py` to produce the CVSS v3.1 vector and base score.
4. **Tag the Finding**: Run `scripts/cwe-search.py <keyword>` to look up the correct CWE ID and OWASP category for the vulnerability type.
5. **Write the Finding**: Fill every field using only information provided or derivable from the input
6. **Flag Gaps**: Mark any field without sufficient input as `[TO BE ADDED]`

## Output Format

**Title:** Short, action-oriented title describing the vulnerability (e.g. "Unauthenticated Access to Admin Endpoint")

**Severity:** Critical / High / Medium / Low / Informational
*Justification: one sentence explaining the rating based on exploitability and impact*

**CVSS:** `CVSS:3.1/AV:_/AC:_/PR:_/UI:_/S:_/C:_/I:_/A:_` — [score] ([rating])

**Description:** What the vulnerability is, where it was found, and why it matters. 2–4 sentences, technical but readable by a non-specialist.

**Evidence:** The specific proof — URL, HTTP request/response snippet, log line, screenshot reference, or step-by-step reproduction steps. Be precise. If not provided: `[TO BE ADDED]`

**Impact:** What an attacker can achieve by exploiting this. Be concrete — data exposure, privilege escalation, account takeover, RCE, lateral movement, etc.

**Recommendation:** What to fix and exactly how. Not "fix the access control" — but "validate object ownership server-side on every request to `/api/resource/{id}` before returning data."

**References:** CWE ID, OWASP Top 10 category, and/or CVE if applicable. See `references/owasp-cwe-map.md` for common mappings.

## Rules

- Never invent evidence — if the user didn't provide it, mark it `[TO BE ADDED]`
- Severity reflects actual exploitability and business impact in context, not the vulnerability class alone
- Recommendations must be specific enough that a developer can implement the fix without follow-up questions
- Ask at most one clarifying question per finding
- Do not add disclaimers, caveats, or legal boilerplate to the output
- See `references/examples.md` for a complete example at each severity level
