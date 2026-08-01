#!/usr/bin/env python3
"""Verify that a Checkmarx scan of this repository reproduces all ten chains.

    python verify_chains.py <scan_export.json> [--catalog chains_index_nexa.json]

Reports, per chain, which required findings fired and at what severity, then
flags any Critical or High finding anywhere in the scan - the repository is
built so that none should exist in application code or IaC.

Requires the cps_engine package (from the CPS project) on PYTHONPATH.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def norm(name: str) -> str:
    out = []
    for ch in str(name).lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " _-":
            out.append("_")
    return "_".join(p for p in "".join(out).split("_") if p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scan")
    ap.add_argument("--catalog", default="chains_index_nexa.json")
    args = ap.parse_args()

    try:
        from cps_engine import parse_checkmarx_json, score_findings
        from cps_engine.rubric import band, score_chain
    except ImportError:
        print("cps_engine not importable. Run from the cps_project directory or set "
              "PYTHONPATH to it.", file=sys.stderr)
        return 2

    findings = parse_checkmarx_json(args.scan)
    score_findings(findings)
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))

    index: dict[str, list] = {}
    for f in findings:
        index.setdefault(norm(f.query_name), []).append(f)

    assembled = 0
    for chain in catalog["chains"]:
        rows, scores, missing = [], [], []
        for req in chain["required_findings"]:
            q = req["query_name"]
            cands = index.get(norm(q), [])
            scope = req.get("match_file_contains")
            if scope:
                cands = [c for c in cands
                         if scope.lower() in str(c.source_file).lower()]
            label = q if not scope else f"{q} [in {scope}]"
            if not cands:
                missing.append(label)
                rows.append(f"  [--] {label}  NOT FOUND "
                            f"(expected {req['default_severity_in_catalog']})")
                continue
            best = max(cands, key=lambda c: c.cps_score or 0.0)
            scores.append(best.cps_score or 0.0)
            drift = ("" if str(best.default_severity).lower()
                     == req["default_severity_in_catalog"].lower()
                     else f"  <-- severity drift, expected "
                          f"{req['default_severity_in_catalog']}")
            rows.append(f"  [ok] {label}  {best.default_severity}/"
                        f"{(best.cps_score or 0):.2f}  x{len(cands)}{drift}")

        total = len(chain["required_findings"])
        got = total - len(missing)
        cps = score_chain(scores) if scores else 0.0
        state = ("FULLY_ASSEMBLED" if got == total
                 else "PARTIALLY_ASSEMBLED" if got else "NOT_ASSEMBLED")
        if state == "FULLY_ASSEMBLED":
            assembled += 1

        print("=" * 78)
        print(f"{chain['id']} — {chain['name']}")
        print(f"  state {state}   {got} of {total}   chain CPS {cps:.2f} ({band(cps)})")
        print(f"  location: {chain['validation']['location']}")
        for r in rows:
            print(r)
        print()

    over = [f for f in findings
            if str(f.default_severity).lower() in ("high", "critical")]
    print("=" * 78)
    print(f"Chains fully assembled: {assembled} of {len(catalog['chains'])}")
    if over:
        print(f"\nWARNING: {len(over)} High/Critical finding(s) present. "
              f"The repository targets Medium and below:")
        seen = set()
        for f in over:
            key = (f.query_name, f.default_severity)
            if key in seen:
                continue
            seen.add(key)
            print(f"  {f.default_severity:<9} {f.query_name}  ::  {f.source_file}")
    else:
        print("No High or Critical findings present.")
    return 0 if assembled == len(catalog["chains"]) else 1


if __name__ == "__main__":
    sys.exit(main())
