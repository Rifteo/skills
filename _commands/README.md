# Rifteo Slash Commands

Slash commands for Claude Code that invoke Rifteo workflows directly from the prompt.

---

## How They Work

Each `.md` file in this folder is a Claude Code slash command. When installed, typing `/rifteo:<name>` in any Claude Code session loads the file as a prompt and executes it with your input as `$ARGUMENTS`.

These commands are self-contained. They do not require the corresponding skill to be installed, though installing the skill alongside gives the agent deeper reference material.

---

## Available Commands

| Command | What it does |
|---|---|
| `/rifteo:triage` | Runs the 7-question pre-submission gate. Outputs GO, KILL, or DOWNGRADE. |
| `/rifteo:chain` | Given a confirmed finding, checks the signal table for companion bugs to escalate severity. |
| `/rifteo:report` | Writes a submission-ready bug bounty report with title, steps, PoC, impact, and remediation. |
| `/rifteo:hunt` | Starts a structured 7-phase engagement workflow on a target. |
| `/rifteo:intel` | Looks up CVEs, GitHub advisories, and HackerOne hacktivity for a named technology. |
| `/rifteo:setup` | Audits current Rifteo install state and gives exact steps for anything missing. |

---

## Installation

Commands are installed automatically by skills-cli when you add a skill for Claude Code:

```
rifteo-skills add bugbounty-reporter
```

After the skill installs, the CLI prompts:

```
Install Rifteo slash commands for Claude Code? [Y/n/never]
```

Press Y to install all commands to `~/.claude/commands/rifteo/`.

To reset the "never" preference, delete the `commands` key from `~/.rifteo/prefs.json`.

---

## Usage Examples

```
/rifteo:triage Reflected XSS on /search?q= parameter, no auth required, target.com is in scope

/rifteo:chain IDOR on GET /api/invoices/{id}, integer ID, unauthenticated access confirmed

/rifteo:report SQLi in login form, time-based blind, PostgreSQL, HackerOne program

/rifteo:hunt api.target.com — in scope, accepted: RCE, SQLi, IDOR, stored XSS

/rifteo:intel Apache Struts 2.5.16
```

---

## Contributing

To add a new command, create a `.md` file in this folder. The filename becomes the command name. Use `$ARGUMENTS` where the user's input should be inserted. Keep commands self-contained — do not rely on external files being present.

`README.md` is excluded from installation automatically.
