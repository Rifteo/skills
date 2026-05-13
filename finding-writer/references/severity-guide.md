# Severity Rating Guide

Use this guide to assign consistent, defensible severity ratings. Base the score on the **worst realistic exploitation scenario** given the context provided.

## Severity Levels

### Critical
- Remote code execution with no authentication
- Full database dump accessible without credentials
- Authentication bypass on a production system
- Direct access to cloud credentials or secrets
- Supply chain compromise affecting downstream users

### High
- Authenticated RCE or SQLi
- Horizontal privilege escalation (accessing other users' data)
- Vertical privilege escalation (user → admin)
- Sensitive PII/financial data exposed to authenticated users who shouldn't have access
- Server-Side Request Forgery (SSRF) reaching internal services

### Medium
- Information disclosure that meaningfully aids further attacks (stack traces, internal paths, version banners)
- CSRF on sensitive actions (password change, account settings)
- Stored XSS on low-traffic or internal pages
- Insecure Direct Object Reference with limited impact
- Missing rate limiting on sensitive endpoints (login, OTP, password reset)

### Low
- Reflected XSS requiring significant user interaction
- Missing security headers (CSP, X-Frame-Options) with no direct exploitability
- Verbose error messages without sensitive data
- Weak TLS configuration (TLS 1.1 still accepted, weak ciphers)
- Cookie flags missing (HttpOnly, Secure) with limited exploitability

### Informational
- Best practice deviations with no direct security impact
- Outdated but unexploitable software versions
- Missing documentation or logging
- Observations that may warrant monitoring but pose no current risk

## Adjusting the Rating

Increase severity when:
- The target holds sensitive data (PII, payment, health records)
- The finding is easily scriptable or already has public PoC/exploit
- The affected system is internet-facing with no additional controls

Decrease severity when:
- Exploitation requires a highly privileged starting position unlikely to be reached
- Compensating controls (WAF, network segmentation, MFA) meaningfully reduce likelihood
- The environment is non-production with no real data
