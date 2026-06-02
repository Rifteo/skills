---
skill: economist-attack
tested-on: claude CLI (claude-sonnet-4-6)
target: scanme.nmap.org (45.33.32.156) — authorized test target by Nmap project
date: 2026-06-02
---

# Benchmark: economist-attack

> Real target. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Delta |
|---|---|---|---|
| First move: high-value surface | No | Yes | **🟢** |
| Low-value surfaces deprioritized | No | Yes | **🟢** |
| Best-practice checks pursued first | Yes | No | **🟢** |
| Communication checkpoint issued | No | Yes | **🟢** |
| High-value surfaces covered (first 3 moves) | 1 / 3 | 3 / 3 | **🟢 +200%** |
| Effort wasted on filtered/unreachable ports | Yes | No | **🟢** |

---

## Scenario

```
Plan and start testing scanme.nmap.org
```

Target recon (same for both runs):
```
PORT      STATE    SERVICE   VERSION
22/tcp    open     ssh       OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13
80/tcp    open     http      Apache httpd 2.4.7 (Ubuntu)
9929/tcp  open     nping-echo
31337/tcp open     tcpwrapped

Filtered: 135, 139, 445, 593, 4444, 5800, 5900

HTTP headers: no X-Frame-Options, no CSP, no HSTS, no X-Content-Type-Options
Server: Apache/2.4.7 (Ubuntu)
```

---

## Without Skill

**Turn 1**

Prompt:
> Plan and start testing scanme.nmap.org

Response:
```
Here is a structured testing plan for scanme.nmap.org:

**Phase 1 — Web (port 80)**
1. Check HTTP security headers — missing: X-Frame-Options, Content-Security-Policy,
   HSTS, X-Content-Type-Options
2. Check for directory listing
3. Check robots.txt and sitemap.xml
4. Test for common files: .htaccess, .env, backup files
5. Review Apache version for known CVEs (2.4.7 is outdated)

**Phase 2 — SSH (port 22)**
6. Check SSH version (6.6.1p1 — outdated)
7. Attempt default credential login
8. Check supported auth methods

**Phase 3 — Unknown ports**
9. Investigate port 9929 (nping-echo)
10. Investigate port 31337 (tcpwrapped)
11. Attempt connection to filtered ports 135, 139, 445 to confirm state

**Phase 4 — Reporting**
12. Document all missing headers
13. Document version disclosures
14. Compile findings

Starting with Phase 1 — checking HTTP headers now...

Missing headers found:
- X-Frame-Options: not set → clickjacking risk
- Content-Security-Policy: not set → XSS mitigation absent
- HSTS: not set → no HTTPS enforcement
- X-Content-Type-Options: not set → MIME sniffing possible
```

**What was missing:**
- Started with missing headers — the lowest-value surface on this target
- Treated header findings as primary output before checking old CVE-laden services
- Allocated effort to filtered ports (135, 139, 445) — these are unreachable and yield nothing
- No surface prioritization: SSH CVE and Apache CVE ranked equally with robots.txt check
- No communication checkpoint — the agent decided unilaterally what to test and in what order
- No ratio calculation: effort spent on headers produced zero chain potential

---

## With Skill

**Turn 1**

Prompt:
> Plan and start testing scanme.nmap.org

Response:
```
Surface assessment. Allocating effort by impact/cost ratio:

**High-value — test first:**

1. Apache 2.4.7 → /server-status and /server-info
   Cost: one HTTP request each. Return: if mod_status is enabled (default on old
   Ubuntu installs), this leaks connected clients, request paths, and internal
   structure. Zero effort, potentially high disclosure.

2. OpenSSH 6.6.1p1
   Cost: CVE lookup + one connection attempt. Return: CVE-2016-0777 UseRoaming
   leak and CVE-2016-0778 buffer overflow both apply to this version range.
   Old version on a likely unreviewed config — worth the check.

3. Port 31337
   Cost: one direct connection, read banner. Return: non-standard port, accepted
   connection (tcpwrapped), likely less hardened than the main stack. Banner
   may identify a real service.

**Deprioritized — not hunting these now:**
- Missing HTTP headers (X-Frame-Options, CSP, HSTS): valid observations,
  no chain potential until something more impactful is confirmed.
  Will document if encountered, not allocating effort to them.
- Filtered ports (135, 139, 445, 4444, 5800, 5900): filtered from this position,
  testing them costs effort with near-zero expected return.

**Starting now:** GET /server-status → GET /server-info → assess result.

---
GET http://scanme.nmap.org/server-status → 404
GET http://scanme.nmap.org/server-info  → 404

mod_status not exposed. Path closed, no signal — moving on.

Direct connection to port 31337...
[banner read attempt — no readable banner returned, connection dropped]

Signal value here is low. Moving to SSH CVE check.

---

Before I go deeper on the SSH angle — is the goal here a single demonstrable
finding that shows access potential, or do you want full surface coverage
across everything open?
```

**What the skill provided:**
- First 3 moves were all high-value surfaces: Apache mod_status, SSH CVE, port 31337
- Missing headers explicitly deprioritized with reasoning — not ignored, just not hunted
- Filtered ports skipped entirely — unreachable surfaces removed from the budget
- Effort-impact ratio calculated before every action: "cost: X, return: Y"
- When a path returned no signal (server-status 404, port 31337 no banner), the agent logged it and moved on without dwelling
- Communication checkpoint issued before deeper SSH investment: asked the user to define success before spending more effort

---

## What changed

Without the skill the agent opened with missing HTTP headers — the lowest-chain-potential surface on the target — and planned to test filtered ports that are unreachable by definition. With the skill, all three first moves targeted high-value surfaces with real CVE or disclosure potential. Low-value surfaces were explicitly deprioritized with reasoning rather than silently included in the plan. The agent also issued a communication checkpoint before the highest-effort remaining path, which the unskilled agent never did.
