#!/usr/bin/env python3
"""
redirect_probe.py — Open redirect parameter fuzzer
Dependencies: pip install requests colorama

Usage:
  # Single URL with parameter to fuzz
  python3 redirect_probe.py -u "https://target.com/login?next=FUZZ" -p references/payloads.txt

  # Multiple URLs from file
  python3 redirect_probe.py -l targets.txt -p references/payloads.txt

  # With auth cookie
  python3 redirect_probe.py -u "https://target.com/login?next=FUZZ" \
    -p references/payloads.txt --cookie "session=abc123"

  # With Bearer token
  python3 redirect_probe.py -u "https://target.com/login?next=FUZZ" \
    -p references/payloads.txt --token "eyJ..."

  # Output to JSON
  python3 redirect_probe.py -u "https://target.com/login?next=FUZZ" \
    -p references/payloads.txt -o report.json
"""

import argparse
import json
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("Missing dependencies. Run: pip install requests colorama")
    sys.exit(1)

REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}
TIMEOUT = 10
MAX_WORKERS = 10


def check_redirect(session, url, payload, evil_domain="evil.com"):
    """Send request and check if Location header points to our payload domain."""
    target_url = url.replace("FUZZ", urllib.parse.quote(payload, safe=":/@!$&'()*+,;="))
    try:
        r = session.get(target_url, allow_redirects=False, timeout=TIMEOUT)
        location = r.headers.get("Location", "")
        if r.status_code in REDIRECT_STATUS_CODES and evil_domain in location:
            return {
                "url": target_url,
                "payload": payload,
                "status": r.status_code,
                "location": location,
                "vulnerable": True,
            }
    except requests.exceptions.RequestException:
        pass
    return None


def build_session(cookie=None, token=None):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Security Researcher)"})
    if cookie:
        for c in cookie.split(";"):
            c = c.strip()
            if "=" in c:
                name, _, value = c.partition("=")
                s.cookies.set(name.strip(), value.strip())
    if token:
        s.headers["Authorization"] = f"Bearer {token}"
    return s


def probe_url(session, url, payloads, evil_domain):
    findings = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(check_redirect, session, url, p, evil_domain): p for p in payloads}
        for future in as_completed(futures):
            result = future.result()
            if result:
                findings.append(result)
    return findings


def main():
    parser = argparse.ArgumentParser(description="Open redirect parameter fuzzer")
    parser.add_argument("-u", "--url", help="Single target URL with FUZZ marker")
    parser.add_argument("-l", "--list", help="File containing target URLs with FUZZ marker")
    parser.add_argument("-p", "--payloads", required=True, help="Payload file")
    parser.add_argument("--cookie", help="Cookie header value (key=val; key2=val2)")
    parser.add_argument("--token", help="Bearer token")
    parser.add_argument("--evil-domain", default="evil.com", help="Domain to detect in Location header (default: evil.com)")
    parser.add_argument("-o", "--output", help="Output JSON file")
    parser.add_argument("--delay", type=float, default=0, help="Delay between requests in seconds")
    args = parser.parse_args()

    if not args.url and not args.list:
        parser.error("Provide -u (single URL) or -l (URL list)")

    with open(args.payloads) as f:
        payloads = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

    urls = []
    if args.url:
        urls.append(args.url)
    if args.list:
        with open(args.list) as f:
            urls.extend(line.strip() for line in f if line.strip())

    session = build_session(args.cookie, args.token)

    print(f"{Fore.CYAN}[*] Loaded {len(payloads)} payloads | {len(urls)} target(s)")
    print(f"{Fore.CYAN}[*] Evil domain: {args.evil_domain}")
    print(f"{Fore.CYAN}[*] Starting scan...\n")

    all_findings = []

    for url in urls:
        print(f"{Fore.YELLOW}[>] Probing: {url}")
        findings = probe_url(session, url, payloads, args.evil_domain)
        for f in findings:
            print(f"{Fore.GREEN}[VULN] {f['status']} → {f['location']}")
            print(f"       Payload: {f['payload']}")
            print(f"       URL: {f['url']}\n")
            all_findings.append(f)
        if not findings:
            print(f"{Fore.RED}       No open redirect found\n")
        if args.delay:
            time.sleep(args.delay)

    print(f"\n{Fore.CYAN}[*] Scan complete. {len(all_findings)} finding(s).")

    if args.output:
        with open(args.output, "w") as out:
            json.dump(all_findings, out, indent=2)
        print(f"{Fore.CYAN}[*] Results saved to {args.output}")

    return 0 if not all_findings else 1


if __name__ == "__main__":
    sys.exit(main())
