<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/banner-dark.png">
  <source media="(prefers-color-scheme: light)" srcset=".github/assets/banner-light.png">
  <img src=".github/assets/banner-light.png" alt="AuditGuard Skills" width="250">
</picture>

---

**Your agent improvises. Skills don't.**

Install proven pentest methodologies into Claude Code, Cursor, Gemini CLI, and 50+ other agents in one command.

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![npm](https://img.shields.io/badge/npm-coming%20soon-lightgrey)](https://www.npmjs.com/package/auditguard-skills)
[![Skills](https://img.shields.io/badge/skills-27-brightgreen)](https://github.com/AuditGuard-Community/skills)
[![Agents](https://img.shields.io/badge/agents-53-blue)](https://github.com/AuditGuard-Community/skills)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](SKILL_GUIDE.md)

</div>

---

## The problem with AI agents and security work

Ask an agent to hunt for IDOR bugs. It will improvise. It misses verb inconsistency checks, skips GraphQL object exposure, and never tests parameter pollution. You re-prompt five times, spend 3x the tokens, and still get an incomplete result.

The agent is not dumb. It lacks a methodology.

---

## What a skill is

A skill is a battle-tested methodology file your agent reads before starting a task. It covers every test case, every bypass technique, every output format a practitioner would use. The agent stops improvising and starts executing.

| | Without skill | With skill |
|---|---|---|
| Output quality | Inconsistent | Structured and complete |
| Turns to finish | 3 to 5 | 1 |
| Methodology coverage | Partial | Full |
| Report format | Whatever the agent guesses | Triage-ready, platform-specific |

27 skills. 53 agents. One command to install.

---

## Quickstart

```bash
npx auditguard-skills add bugbounty-reporter
```

No account. No configuration. The CLI detects your installed agents automatically and puts the skill in the right place.

> npm publish coming soon. In the meantime: `git clone` + `npm link` (see Install below).

---

## Install

```bash
git clone https://github.com/AuditGuard-Community/skills
cd skills
npm link
```

---

## CLI

```bash
# Install a skill into all detected agents
auditguard-skills add bugbounty-reporter

# Install into a specific agent
auditguard-skills add bugbounty-reporter --agent claude-code

# Install globally across all projects
auditguard-skills add bugbounty-reporter --global

# Browse all available skills
auditguard-skills available

# See what is installed
auditguard-skills list

# See which agents were detected on this machine
auditguard-skills agents

# Remove a skill
auditguard-skills remove bugbounty-reporter
```

Not sure which skill to use? Install `find-skills` first:

```bash
npx auditguard-skills add find-skills
```

It reads your task and loads the right skill automatically.

---

## Skills

### Bug Bounty

| Skill | What it does | Platforms |
|---|---|---|
| `bugbounty-reporter` | Converts raw findings into triage-ready reports. Pre-submission gate included. | HackerOne, Bugcrowd, Intigriti, YesWeHack |
| `caveman` | Ultra-compressed comms mode for fast-paced testing sessions | All |

### Vulnerability Testing

| Skill | What it does |
|---|---|
| `idor-hunter` | Systematic IDOR and BOLA detection with multi-account testing and bypass techniques |
| `xss-hunter` | Full XSS methodology: reflected, stored, DOM, filter bypass, CSP evasion, mXSS |
| `ssrf-hunter` | SSRF detection and exploitation including internal recon, cloud metadata, and filter bypass |
| `xxe-phantom` | XXE injection: file read, blind OOB, SSRF chaining, SVG and XLSX vectors |
| `ssti-hunter` | Server-side template injection with engine fingerprinting and RCE exploitation |
| `js-analyzer` | JavaScript analysis for secrets, endpoints, sinks, and prototype pollution |
| `jwt-cracker` | JWT attacks: alg:none, weak secret brute-force, RS256 to HS256, kid injection |
| `hpp-hunter` | HTTP parameter pollution detection and exploitation |
| `clickjacking-hunter` | Clickjacking detection and PoC generation |
| `redirect-forge` | Open redirect discovery and OAuth code theft chaining |

### Reporting and Scoring

| Skill | What it does |
|---|---|
| `finding-writer` | Converts raw notes into a structured, report-ready finding |
| `pentest-report` | Assembles a full pentest report from individual findings |
| `cvss-scorer` | Computes exact CVSS v3.1 base score and vector from a vulnerability description |
| `risk-assessor` | Business risk assessment from technical findings |
| `remediation-planner` | Generates specific, prioritized remediation plans |

### Recon and Assessment

| Skill | What it does |
|---|---|
| `attack-surface` | Maps the full attack surface before testing begins |
| `scope-grill` | Validates and clarifies engagement scope |
| `check-exploit` | Checks if a CVE has a public exploit and assesses exploitability |
| `vuln-diagnose` | Diagnoses ambiguous or incomplete vulnerability reports |
| `nuclei-template-writer` | Writes production-ready Nuclei templates from vulnerability descriptions |

### Compliance and Governance

| Skill | What it does |
|---|---|
| `compliance-gap-analyzer` | Identifies compliance gaps against security frameworks |
| `control-lookup` | Maps controls across ISO 27001, SOC2, NIST, and PCI-DSS |

### Workflow

| Skill | What it does |
|---|---|
| `find-skills` | Discovers and loads the right skill for any security task |
| `engagement-handoff` | Structures engagement handoff notes between team members |
| `ctf-writeup` | Formats CTF challenge writeups |
| `skill-benchmark` | Benchmarks skill performance with and without the agent |

---

## Slash Commands for Claude Code

Install a skill for Claude Code and you get five slash commands that work in every session, no skill loaded required:

| Command | What it does |
|---|---|
| `/auditguard:triage` | 7-question pre-submission gate. Outputs GO, KILL, or DOWNGRADE with evidence. |
| `/auditguard:chain` | Given a confirmed finding, checks the signal table for companion bugs to escalate severity |
| `/auditguard:report` | Writes a submission-ready bug bounty report: title, steps, PoC, impact, remediation |
| `/auditguard:hunt` | Launches a structured 7-phase engagement workflow on a target |
| `/auditguard:intel` | Pulls CVEs, GitHub advisories, and HackerOne hacktivity for any named technology |

```bash
auditguard-skills add bugbounty-reporter --agent claude-code
# Install AuditGuard slash commands for Claude Code? [Y/n/never]
```

---

## How to activate a skill

After installing, tell your agent to use the skill:

- **Claude Code** — type `/skills` and select from the list
- **Cursor / Windsurf** — type `/skill-name` in chat
- **Gemini CLI** — type `@skill-name` to invoke
- **Other agents** — skills are loaded automatically from the skills directory on session start

Then describe your task in plain language:

```
I found that /api/orders/{id} returns order data without checking 
if the authenticated user owns that order. Any integer ID works.
```

The agent produces a complete, triage-ready report. First try.

---

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
| + 38 more | run `auditguard-skills agents` to see all |

---

## Contributing

Skills are built by practitioners, for practitioners. If you have a methodology that works, the community needs it.

Read the **[Skill Structure Guide](SKILL_GUIDE.md)** for the full format.

The short version:
1. Create a folder named after your skill
2. Add `SKILL.md` with YAML frontmatter and methodology
3. Open a pull request

Once merged, `find-skills` picks it up automatically and your skill is live for the entire community.

---

## Contexts

Skills pair with [AuditGuard Contexts](https://github.com/AuditGuard-Community/contexts), engagement-specific knowledge bases for web app pentest, cloud audit, mobile pentest, and more. Load a context at the start of an engagement and the agent knows the full scope, methodology, and relevant skills before you ask the first question.

---

## Part of AuditGuard

These skills work standalone with any agent and integrate natively with [AuditGuard](https://github.com/AuditGuard-Community), the pentest management platform built for security teams and consultancies.

---

MIT License
