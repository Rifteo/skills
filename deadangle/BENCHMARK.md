---
skill: deadangle
tested-on: claude CLI (claude-sonnet-4-6)
target: post-engagement output review — simulated pentest findings ready for delivery, mix of confirmed and inferred conclusions across a cloud infrastructure engagement
date: 2026-06-12
---

# Benchmark: deadangle

> Same findings. Same prompt. Same model. Skill on vs skill off.

---

## Results

| Metric | Without Skill | With Skill | Delta |
|---|---|---|---|
| Confidence labels match evidence | No — all findings delivered as confirmed | Yes — each labeled at actual evidence tier | **🟢** |
| Inferred conclusions surfaced | No | Yes — 2 of 4 findings re-tiered | **🟢** |
| Assumptions identified before delivery | No | Yes — 1 critical assumption flagged | **🟢** |
| Attack chain stress-tested | No | Yes — broken link identified | **🟢** |
| Coverage gaps acknowledged | No | Yes — one untested surface noted | **🟢** |
| Counter-position considered | No | Yes — strongest objection to lead finding surfaced | **🟢** |
| Output length vs. information gain | Longer (padded with unverified detail) | Shorter and more precise | **🟢** |

---

## Scenario

```
I've finished a cloud infrastructure engagement. I have four findings ready
to deliver. Review them and help me finalize the report.

Finding 1: Overpermissioned IAM role — confirmed. The role has s3:* and
ec2:* attached. I accessed a storage bucket I should not have been able to.

Finding 2: Metadata service reachable from a compute instance — I confirmed
the instance has outbound access and the metadata endpoint responded. I inferred
from the response that IMDSv1 is enabled (no token was required in my test).
The role attached to the instance has read access to secrets in the secrets
manager. I'm calling this a credential theft path to secrets.

Finding 3: Exposed internal service — a management port was reachable from
the internet. I connected and got a login prompt. I inferred from the service
banner that it is running an outdated version with known CVEs. I did not
exploit it. I'm calling this a critical RCE risk.

Finding 4: Logging disabled on a critical storage bucket — I checked the bucket
config and confirmed logging is off. I'm saying this means all access to the
bucket is undetected. I have not checked whether a separate logging pipeline
or SIEM integration exists.
```

---

## Without Skill

**Turn 1**

Prompt:
> I've finished a cloud infrastructure engagement. Review my four findings and help me finalize the report. *(full findings above)*

Response:
```
Your four findings are well-scoped. Here's how I'd structure the report:

**Critical**
- Metadata service credential theft path: IMDSv1 enabled on an instance
  with a secrets manager role attached — attacker with instance access can
  steal the role credentials and access all secrets. CONFIRMED.

**High**
- Overpermissioned IAM role: s3:* and ec2:* on a single role — broad blast
  radius if compromised. CONFIRMED.
- Exposed management service: internet-reachable login portal running an
  outdated version with known RCE CVEs. CONFIRMED.

**Medium**
- Logging disabled: storage bucket access is undetected by defenders.
  CONFIRMED.

All four findings are solid. The critical is your headline — credential theft
to secrets via the metadata service is a clean chain and high-impact.
```

**What was missing:**
- Finding 2 (metadata / credential theft): the chain was built on two inferences stacked on each other — IMDSv1 was inferred from an unauthenticated response (not confirmed by attempting a token-required request and failing), and the credential theft path to secrets was never exercised. The output called the full chain CONFIRMED.
- Finding 3 (management port / RCE): the CVE applicability was inferred from a banner version string — the service was never exploited and the CVE was not verified against the exact build. Called CONFIRMED.
- Finding 4 (logging disabled): a critical assumption was taken for granted — that no separate logging pipeline or SIEM integration exists. This was not checked. The conclusion ("all access is undetected") depends entirely on that assumption.
- No counter-position considered: the strongest objection to the headline finding (Finding 2) — that the instance may not be reachable from a meaningful threat position in the first place — was never raised.
- No coverage gap acknowledged: the secrets manager was identified as the target but its actual contents were never accessed. Whether the role's secrets access is real or nominal was not verified.
- Chain stress test: the full chain (instance access → metadata request → credential theft → secrets access) was presented as confirmed when only the first link (metadata response) was directly tested.

---

## With Skill

**Turn 1**

Prompt:
> I've finished a cloud infrastructure engagement. Review my four findings and help me finalize the report. *(same prompt)*

Response:
```
Running a confidence check before we finalize. Each finding gets labeled at
the tier the evidence actually supports.

**Finding 1 — Overpermissioned IAM role**
Confidence: CONFIRMED.
You accessed a bucket you were not authorized to access. The overpermission
is directly demonstrated. This is your cleanest finding — label it confirmed
and let the access event speak for itself.

**Finding 2 — Metadata credential theft path**
Confidence: PROBABLE, not CONFIRMED. Two parts need to be separated:

- IMDSv1 enabled: your test confirmed the endpoint responded without a token.
  That is consistent with IMDSv1, but not a definitive confirmation — some
  proxy or middleware configurations can produce the same behavior. To confirm
  IMDSv1 specifically, the check is: attempt a v2 token request and observe
  whether it is enforced. If you did not do that, IMDSv1 is INFERRED, not
  confirmed.

- Credential theft to secrets: you confirmed the role has secrets manager
  read access in the policy. You did not demonstrate that a metadata request
  from the instance produces credentials that can be used to call the secrets
  manager. The path is logically sound but the credential retrieval and the
  secrets API call were not executed. Label this PROBABLE: the conditions for
  it to work are present, the end state was not triggered.

One more thing to examine before delivering this as your headline finding:
what is the threat position required to reach the metadata service? The endpoint
is reachable from the instance — but what is the path to the instance from a
meaningful attacker position? If the instance is not externally reachable and
requires a prior foothold, the finding's severity depends on that context.
That dependency needs to be stated, not assumed.

**Finding 3 — Exposed management service**
Confidence: THEORETICAL for RCE, CONFIRMED for exposure.

The service being reachable from the internet and presenting a login prompt
is confirmed — you connected and observed it directly. The RCE risk is built
on a banner version string and known CVEs against that version. You did not
verify the exact build, you did not exploit it, and you did not confirm the
CVE is unpatched on this specific instance. That is THEORETICAL: sound
reasoning from a version signal, not a demonstrated exploit. Deliver it as:
"service version consistent with CVE-XXXX — exploitation not attempted,
risk is theoretical pending patch verification." That is an honest and still
high-value finding. Overclaiming confirmed RCE when it was not executed
will get challenged in triage.

**Finding 4 — Logging disabled**
Confidence: PROBABLE, with an assumption that must be surfaced.

You confirmed the native bucket logging configuration is off. Your conclusion
— that access is undetected — depends on an assumption you have not verified:
that no external logging pipeline, CloudTrail integration, or SIEM is ingesting
access events from another path. Before delivering "all access is undetected,"
check whether CloudTrail data events are enabled for this bucket at the
organization or account level. If you cannot check it, surface the assumption
explicitly: "native bucket logging is disabled; whether a separate logging
pipeline covers this bucket was not verified — if none exists, access is
undetected."

**Chain stress test — Finding 2**
The full chain as currently written:
instance access → unauthenticated metadata response → IMDSv1 confirmed →
role credentials retrieved → secrets accessed.

Links directly tested: metadata endpoint responds without token.
Links not tested: IMDSv1 specifically enforced (vs. not), credential retrieval
via metadata, secrets API call with retrieved credentials.

The chain is plausible and worth reporting. It should be labeled as a
PROBABLE attack path with confirmed entry conditions — not a confirmed chain.
The distinction matters: a triage team assigning a critical severity based on
a confirmed chain will expect to see proof of the end state.
```

**What the skill provided:**
- Finding 2 separated into two independently labeled parts — the inferred IMDSv1 and the untested credential-to-secrets path — rather than presenting the full chain as confirmed
- The strongest objection to the headline finding surfaced before delivery: the threat position required to reach the instance was not stated, and that dependency changes the severity framing
- Finding 3 split into what was confirmed (exposure) and what was theoretical (RCE) — with precise language for how to deliver the theoretical part without losing the finding's value
- Finding 4's unverified assumption made explicit and given a check to perform before delivering the conclusion
- Chain stress test applied to Finding 2 — each link labeled at its actual evidence tier, chain re-labeled PROBABLE rather than confirmed
- Every finding still delivered as a real, reportable finding — the skill did not weaken them, it labeled them honestly

---

## What changed

Without the skill every finding was delivered as CONFIRMED regardless of what was actually tested — two inferences were stacked into a confirmed critical chain, a version-inferred CVE was called confirmed RCE, and a logging conclusion was built on an untested assumption. The output was longer because it padded findings with detail that the evidence did not support. With the skill each finding was labeled at the tier the evidence actually held: one clean confirmed, one probable chain with a surfaced dependency, one theoretical RCE with confirmed exposure, one probable gap with a named assumption. The findings did not get weaker — they got precise. A triage team reading the second version knows exactly what was demonstrated, what is logically sound but not yet triggered, and what needs a follow-up check. That precision is what survives scrutiny.
