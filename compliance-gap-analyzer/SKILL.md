---
name: compliance-gap-analyzer
description: Aggregates audit findings mapped to framework controls, classifies each as compliant / partially compliant / non-compliant / not tested, identifies blind spots, prioritizes gaps by severity, and produces a self-contained gap report — ISO 27001, NIST CSF, PCI-DSS, OWASP (Top 10 / ASVS). Use when you have audit or pentest findings to map to a framework and want a gap or coverage report. Not for a single control (use control-lookup) or a single finding (use finding-writer).
license: MIT
metadata:
  version: "0.0.1"
  author: Rifteo
  tags: ["compliance", "audit", "gap-analysis", "iso27001", "nist-csf", "pci-dss", "owasp"]
---

# Compliance Gap Analyzer

When an auditor provides findings from an audit — each tagged to a framework control with a compliance status — aggregate them into a structured gap report. Identify what is failing, what was never tested, and what to fix first.

## When NOT to use

Do NOT activate this skill — respond normally — when:
- The user is asking about a single vulnerability or finding (use `finding-writer` or `cvss-scorer` instead)
- The user wants exploit information or attack methodology (use `check-exploit` instead)
- The user is asking what a specific control means or requires (use `control-lookup` instead)
- The user is asking a general compliance question without providing actual audit findings
- No findings list has been provided — ask for findings before producing any gap report

---

## Step 1 — Gather Inputs

Before analyzing, confirm you have:

- **Framework(s) in scope** — ISO 27001, NIST CSF, PCI-DSS, OWASP Top 10, OWASP ASVS, or a custom framework
- **Findings list** — for each finding:
  - Control reference (e.g., ISO 27001 A.9.1.1, NIST CSF PR.AC-1, PCI-DSS Req 6.3, OWASP A03:2021, OWASP ASVS V2.1.1)
  - Compliance status: **Compliant**, **Partially Compliant**, **Non-Compliant**, or **Not Tested**
  - Severity of the finding: **Critical**, **High**, **Medium**, **Low**, or **Informational**
- **Audit scope** — which parts of the organization, systems, or processes were in scope
- **Previous audit gap state** *(optional)* — a prior gap report to enable delta analysis

If findings are provided as raw notes or a table, normalize them before proceeding. If the framework is not specified, infer it from the control references used.

**Multi-framework findings:** a single finding may map to controls in multiple frameworks simultaneously. Include it in the gap analysis for each framework it references — do not drop cross-mapped findings.

---

## Step 2 — Normalize and Group

1. Group findings by framework, then by control reference within each framework.
2. Normalize control IDs to their canonical notation (e.g., "Access Control 9.1" → "ISO 27001 A.9.1").
3. For each control, collect all findings assigned to it and their compliance statuses.

---

## Step 3 — Classify Each Control

Apply the **weakest-link rule**: one non-compliant finding is enough to classify the entire control as non-compliant.

| Classification | Criteria |
|---|---|
| **Compliant** | All findings for this control pass; no gaps identified |
| **Partially Compliant** | Mix of compliant and partially compliant findings; control is not fully satisfied |
| **Non-Compliant** | One or more findings explicitly fail this control |
| **Not Tested** | No findings assigned to this control — it was not audited (blind spot) |

A control rated **Partially Compliant** must be treated as a gap — partial compliance is not compliance.

---

## Step 4 — Prioritize Gaps

Assign a **gap priority** to each non-compliant or partially compliant control based on two factors:

**Finding severity** (worst finding assigned to that control):

| Severity | Weight |
|---|---|
| Critical | 4 |
| High | 3 |
| Medium | 2 |
| Low | 1 |
| Informational | 0 |

**Control criticality** within the framework:

| Criticality | Weight | Examples |
|---|---|---|
| Foundational | +2 | Access control, identity management, encryption at rest/transit, incident response |
| Standard | +1 | Most operational and procedural controls |
| Supporting | 0 | Documentation, awareness, supplemental controls |

**Gap Priority Score = Finding Severity Weight + Control Criticality Weight**

| Score | Gap Priority |
|---|---|
| 5–6 | Critical — remediate within 48 hours |
| 3–4 | High — remediate within 7 days |
| 2 | Medium — remediate within 30 days |
| 0–1 | Low — schedule in next maintenance cycle |

Blind spots (Not Tested controls) are always flagged separately — they carry unknown risk and must be acknowledged regardless of priority score.

---

## Step 5 — Delta Analysis *(only if previous audit state is provided)*

Compare the current gap state against the previous audit:

| Change Type | Definition |
|---|---|
| **New gap** | Control was Compliant or Not Tested before; now Non-Compliant or Partially Compliant |
| **Closed gap** | Control was Non-Compliant or Partially Compliant before; now Compliant |
| **Persistent gap** | Control was Non-Compliant or Partially Compliant before; still is |
| **Regression** | Control was Compliant before; now Non-Compliant (flag explicitly — this is a priority signal) |
| **New blind spot** | Control was tested before; now Not Tested — scope was reduced |
| **Blind spot resolved** | Control was Not Tested before; now has findings |

Regressions must always be called out prominently — a control that passed before and now fails indicates a process breakdown, not just a gap.

---

## Output Format

Produce exactly this structure. Do not omit any section. If a section has no entries, state "None."

---

**Audit:** [Audit name or identifier, if provided]
**Framework(s):** [List all frameworks analyzed]
**Scope:** [Systems, processes, or organizational units in scope]
**Findings analyzed:** [Total count]
**Controls assessed:** [Count of controls with at least one finding]
**Analysis date:** [Today's date]

---

### Coverage Summary

| Framework | Total Controls in Scope | Tested | Not Tested (Blind Spots) | Compliant | Partially Compliant | Non-Compliant |
|---|---|---|---|---|---|---|
| [Framework] | [N] | [N] | [N] | [N] | [N] | [N] |

**Overall compliance rate:** [Compliant ÷ Tested controls, expressed as %]
**Gap rate:** [(Partially Compliant + Non-Compliant) ÷ Tested controls, expressed as %]
**Coverage rate:** [Tested ÷ Total controls in scope, expressed as %]

---

### Prioritized Gap List

*(Non-Compliant and Partially Compliant controls only, ordered by Gap Priority Score descending)*

| # | Control | Framework | Classification | Worst Finding Severity | Gap Priority | Findings Count | Remediation Target |
|---|---|---|---|---|---|---|---|
| 1 | [Control ID + name] | [Framework] | [Non-Compliant / Partially Compliant] | [Critical / High / Medium / Low] | [Critical / High / Medium / Low] | [N] | [48h / 7d / 30d / Next cycle] |

For each gap, include a one-line summary:
- **Gap:** [What is failing or insufficiently addressed]
- **Evidence:** [Finding title(s) that triggered this classification]
- **Recommended action:** [One specific, actionable remediation step]

---

### Blind Spots (Not Tested Controls)

Controls that were in scope for the framework but received no findings — their compliance status is unknown.

| Control | Framework | Criticality | Risk Note |
|---|---|---|---|
| [Control ID + name] | [Framework] | [Foundational / Standard / Supporting] | [Brief note on why this matters] |

**Recommendation:** Extend the next audit's scope to cover these controls. Foundational blind spots should be prioritized in scope planning.

---

### Compliant Controls

*(Summary only — do not list individual findings)*

| Control | Framework | Findings Count |
|---|---|---|
| [Control ID + name] | [Framework] | [N] |

---

### Delta Analysis *(omit this section entirely if no previous audit state was provided)*

**Previous audit date:** [Date]
**Comparison summary:**

| Change Type | Count | Controls |
|---|---|---|
| New gaps | [N] | [Control IDs] |
| Closed gaps | [N] | [Control IDs] |
| Persistent gaps | [N] | [Control IDs] |
| Regressions | [N] | [Control IDs — **flag each one explicitly below**] |
| New blind spots | [N] | [Control IDs] |
| Blind spots resolved | [N] | [Control IDs] |

**Regressions — immediate attention required:**
For each regressed control, state:
- **Control:** [ID + name]
- **Previous status:** Compliant
- **Current status:** [Non-Compliant / Partially Compliant]
- **Likely cause:** [What changed — new finding, scope expansion, process breakdown]
- **Action required:** [Specific step to investigate and remediate]

---

### Key Observations

3–5 concise observations that an auditor or security lead needs to know — patterns across gaps, systemic issues, highest-risk area, or scope concerns. These should not repeat what is already in the tables; they should synthesize it.

---

### Recommended Next Steps

Ordered list of actions, highest priority first:

1. [Specific action — who does what, by when]
2. ...

---

## Rules

- Apply the weakest-link rule consistently — a control with one failing finding is Non-Compliant, not Partially Compliant
- Partially Compliant is a gap — never treat it as passing
- Not Tested controls must always appear in the Blind Spots section — omitting them understates risk
- Never calculate the compliance rate over total controls in scope — only over tested controls; use the coverage rate separately to surface the blind spot risk
- Regressions must always be flagged explicitly and separately from new gaps — they signal process breakdown, not just missing work
- Cross-framework findings must appear in every framework they reference — do not deduplicate across frameworks
- The output must be complete and self-contained — a reader who did not attend the audit must be able to understand the full compliance posture from this report alone
- If the findings list is empty or no controls are mapped, do not produce a gap report — ask the auditor to provide the findings with control mappings before proceeding
- If the framework is not one of ISO 27001, NIST CSF, PCI-DSS, OWASP Top 10, or OWASP ASVS, apply the same methodology using the control references provided — the framework-agnostic structure is always valid
- For OWASP Top 10: treat each risk category (A01–A10) as a control; findings map to whichever category the vulnerability falls under
- For OWASP ASVS: treat each verification requirement (VX.Y.Z) as a control; use the ASVS level (L1/L2/L3) as a proxy for control criticality when computing gap priority
