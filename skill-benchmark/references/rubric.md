# Scoring Rubric

Apply each dimension independently. Deduct points using the criteria below.
Never round up — if evidence is ambiguous, take the lower score.

---

## Dimension 1 — Trigger quality (25 pts)

The description field is the **only** thing agents see before deciding whether
to load a skill. If it is vague, the skill never fires. If it is too broad,
it fires on the wrong tasks.

**Start at 25. Deduct:**

| Signal | Deduct |
|--------|--------|
| Description is fewer than 30 words | −8 |
| Description uses only generic verbs ("help with", "assist", "improve") | −6 |
| Description contains no concrete trigger phrases (user-facing language) | −6 |
| No "use even when…" / "trigger also for…" extension clause | −3 |
| Trigger and body overlap heavily (description is just a title for the body) | −4 |
| Description promises more than the body delivers | −5 |

**Bonus (cap at 25):**

| Signal | Add |
|--------|-----|
| Contains ≥3 concrete example trigger phrases | +2 |
| Explicitly lists what it does NOT cover | +1 |

---

## Dimension 2 — Instruction clarity (25 pts)

Steps must be unambiguous enough that two different agents produce the same
result on the same input.

**Start at 25. Deduct:**

| Signal | Deduct |
|--------|--------|
| Steps are prose paragraphs with no numbered/bulleted structure | −10 |
| Any step uses "maybe", "if appropriate", "you could", "consider" | −4 per instance, max −12 |
| A step requires judgment without giving criteria (e.g. "choose the best approach") | −5 |
| Steps reference each other unclearly ("as above", "repeat step 2") | −3 |
| Body exceeds 500 lines without a table of contents or sub-references | −4 |
| No step defines what constitutes failure or an error condition | −4 |

---

## Dimension 3 — Agent-agnostic design (20 pts)

A skill that hardcodes assumptions about the runtime environment fails silently
on incompatible agents.

**Start at 20. Deduct:**

| Signal | Deduct |
|--------|--------|
| Assumes `bash` shell without a Windows/PowerShell fallback | −5 |
| References MCP tools by name without checking availability | −5 |
| References a specific IDE panel or GUI element (e.g. "click the sidebar") | −6 |
| Assumes a specific model family (e.g. "Claude will…", "GPT can…") | −4 |
| Hardcodes absolute paths (e.g. `/Users/john/`, `C:\Users\`) | −4 |
| Uses `npm`, `pip`, or `brew` without checking if available | −3 |
| References browser/display availability without fallback | −3 |

---

## Dimension 4 — Self-containment (15 pts)

An agent loading this skill for the first time, with no prior conversation
context, must be able to complete the task without needing to ask clarifying
questions about the skill's own operation.

**Start at 15. Deduct:**

| Signal | Deduct |
|--------|--------|
| Skill assumes a previous skill was run ("after running X skill…") | −5 |
| References an external document without bundling it or providing a URL | −5 |
| Requires environment variables without documenting where to set them | −4 |
| Uses pronouns with no clear antecedent ("run it", "apply the fix") at skill start | −3 |
| Skill behavior changes based on undocumented prior state | −4 |

---

## Dimension 5 — Output definition (15 pts)

If the skill does not define what a successful output looks like, agents will
produce wildly different formats and the user cannot rely on the result.

**Start at 15. Deduct:**

| Signal | Deduct |
|--------|--------|
| No output format defined (no template, schema, or example) | −10 |
| Output format defined but not consistently used in all branches | −5 |
| No success/done signal (agent doesn't know when to stop) | −4 |
| No error output format (what to say when something fails) | −3 |

---

## Score interpretation

| Range | Meaning |
|-------|---------|
| 90–100 | Excellent — publish as-is |
| 75–89 | Good — fix 1–2 items before publishing |
| 60–74 | Acceptable — usable but will degrade on some agents |
| 45–59 | Needs work — will silently fail often |
| Below 45 | Rewrite recommended |
