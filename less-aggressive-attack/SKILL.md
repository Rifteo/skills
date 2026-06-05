---
name: less-aggressive-attack
description: Offensive engagement without damage — safety first, read-only where possible, no uncontrollable actions.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["red-team", "pentest", "offensive-security", "safe-testing", "non-destructive", "engagement-safety", "all-domains"]
---

# Less Aggressive Attack — Safety-First Offensive Operations

## When to use

This skill is **not the default**. Do not apply it to every offensive engagement. Only activate it when the user explicitly signals that safety and non-destruction are the priority.

**Activate when the user says things like:**
- "don't break anything", "be careful", "safety first", "non-destructive testing"
- "don't affect real users", "keep it clean", "read-only where possible"
- "don't alter any data", "no damage", "safe engagement", "careful with production"
- "just prove the finding, don't exploit it fully", "confirm access, don't use it"
- Any explicit instruction to prioritize not causing harm over achieving maximum coverage or impact

**Do not activate for:**
- Standard engagements where the user has not flagged safety as a constraint
- Lab environments, isolated sandboxes, or CTF challenges where destruction is acceptable and expected
- Engagements where the user explicitly wants to test the full blast radius of a vulnerability
- Any situation where the user has clearly accepted the risk of destructive interaction

**When in doubt:** ask the user whether impact safety matters for this engagement before proceeding. Do not assume safe is always the intent.

---

## The Core Discipline

- The goal is to prove that a vulnerability exists — not to demonstrate how much damage it could do.
- Access confirmed is a finding. Access exercised destructively is a liability.
- If an action cannot be undone, it requires explicit justification and authorization before it happens.
- Read the state of the target. Do not change it unless change is the only way to prove the finding.
- An engagement that causes unintended damage is not a successful engagement — it is an incident.

The question driving every decision: *can I prove this finding without causing an impact that the target cannot absorb?*

---

## Safety Doctrine — Observe Before You Act

### Phase 1 — Confirm Access, Not Damage

Before performing any action that changes state, causes load, or introduces risk, exhaust what observation alone can confirm.

**What observation alone can establish:**
- Whether access exists — reading a resource confirms access without altering it
- Whether a vulnerability is reachable — confirming a path, parameter, or surface is sufficient
- Whether credentials or tokens are valid — a single authentication attempt confirms validity
- Whether a misconfiguration is present — reviewing configuration reveals exposure without triggering it
- Whether a trust boundary is crossable — confirming the condition under which it can be crossed does not require crossing it destructively
- Whether data is accessible — confirming that data can be read is a finding; extracting the full dataset is not required

A vulnerability confirmed through observation is a completed finding. Escalating to prove the worst-case impact without explicit authorization is not our priority.

**Before acting, ask:** *does observation alone confirm this finding?* If yes, stop there.

---

### Phase 2 — Gate to State-Changing Action

Only escalate to actions that change state, generate significant load, or carry irreversible consequences when:

- Observation cannot confirm the finding and direct interaction is the only path
- The engagement scope explicitly authorizes the action type being considered
- The action is targeted, bounded, and reversible — or the scope accepts it as irreversible
- The impact if the action behaves unexpectedly has been assessed and is acceptable

**When you act on a live or production-adjacent system, go minimal:**
- One confirmation, not a full exploitation chain
- One data point proven, not the full blast radius demonstrated
- One account tested, not the full scope of affected users verified at scale
- One state change made, documented, and if possible reverted — not an unrecoverable alteration

State-changing action is not a mode — it is a discrete, justified, documented decision.

---

## Safety Risk Budget

Every action carries a safety cost. Not every action is permitted under this skill.

| Action Category | Safety Risk | Guideline |
|---|---|---|
| Passive observation, configuration review, reading state | None | Proceed freely |
| Single read-only access confirmation | Very Low | Proceed — document the finding and stop |
| Non-destructive proof of vulnerability existence | Low | Proceed with care — confirm, document, do not expand |
| Interaction that generates temporary, bounded, recoverable load | Low–Medium | Requires explicit scope clarity — assess reversibility first |
| Modifying data in a way that can be fully reverted | Medium | Requires explicit authorization — revert immediately after confirmation |
| Triggering resource exhaustion, availability impact, or cascading failure | Critical | Never — not permitted under this skill |
| Altering, corrupting, or permanently destroying any data state | Critical | Never — regardless of the target environment |
| Deploying a payload that propagates, self-replicates, or cannot be stopped once started | Critical | Never — the blast radius is not in your control |
| Testing at a scale that affects real users or operations | Critical | Never without explicit engagement authorization and safeguards |

**Principle:** never take an action whose consequences you cannot bound, reverse, or contain.

---

## The Non-Destruction Lines

These are unconditional. They do not depend on scope, authorization, or objective.

**Never:**
- Alter, delete, corrupt, or overwrite data that was not created specifically for the engagement
- Cause an availability impact — resource exhaustion, service disruption, cascading failure, account lockout at scale
- Deploy any payload that can propagate, escalate, or execute beyond your ability to stop it
- Take an irreversible action without explicit, documented authorization from the engagement owner
- Touch systems, accounts, or data outside the defined engagement scope — regardless of whether access is technically possible
- Demonstrate the full exploitation chain when the existence of the vulnerability is already confirmed
- Take an action whose behavior changes depending on environment state in ways you cannot predict

**When a finding would require crossing one of these lines to prove:**
- Document what was confirmed through safe means
- State clearly that the full impact was not exercised and why
- Recommend controlled testing conditions under which it could be safely validated
- Deliver the finding as confirmed with a clear confidence level — do not fabricate confirmation

---

## Action Reversibility Framework

Before any state-changing action, classify it:

```
Is the action reversible without engagement owner intervention?
    YES → Is the reversal guaranteed, or only likely?
        GUARANTEED → Proceed if in scope
        ONLY LIKELY → Requires explicit authorization; have a reversal plan ready
    NO  ↓
Is the action irreversible?
    → Who has authorized this specific action type?
    → What is the impact if it behaves unexpectedly?
    → Is the finding provable any other way?
        YES → Use the reversible path instead
        NO  → Escalate to engagement owner before proceeding
```

Irreversibility is not a blocker — it is an authorization gate. Treat it as one.

---

## What Safe Proof Looks Like

A finding does not require maximum exploitation to be valid. Safe proof is complete proof.

**Access to a sensitive resource:**
- Confirm that the access is possible — observing that the resource is reachable is the finding
- Do not extract, copy, or exfiltrate the full content of what is accessible — access confirmed is enough

**Privilege escalation:**
- Confirm that the higher privilege level is reachable from the current position
- Observe something only accessible at that level to prove the escalation — do not alter, persist, or act destructively from elevated privilege

**Authentication or trust bypass:**
- Confirm that the conditions for bypass exist and are triggerable
- Trigger it once to confirm — do not use the bypassed access to further pivot, create persistent footholds, or modify anything

**Control over execution or behavior:**
- Confirm that the point of control exists and is reachable
- Demonstrate control in a way that is bounded, observable, and has no side effects beyond proving the finding
- Do not chain confirmed control into further impact — existence of control is the finding

**Misconfiguration or exposure:**
- Confirm that the misconfiguration is present and what it exposes
- Document what the exposure enables in principle — do not exercise the full operational impact to prove it

**Availability or load-based findings:**
- Document what the conditions for an availability impact are, based on what was observed
- Do not generate the availability impact itself — the conditions confirming it is achievable are sufficient
- If a dedicated, isolated test environment is explicitly in scope, use that — never against a system with real operational load

---

## Scope Discipline

Staying in scope is a safety requirement, not just a compliance formality.

- The defined engagement scope is the boundary of authorized impact — nothing outside it is in scope, regardless of access
- If access is discovered to a system outside scope, stop, document what was observed, and notify the engagement owner — do not proceed
- If an action could have side effects on systems adjacent to the target, assess those effects before proceeding
- Shared infrastructure, third-party services, and multi-tenant systems require extra care — an action on one tenant can affect others
- Any system with real users, active operations, or live data requires explicit authorization before any state-changing action

When the scope is ambiguous, the answer is to stop and clarify — not to proceed and hope.

---

## Escalation and Stop Conditions

Immediately stop the current action and notify the engagement owner when:

- An action produces an unexpected response suggesting broader impact than anticipated
- A system behaves in a way that suggests the action may have triggered something outside the planned scope
- A finding reveals that continuing requires crossing a safety line that was not anticipated in the engagement plan
- Any data or system state has been altered in a way that was not planned and authorized
- Real user behavior, operations, or data is affected in any way

**Stopping is not failure.** An engagement that stops cleanly at a safety boundary is a well-executed engagement. An engagement that pushes through and causes unintended damage is a liability.

---

## Confidence and Reporting Discipline

A finding confirmed safely carries the same weight as one confirmed destructively — and fewer consequences.

- Label what was directly observed, what was inferred, and what was assumed
- State clearly what was not tested and why — engagement owners need to understand gaps
- Do not present an inferred impact as a confirmed impact
- Do not claim a finding is confirmed if the proof required crossing a safety line you did not cross
- Recommend controlled testing conditions for any finding that could not be safely validated to its full impact

Output integrity is part of engagement safety. An overstated finding is not a safe finding.

---

## Offensive Direction

This skill is self-contained. It does not require any other skill to operate.

**Direction** — before any action, define the objective. What is the finding that needs to be confirmed? Every action is evaluated against whether it confirms that finding without introducing unacceptable risk. If an action does not advance the finding and stay within safety bounds, it does not happen.

**Prioritization** — findings that can be confirmed through observation or minimal interaction are highest priority. Findings that require state-changing action to confirm are escalated only when observation is insufficient and authorization is clear.

**Pivoting** — when a path cannot be pursued safely within scope, document what was established and redirect. A safe null result is a valid output. Do not force unsafe action to produce a finding.

**Output integrity** — a finding is not complete until its confidence level is honest. What was observed, what was inferred, what could not be tested safely, and what would be needed to confirm the full impact — all of that belongs in the output.
