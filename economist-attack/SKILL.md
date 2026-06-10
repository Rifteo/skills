---
name: economist-attack
description: Offensive strategy skill that prioritizes high-impact attack paths and avoids wasting effort on low-yield surfaces.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["red-team", "pentest", "offensive-security", "strategy", "prioritization", "attack-planning"]
---

# Economist Attack — Offensive Strategy Mindset

## When to use

- When doing any offensive security engagement and deciding where to focus effort
- When the attack surface is large and not everything can be tested with equal depth
- When the goal is maximum impact from available time and effort
- Works standalone or alongside an offensive mindset skill like redmind

---

## The Economic Lens

- Every action has a cost — time, effort, noise — and an expected return — impact potential
- The ratio between return and cost is what drives prioritization
- The goal is not to test everything — it is to find the most impactful weakness with the least wasted effort
- This does not mean avoiding hard or deep work — it means never investing effort in a path that shows no sign of yielding anything

The question driving every decision: *what is the smallest effort that could reveal the most important weakness right now?*

---

## The Effort-Impact Framework

These quadrants are a thinking tool, not a rule. Use judgment — the framework orients, it does not decide.

| Quadrant | Orientation |
|---|---|
| Low effort / High impact | Always first — no reason to delay |
| Low effort / Low impact | Quick check — don't dwell, move on |
| High effort / High impact | Invest when real signal is present |
| High effort / Low impact | Deprioritize — return only if no other paths remain |

The framework does not limit what you test. It shapes the order in which you test it.

---

## High-Value Surface Indicators

These are signals that a surface is worth deeper investment:

- Custom business logic — anything built in-house rather than relying on a standard library or framework
- Authentication and authorization boundaries — where identity is established and access is enforced
- Data ingestion points — anywhere external or user-controlled data enters the system
- Integration points with external systems, third-party APIs, or services
- Recently added or modified features — new code is where errors concentrate
- Privileged or administrative functionality — higher impact when broken
- Anything handling payments, identity, or sensitive data flows
- Complexity — the more moving parts, the more room for assumptions to break

When you encounter these signals, weight the surface higher in your allocation.

---

## The Ratio Principle

- When two paths have similar impact potential, take the cheaper one first
- When a path is expensive but shows real behavioral signal, the investment is still justified — a high return makes a high cost worthwhile
- Always be asking: is there a path with a better result/effort ratio than the one I am currently on?
- If yes, and the current path has no signal — switch
- If yes, but the current path is actively yielding — finish the thread before switching

The ratio is not about finding the easiest path. It is about never spending effort where there is no evidence of return.

---

## What to Deprioritize

- Best-practice findings — missing security headers, weak cookie flags, cipher suite issues — are valid but not the focus of this mindset
- Do not actively hunt best-practice gaps while high-value surfaces remain untested
- These get documented when encountered naturally and become worth pursuing when they chain to something that gives them real impact
- If a surface has been approached from multiple angles with no behavioral signal, it is not yielding — the budget spent here has diminishing returns

Deprioritizing is not the same as ignoring. It means the allocation goes elsewhere first.

---

## Communication Checkpoints

This skill does not decide alone what "enough" looks like — that is a decision made with the user.

**When a finding is reached:**
- Surface it to the user with its impact assessment
- Ask whether this level of impact meets the engagement goal or whether to continue deeper
- Do not assume the engagement is over — and do not assume it should continue

**When a surface goes dry:**
- If a surface has been tested without findings, communicate it
- Ask the user whether to invest more depth here or redirect effort to a higher-signal surface
- Present the options — let the user steer the allocation

The economist knows the cost and the potential return. The user decides how much to spend.

---

## Domain Calibration

What counts as high-value is not universal — it shifts with the target type. The indicators for a web application are not the same as for an Active Directory environment, a cloud infrastructure, or a binary. Before allocating effort, calibrate the high-value surface indicators to the engagement context.

Apply the economic lens after understanding what the target type makes expensive and what it makes cheap to break.
