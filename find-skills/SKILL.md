---
name: find-skills
description: Helps users discover and install AuditGuard agent skills when they ask questions like "is there a skill for X", "how do I write a finding", "find a skill that can...", or want to extend their agent for security and audit work.
---

# Find AuditGuard Skills

When the user is looking for functionality that might exist as an installable AuditGuard skill, help them discover and install it.

## Available Skills

| Skill | What it does | Install |
|---|---|---|
| `ai-act-classifier` | Classifies an AI system under the EU AI Act risk tiers and identifies applicable obligations | `auditguard-skills add ai-act-classifier` |
| `audit-checklist` | Generates a framework-specific audit checklist from a scope description or system type | `auditguard-skills add audit-checklist` |
| `audit-email-writer` | Drafts professional audit communication emails — kickoff, evidence requests, finding notifications, and report delivery | `auditguard-skills add audit-email-writer` |
| `compliance-gap-analyzer` | Compares an organization's current controls against a compliance framework and identifies gaps, partially met controls, and priorities | `auditguard-skills add compliance-gap-analyzer` |
| `control-tester` | Generates detailed test procedures for a given security or compliance control | `auditguard-skills add control-tester` |
| `executive-brief-writer` | Converts a list of audit findings into a board-ready executive summary — one page, risk-focused, no jargon | `auditguard-skills add executive-brief-writer` |
| `finding-writer` | Converts raw pentest notes, logs, or observations into a structured audit finding ready for a report | `auditguard-skills add finding-writer` |
| `remediation-planner` | Converts an audit finding into a concrete step-by-step remediation plan with effort estimates and priority | `auditguard-skills add remediation-planner` |
| `risk-assessor` | Scores a described risk using a likelihood × impact matrix and produces a structured risk assessment | `auditguard-skills add risk-assessor` |
| `scope-analyzer` | Takes a project brief or system description and proposes a structured audit scope with boundaries, key risks, and exclusions | `auditguard-skills add scope-analyzer` |

## How to Find a Skill

**List all available skills:**
```bash
auditguard-skills available
```

**List what's already installed:**
```bash
auditguard-skills list
```

**Install a skill globally (available in all projects):**
```bash
auditguard-skills add <skill-name> --global
```

**Install for a specific agent:**
```bash
auditguard-skills add <skill-name> --agent claude-code
```

## Matching User Needs to Skills

When the user asks about a task, suggest the right skill:

- Classifies an AI system under the EU AI Act risk tiers and identifies applicable obligations → `ai-act-classifier`
- Generates a framework-specific audit checklist from a scope description or system type → `audit-checklist`
- Drafts professional audit communication emails — kickoff, evidence requests, finding notifications, and report delivery → `audit-email-writer`
- Compares an organization's current controls against a compliance framework and identifies gaps, partially met controls, and priorities → `compliance-gap-analyzer`
- Generates detailed test procedures for a given security or compliance control → `control-tester`
- Converts a list of audit findings into a board-ready executive summary — one page, risk-focused, no jargon → `executive-brief-writer`
- Converts raw pentest notes, logs, or observations into a structured audit finding ready for a report → `finding-writer`
- Converts an audit finding into a concrete step-by-step remediation plan with effort estimates and priority → `remediation-planner`
- Scores a described risk using a likelihood × impact matrix and produces a structured risk assessment → `risk-assessor`
- Takes a project brief or system description and proposes a structured audit scope with boundaries, key risks, and exclusions → `scope-analyzer`

## Rules

- Always show the install command so the user can act immediately
- If no skill matches, offer to help directly using your own capabilities
- If the user wants a skill that doesn't exist yet, point them to contribute at github.com/medinnov/agent-skills
