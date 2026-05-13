# Agent Profiles & Compatibility Matrix

Skills don't need to be tested on live agents. Compatibility is determined by
static analysis — looking for signals in the skill text that predict failure
on a given agent class.

---

## Agent profiles

Agents are grouped into 7 profiles. Each profile has a set of hard-fail and
soft-fail signals.

---

### Profile A — Shell-native CLI agents

**Agents:** Claude Code, OpenCode, Gemini CLI, Codex, Goose, Aider-Desk,
Devin for Terminal, Kiro CLI, ForgeCode, MCPJam, Roo Code, Firebender,
Mux, Crush, OpenHands, Deep Agents

**Assumptions:** Full shell access (`bash`/`zsh`), filesystem read/write,
can run subprocesses, usually Linux/macOS.

**Hard-fail signals (mark ❌ if any present):**
- Skill instructs GUI interaction ("click", "open the panel", "drag")
- Skill requires a running browser without a headless fallback
- Skill assumes Windows-only tools (`powershell.exe`, `.bat`, `winget`)

**Soft-fail signals (mark ⚠️ if any present):**
- Skill uses `brew` without `apt`/`yum` fallback
- Skill uses `python` (may be `python3` on newer systems)
- Skill assumes `git` is pre-configured with credentials

---

### Profile B — IDE-embedded agents

**Agents:** Cursor, Windsurf, GitHub Copilot, Cline, Continue, Kilo Code,
Rovo Dev, Trae, Trae CN, Dexto, Warp, Zencoder, Tabnine CLI, Neovate,
Code Studio, CodeBuddy

**Assumptions:** Running inside an editor, active file/project in context,
may have limited or no subprocess shell, Windows is common.

**Hard-fail signals (mark ❌ if any present):**
- Skill uses `bash -c` or shell subprocesses as primary mechanism
- Skill reads files using shell commands only (no fallback to file-read tool)
- Skill assumes Linux paths (`/home/`, `/usr/`)

**Soft-fail signals (mark ⚠️ if any present):**
- Skill uses MCP tools not guaranteed in IDEs
- Skill assumes `git` CLI is available (some IDE agents use git API instead)
- Skill references terminal sessions or tmux

---

### Profile C — MCP-aware agents

**Agents:** Claude Code, Goose, Roo Code, OpenHands, Junie, Windsurf
(with MCP enabled), Augment, Kode

**Assumptions:** MCP server support available, can call external services via
MCP protocol.

**Hard-fail signals (mark ❌ if any present):**
- Skill references MCP tool names that are non-standard (custom MCPs)
  without checking availability first

**Soft-fail signals (mark ⚠️ if any present):**
- Skill uses MCP calls without a non-MCP fallback path
- Skill assumes a specific MCP server is running

---

### Profile D — Lightweight / minimal agents

**Agents:** Amp, Kimi Code CLI, Pi, Qoder, Pochi, AdaL, Replit, Universal,
iFlow CLI, Hermes Agent, Mistral Vibe, Command Code, Cortex Code, Droid

**Assumptions:** Minimal tool set, often just read/write/search. No subprocess
execution. Context window may be smaller.

**Hard-fail signals (mark ❌ if any present):**
- Skill relies on subprocess execution as the primary mechanism
- Skill body exceeds 400 lines with no summary/progressive disclosure

**Soft-fail signals (mark ⚠️ if any present):**
- Skill uses more than 3 external tool types
- Skill has nested conditional branches more than 2 levels deep

---

### Profile E — Enterprise / restricted agents

**Agents:** IBM Bob, CodeArts Agent, Codemaker, Qwen Code, Antigravity,
Junie (enterprise), Rovo Dev (Atlassian)

**Assumptions:** Network access may be restricted, external URLs may be
blocked, compliance constraints may apply.

**Hard-fail signals (mark ❌ if any present):**
- Skill fetches from external URLs as a required step with no offline fallback
- Skill sends data to third-party APIs as a core step

**Soft-fail signals (mark ⚠️ if any present):**
- Skill uses public CDN links without noting they may be blocked
- Skill stores credentials in plaintext files

---

### Profile F — Notebook / data agents

**Agents:** Continue (data mode), Codex (Jupyter), Replit

**Assumptions:** Notebook-aware, Python-first, may not have terminal.

**Hard-fail signals (mark ❌ if any present):**
- Skill is entirely shell-based with no Python/notebook alternative

**Soft-fail signals (mark ⚠️ if any present):**
- Skill assumes sequential file execution outside a notebook

---

### Profile G — Windows-native agents

**Agents:** Warp (Windows), Cursor (Windows), GitHub Copilot (Windows),
Windsurf (Windows), Trae (Windows), Code Studio (Windows)

**Assumptions:** PowerShell or CMD primary shell, Windows paths, no `bash`
by default.

**Hard-fail signals (mark ❌ if any present):**
- Skill uses bash-only constructs (`#!/bin/bash`, `&&` chaining without
  PowerShell equivalent, `chmod`, `ln -s`)
- Skill uses Linux paths as hard requirements

**Soft-fail signals (mark ⚠️ if any present):**
- Skill uses `python3` (often just `python` on Windows)
- Skill uses forward-slash paths without noting Windows alternative

---

## Compatibility signal quick-reference

Use this table when scanning the target skill for signals.

| Text pattern in skill | Profile affected | Severity |
|---|---|---|
| `bash -c` / `#!/bin/bash` | B, G | Hard |
| `chmod` / `ln -s` / `grep -E` | G | Hard |
| GUI verb: "click", "drag", "open panel" | A | Hard |
| `fetch('https://...external...')` as required step | E | Hard |
| Body > 400 lines, no TOC | D | Hard |
| MCP tool reference, no fallback | C | Soft |
| `brew install` without apt fallback | A | Soft |
| `/home/` or `/usr/` hardcoded | B, G | Soft |
| `python` (not `python3`) | A | Soft |
| `git push` / credential operations | B | Soft |
| External URL, no offline note | E | Soft |
| Nested conditionals (3+ deep) | D | Soft |
| `tmux` / `screen` | B | Soft |
| `winget` / `.bat` / `powershell.exe` | A | Hard |
