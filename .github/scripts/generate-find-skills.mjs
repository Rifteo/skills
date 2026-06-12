import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..')
const SKIP = new Set(['.git', '.github', 'find-skills', 'node_modules'])

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/)
  if (!match) return null
  const fm = {}
  for (const line of match[1].split('\n')) {
    const [key, ...rest] = line.split(':')
    if (key && rest.length) fm[key.trim()] = rest.join(':').trim()
  }
  return fm
}

function loadSkills() {
  return fs.readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !SKIP.has(d.name))
    .map(d => {
      const skillFile = path.join(ROOT, d.name, 'SKILL.md')
      if (!fs.existsSync(skillFile)) return null
      const fm = parseFrontmatter(fs.readFileSync(skillFile, 'utf8'))
      if (!fm?.name || !fm?.description) return null
      return { name: fm.name, description: fm.description, folder: d.name }
    })
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name))
}

function generate(skills) {
  const table = [
    '| Skill | What it does | Install |',
    '|---|---|---|',
    ...skills.map(s =>
      `| \`${s.name}\` | ${s.description} | \`rifteo-skills add ${s.name}\` |`
    )
  ].join('\n')

  const matching = skills.map(s =>
    `- ${s.description} → \`${s.name}\``
  ).join('\n')

  return `---
name: find-skills
description: Helps users discover and install Rifteo agent skills when they ask questions like "is there a skill for X", "how do I write a finding", "find a skill that can...", or want to extend their agent for security and audit work.
---

# Find Rifteo Skills

When the user is looking for functionality that might exist as an installable Rifteo skill, help them discover and install it.

## Available Skills

${table}

## How to Find a Skill

**List all available skills:**
\`\`\`bash
rifteo-skills available
\`\`\`

**List what's already installed:**
\`\`\`bash
rifteo-skills list
\`\`\`

**Install a skill globally (available in all projects):**
\`\`\`bash
rifteo-skills add <skill-name> --global
\`\`\`

**Install for a specific agent:**
\`\`\`bash
rifteo-skills add <skill-name> --agent claude-code
\`\`\`

## Matching User Needs to Skills

When the user asks about a task, suggest the right skill:

${matching}

## Rules

- Always show the install command so the user can act immediately
- If no skill matches, offer to help directly using your own capabilities
- If the user wants a skill that doesn't exist yet, point them to contribute at github.com/rifteo/skills
`
}

const skills = loadSkills()
const output = generate(skills)
const outPath = path.join(ROOT, 'find-skills', 'SKILL.md')

fs.mkdirSync(path.dirname(outPath), { recursive: true })
fs.writeFileSync(outPath, output, 'utf8')

console.log(`Generated find-skills/SKILL.md with ${skills.length} skills:`)
skills.forEach(s => console.log(`  • ${s.name}`))
