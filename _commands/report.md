Write a submission-ready bug bounty report for this finding: $ARGUMENTS

Use the structure below. Mark any missing field [TO ADD] — never invent evidence.

---

## Title
Format: {Bug class} in {scope/endpoint} through {parameter or element} Leads To {impact}

## Description
2-4 sentences. Start with the finding. Template: [Vuln class] exists in [location]. The application [root cause]. An attacker can [impact].

## Steps to Reproduce
Numbered, exact, reproducible by someone who has never seen the app.
- State auth context at step 1
- If two accounts needed, say so at step 1
- Include exact URL, method, parameter, and value at each step
- End with: "Observe: [what proves the vulnerability]"

## Proof of Concept
Preferred: HTTP request/response. Alternatively: curl command or payload + trigger location.
Redact real PII. Truncate long tokens.

## Impact
Name the actual outcome. No vague statements like "could lead to". State what an attacker gains.

## Remediation
Specific and actionable. Not "fix the access control" — name the exact control to add or fix.

## Severity
Assign: Critical / High / Medium / Low with a one-line justification.
Include CVSS 3.1 score if the platform requires it (HackerOne, Intigriti).

---

## Platform notes
- HackerOne: CVSS score required, markdown supported
- Bugcrowd: use P1/P2/P3/P4 labels, not Critical/High
- Intigriti: CVSSv3 required, screenshot required for each reproduction step
- YesWeHack: OWASP category required
