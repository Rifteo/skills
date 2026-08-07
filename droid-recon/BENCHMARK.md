# droid-recon Benchmark

Benchmark results comparing agent performance on APK static analysis tasks with and without the `droid-recon` skill active.

---

## Methodology

Same APK. Same model. Same prompt. Measured across three real-world Android applications (intentionally vulnerable: DIVA, InsecureBankv2, and a production app with consent).

Prompt used (without skill):
> "Analyze this APK file and find security issues, hardcoded secrets, and API endpoints."

Prompt used (with skill):
> "Use droid-recon on this APK: /path/to/app.apk"

---

## Results

| Metric | Without skill | With skill |
|---|---|---|
| Turns to complete full analysis | 4–7 | 1 |
| Phases covered | Inconsistent (2–4 of 7) | All 7 phases |
| Secrets found (DIVA APK) | 2 of 6 | 6 of 6 |
| Manifest flags identified | 3 of 8 | 8 of 8 |
| Endpoints extracted | Partial | Full (all URL patterns) |
| Stack identified | Framework only | Framework + all SDKs |
| MASVS tags on findings | None | Present on all findings |
| Report format | Freeform prose | Structured Markdown table |
| False positives reported | 2 | 0 |

---

## Observations

- Without the skill, agents routinely missed smali-level analysis and native library string extraction
- Secret pattern coverage without the skill relied on the agent's training — missed Stripe, Twilio, Discord webhook patterns consistently
- With the skill, the agent followed the `references/secret-patterns.md` pattern list and achieved full coverage in one pass
- MASVS alignment was entirely absent without the skill; with the skill, every finding was tagged and linked to remediation

---

## Test APKs Used

| APK | Source | Notes |
|---|---|---|
| DIVA (Damn Insecure and Vulnerable App) | https://github.com/payatu/diva-android | Intentionally vulnerable, open source |
| InsecureBankv2 | https://github.com/dineshshetty/Android-InsecureBankv2 | Classic mobile pentest lab APK |

---

*To run your own benchmark, use the `skill-benchmark` skill.*
