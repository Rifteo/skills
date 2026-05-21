---
skill: xss-hunter
tested-on: claude CLI (claude-sonnet-4-6)
date: 2026-05-20
---

# Benchmark: xss-hunter

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~4,378 | ~1,622 | **🟢 -63%** |
| Time | 88s | 41s | **🟢 -53%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Hunt for XSS on target.com — the search parameter value is reflected in the page response and the app has a CSP header with unsafe-inline
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Hunt for XSS on target.com — the search parameter value is reflected in the page response and the app has a CSP header with unsafe-inline

**Response**
```
## Phase 1: SCOPE

**Program brief assumption for target.com**

Without a specific program brief, I'll operate under standard bug bounty defaults and flag assumptions explicitly.

| Category | Details |
|---|---|
| In-scope asset | `target.com` and subdomains (assumed) |
| Accepted impact | XSS, auth bypass, IDOR, RCE, data exposure |
| Never-submit | DoS, automated mass scanning, social engineering, physical |
| Special rules | No automated scanners against production; manual PoC only |

**Scope gate:** I am allowed to manually test `target.com` web application for injection and logic bugs affecting authenticated and unauthenticated users; I am not allowed to DoS, brute-force credentials at scale, or touch out-of-scope infrastructure.

---

## Phase 2: RECON

Running recon against `target.com` (methodology shown; adapt output to live results).

**2.1 — Subdomain enumeration**

```bash
# Certificate transparency
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq '.[].name_value'
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `xss-hunter` loaded as context.

#### Turn 1

**Prompt**
> Hunt for XSS on target.com — the search parameter value is reflected in the page response and the app has a CSP header with unsafe-inline

**Response**
```
Based on the skill methodology, here's the targeted hunt for this scenario.

---

## Context Analysis

Two key facts shape the approach:
- **Reflected parameter** → Attack 1 (Reflected XSS)
- **CSP has `unsafe-inline`** → Attack 6.1 (instant CSP bypass — inline scripts allowed)

`unsafe-inline` means `<script>alert(1)</script>` and inline event handlers are permitted by the CSP itself. No bypass needed — the policy is the vulnerability.

---

## Step 1 — Locate the Reflection Context

Inject a canary to find exactly where the value lands in the page source:

```
GET /search?q=xsstest123
```

Open DevTools → View Source → search for `xsstest123`. The surrounding HTML tells you which payload to use:

| What you see | Context | Payload shape |
|---|---|---|
| `<p>xsstest123</p>` | HTML body | `<script>` or `<img onerror>` |
| `value="xsstest123"` | HTML attribute | `" onmouseover=` or `">` |
| `var q = "xsstest123"` | JS string | `";alert(1)//` |
| `\`Hello xsstest123\`` | JS template lit
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
