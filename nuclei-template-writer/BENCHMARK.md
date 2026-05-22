---
skill: nuclei-template-writer
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: nuclei-template-writer
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Good | Complete | 🟢 +1 level(s) |
| Turns to complete | 1 | 1 | ⚪ 0 |
| Response tokens | ~1,632 | ~1,585 | 🟢 -3% |
| Total time | 31s | 33s | 🔴 +7% |
| User effort | Low | Low | ⚪ Low |

## Scenario

Pentester confirmed XSS, shares the raw request — wants a Nuclei template to automate

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded.

### Turn 1

**Prompt**

confirmed reflected XSS on /search?q=:

GET /search?q=<script>alert(document.domain)</script>
Host: shop.target.com

the HTML response reflects the payload directly in the page without encoding. i want to automate detection on other client domains, make me the nuclei template

**Response**

# Nuclei Template: Reflected XSS Detection

```yaml
id: reflected-xss-search-param

info:
  name: Reflected XSS - Search Parameter (Unencoded Reflection)
  author: your-handle
  severity: medium
  description: |
    The application reflects user-supplied input from the 'q' parameter
    directly into the HTML response without output encoding, enabling
    reflected cross-site scripting attacks.
  remediation: |
    HTML-encode all user-supplied input before reflecting it in responses.
    Apply context-aware output encoding (HTML entity encoding for HTML context).
    Implement a Content Security Policy (CSP) as defense-in-depth.
  reference:
    - https://owasp.org/www-community/attacks/xss/
    - https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
  tags: xss,reflected,search,client-side
  classification:
    cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N
    cvss-score: 6.1
    cwe-id: CWE-79

# -------------------------------------------------------
# Payloads are chosen to confirm UNENCODED reflection,
# not just string reflection. Each has a unique marker.
# -------------------------------------------------------

http:
  - method: GET
    path:
      - "{{BaseURL}}/search?q={{payload}}"

    payloads:
      payload:
        # Standard script tag - baseline
        - "<script>alert(document.domain)</script>"
        # Variation: event handler (bypasses some script-tag filters)
        - "\"><img src=x onerror=alert(document.domain)>"
        # Variation: no quotes, break out of attribute context
        - "xss'><svg onload=alert(document.domain)>"
        # Variation: case/encoding evasion
        - "<ScRiPt>alert(document.domain)</ScRiPt>"
        # Variation: javascript URI
        - "javascript:alert(document.domain)"
        # Variation: template literal / no parentheses (CSP bypass probe)
        - "<script>alert`document.domain`</script>"

    stop-at-first-match: true

    matchers-condition: and
 

*[truncated]*

## With Skill — 1 turn, complete

Same prompt, with `nuclei-template-writer` loaded as system context.

### Turn 1

**Prompt**

confirmed reflected XSS on /search?q=:

GET /search?q=<script>alert(document.domain)</script>
Host: shop.target.com

the HTML response reflects the payload directly in the page without encoding. i want to automate detection on other client domains, make me the nuclei template

**Response**

The finding is Type B (request only, no response body pasted). The matcher will use the canonical XSS probe rather than a literal string from the response — I'll note that below.

---

**Step 0 — Parsed input**

| Field | Value |
|---|---|
| Method | GET |
| Path | `/search` |
| Parameter | `q` (query string) |
| Payload | `<script>alert(document.domain)</script>` |
| Auth | None detected |
| Response | Not provided — described as "reflects payload directly without encoding" |

No auth present → unauthenticated only, no login-flow template needed.

---

**Step 1 — Classified**

- **Class:** Reflected XSS
- **Severity:** Medium (unauthenticated, GET-based, requires user interaction for full exploit — matches standard severity for reflected XSS)
- **Tags:** `xss,reflected`
- **Detection method:** Response-based word match — the payload string should appear verbatim in the response body

---

**Step 2 — Detection strategy**

Two matchers combined with `and`:
1. **Word matcher** on `<script>alert(document.domain)</script>` — confirms the payload is reflected unencoded
2. **Status matcher** on `200` — ensures we're looking at a real page, not a redirect to a WAF block page or error

Word matcher is the critical one. Status is secondary — it eliminates cases where the server returns a 403/301 before the payload ever reaches the response body. Both must pass.

The payload `<script>alert(document.domain)</script>` was chosen deliberately over `<script>alert(1)</script>`:
- `document.domain` is harder to accidentally appear in a normal page response
- Reduces false positives from pages that coincidentally contain `alert(1)` in JavaScript

---

**Step 3 — Template**

```yaml
id: reflected-xss-search-q

info:
  name: Reflected XSS via search query parameter (q)
  author: custom
  severity: medium
  description: >
    The /search endpoint reflects the value of the 'q' parameter directly into
    the HTML response without encoding. An attacker can inject arbitrary script
    tha

*[truncated]*

## What changed

Both completed in 1 turn, but the quality on that first turn differed: **Good** without the skill vs **Complete** with it. The skill enforces a consistent methodology from the first prompt.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
