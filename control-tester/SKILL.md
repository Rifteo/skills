---
name: control-tester
description: Generates detailed test procedures for a given security or compliance control
---

# Control Tester

When the user provides a control (by name, ID, or description), generate a complete test procedure an auditor can follow to verify whether that control is implemented and operating effectively.

## Output Format

**Control:** Name or ID of the control being tested

**Objective:** What this control is supposed to achieve in one sentence

**Test Approach:** Inquiry / Observation / Inspection / Re-performance (or a combination)

**Steps:**
Numbered step-by-step procedure the auditor follows. Each step should specify:
- What to do
- What to look at or request
- What a passing result looks like
- What a failing result looks like

**Evidence to Collect:**
List of artifacts the auditor should obtain — screenshots, logs, config exports, policy documents, interview notes, etc.

**Pass Criteria:** What constitutes a well-implemented, operating control

**Fail Indicators:** Specific red flags or gaps that constitute a finding

**Relevant Framework Mappings:** ISO 27001, SOC2, NIST, CIS, PCI-DSS references if applicable

## Rules

- Steps must be specific enough for a junior auditor to follow without additional guidance
- Always include both technical verification (system config, logs) and process verification (policy, interviews)
- If the control is ambiguous, ask which framework or context it applies to before generating procedures
