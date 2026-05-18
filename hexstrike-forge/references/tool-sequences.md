# HexStrike Tool Sequences

Ordered playbooks by target type. Run phases in order — do not skip ahead.

---

## Web Application

### Phase 1 — Passive Recon (no traffic to target)
- Subdomain enumeration (subfinder, amass, crt.sh)
- OSINT: DNS records, WHOIS, historical URLs (wayback/gau)
- Technology fingerprinting from public sources (Shodan, BuiltWith)
- Certificate transparency log analysis

**Output:** subdomains list, tech stack indicators, historical endpoints

### Phase 2 — Active Recon (traffic to target, no auth)
- Port scan + service detection on all discovered hosts
- HTTP fingerprinting: server headers, cookies, error pages, robots.txt, sitemap.xml
- Directory and file discovery (common paths, backup files, config files)
- JavaScript analysis: endpoints, API routes, secrets in source

**Output:** live hosts, open ports, endpoint map, tech stack confirmed

### Phase 3 — Unauthenticated Vulnerability Scan
- Nuclei templates: CVEs, misconfigurations, default credentials, exposed panels
- Header security analysis (CSP, HSTS, X-Frame-Options, CORS)
- SSL/TLS analysis (weak ciphers, expired cert, HSTS preload)
- Open redirect detection
- Information disclosure (stack traces, debug pages, .env, .git exposure)

**Output:** raw flags list — triage before Phase 4

### Phase 4 — Authenticated Testing (requires test accounts)
- Session management: token entropy, cookie flags, session fixation
- Access control: IDOR on all object references, horizontal + vertical privilege escalation
- Business logic: price manipulation, workflow bypass, race conditions
- Input validation: SQLi, XSS, SSTI, command injection on all user-controlled fields
- File upload: MIME bypass, path traversal, stored XSS via filename

**Output:** raw flags list — triage before Phase 5

### Phase 5 — Deep Exploitation (confirmed findings only)
- For each CONFIRMED finding: build minimal PoC demonstrating worst-case impact
- Chain findings where possible (e.g. XSS → session theft → account takeover)

---

## API (REST / GraphQL)

### Phase 1 — Discovery
- Enumerate all endpoints: Swagger/OpenAPI docs, JS source, path fuzzing
- GraphQL: introspection query, schema extraction
- Identify auth mechanism: Bearer, API key, OAuth, session cookie

### Phase 2 — Auth Testing
- JWT: algorithm confusion (none/RS256→HS256), weak secret brute-force, claim tampering
- API key: entropy check, scope testing, key rotation policy
- OAuth: state parameter, redirect_uri bypass, token leakage in referrer

### Phase 3 — Authorization Testing
- IDOR/BOLA on every object ID in every endpoint
- Mass assignment: send extra fields in POST/PUT bodies
- Privilege escalation: call admin endpoints with user token
- Rate limiting: auth endpoints, OTP, password reset

### Phase 4 — Injection
- SQLi on all filter/search/sort parameters
- NoSQL injection (MongoDB operators: `$where`, `$gt`, `$regex`)
- SSRF via URL parameters, webhook URLs, import endpoints
- XXE on any XML-accepting endpoint

---

## Network / Infrastructure

### Phase 1 — Discovery
- Full port scan (all 65535 ports) on in-scope IP ranges
- Service and version detection on open ports
- OS fingerprinting

### Phase 2 — Service Enumeration
- Per-service enumeration: SMB shares, FTP anonymous, SNMP community strings, LDAP base DN
- Default credential testing on management interfaces (SSH, RDP, Telnet, web UIs)
- Banner grabbing for version-based CVE matching

### Phase 3 — Vulnerability Identification
- CVE matching against detected versions
- Nuclei network templates
- Check CISA KEV for any matched CVEs (run `check-exploit` skill)

### Phase 4 — Exploitation
- Confirmed CVEs with public PoC only
- Check for lateral movement paths between in-scope hosts

---

## Cloud (AWS / GCP / Azure)

### Phase 1 — Passive Enumeration
- S3/GCS/Azure Blob: enumerate public buckets by naming convention
- Exposed credentials: GitHub dork, Shodan, leaked .env files
- Certificate transparency for cloud-hosted subdomains

### Phase 2 — Metadata & SSRF
- IMDS endpoint reachability (169.254.169.254, 169.254.170.2)
- SSRF to metadata from any discovered web app on cloud infrastructure

### Phase 3 — IAM & Permissions
- Enumerate IAM roles, policies, and attached permissions (if credentials available)
- Check for overly permissive roles (AdministratorAccess, *)
- Identify publicly accessible resources: snapshots, AMIs, functions

### Phase 4 — Service-Specific Testing
- Lambda/Cloud Functions: environment variable exposure, event injection
- RDS/database: public accessibility, default credentials
- API Gateway: authentication bypass, resource policy misconfigurations
