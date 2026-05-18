# Attack Surface Priority Matrix

Use this to rank which components to test first when time is limited.

## Scoring Factors

Assign each component a score of 1-3 for each factor, then sum.

| Factor | 1 — Low priority | 2 — Medium | 3 — High priority |
|---|---|---|---|
| **Exposure** | Internal only | Authenticated users | Unauthenticated / public |
| **Data sensitivity** | Non-sensitive | Business data | PII / financial / credentials |
| **Auth controls** | Strong MFA + authz | Basic auth | None / weak |
| **Historical issues** | No known issues | Minor past findings | Critical past findings |
| **Tech age** | Modern, patched | Mixed | Legacy / end-of-life |
| **Business criticality** | Low-value feature | Standard feature | Core business function |

## Priority Tiers

| Total Score | Priority | Action |
|---|---|---|
| 15–18 | Critical — test first | Immediately |
| 10–14 | High | Early in engagement |
| 6–9 | Medium | Mid-engagement |
| 3–5 | Low | If time allows |

## Quick-Scan High-Value Targets

These always score high regardless of matrix:

- **Login / authentication endpoints** — highest-impact vulnerabilities live here
- **Password reset flows** — consistently overlooked, consistently broken
- **File upload / download** — path traversal, stored XSS, malware upload
- **Admin panels** — especially if internet-facing
- **API endpoints returning collections** — IDOR, mass assignment, over-fetching
- **Payment / billing flows** — business logic, price manipulation
- **OAuth / SSO integrations** — state parameter issues, redirect bypass
- **Export / report functions** — SSRF, injection, data leakage
