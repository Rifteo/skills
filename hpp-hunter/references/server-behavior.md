# Server Parameter Handling Behavior

How different technology stacks process duplicate HTTP parameters. Knowing this is essential before crafting any HPP payload.

---

## Duplicate Query String Parameters

| Technology | Duplicate behavior | Example result for `?p=a&p=b` |
|---|---|---|
| PHP / Apache | Last value wins | `$_GET['p'] = 'b'` |
| ASP.NET / IIS | All values joined with `, ` | `Request["p"] = "a, b"` |
| JSP / Tomcat | First value wins | `request.getParameter("p") = 'a'` |
| Node.js / Express | Array | `req.query.p = ['a', 'b']` |
| Python / Flask | First value wins | `request.args.get('p') = 'a'` |
| Python / Django | Last value wins | `request.GET['p'] = 'b'` |
| Ruby / Rails | Last value wins | `params[:p] = 'b'` |
| Go / net/http | First value wins | `r.URL.Query().Get("p") = 'a'` |
| Perl / CGI | First value wins | `param('p') = 'a'` |

---

## Duplicate POST Body Parameters

| Technology | Behavior |
|---|---|
| PHP | Last value wins |
| ASP.NET | Comma-concatenated |
| Node.js / Express (urlencoded) | Array or last depending on `qs` library config |
| Python / Flask | First value wins |
| Python / Django | Last value wins |
| Ruby / Rails | Last value wins |
| Java / Spring | Array or first depending on `@RequestParam` config |

---

## Proxy and Middleware Behavior

| Component | Behavior |
|---|---|
| Nginx (reverse proxy) | Passes all duplicate params to back-end unchanged |
| Apache mod_proxy | Passes all — back-end decides |
| AWS ALB | Passes all |
| Cloudflare WAF | Inspects each value independently — does not merge |
| ModSecurity | Inspects first occurrence by default |
| AWS WAF | Inspects first occurrence or all depending on rule config |

> WAFs inspecting only the first (or only one) occurrence while the back-end uses the last → the core HPP WAF bypass primitive.

---

## JSON Body Duplicate Keys

| Parser | Behavior |
|---|---|
| Python `json` | Last key wins (silently) |
| JavaScript `JSON.parse` | Last key wins |
| Java Jackson | Last key wins (default) |
| Java Gson | Last key wins |
| Go `encoding/json` | Last key wins |
| PHP `json_decode` | Last key wins |
| Ruby `JSON.parse` | Last key wins |

Most JSON parsers use last-wins. Combined with a WAF that inspects the first occurrence → reliable bypass for JSON-based APIs.

---

## Array Syntax Variations

Different frameworks recognize different array notations:

| Notation | Recognized by |
|---|---|
| `param[]=a&param[]=b` | PHP, Rails |
| `param[0]=a&param[1]=b` | PHP, Rails, Spring |
| `param=a&param=b` | Express, Django, Flask (as array/list) |
| `param=a,b` | Some custom parsers, CSV-style |

---

## HTTP Header Duplicate Behavior

| Header | Common behavior |
|---|---|
| `X-Forwarded-For` | Many proxies append; back-end reads last or first depending on config |
| `Host` | Most servers use first; some proxies use last → Host header injection |
| `Cookie` | RFC says last wins; browsers send first; servers vary |
| `Content-Type` | First wins in most parsers |
| `Authorization` | First wins; second usually ignored |
| Custom headers | Entirely implementation-dependent |
