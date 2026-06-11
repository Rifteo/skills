---
name: find-skills
description: Helps users discover and install AuditGuard agent skills when they ask questions like "is there a skill for X", "how do I write a finding", "find a skill that can...", or want to extend their agent for security and audit work.
---

# Find AuditGuard Skills

When the user is looking for functionality that might exist as an installable AuditGuard skill, help them discover and install it.

## Available Skills

| Skill | What it does | Install |
|---|---|---|
| `attack-surface` | Maps every entry point, component, and trust boundary of a target before testing begins — prevents missed coverage and prioritizes the highest-value attack paths | `auditguard-skills add attack-surface` |
| `bugbounty-reporter` | Converts raw bug bounty findings into a complete, triage-ready report with clear description, numbered reproduction steps, self-contained PoC, risk, and remediation. Writes for triagers who are not necessarily security experts. Covers all vuln classes and major platforms (HackerOne, Bugcrowd, Intigriti, YesWeHack). | `auditguard-skills add bugbounty-reporter` |
| `caveman` | Ultra-compressed response mode for cybersecurity contexts — strips filler while keeping CVEs, payloads, CVSS scores, and findings exact. User-triggered only (/caveman, "caveman mode", "be brief", "in short", "tl;dr", "straight to the point", "just the findings"). | `auditguard-skills add caveman` |
| `check-exploit` | Searches known exploit databases and sources for a given service, version, or CVE — from searchsploit to Vulners, MSF, and beyond | `auditguard-skills add check-exploit` |
| `clickjacking-hunter` | Complete clickjacking (UI redressing) methodology — framing protection detection, single-click and multi-step PoC construction, JS frame-busting bypass, drag-and-drop and OAuth consent variants, and report structure. | `auditguard-skills add clickjacking-hunter` |
| `compliance-gap-analyzer` | Aggregates audit findings mapped to framework controls, classifies each control as compliant / partially compliant / non-compliant / not tested, identifies blind spots, prioritizes gaps by severity, and produces a complete self-contained gap report — supports ISO 27001, NIST CSF, PCI-DSS, and OWASP (Top 10 / ASVS) | `auditguard-skills add compliance-gap-analyzer` |
| `control-lookup` | Looks up any control ID across ISO 27001, NIST CSF, PCI-DSS v4, and OWASP (Top 10 / ASVS) — returns the full control card, cross-framework mappings with confidence level, related controls, and testing hints | `auditguard-skills add control-lookup` |
| `ctf-writeup` | Generates a clean, publishable CTF challenge writeup from solve notes — suitable for HTB, CTFtime, personal blogs, and team wikis | `auditguard-skills add ctf-writeup` |
| `cvss-scorer` | Computes an exact CVSS v3.1 base score and vector from a vulnerability description. Infers metrics from context, picks the most accurate score when info is sufficient, and asks one short question only when the ambiguity would change the severity level. No noise, no tables, no formula dumps. | `auditguard-skills add cvss-scorer` |
| `deadangle` | A final accuracy check for security work — it re-tests a conclusion against the evidence and labels each part as confirmed, inferred, or assumed, so an unverified result never goes out as if it were proven. Use it right before delivering a finding, assigning a severity or confidence rating, claiming something is exploitable or confirmed, presenting a multi-step attack path, or summarizing what was tested. Match the effort to the stakes: a quick check for one small finding, a full pass for a report or attack chain. Also runs on request: "deadangle" or "/deadangle". | `auditguard-skills add deadangle` |
| `economist-attack` | Offensive strategy skill that prioritizes high-impact attack paths and avoids wasting effort on low-yield surfaces. | `auditguard-skills add economist-attack` |
| `engagement-handoff` | Documents the current state of an active pentest engagement so the next agent session can continue without losing context — findings, coverage, next steps, and open threads | `auditguard-skills add engagement-handoff` |
| `finding-writer` | Converts raw pentest notes, logs, or observations into a structured audit finding ready for a security report | `auditguard-skills add finding-writer` |
| `hexstrike-forge` | Full HexStrike engagement workflow — sequences the right tools for your target type, kills false positives, and forges confirmed findings into a professional report | `auditguard-skills add hexstrike-forge` |
| `hpp-hunter` | Complete HTTP Parameter Pollution methodology — server behavior fingerprinting, server-side and client-side HPP, WAF bypass via parameter splitting, OAuth/payment/access-control abuse, header and JSON body pollution, and report structure. | `auditguard-skills add hpp-hunter` |
| `idor-hunter` | Systematic IDOR/BOLA detection methodology — recon, multi-account testing, bypass techniques, and report structure | `auditguard-skills add idor-hunter` |
| `js-analyzer` | Full JavaScript analysis methodology for pentesting and bug bounty — JS file discovery, secret extraction, endpoint mapping, DOM XSS, prototype pollution, postMessage abuse, client-side logic flaws, source map extraction, and hardcoded credential hunting | `auditguard-skills add js-analyzer` |
| `jwt-cracker` | Full JWT attack methodology — alg:none, RS256 to HS256 confusion, weak secret brute-force, kid injection, jku/jwk injection, and claim tampering | `auditguard-skills add jwt-cracker` |
| `less-aggressive-attack` | Tests for vulnerabilities, but less aggressively — read-only where possible, confirming a flaw without exercising its full impact or causing damage, following a strict set of safety rules. Not the default. Use it whenever the user wants the testing to stay cautious and non-destructive, or when the target is sensitive enough that an aggressive action could do real harm — in any context, Do not use it when the user wants a full, aggressive test, or on isolated labs, sandboxes, and CTFs where destruction is expected. | `auditguard-skills add less-aggressive-attack` |
| `less-noise-attack` | Runs offensive security work in a low-noise mode — passive recon first, minimal footprint, and only deliberate, targeted active actions that blend with legitimate traffic, so the engagement stays below detection thresholds. Not the default. Use it whenever the user wants to stay undetected, or when the target is monitored enough that tripping a WAF, SOC, or anomaly detector could get the engagement flagged and blocked mid-operation — in any context. Do not use it when speed and coverage matter more than stealth, or on isolated labs, sandboxes, and CTFs where detection is not a concern. | `auditguard-skills add less-noise-attack` |
| `nuclei-template-writer` | Converts a vulnerability description or HTTP request/response pair into a ready-to-run Nuclei YAML template — handles auth strategies, matcher selection, OOB detection, and multi-step flows | `auditguard-skills add nuclei-template-writer` |
| `pentest-report` | Generates a complete, client-ready penetration test report from all findings in the current engagement — executive summary, risk table, technical findings, and recommendations | `auditguard-skills add pentest-report` |
| `redirect-forge` | Complete open redirect detection and exploitation methodology — parameter discovery, 30+ bypass techniques, OAuth token theft, SSRF chaining, CSP abuse, phishing escalation, and report structure | `auditguard-skills add redirect-forge` |
| `redmind` | Red team mindset that shifts the agent to offensive security thinking across any target or engagement type. | `auditguard-skills add redmind` |
| `remediation-planner` | Converts a security finding or vulnerability into a prioritized step-by-step remediation plan with effort estimates per step. | `auditguard-skills add remediation-planner` |
| `risk-assessor` | Scores a vulnerability using likelihood × impact, CIA triad, CVSS correlation, and SLA-bound remediation urgency | `auditguard-skills add risk-assessor` |
| `scope-grill` | Interviews the user about a pentest or audit engagement before any testing begins — captures target, scope, rules of engagement, auth, and deliverables into a structured brief | `auditguard-skills add scope-grill` |
| `skill-benchmark` | Scores any SKILL.md across 5 quality dimensions, runs a compatibility check against 50+ AI agents, and returns a ranked fix list — use when asked to benchmark, audit, or check cross-agent compatibility of a skill. | `auditguard-skills add skill-benchmark` |
| `ssrf-hunter` | Complete SSRF detection and exploitation methodology — injection point discovery, cloud metadata theft (AWS/GCP/Azure), internal network enumeration, protocol handler abuse, filter bypass techniques, blind SSRF via OOB, and report structure. | `auditguard-skills add ssrf-hunter` |
| `ssti-hunter` | Complete SSTI detection and exploitation methodology — engine fingerprinting, RCE payloads per engine (Jinja2, Twig, FreeMarker, Velocity, Mako, ERB, EJS, Pebble, Thymeleaf, Smarty, Pug, Handlebars, Nunjucks), sandbox escapes, blind detection, and report structure | `auditguard-skills add ssti-hunter` |
| `vuln-diagnose` | Builds a deterministic, reproducible proof-of-concept for a suspected vulnerability before writing a finding — eliminates false positives and produces airtight evidence | `auditguard-skills add vuln-diagnose` |
| `xss-hunter` | Complete XSS testing methodology — covers reflected, stored, DOM-based, blind, and mutation XSS, CSP bypass, DOM clobbering, filter/WAF evasion, and impact escalation | `auditguard-skills add xss-hunter` |
| `xxe-phantom` | Complete XXE (XML External Entity) detection and exploitation methodology — classic file read, blind OOB exfiltration, XInclude, SVG/DOCX/SAML vectors, WAF bypass, SSRF chaining, and report structure | `auditguard-skills add xxe-phantom` |

## How to Find a Skill

**List all available skills:**
```bash
auditguard-skills available
```

**List what's already installed:**
```bash
auditguard-skills list
```

**Install a skill globally (available in all projects):**
```bash
auditguard-skills add <skill-name> --global
```

**Install for a specific agent:**
```bash
auditguard-skills add <skill-name> --agent claude-code
```

## Matching User Needs to Skills

When the user asks about a task, suggest the right skill:

- Maps every entry point, component, and trust boundary of a target before testing begins — prevents missed coverage and prioritizes the highest-value attack paths → `attack-surface`
- Converts raw bug bounty findings into a complete, triage-ready report with clear description, numbered reproduction steps, self-contained PoC, risk, and remediation. Writes for triagers who are not necessarily security experts. Covers all vuln classes and major platforms (HackerOne, Bugcrowd, Intigriti, YesWeHack). → `bugbounty-reporter`
- Ultra-compressed response mode for cybersecurity contexts — strips filler while keeping CVEs, payloads, CVSS scores, and findings exact. User-triggered only (/caveman, "caveman mode", "be brief", "in short", "tl;dr", "straight to the point", "just the findings"). → `caveman`
- Searches known exploit databases and sources for a given service, version, or CVE — from searchsploit to Vulners, MSF, and beyond → `check-exploit`
- Complete clickjacking (UI redressing) methodology — framing protection detection, single-click and multi-step PoC construction, JS frame-busting bypass, drag-and-drop and OAuth consent variants, and report structure. → `clickjacking-hunter`
- Aggregates audit findings mapped to framework controls, classifies each control as compliant / partially compliant / non-compliant / not tested, identifies blind spots, prioritizes gaps by severity, and produces a complete self-contained gap report — supports ISO 27001, NIST CSF, PCI-DSS, and OWASP (Top 10 / ASVS) → `compliance-gap-analyzer`
- Looks up any control ID across ISO 27001, NIST CSF, PCI-DSS v4, and OWASP (Top 10 / ASVS) — returns the full control card, cross-framework mappings with confidence level, related controls, and testing hints → `control-lookup`
- Generates a clean, publishable CTF challenge writeup from solve notes — suitable for HTB, CTFtime, personal blogs, and team wikis → `ctf-writeup`
- Computes an exact CVSS v3.1 base score and vector from a vulnerability description. Infers metrics from context, picks the most accurate score when info is sufficient, and asks one short question only when the ambiguity would change the severity level. No noise, no tables, no formula dumps. → `cvss-scorer`
- A final accuracy check for security work — it re-tests a conclusion against the evidence and labels each part as confirmed, inferred, or assumed, so an unverified result never goes out as if it were proven. Use it right before delivering a finding, assigning a severity or confidence rating, claiming something is exploitable or confirmed, presenting a multi-step attack path, or summarizing what was tested. Match the effort to the stakes: a quick check for one small finding, a full pass for a report or attack chain. Also runs on request: "deadangle" or "/deadangle". → `deadangle`
- Offensive strategy skill that prioritizes high-impact attack paths and avoids wasting effort on low-yield surfaces. → `economist-attack`
- Documents the current state of an active pentest engagement so the next agent session can continue without losing context — findings, coverage, next steps, and open threads → `engagement-handoff`
- Converts raw pentest notes, logs, or observations into a structured audit finding ready for a security report → `finding-writer`
- Full HexStrike engagement workflow — sequences the right tools for your target type, kills false positives, and forges confirmed findings into a professional report → `hexstrike-forge`
- Complete HTTP Parameter Pollution methodology — server behavior fingerprinting, server-side and client-side HPP, WAF bypass via parameter splitting, OAuth/payment/access-control abuse, header and JSON body pollution, and report structure. → `hpp-hunter`
- Systematic IDOR/BOLA detection methodology — recon, multi-account testing, bypass techniques, and report structure → `idor-hunter`
- Full JavaScript analysis methodology for pentesting and bug bounty — JS file discovery, secret extraction, endpoint mapping, DOM XSS, prototype pollution, postMessage abuse, client-side logic flaws, source map extraction, and hardcoded credential hunting → `js-analyzer`
- Full JWT attack methodology — alg:none, RS256 to HS256 confusion, weak secret brute-force, kid injection, jku/jwk injection, and claim tampering → `jwt-cracker`
- Tests for vulnerabilities, but less aggressively — read-only where possible, confirming a flaw without exercising its full impact or causing damage, following a strict set of safety rules. Not the default. Use it whenever the user wants the testing to stay cautious and non-destructive, or when the target is sensitive enough that an aggressive action could do real harm — in any context, Do not use it when the user wants a full, aggressive test, or on isolated labs, sandboxes, and CTFs where destruction is expected. → `less-aggressive-attack`
- Runs offensive security work in a low-noise mode — passive recon first, minimal footprint, and only deliberate, targeted active actions that blend with legitimate traffic, so the engagement stays below detection thresholds. Not the default. Use it whenever the user wants to stay undetected, or when the target is monitored enough that tripping a WAF, SOC, or anomaly detector could get the engagement flagged and blocked mid-operation — in any context. Do not use it when speed and coverage matter more than stealth, or on isolated labs, sandboxes, and CTFs where detection is not a concern. → `less-noise-attack`
- Converts a vulnerability description or HTTP request/response pair into a ready-to-run Nuclei YAML template — handles auth strategies, matcher selection, OOB detection, and multi-step flows → `nuclei-template-writer`
- Generates a complete, client-ready penetration test report from all findings in the current engagement — executive summary, risk table, technical findings, and recommendations → `pentest-report`
- Complete open redirect detection and exploitation methodology — parameter discovery, 30+ bypass techniques, OAuth token theft, SSRF chaining, CSP abuse, phishing escalation, and report structure → `redirect-forge`
- Red team mindset that shifts the agent to offensive security thinking across any target or engagement type. → `redmind`
- Converts a security finding or vulnerability into a prioritized step-by-step remediation plan with effort estimates per step. → `remediation-planner`
- Scores a vulnerability using likelihood × impact, CIA triad, CVSS correlation, and SLA-bound remediation urgency → `risk-assessor`
- Interviews the user about a pentest or audit engagement before any testing begins — captures target, scope, rules of engagement, auth, and deliverables into a structured brief → `scope-grill`
- Scores any SKILL.md across 5 quality dimensions, runs a compatibility check against 50+ AI agents, and returns a ranked fix list — use when asked to benchmark, audit, or check cross-agent compatibility of a skill. → `skill-benchmark`
- Complete SSRF detection and exploitation methodology — injection point discovery, cloud metadata theft (AWS/GCP/Azure), internal network enumeration, protocol handler abuse, filter bypass techniques, blind SSRF via OOB, and report structure. → `ssrf-hunter`
- Complete SSTI detection and exploitation methodology — engine fingerprinting, RCE payloads per engine (Jinja2, Twig, FreeMarker, Velocity, Mako, ERB, EJS, Pebble, Thymeleaf, Smarty, Pug, Handlebars, Nunjucks), sandbox escapes, blind detection, and report structure → `ssti-hunter`
- Builds a deterministic, reproducible proof-of-concept for a suspected vulnerability before writing a finding — eliminates false positives and produces airtight evidence → `vuln-diagnose`
- Complete XSS testing methodology — covers reflected, stored, DOM-based, blind, and mutation XSS, CSP bypass, DOM clobbering, filter/WAF evasion, and impact escalation → `xss-hunter`
- Complete XXE (XML External Entity) detection and exploitation methodology — classic file read, blind OOB exfiltration, XInclude, SVG/DOCX/SAML vectors, WAF bypass, SSRF chaining, and report structure → `xxe-phantom`

## Rules

- Always show the install command so the user can act immediately
- If no skill matches, offer to help directly using your own capabilities
- If the user wants a skill that doesn't exist yet, point them to contribute at github.com/AuditGuard-Community/skills
