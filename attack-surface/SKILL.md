---
name: attack-surface
description: Maps every entry point, component, and trust boundary of a target before testing begins — preventing missed coverage and prioritizing the highest-value attack paths. Use at the start of an engagement, once scope is set, when you have a target and need to decide where to begin or what to test.
license: MIT
metadata:
  version: "1.0.0"
  author: Rifteo
  tags: ["pentest", "recon", "attack-surface", "mapping", "methodology"]
---

# Attack Surface Mapper

Before testing individual vulnerabilities, map the full attack surface. Untested components are unfound vulnerabilities. This skill produces a structured map that drives testing coverage.

## Process

### Phase 1 — Enumerate Entry Points

Systematically identify every place an attacker could interact with the target:

- **Web** — domains, subdomains, ports 80/443, login pages, API endpoints, file upload, search, export
- **APIs** — REST, GraphQL, SOAP, WebSocket, mobile API backends
- **Auth flows** — login, registration, password reset, OAuth/SSO, MFA bypass paths
- **Network** — open ports, admin interfaces (SSH, RDP, Telnet), VPNs, exposed management panels
- **Cloud** — S3 buckets, blob storage, exposed functions/lambdas, public AMIs, metadata endpoints
- **Third-party integrations** — webhooks, OAuth providers, embedded iframes, CDN-served content
- **Client-side** — JavaScript source, local storage, service workers, postMessage handlers

### Phase 2 — Identify Trust Boundaries

Mark where the system transitions between trust levels:
- Unauthenticated → authenticated
- User role → admin role
- External network → internal network
- Client-controlled input → server-side processing

### Phase 3 — Tech Stack Fingerprint

For each component, note:
- Language / framework
- Version (if visible)
- Authentication mechanism
- Known CVEs for the version (run `check-exploit` skill on identified versions)

### Phase 4 — Prioritize

Rank attack paths by value. See `references/priority-matrix.md`.

## Output Format

Produce a **Surface Map** table:

| Component | Type | Auth Required | Tech Stack | Priority | Notes |
|---|---|---|---|---|---|
| `/api/v2/users` | REST API | Bearer token | Node.js/Express | High | Returns PII |
| `admin.target.com` | Web app | Basic auth | Apache/PHP | Critical | Exposed to internet |

Follow with a **Recommended Testing Order** — ordered list of highest-value targets first.

## Rules

- Do not start testing until Phase 1 is complete — partial maps lead to missed coverage
- If the scope is large, timebox Phase 1 and note what was not mapped
- Reference `check-exploit` for every identified technology version
