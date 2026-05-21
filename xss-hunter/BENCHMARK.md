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
| Time | ~8 min | ~2 min | **🟢 -75%** |
| XSS findings (out of 10) | 7 | 9 | **🟢 +29%** |
| Output quality | Complete | Complete | |

---

## Scenario

Custom lab with 10 planted XSS vulnerabilities — same target, same model, agent runs until it can find no more issues.

```
Hunt for all XSS vulnerabilities in this lab and find as many as possible
```

---

## Execution Results

### Without Skill — 7/10 XSS found in ~8 minutes

![XSS without skill](../.github/assets/XSS-no-skill.png)

The agent found **7 out of 10** XSS vulnerabilities but took approximately **8 minutes**. It missed 3 issues — including DOM-based and stored variants — due to an incomplete coverage strategy and redundant steps.

### With Skill — 9/10 XSS found in ~2 minutes

![XSS with skill](../.github/assets/xss-skill.png)

With `xss-hunter` loaded, the agent found **9 out of 10** XSS vulnerabilities in approximately **2 minutes**. The structured methodology covered reflected, stored, DOM-based, and blind XSS in a single efficient pass — 4× faster with better coverage.

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Hunt for all XSS vulnerabilities in this lab and find as many as possible

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
> Hunt for all XSS vulnerabilities in this lab and find as many as possible

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

The skill delivered **more findings in less time**: 9/10 XSS in ~2 minutes vs 7/10 in ~8 minutes. The time difference (4×) comes from the skill's pre-ordered test sequence — reflected first, then stored, then DOM-based — eliminating the redundant recon the agent ran without guidance. The coverage difference (2 extra findings) comes from the skill explicitly covering DOM-based and stored variants that the improvised run skipped.

---
