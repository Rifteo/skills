---
name: skill-benchmark
description: Scores any SKILL.md across 5 quality dimensions, runs a compatibility check against 50+ AI agents, and returns a ranked fix list. Use when asked to benchmark, audit, or check cross-agent compatibility of a skill — e.g. before publishing or opening a PR.
---

# Skill Benchmark

Reads a target `SKILL.md`, scores it across 5 weighted dimensions (100 pts
total), runs a static compatibility analysis against 50+ agent profiles, and
returns a structured report with a ranked fix list.

**No agents need to be installed.** Everything is static analysis — you read
the skill file, apply the rubric below, and produce the report.

## Protocol

### Step 0 — Locate the target skill

1. If the user provided a path, read that file directly.
2. If not, search in this priority order:
   - Current directory: `SKILL.md`, `*/SKILL.md`
   - Project skill paths: `.claude/skills/`, `.agents/skills/`, `.cline/skills/`
   - Global paths: `~/.claude/skills/`, `~/.config/agents/skills/`
3. If multiple are found, list them and ask the user to confirm which one.
4. If no SKILL.md is found after exhausting all search paths, stop and output:
   `[skill-benchmark error] No SKILL.md found — provide a file path to continue.`
5. Read the full file into context before proceeding.

---

### Step 1 — Intake

Extract and note:
- **Skill name** (frontmatter `name:` field)
- **Description** (frontmatter `description:` field, full text)
- **Body length** (line count)
- **Has bundled resources?** (scripts/, references/, assets/ subdirs)
- **Explicit agent targets** (any `--agent` flag mentions or agent-specific sections)

---

### Step 2 — Score each dimension

Apply the rubric in `references/rubric.md`. For each dimension, note the
score, a one-sentence rationale, and the single most impactful fix.

| # | Dimension | Max pts |
|---|-----------|---------|
| 1 | Trigger quality | 25 |
| 2 | Instruction clarity | 25 |
| 3 | Agent-agnostic design | 20 |
| 4 | Self-containment | 15 |
| 5 | Output definition | 15 |
| | **Total** | **100** |

Scoring is strict. A score of 70+ means the skill is publishable. Below 50
means it will silently fail on most agents.

---

### Step 3 — Run compatibility matrix

Read `references/agent-profiles.md`. For each of the 7 agent profiles,
check the target skill for the compatibility signals listed. Assign one of:

- ✅ **Compatible** — no blocking signals found
- ⚠️ **Partial** — one or more soft-fail signals (skill may work but
  will degrade or skip steps)
- ❌ **Likely broken** — one or more hard-fail signals

Then map each named agent to its profile result. When an agent appears in
multiple profiles (e.g., Claude Code in A and C), assign the worst result
across all applicable profiles: ❌ overrides ⚠️ overrides ✅.

---

### Step 4 — Generate the report

Use the template in `references/report-template.md`.

Fill in every section. Do not skip the "Top fixes" section — it is the
most actionable part and the reason the skill exists.

Sort the 54 agents into three groups (Compatible / Partial / Broken) and
list them comma-separated. Do not list each agent on its own line.

---

### Step 5 — Offer next steps

After presenting the report, offer exactly these three options:

1. **Auto-fix** — apply the top-ranked fix and re-score immediately
2. **Deep dive** — expand any dimension score with full evidence from the skill text
3. **Export** — save the report as `skill-benchmark-report.md` in the same directory as the evaluated skill
