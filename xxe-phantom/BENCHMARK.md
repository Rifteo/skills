---
skill: xxe-phantom
tested-on: claude CLI
date: 2026-05-20
---

# Benchmark: xxe-phantom

> Real numbers. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Improvement |
|---|---|---|---|
| Turns to complete | 1 | 1 | **⚪ 0%** |
| Total tokens | ~4,138 | ~2,636 | **🟡 -36%** |
| Time | 90s | 57s | **🟡 -37%** |
| Output quality | Complete | Complete | |

---

## Scenario

```
Test for XXE on the SAML SSO endpoint at /saml/acs — it processes XML assertions and the app is running on a Java stack
```

---

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded. It improvised.

#### Turn 1

**Prompt**
> Test for XXE on the SAML SSO endpoint at /saml/acs — it processes XML assertions and the app is running on a Java stack

**Response**
```
## Phase 1: SCOPE

No program brief was provided, so I'll proceed with the standard constraint set for this engagement type and flag anything that needs explicit authorization.

**Allowed:** Test the `/saml/acs` endpoint for XXE via crafted SAML assertions — OOB exfiltration, file read, SSRF as impact. All payloads are single-request, non-destructive, and targeted at one endpoint.

**Not allowed (absent explicit authorization):** Automated scanning, DoS via recursive entity expansion (billion-laughs), exfiltrating files beyond proof (e.g., `/etc/passwd` first line only), pivoting to internal hosts beyond confirming SSRF reachability.

**Gate PASSED.** Scope is one endpoint, one vuln class, proof-only impact.

---

## Phase 2: RECON

Target is a known endpoint (`/saml/acs`) on a Java stack. Recon is scoped to understanding the SAML implementation surface.

**Surface mapping:**

| Signal | Finding |
|--------|---------|
| Endpoint | `POST /saml/acs` — SAML Assertion Consumer Service |
| 
... [truncated]
```

---

## With Skill — 1 turn, complete

The agent received the same prompt with `xxe-phantom` loaded as context.

#### Turn 1

**Prompt**
> Test for XXE on the SAML SSO endpoint at /saml/acs — it processes XML assertions and the app is running on a Java stack

**Response**
```
## XXE Testing — SAML ACS Endpoint (`/saml/acs`) on Java

---

### Phase 1 — Intercept and Decode the SAMLResponse

First, capture a legitimate SAMLResponse in Burp Suite, then decode it:

```bash
# Decode the base64 SAMLResponse from the POST body
echo "PHNhbWxwOlJlc3BvbnNlIHhtbG5z..." | base64 -d | xmllint --format -
```

The decoded XML will look roughly like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ...>
  <saml:Assertion ...>
    ...
  </saml:Assertion>
</samlp:Response>
```

---

### Phase 2 — Determine Signature Scope

Critical before injecting — Java SAML libs (OpenSAML, Spring Security SAML) sign either the `<Assertion>` element or the `<Response>` wrapper:

| Scenario | Where to inject |
|---|---|
| No signature validation | Anywhere in the XML |
| `<Assertion>` signed only | Inject in `<Response>` wrapper **outside** the assertion |
| En
... [truncated]
```

---

## What changed

Both runs completed in 1 turn. The skill ensured consistent structure and methodology coverage — without it, output quality depends on the agent improvising correctly every time.

With the skill, the agent followed a proven methodology from the first prompt.

---
