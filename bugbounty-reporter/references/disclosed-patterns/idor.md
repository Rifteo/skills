# IDOR — 26 Disclosed Reports

---

## High-Signal Targets

- Financial documents: invoices, orders, payment methods, receipts (Shopify, PayPal)
- Private repositories and source code (GitHub)
- User messages and DMs (Reddit)
- Account management endpoints (Mozilla)
- Multi-tenant org admin paths
- Content moderation logs

---

## Hunting Methodology

1. Map all object references in authenticated features, capture every ID parameter
2. Enumerate ID types: sequential integers, UUIDs, hashed values, base64
3. Create two accounts at identical privilege level
4. Replay resource IDs across user contexts using different session credentials
5. Test cross-tenant and cross-org scenarios explicitly
6. Target GraphQL endpoints with introspection and ID substitution
7. Test destructive operations (DELETE, PATCH, PUT), not just GET
8. Chain multiple IDORs using leaked IDs to escalate impact
9. Test state-changing edge cases: expired tokens, archived resources
10. Document precise access differential with screenshots

---

## Paid Patterns

**Integer ID increment:**
```
GET /api/v1/invoices/1234 → own invoice
GET /api/v1/invoices/1235 → another user's invoice with full PII
```

**UUID enumeration:**
```
# UUID leaked in one endpoint, used to access another
GET /api/users/me → { "id": "550e8400-e29b-41d4-a716-446655440000" }
GET /api/admin/users/550e8400-e29b-41d4-a716-446655440000 → full admin view
```

**Verb inconsistency:**
```
GET  /api/v1/users/1235/profile  → 403 Forbidden
PUT  /api/v1/users/1235/profile  → 200 OK (updates victim profile)
DELETE /api/v1/users/1235        → 200 OK (deletes victim account)
```

**Nested object IDOR:**
```
GET /api/org/1234/members → own org members
GET /api/org/1235/members → another org's full member list
```

**Parameter pollution:**
```
GET /api/profile?user_id=own_id&user_id=victim_id
# Server takes last value, returns victim's data
```

**GraphQL IDOR:**
```graphql
{
  user(id: "victim-uuid") {
    email
    privateMessages { content }
    paymentMethods { cardNumber }
  }
}
```

---

## Root Causes

- Authorization at route level only, per-object ownership check missing in ORM query
- Client-supplied IDs accepted without verification against session
- Multi-tenant isolation: per-user controls implemented, org-level boundaries omitted
- GraphQL resolvers lacking field-level authorization
- HTTP verb inconsistency: GET protected, write operations not

---

## Real-World Scenarios (affected platforms)

- **Shopify, PayPal**: financial/billing object exposure
- **GitHub**: private repository source code access
- **Reddit**: private message threads and mod logs
- **Mozilla**: account management endpoint privilege escalation

---

## Pre-Submission Validation Gate

1. What can the attacker access or modify right now? Map to CIA triad.
2. Is the impact meaningful? (PII, financial data, source code, private communications)
3. Reproducible using fresh accounts within 10 minutes? If not, do not file.
