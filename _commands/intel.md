Look up vulnerability intelligence for this technology or target: $ARGUMENTS

Run all three lookups and summarize findings.

## 1. CVE Lookup (NVD)
Search https://nvd.nist.gov/vuln/search for the technology name and version.
Report: CVE ID, CVSS score, affected versions, patch version, brief description.
Flag any CVE with CVSS >= 7.0 as high priority.

## 2. GitHub Security Advisories
Search https://github.com/advisories for the technology or package name.
Report: GHSA ID, severity, affected versions, patched version.

## 3. HackerOne Hacktivity
Search https://hackerone.com/hacktivity for disclosed reports mentioning the technology.
Report: vulnerability class, bounty paid, a one-line description of what was exploited.

---

After all three lookups, produce:

**Confirmed vulnerabilities** — CVEs or advisories that apply to the exact version in scope. State if a PoC or exploit is publicly available.

**Attack surface** — Based on disclosed reports, what vuln classes are most common against this technology?

**Recommended tests** — Top 3 things to test first given the intelligence gathered.
