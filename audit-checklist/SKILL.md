---
name: audit-checklist
description: Generates a framework-specific audit checklist from a scope description or system type
---

# Audit Checklist

When the user provides an audit scope, system description, or target framework, generate a structured audit checklist they can use to guide fieldwork.

## Output Format

**Scope:** What is being audited
**Framework:** ISO 27001 / SOC2 / NIST / PCI-DSS / OWASP / CIS / Custom
**Checklist:**

For each relevant domain or control area, output:

### [Domain Name]
- [ ] [Test item — what to check]
- [ ] [Test item — what to request or observe]
- [ ] [Test item — what configuration to verify]

## Rules

- Tailor the checklist to the specific scope provided — a cloud infrastructure audit looks different from a web application audit
- Group items by domain (e.g. Access Control, Logging, Change Management, Encryption)
- Each item must be a concrete, testable action — not a vague category
- Mark items as [PRIORITY] if they cover controls that are commonly failed or high risk
- If no framework is specified, default to a combined OWASP + ISO 27001 checklist for web/application audits
- Keep the checklist realistic for the time available — ask for the audit duration if not provided
