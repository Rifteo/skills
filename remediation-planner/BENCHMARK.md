---
skill: remediation-planner
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: remediation-planner

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~1,227 | ~748 | **🟡 -39%** |
| Time | 42s | 24s | **🟡 -43%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Create a remediation plan for a time-based blind SQL injection in the user search endpoint — PostgreSQL backend, parameter is username in a GET request
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Create a remediation plan for a time-based blind SQL injection in the user search endpoint — PostgreSQL backend, parameter is username in a GET request

**Response**
```
## Remediation Plan: Time-Based Blind SQLi — User Search Endpoint

---

### Root Cause

The `username` parameter is interpolated directly into a SQL query string before execution, allowing an attacker to inject `pg_sleep()` or similar timing primitives to extract data character by character without visible output.

---

### Priority Fix: Parameterized Queries

This is the only complete fix. Everything else below is defense-in-depth.

**Before (vulnerable):**
```python
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

**After (fixed):**
```python
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

For ORMs:
```python
# SQLAlchemy
User.query.filter(User.username == username).all()

# Django ORM
User.objects.filter(username=username)
```

The parameter placeholder (`%s` in psycopg2, `$1` in asyncpg) causes the driver to send the value as a bind parameter — the database engine never parses it as SQL.

---

### Laye
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `remediation-planner` loaded as context.

#### Turn 1

**Prompt**
> Create a remediation plan for a time-based blind SQL injection in the user search endpoint — PostgreSQL backend, parameter is username in a GET request

**Response**
```
**Remediation Plan: Time-Based Blind SQL Injection in User Search Endpoint (`username` parameter)**

---

**Step 1 — Parameterize the Query Immediately**
Replace the raw string interpolation of `username` with a parameterized query or prepared statement. In PostgreSQL this means using `$1` placeholders (e.g., via `pg`, `psycopg2`, `JDBC`, or your ORM) — the driver then handles quoting and escaping at the protocol level, eliminating the injection surface entirely.
`Effort: Low`

---

**Step 2 — Audit All Other Query Construction in the Codebase**
The presence of one injectable parameter strongly suggests the same pattern is used elsewhere. Search for string concatenation or interpolation in SQL strings across all data-access code (look for patterns like `"SELECT … " + variable` or f-strings/template literals building queries). Fix every instance, not just this endpoint.
`Effort: Medium`

---

**Step 3 — Enforce Input Validation on `username`**
Add an allowlist validator at the controlle
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
