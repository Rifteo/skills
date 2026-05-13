---
name: ai-act-classifier
description: Classifies an AI system under the EU AI Act risk tiers and identifies applicable obligations
---

# EU AI Act Classifier

When the user describes an AI system or use case, classify it under the EU AI Act risk framework and outline the applicable obligations.

## EU AI Act Risk Tiers

**Unacceptable Risk (Prohibited):**
AI systems banned outright — social scoring by governments, real-time remote biometric surveillance in public spaces, manipulation of vulnerable groups, subliminal techniques.

**High Risk:**
AI in critical infrastructure, education, employment, essential services, law enforcement, migration, justice, democratic processes. Subject to strict requirements before market placement.

**Limited Risk:**
AI systems with specific transparency obligations — chatbots must disclose they are AI, deepfakes must be labeled.

**Minimal Risk:**
All other AI systems — no mandatory requirements, voluntary codes of conduct encouraged.

## Output Format

**System Description:** Summary of the AI system as provided

**Classification:** Unacceptable / High Risk / Limited Risk / Minimal Risk

**Justification:** Why this classification applies — which article or annex of the EU AI Act is relevant

**Applicable Obligations:**
For each obligation that applies, list:
- What is required
- Who is responsible (provider vs deployer)
- Timeline for compliance

**Risk Flags:**
Any aspects of the described system that could push it into a higher risk tier

**Recommended Next Steps:**
Concrete actions to achieve or maintain compliance

## Rules

- If the use case is ambiguous, ask clarifying questions about the deployment context and affected population
- Always distinguish between provider obligations (who builds the AI) and deployer obligations (who uses it)
- Note if the system falls under a General Purpose AI (GPAI) model classification
- Reference specific EU AI Act articles where possible
