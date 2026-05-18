---
name: ctf-writeup
description: Generates a clean, publishable CTF challenge writeup from solve notes — suitable for HTB, CTFtime, personal blogs, and team wikis
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["ctf", "writeup", "hacking", "learning", "community"]
---

# CTF Writeup Generator

Turn solve notes, tool output, and scattered observations into a clean, publishable CTF writeup. Good writeups teach. Great writeups show the wrong turns too.

## When to Use

- User solved a CTF challenge and wants to document it
- User says "write up this challenge", "generate a writeup", "document my solve"
- Team wants a record of solutions for their internal wiki

## What You Need Before Starting

Ask if not provided:
- Challenge name, category, and point value
- CTF event name and date
- The flag (for confirmation)
- Key steps taken to solve it — notes, commands, payloads used
- Any wrong turns worth documenting

## Writeup Structure

### Header
```
# [Challenge Name] — [CTF Event Name]
**Category:** [Web / Pwn / Crypto / Forensics / OSINT / Misc]
**Points:** [value]
**Difficulty:** [as rated by organizer or personal assessment]
**Flag:** [flag{...}]
```

### Challenge Description
Paste the original challenge text or summarize it in 2-3 sentences. What was given? (URL, binary, file, hint?)

### Initial Analysis
What did you notice first? What tools did you use to understand the challenge? Keep it honest — include the first (wrong) hypothesis if it's instructive.

### Solution Walkthrough
Step-by-step. Number the steps. Show every command, payload, or key observation.

```bash
# Show actual commands
curl -X POST https://target/endpoint -d "param=payload"
```

Explain *why* each step worked — not just what happened. That's what makes a writeup worth reading.

### Key Insight
One paragraph: what was the core trick? What would someone need to know to solve this without your writeup? This is the part other players will search for.

### Flag
```
flag{the_actual_flag_here}
```

### Takeaways (optional)
What did you learn? What tool or technique was new? What would you do differently?

## Rules

- Show real commands and payloads — vague writeups help nobody
- Include wrong turns when they illustrate a useful lesson
- Keep the tone direct and technical — this is for peers, not a marketing audience
- If the challenge involves a CVE or known technique, name it and link to the reference
- Never publish writeups for active competitions where sharing is prohibited
