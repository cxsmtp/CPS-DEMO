"""
Unit tests for cps_engine.checkmarx_parser.

Verifies all three supported JSON shapes parse correctly and that an
unrecognized shape raises UnsupportedReportShapeError.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cps_engine.checkmarx_parser import (
    UnsupportedReportShapeError,
    filter_low_severity,
    is_aggregate_findings,
    parse_checkmarx_json,
)


SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


# ---------------------------------------------------------------------------
# Checkmarx One results JSON
# ---------------------------------------------------------------------------


def test_parses_cxone_results_json():
    findings = parse_checkmarx_json(SAMPLE_DIR / "sample_checkmarx_export.json")
    # Sample has 12 findings.
    assert len(findings) == 12
    # Verify a representative finding's fields are populated correctly.
    by_id = {f.finding_id: f for f in findings}
    trust = by_id["SIM-1003"]
    assert trust.query_name == "Trust_Boundary_Violation_in_Session_Variables"
    assert trust.cwe == 501
    assert trust.default_severity == "Low"
    assert trust.language == "Python"
    assert trust.source_file == "app/session.py"
    assert trust.line == 88


def test_low_filter_excludes_high_severity():
    findings = parse_checkmarx_json(SAMPLE_DIR / "sample_checkmarx_export.json")
    low = filter_low_severity(findings)
    severities = {f.default_severity for f in low}
    assert severities == {"Low"}
    # Sample has 2 High findings + 10 Low findings.
    assert len(low) == 10


# ---------------------------------------------------------------------------
# SARIF
# ---------------------------------------------------------------------------


def test_parses_sarif():
    findings = parse_checkmarx_json(
        SAMPLE_DIR / "sample_checkmarx_export.sarif.json"
    )
    assert len(findings) == 5
    # SARIF 'note' level should normalize to 'Low'.
    severities = {f.default_severity for f in findings}
    assert severities == {"Low"}
    # CWE should come through from rule properties.
    by_query = {f.query_name: f for f in findings}
    assert by_query["Trust_Boundary_Violation_in_Session_Variables"].cwe == 501
    assert by_query["URL_Canonicalization_Issue"].cwe == 647


# ---------------------------------------------------------------------------
# Legacy CxSAST JSON
# ---------------------------------------------------------------------------


def test_parses_cxsast_legacy_json(tmp_path: Path):
    legacy = {
        "Queries": [
            {
                "QueryName": "Open_Redirect",
                "Severity": "Low",
                "CweId": 601,
                "Language": "Python",
                "Results": [
                    {
                        "FileName": "app/auth/views.py",
                        "Line": 42,
                        "SimilarityId": "LEG-1",
                    },
                ],
            },
            {
                "QueryName": "Log_Forging",
                "Severity": "Low",
                "CweId": 117,
                "Language": "Python",
                "Results": [
                    {
                        "FileName": "app/logger.py",
                        "Line": 55,
                        "SimilarityId": "LEG-2",
                    },
                ],
            },
        ]
    }
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(legacy), encoding="utf-8")

    findings = parse_checkmarx_json(path)
    assert len(findings) == 2
    by_id = {f.finding_id: f for f in findings}
    assert by_id["LEG-1"].query_name == "Open_Redirect"
    assert by_id["LEG-1"].cwe == 601
    assert by_id["LEG-2"].source_file == "app/logger.py"


# ---------------------------------------------------------------------------
# Checkmarx One Improved Project Report (aggregate)
# ---------------------------------------------------------------------------


def test_parses_improved_project_report():
    """Verify the aggregate-report shape parses to per-(query,severity)
    Finding objects, that the aggregate flag is set, and that the
    Low-only filter produces the expected count."""
    findings = parse_checkmarx_json(
        SAMPLE_DIR / "sample_improved_project_report.json"
    )
    assert len(findings) == 12  # 4 Medium + 8 Low
    assert is_aggregate_findings(findings)

    low = filter_low_severity(findings)
    assert len(low) == 8

    counts: dict[str, int] = {}
    for f in low:
        counts[f.query_name] = counts.get(f.query_name, 0) + 1
    assert counts == {
        "Trust_Boundary_Violation_in_Session_Variables": 5,
        "Log_Forging": 1,
        "Cookie_Poisoning": 1,
        "Missing_Content_Security_Policy": 1,
    }


def test_aggregate_report_findings_have_synthetic_ids():
    findings = parse_checkmarx_json(
        SAMPLE_DIR / "sample_improved_project_report.json"
    )
    assert all(f.finding_id.startswith("agg-") for f in findings)


def test_aggregate_flag_false_for_perfinding_export():
    findings = parse_checkmarx_json(
        SAMPLE_DIR / "sample_checkmarx_export.json"
    )
    assert not is_aggregate_findings(findings)


# ---------------------------------------------------------------------------
# Unsupported shape
# ---------------------------------------------------------------------------


def test_unrecognized_shape_raises(tmp_path: Path):
    junk = {"unrelated": [1, 2, 3]}
    path = tmp_path / "junk.json"
    path.write_text(json.dumps(junk), encoding="utf-8")

    with pytest.raises(UnsupportedReportShapeError):
        parse_checkmarx_json(path)


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        parse_checkmarx_json(tmp_path / "does_not_exist.json")


def test_invalid_json_raises(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        parse_checkmarx_json(path)
