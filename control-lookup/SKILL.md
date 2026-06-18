---
name: control-lookup
description: Looks up any control ID across ISO 27001, NIST CSF, PCI-DSS v4, and OWASP (Top 10 / ASVS) — returns the full control card, cross-framework mappings with confidence level, related controls, and testing hints. Use when you have a control ID, a cross-framework mapping question, or a plain-language search for the control covering a topic (e.g. MFA, patch management).
license: MIT
metadata:
  version: "0.0.1"
  author: Rifteo
  tags: ["compliance", "controls", "framework-mapping", "iso27001", "nist-csf", "pci-dss", "owasp"]
---

# Control Lookup

When a user provides a control ID, a control name, or a plain-language description of a control objective, identify it, return its full details, and map it across ISO 27001, NIST CSF, PCI-DSS v4, and OWASP (Top 10 / ASVS).

## Step 1 — Parse the Input

Accept any of the following input forms:

| Input form | Example |
|---|---|
| Control ID — ISO 27001 | A.8.2, A.9.1.1, 5.15 (2022 notation) |
| Control ID — NIST CSF | PR.AC-1, DE.CM-7, ID.AM-2, GV.OC-01 (CSF 2.0) |
| Control ID — PCI-DSS v4 | Req 7.1.2, 10.2.1, 6.3 |
| Control ID — OWASP Top 10 | A01:2021, A03:2021 |
| Control ID — OWASP ASVS | V2.1.1, V4.3.2, V7.1.1 |
| Control name or keyword | "least privilege", "patch management", "MFA", "encryption at rest", "injection" |
| Plain-language objective | "access should be revoked when an employee leaves" |

**If the input is ambiguous** (e.g., "Control 5" could be ISO 27001 clause 5 or NIST CSF category), list all candidates and ask the user to confirm before proceeding.

**Normalize** the control ID to its canonical notation before outputting:
- ISO 27001: use Annex A notation for 2022 (`A.5.x`) and 2013 (`A.x.x.x`); note the edition
- NIST CSF: use Function.Category-Subcategory (e.g., `PR.AC-1`); note whether CSF 1.1 or 2.0
- PCI-DSS: use `Requirement X.Y.Z`; note v3.2.1 or v4.0 if relevant
- OWASP Top 10: use `AXX:YYYY` (e.g., `A01:2021`); note the year edition
- OWASP ASVS: use `VX.Y.Z` (e.g., `V2.1.1`); note the ASVS version (4.0 or 5.0)

---

## Step 2 — Control Card

Produce the full control details for the identified control:

- **ID:** canonical control reference
- **Framework:** name and version
- **Domain / Category:** the high-level grouping this control belongs to (e.g., "Access Control", "Identify > Asset Management", "Logging and Monitoring")
- **Control name:** official short title
- **Control objective:** what the control is designed to achieve — one to two sentences in plain language
- **Full description:** the normative text or a faithful paraphrase if the normative text is lengthy
- **Control type:** Preventive / Detective / Corrective / Compensating (a control may have more than one type)
- **Implementation guidance:** 2–4 bullet points on how organizations typically implement this control

---

## Step 3 — Cross-Framework Mapping

Map the control to its equivalents in the other frameworks. For each mapping, state a **confidence level**:

| Confidence | Meaning |
|---|---|
| **Direct** | Controls share the same objective and scope — satisfying one largely satisfies the other |
| **Partial** | Controls overlap significantly but differ in scope, specificity, or implementation requirements |
| **Related** | Controls address adjacent objectives — relevant context, but not interchangeable |

Present the mapping as a table:

| Framework | Control ID | Control Name | Confidence | Notes |
|---|---|---|---|---|
| ISO 27001 | [ID] | [Name] | Direct / Partial / Related | [Brief note on what aligns and what differs] |
| NIST CSF | [ID] | [Name] | Direct / Partial / Related | |
| PCI-DSS v4 | [ID] | [Name] | Direct / Partial / Related | |
| OWASP Top 10 | [ID] | [Name] | Direct / Partial / Related | |
| OWASP ASVS | [ID] | [Name] | Direct / Partial / Related | |

If no mapping exists for a framework, state: "No direct or partial mapping — this control addresses a domain not covered by [Framework]."

**Multi-mapping:** a single control may map to more than one control in another framework. List all relevant mappings per framework, ranked by confidence.

---

## Step 4 — Related Controls (Same Framework)

List 2–4 controls within the same framework that are closely related — controls that are commonly tested together, that depend on this control, or that this control depends on.

| Control ID | Control Name | Relationship |
|---|---|---|
| [ID] | [Name] | [Prerequisite / Dependent / Commonly tested together / Compensating] |

---

## Step 5 — Testing Hints

Provide 3–5 concrete, evidence-based indicators an auditor would look for to determine if this control is satisfied:

- **[Evidence type]:** [What to request or observe — e.g., "Access control policy document, reviewed and approved within the last 12 months"]
- **[Evidence type]:** [e.g., "Screenshot or export of RBAC configuration showing least-privilege role assignments"]
- **[Evidence type]:** [e.g., "Sample of joiner/mover/leaver tickets showing access revocation within the defined SLA"]
- **[Evidence type]:** [e.g., "User access review sign-off records from the last review cycle"]

Also note:
- **Common failure modes:** what auditors most frequently find non-compliant for this control
- **Edge cases:** scenarios where the control is technically in place but the spirit is not met

---

## Output Format

Produce exactly this structure for every lookup:

---

**Control:** [Canonical ID] — [Control Name]
**Framework:** [Framework name and version]
**Domain:** [Domain / Category / Function]
**Type:** [Preventive / Detective / Corrective / Compensating]

**Objective:**
[One to two sentences — what this control is designed to achieve]

**Description:**
[Full control description or faithful paraphrase]

**Implementation guidance:**
- [Point 1]
- [Point 2]
- [Point 3]

---

**Cross-Framework Mappings:**

| Framework | Control ID | Control Name | Confidence | Notes |
|---|---|---|---|---|
| ISO 27001 (2022) | | | | |
| NIST CSF | | | | |
| PCI-DSS v4 | | | | |
| OWASP Top 10 | | | | |
| OWASP ASVS | | | | |

---

**Related Controls ([Framework]):**

| Control ID | Control Name | Relationship |
|---|---|---|
| | | |

---

**Testing Hints:**
- **[Evidence type]:** [What to request or observe]
- **[Evidence type]:** [...]
- **[Evidence type]:** [...]

**Common failure modes:** [2–3 sentences on what most often goes wrong]
**Edge cases:** [1–2 sentences on subtle non-compliance patterns]

---

## Rules

- Always state the framework version alongside the framework name — ISO 27001:2013 and ISO 27001:2022 have different Annex A structures; NIST CSF 1.1 and 2.0 differ in structure and function names
- Never fabricate a cross-framework mapping — if a control genuinely has no equivalent in another framework, say so explicitly rather than forcing a weak mapping
- Confidence level must reflect the actual degree of overlap — do not mark a mapping as Direct unless satisfying one control would substantially satisfy the other
- If the user provides a keyword or description instead of an ID, identify the best-matching control and state your reasoning before producing the card — do not silently assume a match
- Testing hints must be evidence-based and specific — "review the policy" is not a testing hint; "request the access control policy, verify it was approved by management and reviewed within the last 12 months, and confirm the review date in the document header" is
- If the lookup returns multiple candidate controls (e.g., a keyword matches controls in several frameworks), produce a card for each, clearly separated
- Do not truncate the cross-framework mapping table — all four frameworks (plus both OWASP rows) must always appear, even if the entry is "No direct or partial mapping"
- For OWASP: Top 10 maps to broad risk categories (application-level); ASVS maps to granular technical controls — always populate both rows when the control has an application security dimension; leave both as "No direct or partial mapping" for purely organizational or physical controls
