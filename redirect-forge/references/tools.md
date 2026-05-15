# Tools Reference — Open Redirect Testing

## openredirex
Purpose-built open redirect fuzzer. Sends payloads across all discovered parameters.
```bash
pip install openredirex

# Basic usage — file of target URLs with FUZZ marker
openredirex -l targets.txt -p references/payloads.txt

# Single target
openredirex -u "https://target.com/login?next=FUZZ" -p references/payloads.txt
```

## ffuf
Fast fuzzer for parameter values. Filter out non-redirect responses.
```bash
# Fuzz redirect parameter
ffuf -u "https://target.com/login?next=FUZZ" \
     -w references/payloads.txt \
     -mc 301,302,307,308 \
     -fr "Location: https://target\.com"   # filter out safe redirects

# Test with custom header
ffuf -u "https://target.com/" \
     -H "Referer: FUZZ" \
     -w references/payloads.txt \
     -mc 301,302,307,308
```

## gau + gf
Collect URLs from Wayback Machine, Common Crawl, and OTX, then filter redirect params.
```bash
# Install
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/tomnomnom/gf@latest

# Run
gau target.com | gf redirect | sort -u | tee redirect-params.txt
```

## katana (active crawling)
```bash
katana -u https://target.com -d 4 -silent -jc -kf all | \
  grep -iE "(redirect|return|next|goto|url=|dest=|redir=|forward=|target=)" | sort -u
```

## nuclei (template-based)
```bash
nuclei -l redirect-params.txt -t nuclei-templates/http/redirect/ -severity medium,high,critical
```

## Burp Suite Workflow

1. **Param Miner** — discovers hidden redirect parameters:
   - Proxy tab → HTTP history → right-click request → Extensions → Param Miner → Guess params
   - Enable "Add 'fcbz' canary" to identify where parameters are reflected

2. **Intruder** — fuzz with payloads.txt:
   - Mark redirect value as payload position: `?next=§FUZZ§`
   - Load `references/payloads.txt` as payload list
   - Filter: Response received → match `Location:` containing `evil.com`

3. **Collaborator** — blind redirect detection:
   - Use a Collaborator URL as the redirect target
   - Confirm via Collaborator tab → DNS/HTTP interactions

4. **Match and Replace** — intercept and replace redirect param in all requests:
   - Proxy → Options → Match and Replace
   - Rule: replace `(?i)(next|redirect|url|return|goto)=https?://[^&]+` with `$1=https://COLLABORATOR-URL`

## interactsh (open-source OOB)
```bash
# Start OOB server
interactsh-client

# Use generated URL as redirect target
curl -v "https://target.com/login?next=https://YOUR-INTERACTSH-ID.oast.pro"
# Watch interactsh console for DNS/HTTP callback
```

## dalfox (also detects javascript: redirects)
```bash
dalfox url "https://target.com/login?next=test" --only-custom-payload
```

## Python one-liner — check if Location header reflects input
```bash
python3 -c "
import requests, sys
url = sys.argv[1]
r = requests.get(url, allow_redirects=False)
print('Status:', r.status_code)
print('Location:', r.headers.get('Location','(none)'))
" "https://target.com/login?next=https://evil.com"
```
