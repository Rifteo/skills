---
skill: remediation-planner
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: remediation-planner
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Incomplete | Complete | 🟢 +3 level(s) |
| Turns to complete | 2 | 1 | 🟢 -1 turn(s) |
| Response tokens | ~2,419 | ~1,052 | 🟢 -57% |
| Total time | 44s | 22s | 🟢 -50% |
| User effort | Medium | Low | 🟢 Low |

## Scenario

Dev asks how to fix a SQLi in their code, release is in 3 days

## Without Skill — 2 turns required

The agent received the prompt with no skill loaded. The first response was incomplete — it took 2 rounds of prompting to reach a usable result.

### Turn 1

**Prompt**

pentest found a SQLi on our search endpoint. here's the Java Spring Boot code:

@GetMapping("/search")
public List<Product> search(@RequestParam String query) {
    String sql = "SELECT * FROM products WHERE name = '" + query + "'";
    return jdbcTemplate.query(sql, productMapper);
}

payload that worked: ' OR '1'='1' --

we have a release in 3 days, how do we fix this and in what order?

**Response**

## SQL Injection Fix - Priority Order

### 1. Immediate Fix (Do This First - 30 mins)

The core problem is string concatenation building SQL. Fix with a parameterized query:

```java
// VULNERABLE - never do this
String sql = "SELECT * FROM products WHERE name = '" + query + "'";

// FIXED - parameterized query
@GetMapping("/search")
public List<Product> search(@RequestParam String query) {
    String sql = "SELECT * FROM products WHERE name = ?";
    return jdbcTemplate.query(sql, productMapper, query);
}
```

The `?` placeholder ensures the driver treats input as **data, never as SQL syntax**, regardless of content.

---

### 2. Add Input Validation (Do This Second)

```java
@GetMapping("/search")
public List<Product> search(@RequestParam String query) {

    // basic validation - adjust rules to your business needs
    if (query == null || query.isBlank()) {
        throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Query required");
    }
    if (query.length() > 100) {
        throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Query too long");
    }

    String sql = "SELECT * FROM products WHERE name = ?";
    return jdbcTemplate.query(sql, productMapper, query);
}
```

> **Note:** Validation is a second layer, not a replacement for parameterized queries. Attackers can bypass input filters; they cannot bypass parameterized queries.

---

### 3. Consider Using Spring Data JPA (Better Long-term)

If you have time and this pattern exists elsewhere in the codebase:

```java
// Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByNameContainingIgnoreCase(String name);
    // Spring generates the safe query automatically
}

// Controller
@GetMapping("/search")
public List<Product> search(@RequestParam String query) {
    return productRepository.findByNameContainingIgnoreCase(query);
}
```

---

### 4. Check for the Same Pattern Elsewhere

Before release, scan the whole codebase:

```bash
# fin

*[truncated]*

*Missing sections triggered 1 follow-up prompt(s) before the agent produced a complete result.*

## With Skill — 1 turn, complete

Same prompt, with `remediation-planner` loaded as system context.

### Turn 1

**Prompt**

pentest found a SQLi on our search endpoint. here's the Java Spring Boot code:

@GetMapping("/search")
public List<Product> search(@RequestParam String query) {
    String sql = "SELECT * FROM products WHERE name = '" + query + "'";
    return jdbcTemplate.query(sql, productMapper);
}

payload that worked: ' OR '1'='1' --

we have a release in 3 days, how do we fix this and in what order?

**Response**

**Remediation Plan: SQL Injection in `/search` Endpoint (Spring Boot / JdbcTemplate)**

---

**Step 1 — Replace String Concatenation with a Parameterized Query**
Swap the concatenated SQL string for a `?` placeholder — JdbcTemplate handles binding safely and this is a one-line change.

`Effort: Low`

**Before (vulnerable):**
```java
String sql = "SELECT * FROM products WHERE name = '" + query + "'";
return jdbcTemplate.query(sql, productMapper);
```

**After (safe):**
```java
String sql = "SELECT * FROM products WHERE name = ?";
return jdbcTemplate.query(sql, productMapper, query);
```

> This is your **release blocker fix**. Do this before anything else ships.

---

**Step 2 — Add Input Validation on the `query` Parameter**
Reject or sanitize inputs that don't match expected patterns — a product name search shouldn't accept quotes, comment sequences (`--`, `/*`), or semicolons.

`Effort: Low`

```java
@GetMapping("/search")
public ResponseEntity<List<Product>> search(@RequestParam String query) {
    if (query == null || query.isBlank() || query.length() > 100) {
        return ResponseEntity.badRequest().build();
    }
    // optional: allowlist pattern if product names are alphanumeric only
    if (!query.matches("[\\w\\s\\-]+")) {
        return ResponseEntity.badRequest().build();
    }
    String sql = "SELECT * FROM products WHERE name = ?";
    return ResponseEntity.ok(jdbcTemplate.query(sql, productMapper, query));
}
```

> Adjust the regex to match your actual product naming rules. This is defense-in-depth — Step 1 is still the primary fix.

---

**Step 3 — Audit All Other JdbcTemplate Usages in the Codebase**
The same pattern almost certainly exists elsewhere. Search for `jdbcTemplate` and any string concatenation with user-supplied variables before the release.

`Effort: Low–Medium`

Run this in your repo to find candidates:
```bash
grep -rn "jdbcTemplate" src/ | grep -E '"\s*\+|query\s*\+'
```
Or search your IDE for `jdbcTemplate.query` and `jdbcTemplat

*[truncated]*

## What changed

Without the skill, the first response was **Incomplete** — the agent needed **2 turns** and follow-up prompts to fill the gaps. With the skill, the agent delivered a **Complete** answer in **1 turn**.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
