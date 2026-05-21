# Engagement Phases — Capability Matrix

Each phase defines the goal and the capability needed. Query available HexStrike tools via `server_health`, match the capability keyword to a tool description, and use it. Prefer tools with structured output (JSON/XML) over plain text when multiple options exist.

If no tool matches a capability, note the gap and skip that phase — do not improvise with an unrelated tool.

---

## Web Application

| Phase | Goal | Capability needed |
|---|---|---|
| 1. Passive recon | Enumerate subdomains | Subdomain enumerator / DNS brute-forcer |
| 1. Passive recon | Historical URLs and known endpoints | Historical URL enumeration |
| 1. Passive recon | Crawl live pages and extract links | Web crawler / spider |
| 2. Fingerprint | Identify technologies, frameworks, server versions | Technology detection / HTTP probe |
| 2. Fingerprint | Check TLS version and cipher strength on HTTPS | TLS / SSL scanner |
| 2. Fingerprint | Discover hidden directories and files | Directory / path brute-forcer |
| 3. Vuln scan | Detect CVEs, misconfigurations, exposed panels | CVE scanner with web templates |
| 3. Vuln scan | Find web server misconfigurations | Web server scanner |
| 3. Vuln scan | Test for SQL injection on input parameters | SQL injection scanner |
| 3. Vuln scan | Test reflected and stored XSS on parameters | XSS scanner / fuzzer |
| 3. Vuln scan | Check for CORS misconfiguration | HTTP probe with CORS origin test |
| 3. Vuln scan | Test Host header injection and routing bypass | HTTP probe with header manipulation |
| 3. Vuln scan | Check for open redirect on redirect parameters | Open redirect tester |
| 4. Authenticated | Repeat vuln scan with session injected | Same as phase 3 with auth header |
| 4. Authenticated | Test for IDOR on object references in authenticated requests | HTTP probe with ID enumeration |
| 4. Authenticated | Test for privilege escalation between roles | HTTP probe with role comparison |

---

## API

| Phase | Goal | Capability needed |
|---|---|---|
| 1. Passive recon | Discover historical API endpoints | Historical URL enumeration |
| 1. Passive recon | Extract endpoints from JavaScript bundles | JavaScript crawler / static analyzer |
| 1. Passive recon | Detect GraphQL endpoint and run introspection | GraphQL introspection scanner |
| 2. Fingerprint | Probe HTTP methods and status codes per endpoint | HTTP probe with method enumeration |
| 2. Discovery | Discover hidden parameters on endpoints | Parameter discovery / fuzzer |
| 2. Discovery | Enumerate undiscovered endpoints via wordlist | Directory / endpoint fuzzer |
| 3. Vuln scan | Detect API-specific CVEs and misconfigs | CVE scanner with API templates |
| 3. Vuln scan | Test for unauthenticated access to protected endpoints | HTTP probe without auth headers |
| 3. Vuln scan | Test for JWT algorithm confusion and signature bypass | JWT analyzer |
| 3. Vuln scan | Test for mass assignment on POST/PUT requests | HTTP probe with extra field injection |
| 3. Vuln scan | Test rate limiting on sensitive endpoints | Rate limit tester / HTTP flood probe |
| 4. Authenticated | Test IDOR by enumerating IDs with auth token | HTTP probe with ID enumeration |
| 4. Authenticated | Test for BOLA — access another user's resources | HTTP probe with cross-account token |
| 4. Authenticated | Test for broken function-level authorization | HTTP probe with lower-privilege token |

---

## Network / Infrastructure

| Phase | Goal | Capability needed |
|---|---|---|
| 1. Discovery | Identify open TCP ports and running services | Port scanner with service detection |
| 1. Discovery | Scan common UDP ports (DNS 53, SNMP 161, NTP 123) | UDP port scanner |
| 2. Fingerprint | Confirm service versions via banner grabbing | Banner grabber / service prober |
| 2. TLS check | Detect weak TLS versions and cipher suites on any HTTPS service | TLS / SSL scanner |
| 2. Service check | Enumerate SNMP community strings | SNMP scanner |
| 2. Service check | CVEs for detected services | CVE scanner with network templates |
| 2. Service check | Test default credentials on exposed services | Default credential checker |
| 2. Service check | Check for anonymous access on FTP, SMB, LDAP | Anonymous access prober |
| 3. Vuln scan | Full CVE and exposure check across all open ports | CVE scanner with full template set |
| 3. Vuln scan | Check for unpatched RCE CVEs on detected service versions | CVE scanner with RCE filter |
| 4. Authenticated | Service-specific authenticated enumeration | Service-native capability (SSH, SMB, RDP) |
| 4. Authenticated | Check for lateral movement paths from compromised host | Internal network mapper |

---

## Cloud

| Phase | Goal | Capability needed |
|---|---|---|
| 1. Discovery | Enumerate subdomains and cloud-hosted assets | Subdomain enumerator |
| 1. Discovery | Check for subdomain takeover on dangling DNS records | Subdomain takeover scanner |
| 1. Discovery | Probe discovered assets for live services | HTTP probe |
| 2. Storage check | Detect publicly accessible cloud storage buckets | Cloud storage scanner (S3, GCS, Azure Blob) |
| 2. Metadata check | Check for exposed instance metadata endpoint | HTTP probe on metadata IPs (169.254.169.254, etc.) |
| 2. Secrets check | Find hardcoded credentials in HTTP responses and JS | Token / secret scanner |
| 2. Secrets check | Search organization's public GitHub repos for leaked secrets | Public repo secret scanner |
| 2. Serverless | Enumerate exposed serverless functions or Lambda URLs | HTTP probe with function endpoint wordlist |
| 3. Vuln scan | CVEs for cloud services in use | CVE scanner with cloud templates |
| 3. Vuln scan | Detect misconfigured container registries | Container registry prober |
| 4. Authenticated | IAM permission audit and privilege escalation paths | Cloud IAM auditor |
| 4. Authenticated | Enumerate resources accessible with current credentials | Cloud resource enumerator |

---

## Mobile / Thick Client

| Phase | Goal | Capability needed |
|---|---|---|
| 1. Recon | Identify backend API endpoints from app traffic or bundle | HTTP proxy / traffic analyzer |
| 1. Recon | Extract hardcoded URLs, keys, secrets from app binary | Static binary analyzer |
| 2. Fingerprint | Probe identified API endpoints for live services | HTTP probe |
| 2. Fingerprint | Check certificate pinning bypass feasibility | TLS probe with custom cert |
| 3. Vuln scan | Run API vuln scan against discovered backend endpoints | CVE scanner with API templates |
| 3. Vuln scan | Test authentication endpoints for bypass | HTTP probe without auth / with tampered tokens |
| 3. Vuln scan | Check for sensitive data in responses (PII, tokens, keys) | HTTP probe with response content analysis |
| 4. Authenticated | Test IDOR and BOLA on backend API with app-issued token | HTTP probe with ID enumeration |
| 4. Authenticated | Test for privilege escalation between user roles | HTTP probe with role comparison |

---

## Phase Sequencing Rules

1. Always complete passive recon before active scanning
2. Always complete unauthenticated phases before authenticated phases
3. Triage after each capability phase before moving to the next
4. If `server_health` returns no tool matching a capability, note the gap and skip — do not improvise
5. For multi-target engagements, complete phase 1 across all targets before starting phase 2
