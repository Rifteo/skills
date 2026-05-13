---
name: executive-brief-writer
description: Converts a list of audit findings into a board-ready executive summary — one page, risk-focused, no jargon
---

# Executive Brief Writer

When the user provides audit findings, a report, or a list of vulnerabilities, produce a concise executive summary suitable for a CISO, board member, or non-technical stakeholder.

## Output Format

**Executive Summary** *(max one page)*

**Overall Risk Posture:** [Critical / High / Medium / Low] — one sentence justification

**Audit Overview:** What was audited, when, and by whom. 2-3 sentences.

**Key Findings:**
Top 3–5 findings only — the ones that matter most to leadership.
For each:
- Issue (in plain language, no technical jargon)
- Business risk (what could go wrong for the organization)
- Status (Open / In Remediation / Closed)

**Risk Summary Table:**

| Severity | Count |
|---|---|
| Critical | X |
| High | X |
| Medium | X |
| Low | X |

**Immediate Actions Required:**
2–3 bullet points — what leadership needs to decide or unblock right now

**Next Steps:**
Remediation timeline, next review date, owner

## Rules

- No CVE numbers, no CVSS scores, no technical terms in the executive section
- Translate every finding into a business consequence — not "SQL injection" but "attackers could extract the entire customer database"
- If there are more than 5 findings, group minor ones and surface only the critical and high items
- Tone must be clear and direct — executives need to act, not study
