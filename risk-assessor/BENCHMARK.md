---
skill: risk-assessor
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: risk-assessor
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Incomplete | Complete | 🟢 +3 level(s) |
| Turns to complete | 2 | 1 | 🟢 -1 turn(s) |
| Response tokens | ~4,629 | ~2,009 | 🟢 -57% |
| Total time | 101s | 68s | 🟢 -32% |
| User effort | Medium | Low | 🟢 Low |

## Scenario

Security engineer asks if a critical CVE needs emergency patching, management context needed

## Without Skill — 2 turns required

The agent received the prompt with no skill loaded. The first response was incomplete — it took 2 rounds of prompting to reach a usable result.

### Turn 1

**Prompt**

we have CVE-2023-50164 on our apache struts 2.5.30 in prod. official CVSS 9.8, metasploit module available. public server, no auth required to exploit, it processes PCI customer data (names, emails, credit cards). we have cloudflare WAF but no specific rule for this CVE. patch is available but our release cycle is in 2 weeks. what's the real risk and does it justify an emergency patch?

**Response**

# CVE-2023-50164 Complete Risk Assessment

## Vulnerability Summary

| Field | Detail |
|-------|--------|
| CVE | CVE-2023-50164 |
| Component | Apache Struts 2.5.30 |
| Vulnerability Type | File upload path traversal → RCE |
| CVSS Base Score | 9.8 Critical |
| Exploit Availability | Public Metasploit module |
| Auth Required | None |
| User Interaction | None |
| Patch Available | Yes |

---

## Likelihood Assessment

### Threat Actor Accessibility

| Factor | Assessment | Rationale |
|--------|------------|-----------|
| Exploit complexity | **Very Low** | Metasploit module reduces exploitation to point-and-click |
| Attacker skill required | **Script-kiddie level** | No bespoke exploit development needed |
| Attack vector | **Network (internet)** | Public-facing server, no network restrictions |
| Authentication barrier | **None** | Zero friction for attacker |
| Time since public disclosure | **High risk window** | Automated scanning begins within hours of Metasploit module release |

### Active Exploitation Context

This CVE is **actively exploited in the wild**. Relevant threat intelligence:

- Automated scanners (Shodan-driven bots, opportunistic crawlers) actively probe for Struts vulnerabilities continuously
- Nation-state and ransomware groups specifically target PCI-in-scope infrastructure
- Time-to-exploitation for Metasploit-available CVEs is measured in **hours to days**, not weeks
- Apache Struts has a well-documented history of rapid mass exploitation (Equifax breach was also a Struts CVE)

### WAF Effectiveness Adjustment

Cloudflare without a specific CVE-2023-50164 rule does **not** meaningfully reduce likelihood:

```
Generic WAF protection against this CVE:
- Known signatures:        Maybe blocked
- Encoded payload variants: Likely not blocked  
- Attacker WAF testing:    Trivially bypassed with iteration
- Post-exploitation traffic: Not blocked

Effective likelihood reduction from untuned WAF: Low
```

### Likelihood Rating

```
Likelihood Sc

*[truncated]*

*Missing sections triggered 1 follow-up prompt(s) before the agent produced a complete result.*

## With Skill — 1 turn, complete

Same prompt, with `risk-assessor` loaded as system context.

### Turn 1

**Prompt**

we have CVE-2023-50164 on our apache struts 2.5.30 in prod. official CVSS 9.8, metasploit module available. public server, no auth required to exploit, it processes PCI customer data (names, emails, credit cards). we have cloudflare WAF but no specific rule for this CVE. patch is available but our release cycle is in 2 weeks. what's the real risk and does it justify an emergency patch?

**Response**

**Vulnerability:** Apache Struts 2 File Upload Parameter Manipulation leading to Remote Code Execution (CVE-2023-50164) — affecting Struts 2.5.30 in production

**Attack Surface:** Internet-facing application server, no authentication required to trigger the file upload endpoint, public IP, Cloudflare WAF in place but no CVE-specific rule configured

---

**Likelihood:** High — Score: 3
- Attack vector: Network (internet-facing)
- Exploit availability: Weaponized — Metasploit module is publicly available; mass scanning campaigns for this CVE were observed within days of disclosure
- Authentication required: None
- Key modifier applied: "Actively exploited in the wild" override — CISA KEV listed CVE-2023-50164; Metasploit module lowers attacker skill bar to near-zero
- Justification: Any threat actor with Metasploit and an internet connection can attempt exploitation against your endpoint today. The skill requirement is effectively eliminated by the weaponized module. Likelihood is locked at 3 regardless of other factors.

**Impact:** High — Score: 3
- Confidentiality: High (3) — PCI cardholder data (names, emails, credit card numbers) confirmed in scope; full server compromise would expose all data the application can access
- Integrity: High (3) — Successful exploitation delivers RCE; attacker can modify application code, inject malicious logic into the payment flow, or tamper with transaction data
- Availability: High (3) — RCE enables full service shutdown, data destruction, or ransomware deployment
- Scope: **Changed** — RCE on the app server creates a pivot point into internal network segments, databases, and adjacent PCI-scoped systems; +0.5 applied
- Dominant axis: All three at maximum; C governs due to PCI data but I is equally severe given RCE
- Justification: RCE with no authentication on a system processing live credit card data is a worst-case impact scenario. All three CIA axes are at their ceiling. Scope change is near-certain given typical DMZ → DB tr

*[truncated]*

## What changed

Without the skill, the first response was **Incomplete** — the agent needed **2 turns** and follow-up prompts to fill the gaps. With the skill, the agent delivered a **Complete** answer in **1 turn**.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
