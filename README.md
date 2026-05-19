<div align="center">

# AuditGuard Agent Skills

Reusable instruction sets for pentesters, auditors, and security practitioners. Install into Claude Code, Cursor, Gemini CLI, GitHub Copilot, Windsurf, and more in one command.

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![npm](https://img.shields.io/badge/npm-coming%20soon-lightgrey)](https://www.npmjs.com/package/auditguard-skills)
[![Issues](https://img.shields.io/github/issues/AuditGuard-Community/skills)](https://github.com/AuditGuard-Community/skills/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](SKILL_GUIDE.md)

</div>

## Why Skills?

Without a skill, an agent improvises. It misses bypass techniques, skips confirmation steps, and produces inconsistent output. You end up re-prompting multiple times to get a complete result, burning tokens and time.

A skill gives the agent a proven methodology. Same quality every run, first try.

| | Without skill | With skill |
|---|---|---|
| Output quality | Inconsistent | Structured and complete |
| Turns to completion | 3-5 | 1 |
| Methodology coverage | Partial | Full |

Not sure which skill to use? Install `find-skills` first. It helps you discover and load the right skill for any task.

```bash
npx auditguard-skills add find-skills
```

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

> npm publish coming soon. `npx auditguard-skills` will work without cloning once released.

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

### Bug Bounty

| Skill | What it does | Platforms |
|---|---|---|
| `bugbounty-reporter` | Converts raw findings into triage-ready reports | HackerOne, Bugcrowd, Intigriti, YesWeHack |
| `caveman` | Ultra-compressed communication mode for fast-paced testing | All |

### Vulnerability Testing

| Skill | What it does |
|---|---|
| `idor-hunter` | Systematic IDOR/BOLA detection with multi-account testing and bypass techniques |
| `xss-hunter` | Full XSS methodology covering reflected, stored, DOM, filter bypass, and exploitation |
| `ssrf-hunter` | SSRF detection and exploitation including internal recon, cloud metadata, and filter bypass |
| `xxe-phantom` | XXE injection covering file read, blind OOB, SSRF chaining, and SVG/XLSX vectors |
| `ssti-hunter` | Server-side template injection with engine fingerprinting and RCE exploitation |
| `js-analyzer` | JavaScript analysis for secrets, endpoints, sinks, and prototype pollution |
| `jwt-cracker` | JWT attacks including alg:none, weak secret brute-force, RS256 to HS256, and kid injection |
| `hpp-hunter` | HTTP parameter pollution detection and exploitation |
| `clickjacking-hunter` | Clickjacking detection and PoC generation |
| `redirect-forge` | Open redirect discovery and OAuth chaining |

### Reporting & Scoring

| Skill | What it does |
|---|---|
| `finding-writer` | Converts raw notes into a structured, report-ready finding |
| `pentest-report` | Assembles a full pentest report from findings |
| `cvss-scorer` | Computes exact CVSS v3.1 base score and vector from a vulnerability description |
| `risk-assessor` | Business risk assessment from technical findings |
| `remediation-planner` | Generates specific, prioritized remediation plans |

### Recon & Assessment

| Skill | What it does |
|---|---|
| `attack-surface` | Maps the full attack surface before testing begins |
| `scope-grill` | Validates and clarifies engagement scope |
| `check-exploit` | Checks if a CVE has a public exploit and assesses exploitability |
| `vuln-diagnose` | Diagnoses ambiguous vulnerability reports |
| `nuclei-template-writer` | Writes Nuclei templates from vulnerability descriptions |

### Compliance & Governance

| Skill | What it does |
|---|---|
| `compliance-gap-analyzer` | Identifies compliance gaps against security frameworks |
| `control-lookup` | Looks up controls across ISO 27001, SOC2, NIST, and PCI-DSS |

### Workflow

| Skill | What it does |
|---|---|
| `find-skills` | Discover and install the right skill for any security task |
| `engagement-handoff` | Structures engagement handoff notes between team members |
| `ctf-writeup` | Formats CTF challenge writeups |
| `skill-benchmark` | Benchmarks skill performance with and without the agent |

[Contribute a skill](SKILL_GUIDE.md)

## How to use a skill

After installing, activate the skill from your agent:

- **Claude Code** - type `/skills` and select the skill from the list
- **Cursor / Windsurf** - type `/skill-name` in the chat
- **Gemini CLI** - type `@skill-name` to invoke
- **Other agents** - skills are loaded automatically from the skills directory on session start

Once active, just describe what you need in plain language and the skill handles the structure.

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

Read the **[Skill Structure Guide](SKILL_GUIDE.md)** for the full format including frontmatter fields, references, scripts, and best practices.

Quick version:
1. Create a folder named after your skill
2. Add a `SKILL.md` with YAML frontmatter and instructions
3. Open a pull request

Once merged, the `find-skills` index updates automatically and your skill is immediately discoverable by the community.

## Contexts

Skills pair with [AuditGuard Contexts](https://github.com/AuditGuard-Community/contexts), engagement-specific knowledge bases for web app pentest, cloud audit, mobile pentest, and more.

## Part of AuditGuard

These skills work standalone with any agent and integrate natively with [AuditGuard](https://github.com/AuditGuard-Community), the pentest management platform built for security teams and consultancies.

## License

MIT
