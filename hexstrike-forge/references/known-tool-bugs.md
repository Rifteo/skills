# Known Tool Bugs

Behavioral issues for tools that are present but misbehave. When you hit one of these, apply the handling rule immediately — do not retry the broken invocation.

If a tool is simply not found, do not use this file. Return to `tool-sequences.md`, find the capability needed for that phase, and pick a different available tool that covers it.

---

## Tool returns an unrecognised option error

**Symptom:** Any tool exits immediately with `No such option`, `unknown flag`, or `unrecognized argument`
**Cause:** HexStrike may run a different version of the tool than expected. CLI flags change between versions.
**Handling:** Do not guess corrected flags. Ask HexStrike for the tool's help output (`<tool> --help`) to get the correct flag syntax for the installed version, then re-invoke.

---

## Tool times out with partial output

**Symptom:** Process exits at the scan timeout with no completion marker but non-empty stdout
**Common tools:** nikto, nmap full-port scans, large nuclei runs
**Handling:** Do not discard. Extract whatever was returned, triage it as normal, and note in the finding: "Scan incomplete (timeout) — partial results triaged." Then continue the engagement — do not re-run the timed-out scan unless critical coverage is missing.

---

## Tool completes instantly with empty output

**Symptom:** Command exits 0 in under 2 seconds with no results on a target that should have results
**Common causes:** Rate limiting, silent auth failure, target filtering the tool's requests
**Handling:** Do not treat as a clean result. Mark the phase as inconclusive. If the target is public and not rate-limited, the tool may have a connectivity issue — note it and move to the next phase.

---

## Tool output contains ANSI color codes or JSON wrapper metadata

**Symptom:** Raw output is wrapped in `{"stdout": "...", "exit_code": 0}` or littered with `[92m` escape sequences
**Handling:** Always extract the `stdout` field and strip ANSI codes before reading. This applies to every tool response, not just known offenders.
