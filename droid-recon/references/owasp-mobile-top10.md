# OWASP Mobile Security Reference

Quick reference for mapping droid-recon findings to OWASP Mobile Top 10 (2024) and MASVS (Mobile Application Security Verification Standard) v2.

Use this file to:
- Assign the correct MASVS category and OWASP Mobile ID to each finding
- Get concise remediation guidance per category
- Understand severity context

---

## OWASP Mobile Top 10 (2024)

| ID | Category | MASVS Mapping |
|---|---|---|
| M1 | Improper Credential Usage | MASVS-AUTH, MASVS-STORAGE |
| M2 | Inadequate Supply Chain Security | MASVS-CODE |
| M3 | Insecure Authentication / Authorization | MASVS-AUTH |
| M4 | Insufficient Input/Output Validation | MASVS-CODE, MASVS-PLATFORM |
| M5 | Insecure Communication | MASVS-NETWORK |
| M6 | Inadequate Privacy Controls | MASVS-STORAGE, MASVS-PLATFORM |
| M7 | Insufficient Binary Protections | MASVS-RESILIENCE |
| M8 | Security Misconfiguration | MASVS-PLATFORM, MASVS-NETWORK |
| M9 | Insecure Data Storage | MASVS-STORAGE |
| M10 | Insufficient Cryptography | MASVS-CRYPTO |

---

## MASVS Categories (v2)

---

### MASVS-STORAGE — Secure Data Storage

**Applies to:** Where sensitive data is stored and how it is protected.

#### MASVS-STORAGE-1: Sensitive data is not stored in app-accessible locations

Findings that trigger this:
- Sensitive data written to external storage (`getExternalStorageDirectory`)
- Sensitive data in world-readable files (`MODE_WORLD_READABLE`)
- Credentials or tokens in `SharedPreferences` without encryption

**Remediation:**
- Use Android Keystore to protect cryptographic keys
- Use `EncryptedSharedPreferences` (Jetpack Security) for sensitive preferences
- Use `EncryptedFile` for sensitive file storage
- Never write PII, tokens, or keys to external storage

#### MASVS-STORAGE-2: No sensitive data in app backups

Findings that trigger this:
- `android:allowBackup="true"` in manifest
- Sensitive files not excluded from backup rules

**Remediation:**
```xml
<application android:allowBackup="false" ...>
<!-- or with selective exclusion -->
<application android:dataExtractionRules="@xml/data_extraction_rules" ...>
```

```xml
<!-- res/xml/data_extraction_rules.xml -->
<data-extraction-rules>
  <cloud-backup>
    <exclude domain="sharedpref" path="." />
    <exclude domain="database" path="." />
  </cloud-backup>
</data-extraction-rules>
```

---

### MASVS-CRYPTO — Cryptography

**Applies to:** How the app implements and uses cryptography.

#### MASVS-CRYPTO-1: Cryptography follows current best practices

Findings that trigger this:
- Use of `MD5`, `SHA-1` for security purposes
- Use of `DES`, `3DES`, `RC4`, `RC2`
- AES in ECB mode (`AES/ECB/PKCS5Padding`)
- Hardcoded IV or salt
- `java.util.Random` used for security-sensitive operations
- Short or predictable key material

**Remediation:**
- Use `AES/GCM/NoPadding` (authenticated encryption)
- Use `SHA-256` or `SHA-3` for hashing
- Generate IVs randomly: `SecureRandom().nextBytes(iv)`
- Use `SecureRandom` not `Random` for security operations
- Minimum key length: AES-128, RSA-2048, EC-256

```java
// Correct AES-GCM
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
byte[] iv = new byte[12];
new SecureRandom().nextBytes(iv);
cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
```

#### MASVS-CRYPTO-2: App uses proven random number generation

**Remediation:**
```java
// Use SecureRandom, never java.util.Random for security
SecureRandom random = new SecureRandom();
byte[] token = new byte[32];
random.nextBytes(token);
```

---

### MASVS-AUTH — Authentication and Authorization

**Applies to:** How the app authenticates users and enforces access control.

#### MASVS-AUTH-1: Authentication and session management

Findings that trigger this:
- Hardcoded credentials in code
- Tokens stored in plaintext SharedPreferences
- No token expiry or refresh logic
- Biometric auth easily bypassable

**Remediation:**
- Store tokens in `EncryptedSharedPreferences` or Android Keystore
- Implement token refresh with short-lived access tokens
- Use `BiometricPrompt` with `CryptoObject` (key-bound biometrics)
- Never store passwords — use proper auth flows (OAuth 2.0, OpenID Connect)

#### MASVS-AUTH-2: Step-up authentication for sensitive operations

Sensitive operations (payments, profile changes) should require re-authentication.

---

### MASVS-NETWORK — Network Communication

**Applies to:** How the app protects data in transit.

#### MASVS-NETWORK-1: TLS used for all network communication

Findings that trigger this:
- `http://` URLs in production code
- `android:usesCleartextTraffic="true"`
- `<domain-config cleartextTrafficPermitted="true">` in NSC

**Remediation:**
```xml
<!-- Network Security Config -->
<network-security-config>
  <base-config cleartextTrafficPermitted="false">
    <trust-anchors>
      <certificates src="system"/>
    </trust-anchors>
  </base-config>
</network-security-config>
```

#### MASVS-NETWORK-2: TLS settings follow current best practices

Findings that trigger this:
- `ALLOW_ALL_HOSTNAME_VERIFIER`
- Custom `X509TrustManager` that does not validate
- `onReceivedSslError` calling `handler.proceed()`
- No certificate pinning

**Remediation:**
```java
// Never do this
hostnameVerifier = (hostname, session) -> true; // INSECURE

// Correct hostname verification is automatic with OkHttp / HttpsURLConnection
// For custom X509TrustManager, always implement checkServerTrusted fully

// Certificate pinning with OkHttp
CertificatePinner pinner = new CertificatePinner.Builder()
  .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
  .build();
OkHttpClient client = new OkHttpClient.Builder()
  .certificatePinner(pinner)
  .build();
```

#### MASVS-NETWORK-3: Certificate pinning for critical connections

Implement pinning for high-value endpoints. Pin the intermediate CA, not the leaf cert, to allow rotation. Always implement a backup pin.

---

### MASVS-PLATFORM — Platform Interaction

**Applies to:** How the app interacts with the Android platform and other apps.

#### MASVS-PLATFORM-1: App uses the minimum required permissions

Findings that trigger this:
- Dangerous permissions declared but not demonstrably necessary
- `READ_CONTACTS`, `RECORD_AUDIO`, `CAMERA` without clear product justification

**Remediation:**
- Remove all permissions not required for core functionality
- Use `ACCESS_COARSE_LOCATION` instead of `ACCESS_FINE_LOCATION` where precision is not needed
- Request permissions at runtime, only when needed

#### MASVS-PLATFORM-2: Secure use of IPC mechanisms

Findings that trigger this:
- Exported Activities/Services/Receivers without permission
- `addJavascriptInterface` with `setJavaScriptEnabled(true)`
- `setAllowFileAccessFromFileURLs(true)` in WebView
- Implicit intents sending sensitive data

**Remediation:**
```xml
<!-- Unexported by default -->
<activity android:name=".SensitiveActivity"
          android:exported="false" />

<!-- If exported, require a permission -->
<activity android:name=".PublicActivity"
          android:exported="true"
          android:permission="com.example.CUSTOM_PERMISSION" />
```

```java
// WebView hardening
webView.getSettings().setJavaScriptEnabled(false); // disable if not needed
webView.getSettings().setAllowFileAccess(false);
webView.getSettings().setAllowFileAccessFromFileURLs(false);
webView.getSettings().setAllowUniversalAccessFromFileURLs(false);

// Only load trusted URLs
if (isTrustedUrl(url)) {
  webView.loadUrl(url);
}
```

#### MASVS-PLATFORM-3: The app protects sensitive functionality from UI attacks (Tapjacking)

Findings that trigger this:
- Activities missing `filterTouchesWhenObscured`

**Remediation:**
```xml
<View android:filterTouchesWhenObscured="true" />
```

---

### MASVS-CODE — Code Quality

**Applies to:** Code-level security issues.

#### MASVS-CODE-1: The app requires an up-to-date platform version

Findings that trigger this:
- `minSdkVersion` below 21 (Android 5.0 / Lollipop)
- `targetSdkVersion` significantly behind current

**Remediation:**
- Set `minSdkVersion` >= 24 (Android 7.0) for modern security baseline
- Set `targetSdkVersion` to the latest stable Android version

#### MASVS-CODE-2: The app only uses supported / active third-party components

Findings that trigger this:
- Outdated third-party libraries with known CVEs
- Unmaintained dependencies

**Remediation:**
- Run `./gradlew dependencyUpdates` (gradle-versions-plugin)
- Audit dependencies with OWASP Dependency-Check
- Subscribe to GitHub security advisories for key dependencies

#### MASVS-CODE-3: The app uses secure coding practices

Findings that trigger this:
- `Log.d/e/i` statements logging PII or credentials
- SQL queries built with string concatenation
- Dynamic code loading without integrity checks

**Remediation:**
```java
// No sensitive data in logs
Log.d("Auth", "Login attempt"); // OK
Log.d("Auth", "Password: " + password); // NEVER

// Parameterized queries
db.rawQuery("SELECT * FROM users WHERE id = ?", new String[]{userId}); // OK
db.rawQuery("SELECT * FROM users WHERE id = " + userId); // INSECURE
```

---

### MASVS-RESILIENCE — Reverse Engineering Resistance

**Applies to:** Whether the app resists runtime tampering and analysis.

> Note: MASVS-RESILIENCE controls are recommended for high-risk applications (banking, payment, DRM) but not a universal requirement. Tag findings as informational if the app is not in a high-risk category.

#### MASVS-RESILIENCE-1: Obfuscation applied

Findings that trigger this:
- Readable class/method names in smali output
- No ProGuard/R8 rules applied

**Remediation:**
```proguard
# Enable full obfuscation in proguard-rules.pro
-obfuscationdictionary obfuscation-dictionary.txt
-keepattributes SourceFile,LineNumberTable
```

#### MASVS-RESILIENCE-2: Anti-tampering mechanisms

App should detect if it has been repackaged or modified. Use Play Integrity API (replaces SafetyNet).

#### MASVS-RESILIENCE-3: Root / emulator detection

Consider implementing runtime checks for rooted/emulated environments in high-risk apps.

#### MASVS-RESILIENCE-4: Certificate pinning

Implemented at MASVS-NETWORK-3 level. For high-risk apps, also verify against tampering of the pinning logic itself.

---

## Severity Mapping by MASVS Category

| MASVS | Typical Severity | Notes |
|---|---|---|
| MASVS-STORAGE-1 (plaintext secrets) | Critical | Credentials/keys in plaintext = immediate risk |
| MASVS-STORAGE-2 (backup) | High | Requires physical access or ADB |
| MASVS-CRYPTO-1 (weak algo) | High | Data encrypted with weak cipher = effectively plaintext |
| MASVS-AUTH-1 (hardcoded creds) | Critical | Direct account compromise |
| MASVS-NETWORK-1 (cleartext) | High | Requires network position |
| MASVS-NETWORK-2 (TLS bypass) | Critical | Active MITM trivially possible |
| MASVS-PLATFORM-2 (WebView RCE) | Critical | Remote code execution if loading untrusted URL |
| MASVS-PLATFORM-2 (exported) | High | App-to-app attack surface |
| MASVS-CODE-3 (log leakage) | Medium | Requires device access or logcat access |
| MASVS-RESILIENCE | Low–Info | Context-dependent; informational for most apps |

---

## Quick Lookup: Finding → OWASP ID

| Finding | OWASP Mobile | MASVS |
|---|---|---|
| Hardcoded API key | M1 | MASVS-STORAGE-2 |
| Hardcoded password | M1 | MASVS-AUTH-1 |
| Plaintext HTTP | M5 | MASVS-NETWORK-1 |
| SSL bypass / custom TrustManager | M5 | MASVS-NETWORK-2 |
| AES/ECB or MD5 usage | M10 | MASVS-CRYPTO-1 |
| Hardcoded IV | M10 | MASVS-CRYPTO-1 |
| SQLite unencrypted | M9 | MASVS-STORAGE-1 |
| SharedPreferences tokens | M9 | MASVS-STORAGE-1 |
| External storage PII | M9 | MASVS-STORAGE-1 |
| android:allowBackup=true | M9 | MASVS-STORAGE-2 |
| android:debuggable=true | M8 | MASVS-CODE |
| Exported component no permission | M8 | MASVS-PLATFORM-2 |
| WebView + JavaScript interface | M4 | MASVS-PLATFORM-2 |
| Dangerous permissions | M6 | MASVS-PLATFORM-1 |
| Log.d with credentials | M6 | MASVS-CODE-3 |
| No obfuscation | M7 | MASVS-RESILIENCE-1 |
| Dynamic code loading | M7 | MASVS-RESILIENCE |
| java.util.Random for security | M10 | MASVS-CRYPTO-2 |
| Firebase URL exposed | M1 | MASVS-STORAGE-2 |
| Deep link without validation | M4 | MASVS-PLATFORM-2 |
