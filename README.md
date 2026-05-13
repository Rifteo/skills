# AuditGuard Agent Skills

Reusable instruction sets for pentesters, auditors, and security practitioners. Install into Claude Code, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and 20+ other agents in one command.

## Quickstart

```bash
npx auditguard-skills add finding-writer
```

No account needed. No configuration. The CLI auto-detects your installed agents and drops the skill in the right place.

## Install the CLI

```bash
git clone https://github.com/AuditGuard-Community/skills
cd skills
npm link
```

> npm publish coming soon — `npx auditguard-skills` will work without cloning once released.

## Commands

```bash
# Install a skill into all detected agents
auditguard-skills add finding-writer

# Install into a specific agent
auditguard-skills add finding-writer --agent claude-code

# Install globally (available in all projects)
auditguard-skills add finding-writer --global

# List all available skills
auditguard-skills available

# List installed skills
auditguard-skills list

# Show which agents were detected on this machine
auditguard-skills agents

# Remove a skill
auditguard-skills remove finding-writer
```

## Available Skills

| Skill | What it does |
|---|---|
| `find-skills` | Discover and install the right AuditGuard skill for any security or audit task |
| `finding-writer` | Raw notes or logs → structured audit finding (title, severity, evidence, impact, recommendation) |
| `risk-assessor` | Scores risks using a likelihood × impact matrix with justification |
| `control-tester` | Generates step-by-step test procedures for any security control |
| `remediation-planner` | Turns a finding into a concrete remediation plan with effort estimates |
| `audit-checklist` | Generates framework-specific checklists (ISO 27001, SOC2, NIST, PCI-DSS, GDPR, DORA) |
| `scope-analyzer` | Proposes audit scope, boundaries, and key risk areas from a brief description |
| `executive-brief-writer` | Findings → board-ready one-page executive summary |
| `compliance-gap-analyzer` | Identifies gaps against ISO 27001, SOC2, NIST, PCI-DSS, GDPR, and DORA |
| `audit-email-writer` | Drafts professional audit communication emails (kickoff, follow-up, findings, closure) |
| `ai-act-classifier` | Classifies AI systems under EU AI Act risk tiers with rationale |

## How to use a skill

After installing, activate the skill from your agent:

- **Claude Code** — type `/skills` and select the skill from the list
- **Cursor / Windsurf** — type `/skill-name` in the chat
- **Gemini CLI** — type `@skill-name` to invoke
- **Other agents** — skills are loaded automatically from the skills directory on session start

Once active, just describe what you need in plain language — the skill handles the structure.

**Example with `finding-writer`:**
```
I found that the /api/orders/{id} endpoint returns order data without 
checking if the authenticated user owns that order. Any user ID works.
```
The agent produces a complete, report-ready finding.

## Supported Agents

| Agent | Flag |
|---|---|
| Claude Code | `claude-code` |
| Gemini CLI | `gemini-cli` |
| Cursor | `cursor` |
| GitHub Copilot | `github-copilot` |
| Windsurf | `windsurf` |
| Cline | `cline` |
| Continue | `continue` |
| Roo Code | `roo` |
| Goose | `goose` |
| OpenHands | `openhands` |
| Codex | `codex` |
| Aider Desk | `aider-desk` |
| Augment | `augment` |
| Kilo Code | `kilo` |
| Amp | `amp` |
| + more | `auditguard-skills agents` to see all |

## Contributing

Have a skill that would help the community? Open a PR.

1. Create a folder named after your skill
2. Add a `SKILL.md` file with YAML frontmatter

```
my-skill/
  SKILL.md
```

```markdown
---
name: my-skill
description: What this skill does and when to use it
---

# My Skill

Instructions for the agent to follow when this skill is activated.
```

3. Open a pull request — that's it.

Once merged, a GitHub Actions workflow automatically updates the `find-skills` skill so your new skill is immediately discoverable by anyone using `auditguard-skills` in their agent.

All skill submissions are welcome.

## Part of AuditGuard

These skills work standalone with any agent and integrate natively with [AuditGuard](https://github.com/AuditGuard-Community) — the pentest management platform built for security teams and consultancies.

## License

MIT
