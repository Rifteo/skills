# JS Analyzer — Regex Patterns Cheatsheet

Quick-copy grep patterns for secret hunting, endpoint extraction, and vulnerability detection.
All patterns are `grep -rEin` compatible. Run against downloaded JS files directory.

---

## Secrets & Credentials

### Cloud Provider Keys

```bash
# AWS Access Key ID
grep -rEn "AKIA[0-9A-Z]{16}" ./js-files/

# AWS Secret Access Key
grep -rEin "aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]" ./js-files/

# GCP / Google API Key
grep -rEn "AIza[0-9A-Za-z\-_]{35}" ./js-files/

# GCP Service Account JSON
grep -rEin '"type"\s*:\s*"service_account"' ./js-files/

# Azure Storage Key
grep -rEn "[a-zA-Z0-9+/]{86}==" ./js-files/

# Azure SAS Token
grep -rEin "sv=[0-9]{4}-[0-9]{2}-[0-9]{2}&" ./js-files/
```

### Payment & Communication APIs

```bash
# Stripe Secret Key
grep -rEn "sk_live_[0-9a-zA-Z]{24}" ./js-files/

# Stripe Publishable Key
grep -rEn "pk_live_[0-9a-zA-Z]{24}" ./js-files/

# Stripe Test Keys (informational)
grep -rEn "sk_test_[0-9a-zA-Z]{24}" ./js-files/

# Twilio Account SID
grep -rEn "AC[a-z0-9]{32}" ./js-files/

# Twilio Auth Token
grep -rEin "twilio.{0,30}['\"][a-f0-9]{32}['\"]" ./js-files/

# SendGrid API Key
grep -rEn "SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}" ./js-files/

# Mailgun API Key
grep -rEn "key-[0-9a-zA-Z]{32}" ./js-files/
```

### Source Code & Version Control

```bash
# GitHub Personal Access Token (classic)
grep -rEn "ghp_[A-Za-z0-9]{36}" ./js-files/

# GitHub OAuth App Token
grep -rEn "gho_[A-Za-z0-9]{36}" ./js-files/

# GitHub Actions Token
grep -rEn "ghs_[A-Za-z0-9]{36}" ./js-files/

# GitLab Personal Access Token
grep -rEn "glpat-[A-Za-z0-9\-_]{20}" ./js-files/
```

### Communication & Collaboration

```bash
# Slack Bot/User/App Token
grep -rEn "xox[baprs]-[0-9]{11}-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{32}" ./js-files/

# Slack Webhook URL
grep -rEn "hooks\.slack\.com/services/T[0-9A-Z]+/B[0-9A-Z]+/[a-zA-Z0-9]+" ./js-files/

# Discord Bot Token
grep -rEn "([MN][A-Za-z0-9]{23}\.[A-Za-z0-9\-_]{6}\.[A-Za-z0-9\-_]{27})" ./js-files/

# Telegram Bot Token
grep -rEn "[0-9]{8,10}:[A-Za-z0-9\-_]{35}" ./js-files/
```

### Databases

```bash
# MongoDB connection string
grep -rEin "mongodb(\+srv)?://[^'\"\s]+:[^'\"\s]+@" ./js-files/

# PostgreSQL connection string
grep -rEin "postgres(ql)?://[^'\"\s]+:[^'\"\s]+@" ./js-files/

# MySQL connection string
grep -rEin "mysql://[^'\"\s]+:[^'\"\s]+@" ./js-files/

# Redis connection string
grep -rEin "redis://[^'\"\s]+:[^'\"\s]+@" ./js-files/

# Generic DB URL
grep -rEin "DB_URL\s*[=:]\s*['\"]" ./js-files/
grep -rEin "DATABASE_URL\s*[=:]\s*['\"]" ./js-files/
```

### Generic Secrets

```bash
# Private keys (PEM format)
grep -rEn "BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY" ./js-files/

# JWT tokens (embedded in source)
grep -rEn "eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}" ./js-files/

# Generic API key assignment patterns
grep -rEin "api.?key\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}['\"]" ./js-files/
grep -rEin "apiKey\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}['\"]" ./js-files/
grep -rEin "access.?token\s*[=:]\s*['\"][A-Za-z0-9_\-\.]{20,}['\"]" ./js-files/
grep -rEin "auth.?token\s*[=:]\s*['\"][A-Za-z0-9_\-\.]{20,}['\"]" ./js-files/
grep -rEin "client.?secret\s*[=:]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]" ./js-files/
grep -rEin "secret.?key\s*[=:]\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]" ./js-files/
grep -rEin "password\s*[=:]\s*['\"][^'\"]{6,}['\"]" ./js-files/

# Firebase configuration
grep -rEin "apiKey.*firebaseapp|storageBucket.*firebaseapp|authDomain.*firebaseapp" ./js-files/
```

---

## Endpoint & API Discovery

```bash
# REST API paths
grep -rEoh '["'"'"'](/api/v?[0-9]*/[a-zA-Z0-9/_\-\?=&\.%]+)["'"'"']' ./js-files/ | sort -u

# fetch() calls
grep -rEon "fetch\(['\"][^'\"]+['\"]" ./js-files/ | sort -u

# axios calls
grep -rEon "axios\.(get|post|put|delete|patch|head)\(['\"][^'\"]+['\"]" ./js-files/ | sort -u

# XMLHttpRequest
grep -rEon '\.open\(['"'"'"](GET|POST|PUT|DELETE)['"'"'"],\s*['"'"'"][^'"'"'"]+['"'"'"]' ./js-files/ | sort -u

# Base URL / API base
grep -rEin "(baseURL|BASE_URL|API_URL|API_BASE|apiEndpoint)\s*[=:]\s*['\"]https?://[^'\"]*['\"]" ./js-files/ | sort -u

# GraphQL operations
grep -rEn "query\s+\w+\s*\{|mutation\s+\w+\s*\{|subscription\s+\w+\s*\{" ./js-files/ | head -20

# Internal / admin endpoints
grep -rEoin '["'"'"'](/admin[^"'"'"']*|/internal[^"'"'"']*|/debug[^"'"'"']*|/dev[^"'"'"']*|/test[^"'"'"']*|/management[^"'"'"']*)["'"'"']' ./js-files/ | sort -u

# S3 buckets
grep -rEin "s3\.amazonaws\.com|s3-[a-z]+-[0-9]+\.amazonaws\.com" ./js-files/ | sort -u
```

---

## DOM XSS Sources & Sinks

```bash
# Sources (user-controllable input)
grep -rEn "location\.(search|hash|href|pathname|host)|document\.(referrer|URL|documentURI|baseURI)|window\.name|history\.state" ./js-files/

# High-risk sinks
grep -rEn "innerHTML\s*=|outerHTML\s*=|insertAdjacentHTML\(" ./js-files/
grep -rEn "document\.write\(|document\.writeln\(" ./js-files/
grep -rEn "\beval\s*\(|\bFunction\s*\(|new\s+Function\s*\(" ./js-files/
grep -rEn "setTimeout\s*\(\s*['\"]|setInterval\s*\(\s*['\"]" ./js-files/

# URL/redirect sinks
grep -rEn "location\.href\s*=|location\.assign\s*\(|location\.replace\s*\(|location\s*=" ./js-files/
grep -rEn "window\.open\s*\(" ./js-files/

# Script/resource injection
grep -rEn "\.src\s*=.*location\|\.href\s*=.*location\|\.action\s*=.*location" ./js-files/

# jQuery sinks
grep -rEn "\.html\s*\(|\.append\s*\(|\.prepend\s*\(|\.after\s*\(|\.before\s*\(|\.replaceWith\s*\(" ./js-files/ | grep -v "'<\|\"<"
```

---

## Prototype Pollution

```bash
# Recursive merge patterns (server & client)
grep -rEn "\[key\]\s*=\s*\w+\[key\]|\[prop\]\s*=\s*\w+\[prop\]" ./js-files/
grep -rEin "Object\.assign\s*\(\s*\{\}|merge\s*\(\s*\{\}|extend\s*\(\s*true\s*,\s*\{\}" ./js-files/
grep -rEin "deepmerge\|lodash\.merge\|_.merge\|jQuery\.extend\s*\(\s*true" ./js-files/

# Direct prototype access
grep -rEn "__proto__|constructor\.prototype|Object\.prototype\." ./js-files/

# Query string parsing (common PP vector)
grep -rEin "qs\.parse\|querystring\.parse\|URLSearchParams\|\.parseQuery" ./js-files/
```

---

## postMessage

```bash
# Message event listeners
grep -rEn "addEventListener\(['\"]message['\"]" ./js-files/
grep -rEn "onmessage\s*=" ./js-files/

# Origin validation (or lack thereof)
grep -rEn "event\.origin|e\.origin|msg\.origin" ./js-files/

# postMessage calls (sending side)
grep -rEn "\.postMessage\(" ./js-files/

# Dangerous handler patterns
grep -rEn "e\.data\b|event\.data\b|msg\.data\b" ./js-files/ | \
  grep -i "eval\|innerHTML\|location\|src\|href"
```

---

## Authentication & Authorization

```bash
# Role checks in JS
grep -rEin "isAdmin\s*[=!]=|role\s*[=!]==\s*['\"]admin['\"]|isStaff\s*[=!]=|isModerator" ./js-files/
grep -rEin "permission|canAccess|hasRole|isAuthorized|isAuthenticated" ./js-files/ | head -20

# Token storage
grep -rEin "localStorage\.(setItem|getItem).*['\"]token\|authToken\|jwt\|session" ./js-files/
grep -rEin "sessionStorage\.(setItem|getItem).*['\"]token\|authToken\|jwt" ./js-files/
grep -rEin "document\.cookie.*['\"]token\|auth\|session" ./js-files/

# Token transmission
grep -rEin "Authorization.*Bearer\|X-Auth-Token\|X-API-Key" ./js-files/

# OAuth / SSO parameters
grep -rEin "client_id\s*[=:]\s*['\"][^'\"]+['\"]" ./js-files/
grep -rEin "redirect_uri\s*[=:]\s*['\"][^'\"]+['\"]" ./js-files/
```

---

## Framework Detection

```bash
# React
grep -rEn "React\.|ReactDOM\.|createRoot\|createElement\|useState\|useEffect" ./js-files/ | head -5

# Angular
grep -rEn "@angular/core\|NgModule\|Component\|Injectable" ./js-files/ | head -5

# Vue
grep -rEn "Vue\.\|createApp\|defineComponent\|ref(\|reactive(" ./js-files/ | head -5

# Next.js
grep -rEn "__NEXT_DATA__\|_next/static\|getServerSideProps\|getStaticProps" ./js-files/ | head -5

# jQuery
grep -rEn "jQuery\s*=\|window\.\$\s*=\|\.fn\.jquery\s*=" ./js-files/ | head -5

# AngularJS 1.x (older)
grep -rEn "angular\.module\|ng-app\|ng-controller\|\$scope\|\$http" ./js-files/ | head -5
```

---

## Sensitive Information Patterns

```bash
# Internal hostnames and IP addresses
grep -rEon "https?://[a-zA-Z0-9\-]+\.(internal|local|corp|intranet|priv|dev|staging)[^\"'\s]*" ./js-files/
grep -rEon "(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)[0-9]{1,3}\.[0-9]{1,3}" ./js-files/

# Debug / logging endpoints
grep -rEin "console\.(log|error|debug|warn|info)\s*\(" ./js-files/ | \
  grep -i "password\|token\|secret\|key\|auth\|credential" | head -10

# TODO / FIXME comments (often contain security notes)
grep -rEin "TODO|FIXME|HACK|XXX|BUG|SECURITY|VULN" ./js-files/ | head -20

# Commented-out code with credentials
grep -rEin "//.*password|//.*secret|//.*api.?key|//.*token" ./js-files/ | head -20

# Version strings
grep -rEn "(version|v)['\"\s:=]+[0-9]+\.[0-9]+\.[0-9]+" ./js-files/ | \
  grep -iv "content-type\|application\|charset" | head -20
```

---

## Open Redirect Indicators

```bash
# Redirect parameters by name
grep -rEin "redirect\s*=\|return_url\s*=\|next\s*=\|url\s*=\|goto\s*=\|dest\s*=\|target\s*=\|callback\s*=" ./js-files/ | head -20

# JS-controlled redirects consuming URL parameters
grep -rEin "location\.(search|hash|href)" ./js-files/ | \
  grep -i "redirect\|return\|next\|url\|goto\|callback\|dest\|target" | head -20
```

---

## JSONP / Legacy Callbacks

```bash
# JSONP callback pattern in URLs
grep -rEin "callback=[a-zA-Z_]\|jsonp=[a-zA-Z_]\|cb=[a-zA-Z_]" ./js-files/

# Script tag dynamic injection
grep -rEin "document\.createElement\s*\(\s*['\"]script['\"]" ./js-files/
grep -rEin "\.src\s*=.*callback\|\.src\s*=.*jsonp" ./js-files/
```

---

## WebSocket Patterns

```bash
# WebSocket initialization
grep -rEn "new WebSocket\s*\(" ./js-files/
grep -rEin "socket\.io\|sockjs\|ws://" ./js-files/

# Messages sent
grep -rEn "\.send\s*\(|\.emit\s*\(" ./js-files/ | grep -v "XMLHttp\|fetch\|axios" | head -20
```
