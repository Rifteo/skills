---
skill: control-lookup
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: control-lookup
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Incomplete | Complete | 🟢 +3 level(s) |
| Turns to complete | 3 | 1 | 🟢 -2 turn(s) |
| Response tokens | ~3,297 | ~2,068 | 🟢 -37% |
| Total time | 63s | 51s | 🟢 -19% |
| User effort | High | Low | 🟢 Low |

## Scenario

Auditor writing a finding, needs the right control ID and cross-framework mapping

## Without Skill — 3 turns required

The agent received the prompt with no skill loaded. The first response was incomplete — it took 3 rounds of prompting to reach a usable result.

### Turn 1

**Prompt**

writing a finding for a client, the vulnerability is they have no documented access control policy. is A.9.1.1 the right ISO 27001 control? i need the details of what this control requires and the mapping to NIST CSF and PCI-DSS, the client is PCI in scope

**Response**

I apologize for the confusion. Looking back at my previous response, I can see that I **did include all four sections** you are asking for:

- ✅ **Control:** — ISO 27001:2013 – A.9.1.1 – Access Control Policy
- ✅ **Objective:** — Defined under the Objective heading
- ✅ **Cross-Framework Mappings:** — Covered ISO 27001, NIST CSF, and PCI-DSS in a dedicated section
- ✅ **Testing Hints:** — 10-step table at the bottom of the response

---

It is possible the response was **truncated by your interface** before fully rendering, as it is a long document.

**Could you clarify one of the following so I can help you correctly:**

1. **Was the response cut off?** If so, which section did it stop at and I will reproduce from that point forward
2. **Is the formatting not rendering correctly?** I can reformat into plain text or a different structure
3. **Are you looking for a different depth or style** in any of those four sections? For example:
   - More detailed Objective language
   - Additional framework mappings (e.g., COBIT, SOC 2, HIPAA)
   - More granular or differently structured Testing Hints
   - A specific report template format you are working to

Let me know and I will produce exactly what you need.

*Missing sections triggered 2 follow-up prompt(s) before the agent produced a complete result.*

## With Skill — 1 turn, complete

Same prompt, with `control-lookup` loaded as system context.

### Turn 1

**Prompt**

writing a finding for a client, the vulnerability is they have no documented access control policy. is A.9.1.1 the right ISO 27001 control? i need the details of what this control requires and the mapping to NIST CSF and PCI-DSS, the client is PCI in scope

**Response**

**Control:** A.9.1.1 — Business Requirements of Access Control
**Framework:** ISO 27001:2013
**Domain:** A.9 Access Control > A.9.1 Business Requirements of Access Control
**Type:** Preventive

> **Note on edition:** You referenced A.9.1.1, which is the **ISO 27001:2013** notation. If your client is certified or scoping against **ISO 27001:2022**, the equivalent is **A.5.15 (Access Control)**. The 2022 control is broader and explicitly includes identity management concepts. If you are not sure which edition applies to your client, check their certificate or scope document — it will state the edition. The rest of this card uses the 2013 control as requested.

**Objective:**
To ensure that access to information and information processing systems is defined and controlled based on documented business and security requirements, preventing unauthorized access to information assets.

**Description:**
The organization shall establish, document, and review an access control policy based on business and information security requirements. The policy must address rules for access control, the rights and restrictions applicable to all users, and be communicated to users and relevant parties. Asset owners shall determine appropriate access control rules, rights, and restrictions for their specific assets, with the level of detail appropriate to the access controls employed.

**Implementation guidance:**
- Produce a formal, approved access control policy document that states the organization's rules for granting, modifying, revoking, and reviewing access across all system types in scope
- The policy should address role-based or need-to-know access principles, separation of duties requirements, and the process for access requests and approvals
- Define the review cycle — typically annual — and assign ownership to a named role (e.g., CISO, IT Manager) responsible for maintaining and approving the policy
- Communicate the policy to all relevant staff and ensure acknowledgment is rec

*[truncated]*

## What changed

Without the skill, the first response was **Incomplete** — the agent needed **3 turns** and follow-up prompts to fill the gaps. With the skill, the agent delivered a **Complete** answer in **1 turn**.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
