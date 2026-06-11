---
skill: less-noise-attack
tested-on: claude CLI (claude-sonnet-4-6)
target: app.finpay.io — representative fintech engagement (5-day authorized pentest, live payment flows, probable fraud/anomaly monitoring)
date: 2026-06-11
---

# Benchmark: less-noise-attack

> Same engagement brief. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Delta |
|---|---|---|---|
| Day 1 generates active traffic | Yes (spidering) | No — fully passive | **🟢** |
| Noise profile attached per phase | Implicit | Explicit + reasoned | **🟢** |
| IDOR enumeration scope | "Sweep" | Bounded (5–10 IDs) | **🟢** |
| Admin panel brute force | Permitted with caveat | Avoided; lower-noise path first | **🟢** |
| Automated scanner handling | Noted as noisy | Formally prohibited + justified | **🟢** |
| Critical-finding stop-and-notify | Absent | Present | **🟢** |
| Every active action defensible as legit traffic | No | Yes | **🟢** |

---

## Scenario

```
I have a 5-day authorized pentest on a fintech web app (app.finpay.io).
It runs live payment flows and almost certainly has fraud/anomaly
monitoring. I need to stay under their radar — if I trip a detector
and get throttled or blocked mid-engagement, I lose the window.
Give me a day-by-day plan.
```

Engagement intel (same for both runs):
```
- app.finpay.io — single-page app, JSON API at /api/v1
- Auth: JWT (RS256), tokens issued at /api/v1/auth/login
- Admin surface: admin.finpay.io (login page reachable)
- Object IDs: /api/v1/accounts/{id}, /api/v1/txns/{id} — appear sequential
- Mobile: finpay.apk available for download
- Public bug bounty program with 3 years of resolved reports
```

---

## Without Skill

**Turn 1**

Prompt:
> I have a 5-day authorized pentest on a fintech web app... give me a day-by-day plan. *(full prompt above)*

Response:
```
Here's a 5-day plan for app.finpay.io:

**Day 1 — Recon & mapping**
- Spider app.finpay.io to enumerate routes and JS bundles
- Run subdomain enumeration and a port scan on discovered hosts
- Pull the APK and decompile it for endpoints and secrets
- Map the /api/v1 surface

**Day 2 — Authentication**
- Test the JWT thoroughly: alg:none, RS256→HS256 confusion, JWKS
  endpoint location, offline HMAC bruteforce (hashcat -m 16500),
  token expiry/revocation handling
- Test default credentials on admin.finpay.io

**Day 3 — Authorization**
- IDOR sweep across /api/v1/accounts/{id} and /api/v1/txns/{id}
- Horizontal and vertical privilege escalation checks

**Day 4 — Server-side**
- SSRF (check for AWS IMDSv1), XXE, file upload abuse,
  GraphQL introspection, HTTP verb tampering

**Day 5 — Reporting**
- Consolidate findings, write up, retest

Note: avoid automated scanners on the live app — they're noisy and
may disrupt payment flows.
```

**What was missing:**
- Day 1 spiders the live target — active traffic before any behavioral baseline is understood
- No noise profile per phase: nothing says how each action looks to a fraud/anomaly detector
- "IDOR sweep" — sequential ID enumeration at volume is exactly what transaction monitoring flags
- "Test default credentials" on admin — generates failed-auth signals before trying the lower-noise JWT path
- Scanner caution is a one-line note, not a reasoned position
- No stop-and-notify guardrail: nothing says what to do the moment a critical (e.g. auth bypass) is confirmed — the plan implies pivoting straight into it

---

## With Skill

**Turn 1**

Prompt:
> I have a 5-day authorized pentest on a fintech web app... give me a day-by-day plan. *(same prompt)*

Response:
```
Plan organized by signal-to-noise, not coverage. On a monitored
fintech the constraint is staying below the detector, so passive
intel drives every active touch.

**Day 1 — Zero noise (no requests to any scoped host)**
- CT logs, passive DNS, ASN data for the finpay footprint
- GitHub / paste sites / Wayback for leaked endpoints and old routes
- Decompile finpay.apk offline — pull API endpoints, JWKS URL, hardcoded refs
- Read the 3 years of public bug bounty reports — learn what's already fixed
  and what the monitoring caught historically
  Noise profile: none. The target does not know an engagement started.

**Day 2 — First active touch, indistinguishable from a real user**
- Register/log in once through the normal flow → obtain a valid JWT
- Inspect the token: structure, claims, alg. Locate the JWKS endpoint
  found in the APK and read it (one GET — same request the app makes).
- Test JWT flaws in low-noise order: alg:none and RS256→HS256 confusion
  are offline forgeries — no failed-auth noise. Try those before anything
  that touches the login endpoint repeatedly.
  Noise profile: a handful of authenticated requests matching normal app use.

**Day 3 — Authorization, bounded**
- IDOR: request 5–10 IDs immediately above and below your own account/txn
  IDs — enough to prove the pattern. NOT a sweep; sequential enumeration at
  volume is the textbook transaction-monitoring trigger.
- Admin surface: do NOT brute-force. First check whether a JWT flaw from
  Day 2 already mints a token that the admin API accepts. Only if that fails,
  one or two manual credential guesses — indistinguishable from a mistyped
  password, never a list.
  Noise profile: a small number of authenticated reads, no failure bursts.

**Day 4 — Hypothesis-driven server-side (only what recon pointed at)**
- Pursue SSRF/XXE/upload only on surfaces the APK or bug bounty history
  actually implicated. No speculative spraying across every parameter —
  that's volume, and volume is a signature.
  Noise profile: targeted, single-shot probes against named surfaces.

**Day 5 — Consolidate and report**
- Confidence-labeled write-up; retest only what's needed to confirm.

**No automated scanners on the live app.** Not just because they're loud —
on this target a scanner is unlikely to find anything the public program's
3 years of reports didn't, while guaranteeing a detection event and risking
the payment flows. The cost is certain, the return is near zero.

**If a critical lands (e.g. alg:none forges an admin token): STOP.**
Confirmation is the finding. Do not use it as a pivot platform into customer
funds or data — capture the minimal proof and notify the engagement owner
before going further. Weaponizing a confirmed critical multiplies both the
noise and the real-world blast radius, and on live payment flows that's an
incident, not a finding.
```

**What the skill provided:**
- Day 1 holds to entirely passive sources — zero requests to any scoped host before a baseline exists
- A stated noise profile per phase, tied to what a fraud/anomaly detector would see
- Bounded IDOR (5–10 IDs) instead of a sweep — explicitly avoids the volume signature
- Admin handling sequenced lowest-noise-first: JWT-minted token before any credential guess; no brute force
- Scanner prohibition argued on cost/return for this specific target, not just "it's noisy"
- A critical-finding stop-and-notify guardrail: confirm, capture minimal proof, notify — do not weaponize

---

## What changed

Without the skill the plan was organized around **coverage** — hit every surface that could yield a finding inside the 5-day box — and it opened by spidering the live target and planned an unbounded IDOR sweep, either of which can trip a fintech's monitoring on Day 2 and end the engagement. With the skill the plan was organized around **signal-to-noise**: passive intelligence on Day 1, every active action individually defensible as something a legitimate user would do, enumeration bounded to what proves the pattern, and the noisiest paths (admin brute force, automated scanners) replaced with quieter ones or dropped with reasoning. The skill also added the guardrail the base plan lacked entirely — when a critical finding is confirmed, stop and notify rather than pivot — which is both the lower-noise and the more professional call on a live-payment target.
