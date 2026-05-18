# Triage Rules

Apply these rules to every HexStrike flag before promoting it to a finding. The goal: eliminate noise, keep signal. Confirm fewer than 20% of raw flags.

---

## Automatic DISCARD — Do Not Report

These patterns are noise. Discard without investigation.

| Pattern | Reason |
|---|---|
| Tool flagged but response was 404 | Resource does not exist |
| Tool flagged but response was identical to unauthenticated baseline | No actual access gained |
| "Missing header" finding where the header has no exploit path on this specific app | Low signal, not a real finding in isolation |
| Version detected but no CVE with public PoC exists | Theoretical risk only |
| Nuclei `info` severity template fired | Informational — note it, don't report it |
| SSL/TLS finding on an internal-only host | Risk context is wrong |
| Rate limiting missing on a non-sensitive endpoint | Not exploitable without other conditions |
| Redirect to same domain | Not an open redirect |
| Self-XSS (only exploitable by the victim on their own session) | No real attack path |

---

## Requires Manual Confirmation — INVESTIGATE

Do not report yet. Test manually before deciding.

| Pattern | What to do |
|---|---|
| SQLi flag with no data extraction evidence | Send `' OR '1'='1` manually, check response delta |
| XSS payload reflected in response | Verify execution in browser — reflection ≠ execution |
| IDOR flag from automated tool | Manually swap IDs between two test accounts, confirm data leak |
| SSRF flag (tool detected redirect) | Manually confirm callback to Burp Collaborator / interactsh |
| Auth bypass flag | Manually replay the request without credentials |
| Nuclei `medium` or above on a login/admin endpoint | Always manually verify |
| "Exposed file" flag (.env, .git, backup) | Fetch the file manually — confirm actual content, not 403 |

---

## Automatic CONFIRM — Fast-Track to Finding

These patterns are high-confidence. Still write up with evidence.

| Pattern | Notes |
|---|---|
| Tool returned data belonging to another test account | Confirmed IDOR — document the request/response |
| XSS payload executed `alert(document.domain)` in browser | Confirmed XSS — capture screenshot |
| SQLi returned database rows or error with schema info | Confirmed SQLi — capture response snippet |
| Unauthenticated access to authenticated-only endpoint returned data | Confirmed auth bypass |
| Credentials found in exposed file (.env, config, backup) | Critical — capture evidence, escalate immediately |
| CVE with CISA KEV match on detected version | High confidence — verify version, write up |

---

## Deduplication Rules

Multiple tools often flag the same issue. Merge into one finding.

- Same endpoint + same vulnerability class = one finding, regardless of how many tools flagged it
- List all tools that confirmed it in the Evidence section
- Use the highest-severity tool's output as the primary evidence
- Example: Nuclei + manual test both confirm XSS on `/search?q=` → one finding, two evidence sources

---

## Triage Checklist Per Flag

Before promoting any flag to CONFIRM:

- [ ] Can I reproduce it with a fresh session?
- [ ] Is the response meaningfully different from the baseline?
- [ ] Does the evidence show actual impact, not just a tool flag?
- [ ] Have I checked if a WAF or compensating control is interfering?
- [ ] Is this the same issue already confirmed on a different endpoint? (deduplicate)
