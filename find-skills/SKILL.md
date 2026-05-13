---
name: find-skills
description: Helps users discover and install AuditGuard agent skills when they ask questions like "is there a skill for X", "how do I write a finding", "find a skill that can...", or want to extend their agent for security and audit work.
---

# Find AuditGuard Skills

When the user is looking for functionality that might exist as an installable AuditGuard skill, help them discover and install it.

## Available Skills

| Skill | What it does | Install |
|---|---|---|
| `finding-writer` | Converts raw pentest notes, logs, or observations into a structured audit finding ready for a security report | `auditguard-skills add finding-writer` |
| `jwt-cracker` | Full JWT attack methodology — alg:none, RS256 to HS256 confusion, weak secret brute-force, kid injection, jku/jwk injection, and claim tampering | `auditguard-skills add jwt-cracker` |
| `skill-benchmark` | Scores any SKILL.md across 5 quality dimensions, runs a compatibility check against 50+ AI agents, and returns a ranked fix list — use when asked to benchmark, audit, or check cross-agent compatibility of a skill. | `auditguard-skills add skill-benchmark` |

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

- Converts raw pentest notes, logs, or observations into a structured audit finding ready for a security report → `finding-writer`
- Full JWT attack methodology — alg:none, RS256 to HS256 confusion, weak secret brute-force, kid injection, jku/jwk injection, and claim tampering → `jwt-cracker`
- Scores any SKILL.md across 5 quality dimensions, runs a compatibility check against 50+ AI agents, and returns a ranked fix list — use when asked to benchmark, audit, or check cross-agent compatibility of a skill. → `skill-benchmark`

## Rules

- Always show the install command so the user can act immediately
- If no skill matches, offer to help directly using your own capabilities
- If the user wants a skill that doesn't exist yet, point them to contribute at github.com/AuditGuard-Community/agent-skills
