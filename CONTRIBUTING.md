# Contributing to Rifteo agent skills

## Adding a skill

1. Fork this repo
2. Create a folder named after your skill (use kebab-case)
3. Add a `SKILL.md` file with YAML frontmatter

```
my-skill/
  SKILL.md
```

```markdown
---
name: my-skill
description: One sentence — what this skill does and when to use it
license: MIT
metadata:
  version: "0.0.1"
  author: Rifteo
  tags: ["security", "audit"]
---

# My Skill

Instructions for the agent to follow when this skill is activated.
```

4. Open a pull request

Once merged, the `generate-find-skills` GitHub Actions workflow automatically updates `find-skills/SKILL.md` so your skill is immediately discoverable.

## Skill quality checklist

- [ ] `name` matches the folder name exactly
- [ ] `description` is one clear sentence (used in the discovery index)
- [ ] Instructions are actionable — the agent should know exactly what to do
- [ ] No invented evidence or hallucinated data in examples
- [ ] Tested with at least one agent before submitting

## Running the generate script locally

```bash
npm run generate
```

This regenerates `find-skills/SKILL.md` from all skill frontmatter. Run it if you want to verify your skill appears correctly before opening a PR.
