---
name: cvss-scorer
description: Computes an exact CVSS v3.1 base score and vector from a vulnerability description. Infers metrics from context, picks the most accurate score when info is sufficient, and asks one short question only when the ambiguity would change the severity level. No noise, no tables, no formula dumps.
license: MIT
metadata:
  version: "2.0.0"
  author: AuditGuard
  tags: ["cvss", "scoring", "severity", "pentest", "audit", "vulnerability"]
---

# CVSS Scorer

Produce an exact CVSS v3.1 vector and score from a vulnerability description. Be decisive. Be accurate. Be short.

---

## When NOT to use

Do NOT produce a CVSS vector — respond normally — when:
- The user is asking what CVSS is or how it works (answer the theory question directly)
- The user wants a full risk assessment beyond CVSS — likelihood, business impact, SLAs (use `risk-assessor` instead)
- The user is asking how to fix a vulnerability (use `remediation-planner` instead)
- No specific vulnerability has been described — a score requires a concrete finding, not a hypothetical

---

## Core Behavior

- **Infer aggressively from context.** Most metrics can be determined from a good description. Do it.
- **Pick the best score when you have enough.** Do not flood with scenarios for every metric. Only surface ambiguity when it would change the severity bucket (e.g. Medium vs High) or meaningfully changes the score (≥1.0 difference).
- **Ask once, ask sharp.** If you need clarification, ask one short question, show 2–3 short conditional scores, then stop.
- **No metric-by-metric explanations.** Only explain a metric if it's non-obvious or the auditor asks. Never explain what AV, AC, PR, etc. mean unless asked.
- **No formula display.** The auditor does not need to see the math.
- **Do not assume AV:N by default.** Infer it. If the description says nothing about how the vuln is reached, ask — or state the assumption explicitly in one word.

---

## Metric Inference

### Attack Vector (AV)
- Web app, API, internet/intranet-reachable → **N**
- Same LAN / WiFi / Bluetooth required → **A**
- Local OS session required → **L**
- Physical device access required → **P**
- If not mentioned and not obvious → state "assumed AV:N (web app)" and flag it

### Attack Complexity (AC)
- IDOR with numeric/sequential ID → **L**
- IDOR with UUID/GUID → **H**
- Race condition → **H**
- MitM required → **H**
- Everything else standard → **L**

### Privileges Required (PR)
- Pre-auth / unauthenticated → **N**
- Any valid account → **L**
- Admin / elevated → **H**
- If unclear → ask (this is the most common ambiguity and always matters)

### User Interaction (UI)
- Stored XSS → **N**
- Reflected XSS, DOM XSS via URL → **R**
- CSRF, clickjacking → **R**
- Direct server-side vuln (SQLi, SSRF, RCE, IDOR, path traversal, XXE) → **N**
- File must be opened → **R**

### Scope (S)
- XSS (any type) → **C** (JS in victim browser = different security origin)
- SSRF → **C**
- XXE with SSRF → **C**
- SSTI / RCE → **C**
- LFI → RCE via log poison → **C**
- SQL injection, IDOR, path traversal, auth bypass, CSRF → **U**
- LFI (read only) → **U**
- Open redirect → **U**

### Confidentiality / Integrity / Availability
- Full read of sensitive data (PII, creds, tokens, secrets) → **C:H**
- Limited or indirect read → **C:L**
- No data exposure → **C:N**
- Write / modify / delete critical data or code execution → **I:H**
- Limited non-critical write → **I:L**
- Full DoS / crash / resource exhaustion → **A:H**
- Partial disruption → **A:L**
- Blind variants (blind SQLi, blind SSRF, blind XXE) → **C:L** not C:H (data inferred, not read)

---

## When to Ask

Only ask when the answer changes the severity bucket or the score by ≥1.0. Format: one question + 2–3 short conditional lines.

**Example — XSS impact unclear:**

> Can this XSS access the session cookie / lead to account takeover, or is HttpOnly set?
>
> - ATO possible (C:H/I:L): `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N` — **8.7 High**
> - No cookie, limited impact (C:L/I:L): `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N` — **5.4 Medium**

**Example — auth state unclear:**

> Is this endpoint pre-auth or does it require a valid session?
>
> - Pre-auth (PR:N): `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` — **9.1 Critical**
> - Any user (PR:L): `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` — **8.1 High**

If the auditor cannot answer, pick the most **technically accurate** option given available context — lean toward what the description implies, not the worst case.

---

## Output Format

```
CVSS:3.1/AV:_/AC:_/PR:_/UI:_/S:_/C:_/I:_/A:_
Score: X.X — Severity
```

Add a short note **only** for metrics that are non-obvious, were assumed, or could surprise the auditor. Skip the rest.

**Example output:**

```
CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N
Score: 4.3 — Medium
```
> AC:H — UUID-based IDOR, not enumerable. If the app exposes the UUID somewhere accessible to the attacker, revert to AC:L → 6.5 Medium.

---

## Common Patterns (internal reference — do not dump to output)

| Vulnerability | Typical Vector | Score |
|---|---|---|
| Unauth RCE (web) | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H | 10.0 Critical |
| Auth RCE any user | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H | 9.9 Critical |
| SQLi full dump pre-auth | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 Critical |
| SQLi full dump low-priv | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N | 8.8 High |
| IDOR numeric pre-auth PII | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 High |
| IDOR UUID pre-auth PII | AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N | 5.9 Medium |
| IDOR numeric low-priv PII | AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N | 6.5 Medium |
| IDOR UUID low-priv PII | AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N | 4.3 Medium |
| Stored XSS → ATO | AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N | 8.7 High |
| Stored XSS no ATO | AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N | 5.4 Medium |
| Reflected XSS | AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 6.1 Medium |
| SSRF internal creds | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N | 8.6 High |
| SSRF blind | AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N | 5.8 Medium |
| CSRF state change | AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N | 6.5 Medium |
| Path traversal read | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 High |
| XXE file read | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 High |
| XXE + SSRF | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N | 8.6 High |
| SSTI → RCE pre-auth | AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H | 10.0 Critical |
| JWT alg:none / weak secret | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 Critical |
| Open redirect | AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N | 4.3 Medium |
| Insecure deserialization RCE | AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H | 9.0 Critical |
| Account takeover broken auth | AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 9.1 Critical |

---

## Rules

- Self-XSS is not a valid standalone finding — flag it, do not score unless it chains
- For chained vulns: use the entry point's AV/AC/PR/UI and the final step's C/I/A/S
- When scope is Changed, use S:C weights for PR in the formula
- Blind variants (blind SQLi, blind SSRF, blind XXE) → C:L not C:H
- Never explain what CVSS metrics mean unless asked
- Never show the score formula or intermediate math in the output
