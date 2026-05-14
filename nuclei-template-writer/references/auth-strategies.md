# Auth Strategies for Nuclei Templates

## Rule: always generate an unauthenticated probe first

Before any auth strategy, strip all auth from the request and test the same endpoint. Put this as a separate template block or a standalone file named `[template-id]-unauth.yaml`. If it hits, the vuln is pre-auth — higher severity, runs on every target with zero setup.

```yaml
# [template-id]-unauth.yaml
id: [template-id]-unauth

info:
  name: [Same name] — Unauthenticated Probe
  severity: [one level higher than authenticated version]
  tags: [same tags],unauth

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=[payload]"
    # No auth headers

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[same matcher as authenticated template]"
      - type: status
        status:
          - 200
```

---

## Strategy 1 — Bearer JWT / API key header

**When:** `Authorization: Bearer eyJ...` or `X-API-Key: abc123` in original request.

**Pattern:** declare a `token` variable, pass at runtime with `-var`.

```yaml
id: [template-id]

info:
  name: [name]
  severity: [severity]
  tags: [tags]

variables:
  token: "REPLACE_ME"

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=[payload]"
    headers:
      Authorization: "Bearer {{token}}"

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[evidence string]"
      - type: status
        status:
          - 200
```

**Run:**
```bash
nuclei -t template.yaml -l targets.txt -var "token=eyJ..."
```

**Scale tip:** if testing many targets on the same platform, register one test account and reuse the same token. For different platforms in your target list, split by platform and run with the matching token.

---

## Strategy 2 — Session cookie from login form

**When:** original request uses `Cookie: session=abc123` and the target has a login endpoint.

**Pattern:** two-step raw template. Step 1 logs in and extracts the session. Step 2 uses it on the vulnerable endpoint. Nuclei extracts and chains automatically.

```yaml
id: [template-id]

info:
  name: [name]
  severity: [severity]
  tags: [tags]

variables:
  username: "REPLACE_ME"
  password: "REPLACE_ME"

http:
  - raw:
      # Step 1 — login and extract session cookie
      - |
        POST /[login-path] HTTP/1.1
        Host: {{Hostname}}
        Content-Type: application/x-www-form-urlencoded

        username={{username}}&password={{password}}

      # Step 2 — exploit with extracted session
      - |
        GET /[vulnerable-path]?[param]=[payload] HTTP/1.1
        Host: {{Hostname}}

    cookie-reuse: true    # Nuclei carries cookies from step 1 to step 2 automatically

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[evidence string]"
      - type: status
        status:
          - 200
```

**Run:**
```bash
nuclei -t template.yaml -l targets.txt -var "username=test@test.com" -var "password=Test1234"
```

**Scale tip:** register a free test account on each target platform. Use the same credentials across all targets on the same platform.

---

## Strategy 3 — Login form that returns JWT (JSON response)

**When:** login endpoint returns `{"access_token": "eyJ..."}` and the vulnerable endpoint uses `Authorization: Bearer`.

**Pattern:** step 1 logs in, extracts JWT from JSON body, step 2 injects it in the header.

```yaml
id: [template-id]

info:
  name: [name]
  severity: [severity]
  tags: [tags]

variables:
  username: "REPLACE_ME"
  password: "REPLACE_ME"

http:
  - raw:
      # Step 1 — login and extract JWT
      - |
        POST /[login-path] HTTP/1.1
        Host: {{Hostname}}
        Content-Type: application/json

        {"email":"{{username}}","password":"{{password}}"}

      # Step 2 — use extracted JWT on vulnerable endpoint
      - |
        GET /[vulnerable-path]?[param]=[payload] HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{jwt_token}}

    extractors:
      - type: json
        name: jwt_token
        internal: true      # makes the value available to subsequent requests
        part: body
        json:
          - ".access_token"  # adjust to match actual JSON key

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[evidence string]"
      - type: status
        status:
          - 200
```

**Run:**
```bash
nuclei -t template.yaml -l targets.txt -var "username=test@test.com" -var "password=Test1234"
```

---

## Strategy 4 — Login form with CSRF token

**When:** login form has a hidden `_csrf` or `authenticity_token` field that must be fetched first.

**Pattern:** three steps. Fetch the login page, extract CSRF, login, exploit.

```yaml
id: [template-id]

variables:
  username: "REPLACE_ME"
  password: "REPLACE_ME"

http:
  - raw:
      # Step 1 — fetch login page and extract CSRF token
      - |
        GET /[login-page] HTTP/1.1
        Host: {{Hostname}}

      # Step 2 — submit login with CSRF token
      - |
        POST /[login-path] HTTP/1.1
        Host: {{Hostname}}
        Content-Type: application/x-www-form-urlencoded

        username={{username}}&password={{password}}&_csrf={{csrf_token}}

      # Step 3 — exploit
      - |
        GET /[vulnerable-path]?[param]=[payload] HTTP/1.1
        Host: {{Hostname}}

    cookie-reuse: true

    extractors:
      - type: regex
        name: csrf_token
        internal: true
        part: body
        regex:
          - 'name="_csrf"[^>]+value="([^"]+)"'  # adjust regex to match the actual field
        group: 1

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[evidence string]"
```

---

## Strategy 5 — Basic auth

**When:** `Authorization: Basic dXNlcjpwYXNz` in original request.

**Pattern:** pass base64-encoded credentials as a variable.

```yaml
id: [template-id]

variables:
  b64creds: "REPLACE_ME"   # base64 of "username:password"

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=[payload]"
    headers:
      Authorization: "Basic {{b64creds}}"

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "[evidence string]"
```

**Encode credentials:**
```bash
echo -n "username:password" | base64
```

**Run:**
```bash
nuclei -t template.yaml -l targets.txt -var "b64creds=dXNlcm5hbWU6cGFzc3dvcmQ="
```

---

## Strategy 6 — API key in custom header or query param

**When:** `X-API-Key: abc123` or `/endpoint?api_key=abc123` in original request.

```yaml
variables:
  api_key: "REPLACE_ME"

http:
  - method: GET
    path:
      - "{{BaseURL}}/[path]?[param]=[payload]&api_key={{api_key}}"
    # OR as a header:
    headers:
      X-API-Key: "{{api_key}}"
```

**Run:**
```bash
nuclei -t template.yaml -l targets.txt -var "api_key=your_key_here"
```

---

## When auth cannot be templated

Flag these in Step 5 and do not attempt to template them:

| Situation | Why it can't be templated |
|---|---|
| OAuth 2.0 / OIDC | Requires browser redirect and callback — no straight HTTP flow |
| SAML SSO | XML signing + IdP redirect chain |
| MFA / TOTP required | Time-based code needed at login |
| Client certificate (mTLS) | Requires local cert file — not portable across targets |
| Captcha on login | Cannot be bypassed in a template |

For these, include only the unauthenticated probe template and note: *"Authenticated variant requires manual testing — auth flow cannot be automated with Nuclei."*
