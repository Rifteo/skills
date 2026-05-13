---
name: scope-analyzer
description: Takes a project brief or system description and proposes a structured audit scope with boundaries, key risks, and exclusions
---

# Scope Analyzer

When the user describes a system, project, or engagement, produce a structured audit scope document they can use to align with the client before fieldwork begins.

## Output Format

**Engagement Overview:** One paragraph summarizing what is being audited and why

**In-Scope Systems:**
List of systems, applications, APIs, infrastructure components, and processes included in the audit

**Out-of-Scope:**
Explicit exclusions with a brief reason for each

**Key Risk Areas:**
Top 5–7 risk areas to prioritize based on the scope — ranked by likelihood and impact

**Audit Objectives:**
What the audit aims to confirm or assess — specific, measurable objectives

**Suggested Approach:**
Recommended audit methodology — black box / grey box / white box, automated + manual, frameworks to apply

**Assumptions:**
What the auditor is assuming about the environment, access level, or documentation availability

**Dependencies:**
What is needed from the client before fieldwork can begin — credentials, architecture diagrams, contacts, etc.

## Rules

- Always make exclusions explicit — scope creep is the most common cause of audit failure
- Key risk areas must be specific to the described system, not generic categories
- If the description is too vague, ask for: system type, tech stack, regulatory context, and previous audit history
- Flag any red flags in the description that suggest elevated risk
