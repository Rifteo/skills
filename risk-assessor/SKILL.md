---
name: risk-assessor
description: Scores a described risk using a likelihood × impact matrix and produces a structured risk assessment
---

# Risk Assessor

When the user describes a risk, assess it using a 3×3 likelihood × impact matrix and produce a structured risk assessment.

## Scoring Matrix

**Likelihood**
- Low (1): Unlikely — requires specific conditions, limited attacker capability
- Medium (2): Possible — some conditions in place, moderate capability
- High (3): Likely — conditions favorable, easily exploitable

**Impact**
- Low (1): Minimal — limited data, reversible, low business consequence
- Medium (2): Moderate — sensitive data, service disruption, reputational damage
- High (3): Severe — critical breach, regulatory consequence, major disruption

**Risk Score = Likelihood × Impact**
- 1–2: Low | 3–4: Medium | 6: High | 9: Critical

## Output Format

**Risk:** One-line description
**Likelihood:** Low / Medium / High + justification
**Impact:** Low / Medium / High + justification
**Score:** [number] → [Low / Medium / High / Critical]
**Existing Controls:** Controls already in place
**Residual Risk:** Risk level after existing controls
**Recommended Treatment:** Accept / Mitigate / Transfer / Avoid + one concrete action

## Rules

- Ask for context if the description is too vague to score
- Always justify likelihood and impact — never just output a number
- If controls are provided, recalculate residual risk explicitly
