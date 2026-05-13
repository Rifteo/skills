---
name: finding-writer
description: Converts raw pentest notes, logs, or observations into a structured audit finding ready for a report
---

# Finding Writer

When the user provides raw notes, a log snippet, a vulnerability description, or any unstructured observation, convert it into a structured audit finding using the format below.

## Output Format

**Title:** Short, action-oriented title describing the vulnerability (e.g. "Unauthenticated Access to Admin Endpoint")

**Severity:** Critical / High / Medium / Low / Informational — justify in one sentence

**Description:** What the vulnerability is, where it was found, and why it matters. 2-4 sentences, technical but clear.

**Evidence:** The specific proof — URL, request/response snippet, screenshot reference, log line, or reproduction steps. Be precise.

**Impact:** What an attacker can do if they exploit this. Be concrete — data exposure, privilege escalation, account takeover, etc.

**Recommendation:** What to fix and how. Be specific — not "fix the access control" but "validate object ownership server-side on every request to /api/resource/{id} before returning data."

**References:** Relevant CWE, OWASP category, or CVE if applicable.

## Rules

- Never invent evidence. If the user didn't provide it, mark it as [TO BE ADDED]
- Severity must reflect actual exploitability and impact, not just vulnerability class
- Keep the recommendation actionable — a developer should be able to act on it immediately
- If the input is ambiguous, ask one clarifying question before writing the finding
