# Skill Structure Guide

A complete reference for creating Rifteo agent skills.

---

## Minimal skill

The only required file is `SKILL.md` inside a folder named after your skill:

```
my-skill/
└── SKILL.md
```

---

## Full skill

A skill can also include reference documents and scripts the agent uses during execution:

```
my-skill/
├── SKILL.md
├── references/
│   ├── owasp-checklist.md
│   └── severity-matrix.md
└── scripts/
    └── extract-findings.py
```

All files are installed alongside `SKILL.md` when a user runs `rifteo-skills add my-skill`.

---

## SKILL.md format

```markdown
---
name: my-skill
description: One sentence — what this skill does and when to use it
license: MIT
metadata:
  version: "1.0.0"
  author: Rifteo
  tags: ["security", "audit"]
---

# My Skill

Instructions for the agent to follow when this skill is active.
```

### Frontmatter fields

| Field | Required | Description |
|---|---|---|
| `name` | yes | Matches the folder name exactly |
| `description` | yes | One sentence shown in `rifteo-skills available` |
| `license` | no | License for the skill (e.g. `MIT`) |
| `metadata.version` | no | Semantic version of the skill |
| `metadata.author` | no | Rifteo |
| `metadata.tags` | no | Array of tags for filtering and discovery |

---

## Writing good instructions

The body of `SKILL.md` is plain text the agent reads and follows. A few principles:

**Be specific about input and output.**
Tell the agent exactly what it should expect from the user and what it should produce.

```markdown
When the user provides raw pentest notes or observations, produce a structured
finding with the following fields: title, severity (Critical/High/Medium/Low/Info),
evidence, impact, and recommendation.
```

**Define the format explicitly.**
If you want structured output, show the template.

```markdown
Use this exact format:

**Title:** [short descriptive title]
**Severity:** [Critical / High / Medium / Low / Info]
**Evidence:** [what was observed]
**Impact:** [what an attacker could do]
**Recommendation:** [how to fix it]
```

**Keep it focused.**
One skill, one job. If you need to cover multiple scenarios, use separate skills.

---

## References folder

Put any documents the agent should consult during execution — checklists, frameworks, scoring matrices, lookup tables.

```
my-skill/
└── references/
    └── cvss-guide.md
```

Reference the file in `SKILL.md` so the agent knows to use it:

```markdown
Use the CVSS scoring guide in references/cvss-guide.md to assign severity.
```

---

## Scripts folder

Put any helper scripts the agent can run as part of the workflow.

```
my-skill/
└── scripts/
    └── parse-output.py
```

Reference the script in `SKILL.md`:

```markdown
If the user provides raw tool output, run scripts/parse-output.py to normalize
it before processing.
```

Scripts can be in any language. Document any dependencies at the top of the script.

---

## Naming conventions

- Folder and `name` field must match exactly: `finding-writer/` → `name: finding-writer`
- Use lowercase kebab-case: `api-auth-tester` not `ApiAuthTester`
- Be descriptive: `jwt-weakness-checker` over `jwt-tool`

---

## Submitting a skill

1. Fork this repo
2. Create your skill folder with `SKILL.md`
3. Open a pull request

Once merged, the `find-skills` index updates automatically — your skill is immediately discoverable by the community.
