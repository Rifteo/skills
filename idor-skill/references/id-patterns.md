# ID Patterns Reference

## Numeric IDs
- Sequential integers: `1`, `2`, `1234` — trivially enumerable, highest IDOR risk
- Padded: `0001`, `00042`
- Prefixed: `ORD-1234`, `USR-99`, `ACC-2024-001`

## UUIDs
- v4 (random): `550e8400-e29b-41d4-a716-446655440000` — not easily guessable
- v1 (timestamp-based): partially predictable — note the timestamp portion
- Short UUIDs / NanoIDs: `V1StGXR8_Z5jdHi6B-myT` — check if truly random

## Hashed / Encoded IDs
- MD5: 32 hex chars — check if it's `md5(user_id)` (trivially reversible if ID is low)
- SHA1/SHA256: 40/64 hex chars
- Base64: ends with `=` padding, decode first
- Custom encoding: look for patterns, try CyberChef "Magic" mode

## Slugs
- Username-based: `/profile/alice` — try `/profile/bob`
- Title-based: `/posts/my-first-post` — enumerate via sitemap or wordlist

## File References
- `/uploads/user_1234/report.pdf` — path contains user ID
- `/download?file=invoice_1234.pdf` — filename contains object ID
- `/export?token=abc123` — opaque token, check if tied to user

## GUIDs in JWTs
Decode the JWT payload (base64, no verification needed client-side):
```
{ "sub": "1234", "org_id": "acme", "role": "user" }
```
Test: modify `sub` or `org_id` → re-sign with `alg: none` trick or test if server validates.

## GraphQL Node IDs
Often base64 of `TypeName:numericID`:
```
"VXNlcjoxMjM0" → base64 decode → "User:1234"
```
Swap `1234` with another user's ID, re-encode.

## Enumeration Tips
- Burp Intruder with numeric payload (0–9999) on the ID position
- `ffuf -w ids.txt -u https://target.com/api/users/FUZZ`
- For UUIDs: not worth brute-forcing — look for them leaked in other responses, logs, emails
- For sequential IDs: note the gap between your ID and "user 1" — are there admin accounts at low IDs?
