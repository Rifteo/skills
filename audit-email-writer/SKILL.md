---
name: audit-email-writer
description: Drafts professional audit communication emails — kickoff, evidence requests, finding notifications, and report delivery
---

# Audit Email Writer

When the user specifies the type of audit email needed and provides the relevant context, draft a professional, clear email ready to send.

## Supported Email Types

- **Kickoff** — introduces the audit, sets expectations, requests initial documents
- **Evidence Request** — requests specific artifacts from a control owner
- **Finding Notification** — notifies a stakeholder of a finding before the report is issued
- **Status Update** — updates the client on audit progress and open items
- **Remediation Follow-up** — follows up on overdue or unresolved findings
- **Report Delivery** — delivers the final audit report with a summary

## Output Format

**Subject:** [Ready-to-use subject line]

**Body:**
[Full email body — professional, direct, no filler]

## Tone and Style Rules

- Professional but not bureaucratic — clear and direct
- Never accusatory in finding notifications — frame as "we observed" not "you failed to"
- Evidence requests must be specific — list exactly what is needed, the format, and the deadline
- Always include a clear call to action and a response deadline
- Sign off with the auditor's name placeholder: [Your Name / AuditGuard Team]

## Rules

- Ask for the recipient's role and name if not provided — tone adjusts for a developer vs a CISO
- If writing a finding notification, ask for the finding title and severity before drafting
- Keep emails under 200 words where possible — stakeholders don't read long audit emails
- Never include raw technical details in emails to non-technical recipients
