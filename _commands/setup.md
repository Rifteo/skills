Audit the current AuditGuard installation and configuration on this machine, then give exact setup steps for anything missing.

## Step 1 — Check installed skills

Read the directory `~/.claude/skills/`. List every subfolder whose name matches a known AuditGuard skill. Known skills:
bugbounty-reporter, finding-writer, idor-hunter, xss-hunter, ssrf-hunter, xxe-phantom, ssti-hunter, js-analyzer, jwt-cracker, hpp-hunter, clickjacking-hunter, redirect-forge, cvss-scorer, risk-assessor, remediation-planner, attack-surface, scope-grill, check-exploit, vuln-diagnose, nuclei-template-writer, compliance-gap-analyzer, control-lookup, find-skills, engagement-handoff, ctf-writeup, skill-benchmark, caveman, pentest-report

Mark each as ✅ installed or — not installed.

## Step 2 — Check installed commands

Read the directory `~/.claude/commands/auditguard/`. List which of these files exist:
triage.md, chain.md, report.md, hunt.md, intel.md, setup.md

Mark each as ✅ installed or — not installed.

## Step 3 — Check context-mcp

Read `~/.claude/mcp.json`. Look for an entry whose command or args reference `auditguard` or `context-mcp`.
- If found: show the server name, transport type, and URL or command.
- If not found: mark as — not configured.

## Step 4 — Check preferences

Read `~/.auditguard/prefs.json`. Report:
- `commands` preference: if "never", the slash command install prompt is suppressed.
- Any other keys present.

If the file does not exist, report: no preferences saved.

---

## Output format

Print a status card:

```
AuditGuard Setup Status
───────────────────────────────────────────

Skills           X / 28 installed
Commands         X / 6 installed
Context MCP      ✅ configured  |  — not configured
Preferences      path/to/prefs.json  |  none

───────────────────────────────────────────
```

Then for each section that has missing items or is not configured, print a **Setup** block with the exact command or action needed:

### Skills not installed
List missing skills. Then show:
```
npx auditguard-skills add <skill-name>
```
Or to install all at once:
```
npx auditguard-skills add --all
```

### Commands not installed
If any command file is missing, show:
```
npx auditguard-skills add bugbounty-reporter
# then answer Y at the "Install slash commands?" prompt
```
Or to install commands directly without reinstalling a skill, explain that running any `add` command for the claude-code agent will re-trigger the prompt. To reset a "never" preference:
```
# edit ~/.auditguard/prefs.json and remove the "commands" key
```

### Context MCP not configured
Show the exact JSON block to add to `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "auditguard-contexts": {
      "type": "sse",
      "url": "https://mcp.auditguard.community/sse"
    }
  }
}
```
And explain: once configured, the agent loads the right methodology context automatically at the start of each engagement — no manual `/context` call needed.

### If everything is configured
Print:
```
Everything looks good. AuditGuard is fully configured.
```
And remind the user of the 6 available commands:
/auditguard:triage   /auditguard:chain    /auditguard:report
/auditguard:hunt     /auditguard:intel    /auditguard:setup
