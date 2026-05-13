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

const dirs = fs.readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !SKIP.has(d.name))

let errors = 0

for (const dir of dirs) {
  const skillFile = path.join(ROOT, dir.name, 'SKILL.md')
  const label = `${dir.name}/SKILL.md`

  if (!fs.existsSync(skillFile)) {
    console.error(`[FAIL] ${dir.name}/ — missing SKILL.md`)
    errors++
    continue
  }

  const content = fs.readFileSync(skillFile, 'utf8')

  if (!content.match(/^---\n[\s\S]*?\n---/)) {
    console.error(`[FAIL] ${label} — malformed or missing frontmatter (check opening and closing ---)`)
    errors++
    continue
  }

  const fm = parseFrontmatter(content)

  if (!fm) {
    console.error(`[FAIL] ${label} — could not parse frontmatter`)
    errors++
    continue
  }

  if (!fm.name) {
    console.error(`[FAIL] ${label} — missing required field: name`)
    errors++
  } else if (fm.name !== dir.name) {
    console.error(`[FAIL] ${label} — name "${fm.name}" does not match folder name "${dir.name}"`)
    errors++
  }

  if (!fm.description) {
    console.error(`[FAIL] ${label} — missing required field: description`)
    errors++
  } else if (fm.description.includes('|')) {
    console.error(`[FAIL] ${label} — description contains "|" which breaks the markdown table`)
    errors++
  }

  if (errors === 0 || !['name', 'description'].some(k => !fm[k])) {
    console.log(`[OK]   ${label}`)
  }
}

if (errors > 0) {
  console.error(`\n${errors} error(s) found — fix them before merging.`)
  process.exit(1)
} else {
  console.log('\nAll skills valid.')
}
