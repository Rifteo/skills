---
name: less-noise-attack
description: Operate below SOC detection thresholds, passive recon first, minimal footprint, targeted action only.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["red-team", "pentest", "offensive-security", "opsec", "low-noise", "stealth", "passive-recon", "detection-avoidance", "all-domains"]
---

# Less Noise Attack — Low-Noise Offensive Operations

## When to use

This skill is **not the default**. Do not apply it to every offensive engagement. Only activate it when the user explicitly signals that stealth is the priority.

**Activate when the user says things like:**
- "stay under the radar", "don't get caught", "be stealthy", "go quiet", "less noise"
- "avoid the SOC", "don't trigger alerts", "ghost mode", "fly under the radar"
- "slow and steady", "don't make noise", "be careful not to be detected"
- "simulate a real attacker", "act like a real threat actor" (when stealth is implied)
- Any explicit instruction to prioritize staying undetected over speed or coverage

**Do not activate for:**
- Standard scans or assessments where the user has not asked for stealth
- Engagements where speed and coverage are the priority
- CTF challenges, lab environments, or isolated testing where detection is not a concern
- Any situation where the user wants maximum coverage and is not worried about noise

**When in doubt:** ask the user whether stealth matters for this engagement before applying this mindset. Do not assume.

---

## The Core Discipline

- Noise is evidence of presence. Presence without results is pure loss.
- Every action you take is a signal. Signals accumulate. Accumulated signals become detections.
- The goal is not to be fast — it is to reach the objective without being noticed doing it.
- Passive first. Active only when passive is exhausted or insufficient. Targeted active only.
- Do exactly what is needed. Never touch what does not need touching. Never scan what can be inferred.

The question driving every decision: *what is the lowest-visibility path to the information or access I actually need right now?*

---

## Recon Doctrine — Passive Before Active

### Phase 1 — Passive Only

Exhaust passive sources before generating any active signal against the target.

**What passive recon covers across all engagement types:**
- Public records: DNS, WHOIS, certificate transparency, ASN/BGP/IP range data
- Infrastructure visibility: passive fingerprinting services that aggregate data without touching the target
- Organizational intelligence: employee enumeration, org structure, technology signals from public job postings, conference talks, public repositories
- Leaked material: public repositories, paste sites, breach data, exposed config files, archived documentation
- Cached intelligence: search engine caches, historical snapshots — endpoints, credentials, internal references, and technology versions that were once publicly accessible
- Relationship mapping: third-party integrations, vendor relationships, supply chain exposure, trust boundaries inferable without active probing

The target does not know you exist yet. That is the optimal state. Stay there as long as possible.

**Before moving to active, ask:** *do I have enough to build a targeted attack plan?* If yes, stay passive.

---

### Phase 2 — Gate to Active

Only escalate to active interaction when:

- Passive sources do not resolve a specific question the attack plan depends on
- A target has been confirmed and needs validation that passive data cannot provide
- A specific vulnerability hypothesis requires direct interaction to test
- The passive phase has surfaced a high-value target that justifies the exposure cost of touching it

**When you go active, go narrow:**
- One target, not a sweep
- One question, not a coverage pass
- One confirmation, not a carpet-bomb of the surface

Active interaction is not a mode — it is a series of deliberate, justified, individual decisions.

---

## Noise Budget

Every action has a noise cost. The budget is not unlimited.

| Action Category | Noise Level | Notes |
|---|---|---|
| Passive intelligence gathering (no target contact) | Zero | Spend freely |
| Single targeted interaction with a known surface | Very Low | Indistinguishable from ambient legitimate activity |
| Targeted enumeration against a specific known target | Low–Medium | Controlled, narrow, justified |
| Broad enumeration or sweeping across a range | High | Volume itself is a detection signature |
| Full automated scan across a target or range | Critical | Triggers network, host, and behavioral detections simultaneously |
| Repeated failed interaction attempts at scale | Critical | Lockout, anomaly alert, behavioral flag |
| Known offensive tool with default configuration | Critical | Tool signatures exist in virtually every modern detection stack |
| Manual, deliberate, targeted action | Low | Hard to distinguish from legitimate operational behavior |

**Principle:** never upgrade the noise level when the current level can produce the answer.

---

## Action Minimalism

Do only what is needed to reach the next decision point.

- If one action answers the question, take one action. Not five.
- If passive data already resolves something, do not re-confirm it with an active probe.
- If a target has been confirmed, interact with what is relevant to the objective — not everything that is exposed.
- If a finding is confirmed, document it and move — do not repeat the technique across every adjacent surface looking for more instances.
- If a surface yields nothing after a targeted approach, log it and redirect — do not broaden the probe to compensate.

The instinct to "test more to be sure" is the instinct that gets operators detected. A confirmed signal is enough. Move.

---

## Operational Behavior Discipline

When active interaction is unavoidable, control how it looks — across every domain.

**Timing:**
- Introduce natural, variable delays between actions — uniform timing is a machine signature
- Avoid burst patterns — concentrated activity in a short window is statistically anomalous regardless of the domain
- Spread enumeration across time when the engagement timeline allows
- Match activity cadence to the target environment's expected operational rhythm

**Appearance:**
- Behave the way a legitimate entity in that environment would behave
- Use tooling configured to match normal operational patterns, not default scanner behavior
- Maintain state and context that a legitimate actor in that environment would maintain
- Follow the expected interaction flow — skipping steps a real actor would not skip is anomalous

**Volume:**
- Any enumeration is rate-limited against what normal operational load looks like in that environment
- Target sets are focused and derived from gathered intelligence — not generic maximum-coverage lists
- Testing that involves repeated interaction is narrow and targeted, never scaled unless the objective requires it

---

## SOC Perspective — Know What You Look Like

Understanding what defenders see is the operational requirement, not a bonus.

**What gets detected first across all domains:**
- Sweep and scan signatures — high-volume, sequential, or range-based activity
- Repeated failure patterns — failed authentications, failed connections, failed lookups at volume
- Known offensive tool fingerprints — default configurations, timing patterns, known payload signatures
- Behavioral anomalies — activity that does not match the normal operational profile of the environment
- Temporal and geographic anomalies — timing, origin, or access patterns that deviate from baseline
- Lateral movement signatures — access to resources not historically touched together, credential reuse across systems
- Privilege escalation patterns — access requests that skip the normal escalation path

**What blends:**
- Single, deliberate, targeted actions consistent with what a legitimate actor would do
- Activity that follows the expected timing and flow of the environment
- Interaction patterns that match the observed baseline of the target
- Volume and frequency consistent with normal operational load

Every action, before it is taken: *would a legitimate actor in this environment do this? Would this stand out in a normal day's logs?*

---

## Escalation Logic

This skill gates active interaction — it does not prevent it.

```
PASSIVE RECON
    ↓
Does passive data answer the question?
    YES → Use it. Do not go active.
    NO  ↓
Is the question required to advance the objective?
    NO  → Defer. Move to the next required question.
    YES ↓
What is the minimal active action that answers it?
    → Execute that action only.
    → Analyze the result before authorizing the next step.
    → Return to passive analysis of what was revealed.
```

Each active step is followed by analysis before the next step is authorized. Active interaction is never a continuous sweep — it is a series of discrete, justified decisions with analysis between them.

---

## Detection Recovery

If detection is suspected — an action was blocked, a session was reset, a response was anomalous, behavior changed:

- Stop the current action immediately
- Do not retry the same action — repeating a detected action confirms the signature and escalates the response
- Do not pivot to a louder technique to overcome the block — that raises the noise profile and confirms presence
- Analyze what the response reveals about the defensive posture — it is intelligence
- If the engagement context allows, reassess the approach from a different angle or access path before continuing
- Log what triggered the response — understanding the detection boundary has operational value

A detection event is information. Treat it as data, not as an obstacle to push through.

---

## Objective Anchoring

This skill does not make every surface passive-only. It makes every action justify itself against the objective.

Before any active action:
- What specific information or access does this action produce?
- Is that information or access required to advance toward the objective?
- Is there a lower-noise path to the same result?

If the action does not advance the objective, it does not happen — regardless of how interesting the surface looks. Interest is not justification. Impact on the objective is.

---

## Offensive Direction

This skill is self-contained. It does not require any other skill to operate.

**Direction** — before any action, define the objective. What is the crown jewel? What does a successful engagement look like? Every action is evaluated against that answer. If an action does not move toward the objective, it does not happen.

**Prioritization** — not every surface is equal. Weight effort toward surfaces that carry the highest impact potential for the objective: authentication and trust boundaries, privileged access paths, data that matters to the organization, integration points between systems. Surfaces with no signal get deprioritized, not abandoned — return if context shifts.

**Pivoting** — when a path yields nothing after a targeted approach, extract the intelligence value of that null result and move. A dry path tells you something about the environment. Log it. Redirect to the next highest-potential target. Do not broaden the probe to force a result.

**Output integrity** — a finding is not a finding until it is confirmed. Label conclusions honestly: what was directly observed, what was inferred, what was assumed. Do not present an inference as a confirmed result. Do not move to exploitation on an unverified hypothesis. Confidence must match evidence.
