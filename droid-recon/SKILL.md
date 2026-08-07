---
name: droid-recon
description: Full static analysis methodology for Android APK files on Linux — decompiles with apktool and jadx, hunts for hardcoded secrets and API keys, maps endpoints and network surface, fingerprints the tech stack, detects vulnerability patterns, and produces a structured Markdown report aligned to OWASP MASVS. Trigger when the user provides an APK file and asks for a security review, secret scan, endpoint extraction, or mobile pentest.
license: MIT
metadata:
  version: "1.0.0"
  author: community
  tags: ["mobile", "android", "apk", "static-analysis", "reverse-engineering", "secrets", "recon"]
---

# Droid Recon — Android APK Static Analysis

A structured static analysis methodology for Android APK files using Linux command-line tools. No emulator, no device, no dynamic instrumentation required — pure static.

When this skill is active, follow every phase in order. Do not skip phases. Run each command, collect output, and build the final Markdown report incrementally.

---

## Pre-flight: Tool Check

Before starting, verify required tools are available:

```bash
for tool in apktool jadx strings grep rg keytool openssl unzip file binwalk; do
  command -v $tool && echo "$tool OK" || echo "$tool MISSING"
done
```

If `jadx` is not found, try `jadx-cli`. If `rg` (ripgrep) is not found, fall back to `grep -r`.

Install missing tools if possible:
```bash
# apktool
sudo apt install apktool

# jadx (Debian/Kali)
sudo apt install jadx

# ripgrep
sudo apt install ripgrep

# binwalk
sudo apt install binwalk
```

Inform the user of any tools that could not be installed and note which phases will be skipped or degraded.

---

## Setup: Create Working Directory

```bash
APK="<path to APK provided by user>"
WORKDIR="/tmp/droid-recon/$(basename $APK .apk)"
mkdir -p "$WORKDIR"/{apktool_out,jadx_out,raw}

echo "Working directory: $WORKDIR"
echo "APK: $APK"
```

Use `$WORKDIR`, `$APK` as variables throughout all subsequent phases.

---

## Phase 0 — Decompile

Run both decompilers in sequence. Both are required — apktool provides smali, resources, and the decoded AndroidManifest.xml; jadx provides readable Java/Kotlin source for deep inspection.

### 0.1 apktool (smali + resources + manifest)

```bash
apktool d -f -o "$WORKDIR/apktool_out" "$APK"
```

Expected output: `$WORKDIR/apktool_out/AndroidManifest.xml`, smali classes, `res/`, `assets/`.

### 0.2 jadx (Java/Kotlin source)

```bash
jadx -d "$WORKDIR/jadx_out" "$APK" 2>&1 | tail -5
# If jadx not available:
jadx-cli -d "$WORKDIR/jadx_out" "$APK" 2>&1 | tail -5
```

Expected output: `$WORKDIR/jadx_out/sources/` with decompiled Java/Kotlin.

### 0.3 Raw unpack (assets, native libs, raw resources)

```bash
unzip -o "$APK" -d "$WORKDIR/raw" > /dev/null
```

This exposes `lib/`, `assets/`, `META-INF/`, `classes.dex`, and any bundled files.

---

## Phase 1 — APK Info & Signing Certificate

Collect baseline information about the APK.

### 1.1 Package metadata

Extract from decoded manifest:

```bash
grep -E 'package=|versionName=|versionCode=' "$WORKDIR/apktool_out/AndroidManifest.xml" | head -5
grep -E 'minSdkVersion|targetSdkVersion' "$WORKDIR/apktool_out/apktool.yml"
```

### 1.2 DEX file info

```bash
ls -lh "$WORKDIR/raw/"*.dex 2>/dev/null
file "$WORKDIR/raw/"*.dex 2>/dev/null
```

Multiple DEX files (`classes2.dex`, `classes3.dex`) indicate multidex — larger attack surface.

### 1.3 Signing certificate

```bash
unzip -p "$APK" META-INF/*.RSA 2>/dev/null | keytool -printcert -v 2>/dev/null || \
unzip -p "$APK" META-INF/*.DSA 2>/dev/null | keytool -printcert -v 2>/dev/null
```

Flag if: debug certificate, self-signed with `CN=Android Debug`, or expired cert.

### 1.4 Native libraries

```bash
find "$WORKDIR/raw/lib" -name "*.so" 2>/dev/null | sort
```

Note architectures present (`armeabi-v7a`, `arm64-v8a`, `x86`, `x86_64`).

### 1.5 Assets and raw resources

```bash
ls -lah "$WORKDIR/raw/assets/" 2>/dev/null
ls -lah "$WORKDIR/apktool_out/res/raw/" 2>/dev/null
```

Flag any unexpected files: `.json`, `.db`, `.sqlite`, `.key`, `.pem`, `.p12`, `.env`, config files.

---

## Phase 2 — Manifest Analysis

The AndroidManifest.xml is the single highest-value file in any APK. Analyze every security-relevant attribute.

### 2.1 Global application flags

```bash
MANIFEST="$WORKDIR/apktool_out/AndroidManifest.xml"

grep -n 'android:debuggable'           "$MANIFEST"
grep -n 'android:allowBackup'          "$MANIFEST"
grep -n 'usesCleartextTraffic'         "$MANIFEST"
grep -n 'networkSecurityConfig'        "$MANIFEST"
grep -n 'android:extractNativeLibs'    "$MANIFEST"
grep -n 'android:requestLegacyExternalStorage' "$MANIFEST"
```

**Flag as critical:**
- `android:debuggable="true"` — app can be attached to with adb and debugged
- `android:allowBackup="true"` — app data can be extracted via `adb backup` without root
- `android:usesCleartextTraffic="true"` — plaintext HTTP is permitted

### 2.2 Exported components

Exported components are reachable by any other app on the device without permission.

```bash
echo "=== Exported Activities ==="
grep -n -A5 '<activity' "$MANIFEST" | grep -E 'android:name|exported="true"'

echo "=== Exported Services ==="
grep -n -A5 '<service' "$MANIFEST" | grep -E 'android:name|exported="true"'

echo "=== Exported Receivers ==="
grep -n -A5 '<receiver' "$MANIFEST" | grep -E 'android:name|exported="true"'

echo "=== Exported Providers ==="
grep -n -A5 '<provider' "$MANIFEST" | grep -E 'android:name|exported="true"|android:permission|readPermission|writePermission'
```

For each exported component, note whether a `android:permission` is set. Exported without permission = attackable from any other app.

### 2.3 Intent filters on exported components

Components with `<intent-filter>` are implicitly exported (pre-Android 12 apps with `targetSdk < 31`). List all intent filters:

```bash
grep -n -B2 '<intent-filter>' "$MANIFEST"
```

### 2.4 Deep link schemes

```bash
grep -n 'android:scheme' "$MANIFEST"
```

Deep link schemes without signature verification can be hijacked by malicious apps.

### 2.5 Permissions

```bash
echo "=== Declared permissions ==="
grep -n 'uses-permission' "$MANIFEST" | grep -oP 'android:name="[^"]+"'

echo "=== Custom permissions ==="
grep -n '<permission ' "$MANIFEST"
```

Flag dangerous permissions: `RECORD_AUDIO`, `READ_CONTACTS`, `ACCESS_FINE_LOCATION`, `READ_CALL_LOG`, `READ_SMS`, `CAMERA`, `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `RECEIVE_SMS`, `PROCESS_OUTGOING_CALLS`.

### 2.6 Network security config

If `networkSecurityConfig` is present, inspect the referenced file:

```bash
NSC_FILE=$(grep -oP 'networkSecurityConfig="@xml/[^"]+' "$MANIFEST" | cut -d'/' -f2)
cat "$WORKDIR/apktool_out/res/xml/${NSC_FILE}.xml" 2>/dev/null
```

Flag:
- `<trust-anchors>` including `<certificates src="user"/>` — user-installed CAs trusted (certificate pinning bypassable)
- `<domain-config cleartextTrafficPermitted="true">` on production domains
- `<debug-overrides>` should not be in production builds

---

## Phase 3 — Secret & Key Hunting

Run all pattern searches against both `jadx_out/` (Java source) and `apktool_out/` (smali + resources + assets). This is the most impactful phase.

Use the full pattern list in `references/secret-patterns.md`.

### 3.1 Setup search targets

```bash
SOURCES="$WORKDIR/jadx_out $WORKDIR/apktool_out"
```

### 3.2 API key patterns

```bash
# Generic API keys
rg -in 'api[_-]?key\s*[=:]\s*["\x27][^\s"]{8,}' $SOURCES

# Google services
rg -o 'AIza[0-9A-Za-z\-_]{35}' $SOURCES
rg -o '"type"\s*:\s*"service_account"' $SOURCES

# AWS
rg -o 'AKIA[0-9A-Z]{16}' $SOURCES
rg -in 'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\x27][A-Za-z0-9/+]{40}' $SOURCES

# Stripe
rg -o '(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}' $SOURCES

# Twilio
rg -o 'SK[0-9a-fA-F]{32}' $SOURCES

# SendGrid
rg -o 'SG\.[a-zA-Z0-9\-_]{22}\.[a-zA-Z0-9\-_]{43}' $SOURCES

# GitHub tokens
rg -o 'ghp_[A-Za-z0-9]{36}' $SOURCES
rg -o 'gho_[A-Za-z0-9]{36}' $SOURCES

# Slack webhooks
rg -o 'https://hooks\.slack\.com/services/T[A-Za-z0-9]+/B[A-Za-z0-9]+/[A-Za-z0-9]+' $SOURCES

# Discord webhooks
rg -o 'https://discord(app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9\-_]+' $SOURCES
```

### 3.3 Hardcoded credentials

```bash
rg -in '(password|passwd|pwd)\s*[=:]\s*["\x27][^"\x27\s]{4,}' $SOURCES
rg -in '(secret|token)\s*[=:]\s*["\x27][^"\x27\s]{8,}' $SOURCES
rg -in 'client[_-]?secret\s*[=:]\s*["\x27][^"\x27\s]+' $SOURCES
rg -in 'auth[_-]?token\s*[=:]\s*["\x27][^"\x27\s]+' $SOURCES
```

### 3.4 Private keys and certificates

```bash
rg -l 'BEGIN RSA PRIVATE KEY|BEGIN PRIVATE KEY|BEGIN EC PRIVATE KEY|BEGIN CERTIFICATE' $SOURCES
find "$WORKDIR/raw/assets" -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.pfx" -o -name "*.jks" -o -name "*.bks" 2>/dev/null
```

### 3.5 Firebase & cloud

```bash
# Firebase project config
rg -o '"project_id"\s*:\s*"[^"]+"' $SOURCES
rg -o '"firebase_url"\s*:\s*"[^"]+"' $SOURCES
cat "$WORKDIR/raw/assets/google-services.json" 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -E 'project_id|api_key|app_id|database_url|storage_bucket'

# Azure
rg -in 'DefaultEndpointsProtocol=https;AccountName=' $SOURCES

# GCP
rg -o '"private_key_id"\s*:\s*"[^"]+"' $SOURCES
```

### 3.6 Database connection strings

```bash
rg -o 'jdbc:[a-z]+://[^\s"<]+' $SOURCES
rg -o 'mongodb(\+srv)?://[^\s"<]+' $SOURCES
rg -o 'postgres(ql)?://[^\s"<]+' $SOURCES
rg -o 'mysql://[^\s"<]+' $SOURCES
rg -o 'redis://[^\s"<]+' $SOURCES
```

### 3.7 Strings from native libraries

```bash
find "$WORKDIR/raw/lib" -name "*.so" 2>/dev/null | while read lib; do
  echo "=== $lib ==="
  strings "$lib" | grep -E 'https?://|api[_-]?key|secret|token|password|Authorization|Bearer' | head -20
done
```

### 3.8 Config files in assets

```bash
for f in $(find "$WORKDIR/raw/assets" "$WORKDIR/apktool_out/assets" -type f 2>/dev/null); do
  case "$f" in
    *.json|*.yaml|*.yml|*.xml|*.properties|*.env|*.cfg|*.conf|*.ini)
      echo "=== $f ==="
      cat "$f" | grep -iE 'key|secret|token|password|endpoint|url|host' | head -20
      ;;
  esac
done
```

**Output of Phase 3:** A table of all discovered secrets:

| Type | File | Line | Value (truncated) | Severity |
|---|---|---|---|---|
| AWS Access Key | src/com/app/Config.java | 42 | AKIA************ | Critical |

---

## Phase 4 — Endpoint & Network Surface Mapping

### 4.1 All HTTP/HTTPS URLs

```bash
rg -oh 'https?://[a-zA-Z0-9._/:%?=&@#~\-]+' $SOURCES | sort -u | grep -v '^\s*$'
```

### 4.2 WebSocket endpoints

```bash
rg -oh 'wss?://[a-zA-Z0-9._/:%?=&@#~\-]+' $SOURCES | sort -u
```

### 4.3 IP addresses (potential internal services)

```bash
rg -oh '\b(?:10\.|192\.168\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)\d{1,3}\.\d{1,3}\b' $SOURCES | sort -u
rg -oh '\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?\b' $SOURCES | sort -u
```

Flag RFC1918 addresses — indicate internal infrastructure exposure.

### 4.4 Deep link schemes

```bash
grep -oP 'android:scheme="[^"]+"' "$WORKDIR/apktool_out/AndroidManifest.xml" | sort -u
grep -oP 'android:host="[^"]+"' "$WORKDIR/apktool_out/AndroidManifest.xml" | sort -u
```

### 4.5 GraphQL

```bash
rg -in 'graphql|/graphql|__schema|mutation\s+\{|query\s+\{' $SOURCES | head -20
```

### 4.6 Retrofit / OkHttp base URLs

```bash
rg -in 'baseUrl|BASE_URL|OkHttpClient|Retrofit\.Builder' $SOURCES | head -20
```

### 4.7 Categorize endpoints

Group discovered URLs by:
- **Production API** — `api.`, `/api/v`, `/v1/`, `/v2/`
- **Staging/Dev** — `staging.`, `dev.`, `test.`, `localhost`, `127.0.0.1`
- **Third-party services** — Google, Firebase, AWS, Sentry, analytics
- **Internal/Private** — RFC1918 IPs, `.internal`, `.local`

---

## Phase 5 — Stack & Library Fingerprinting

### 5.1 Framework detection

```bash
# React Native
ls "$WORKDIR/raw/assets/index.android.bundle" 2>/dev/null && echo "React Native detected"

# Flutter
ls "$WORKDIR/raw/assets/flutter_assets" 2>/dev/null && echo "Flutter detected"
ls "$WORKDIR/raw/lib/arm64-v8a/libflutter.so" 2>/dev/null && echo "Flutter native lib detected"

# Xamarin
ls "$WORKDIR/raw/assemblies" 2>/dev/null && echo "Xamarin detected"

# Cordova / Ionic
ls "$WORKDIR/raw/assets/www/cordova.js" 2>/dev/null && echo "Cordova/Ionic detected"

# Unity
find "$WORKDIR/raw/lib" -name "libunity.so" 2>/dev/null && echo "Unity detected"
```

### 5.2 Networking libraries

```bash
rg -l 'okhttp3|com\.squareup\.okhttp' $SOURCES && echo "OkHttp detected"
rg -l 'retrofit2|com\.squareup\.retrofit' $SOURCES && echo "Retrofit detected"
rg -l 'com\.android\.volley' $SOURCES && echo "Volley detected"
rg -l 'io\.ktor' $SOURCES && echo "Ktor detected"
```

### 5.3 Authentication & Identity

```bash
rg -l 'com\.google\.firebase\.auth|FirebaseAuth' $SOURCES && echo "Firebase Auth"
rg -l 'auth0\.android|com\.auth0' $SOURCES && echo "Auth0"
rg -l 'com\.okta\.oidc|OktaBuilder' $SOURCES && echo "Okta"
rg -l 'com\.amazonaws\.mobile\.client|CognitoUserPool' $SOURCES && echo "AWS Cognito"
```

### 5.4 Storage & databases

```bash
rg -l 'androidx\.room|RoomDatabase' $SOURCES && echo "Room (SQLite ORM)"
rg -l 'io\.realm\.Realm' $SOURCES && echo "Realm DB"
rg -l 'net\.sqlcipher|SQLiteDatabase' $SOURCES && echo "SQLite"
rg -l 'SharedPreferences' $SOURCES && echo "SharedPreferences"
```

### 5.5 Crash reporting & analytics

```bash
rg -l 'com\.google\.firebase\.crashlytics|FirebaseCrashlytics' $SOURCES && echo "Firebase Crashlytics"
rg -l 'io\.sentry|SentryAndroid' $SOURCES && echo "Sentry"
rg -l 'com\.datadog\.android' $SOURCES && echo "Datadog"
rg -l 'com\.mixpanel\.android' $SOURCES && echo "Mixpanel"
rg -l 'com\.amplitude\.android' $SOURCES && echo "Amplitude"
rg -l 'com\.appsflyer' $SOURCES && echo "AppsFlyer"
```

### 5.6 Payment SDKs

```bash
rg -l 'com\.stripe\.android|StripeClient' $SOURCES && echo "Stripe"
rg -l 'com\.braintreepayments' $SOURCES && echo "Braintree"
rg -l 'com\.paypal\.android' $SOURCES && echo "PayPal"
rg -l 'com\.google\.android\.gms\.wallet' $SOURCES && echo "Google Pay"
```

### 5.7 Native library strings

```bash
find "$WORKDIR/raw/lib" -name "*.so" 2>/dev/null | while read lib; do
  LIBNAME=$(basename "$lib")
  IDENTIFIED=$(strings "$lib" | grep -oE '(openssl|libssh|libcurl|boringssl|conscrypt)' | sort -u | tr '\n' ',')
  [ -n "$IDENTIFIED" ] && echo "$LIBNAME: $IDENTIFIED"
done
```

---

## Phase 6 — Vulnerability Pattern Detection

Map each finding to the OWASP MASVS category. Reference `references/owasp-mobile-top10.md` for category descriptions and remediation guidance.

### 6.1 Insecure WebView (MASVS-PLATFORM-2)

```bash
echo "--- JavaScript enabled ---"
rg -n 'setJavaScriptEnabled\(true\)' $SOURCES

echo "--- JavaScript interface exposed ---"
rg -n 'addJavascriptInterface' $SOURCES

echo "--- File access enabled ---"
rg -n 'setAllowFileAccess\(true\)|setAllowFileAccessFromFileURLs\(true\)|setAllowUniversalAccessFromFileURLs\(true\)' $SOURCES

echo "--- WebView loading URLs from Intent ---"
rg -n -A5 'getIntent.*getStringExtra|getIntent.*getData' $SOURCES | grep -A3 'WebView\|loadUrl'
```

Flag any `addJavascriptInterface` combined with `setJavaScriptEnabled(true)` — remote code execution risk if any WebView loads attacker-controlled URLs.

### 6.2 Weak cryptography (MASVS-CRYPTO-1)

```bash
echo "--- Weak algorithms ---"
rg -n '"MD5"|"SHA-1"|"DES"|"RC4"|"RC2"|"Blowfish"' $SOURCES
rg -n '"AES/ECB"|"DES/ECB"' $SOURCES

echo "--- Hardcoded IV ---"
rg -n 'IvParameterSpec\|new byte\[\]\s*{' $SOURCES | head -20

echo "--- Insecure random ---"
rg -n 'new\s+Random\(\)|java\.util\.Random' $SOURCES
rg -n 'Math\.random\(\)' $SOURCES

echo "--- Hardcoded key material ---"
rg -n 'SecretKeySpec|KeySpec' $SOURCES | head -20
```

### 6.3 Insecure data storage (MASVS-STORAGE-1)

```bash
echo "--- World-readable/writable files ---"
rg -n 'MODE_WORLD_READABLE|MODE_WORLD_WRITEABLE' $SOURCES

echo "--- External storage usage ---"
rg -n 'getExternalStorageDirectory|getExternalFilesDir|Environment\.DIRECTORY' $SOURCES

echo "--- Unencrypted SharedPreferences storing sensitive data ---"
rg -n -A5 'getSharedPreferences\|edit\(\)' $SOURCES | grep -iE 'password|token|key|secret|pin|card'

echo "--- Unencrypted SQLite ---"
rg -n 'openOrCreateDatabase\|SQLiteOpenHelper' $SOURCES
rg -l 'sqlcipher' $SOURCES > /dev/null || echo "No SQLCipher found — SQLite databases may be unencrypted"

echo "--- Logging sensitive data ---"
rg -n -i 'Log\.[dDeEiIvVwW]\s*\([^)]*(?:password|token|secret|key|card|ssn|email|pin)' $SOURCES
```

### 6.4 Insecure network communication (MASVS-NETWORK-1)

```bash
echo "--- HTTP (not HTTPS) URLs ---"
rg -oh 'http://[a-zA-Z0-9._/:%?=&@#~\-]+' $SOURCES | grep -v 'http://schemas\|http://www\.w3\|http://xmlns\|http://localhost' | sort -u

echo "--- SSL pinning disabled / hostname verification bypassed ---"
rg -n 'ALLOW_ALL_HOSTNAME_VERIFIER\|NullHostnameVerifier\|getInsecure\|TrustAllCerts\|X509TrustManager' $SOURCES
rg -n 'onReceivedSslError.*proceed\(\)' $SOURCES

echo "--- Custom TrustManager ---"
rg -n 'implements X509TrustManager\|checkClientTrusted\|checkServerTrusted' $SOURCES | head -20
```

### 6.5 Authentication & session (MASVS-AUTH-1)

```bash
echo "--- Hardcoded credentials in auth flows ---"
rg -in -B2 -A2 'authenticate|login|signin' $SOURCES | grep -iE 'password\s*=|password\s*:' | head -20

echo "--- Biometric bypass risk ---"
rg -n 'onAuthenticationFailed\|onAuthenticationError\|BiometricPrompt' $SOURCES

echo "--- Token stored in SharedPreferences (unencrypted) ---"
rg -n -A2 'putString.*token\|putString.*auth\|putString.*jwt' $SOURCES
```

### 6.6 Code quality & reverse engineering resistance (MASVS-RESILIENCE)

```bash
echo "--- Dynamic code loading ---"
rg -n 'DexClassLoader\|PathClassLoader\|InMemoryDexClassLoader\|loadClass' $SOURCES | head -20

echo "--- Reflection usage ---"
rg -n 'java\.lang\.reflect\|Class\.forName\|getDeclaredMethod\|getDeclaredField' $SOURCES | head -20

echo "--- Root detection present? ---"
rg -in 'isRooted\|detectRoot\|RootBeer\|/system/app/Superuser\|/sbin/su\|/system/bin/su' $SOURCES

echo "--- Emulator detection present? ---"
rg -in 'isEmulator\|Build\.FINGERPRINT.*generic\|android\.os\.Build\.PRODUCT.*sdk' $SOURCES

echo "--- Anti-tamper / integrity checks? ---"
rg -in 'getPackageInfo.*signatures\|GET_SIGNATURES\|SigningInfo\|apkSigner' $SOURCES

echo "--- Obfuscation detection (ProGuard/R8 applied?) ---"
ls "$WORKDIR/apktool_out/smali/"* 2>/dev/null | head -5
```

If class names are single letters (`a.smali`, `b.smali`), obfuscation is likely applied.

### 6.7 Intent security (MASVS-PLATFORM-1)

```bash
echo "--- Implicit intents sending sensitive data ---"
rg -n 'new Intent\(\)\|Intent\.ACTION_' $SOURCES | head -20

echo "--- PendingIntent without immutability flag (pre-API31 risk) ---"
rg -n 'PendingIntent\.getActivity\|PendingIntent\.getBroadcast' $SOURCES | head -20

echo "--- Tapjacking protection ---"
rg -n 'filterTouchesWhenObscured\|FLAG_WINDOW_IS_OBSCURED' $SOURCES
```

### 6.8 Backup & debug artifacts

```bash
echo "--- Test/debug code left in build ---"
rg -in 'BuildConfig\.DEBUG\|if\s*\(debug\)\|println\|System\.out\.print' $SOURCES | head -20

echo "--- TODO / FIXME / HACK comments with security relevance ---"
rg -in 'TODO.*(?:security|auth|token|key|fix|hack|workaround)\|FIXME.*(?:security|auth|token|key)' $SOURCES | head -20

echo "--- Test credentials or test endpoints ---"
rg -in 'test.*password\|dummy.*key\|fake.*token\|example\.com\|localhost\|127\.0\.0\.1' $SOURCES | head -20
```

---

## Phase 7 — Output: Structured Markdown Report

Produce the following report. Fill every section with findings from Phases 0–6. Do not omit empty sections — write "None found" if a section has no findings.

```markdown
# Droid Recon Report

**APK:** `<filename>`
**Package:** `<com.example.app>`
**Version:** `<1.2.3>` (build `<456>`)
**Min SDK:** `<21>` (Android 5.0) | **Target SDK:** `<34>` (Android 14)
**Signing:** `<debug / release>` — `<issuer CN>`
**Analysis date:** `<YYYY-MM-DD>`

---

## Risk Summary

| Category | Findings | Highest Severity |
|---|---|---|
| Hardcoded Secrets | N | Critical / High / Medium / Low |
| Manifest Issues | N | ... |
| Insecure Network | N | ... |
| Weak Cryptography | N | ... |
| Insecure Storage | N | ... |
| WebView Issues | N | ... |
| Code Quality | N | ... |
| **Total** | **N** | **Critical / High / ...** |

**Overall Risk Rating:** [Critical / High / Medium / Low]

---

## 1. APK Info & Certificate

| Property | Value |
|---|---|
| Package name | |
| Version | |
| Min SDK | |
| Target SDK | |
| DEX count | |
| Native libs | |
| Signing cert issuer | |
| Cert validity | |

**Certificate flags:** [DEBUG CERT DETECTED / Release cert / Expired]

---

## 2. Manifest Findings

### 2.1 Dangerous Application Flags

| Flag | Value | Risk |
|---|---|---|
| android:debuggable | true/false | Critical if true |
| android:allowBackup | true/false | High if true |
| usesCleartextTraffic | true/false | High if true |

### 2.2 Exported Components

| Component | Name | Permission | Risk |
|---|---|---|---|
| Activity | com.app.DeepLinkActivity | none | High |

### 2.3 Dangerous Permissions

- `android.permission.READ_CONTACTS`
- `android.permission.RECORD_AUDIO`
- ...

### 2.4 Network Security Config

[Findings or "Default config — no custom NSC"]

---

## 3. Hardcoded Secrets

| Type | File | Line | Value (truncated) | MASVS | Severity |
|---|---|---|---|---|---|
| Google API Key | src/Config.java | 42 | AIzaSy****** | MASVS-STORAGE-2 | Critical |

---

## 4. Endpoints & Network Surface

### 4.1 Production Endpoints

- `https://api.example.com/v2/users`
- ...

### 4.2 Staging / Development Endpoints

- `http://dev.internal.example.com/api`
- ...

### 4.3 Third-Party Services

- Firebase: `https://example-default-rtdb.firebaseio.com`
- ...

### 4.4 Internal / Private Addresses

- `http://192.168.1.100:8080` — internal server exposed in code

---

## 5. Tech Stack

| Layer | Technology |
|---|---|
| Framework | Native Android / React Native / Flutter |
| Networking | OkHttp 4.x, Retrofit 2.x |
| Auth | Firebase Auth |
| Storage | Room, SharedPreferences |
| Analytics | Firebase Crashlytics, Sentry |
| Payment | Stripe |
| Native libs | libssl.so, libcrypto.so |

---

## 6. Vulnerability Findings

| # | Title | File / Location | MASVS | OWASP Mobile | Severity |
|---|---|---|---|---|---|
| 1 | JavaScript enabled in WebView | ui/WebActivity.java:88 | MASVS-PLATFORM-2 | M1 | High |
| 2 | Weak cipher: AES/ECB | crypto/Encryptor.java:34 | MASVS-CRYPTO-1 | M5 | High |
| 3 | SSL verification bypassed | net/Client.java:112 | MASVS-NETWORK-1 | M3 | Critical |

### Detailed Findings

For each finding above, provide:

**[#N] Title**
- **Location:** file:line
- **Evidence:** code snippet or grep output
- **Impact:** what an attacker can do
- **MASVS:** MASVS-X-Y
- **OWASP Mobile:** MX — Category name
- **Remediation:** specific fix guidance (reference `references/owasp-mobile-top10.md` for full remediation)

---

## 7. Attack Surface Summary

A concise paragraph summarising the most impactful findings and recommended first actions for remediation or further testing.

**Top 3 findings to act on:**
1. [Most critical]
2. [Second]
3. [Third]

**Suggested next steps:**
- Dynamic analysis recommended for: [WebView, exported components, etc.]
- Manual review recommended for: [specific classes or flows]
- Immediate rotation required: [any exposed keys or tokens]
```

---

## Reference Files

- `references/secret-patterns.md` — Full grep/ripgrep pattern list for secret hunting with regex, tool commands, and severity ratings
- `references/owasp-mobile-top10.md` — OWASP Mobile Top 10 and MASVS category reference with remediation guidance
