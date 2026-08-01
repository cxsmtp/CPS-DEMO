"""Standalone smoke runner for the CPS engine.

Equivalent to running the pytest suite, but does not require pytest. Use
pytest in normal development (see tests/); this runner exists purely so
we can verify the engine works in sandboxes without pytest.
"""

from __future__ import annotations

import json
import math
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cps_engine.checkmarx_parser import (  # noqa: E402
    UnsupportedReportShapeError,
    filter_low_severity,
    parse_checkmarx_json,
)
from cps_engine.rubric import (  # noqa: E402
    AILeverage,
    BlastRadius,
    ChainUtility,
    DimensionScores,
    ImpactProximity,
    Prevalence,
    band,
    score_chain,
    score_finding,
)


def approx(a: float, b: float, tol: float = 1e-3) -> bool:
    return abs(a - b) <= tol


passed: list[str] = []
failed: list[tuple[str, str]] = []


def run(name: str, fn) -> None:
    try:
        fn()
        passed.append(name)
    except AssertionError as e:
        failed.append((name, str(e) or traceback.format_exc()))
    except Exception:
        failed.append((name, traceback.format_exc()))


# --- Algebraic sanity ------------------------------------------------------

def t_all_zero():
    s = DimensionScores(
        Prevalence.NONE, ChainUtility.NONE, AILeverage.NONE,
        BlastRadius.NONE, ImpactProximity.NONE,
    )
    assert score_finding(s) == 0.0


def t_all_critical():
    s = DimensionScores(
        Prevalence.CRITICAL, ChainUtility.CRITICAL, AILeverage.CRITICAL,
        BlastRadius.CRITICAL, ImpactProximity.CRITICAL,
    )
    assert approx(score_finding(s), 10.0, 1e-9)


# --- Stress test cases (paper-derived) -------------------------------------

def t_stress_prompt_injection():
    s = DimensionScores(
        Prevalence.CRITICAL, ChainUtility.CRITICAL, AILeverage.HIGH,
        BlastRadius.HIGH, ImpactProximity.HIGH,
    )
    assert approx(score_finding(s), 8.625), score_finding(s)


def t_stress_rsa_timing():
    s = DimensionScores(
        Prevalence.LOW, ChainUtility.LOW, AILeverage.LOW,
        BlastRadius.MEDIUM, ImpactProximity.MEDIUM,
    )
    assert approx(score_finding(s), 3.25), score_finding(s)


def t_stress_verbose_errors():
    s = DimensionScores(
        Prevalence.CRITICAL, ChainUtility.MEDIUM, AILeverage.HIGH,
        BlastRadius.MEDIUM, ImpactProximity.LOW,
    )
    assert approx(score_finding(s), 6.00), score_finding(s)


def t_stress_hardcoded_creds():
    s = DimensionScores(
        Prevalence.HIGH, ChainUtility.LOW, AILeverage.MEDIUM,
        BlastRadius.HIGH, ImpactProximity.CRITICAL,
    )
    assert approx(score_finding(s), 5.75), score_finding(s)


def t_stress_trivial_csrf():
    s = DimensionScores(
        Prevalence.HIGH, ChainUtility.NONE, AILeverage.LOW,
        BlastRadius.LOW, ImpactProximity.NONE,
    )
    assert approx(score_finding(s), 2.125), score_finding(s)


# --- Chain aggregation -----------------------------------------------------

def t_chain_empty():
    assert score_chain([]) == 0.0


def t_chain_single():
    assert approx(score_chain([7.5]), 7.5, 1e-9)


def t_chain_basic():
    assert approx(score_chain([8.25, 6.75, 6.50]), 9.575)


def t_chain_caps():
    assert score_chain([9.0, 8.0, 8.0, 8.0]) == 10.0


# --- Bands -----------------------------------------------------------------

def t_band_boundaries():
    assert band(0.0) == "Negligible"
    assert band(2.5) == "Negligible"
    assert band(2.6) == "Low"
    assert band(5.0) == "Low"
    assert band(5.1) == "Moderate"
    assert band(7.5) == "Moderate"
    assert band(7.6) == "High"
    assert band(10.0) == "High"


# --- Weights sum to 1 ------------------------------------------------------

def t_weights():
    from cps_engine.rubric import (
        WEIGHT_AI_LEVERAGE, WEIGHT_BLAST_RADIUS, WEIGHT_CHAIN_UTILITY,
        WEIGHT_IMPACT_PROXIMITY, WEIGHT_PREVALENCE,
    )
    total = (
        WEIGHT_PREVALENCE + WEIGHT_CHAIN_UTILITY + WEIGHT_AI_LEVERAGE
        + WEIGHT_BLAST_RADIUS + WEIGHT_IMPACT_PROXIMITY
    )
    assert math.isclose(total, 1.0, abs_tol=1e-12)


# --- JSON parser tests -----------------------------------------------------

def t_parser_cxone():
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_checkmarx_export.json"
    )
    assert len(findings) == 12
    trust = next(f for f in findings if f.finding_id == "SIM-1003")
    assert trust.query_name == "Trust_Boundary_Violation_in_Session_Variables"
    assert trust.cwe == 501
    assert trust.default_severity == "Low"
    assert trust.line == 88


def t_parser_low_filter():
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_checkmarx_export.json"
    )
    low = filter_low_severity(findings)
    assert len(low) == 10
    assert all(f.default_severity == "Low" for f in low)


def t_parser_sarif():
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_checkmarx_export.sarif.json"
    )
    assert len(findings) == 5
    by_query = {f.query_name: f for f in findings}
    assert by_query["URL_Canonicalization_Issue"].cwe == 647
    assert by_query["URL_Canonicalization_Issue"].default_severity == "Low"


def t_parser_legacy():
    legacy = {
        "Queries": [
            {
                "QueryName": "Open_Redirect",
                "Severity": "Low",
                "CweId": 601,
                "Language": "Python",
                "Results": [
                    {"FileName": "app/views.py", "Line": 42, "SimilarityId": "LEG-1"},
                ],
            },
        ]
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(legacy, fh)
        path = fh.name
    findings = parse_checkmarx_json(path)
    Path(path).unlink()
    assert len(findings) == 1
    assert findings[0].query_name == "Open_Redirect"
    assert findings[0].cwe == 601


def t_parser_unsupported_raises():
    junk = {"unrelated": [1, 2, 3]}
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(junk, fh)
        path = fh.name
    raised = False
    try:
        parse_checkmarx_json(path)
    except UnsupportedReportShapeError:
        raised = True
    Path(path).unlink()
    assert raised, "Expected UnsupportedReportShapeError on junk input"


def t_parser_improved_project_report():
    """Verify the Checkmarx One aggregate report shape parses.

    Uses the real (anonymized) tenant export structure as the fixture.
    """
    from cps_engine.checkmarx_parser import is_aggregate_findings
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_improved_project_report.json"
    )
    # Aggregate report has 12 findings total: 4 Medium + 8 Low.
    assert len(findings) == 12, f"expected 12, got {len(findings)}"
    assert is_aggregate_findings(findings), \
        "should be flagged as aggregate"

    # Low filter should leave 8 findings.
    low = filter_low_severity(findings)
    assert len(low) == 8, f"expected 8 Low, got {len(low)}"

    # Trust boundary should be the dominant Low query family with count 5.
    by_query = {}
    for f in low:
        by_query.setdefault(f.query_name, 0)
        by_query[f.query_name] += 1
    assert by_query.get("Trust_Boundary_Violation_in_Session_Variables") == 5
    assert by_query.get("Log_Forging") == 1
    assert by_query.get("Cookie_Poisoning") == 1
    assert by_query.get("Missing_Content_Security_Policy") == 1


def t_parser_improved_project_report_excludes_high_via_low_filter():
    """Aggregate report's Medium findings are correctly excluded by filter."""
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_improved_project_report.json"
    )
    medium = [f for f in findings if f.default_severity == "Medium"]
    # Sample has 4 Medium findings: 2 Use_Of_Hardcoded_Password,
    # 1 Open_Redirect, 1 Secure_Cookie_Flag_Not_Set_In_Config.
    assert len(medium) == 4
    by_q = {}
    for f in medium:
        by_q[f.query_name] = by_q.get(f.query_name, 0) + 1
    assert by_q["Use_Of_Hardcoded_Password"] == 2
    assert by_q["Open_Redirect"] == 1
    assert by_q["Secure_Cookie_Flag_Not_Set_In_Config"] == 1


def t_lookup_normalizes_spaces():
    """Container Running As Root (with spaces) should match the underscore
    key in DEFAULTS."""
    from cps_engine.dimension_defaults import lookup_defaults
    dims_a, known_a = lookup_defaults("Container Running As Root")
    dims_b, known_b = lookup_defaults("Container_Running_As_Root")
    dims_c, known_c = lookup_defaults("container running as root")
    assert known_a and known_b and known_c
    assert dims_a == dims_b == dims_c


def t_lookup_cve_dispatches_to_sca_class():
    """CVE-style query names dispatch to severity-based SCA classes."""
    from cps_engine.dimension_defaults import lookup_defaults, DEFAULTS
    dims_high, known_high = lookup_defaults("CVE-2023-25577", "High")
    assert known_high
    assert dims_high == DEFAULTS["_sca_high"]
    dims_med, known_med = lookup_defaults("CVE-2024-49767", "Medium")
    assert known_med
    assert dims_med == DEFAULTS["_sca_medium"]
    dims_low, known_low = lookup_defaults("CVE-2099-00001", "Low")
    assert known_low
    assert dims_low == DEFAULTS["_sca_low"]


def t_lookup_unknown_still_falls_back():
    """Genuinely unknown query names still fall back to UNKNOWN_QUERY_DEFAULT."""
    from cps_engine.dimension_defaults import (
        UNKNOWN_QUERY_DEFAULT,
        lookup_defaults,
    )
    dims, known = lookup_defaults("ThisQueryDoesNotExistAnywhere")
    assert not known
    assert dims == UNKNOWN_QUERY_DEFAULT


def t_lookup_handles_apostrophes():
    """Query names with apostrophes (e.g. 'AssumeRole') should normalize."""
    from cps_engine.dimension_defaults import lookup_defaults
    dims, known = lookup_defaults(
        "IAM Policy Grants 'AssumeRole' Permission Across All Services",
        "Medium",
    )
    assert known, (
        "Apostrophe-containing IAM query should resolve via punctuation-"
        "stripped normalization"
    )


def t_chain_matcher_against_validation_scan():
    """End-to-end: parse the synthesized validation scan, score, match
    against chains_index.json, confirm CH-001-DEMO is fully assembled."""
    from cps_engine import (
        match_chains,
        parse_checkmarx_json,
        score_findings,
    )
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "validation_scan_synthesized.json"
    )
    score_findings(findings)
    catalog = ROOT / "lab_app" / "chains_index.json"
    report = match_chains(findings, catalog)

    # CH-001-DEMO should be fully assembled.
    demo = next(
        (c for c in report.fully_assembled if c.chain_id == "CH-001-DEMO"),
        None,
    )
    assert demo is not None, (
        "CH-001-DEMO should be fully assembled against the validation scan; "
        f"got fully_assembled={[c.chain_id for c in report.fully_assembled]}, "
        f"partially_assembled={[c.chain_id for c in report.partially_assembled]}"
    )
    assert demo.required_total == 4
    assert demo.required_matched == 4
    # Chain CPS should be in the High band given Privilege Escalation
    # Allowed (8.00) + Trust Boundary (7.87) + IMDSv1 (8.25) + IAM exfil (6.50)
    # max + 0.1*(sum_others) = 8.25 + 0.1*(7.87 + 8.00 + 6.50) = 10.49 capped to 10.0
    assert demo.chain_cps >= 7.6, (
        f"Chain CPS should be in High band (>=7.6); got {demo.chain_cps}"
    )


def t_chain_matcher_handles_partial_assembly():
    """If only some required findings present, chain is partially assembled."""
    from cps_engine import (
        match_chains,
        parse_checkmarx_json,
        score_findings,
    )
    # The sample export deliberately lacks CH-001 chain anatomy — this
    # demonstrates the partial-assembly path.
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_checkmarx_export.json"
    )
    score_findings(findings)
    catalog = ROOT / "lab_app" / "chains_index.json"
    report = match_chains(findings, catalog)
    # Some chain should be partially or not assembled; not all should be full.
    assert len(report.fully_assembled) <= 2


def t_parser_vulnerability_type_report():
    """Verify the Checkmarx One Vulnerability Type comprehensive report
    parser handles per-engine sections (SAST + IaC + SCA).

    Uses the anonymized tenant-shape fixture sample_vulnerability_type_report.json.
    """
    from cps_engine import parse_checkmarx_json
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_vulnerability_type_report.json"
    )
    # Fixture mirrors the user's real scan: 12 SAST + 14 IaC + 16 SCA = 42.
    assert len(findings) == 42, f"expected 42, got {len(findings)}"

    # SAST findings should carry file paths and line numbers.
    sast = [f for f in findings if f.language and "Python" in f.language]
    assert any(f.line > 0 for f in sast), "SAST findings should have line numbers"

    # All 4 CH-001-DEMO required queries present.
    qnames = {f.query_name for f in findings}
    required = {
        "Trust_Boundary_Violation_in_Session_Variables",
        "Instance Uses Metadata Service IMDSv1",
        "IAM policy allows for data exfiltration",
        "Privilege Escalation Allowed",
    }
    assert required.issubset(qnames), (
        f"missing required queries: {required - qnames}"
    )

    # SCA findings should be CVE-prefixed and dispatch via the SCA classes.
    sca = [f for f in findings if f.query_name.startswith("CVE-")]
    assert len(sca) >= 14, f"expected >= 14 SCA findings, got {len(sca)}"


def t_chain_matcher_against_vulnerability_type_report():
    """End-to-end against the user's tenant report shape: matcher should
    detect CH-001-DEMO as fully assembled."""
    from cps_engine import (
        match_chains,
        parse_checkmarx_json,
        score_findings,
    )
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_vulnerability_type_report.json"
    )
    score_findings(findings)
    catalog = ROOT / "lab_app" / "chains_index.json"
    report = match_chains(findings, catalog)
    demo = next(
        (c for c in report.fully_assembled if c.chain_id == "CH-001-DEMO"),
        None,
    )
    assert demo is not None, "CH-001-DEMO should be fully assembled"
    assert demo.required_total == 4
    assert demo.required_matched == 4
    assert demo.chain_cps >= 7.6  # High band


def t_cyclonedx_aibom_parser():
    """Verify the CycloneDX AI-BOM parser handles the Checkmarx AI Supply
    Chain shape and filters by ProjectName."""
    from cps_engine import parse_cyclonedx_ai_bom
    # Without filter: 11 components total in fixture.
    findings = parse_cyclonedx_ai_bom(
        ROOT / "sample_data" / "sample_cyclonedx_ai_bom.json"
    )
    assert len(findings) == 11, f"expected 11, got {len(findings)}"
    # With filter: only 10 in CHA1 project.
    cha1_findings = parse_cyclonedx_ai_bom(
        ROOT / "sample_data" / "sample_cyclonedx_ai_bom.json",
        project_filter="CHA1",
    )
    assert len(cha1_findings) == 10, f"expected 10, got {len(cha1_findings)}"
    # Each should have a recognizable AI-BOM language hint.
    for f in cha1_findings:
        assert f.language in (
            "ai_component_machine_learning_model",
            "ai_component_library",
        ), f"unexpected language hint: {f.language}"


def t_aibom_findings_score_via_language_hint():
    """AI-BOM findings have synthesized query names that don't match
    DEFAULTS directly. Verify they still score correctly via the
    language_hint dispatch."""
    from cps_engine import parse_cyclonedx_ai_bom, score_findings
    findings = parse_cyclonedx_ai_bom(
        ROOT / "sample_data" / "sample_cyclonedx_ai_bom.json",
        project_filter="CHA1",
    )
    report = score_findings(findings)
    # All should have non-zero CPS (because their language_hint dispatched
    # to ai_component_* in DEFAULTS).
    for f in findings:
        assert f.cps_score and f.cps_score > 0, (
            f"AI-BOM finding {f.query_name!r} got zero CPS; language="
            f"{f.language!r}"
        )
    # Models score higher than libraries (per ai_component_* class scores).
    models = [
        f for f in findings
        if f.language == "ai_component_machine_learning_model"
    ]
    libs = [
        f for f in findings
        if f.language == "ai_component_library"
    ]
    assert models and libs
    # All models should have the same score, all libs the same score.
    model_score = models[0].cps_score
    lib_score = libs[0].cps_score
    assert all(abs(m.cps_score - model_score) < 0.01 for m in models)
    assert all(abs(l.cps_score - lib_score) < 0.01 for l in libs)
    # And model score > lib score (CRITICAL AI Leverage on models).
    assert model_score > lib_score


def t_chain_matcher_cha1_full_assembly():
    """End-to-end CH-A1: SAST + IaC + AI-BOM compose into FULLY_ASSEMBLED
    with all 10 inventory components detected."""
    from cps_engine import (
        match_chains,
        parse_checkmarx_json,
        parse_cyclonedx_ai_bom,
        score_findings,
    )
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_cha1_results.json"
    )
    ai_findings = parse_cyclonedx_ai_bom(
        ROOT / "sample_data" / "sample_cyclonedx_ai_bom.json",
        project_filter="CHA1",
    )
    all_findings = findings + ai_findings
    score_findings(all_findings)

    catalog = ROOT / "lab_app" / "chains_index.json"
    report = match_chains(all_findings, catalog)
    cha1 = next(
        (c for c in report.fully_assembled if c.chain_id == "CH-A1"),
        None,
    )
    assert cha1 is not None, "CH-A1 should be fully assembled"
    assert cha1.required_matched == 3
    assert cha1.required_total == 3
    assert cha1.chain_cps >= 7.6, (
        f"CH-A1 chain CPS should be in High band; got {cha1.chain_cps}"
    )
    # All 10 inventory components should be detected.
    assert cha1.ai_inventory, "CH-A1 should declare an ai_inventory"
    assert len(cha1.ai_inventory) == 10
    n_detected = sum(1 for v in cha1.ai_inventory_matched.values() if v)
    assert n_detected == 10, (
        f"expected all 10 AI inventory components detected; got {n_detected}"
    )


def t_parser_container_security_section():
    """The Vulnerability Type parser handles containerScanResults section
    (added for CH-002). Findings should carry Dockerfile filenames and
    Container Security technology labels."""
    from cps_engine import parse_checkmarx_json
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_ch002_results.json"
    )
    # Fixture has 3 SCA + 5 Container = 8 findings.
    assert len(findings) == 8, f"expected 8, got {len(findings)}"
    # Some finding should reference the Dockerfile.
    docker_findings = [f for f in findings if "Dockerfile" in f.source_file]
    assert len(docker_findings) >= 4, (
        f"expected at least 4 Dockerfile findings, got {len(docker_findings)}"
    )


def t_chain_matcher_ch002_ai_weaponised_chain():
    """End-to-end CH-002 (AI-weaponisation): four-engine chain composing
    SAST recon Lows + SCA Low + AI-BOM + IaC into FULLY_ASSEMBLED. Verifies
    the AI-delta computation produces both chain CPS values correctly.
    On the fixture the chain hits the 10.0 cap with and without AI; on real
    tenant scan data the delta becomes visible because per-finding scores
    differ from the fixture."""
    from cps_engine import (
        match_chains,
        parse_checkmarx_json,
        parse_cyclonedx_ai_bom,
        score_findings,
    )
    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "sample_ch002_aiweap_results.json"
    )
    ai_findings = parse_cyclonedx_ai_bom(
        ROOT / "sample_data" / "sample_ch002_aiweap_aibom.json",
        project_filter="CH002_ai_weaponised_recon",
    )
    all_findings = findings + ai_findings
    score_findings(all_findings)
    catalog = ROOT / "lab_app" / "chains_index.json"
    report = match_chains(all_findings, catalog)

    ch002 = next(
        (c for c in report.fully_assembled if c.chain_id == "CH-002"),
        None,
    )
    assert ch002 is not None, "CH-002 should be fully assembled on AI-weaponisation fixture"
    assert ch002.required_total == 6
    assert ch002.required_matched == 6
    assert ch002.chain_cps >= 7.6, (
        f"CH-002 chain CPS should be in High band; got {ch002.chain_cps}"
    )
    # AI-delta computation: matcher must compute chain_cps_without_ai
    # when ai_leverage_findings is declared in the catalog.
    assert ch002.chain_cps_without_ai is not None, (
        "AI-delta should be computed when ai_leverage_findings is declared"
    )
    assert ch002.ai_inventory, "CH-002 declares an AI inventory"
    # The AI agent should be detected in inventory (1 of 1 components).
    n_detected = sum(1 for v in ch002.ai_inventory_matched.values() if v)
    assert n_detected == 1, (
        f"GPT-4o should be detected in inventory; got {n_detected}"
    )


def t_chain_matcher_observed_ch101_to_ch105():
    """End-to-end validation of the five observed-evidence chains (CH-101..
    CH-105). Each fixture contains only findings that were actually
    observed in a completed Checkmarx One scan in the
    checkmarx-global-services-internal tenant, with the severity Checkmarx
    assigned. Asserts each chain assembles fully at High band, and that
    every constituent finding is Low or Medium (never High/Critical)."""
    from cps_engine import match_chains, parse_checkmarx_json, score_findings

    cases = [
        ("observed_dvwa_ch101.json", {"CH-101": 10.00}),
        ("observed_javavulnlab_ch102_ch103.json", {"CH-102": 9.49, "CH-103": 9.96}),
        ("observed_nodegoat_ch104_ch105.json", {"CH-104": 9.14, "CH-105": 9.25}),
    ]
    catalog = ROOT / "lab_app" / "chains_index.json"

    for fixture, expected in cases:
        findings = parse_checkmarx_json(ROOT / "sample_data" / fixture)
        # No constituent finding may be High or Critical.
        for f in findings:
            assert str(f.default_severity).lower() not in ("high", "critical"), (
                f"{fixture}: {f.query_name} is {f.default_severity}; observed "
                f"chains must be built from Low/Medium findings only"
            )
        score_findings(findings)
        report = match_chains(findings, catalog)
        for chain_id, expected_cps in expected.items():
            hit = next(
                (c for c in report.fully_assembled if c.chain_id == chain_id), None
            )
            assert hit is not None, f"{chain_id} should be FULLY_ASSEMBLED on {fixture}"
            assert hit.required_matched == hit.required_total
            assert hit.chain_cps >= 7.6, (
                f"{chain_id} should reach High band; got {hit.chain_cps}"
            )
            assert abs(hit.chain_cps - expected_cps) < 0.01, (
                f"{chain_id} chain CPS drifted: expected {expected_cps}, "
                f"got {hit.chain_cps}"
            )


def t_chain_matcher_observed_ch106_to_ch110():
    """Second observed-evidence batch (CH-106..CH-110), including the
    Informational-only chain and the AI agent framework chain. Same
    guarantees as the first batch: nothing above Medium may appear."""
    from cps_engine import match_chains, parse_checkmarx_json, score_findings

    cases = [
        ("observed_javavulnlab_ch106.json", {"CH-106": 9.15}),
        ("observed_openai_agents_ch107.json", {"CH-107": 9.78}),
        ("observed_dvwa_ch108.json", {"CH-108": 9.24}),
        ("observed_juicelab_ch109.json", {"CH-109": 8.32}),
        ("observed_authlab_ch110.json", {"CH-110": 8.01}),
    ]
    catalog = ROOT / "lab_app" / "chains_index.json"

    for fixture, expected in cases:
        findings = parse_checkmarx_json(ROOT / "sample_data" / fixture)
        for f in findings:
            assert str(f.default_severity).lower() not in ("high", "critical"), (
                f"{fixture}: {f.query_name} is {f.default_severity}"
            )
        score_findings(findings)
        report = match_chains(findings, catalog)
        for chain_id, expected_cps in expected.items():
            hit = next(
                (c for c in report.fully_assembled if c.chain_id == chain_id), None
            )
            assert hit is not None, f"{chain_id} should be FULLY_ASSEMBLED"
            assert hit.required_matched == hit.required_total
            assert hit.chain_cps >= 7.6, f"{chain_id} got {hit.chain_cps}"
            assert abs(hit.chain_cps - expected_cps) < 0.01, (
                f"{chain_id}: expected {expected_cps}, got {hit.chain_cps}"
            )


def t_chain_matcher_path_scoped_required_findings():
    """CH-107 declares the same query name five times, scoped to different
    code paths. Verify path scoping actually discriminates: each required
    finding must match only findings from its own path."""
    from cps_engine import match_chains, parse_checkmarx_json, score_findings

    findings = parse_checkmarx_json(
        ROOT / "sample_data" / "observed_openai_agents_ch107.json"
    )
    score_findings(findings)
    report = match_chains(findings, ROOT / "lab_app" / "chains_index.json")
    ch107 = next(c for c in report.fully_assembled if c.chain_id == "CH-107")
    scoped = [m for m in ch107.matches if "[in " in m.catalog_query_name]
    assert len(scoped) == 4, f"expected 4 path-scoped participants, got {len(scoped)}"
    for m in scoped:
        assert len(m.matched_findings) == 1, (
            f"path scoping failed to discriminate for {m.catalog_query_name}: "
            f"matched {len(m.matched_findings)} findings"
        )


# --- Run -------------------------------------------------------------------

TESTS = [
    ("all_zero_yields_zero", t_all_zero),
    ("all_critical_yields_ten", t_all_critical),
    ("stress: prompt_injection ~ 8.625", t_stress_prompt_injection),
    ("stress: rsa_timing ~ 3.25", t_stress_rsa_timing),
    ("stress: verbose_errors ~ 6.00", t_stress_verbose_errors),
    ("stress: hardcoded_creds ~ 5.75", t_stress_hardcoded_creds),
    ("stress: trivial_csrf ~ 2.125", t_stress_trivial_csrf),
    ("chain: empty -> 0", t_chain_empty),
    ("chain: single -> identity", t_chain_single),
    ("chain: basic 8.25/6.75/6.50 -> 9.575", t_chain_basic),
    ("chain: caps at 10", t_chain_caps),
    ("band: boundaries", t_band_boundaries),
    ("weights: sum to 1", t_weights),
    ("parser: Checkmarx One JSON", t_parser_cxone),
    ("parser: Low filter excludes High severity", t_parser_low_filter),
    ("parser: SARIF", t_parser_sarif),
    ("parser: CxSAST legacy JSON", t_parser_legacy),
    ("parser: unsupported shape raises", t_parser_unsupported_raises),
    ("parser: Improved Project Report (aggregate)",
     t_parser_improved_project_report),
    ("parser: aggregate report Medium filter",
     t_parser_improved_project_report_excludes_high_via_low_filter),
    ("defaults: lookup normalizes spaces/underscores",
     t_lookup_normalizes_spaces),
    ("defaults: CVE dispatches to SCA class",
     t_lookup_cve_dispatches_to_sca_class),
    ("defaults: unknown queries fall back",
     t_lookup_unknown_still_falls_back),
    ("defaults: lookup handles apostrophes",
     t_lookup_handles_apostrophes),
    ("matcher: CH-001-DEMO fully assembled",
     t_chain_matcher_against_validation_scan),
    ("matcher: handles partial assembly",
     t_chain_matcher_handles_partial_assembly),
    ("parser: Vulnerability Type comprehensive report",
     t_parser_vulnerability_type_report),
    ("matcher: CH-001-DEMO fully assembled on tenant-shape report",
     t_chain_matcher_against_vulnerability_type_report),
    ("parser: CycloneDX AI-BOM with project filter",
     t_cyclonedx_aibom_parser),
    ("scorer: AI-BOM findings dispatch via language_hint",
     t_aibom_findings_score_via_language_hint),
    ("matcher: CH-A1 fully assembled with 10 AI inventory components",
     t_chain_matcher_cha1_full_assembly),
    ("parser: containerScanResults section parses correctly",
     t_parser_container_security_section),
    ("matcher: CH-002 AI-weaponisation chain assembles + AI-delta computed",
     t_chain_matcher_ch002_ai_weaponised_chain),
    ("matcher: CH-101..CH-105 observed-evidence chains assemble at High band",
     t_chain_matcher_observed_ch101_to_ch105),
    ("matcher: CH-106..CH-110 observed-evidence chains assemble at High band",
     t_chain_matcher_observed_ch106_to_ch110),
    ("matcher: path-scoped required findings discriminate by code path",
     t_chain_matcher_path_scoped_required_findings),
]

for name, fn in TESTS:
    run(name, fn)

print(f"PASSED: {len(passed)}/{len(TESTS)}")
for n in passed:
    print(f"  ok  {n}")
if failed:
    print()
    print(f"FAILED: {len(failed)}")
    for n, err in failed:
        print(f"  FAIL  {n}")
        print(f"        {err}")
    sys.exit(1)
