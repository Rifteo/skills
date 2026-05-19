# Bug Bounty Report — Blank Template

Copy this. Fill every field. Replace `[TO ADD]` with real content before submitting.

---

**Title:** `[Bug class] in [scope/endpoint] through [parameter] Leads To [impact]`

---

**Description:**

[Vuln class] exists in [location]. The application [root cause — e.g. "does not validate the user_id parameter against the authenticated session"]. An attacker can [impact — e.g. "read, modify, or delete any user's invoice by replacing the numeric ID in the request"].

---

**Steps to Reproduce:**

1. [Auth context — e.g. "Log in with any valid account" or "Create two accounts: Victim and Attacker"]
2. [Navigate to / send request to...]
3. [Action — e.g. "Replace the ID in the request with another user's ID"]
4. Send:
   ```
   [HTTP request or curl command]
   ```
5. Observe: [what proves the vulnerability]

---

**Proof of Concept:**

Request:
```
[METHOD] [PATH] HTTP/1.1
Host: [target]
Authorization: [token — truncated]
[other relevant headers]

[body if applicable]
```

Response:
```
HTTP/1.1 [status]
[relevant response snippet — redact real PII]
```

---

**Risk:**

[One paragraph or bullets. Name the actual outcome.]

---

**Remediation:**

[Specific, actionable fix. Not "fix the access control" — say exactly what to check and where.]

---

**Severity:** [Critical / High / Medium / Low]

**CVSS:** `CVSS:3.1/AV:_/AC:_/PR:_/UI:_/S:_/C:_/I:_/A:_` — [score] ([rating])

**CWE:** [CWE-XXX]
