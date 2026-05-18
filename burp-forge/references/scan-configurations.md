# Burp Scan Configurations

Recommended scan configurations by target type and time available.

---

## Comprehensive Web Scan
**Use when:** Full engagement, 1+ days available, broad web application scope

**Crawl settings:**
- Max crawl depth: unlimited
- Max crawl requests: 10,000
- Detect custom 404: yes
- Application login: configure with all test account credentials

**Scan checks:**
- All active checks enabled
- All passive checks enabled
- JavaScript analysis: enabled
- Out-of-band checks: enabled (use Burp Collaborator)

**Insertion points:**
- URL parameters, body parameters, cookies, headers
- Include JSON values, XML values, multipart parameters

---

## Lightweight / Bug Bounty
**Use when:** Time-boxed assessment, bug bounty, quick win focus

**Crawl settings:**
- Max crawl depth: 5
- Max crawl requests: 2,000
- Focus on authenticated crawl with highest-privilege account

**Scan checks:**
- Active: SQLi, XSS, SSRF, path traversal, OS command injection only
- Passive: all enabled
- Skip: SSL checks, clickjacking, information disclosure (handle manually)

**Insertion points:**
- URL parameters, body parameters, cookies
- Skip headers (reduces noise significantly)

---

## API Scan
**Use when:** REST or GraphQL API target, no traditional web UI

**Setup:**
- Import OpenAPI/Swagger spec if available
- Use Burp's built-in OpenAPI parser to auto-populate endpoints
- Configure auth: Bearer token or API key in header

**Crawl settings:**
- Disable browser-based crawl
- Use manual endpoint list from spec or JS analysis

**Scan checks:**
- Active: SQLi, injection, path traversal, SSRF, auth bypass
- Passive: all enabled
- Enable: JSON insertion points, parameter name fuzzing

**Insertion points:**
- JSON body values, URL path segments, query parameters
- Test each parameter individually — APIs often have per-parameter logic

---

## Authenticated Scan (any config)
**Additional steps for authenticated testing:**

1. Record login macro in Burp for session handling
2. Set session handling rule: re-authenticate when 401/403 received
3. Configure scope to include authenticated-only endpoints
4. Run separate scan instances per role (user, admin, API key)

**Credential handling:**
- Store credentials in Burp project file only — never in scan config exports
- Use separate Burp projects per client engagement

---

## Scan Performance Tips

- Disable checks you'll test manually (IDOR, business logic, auth flows) — Burp is weak here
- Enable Burp Collaborator for SSRF and blind injection — dramatically increases confirmed findings
- Set thread count to 10-15 for production targets (avoid rate limiting / DoS)
- Use "audit selected items" on high-value endpoints rather than full-site scan for speed
