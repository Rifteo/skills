# Cache Poisoning

---

## High-Signal Targets

- CDN-served assets (poisoning affects all visitors simultaneously)
- Authentication and login endpoints (account takeover at scale)
- Multi-tenant SaaS platforms (cross-tenant cache pollution)
- E-commerce affiliate and checkout flows

---

## Hunting Methodology

1. Identify caching infrastructure by analyzing response headers: `Age`, `X-Cache`, `CF-Cache-Status`, `Surrogate-Control`
2. Determine cache key components by varying headers individually to find unkeyed inputs
3. Test unkeyed header reflection: check if attacker-controlled headers appear in responses
4. Test web cache deception: append fake file extensions to dynamic endpoints
5. Validate poisoning by confirming a separate client from a different IP receives the malicious response

**Caching headers to look for:**
```
Age: 42
X-Cache: HIT
CF-Cache-Status: HIT
X-Varnish: 12345 67890
Via: 1.1 varnish
Surrogate-Control: max-age=3600
```

---

## Paid Patterns

**Unkeyed header reflection:**
```http
GET /page HTTP/1.1
Host: target.com
X-Forwarded-Host: attacker.com

# If response reflects attacker.com in a URL (script src, form action, link href)
# and the response gets cached → cache poisoning
```

**Web cache deception:**
```
# Authenticated endpoint with user data
GET /account/profile

# Append fake static extension to trick CDN into caching
GET /account/profile.css
GET /account/profile.js
GET /account/profile.png

# CDN caches response thinking it is a static asset
# Victim visits crafted URL → attacker fetches same URL and receives victim's cached data
```

**Cache poisoning via HTTP request smuggling:**
```
# Smuggle a request that poisons the cache for all subsequent visitors
# The smuggled request's malicious response gets stored in CDN cache
# Every visitor to the page receives the attacker's poisoned response
```

**Parameter cloaking:**
```
# Cache key ignores query string, but backend processes it
GET /search?q=innocent&q=<script>alert(1)</script>
# Cache key: /search?q=innocent
# Backend receives both values, reflects the XSS
# Cached response contains XSS for all users hitting /search?q=innocent
```

---

## Root Causes

- `X-Forwarded-Host` unkeyed in cache but used in URL generation in response
- CDN caching rules based on file extension, not Content-Type or authentication state
- Overly broad TTL rules caching authenticated responses
- Query string excluded from cache key while reflected in response

---

## Critical Validation Requirement

The attacker must poison a cache entry and then demonstrate that a **separate, unauthenticated request from a different client/IP** receives the poisoned response. Self-caching does not qualify as exploitable cache poisoning.

**Validation steps:**
1. Send poisoning request from IP A
2. Confirm poisoning via response
3. Send clean request from IP B (or use Burp Collaborator)
4. Confirm IP B receives the poisoned cached response

---

## Pre-Submission Validation Gate

1. Did a separate client/IP receive the poisoned response?
2. What is the concrete impact? (XSS execution, credential harvesting, data exposure)
3. What is the blast radius? (single user, all users, specific tenant)
