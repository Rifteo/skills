---
skill: clickjacking-hunter
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: clickjacking-hunter

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~5,179 | ~3,608 | **🟡 -30%** |
| Time | 103s | 71s | **🟡 -31%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Test target.com for clickjacking — the fund transfer page and account settings page are the primary high-value targets
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Test target.com for clickjacking — the fund transfer page and account settings page are the primary high-value targets

**Response**
```
Tools weren't approved — I'll deliver the complete hunt as a self-contained runbook with exact commands and PoC code you execute directly.

---

## Phase 1: SCOPE

**Gate:** Test target.com web application for clickjacking via HTTP header analysis and iframe PoC; no automated scanning, no DoS, no out-of-scope third-party services.

---

## Phase 2: RECON

Run these commands yourself to gather live data:

```bash
# Subdomain enumeration via certificate transparency
curl -s "https://crt.sh/?q=%.target.com&output=json" | jq -r '.[].name_value' | sort -u

# Technology fingerprint
curl -sI https://target.com | grep -iE "server|x-powered-by|x-frame-options|content-security-policy|cf-ray|x-cache"

# Historical URLs — fund transfer and settings paths
curl -s "https://web.archive.org/cdx/search/cdx?url=target.com/*&output=text&fl=original&collapse=urlkey" | grep -iE "transfer|fund|send|payment|settings|account|profile"

# JS bundle endpoint harvest
curl -s https://target.com | grep -oP 'src="[^
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `clickjacking-hunter` loaded as context.

#### Turn 1

**Prompt**
> Test target.com for clickjacking — the fund transfer page and account settings page are the primary high-value targets

**Response**
```
Curl to external hosts isn't being approved in this environment. I'll deliver the complete assessment package — commands to run yourself, pre-built PoCs for both endpoints, and a ready-to-fill report template.

---

## Phase 1 — Header Check Commands

Run these yourself (logged in, same browser session not needed for headers):

```bash
# Check both endpoints for framing protections
for path in /transfer /account/settings; do
  echo "=== target.com$path ==="
  curl -sI "https://target.com$path" | grep -i "x-frame-options\|content-security-policy\|HTTP/"
  echo ""
done
```

**Interpret results:**

| Result | Verdict |
|---|---|
| `X-Frame-Options: DENY` or `SAMEORIGIN` | Protected (unless CSP overrides with weaker policy) |
| `Content-Security-Policy: ... frame-ancestors 'none'` | Protected |
| Neither header present | **Vulnerable — build PoC** |
| Only JS frame-busting found (see 1.3 below) | Bypassable — use `sandbox` attribute |

```bash
# Also check for JS frame-busting on both endp
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
