#!/usr/bin/env python3
"""
CVSS v3.1 Base Score Calculator
Usage: python3 cvss-scorer.py [--json '{"AV":"N","AC":"L",...}']
       python3 cvss-scorer.py  # interactive mode
"""

import sys
import json
import math

# CVSS v3.1 metric weights
METRICS = {
    "AV": {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2},
    "AC": {"L": 0.77, "H": 0.44},
    "PR": {
        "unchanged": {"N": 0.85, "L": 0.62, "H": 0.27},
        "changed":   {"N": 0.85, "L": 0.50, "H": 0.50},
    },
    "UI": {"N": 0.85, "R": 0.62},
    "C":  {"H": 0.56, "L": 0.22, "N": 0.00},
    "I":  {"H": 0.56, "L": 0.22, "N": 0.00},
    "A":  {"H": 0.56, "L": 0.22, "N": 0.00},
}

LABELS = {
    "AV": {"N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical"},
    "AC": {"L": "Low", "H": "High"},
    "PR": {"N": "None", "L": "Low", "H": "High"},
    "UI": {"N": "None", "R": "Required"},
    "S":  {"U": "Unchanged", "C": "Changed"},
    "C":  {"H": "High", "L": "Low", "N": "None"},
    "I":  {"H": "High", "L": "Low", "N": "None"},
    "A":  {"H": "High", "L": "Low", "N": "None"},
}

QUESTIONS = [
    ("AV", "Attack Vector",       ["N=Network", "A=Adjacent", "L=Local", "P=Physical"]),
    ("AC", "Attack Complexity",   ["L=Low", "H=High"]),
    ("PR", "Privileges Required", ["N=None", "L=Low", "H=High"]),
    ("UI", "User Interaction",    ["N=None", "R=Required"]),
    ("S",  "Scope",               ["U=Unchanged", "C=Changed"]),
    ("C",  "Confidentiality",     ["H=High", "L=Low", "N=None"]),
    ("I",  "Integrity",           ["H=High", "L=Low", "N=None"]),
    ("A",  "Availability",        ["H=High", "L=Low", "N=None"]),
]


def roundup(value):
    """CVSS v3.1 Roundup function — rounds up to 1 decimal place."""
    return math.ceil(value * 10) / 10


def calculate(m):
    scope = m["S"]
    pr_weights = METRICS["PR"]["changed" if scope == "C" else "unchanged"]

    av = METRICS["AV"][m["AV"]]
    ac = METRICS["AC"][m["AC"]]
    pr = pr_weights[m["PR"]]
    ui = METRICS["UI"][m["UI"]]
    c  = METRICS["C"][m["C"]]
    i  = METRICS["I"][m["I"]]
    a  = METRICS["A"][m["A"]]

    iss = 1 - (1 - c) * (1 - i) * (1 - a)

    if scope == "U":
        impact = 6.42 * iss
    else:
        impact = 7.52 * (iss - 0.029) - 3.25 * ((iss - 0.02) ** 15)

    if impact <= 0:
        return 0.0, "None"

    exploitability = 8.22 * av * ac * pr * ui

    if scope == "U":
        base = roundup(min(impact + exploitability, 10))
    else:
        base = roundup(min(1.08 * (impact + exploitability), 10))

    if base == 0.0:
        rating = "None"
    elif base < 4.0:
        rating = "Low"
    elif base < 7.0:
        rating = "Medium"
    elif base < 9.0:
        rating = "High"
    else:
        rating = "Critical"

    return base, rating


def build_vector(m):
    return (
        f"CVSS:3.1/AV:{m['AV']}/AC:{m['AC']}/PR:{m['PR']}"
        f"/UI:{m['UI']}/S:{m['S']}/C:{m['C']}/I:{m['I']}/A:{m['A']}"
    )


def interactive():
    print("\n  CVSS v3.1 Base Score Calculator\n")
    m = {}
    for key, label, options in QUESTIONS:
        valid = [o.split("=")[0] for o in options]
        opts_str = "  |  ".join(options)
        while True:
            val = input(f"  {label} [{opts_str}]: ").strip().upper()
            if val in valid:
                m[key] = val
                break
            print(f"    Invalid — choose one of: {', '.join(valid)}")
    return m


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--json":
        try:
            m = json.loads(sys.argv[2])
            m = {k: v.upper() for k, v in m.items()}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        m = interactive()

    score, rating = calculate(m)
    vector = build_vector(m)

    print(f"\n  Vector:     {vector}")
    print(f"  Base Score: {score:.1f}")
    print(f"  Rating:     {rating}\n")

    result = {"vector": vector, "score": score, "rating": rating}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
