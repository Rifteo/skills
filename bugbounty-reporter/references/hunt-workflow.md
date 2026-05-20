# Hunt Workflow

A structured 7-phase workflow for a complete engagement. Execute phases sequentially. Do not advance to the next phase until the current phase gate passes.

---

## Phase 1: SCOPE

Define the attack surface before touching anything.

- [ ] Read the full program brief and all in-scope asset definitions
- [ ] List all in-scope domains, wildcards, and IP ranges
- [ ] List all explicitly out-of-scope assets
- [ ] Identify accepted impact types (RCE, SQLi, stored XSS, etc.)
- [ ] Note the program's never-submit list (self-XSS, rate limiting without impact, etc.)
- [ ] Identify any special rules: no automated scanning, no DoS, no social engineering

**Gate:** Can you state in one sentence what you are allowed to test and what you are not?

---

## Phase 2: RECON

Map the attack surface without touching application logic.

- [ ] Enumerate subdomains (passive: crt.sh, dnsx, subfinder; active: brute-force wordlist)
- [ ] Identify live hosts and HTTP services
- [ ] Fingerprint technologies: server headers, JS frameworks, CMS, CDN
- [ ] Collect historical URLs via Wayback Machine and Common Crawl
- [ ] Enumerate endpoints from JS bundles (LinkFinder, relative-url-extractor)
- [ ] Identify API base paths and versioned endpoints
- [ ] Check for exposed git repos, config files, and debug endpoints

**Gate:** Do you have a list of confirmed live endpoints to prioritize?

---

## Phase 3: RANK

Prioritize targets by likelihood of payout. Do not start hunting everywhere.

| Priority | Signal |
|---|---|
| P1 | Authentication, payment, admin functions, file upload |
| P2 | Account settings, OAuth flows, email/phone verification |
| P3 | Search, export, API endpoints with object IDs |
| P4 | Static pages, logout, public-facing read-only content |

Pick 3 to 5 P1 targets to test first. Do not skip to P3 before exhausting P1.

**Gate:** Do you have a ranked shortlist of 3 to 5 high-priority targets?

---

## Phase 4: HUNT

Execute testing against ranked targets.

For each target:
1. Identify the input surface: URL params, JSON body, headers, cookies, file uploads
2. Apply the relevant disclosed pattern (see `references/disclosed-patterns/`)
3. Check the chain signal table (see `references/chain-signals.md`) for companion bugs
4. Document every request and response for every positive signal

Testing order for web applications:
- Authorization: IDOR, privilege escalation, horizontal access
- Authentication: login, password reset, session management
- Injection: SQLi, XSS, XXE, SSTI, command injection
- Business logic: price manipulation, rate limit bypass, verification skip

**Gate:** Do you have at least one candidate finding with a confirmed HTTP request that reproduces it?

---

## Phase 5: VALIDATE

Confirm every candidate finding passes the pre-submission triage gate before writing any report.

Run the 7-question triage gate from the main SKILL.md:
1. Can an attacker use this RIGHT NOW with a real HTTP request?
2. Is the impact on the program's accepted-impact list?
3. Is the asset in scope?
4. Does it work without privileged access an attacker cannot get?
5. Is this not already known or documented behavior?
6. Can impact be proved beyond "technically possible"?
7. Is this not on the program's never-submit list?

Any NO answer = kill or hold. Do not report anything that fails this gate.

For each confirmed finding:
- [ ] Reproduce from a fresh incognito session
- [ ] Capture the full reproduction chain (screenshots + HTTP logs)
- [ ] Run the chain signal check: is there a companion bug?
- [ ] Compute CVSS 3.1 base score

**Gate:** Every finding in your list passed all 7 triage questions and is reproducible in under 10 minutes.

---

## Phase 6: REPORT

Write the report using the finding-writer skill structure.

Required fields for each finding:
- Title: [Vuln Type] on [Asset] allows [Impact]
- Severity: Critical / High / Medium / Low
- CVSS 3.1 score and vector string
- Description: what it is and why it matters (2 to 3 sentences)
- Steps to reproduce: numbered, copy-paste ready
- Evidence: screenshot or HTTP log for each step
- Impact: concrete attacker capability (not "could potentially")
- Recommendation: specific fix, not "sanitize input"
- References: CWE number + OWASP link

Platform-specific requirements:
- HackerOne: CVSS score required, markdown supported
- Bugcrowd: use their severity taxonomy (P1-P4), not CVSS labels
- Intigriti: CVSSv3 required, evidence screenshot required for each step
- YesWeHack: OWASP category required

**Gate:** Report is under 600 words. Reproduction is copy-paste ready from the report alone.

---

## Phase 7: CHECKPOINT

Review before submitting.

- [ ] Re-read the program brief - is the asset still in scope?
- [ ] Has this exact finding been disclosed publicly for this program?
- [ ] Is the CVSS score defensible? Would a triage analyst agree?
- [ ] Did you check the companion chain bugs and document what you tested?
- [ ] Is the report self-contained? Can a triage analyst reproduce without asking you anything?
- [ ] Strip any PII or credentials from screenshots and HTTP logs

Submit only after all checkboxes pass.
