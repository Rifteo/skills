---
skill: compliance-gap-analyzer
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: compliance-gap-analyzer
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Partial | Complete | 🟢 +2 level(s) |
| Turns to complete | 1 | 1 | ⚪ 0 |
| Response tokens | ~4,317 | ~2,661 | 🟢 -38% |
| Total time | 88s | 57s | 🟢 -35% |
| User effort | Low | Low | ⚪ Low |

## Scenario

Auditor dumps raw findings the day before a closing meeting — needs a structured gap report fast

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded.

### Turn 1

**Prompt**

ISO 27001 audit at a 45-person SaaS client, closing meeting tomorrow morning. here's what i have:

- no documented access control policy → non-compliant critical
- onboarding ok but zero offboarding process → partially compliant high
- prod servers not patched for 4 months → non-compliant high
- SDLC documented, mandatory code review, SAST in place → compliant
- identification of applicable laws → not tested, out of scope

framework ISO 27001:2022, generate the full gap report

**Response**

# ISO 27001:2022 Gap Assessment Report

**Client:** [SaaS Client Name]
**Organization Size:** 45 employees
**Assessment Date:** [Date]
**Report Version:** 1.0
**Prepared by:** [Auditor Name / Firm]
**Distribution:** Restricted – Management and Audit Stakeholders Only

---

## 1. Executive Summary

This report presents the findings of an ISO 27001:2022 gap assessment conducted across [Client Name]'s information security management system. The assessment evaluated selected controls against the requirements of ISO/IEC 27001:2022 and its normative Annex A, which references ISO/IEC 27002:2022.

Of the four domains tested, **two are non-compliant**, **one is partially compliant**, and **one is fully compliant**. One domain was designated out of scope for this engagement and was not assessed. The findings include one critical gap that presents immediate organizational and certification risk, and two high-severity findings that require remediation prior to any certification audit.

**Overall Compliance Posture: INSUFFICIENT FOR CERTIFICATION**

| Rating | Count |
|---|---|
| Compliant | 1 |
| Partially Compliant | 1 |
| Non-Compliant | 2 |
| Not Tested / Out of Scope | 1 |

---

## 2. Scope and Methodology

### 2.1 Assessment Scope

This gap assessment covered the following control domains as agreed during the scoping phase:

- Access control policy and management
- Identity lifecycle management (onboarding and offboarding)
- Vulnerability and patch management for production infrastructure
- Secure development lifecycle (SDLC) practices
- Legal, regulatory, and contractual compliance identification

### 2.2 Out of Scope

The identification of applicable laws, regulations, and contractual requirements was explicitly agreed as out of scope for this engagement. This area is noted for completeness but no finding has been raised. **It is recommended that this domain be included in the next assessment cycle** given its direct relevance to ISO 27001:2022 Clause 4.2 and Annex A con

*[truncated]*

## With Skill — 1 turn, complete

Same prompt, with `compliance-gap-analyzer` loaded as system context.

### Turn 1

**Prompt**

ISO 27001 audit at a 45-person SaaS client, closing meeting tomorrow morning. here's what i have:

- no documented access control policy → non-compliant critical
- onboarding ok but zero offboarding process → partially compliant high
- prod servers not patched for 4 months → non-compliant high
- SDLC documented, mandatory code review, SAST in place → compliant
- identification of applicable laws → not tested, out of scope

framework ISO 27001:2022, generate the full gap report

**Response**

# Compliance Gap Report

**Audit:** ISO 27001:2022 Readiness Audit
**Framework(s):** ISO 27001:2022
**Scope:** All in-scope controls; legal/regulatory identification explicitly excluded
**Findings analyzed:** 5
**Controls assessed:** 4 (1 explicitly excluded from scope)
**Analysis date:** 2025-07-14

---

## Coverage Summary

| Framework | Total Controls in Scope | Tested | Not Tested (Blind Spots) | Compliant | Partially Compliant | Non-Compliant |
|---|---|---|---|---|---|---|
| ISO 27001:2022 | 5 | 4 | 1 | 1 | 1 | 2 |

**Overall compliance rate:** 25% (1 of 4 tested controls)
**Gap rate:** 75% (3 of 4 tested controls — includes Partially Compliant)
**Coverage rate:** 80% (4 of 5 in-scope controls tested)

> **Note for closing meeting:** Three-quarters of tested controls are failing. With one control excluded from scope and the compliance rate at 25%, this client is not in a position to pursue certification without a structured remediation programme.

---

## Prioritized Gap List

*Ordered by Gap Priority Score, highest first.*

---

### Gap 1 — Access Control Policy

| Field | Value |
|---|---|
| **Control** | ISO 27001:2022 A.5.15 — Access Control |
| **Classification** | Non-Compliant |
| **Worst Finding Severity** | Critical |
| **Control Criticality** | Foundational (+2) |
| **Gap Priority Score** | 4 + 2 = **6 → Critical** |
| **Remediation Target** | **Within 48 hours** |

- **Gap:** No documented access control policy exists. Without a policy, there is no baseline against which access rights can be granted, reviewed, or revoked — every downstream access control is effectively ungoverned.
- **Evidence:** "No documented access control policy — Non-Compliant, Critical"
- **Recommended action:** Draft and obtain management sign-off on an Access Control Policy this week. A minimal viable policy must at minimum define: who can grant access, the principle of least privilege, mandatory access reviews, and the handling of privileged accounts. Pair with Gap 2 immedi

*[truncated]*

## What changed

Both completed in 1 turn, but the quality on that first turn differed: **Partial** without the skill vs **Complete** with it. The skill enforces a consistent methodology from the first prompt.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
