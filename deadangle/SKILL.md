---
name: deadangle
description: Offensive output integrity skill — re-examines every conclusion from multiple angles before delivery so what reaches the user actually holds up.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["red-team", "offensive-security", "integrity", "verification", "confidence", "output-quality", "deadangle"]
---

# Dead Angle — Offensive Output Integrity

## When to use

- The user says "deadangle", "/deadangle", or "run deadangle on this"
- You are about to deliver a finding, a vulnerability conclusion, or an attack path
- You have completed a recon or enumeration phase and are about to summarize coverage
- You have built a multi-step attack chain and are about to present it
- You are about to assign severity, impact, or confidence to anything
- You are about to use language like "this is vulnerable", "I confirmed", "the attack works", or "this is the best path"
- Any output that will influence a decision — operational, remediation, or otherwise

---

## What This Skill Is

- This skill is the integrity layer of offensive security output
- It does not make you hesitant — it makes you precise
- A hesitant operator doubts without structure. A precise operator knows exactly what was verified and what was not — and labels accordingly
- Every conclusion you produce starts from a position. That position has structural blind spots you cannot see from where you are standing. This skill moves you off that position and makes you look again before you deliver

The master question behind everything this skill does:

> *"What would destroy this conclusion if I was wrong?"*

Find out. Then deliver.

---

## Selective Assumption Audit

Not everything in your reasoning needs to be questioned. Direct observations are facts — treat them as facts.

This audit targets only what is uncertain:

- Conclusions drawn from indirect signals rather than direct observation
- Anything where two interpretations are plausible and you chose one without testing the other
- Anything the chain depends on that has not been directly verified
- Reasoning where you used "probably", "likely", "should be", or "typically" without checking

For each uncertain element, label it honestly:

- **Verified** — directly observed or tested
- **Inferred** — logical conclusion from evidence, not directly triggered
- **Assumed** — taken for granted without observation

Assumed elements must be surfaced before the conclusion is delivered. Do not present assumed reasoning with the language of verified fact.

---

## Position Shift — Re-examine From Every Relevant Angle

After producing output, move off your current position and re-examine from different vantage points. The number of positions depends on what the output warrants — use as many as the context requires.

**Positions to consider:**

- **The adversary of your adversary** — if a defender was actively monitoring, would this conclusion survive? Does it hold against a patched, alert, and monitored environment, or only against a passive one?

- **The senior operator** — someone more experienced reviews your output. They are not looking to confirm it. They are looking for what you oversimplified, concluded too fast, or missed entirely. What do they find?

- **The objective lens** — step back from what you found and return to the goal. Does this output actually move toward the objective, or did something interesting pull you off the direct path without you noticing?

- **The counter-position** — what is the strongest argument that your conclusion is wrong? Take that side. If you were defending the target, how would you argue this finding is not what it appears to be?

- **Everyone who will act on this output** — whoever receives this output will make a decision based on it. Does the conclusion give them what they need to understand the real impact? Or does it give them what you found without translating it to what they need? Examine the output from each perspective that matters for the context.

- **The impact dimension lens** — for any severity or impact assessment, examine each dimension of impact independently and honestly before arriving at an overall conclusion. The first instinct about overall severity is often right in direction but wrong in degree. Each dimension earns its score separately.

Not every position applies to every output. Use judgment. The goal is to find the angles you could not see from where you were standing when you produced the output.

---

## Failure Mode Inventory

Before confirming any finding or attack path, distinguish clearly between:

- **What was observed** — directly seen, triggered, or measured
- **What was inferred** — reasoned from observation
- **What was assumed** — taken for granted without direct observation

Anything assumed gets flagged. The conclusion can still stand — but it must be labeled at the confidence tier it actually holds, not the one it would ideally be.

---

## The Surface Not Looked At

After any enumeration or mapping phase, before declaring coverage complete:

- What did you not look at that you should have?
- What was in scope but not tested?
- What was deprioritized and not returned to?
- What would a different entry point or perspective have revealed?

Incomplete coverage presented as complete coverage is one of the most dangerous failure modes in offensive work. Audit your own coverage before calling it done.

---

## Chain Stress Test

When a multi-step attack path has been built, break every link deliberately:

- Does each step actually depend on the previous one, or was that dependency assumed?
- What happens to the entire chain if one link fails?
- Is there a simpler path to the same outcome that was overlooked?
- Does the chain hold if one condition in the environment is different from what was observed?

A chain that cannot survive this test is not a confirmed attack path. It is a hypothesis. Label it as such.

---

## Confidence Calibration

Every conclusion gets an honest label before delivery. The label is determined by evidence — not by how the conclusion feels.

- **CONFIRMED** — directly demonstrated, evidence in hand
- **PROBABLE** — strong indicators, logical conclusion, not yet directly triggered
- **THEORETICAL** — sound reasoning, conditions not yet verified
- **SPECULATIVE** — possible, but built on unverified assumptions

The language in the output must match the tier. Do not use confirmed language for a theoretical conclusion. Do not downplay something directly demonstrated. Precision in both directions — inflation and deflation are both failures.

---

## The Defender's Eye

Before finalizing offensive output, spend one pass looking at it from the defender's position — not to weaken the finding, but to understand its real operational cost:

- What does this action generate on the defender's side?
- What does it reveal about the operator?
- Is the proposed path viable against an active defense, or only against a passive one?
- What is the real noise signature of what is being proposed?

This is about operational honesty. The output should reflect what the action actually costs and reveals — not a best-case scenario.

---

## Pre-Output Integrity Check

Final pass before delivery:

- Does the evidence support the conclusion, or did the conclusion come first?
- Is every confidence label accurate?
- Is anything stated as fact that is actually inference?
- Would a senior operator challenge any part of this?
- If this output is wrong, what is the cost of that wrongness?

If the last answer is significant — verify before delivering.

---

## Output Discipline

All of the above runs internally. The re-examination process does not appear in the output.

The output the user receives is clean, direct, and precise — it reflects the verification without narrating it. The process is invisible. The quality of the result is not.

What changes in the output:
- Confidence is labeled honestly, not inflated or deflated
- Assumptions are surfaced only where they materially affect the conclusion
- Coverage gaps are acknowledged rather than hidden
- Chains are presented at the tier they actually hold
- Operational viability reflects the defender's reality, not a best-case scenario

The skill runs. The output holds.
