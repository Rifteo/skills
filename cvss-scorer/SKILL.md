---
name: cvss-scorer
description: Computes an exact CVSS v3.1 base score and vector from a vulnerability description. Infers metrics from context (IDOR+UUID=AC:H, XSS=S:C, pre-auth=PR:N, etc.), flags every ambiguous metric, asks the auditor one targeted question per ambiguity, and shows a conditional score table (score for each possible value) before locking the final vector.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["cvss", "scoring", "severity", "pentest", "audit", "vulnerability"]
---

# CVSS Scorer

Produce an exact CVSS v3.1 base score and vector from a vulnerability description.

## Process

1. Parse the vulnerability description
2. Infer each of the 8 metrics using the rules below
3. Flag every metric that cannot be determined from context
4. For each ambiguous metric: state why it's ambiguous + ask one question + show conditional score table
5. Once all metrics are resolved, compute the exact score using the formula
6. Output the full vector, score, severity, and per-metric justification

Never guess an ambiguous metric silently. Always surface it.

---

## Metric Inference Rules

### Attack Vector (AV)

| Value | When to apply |
|---|---|
| **Network (N)** | Exploitable over any network (internet, intranet, internal LAN). Default for all web application vulnerabilities — even internal-only apps. |
| **Adjacent (A)** | Requires attacker on the same physical/logical network segment: Bluetooth, WiFi, local subnet with no routing. |
| **Local (L)** | Requires local OS session (shell, RDP, local file). No network path. |
| **Physical (P)** | Requires physical device access. |

> Default assumption for web vulns: **AV:N**. Only override if description explicitly limits access.

---

### Attack Complexity (AC)

| Value | When to apply |
|---|---|
| **Low (L)** | No special conditions. Attacker can exploit reliably and repeatedly. |
| **High (H)** | Requires conditions outside the attacker's direct control. |

**Context-based inference:**

| Context | AC |
|---|---|
| IDOR with **numeric / sequential IDs** | AC:L — trivially enumerable |
| IDOR with **UUID / GUID** | AC:H — random, not enumerable |
| Race condition required | AC:H |
| Requires MitM or network interception | AC:H |
| Requires non-default target configuration | AC:H |
| Requires knowledge of internal values (e.g. unpublished API key) | AC:H |
| Standard web vuln (SQLi, XSS, SSRF, CSRF, path traversal, auth bypass) | AC:L |
| Insecure deserialization | AC:H — reliable RCE via deserialization is rarely trivial |

---

### Privileges Required (PR)

| Value | When to apply |
|---|---|
| **None (N)** | Unauthenticated. No account needed. |
| **Low (L)** | Requires any valid account (standard user, guest, basic API key). |
| **High (H)** | Requires elevated or administrative privileges. |

**When the description does not specify authentication state — this is the most common ambiguity. Ask:**

> "Does exploiting this vulnerability require the attacker to be authenticated? (unauthenticated / any account / admin only)"

Then show a conditional table (see Conditional Scoring section).

---

### User Interaction (UI)

| Value | When to apply |
|---|---|
| **None (N)** | No victim action required. Attacker exploits directly. |
| **Required (R)** | A victim must take an action (click a link, visit a page, submit a form, open a file). |

**Context-based inference:**

| Context | UI |
|---|---|
| Stored XSS | UI:N — victim just visits the page passively |
| Reflected XSS | UI:R — victim must click attacker-crafted URL |
| DOM XSS via URL fragment | UI:R |
| CSRF | UI:R — victim must be tricked into submitting a request |
| Clickjacking | UI:R |
| Direct API / server-side vulnerability (SQLi, SSRF, RCE, IDOR, path traversal, XXE) | UI:N |
| Malicious file that must be opened | UI:R |
| Phishing-dependent chain | UI:R |

---

### Scope (S)

| Value | When to apply |
|---|---|
| **Unchanged (U)** | Exploitation is confined to the vulnerable component. The attacker gains no access to resources outside it. |
| **Changed (C)** | Exploitation impacts resources beyond the vulnerable component — different security authority, different system, or the victim's browser context. |

**Context-based inference:**

| Context | S |
|---|---|
| **XSS (any type)** | S:C — attacker JS runs in the victim's browser under a different security origin |
| **SSRF** | S:C — server makes requests to other internal/external systems |
| **XXE with SSRF capability** | S:C |
| **SSTI leading to RCE** | S:C — code executes at OS level, outside the app |
| **RCE** | S:C — OS-level impact outside the application scope |
| **Template injection → OS command** | S:C |
| **SQL injection (data only)** | S:U — impact stays within the database component |
| **IDOR** | S:U |
| **Path traversal (read/write files)** | S:U — stays on the same server |
| **Auth bypass** | S:U — access stays within the same application |
| **CSRF** | S:U — action is within the same application |
| **Insecure deserialization → RCE** | S:C |
| **LFI (file read only)** | S:U |
| **LFI → RCE via log poisoning** | S:C |
| **Open redirect** | S:U (no code execution cross-origin) |

> When exploitation could chain to other systems but doesn't by default, note both possibilities and ask.

---

### Confidentiality (C), Integrity (I), Availability (A)

| Value | C | I | A |
|---|---|---|---|
| **None (N)** | No data read | No data modification | No service impact |
| **Low (L)** | Limited data access (non-sensitive, partial, indirect) | Limited modification of non-critical data | Reduced performance, partial disruption |
| **High (H)** | Full read of sensitive data (PII, credentials, secrets, tokens) | Write/delete/corrupt critical data, code execution | Full DoS, crash, resource exhaustion |

**Context-based inference:**

| Context | C | I | A |
|---|---|---|---|
| RCE | H | H | H |
| SQLi — full DB dump | H | N | N |
| SQLi — full DB dump + write | H | H | N |
| SQLi — DROP / truncate | N | H | H |
| IDOR — read another user's profile/PII | H | N | N |
| IDOR — update another user's data | L | H | N |
| IDOR — delete another user's data | N | H | H |
| Stored XSS — session hijack | H | L | N |
| Stored XSS — defacement only | N | L | N |
| SSRF — internal metadata / creds | H | N | N |
| SSRF — blind (confirms connectivity only) | L | N | N |
| CSRF — account modification | N | H | N |
| Path traversal — read /etc/passwd | H | N | N |
| Path traversal — write webshell | H | H | H |
| XXE — local file read | H | N | N |
| Auth bypass — read access | H | N | N |
| Auth bypass — full account takeover | H | H | N |
| Open redirect | L | N | N |
| DoS / crash | N | N | H |
| Resource exhaustion | N | N | H |

> Impact depends heavily on **what data is in scope** and **what actions are possible**. If the description is vague (e.g. "read user data" — is it PII or just a username?), ask before assigning High.

---

## Conditional Scoring

When one or more metrics are ambiguous, do NOT pick a value silently. Instead:

1. Identify every ambiguous metric
2. Ask the auditor one clear, direct question per ambiguity
3. Show a conditional score table: for each possible value of the ambiguous metric, show the full vector and score — all other metrics fixed

**Format:**

```
Ambiguous: Privileges Required (PR)
Cannot determine from the description whether authentication is required.

→ Does the attacker need to be logged in to exploit this?

| PR | CVSS Vector | Score | Severity |
|----|-------------|-------|----------|
| None (unauthenticated) | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 | Critical |
| Low (any user) | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N | 8.1 | High |
| High (admin only) | CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N | 6.5 | Medium |
```

If **multiple metrics are ambiguous**, show the conditional table for all combinations. If combinations exceed 6 rows, group by the highest-impact metric and note the others.

---

## CVSS v3.1 Formula

Use this to compute scores exactly. Do not estimate.

**Metric weights:**

| Metric | Value | Weight |
|---|---|---|
| AV | Network | 0.85 |
| AV | Adjacent | 0.62 |
| AV | Local | 0.55 |
| AV | Physical | 0.20 |
| AC | Low | 0.77 |
| AC | High | 0.44 |
| PR (S:U) | None | 0.85 |
| PR (S:U) | Low | 0.62 |
| PR (S:U) | High | 0.27 |
| PR (S:C) | None | 0.85 |
| PR (S:C) | Low | 0.68 |
| PR (S:C) | High | 0.50 |
| UI | None | 0.85 |
| UI | Required | 0.62 |
| C / I / A | None | 0.00 |
| C / I / A | Low | 0.22 |
| C / I / A | High | 0.56 |

**Calculation steps:**

```
ISCBase = 1 − [(1 − C) × (1 − I) × (1 − A)]

If Scope Unchanged:
  ISC = 6.42 × ISCBase

If Scope Changed:
  ISC = 7.52 × [ISCBase − 0.029] − 3.25 × [ISCBase − 0.02]^15

Exploitability = 8.22 × AV × AC × PR × UI

If ISC ≤ 0:
  Base Score = 0.0
Else if Scope Unchanged:
  Base Score = Roundup(min(ISC + Exploitability, 10))
Else if Scope Changed:
  Base Score = Roundup(min(1.08 × (ISC + Exploitability), 10))

Roundup(x) = ceiling(x × 10) / 10
```

**Severity thresholds:**

| Score | Severity |
|---|---|
| 0.0 | None |
| 0.1 – 3.9 | Low |
| 4.0 – 6.9 | Medium |
| 7.0 – 8.9 | High |
| 9.0 – 10.0 | Critical |

> Note: PR weight changes depending on Scope. When S:C, use the S:C row for PR. Always determine Scope before computing PR weight.

---

## Common Vulnerability Reference

Quick-reference vectors for typical findings. Treat as starting points — always verify against the actual description.

| Vulnerability | Vector | Score | Severity | Key assumption |
|---|---|---|---|---|
| Unauth RCE (web) | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H | 10.0 | Critical | Pre-auth, network-reachable |
| Auth RCE (low priv) | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H | 9.9 | Critical | Any account |
| SQLi — full dump, pre-auth | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 | Critical | Pre-auth, read+write |
| SQLi — full dump, low-priv | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N | 8.8 | High | Authenticated |
| IDOR numeric, pre-auth, PII | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 | High | Sequential ID |
| IDOR UUID, pre-auth, PII | AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N | 5.9 | Medium | Random UUID |
| IDOR numeric, low-priv, PII | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N | 6.5 | Medium | Authenticated |
| IDOR UUID, low-priv, PII | AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N | 4.3 | Medium | Auth + UUID |
| Stored XSS — session hijack | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N | 8.7 | High | Low-priv stored |
| Stored XSS — low-priv, no hijack | AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N | 5.4 | Medium | Limited impact |
| Reflected XSS | AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 6.1 | Medium | Pre-auth, victim clicks |
| SSRF — internal creds/metadata | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N | 8.6 | High | Pre-auth, scope changed |
| SSRF — blind | AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N | 5.8 | Medium | Confirms connectivity |
| CSRF — account action | AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N | 6.5 | Medium | Victim must click |
| Path traversal — read /etc/passwd | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 | High | Pre-auth |
| XXE — local file read | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 | High | Pre-auth |
| XXE — with SSRF | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N | 8.6 | High | Scope changed |
| SSTI → RCE | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H | 10.0 | Critical | Pre-auth |
| JWT alg:none / weak secret | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 | Critical | Full auth bypass |
| Open redirect | AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N | 4.3 | Medium | User clicks link |
| Insecure deserialization → RCE | AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H | 9.0 | Critical | AC:H — reliable exploit is rare |
| Account takeover via broken auth | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 | Critical | Pre-auth |

---

## Output Format

Always produce this structure after all metrics are resolved:

---

**Vulnerability:** [one-line description]

**CVSS Vector:** `CVSS:3.1/AV:_/AC:_/PR:_/UI:_/S:_/C:_/I:_/A:_`

**Base Score:** [score] — **[Severity]**

**Metric Breakdown:**

| Metric | Value | Rationale |
|---|---|---|
| Attack Vector (AV) | [N/A/L/P] | [why — e.g. "web app reachable over internet"] |
| Attack Complexity (AC) | [L/H] | [why — e.g. "UUID, not enumerable"] |
| Privileges Required (PR) | [N/L/H] | [why — e.g. "endpoint requires valid session"] |
| User Interaction (UI) | [N/R] | [why — e.g. "stored XSS, victim passively triggers"] |
| Scope (S) | [U/C] | [why — e.g. "XSS executes in victim's browser context"] |
| Confidentiality (C) | [N/L/H] | [why — e.g. "exposes full user PII"] |
| Integrity (I) | [N/L/H] | [why] |
| Availability (A) | [N/L/H] | [why] |

**Score Computation:**
```
ISCBase = 1 − [(1 − C) × (1 − I) × (1 − A)] = [value]
ISC     = [formula used] = [value]
Exploit = 8.22 × [AV] × [AC] × [PR] × [UI] = [value]
Score   = Roundup(min([ISC + Exploit or 1.08×(ISC+Exploit)], 10)) = [final]
```

---

## Rules

- Compute scores using the formula, not by memory or estimation — even "obvious" scores must be verified
- Never silently pick a value for an ambiguous metric — always surface it with a conditional table
- When scope is Changed, use the S:C PR weight (not S:U) in the exploitability formula
- For chained vulnerabilities, score the full chain — the entry point's metrics drive AV/AC/PR/UI, the final impact drives C/I/A/S
- If the impact is "unknown" (e.g. "read user data" — unclear sensitivity), ask before assigning High — overstating a score is as harmful as understating it
- Self-XSS is not typically a valid finding — flag it and do not score unless it chains to something else
- For blind variants of vulns (blind SQLi, blind SSRF, blind XXE), C is L not H — the attacker cannot directly read data, only infer it
