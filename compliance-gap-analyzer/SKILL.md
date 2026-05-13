---
name: compliance-gap-analyzer
description: Compares an organization's current controls against a compliance framework and identifies gaps, partially met controls, and priorities
---

# Compliance Gap Analyzer

When the user provides information about their current security controls, policies, or practices — and specifies a target framework — identify what is missing, partially implemented, or fully met.

## Output Format

**Framework:** ISO 27001 / SOC2 / NIST CSF / PCI-DSS / GDPR / DORA / NIS2 / Other

**Assessment Summary:**
- Fully Met: X controls
- Partially Met: X controls
- Not Met: X controls
- Not Applicable: X controls

**Gap Table:**

| Control | Status | Gap Description | Priority |
|---|---|---|---|
| [Control ID + Name] | ✅ Met / ⚠️ Partial / ❌ Not Met / N/A | What is missing or insufficient | High / Medium / Low |

**Priority Gaps (Top 5):**
The most critical gaps to address first — based on risk exposure and audit failure likelihood.
For each: what's missing, why it matters, and one concrete first step to close it.

**Quick Wins:**
Controls that can be fully met with low effort — policy updates, configuration changes, documentation.

**Recommended Roadmap:**
Phase 1 (0–30 days): quick wins and critical gaps
Phase 2 (30–90 days): medium priority gaps
Phase 3 (90+ days): structural or long-term improvements

## Rules

- Ask for the specific framework version if it matters (e.g. ISO 27001:2022 vs 2013)
- If the user provides incomplete information, mark controls as "Unable to assess" rather than assuming
- Always distinguish between a control that doesn't exist vs one that exists but isn't documented
- Focus the roadmap on what is realistic given the organization's size and resources
