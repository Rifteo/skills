---
name: nuclei-template-writer
description: Converts a vulnerability description or HTTP request/response pair into a ready-to-run Nuclei YAML template — handles auth strategies, matcher selection, OOB detection, and multi-step flows. Use when you want to automate detection of a finding across other targets or build a personal template library.
license: MIT
metadata:
  version: "0.0.1"
  author: Rifteo
  tags: ["nuclei", "automation", "scanner", "template", "pentest", "bug-bounty"]
---

# Nuclei Template Writer

Turns a finding into a Nuclei template. The template can then be run against thousands of targets to find the same vulnerability at scale.

## Protocol

### Step 0 — Parse the input

Identify the input type — determines how precise the output can be:

| Type | What was given | Template quality |
|---|---|---|
| A | Description only | Skeleton with placeholder payloads — mark what needs customization |
| B | HTTP request only | Parameterized request, best-guess matchers — note matchers are inferred |
| C | HTTP request + response | Full template with precise matchers — production ready |
| D | Multiple requests (IDOR, multi-step) | Multi-step raw template |

Extract every detail available:
- HTTP method, full path, query parameters
- Request headers (note auth headers — document them, never hardcode values)
- Request body
- Response status code, response headers, response body (key sections)
- Any payload or test string mentioned
- Any error message, leaked string, or behavioral signal described

If input is ambiguous, ask ONE question: "What does the response look like when the vulnerability triggers?"

---

### Step 1 — Classify the vulnerability

Match the finding against `references/vuln-classes.md`. Identify:
- **Primary class** — XSS, SQLi, SSRF, LFI, IDOR, etc.
- **Severity** — from the class table; adjust up if auth not required or down if interaction needed
- **Tags** — from the class table
- **Detection method** — response-based, OOB, time-based, or status-based

If the class is not in the table, follow this fallback in order:
1. Does the response contain a unique string when the vuln triggers? → word matcher
2. Does the response contain a pattern (version, key, email)? → regex matcher
3. Is there no response signal at all (blind vuln)? → go to Step 2's interactsh path
4. If none apply, stop and output: `[nuclei-template-writer] Cannot determine detection method — provide the response body or describe what changes when the vulnerability triggers.`

---

### Step 2 — Choose detection strategy

Use `references/matcher-guide.md` to select the right matcher. Priority order:

1. **Word matcher** — if a specific string appears in the response (error message, reflected payload, leaked data). Most reliable, lowest false-positive risk.
2. **Regex matcher** — if the evidence is a pattern (version number, email, secret format, dynamic value).
3. **Status matcher** — only as a secondary matcher, never alone (too many false positives).
4. **DSL matcher** — for time-based blind vulns (`response_time > 5`) or header condition checks.
5. **Interactsh matcher** — for blind OOB vulns (SSRF, blind XXE, blind command injection). Requires `{{interactsh-url}}` as the payload.

Always combine matchers with `matchers-condition: and` when using status + word/regex to reduce false positives.

---

### Step 2.5 — Determine auth strategy

Check if the original request contains any authentication. Use `references/auth-strategies.md` to select the right approach.

**First — always generate an unauthenticated probe variant:**
Strip all auth headers/cookies and test the same endpoint. Include this as a separate template or first request block. Reason: the same vuln may be exploitable without auth on other targets even if auth was required on the original. If the unauthenticated probe hits, upgrade severity by one level.

**Then — handle the authenticated case based on auth type:**

| Auth detected | Strategy | Scales to other targets? |
|---|---|---|
| No auth | Unauthenticated probe only — done | ✅ Yes, fully |
| Bearer JWT / API key header | `{{token}}` variable + `-var` at runtime | ✅ Yes, one token per target |
| Session cookie from login form | Login-flow template — auto-extracts token | ✅ Yes, with test credentials |
| Basic auth | `{{b64creds}}` variable, base64 of user:pass | ✅ Yes, one cred set per target |
| OAuth / SAML / SSO | Flag as limitation — too complex for a template | ❌ Manual only |
| CSRF token in body | Login-flow template — extracts CSRF then exploits | ✅ Yes, with test credentials |

See `references/auth-strategies.md` for the full template pattern for each auth type.

---

### Step 3 — Generate the template

Follow the Nuclei YAML schema exactly. Build each block:

**ID:** `{vuln-class}-{endpoint-slug}` — kebab-case, descriptive, unique.
Example: `reflected-xss-api-user-export-format`

**Info block:**
```yaml
info:
  name: [human-readable description of what this detects]
  author: [leave blank or use "custom"]
  severity: [info/low/medium/high/critical]
  description: [one sentence — what triggers it and what the impact is]
  tags: [from vuln-classes.md, comma-separated]
```

**HTTP block:**
- Replace the hostname with `{{BaseURL}}`
- Replace OOB payloads with `{{interactsh-url}}`
- Replace dynamic/session values (CSRF tokens, timestamps) with notes
- Never hardcode auth tokens — always use variables (see auth strategy from Step 2.5)
- For login-flow templates: use `raw:` block with `cookie-reuse: true` and an extractor on the first request
- For multi-step (IDOR): use `raw:` block with `cookie-reuse: true`

**Matchers:**
- Add `matchers-condition: and` when using multiple matchers
- Word matchers: use the exact string from the response, not a generic one
- Regex matchers: keep patterns tight — prefer anchors and specific character classes
- Always add a status matcher as secondary when the vuln returns a specific code

**Variables block** — always declare variables for anything target-specific:
```yaml
variables:
  token: "REPLACE_ME"       # for Bearer/API key auth
  username: "REPLACE_ME"    # for login-flow templates
  password: "REPLACE_ME"    # for login-flow templates
```

**Output order when auth is required:** generate two templates:
1. Unauthenticated probe (stripped of auth) — label it `[unauthenticated]`
2. Authenticated template with chosen auth strategy — label it `[authenticated]`

Apply the skeleton from `references/vuln-classes.md` for the matched class, then apply the auth pattern from `references/auth-strategies.md`.

---

### Step 4 — Output

Produce in this exact order:

**1. The complete template** — fenced as ` ```yaml `

**2. Customize before running** — bullet list of exactly what to change before the template works:
- Which headers need real values
- Which payloads need adjustment for the target
- Whether interactsh needs to be set up

**3. Test command** — show the right command for the auth strategy used:
```bash
# No auth — run directly
nuclei -t template-name.yaml -l targets.txt

# Bearer / API key — pass token at runtime
nuclei -t template-name.yaml -l targets.txt -var "token=eyJ..."

# Login-flow — pass credentials at runtime
nuclei -t template-name.yaml -l targets.txt -var "username=test@test.com" -var "password=Test1234"

# OOB template
nuclei -t template-name.yaml -l targets.txt -iserver https://interactsh.com
```

**4. Validate before bulk-running:** test on one confirmed-vulnerable target (expect a hit) and one clean target (expect no hit). If both trigger, the matcher is too broad — tighten the word or regex before scaling.

---

### Step 5 — Flag limitations

State clearly if any of the following apply:

- **OOB required:** "This template uses interactsh — set up a listener before running. Hits will appear in your interactsh dashboard, not in nuclei output directly."
- **Auth required (Bearer/API key):** "Pass your token at runtime with `-var token=YOUR_TOKEN`. You need a valid account on each target. The unauthenticated probe is included — check if it hits first."
- **Auth required (login flow):** "Pass test credentials with `-var username=X -var password=Y`. The template logs in automatically and extracts the session. You need a registered account on each target."
- **Auth required (OAuth/SSO):** "Cannot be templated reliably — OAuth flows require browser interaction. Test manually on each target."
- **Multi-account required (IDOR):** "This template needs two valid accounts on the target. Replace `VICTIM_OBJECT_ID` and `ATTACKER_SESSION` with real values."
- **Low confidence matchers (Type A/B):** "Matchers are inferred from the description — validate against the real response before bulk-running to avoid false positives."

---

## Reference Files

- `references/vuln-classes.md` — Vulnerability class table with severity, tags, and template skeletons
- `references/matcher-guide.md` — Matcher type selection guide with examples
- `references/auth-strategies.md` — Auth patterns and full template examples per auth type
