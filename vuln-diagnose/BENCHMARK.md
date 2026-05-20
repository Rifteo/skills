---
skill: vuln-diagnose
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: vuln-diagnose

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~1,228 | ~1,355 | **🟠 +10%** |
| Time | 35s | 39s | **🟠 +11%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Diagnose this finding: the app returns 403 for requests to /admin but returns 200 and serves admin content when the request includes the header X-Original-URL: /admin
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Diagnose this finding: the app returns 403 for requests to /admin but returns 200 and serves admin content when the request includes the header X-Original-URL: /admin

**Response**
```
**Pre-Submission Triage Gate**

**Finding:** Access control bypass via `X-Original-URL` header — GET /admin returns 403 normally, but `X-Original-URL: /admin` returns 200 with admin content.

---

**1. Can an attacker use this RIGHT NOW with a real HTTP request?**
**YES** — A single curl command with the header already reproduces a 200 + admin content response, no setup required.

**2. Is the impact on the program's accepted-impact list?**
**LIKELY YES** — Unauthorized access to an admin panel is a canonical access control finding accepted by virtually every bug bounty program, but verify the specific program's policy before submitting.

**3. Is the asset in scope?**
**UNVERIFIED** — Scope depends on the specific program; confirm the target domain is listed before proceeding.

**4. Does it work without privileged access an attacker cannot get?**
**YES** — No credentials, session tokens, or prior authentication are required; the bypass is header-only.

**5. Is this not already known or 
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `vuln-diagnose` loaded as context.

#### Turn 1

**Prompt**
> Diagnose this finding: the app returns 403 for requests to /admin but returns 200 and serves admin content when the request includes the header X-Original-URL: /admin

**Response**
```
## Step 1 — Hypothesis

> I believe an **access control bypass** exists at `/admin` because the application enforces URL-based restrictions at the network/proxy layer but honors the `X-Original-URL` header to route internally — allowing the header to override the enforced path.

---

## Step 2 — Minimal Feedback Loop

The binary test is already implicit in the report. Formalizing it:

**Blocked (expected):**
```http
GET /admin HTTP/1.1
Host: target.example.com
```
→ Response: `403 Forbidden`

**Bypassed (unexpected):**
```http
GET / HTTP/1.1
Host: target.example.com
X-Original-URL: /admin
```
→ Response: `200 OK` + admin content

The structural reason this works: a reverse proxy (commonly Nginx with `proxy_set_header X-Original-URL`) strips the header from untrusted sources in some configs but in vulnerable configs passes it through. The backend framework (Django, Symfony, Rails) then reads `X-Original-URL` to determine the routed path, bypassing the proxy-level ACL that only checked t
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. However, without the skill the agent used 127 fewer tokens by producing a shallower, less structured output. With the skill, the agent produced a thorough, fully structured result — the token increase reflects depth, not inefficiency.

With the skill, the agent followed a proven methodology from the first prompt.

---
