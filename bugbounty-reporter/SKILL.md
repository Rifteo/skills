---
name: bugbounty-reporter
description: Converts raw bug bounty findings into a complete, triage-ready report — clear description, numbered reproduction steps, self-contained PoC, risk, and remediation. Writes for triagers who are not necessarily security experts. Covers all vuln classes and major platforms (HackerOne, Bugcrowd, Intigriti, YesWeHack).
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["bug-bounty", "reporting", "h1", "bugcrowd", "intigriti", "pentest"]
---

# Bug Bounty Reporter

Turn raw findings into a report that gets triaged, not closed. Bug bounty reports fail for two reasons: the triager can't reproduce it, or can't understand why it matters. This skill fixes both.

## When to Use

- User has a confirmed bug bounty finding and needs to write it up
- User says "write this up", "report this", "format this for H1/Bugcrowd/Intigriti"
- User has raw notes, a request/response, or a PoC and needs a submission-ready report

## Process

1. Parse the finding — vulnerability class, endpoint, parameter, auth state, observed behavior
2. If critical context is missing, ask **one** question before writing — never stall with multiple questions
3. Check: is this self-XSS, clickjacking on a low-value page, or missing header with no exploit path? If yes, flag it as likely N/A before writing
4. Write the report using the structure below
5. Mark any missing field `[TO ADD]` — never invent evidence

---

## Report Structure

### Title
Format: `{Bug class} in {scope/endpoint} through {parameter or element} Leads To {impact}`

```
✓ IDOR in api.target.com/invoices/{id} through integer ID Leads To Full Customer Data Exposure
✓ Stored XSS in target.com/profile through bio field Leads To Account Takeover
✗ XSS found
✗ Security issue in API
```

### Description
2–4 sentences. No filler. Start with the finding.

Template: `[Vuln class] exists in [location]. The application [root cause]. An attacker can [impact].`

### Steps to Reproduce
Numbered, exact, reproducible by someone who has never seen the app.
- State the auth context at step 1
- If two accounts are needed, say so at step 1
- Include exact URL, method, parameter, and value at each step
- End with: "Observe: [what proves the vulnerability]"

### Proof of Concept
Use the format that fits:
- **HTTP request/response** — preferred for API and web vulns
- **curl command** — for easy reproduction
- **Payload + trigger location** — for injection vulns

Rules: redact real PII, truncate long tokens, note if destructive actions used test accounts only.

### Risk
One paragraph or bullets. Name the actual outcome — no vague statements.
See `references/vuln-reference.md` for risk statements by vuln class.

### Remediation
Specific and actionable — not "fix the access control".
See `references/vuln-reference.md` for remediation by vuln class.

### Severity
See `references/severity-platform.md` for severity criteria and CVSS guidance.
Run `scripts/cvss-scorer.py` to compute the CVSS vector and score if required by the program.

---

## Rules

- Never invent evidence — mark missing fields `[TO ADD]`
- One clarifying question max before writing
- Do not overstate impact to chase a higher bounty — it damages credibility
- If HttpOnly blocks cookie theft in an XSS, state what's actually achievable
- Self-XSS with no escalation path = not reportable — flag it, suggest a chain if one exists
- Check for duplicates before submitting — see `references/severity-platform.md`
- No disclaimers or legal boilerplate in the report
