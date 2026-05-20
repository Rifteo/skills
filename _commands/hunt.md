Start a structured hunt on this target: $ARGUMENTS

Work through each phase sequentially. Do not advance until the phase gate passes.

---

## Phase 1: SCOPE
- Read the program brief, list in-scope assets and accepted impact types
- Note the never-submit list and any special rules (no automated scanning, no DoS)
Gate: State in one sentence what you are allowed to test and what you are not.

## Phase 2: RECON
- Enumerate subdomains (crt.sh, subfinder, brute-force)
- Identify live hosts, technologies, CDN, JS frameworks
- Collect historical URLs via Wayback Machine
- Enumerate endpoints from JS bundles
Gate: List confirmed live endpoints to prioritize.

## Phase 3: RANK
Prioritize targets:
- P1: Authentication, payment, admin, file upload
- P2: Account settings, OAuth, email/phone verification
- P3: Search, export, API endpoints with object IDs
- P4: Static pages, public read-only content

Pick 3-5 P1 targets. Do not move to P3 before exhausting P1.
Gate: Name 3-5 high-priority targets to test first.

## Phase 4: HUNT
For each target: map input surface, apply the relevant vuln class methodology, check chain signals for companion bugs, document every positive signal with full request/response.

Testing order: authorization first, then authentication, then injection, then business logic.
Gate: At least one candidate finding with a confirmed HTTP request that reproduces it.

## Phase 5: VALIDATE
Run the 7-question triage gate on every candidate:
1. Can an attacker use this RIGHT NOW with a real HTTP request?
2. Is the impact on the program's accepted-impact list?
3. Is the asset in scope?
4. Does it work without privileged access an attacker cannot get?
5. Is this not already known or documented behavior?
6. Can impact be proved beyond "technically possible"?
7. Is this not on the program's never-submit list?

Gate: Every finding passed all 7 questions and reproduces in under 10 minutes.

## Phase 6: REPORT
Write each finding using: Title, Description, Steps to Reproduce, PoC, Impact, Remediation, Severity.
Report under 600 words. Reproduction must be copy-paste ready from the report alone.
Gate: Report is complete and self-contained.

## Phase 7: CHECKPOINT
- Re-read program brief, confirm asset still in scope
- Confirm finding not already publicly disclosed for this program
- Strip PII and credentials from screenshots and HTTP logs
- Confirm a triage analyst can reproduce without asking you anything
