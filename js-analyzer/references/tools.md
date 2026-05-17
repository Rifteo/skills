# JS Analyzer — Tool Reference

## Discovery & Crawling

### katana
```bash
go install github.com/projectdiscovery/katana/cmd/katana@latest
# JS-aware crawl with 5 levels deep
katana -u https://target.com -jc -d 5 -o js-urls.txt
# With headless browser (for SPAs)
katana -u https://target.com -headless -jc -d 5
```

### gau (Get All URLs)
```bash
go install github.com/lc/gau/v2/cmd/gau@latest
gau target.com | grep "\.js$" | sort -u
gau --threads 5 target.com | grep "\.js" | sort -u
```

### waybackurls
```bash
go install github.com/tomnomnom/waybackurls@latest
waybackurls target.com | grep "\.js$" | sort -u
```

### hakrawler
```bash
go install github.com/hakluke/hakrawler@latest
echo "https://target.com" | hakrawler -js -d 4
```

### gospider
```bash
go install github.com/jaeles-project/gospider@latest
gospider -s "https://target.com" -c 10 -d 5 --js -o gospider-out/
```

### getJS
```bash
go install github.com/003random/getJS@latest
getJS --url https://target.com --complete --output js-list.txt
```

---

## Source Map Extraction

### sourcemapper
```bash
go install github.com/denandz/sourcemapper@latest
sourcemapper -url https://target.com/main.js.map -output ./src-out/
```

### unwebpack-sourcemap
```bash
pip3 install unwebpack-sourcemap
unwebpack_sourcemap https://target.com/main.js.map ./src-out/
```

---

## Secret Detection

### trufflehog
```bash
pip3 install trufflehog3
# or
brew install trufflesecurity/trufflehog/trufflehog

trufflehog filesystem ./js-files/ --only-verified
trufflehog git file://./repo/
```

### gitleaks
```bash
brew install gitleaks
# or
go install github.com/gitleaks/gitleaks/v8@latest

gitleaks detect --source ./js-files/ -v
gitleaks detect --source ./js-files/ --report-format json --report-path report.json
```

### SecretFinder
```bash
git clone https://github.com/m4ll0k/SecretFinder
pip3 install -r SecretFinder/requirements.txt

python3 SecretFinder.py -i https://target.com/main.js -o cli
python3 SecretFinder.py -i ./main.js -o cli  # local file
python3 SecretFinder.py -i https://target.com -e -o results.html  # entire domain
```

### jsluice
```bash
go install github.com/BishopFox/jsluice/cmd/jsluice@latest

jsluice secrets https://target.com/main.js
jsluice urls https://target.com/main.js
jsluice urls -R https://target.com/main.js | jq .  # recursive
```

---

## Endpoint & URL Extraction

### LinkFinder
```bash
git clone https://github.com/GerbenJavado/LinkFinder
pip3 install -r LinkFinder/requirements.txt

python3 linkfinder.py -i https://target.com/main.js -o cli
python3 linkfinder.py -i ./main.js -o cli
python3 linkfinder.py -i https://target.com -d -o results.html  # domain mode
```

---

## DOM XSS Scanning

### dalfox
```bash
go install github.com/hahwul/dalfox/v2@latest

dalfox url "https://target.com/page?param=FUZZ"
dalfox url "https://target.com/page?param=FUZZ" --deep-domxss
dalfox file urls.txt --worker 5
```

### Burp DOM Invader
- Built into Burp Suite Professional
- Enable in the Burp browser via the Burp icon → DOM Invader → Enable
- Automatically traces sources and sinks
- Use "postMessage interception" mode for iframe/postMessage testing

---

## Prototype Pollution

### ppfuzz
```bash
go install github.com/dwisiswant0/ppfuzz@latest
ppfuzz -u "https://target.com/?param=FUZZ" -t 30
```

### ppmap
```bash
git clone https://github.com/kleiton0x00/ppmap
npm install -g puppeteer
node ppmap/ppmap.js "https://target.com"
```

---

## Third-Party Library Scanning

### retire.js
```bash
npm install -g retire
retire --path ./js-files/ --outputformat json
retire --js --url https://target.com  # scan live site
retire --js --jsrepo custom.json ./js-files/  # custom vulnerability database
```

### npm audit
```bash
# If package.json is available (from source map extraction)
cd ./sourcemap-out/
npm audit
npm audit --json | jq '.vulnerabilities | to_entries[] | {pkg: .key, severity: .value.severity}'
```

---

## Deobfuscation

### js-beautify
```bash
npm install -g js-beautify
js-beautify --output pretty.js minified.js
js-beautify -r minified.js  # replace in place
```

### synchrony
```bash
npx synchrony deobfuscate obfuscated.js
npx synchrony deobfuscate --output deob.js obfuscated.js
```

### deobfuscate.io
- Online: https://deobfuscate.io
- Handles obfuscator.io and common obfuscation patterns

### prettier
```bash
npm install -g prettier
prettier --write main.js
```

---

## CSP Analysis

### csp-evaluator (Google)
- Online: https://csp-evaluator.withgoogle.com
- CLI wrapper:
```bash
pip3 install csp-evaluator
csp-evaluator "default-src 'self'; script-src 'unsafe-eval'"
```

### Burp Suite — CSP Auditor extension
- Install from BApp store
- Automatically flags weak CSP directives

---

## Framework-Specific

### Angular Security
```bash
# Check Angular version
grep -r "angular" ./js-files/ | grep -oE '"[0-9]+\.[0-9]+\.[0-9]+"' | head -5
# AngularJS 1.x sandbox escapes: https://portswigger.net/research/xss-without-html
```

### Next.js Analysis
```bash
# Detect Next.js
curl -s https://target.com | grep "_next"

# Extract build ID (useful for cache busting and chunk enumeration)
curl -s https://target.com/_next/static/chunks/pages/_app.js | head -5
```

---

## All-in-One Workflows

### Full JS recon pipeline
```bash
TARGET="target.com"

# 1. Collect JS URLs
(waybackurls $TARGET; gau $TARGET) | grep "\.js$" | sort -u > js-urls.txt
echo "https://$TARGET" | katana -jc -d 5 >> js-urls.txt
sort -u js-urls.txt -o js-urls.txt

# 2. Download all JS files
mkdir -p js-files
while read url; do
  filename=$(echo "$url" | md5sum | cut -d' ' -f1).js
  curl -s -m 10 "$url" -o "js-files/$filename" &
done < js-urls.txt
wait

# 3. Hunt for secrets
grep -rEh "AKIA[0-9A-Z]{16}|sk_live_[0-9a-zA-Z]{24}|ghp_[A-Za-z0-9]{36}|AIza[0-9A-Za-z\-_]{35}" js-files/ > secrets-found.txt

# 4. Extract endpoints
grep -rEoh '"(/api/[^"]+)"' js-files/ | sort -u >> endpoints.txt
grep -rEoh '"(/v[0-9]/[^"]+)"' js-files/ | sort -u >> endpoints.txt

# 5. Source maps
while read url; do
  mapurl="$url.map"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$mapurl")
  [ "$code" = "200" ] && echo "$mapurl" >> sourcemaps-found.txt
done < js-urls.txt
```
