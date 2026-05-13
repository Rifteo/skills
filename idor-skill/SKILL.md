---
name: idor
description: >
  Insecure Direct Object Reference (IDOR) vulnerability detection and exploitation methodology for web application security testing and penetration testing. Use this skill whenever the user asks to test for IDOR, broken object-level authorization (BOLA), access control issues on APIs or web apps, privilege escalation (horizontal or vertical), or when they mention testing endpoints with IDs, UUIDs, usernames, or any object reference in URLs, JSON bodies, headers, or cookies. Also trigger when the user says things like "test if I can access other users' data", "check authorization on this API", or "find broken access control". This skill gives the agent a complete, exhaustive methodology — always use it instead of ad-hoc guessing.
---

# IDOR / BOLA Detection Skill

IDOR (Insecure Direct Object Reference) — also called BOLA (Broken Object Level Authorization) in API contexts — occurs when an application exposes a reference to an internal object (ID, filename, key) without verifying the requester is authorized to access it.

This is the #1 finding in bug bounty programs. A systematic approach is essential; random testing misses most cases.

---

## Phase 1 — Reconnaissance: Find All Object References

Before testing anything, map every place the application exposes object references. Cast a wide net.

### 1.1 URL Path Parameters
```
GET /api/users/1234/profile
GET /invoices/9981/download
GET /orders/ORD-2024-00042
```

### 1.2 Query String Parameters
```
GET /dashboard?user_id=1234
GET /export?report=88&account=5
GET /messages?thread=229&inbox=user1
```

### 1.3 Request Body (JSON / Form Data)
```json
{ "user_id": 1234, "account": "ACC-99" }
```
```
POST /transfer
to_account=12345&amount=100
```

### 1.4 Headers
- `X-User-ID`, `X-Account`, `X-Tenant-ID`
- Custom headers injected by proxies or internal routing

### 1.5 Cookies
- Session cookies that encode a user or role ID
- Non-session cookies: `account_id=1234`, `org=acme`

### 1.6 GraphQL
```graphql
query { user(id: "1234") { email phone address } }
mutation { deletePost(id: "99") { success } }
```

### 1.7 WebSocket Messages
```json
{ "action": "subscribe", "channel": "user_1234_notifications" }
```

### 1.8 Hidden / Non-Obvious References
- Base64-encoded IDs: decode first (`dXNlcl8xMjM0` → `user_1234`)
- JWT claims: `sub`, `user_id`, `org_id` inside the payload
- Hashed IDs: note the hash type, check if predictable
- File names in upload/download flows: `/uploads/user_1234/avatar.png`

**Output of Phase 1:** a table of all discovered references, their location, and their apparent type (numeric ID, UUID, slug, etc.).

---

## Phase 2 — Set Up Test Accounts

IDOR requires at least two distinct principals to confirm unauthorized access.

| Scenario | Accounts needed |
|---|---|
| Horizontal privilege escalation | 2 accounts with the same role (Victim A, Attacker B) |
| Vertical privilege escalation | 1 low-privilege + 1 high-privilege account |
| Unauthenticated access | 1 account + unauthenticated session |
| Multi-tenant | 1 account per tenant |

Capture **separate session tokens** for each account before testing.

---

## Phase 3 — Systematic Testing

For each object reference found in Phase 1, run the following tests. Use the **Attacker's session** to access the **Victim's object**.

### 3.1 Horizontal IDOR (Same role, different user)
1. Log in as Victim → capture the object reference (e.g., `user_id=1234`)
2. Log in as Attacker → replace their own ID with Victim's ID
3. Check: does the response return Victim's data? Can Attacker modify/delete it?

### 3.2 Vertical IDOR (Low privilege → High privilege)
1. Identify admin/privileged endpoints (look for `/admin/`, `/manage/`, `/internal/`)
2. Use low-privilege session to call them
3. Also: swap a low-privilege object ID into a high-privilege endpoint

### 3.3 Unauthenticated Access
1. Remove auth headers/cookies entirely
2. Replay the request — does the server still respond with data?

### 3.4 State-Change Operations (highest impact)
Always test IDOR on write operations — these are critical findings:
- `PUT /users/1234` — update another user's profile
- `DELETE /posts/99` — delete another user's content
- `POST /payments/1234/refund` — trigger financial operations on another account
- `POST /admin/users/1234/promote` — privilege escalation

### 3.5 Second-Order IDOR
The reference isn't in the request but is resolved server-side:
- Upload a file → server stores it with your user ID internally
- A download or share link later resolves to someone else's object
- Test: modify the share token or download ID

---

## Phase 4 — Bypass Techniques

If a naive ID swap is blocked, try these before giving up:

### 4.1 ID Manipulation
| Technique | Example |
|---|---|
| Integer increment/decrement | `1234` → `1233`, `1235` |
| Negative values | `user_id=-1` |
| Zero | `user_id=0` |
| Array wrapping | `user_id[]=1234` |
| JSON type confusion | `"user_id": "1234"` vs `"user_id": 1234` |
| Large/overflow value | `user_id=999999999` |

### 4.2 Encoding Bypasses
- URL encode: `1234` → `%31%32%33%34`
- Double URL encode
- Base64 encode the ID
- Unicode normalization

### 4.3 HTTP Method Manipulation
Try alternate HTTP methods on the same endpoint:
```
GET    /api/users/1234   → 403
POST   /api/users/1234   → 200?
HEAD   /api/users/1234   → leaks via response headers?
OPTIONS /api/users/1234  → reveals allowed methods
```

### 4.4 Parameter Pollution
```
GET /api/orders?id=YOUR_ID&id=VICTIM_ID
POST body: user_id=YOUR_ID&user_id=VICTIM_ID
```

### 4.5 Path Traversal Hybrid
```
GET /api/users/YOUR_ID/../VICTIM_ID/profile
GET /api/users/YOUR_ID/../../admin/list
```

### 4.6 Version / Endpoint Switching
If `v2` is protected, try `v1`:
```
/api/v2/users/1234  → 403
/api/v1/users/1234  → 200 ✓
/api/users/1234     → 200 ✓
```

### 4.7 Content-Type Switching
Server may parse differently:
```
Content-Type: application/json    → { "user_id": 1234 }
Content-Type: application/x-www-form-urlencoded → user_id=1234
Content-Type: text/xml            → <user_id>1234</user_id>
```

---

## Phase 5 — Confirm the Finding

A true IDOR requires **evidence** that unauthorized data was accessed or modified. Don't report without confirmation.

**Confirmation checklist:**
- [ ] Response contains data belonging to Victim (name, email, PII, etc.)
- [ ] The request used Attacker's valid session (not Victim's)
- [ ] The behavior is reproducible
- [ ] The object ID was the only thing changed between a passing and failing request

**Avoid false positives:**
- 200 response ≠ IDOR (some apps return 200 with empty/generic data)
- Compare response body between "own object" and "victim object" — are they actually different?

---

## Phase 6 — Report Structure

When reporting an IDOR finding, include:

```
Title: IDOR on [endpoint] allows [horizontal/vertical] privilege escalation

Severity: [Critical / High / Medium based on data sensitivity and impact]

Affected endpoint: [METHOD] [URL]

Steps to reproduce:
1. Log in as Account A (victim). Note [object reference] = [value].
2. Log in as Account B (attacker).
3. Send: [exact HTTP request with attacker session + victim ID]
4. Observe: [what data was returned / action performed]

Impact:
- [What data is exposed or what action can be performed]
- [Number of affected users / scope]

Evidence:
- Request: [redacted HTTP request]
- Response: [relevant snippet showing victim's data]

Remediation:
- Validate that the authenticated user owns or has permission for every object reference server-side
- Never rely on client-supplied IDs alone; always verify against the session's identity
- Implement object-level authorization checks at the service layer, not just routing
```

---

## Quick-Reference: Priority Testing Order

When time is limited, test in this order (highest-impact first):

1. **Financial / payment endpoints** (transfers, refunds, invoices)
2. **PII endpoints** (profile, address, SSN, documents)
3. **State-change operations** (delete, update, promote)
4. **Admin / privileged endpoints** with low-privilege token
5. **File download / export endpoints**
6. **Read-only data endpoints** (lower priority but still valid)

---

## Reference Files

- `references/id-patterns.md` — Common ID formats and how to recognize/enumerate them
- `references/tools.md` — Recommended tools (Burp Suite extensions, ffuf, custom scripts)
