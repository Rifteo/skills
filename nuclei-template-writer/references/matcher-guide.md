# Matcher Selection Guide

## Decision tree

```
Does the response body contain a specific string when the vuln triggers?
  YES → word matcher
  NO  →
    Is the evidence a pattern (version, email, key, dynamic value)?
      YES → regex matcher
      NO  →
        Is it a blind/OOB vuln (SSRF, blind SQLi, blind RCE)?
          YES → interactsh matcher
          NO  →
            Is it time-based (blind SQLi, sleep-based)?
              YES → dsl matcher (response_time)
              NO  → status matcher (last resort, always pair with another)
```

---

## Word matcher

Best for: reflected payloads, error messages, specific leaked strings, version banners.

```yaml
matchers:
  - type: word
    part: body          # body / header / response / all
    words:
      - "root:x:0:0"    # path traversal — /etc/passwd content
    case-insensitive: false  # set true for error messages
```

**Multiple words (AND logic — all must appear):**
```yaml
- type: word
  part: body
  words:
    - "syntax error"
    - "mysql"
  condition: and
```

**Multiple words (OR logic — any must appear):**
```yaml
- type: word
  part: body
  words:
    - "ORA-"
    - "syntax error in your SQL"
    - "mysql_fetch"
  condition: or
```

**Header matching:**
```yaml
- type: word
  part: header
  words:
    - "Access-Control-Allow-Origin: *"
```

---

## Regex matcher

Best for: PII patterns, API keys, version strings, dynamic values that change per response.

```yaml
matchers:
  - type: regex
    part: body
    regex:
      - "([a-zA-Z0-9]{32,45})"          # generic secret
      - "AIza[0-9A-Za-z\\-_]{35}"        # Google API key
      - "AKIA[0-9A-Z]{16}"               # AWS access key
      - "[0-9]+\\.[0-9]+\\.[0-9]+"       # version number
      - "[a-z0-9._%+\\-]+@[a-z0-9.\\-]+\\.[a-z]{2,4}"  # email
```

**Keep regex tight** — broad patterns create massive false positives at scale.

---

## Status matcher

Best for: auth bypass (expect 200 on protected endpoint), access control (expect 403→200).

**Never use alone.** Always combine with word or regex:

```yaml
matchers-condition: and
matchers:
  - type: status
    status:
      - 200
  - type: word
    part: body
    words:
      - "admin_panel"
```

---

## DSL matcher

Best for: time-based blind SQLi, conditional response size checks, complex header logic.

```yaml
# Time-based blind SQLi (sleep 5 seconds)
matchers:
  - type: dsl
    dsl:
      - "duration >= 5"

# Response size comparison
  - type: dsl
    dsl:
      - "len(body) > 5000"

# Header value check
  - type: dsl
    dsl:
      - "contains(tolower(all_headers), 'access-control-allow-origin: *')"
      - "status_code == 200"
    condition: and
```

**Common DSL variables:**
| Variable | What it is |
|---|---|
| `duration` | Response time in seconds |
| `status_code` | HTTP status code |
| `body` | Response body as string |
| `all_headers` | All response headers as string |
| `len(body)` | Response body length |
| `contains(s, sub)` | True if s contains sub |
| `tolower(s)` | Lowercase string |

---

## Interactsh matcher (OOB)

Best for: blind SSRF, blind XXE, blind command injection, blind SSTI.

**How it works:** Nuclei replaces `{{interactsh-url}}` with a unique callback URL. When the target makes an outbound request to that URL, Nuclei's interactsh server records the hit. The matcher fires on the callback, not the HTTP response.

```yaml
http:
  - method: GET
    path:
      - "{{BaseURL}}/fetch?url=http://{{interactsh-url}}"

    matchers:
      - type: word
        part: interactsh_protocol   # "http", "dns", or "smtp"
        words:
          - "http"
```

**For DNS-based detection (more reliable through firewalls):**
```yaml
    matchers:
      - type: word
        part: interactsh_protocol
        words:
          - "dns"
```

**Running with interactsh:**
```bash
nuclei -t template.yaml -l targets.txt -iserver https://interactsh.com
```

Callbacks appear in nuclei output AND at `https://app.interactsh.com` if using the hosted server.

---

## Extractors (bonus — pull data from responses)

Use extractors to capture and display interesting values found during scanning:

```yaml
extractors:
  - type: regex
    part: body
    name: api_key
    regex:
      - "api_key['\"]?\\s*[:=]\\s*['\"]?([a-zA-Z0-9_\\-]{20,})"
    group: 1        # capture group index

  - type: kval      # key=value extractor
    kval:
      - server      # extracts Server header value
```

Extracted values appear in nuclei output next to the finding.
