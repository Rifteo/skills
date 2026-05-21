---
skill: ssti-hunter
tested-on: claude CLI (claude-sonnet-4-6)
date: 2026-05-20
---

# Benchmark: ssti-hunter

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~3,475 | ~2,241 | **🟡 -36%** |
| Time | 105s | 65s | **🟡 -38%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Could you find SSTI in this PortSwigger lab https://portswiggerlab.net
```

---

## Execution Results

### Without Skill — SSTI found and exploited (slower)

![SSTI without skill](../.github/assets/SSTI-no-skill.png)

The agent found and exploited the SSTI vulnerability but took a less direct path — it spent extra turns enumerating the template engine before committing to a payload, resulting in a longer time to exploit.

### With Skill — SSTI found and exploited (faster)

![SSTI with skill](../.github/assets/SSTI-skill.png)

With `ssti-hunter` loaded, the agent followed a systematic polyglot detection sequence and reached confirmed exploitation faster. Same result, less time — the skill eliminated guesswork on payload ordering and engine fingerprinting.

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Could you find SSTI in this PortSwigger lab https://portswiggerlab.net

**Response**
```
# Structured Hunt: SSTI on target.com — Report Generation

---

## Phase 1: SCOPE

**Assumed program context** (no brief provided — applying standard bug bounty defaults):

| Item | Assumption |
|---|---|
| In-scope asset | `target.com` and its subdomains |
| Accepted impact | RCE, data exfiltration, auth bypass, privilege escalation |
| Never-submit | DoS/DDoS, brute force, automated scanning without permission, social engineering |
| Special rules | No automated scanning, no destructive payloads on prod data |

**Gate:** You are allowed to test `target.com` web application features (specifically the report generation / PDF export surface) for injection vulnerabilities; you are **not** allowed to run automated scanners, cause denial of service, or exfiltrate real user data.

---

## Phase 2: RECON

### Target surface from the brief
The brief already narrows the attack surface precisely:
- Feature: **report generation**
- Sink: **PDF rendering engine** (likely Jinja2/Twig/Freemarker/Ve
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `ssti-hunter` loaded as context.

#### Turn 1

**Prompt**
> Could you find SSTI in this PortSwigger lab https://portswiggerlab.net

**Response**
```
I'll walk through the SSTI Hunter methodology applied to this specific attack surface: the report name field reflected in PDF output.

---

## Target Analysis

**Surface:** Report name → rendered into PDF via a server-side template engine
**Risk:** PDF generators (WeasyPrint, wkhtmltopdf, Puppeteer) almost always use a template engine under the hood — Jinja2, Twig, FreeMarker, ERB, EJS, and Thymeleaf are the most common.
**Blind factor:** Output appears in a PDF, not raw HTML — time-based and OOB confirmation matter here.

---

## Phase 1 — Confirm Reflection

Before probing for evaluation, confirm the field is reflected in the PDF at all.

```
Report name: SSTI_CANARY_1337
```

Download the generated PDF and verify the string appears. If it does, the field is live.

---

## Phase 2 — Detection Probes

Submit each payload as the report name. Download the PDF and look for the **evaluated result** (e.g. `49`), not the literal string.

```
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}
{{7*'7'}}
... [truncated]
```

---

## What changed

Both runs found and exploited the SSTI. The difference is **speed and precision**: without the skill, the agent spent extra time guessing the template engine before picking payloads. With the skill, it used a deterministic polyglot detection sequence and reached confirmed exploitation faster — no wasted turns, no engine guessing. In a time-boxed engagement, that gap matters.

---
