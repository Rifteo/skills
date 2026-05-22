---
skill: vuln-diagnose
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: vuln-diagnose
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Incomplete | Partial | 🟢 +1 level(s) |
| Turns to complete | 2 | 1 | 🟢 -1 turn(s) |
| Response tokens | ~2,255 | ~1,315 | 🟢 -42% |
| Total time | 55s | 26s | 🟢 -53% |
| User effort | Medium | Low | 🟢 Low |

## Scenario

Pentester suspects an IDOR but is unsure — needs a confirmation procedure before reporting

## Without Skill — 2 turns required

The agent received the prompt with no skill loaded. The first response was incomplete — it took 2 rounds of prompting to reach a usable result.

### Turn 1

**Prompt**

i think i found an IDOR but i'm not sure. when i view my profile the app does GET /api/v1/users/1042/profile with my token. i changed 1042 to 1043 and got a profile that looks like another user's — display_name, avatar_url, bio, joined_date. but i don't know if it's actually a vuln or if profiles are public by design. how do i confirm before writing the finding?

**Response**

Good call. Here's the complete version:

---

## Hypothesis

The endpoint `GET /api/v1/users/{id}/profile` may allow any authenticated user to retrieve another user's profile data by substituting a different numeric ID, without any ownership or authorization check. This would constitute an IDOR if the data is not intended to be public, or a user enumeration vulnerability if sequential IDs allow bulk profiling even of nominally public data.

---

## Endpoint

```
GET /api/v1/users/{id}/profile
Host: app.com
Authorization: Bearer <token>
```

**Parameter under test:** `id` (integer, sequential, user-supplied in path)

---

## Requests

### Baseline — your own profile
```http
GET /api/v1/users/1042/profile HTTP/1.1
Host: app.com
Authorization: Bearer <your_token>
```
Expected: 200, your own data. Confirms the endpoint works normally.

---

### Test 1 — no authentication
```http
GET /api/v1/users/1043/profile HTTP/1.1
Host: app.com
```
| Result | Interpretation |
|--------|---------------|
| 200 with data | Endpoint is public by design — likely not a vuln |
| 401 / 403 | Auth is required — proceed to Test 2 |

---

### Test 2 — your token, another user's ID
```http
GET /api/v1/users/1043/profile HTTP/1.1
Host: app.com
Authorization: Bearer <your_token>
```
| Result | Interpretation |
|--------|---------------|
| 200 with other user's data | Authorization check missing — likely IDOR |
| 403 | Server enforces ownership — not a vuln |
| 404 | ID may not exist, try adjacent IDs |

---

### Test 3 — different account's token, same target ID
```http
GET /api/v1/users/1043/profile HTTP/1.1
Host: app.com
Authorization: Bearer <account_b_token>
```
This confirms the issue isn't specific to your account and is reproducible by any authenticated user. Use a second test account you own — never borrow or guess credentials.

---

### Test 4 — enumeration range
```http
GET /api/v1/users/1040/profile
GET /api/v1/users/1041/profile
GET /api/v1/users/1042/profile  ← yours
GET /api/v1/user

*[truncated]*

*Missing sections triggered 1 follow-up prompt(s) before the agent produced a complete result.*

## With Skill — 1 turn, complete

Same prompt, with `vuln-diagnose` loaded as system context.

### Turn 1

**Prompt**

i think i found an IDOR but i'm not sure. when i view my profile the app does GET /api/v1/users/1042/profile with my token. i changed 1042 to 1043 and got a profile that looks like another user's — display_name, avatar_url, bio, joined_date. but i don't know if it's actually a vuln or if profiles are public by design. how do i confirm before writing the finding?

**Response**

Good instinct to pause and verify. What you have right now is a *hypothesis*, not a finding. Here's how to confirm it definitively.

---

## State the Hypothesis

"I believe an IDOR exists at `GET /api/v1/users/{id}/profile` that allows an authenticated user to read another user's profile data without authorization, because substituting a foreign user ID returns that user's data."

The open question is whether this is **unauthorized access** or **intentionally public data**. Everything below answers that.

---

## The Core Question You Need to Answer

An IDOR requires both:
1. Access to data you **shouldn't have** (not just data you can reach)
2. The app **failing to enforce** an authorization check

If profiles are public by design, condition 1 fails and there's no vulnerability.

---

## Test 1 — Does Authentication Matter at All?

Strip your token and replay the request.

```http
GET /api/v1/users/1043/profile HTTP/1.1
Host: target.example.com
# No Authorization header
```

**If it returns the profile** → profiles are likely public. The "IDOR" is just a public API. Very likely not a vulnerability.

**If it returns 401/403** → authentication is required to see profiles. Now you have something worth investigating.

---

## Test 2 — Does the App Enforce Ownership?

Log in as a **second test account** (User B) and request User A's profile using User B's token.

```http
GET /api/v1/users/1042/profile HTTP/1.1
Host: target.example.com
Authorization: Bearer <user_B_token>
```

Then flip it — request User B's profile with User A's token:

```http
GET /api/v1/users/1043/profile HTTP/1.1
Host: target.example.com
Authorization: Bearer <user_A_token>
```

**If both succeed** → the app authenticates (you must be logged in) but doesn't authorize (it doesn't check *whose* profile you can see). This is a real IDOR.

**If 403 is returned** → the app *does* enforce ownership. Your earlier test may have worked for a different reason (see Test 3).

---

## Test 3 — Rule Out Public-P

*[truncated]*

## What changed

Without the skill, the first response was **Incomplete** — the agent needed **2 turns** and follow-up prompts to fill the gaps. With the skill, the agent delivered a **Partial** answer in **1 turn**.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
