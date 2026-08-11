# ad-recon Benchmark

Benchmark results comparing agent performance on Active Directory enumeration tasks with and without the `ad-recon` skill active.

---

## Methodology

Same lab domain. Same model. Same prompt. Measured on a GOAD (Game of Active Directory) lab instance with one Kerberoastable service account, one GenericAll ACL misconfiguration, one AS-REP roastable account, and an ESC1-vulnerable AD CS template intentionally seeded.

Prompt used (without skill):
> "I have credentials for this Active Directory domain (user:pass@dc-ip). Find a path to Domain Admin."

Prompt used (with skill):
> "Use ad-recon on this domain: user:pass@dc-ip"

---

## Results

| Metric | Without skill | With skill |
|---|---|---|
| Turns to complete full analysis | 5-9 | 1 |
| Phases covered | Inconsistent (2-5 of 8) | All 8 phases |
| Seeded escalation paths found (of 4) | 1-2 of 4 | 4 of 4 |
| BloodHound collection performed | Sometimes skipped | Always run |
| AD CS enumeration performed | Rarely | Always run |
| ATT&CK tags on findings | None | Present on all findings |
| Report format | Freeform prose | Structured Markdown table |
| False positives reported | 1 | 0 |

---

## Observations

- Without the skill, agents frequently jumped straight to Kerberoasting/password spraying and skipped ACL and AD CS enumeration entirely: missing the GenericAll and ESC1 paths in this lab
- BloodHound collection was inconsistently performed without the skill; some runs relied only on manual LDAP queries and missed the graph-based shortest path to Domain Admin
- AD CS (ESC1-ESC8) enumeration was almost never run without the skill: agents defaulted to Kerberos/ACL attacks only
- With the skill, the agent followed all 8 phases and cross-referenced BloodHound output against `references/ad-attack-patterns.md`, achieving full path coverage in one pass
- ATT&CK mapping was entirely absent without the skill; with the skill, every finding was tagged to a specific technique ID and tactic

---

## Test Environment Used

| Lab | Source | Notes |
|---|---|---|
| GOAD (Game of Active Directory) | https://github.com/Orange-Cyberdefense/GOAD | Multi-domain, intentionally vulnerable AD lab |
| HackTheBox / offline AD labs | N/A | Used for spot-checking individual attack primitives |

---

## Real-World Validation Notes

**Password pattern hypothesis:** Before full password spray, test organization-specific patterns on DA/admin accounts. Pattern: `OrgName@YearFounded` (e.g., test years 2000-2015). Single well-guessed password is faster than spray and avoids lockout.

**GenericAll on protected groups:** When discovered on Domain Admins, Enterprise Admins, or similar protected objects, exploit via LDAP group member modification (Phase 4.2). Remote ACL tools may miss these due to caching/filtering: always cross-verify with DC console `Get-Acl` on real engagements.

**Attack chain validation:** Kerberoastable service account → GenericAll on privileged group → LDAP group membership modification → member becomes DA → DCSync entire NTDS. Full domain compromise in 4 steps.

---

*To run your own benchmark, use the `skill-benchmark` skill.*
