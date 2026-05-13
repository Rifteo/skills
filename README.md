# AuditGuard Agent Skills

Reusable instruction sets for pentesters, auditors, and security practitioners. Install into Claude Code, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and 54+ other agents in one command.

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

More skills coming soon. [Contribute one →](SKILL_GUIDE.md)

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

Read the **[Skill Structure Guide](SKILL_GUIDE.md)** for the full format — frontmatter fields, references, scripts, and best practices.

Quick version:
1. Create a folder named after your skill
2. Add a `SKILL.md` with YAML frontmatter and instructions
3. Open a pull request

Once merged, the `find-skills` index updates automatically — your skill is immediately discoverable by the community.

## Part of AuditGuard

These skills work standalone with any agent and integrate natively with [AuditGuard](https://github.com/AuditGuard-Community) — the pentest management platform built for security teams and consultancies.

## License

MIT
