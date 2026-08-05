# Secret & Key Patterns Reference

Complete pattern list for hunting hardcoded secrets in decompiled APK source.
All patterns are written for `ripgrep` (`rg`). Replace `rg` with `grep -rP` if ripgrep is unavailable.

Run all searches against both the `jadx_out/` and `apktool_out/` directories.

---

## Usage

```bash
SOURCES="$WORKDIR/jadx_out $WORKDIR/apktool_out"
```

---

## Section 1 — Cloud Provider Keys

### 1.1 Google / GCP

| Pattern | Severity | Command |
|---|---|---|
| Google API Key | Critical | `rg -o 'AIza[0-9A-Za-z\-_]{35}' $SOURCES` |
| GCP Service Account JSON | Critical | `rg -l '"type"\s*:\s*"service_account"' $SOURCES` |
| GCP Private Key ID | Critical | `rg -o '"private_key_id"\s*:\s*"[a-f0-9]+"' $SOURCES` |
| Google OAuth client secret | High | `rg -in 'client_secret.*[0-9A-Za-z\-_]{20,}' $SOURCES` |

```bash
# Full GCP sweep
rg -o 'AIza[0-9A-Za-z\-_]{35}' $SOURCES
rg -l '"type"\s*:\s*"service_account"' $SOURCES
rg -o '"private_key_id"\s*:\s*"[a-f0-9]+"' $SOURCES
rg -in 'client_secret\s*[=:]\s*["\x27][^\s"]{10,}' $SOURCES
```

### 1.2 Amazon Web Services (AWS)

| Pattern | Severity | Notes |
|---|---|---|
| AWS Access Key ID | Critical | Starts with `AKIA` (long-term) or `ASIA` (temp) |
| AWS Secret Access Key | Critical | 40-char base64-like string paired with access key |
| AWS Session Token | Critical | Very long base64 string |

```bash
# AWS Access Key ID
rg -o '\bAKIA[0-9A-Z]{16}\b' $SOURCES
rg -o '\bASIA[0-9A-Z]{16}\b' $SOURCES

# AWS Secret Access Key (often near the access key ID)
rg -in 'aws[_\-]?secret[_\-]?access[_\-]?key\s*[=:]\s*["\x27]?[A-Za-z0-9/+=]{40}' $SOURCES

# Generic AWS credential patterns
rg -in 'aws_access_key_id\s*[=:]' $SOURCES
rg -in 'aws_session_token\s*[=:]' $SOURCES

# S3 bucket URLs (not secrets, but surface mapping)
rg -o 's3://[a-z0-9\-\.]+' $SOURCES
rg -o 'https://[a-z0-9\-\.]+\.s3\.amazonaws\.com' $SOURCES
```

### 1.3 Azure

```bash
# Azure Storage connection string
rg -o 'DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]+' $SOURCES

# Azure SAS token
rg -o 'sv=[0-9\-]+&s[A-Za-z]=[a-zA-Z]+&[A-Za-z0-9%=&]+' $SOURCES

# Azure client secret
rg -in 'AZURE_CLIENT_SECRET\s*[=:]\s*["\x27]?[^\s"]{10,}' $SOURCES

# Azure subscription / tenant IDs
rg -o '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' $SOURCES | head -20
```

---

## Section 2 — Firebase & Google Mobile Services

```bash
# Firebase Realtime Database URL
rg -o 'https://[a-z0-9\-]+\.firebaseio\.com' $SOURCES

# Firebase project ID
rg -o '"project_id"\s*:\s*"[a-z0-9\-]+"' $SOURCES

# Firebase Storage bucket
rg -o '"storage_bucket"\s*:\s*"[a-z0-9\-]+\.appspot\.com"' $SOURCES

# Firebase API key (google-services.json)
rg -o '"api_key"\s*:\s*\[.*?"value"\s*:\s*"[^"]+"' $SOURCES

# Full google-services.json parse
cat "$WORKDIR/raw/assets/google-services.json" 2>/dev/null | grep -E '"api_key|project_id|firebase_url|storage_bucket|mobilesdk_app_id"'

# Firebase server key (legacy cloud messaging)
rg -o 'AAAA[A-Za-z0-9_\-]{7}:[A-Za-z0-9_\-]{140}' $SOURCES
```

---

## Section 3 — Payment Processors

### 3.1 Stripe

```bash
# Secret key (never in mobile apps)
rg -o 'sk_(test|live)_[0-9a-zA-Z]{24,}' $SOURCES

# Publishable key (acceptable in mobile, but note exposure)
rg -o 'pk_(test|live)_[0-9a-zA-Z]{24,}' $SOURCES

# Restricted key
rg -o 'rk_(test|live)_[0-9a-zA-Z]{24,}' $SOURCES
```

### 3.2 PayPal / Braintree

```bash
rg -in 'braintree[_\-]?(token|key|secret)\s*[=:]' $SOURCES
rg -in 'paypal[_\-]?(client[_\-]?secret|token)\s*[=:]' $SOURCES
```

### 3.3 Square

```bash
rg -o 'sq0[a-z]{3}-[0-9A-Za-z\-_]{22,}' $SOURCES
```

---

## Section 4 — Communication & Collaboration Services

### 4.1 Twilio

```bash
# Account SID
rg -o 'AC[a-f0-9]{32}' $SOURCES

# Auth token
rg -o '[a-f0-9]{32}' $SOURCES  # combined with nearby "TWILIO" or "auth_token"
rg -in 'twilio.*auth[_\-]?token\s*[=:]' $SOURCES

# API key
rg -o 'SK[0-9a-fA-F]{32}' $SOURCES
```

### 4.2 SendGrid

```bash
rg -o 'SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43}' $SOURCES
```

### 4.3 Mailgun

```bash
rg -o 'key-[0-9a-f]{32}' $SOURCES
```

### 4.4 Slack

```bash
# Webhook
rg -o 'https://hooks\.slack\.com/services/T[A-Za-z0-9_]+/B[A-Za-z0-9_]+/[A-Za-z0-9_]+' $SOURCES

# Bot/API token
rg -o 'xox[baprs]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}' $SOURCES
rg -o 'xoxb-[0-9\-]+' $SOURCES
```

### 4.5 Discord

```bash
rg -o 'https://discord(app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9\-_]+' $SOURCES
```

---

## Section 5 — Source Control & CI/CD

### 5.1 GitHub

```bash
# Personal access token (classic)
rg -o 'ghp_[A-Za-z0-9]{36}' $SOURCES

# OAuth token
rg -o 'gho_[A-Za-z0-9]{36}' $SOURCES

# GitHub App token
rg -o 'ghu_[A-Za-z0-9]{36}' $SOURCES
rg -o 'ghs_[A-Za-z0-9]{36}' $SOURCES
rg -o 'ghr_[A-Za-z0-9]{36}' $SOURCES
```

### 5.2 GitLab

```bash
rg -o 'glpat-[A-Za-z0-9\-_]{20}' $SOURCES
```

### 5.3 CircleCI / Travis / Jenkins

```bash
rg -in 'CIRCLE_TOKEN\s*[=:]|TRAVIS.*TOKEN\s*[=:]|JENKINS.*TOKEN\s*[=:]' $SOURCES
```

---

## Section 6 — Generic Credential Patterns

These catch hardcoded passwords and secrets that don't match a specific service pattern.

```bash
# Generic API key assignments
rg -in 'api[_\-]?key\s*[=:]\s*["\x27][A-Za-z0-9_\-]{8,}' $SOURCES

# Passwords
rg -in '(password|passwd|pwd)\s*[=:]\s*["\x27][^"\x27\s]{4,}' $SOURCES

# Secrets
rg -in '(secret|client[_\-]?secret)\s*[=:]\s*["\x27][^"\x27\s]{8,}' $SOURCES

# Auth tokens
rg -in '(auth[_\-]?token|access[_\-]?token|bearer[_\-]?token)\s*[=:]\s*["\x27][^"\x27\s]{8,}' $SOURCES

# JWT secrets (signing keys hardcoded)
rg -in 'jwt[_\-]?secret\s*[=:]\s*["\x27][^"\x27\s]{8,}' $SOURCES

# Encryption keys
rg -in '(encryption[_\-]?key|encrypt[_\-]?key|aes[_\-]?key)\s*[=:]\s*["\x27][^"\x27\s]{8,}' $SOURCES
```

---

## Section 7 — Cryptographic Material

```bash
# PEM private keys
rg -l 'BEGIN RSA PRIVATE KEY|BEGIN PRIVATE KEY|BEGIN EC PRIVATE KEY|BEGIN DSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY' $SOURCES

# Certificates embedded in code
rg -l 'BEGIN CERTIFICATE' $SOURCES

# Certificate files
find "$WORKDIR" -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.pfx" -o -name "*.jks" -o -name "*.bks" 2>/dev/null

# Base64-encoded keys (common obfuscation technique)
rg -n 'Base64\.decode\("[A-Za-z0-9+/=]{40,}"' $SOURCES
```

---

## Section 8 — Database Connection Strings

```bash
rg -o 'jdbc:[a-z]+://[^\s"<>]+' $SOURCES
rg -o 'mongodb(\+srv)?://[^\s"<>]+' $SOURCES
rg -o 'postgres(ql)?://[^\s"<>]+' $SOURCES
rg -o 'mysql://[^\s"<>]+' $SOURCES
rg -o 'redis://[^\s"<>]+' $SOURCES
rg -o 'amqp://[^\s"<>]+' $SOURCES
rg -o 'sqlite://[^\s"<>]+' $SOURCES
```

---

## Section 9 — Native Library String Extraction

```bash
find "$WORKDIR/raw/lib" -name "*.so" 2>/dev/null | while read lib; do
  echo "=== Scanning: $(basename $lib) ==="
  strings "$lib" | grep -iE \
    'api.?key|secret|token|password|authorization|bearer|basic |client.?id|private.?key|aws|gcp|azure|firebase|stripe|twilio' \
    | grep -v '^\s*$' \
    | head -30
  echo ""
done
```

---

## Section 10 — Config & Asset Files

```bash
# Scan all config-like files in assets
find "$WORKDIR/raw/assets" "$WORKDIR/apktool_out/assets" "$WORKDIR/apktool_out/res/raw" -type f 2>/dev/null \
  \( -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.xml" \
     -o -name "*.properties" -o -name "*.env" -o -name "*.cfg" \
     -o -name "*.conf" -o -name "*.ini" -o -name "*.toml" \) \
  | while read f; do
    HITS=$(grep -iE 'key|secret|token|password|endpoint|url|host|credential' "$f" | grep -v '^\s*#' | head -10)
    if [ -n "$HITS" ]; then
      echo "=== $f ==="
      echo "$HITS"
      echo ""
    fi
  done
```

---

## Severity Classification

| Severity | Criteria |
|---|---|
| **Critical** | Active cloud credentials, payment secret keys, private cryptographic keys — immediate account compromise or data breach possible |
| **High** | Service tokens, webhook URLs, OAuth client secrets — significant abuse potential |
| **Medium** | Staging/test credentials, internal API keys with limited scope |
| **Low** | Publishable keys (by design public), analytics IDs, non-sensitive config values |
| **Info** | Internal hostnames, non-sensitive metadata, debug-only keys clearly scoped |

---

## False Positive Reduction

Before reporting a finding:

1. **Confirm the value is non-empty and non-placeholder** — skip `YOUR_API_KEY_HERE`, `REPLACE_ME`, `TODO`
2. **Check if it is used in a test class** — `src/test/`, `androidTest/`, classes named `*Test`, `*Mock`
3. **Confirm the key is active** — where possible, attempt a lightweight validation (e.g., a public read-only API call)
4. **Publishable keys** — Stripe `pk_`, Google Maps API keys for Android — note them as info if they are restricted to the app package
