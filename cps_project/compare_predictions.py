#!/usr/bin/env python3
"""
Compare locked pre-scan predictions against an actual Checkmarx export.

    python compare_predictions.py <scan_export.json> [--predictions PREDICTIONS_CH003_CH004.json]

For every predicted chain participant this reports whether the query fired,
what severity the tenant actually assigned, and what individual CPS the
rubric produced. Then it recomputes chain CPS from the findings that
actually fired and diffs it against the prediction.

The point is that the comparison is mechanical. No interpretation, no
marking our own homework.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cps_engine import parse_checkmarx_json, score_findings
from cps_engine.rubric import band, score_chain


def _norm(name: str) -> str:
    """Match the engine's query-name normalisation closely enough to pair
    a catalog name with whatever the tenant emitted."""
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " _-":
            out.append("_")
    collapsed = "_".join(p for p in "".join(out).split("_") if p)
    return collapsed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scan", help="Checkmarx export JSON")
    ap.add_argument("--predictions", default="PREDICTIONS_CH003_CH004.json")
    args = ap.parse_args()

    predictions = json.loads(Path(args.predictions).read_text(encoding="utf-8"))
    findings = parse_checkmarx_json(args.scan)
    score_findings(findings)

    actual: dict[str, list] = {}
    for f in findings:
        actual.setdefault(_norm(f.query_name), []).append(f)

    grand_hits = grand_total = 0

    for chain_id, chain in predictions["chains"].items():
        print("=" * 78)
        print(f"{chain_id}   predicted chain CPS "
              f"{chain['predicted_chain_cps']:.2f} ({chain['predicted_chain_band']})")
        print("=" * 78)
        print(f"{'query':<40}{'pred':<16}{'actual':<16}{'verdict'}")
        print("-" * 78)

        observed_scores = []
        for row in chain["findings"]:
            key = _norm(row["query_name"])
            matches = actual.get(key, [])
            grand_total += 1
            pred = f"{row['predicted_severity']}/{row['predicted_individual_cps']:.2f}"

            if not matches:
                print(f"{row['query_name']:<40}{pred:<16}{'-- not found':<16}MISS")
                continue

            grand_hits += 1
            best = max(matches, key=lambda f: f.cps_score or 0.0)
            got = f"{best.default_severity}/{(best.cps_score or 0.0):.2f}"
            observed_scores.append(best.cps_score or 0.0)

            verdict = "HIT"
            if str(best.default_severity).lower() != row["predicted_severity"].lower():
                verdict = (f"HIT / severity drift "
                           f"({row['predicted_severity']} -> {best.default_severity})")
            print(f"{row['query_name']:<40}{pred:<16}{got:<16}{verdict}"
                  f"   x{len(matches)}")

        n_found = len(observed_scores)
        n_total = len(chain["findings"])
        if observed_scores:
            actual_chain = score_chain(observed_scores)
            state = "FULLY_ASSEMBLED" if n_found == n_total else "PARTIALLY_ASSEMBLED"
            delta = actual_chain - chain["predicted_chain_cps"]
            print("-" * 78)
            print(f"  state            {state}  ({n_found} of {n_total} present)")
            print(f"  actual chain CPS {actual_chain:.2f} ({band(actual_chain)})")
            print(f"  vs prediction    {delta:+.2f}   "
                  f"band {chain['predicted_chain_band']} -> {band(actual_chain)}")
        else:
            print("-" * 78)
            print("  state            NOT_ASSEMBLED (no predicted findings fired)")
        print()

    print("=" * 78)
    print(f"Prediction accuracy: {grand_hits} of {grand_total} predicted findings fired "
          f"({(100.0 * grand_hits / grand_total if grand_total else 0):.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
