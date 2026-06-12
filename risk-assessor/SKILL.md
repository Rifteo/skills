---
name: risk-assessor
description: Scores a vulnerability using likelihood × impact, CIA triad, CVSS correlation, and SLA-bound remediation urgency. Use when you need a risk rating and remediation urgency for a finding, beyond a raw CVSS score.
---

# Risk Assessor

When the user describes a vulnerability or security risk, score it using a structured likelihood × impact matrix, analyze the CIA triad, correlate with CVSS if available, and produce a complete risk classification with treatment recommendations and escalation triggers.

## When NOT to use

Do NOT apply the risk scoring format — respond normally — when:
- The user is asking how to exploit a vulnerability (use `check-exploit` or the relevant hunter skill)
- The user is asking how to fix a vulnerability (use `remediation-planner` instead)
- The user is asking a general question about risk management theory or frameworks
- The user is asking about compliance requirements without describing a specific vulnerability
- No concrete vulnerability or security risk has been described — the scoring methodology requires a real subject

---

## Step 1 — Gather Context

Before scoring, confirm you have:
- **Affected component** — what system, service, or asset is vulnerable
- **Network exposure** — internet-facing, internal network, local only, physical access only
- **Authentication required** — none, low-privilege account, high-privilege account
- **Exploit availability** — no known exploit, theoretical, PoC published, weaponized, actively exploited
- **Data in scope** — public data, internal data, PII/PHI/PCI, credentials, IP
- **Existing controls** — WAF, network segmentation, EDR, monitoring, compensating controls
- **CVSS score** — if available (v3.x preferred)

If any of these are missing and the description is too vague to infer them, ask for the missing items before scoring.

---

## Step 2 — Score Likelihood (1–3)

Likelihood measures how probable exploitation is, given attacker capability and environmental exposure.

| Score | Level | Criteria |
|---|---|---|
| 1 | **Low** | No public exploit; requires physical access or highly privileged position; complex multi-step chain; no known threat actors targeting this class |
| 2 | **Medium** | Technique or PoC is known and published; exploitable remotely with moderate skill; requires non-default conditions or limited user interaction |
| 3 | **High** | Exploit is public or weaponized; network-accessible with no authentication; actively exploited in the wild (CISA KEV confirmed or credible threat intel) |

**Likelihood modifiers — evaluate each and adjust the base score:**

| Factor | Modifier |
|---|---|
| Attack vector: Network | +0.5 |
| Attack vector: Adjacent network | 0 |
| Attack vector: Local or Physical | −0.5 |
| No authentication required | +0.5 |
| High privilege required | −0.5 |
| User interaction required | −0.5 |
| Patch available and applied | Score only residual risk; inherent likelihood unchanged |
| Patch available but not applied | 0 |
| No patch available | +0.5 |
| Actively exploited in the wild | Override to 3 regardless of other factors |

Round modifiers to the nearest integer; clamp to [1, 3].

---

## Step 3 — Score Impact (1–3)

Impact measures the worst-case consequence if the vulnerability is exploited. Evaluate each CIA axis, then take the highest axis score as the overall impact score.

**Confidentiality — can an attacker read data they shouldn't?**

| Score | Criteria |
|---|---|
| 0 | No data exposed |
| 1 | Non-sensitive or public data; limited scope |
| 2 | Internal data, credentials, or business-sensitive information |
| 3 | PII, PHI, PCI data; secrets; mass exfiltration possible |

**Integrity — can an attacker modify data or code?**

| Score | Criteria |
|---|---|
| 0 | No modification possible |
| 1 | Limited write access to non-critical resources |
| 2 | Modification of business data or application logic |
| 3 | Code execution, supply chain tampering, full data destruction |

**Availability — can an attacker disrupt or destroy the service?**

| Score | Criteria |
|---|---|
| 0 | No availability impact |
| 1 | Degraded performance; limited or recoverable disruption |
| 2 | Service disruption affecting users or operations |
| 3 | Full outage of critical service; data destruction; unrecoverable without backup |

**Scope modifier:**
- **Changed scope** (exploitation pivots to other systems): +0.5 to overall impact
- **Unchanged scope** (exploitation stays contained): 0

**Business context modifier:**

| Context | Modifier |
|---|---|
| Critical system (core revenue, safety, regulatory reporting) | +0.5 |
| Standard business system | 0 |
| Non-critical or test system | −0.5 |

Round and clamp impact to [1, 3].

---

## Step 4 — Risk Matrix

**Risk Score = Likelihood × Impact**

| | **Impact: Low (1)** | **Impact: Medium (2)** | **Impact: High (3)** |
|---|---|---|---|
| **Likelihood: High (3)** | Medium (3) | High (6) | Critical (9) |
| **Likelihood: Medium (2)** | Low (2) | Medium (4) | High (6) |
| **Likelihood: Low (1)** | Low (1) | Low (2) | Medium (3) |

**Risk level thresholds:**
- **1–2 → Low** — monitor; schedule in standard maintenance backlog
- **3–4 → Medium** — plan remediation within 30 days
- **6 → High** — remediate within 7 days; notify security lead
- **9 → Critical** — immediate escalation; patch or mitigate within 48 hours

---

## Step 5 — CVSS Correlation (if score is available)

Map the provided CVSS v3.x Base Score to a level, then compare with the matrix result:

| CVSS Range | Level |
|---|---|
| 0.1–3.9 | Low |
| 4.0–6.9 | Medium |
| 7.0–8.9 | High |
| 9.0–10.0 | Critical |

**If the matrix score and CVSS diverge by more than one level**, flag it explicitly and explain why — CVSS is environment-agnostic, the matrix accounts for compensating controls, business criticality, and actual threat intelligence. The matrix score takes precedence in production environments.

---

## Output Format

Produce exactly this structure. Do not omit any section.

---

**Vulnerability:** [One-line description including the affected component and vulnerability class]

**Attack Surface:** [Where and how the vulnerability is reachable — e.g. "Internet-facing REST API, unauthenticated endpoint, no WAF in place"]

---

**Likelihood:** [Low / Medium / High] — Score: [1 / 2 / 3]
- Attack vector: [Network / Adjacent / Local / Physical]
- Exploit availability: [No public exploit / PoC published / Weaponized / Actively exploited]
- Authentication required: [None / Low privilege / High privilege]
- Key modifier applied: [state the most significant modifier, or "None"]
- Justification: [1–2 sentences explaining the score]

**Impact:** [Low / Medium / High] — Score: [1 / 2 / 3]
- Confidentiality: [None (0) / Low (1) / High (2–3)] — [brief reason]
- Integrity: [None (0) / Low (1) / High (2–3)] — [brief reason]
- Availability: [None (0) / Low (1) / High (2–3)] — [brief reason]
- Scope: [Unchanged / Changed — lateral movement or cross-system impact possible]
- Dominant axis: [C / I / A]
- Justification: [1–2 sentences explaining the score]

**Inherent Risk Score:** [Likelihood × Impact] → **[Low / Medium / High / Critical]**

*(Include only if CVSS score was provided)*
**CVSS Correlation:** CVSS [score] ([version]) → [Low / Medium / High / Critical] | [Aligned with matrix / Diverges — [explanation]]

---

**Existing Controls:**
[List each control and briefly state whether it reduces likelihood, impact, or both. If none, state "None identified."]
- [Control name]: [reduces likelihood / reduces impact / compensating]

**Residual Risk:** [Low / Medium / High / Critical]
[Recalculate explicitly — e.g. "With WAF blocking known exploit patterns, likelihood drops from High to Medium. Impact unchanged at High. Residual score: 6 → High."]

---

**Remediation SLA:**

| Residual Risk | Target |
|---|---|
| Critical | Escalate within 24h; patch or mitigate within 48h |
| High | Remediate within 7 days; notify security lead |
| Medium | Remediate within 30 days |
| Low | Schedule in next maintenance cycle |

**Recommended Treatment:** [Mitigate / Accept / Transfer / Avoid]

- **Mitigate:** [One specific, actionable step — e.g. "Apply vendor patch for CVE-XXXX-XXXX. If patching is not immediately possible, restrict the endpoint to VPN-only access and enable rate limiting at the load balancer."]
- **Accept:** Only valid for Low residual risk. Requires documented business justification and named owner sign-off.
- **Transfer:** [If applicable — e.g. "Engage cyber insurance and document residual risk. Validate vendor SLA covers this class of incident."]
- **Avoid:** [If applicable — e.g. "Decommission the legacy endpoint if it is no longer required by the business."]

---

**Escalation Triggers:**
Flag any that apply. If none apply, state "None at this time."
- [ ] Active exploitation detected in this environment
- [ ] CISA KEV listing or credible threat intel confirms active campaigns against this class
- [ ] Regulatory data confirmed in scope (PII, PHI, PCI, financial records)
- [ ] Privilege escalation or lateral movement is possible upon exploitation
- [ ] Two or more vulnerabilities chain to achieve a higher combined impact
- [ ] No patch available and no viable compensating control

---

## Rules

- Never output a score without justifying both likelihood and impact — a number without context is not an assessment
- Always recalculate residual risk explicitly when controls are present — do not assume controls are 100% effective
- "Actively exploited in the wild" overrides likelihood to High (3) regardless of other factors
- For chained vulnerabilities, assess the risk of the full attack chain, not each vulnerability in isolation — the chain score governs
- If CVSS and the matrix diverge, always explain the discrepancy; the matrix score takes precedence for production risk decisions
- The Escalation Triggers section must always appear — even if all items are unchecked
- The output must be complete and self-contained — a reader unfamiliar with the vulnerability must be able to understand the risk from the assessment alone
- Accept treatment is only valid for Low residual risk — never recommend Accept for Medium, High, or Critical residual risk
