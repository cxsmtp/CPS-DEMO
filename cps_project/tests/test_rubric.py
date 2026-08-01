"""
Unit tests for cps_engine.rubric.

The tests fall into four categories:

1. Algebraic sanity:
   - Weights sum to 1.0 (tested at module import via assert).
   - All-zero scores yield 0.0.
   - All-four scores yield 10.0.
   - Score is monotonic in each dimension when others are held fixed.

2. Reproducibility of paper stress-test cases:
   - Prompt injection in AI agent (high-end of the rubric)
   - Timing side-channel in RSA (low-CPS for genuine high-CVSS issue)
   - Verbose error messages (catalog's central thesis: low default
     severity, moderate CPS)
   - Hardcoded credentials (high CPS but low Chain Utility)
   - Trivial CSRF on theme endpoint (correctly negligible)

3. Chain-level aggregation behavior:
   - Single finding equals its individual score.
   - Empty input is 0.0.
   - Cap at 10.0 holds when components saturate.
   - Alpha contribution behaves as documented.

4. Interpretive bands:
   - Boundary values map to the correct band.
"""

from __future__ import annotations

import math

import pytest

from cps_engine.rubric import (
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


# ---------------------------------------------------------------------------
# Algebraic sanity
# ---------------------------------------------------------------------------


def test_all_zero_scores_yield_zero() -> None:
    s = DimensionScores(
        Prevalence.NONE,
        ChainUtility.NONE,
        AILeverage.NONE,
        BlastRadius.NONE,
        ImpactProximity.NONE,
    )
    assert score_finding(s) == 0.0


def test_all_critical_scores_yield_ten() -> None:
    s = DimensionScores(
        Prevalence.CRITICAL,
        ChainUtility.CRITICAL,
        AILeverage.CRITICAL,
        BlastRadius.CRITICAL,
        ImpactProximity.CRITICAL,
    )
    assert score_finding(s) == pytest.approx(10.0, abs=1e-9)


def test_score_is_in_range() -> None:
    """Property check: random valid inputs always produce a value in [0, 10]."""
    import random
    rng = random.Random(0)
    for _ in range(200):
        s = DimensionScores(
            Prevalence(rng.randint(0, 4)),
            ChainUtility(rng.randint(0, 4)),
            AILeverage(rng.randint(0, 4)),
            BlastRadius(rng.randint(0, 4)),
            ImpactProximity(rng.randint(0, 4)),
        )
        cps = score_finding(s)
        assert 0.0 <= cps <= 10.0


def test_monotonicity_in_chain_utility() -> None:
    """Holding others fixed, raising Chain Utility never lowers the score."""
    base = {
        "prevalence": Prevalence.MEDIUM,
        "ai_leverage": AILeverage.MEDIUM,
        "blast_radius": BlastRadius.MEDIUM,
        "impact_proximity": ImpactProximity.MEDIUM,
    }
    last = -1.0
    for cu in (
        ChainUtility.NONE,
        ChainUtility.LOW,
        ChainUtility.MEDIUM,
        ChainUtility.HIGH,
        ChainUtility.CRITICAL,
    ):
        cps = score_finding(DimensionScores(chain_utility=cu, **base))
        assert cps >= last, f"non-monotonic at {cu}: {cps} < {last}"
        last = cps


# ---------------------------------------------------------------------------
# Paper stress-test cases (reproduce numbers from the rubric stress test)
# ---------------------------------------------------------------------------
# Each test below corresponds to a case worked through during catalog design.
# Numbers match those documented in the paper.


def test_stress_test_prompt_injection_high() -> None:
    """Prompt injection in agent with email + calendar tools.

    Expected CPS ~ 8.625 per the stress test.
    Inputs: P=4 C=4 A=3 B=3 I=3
    """
    s = DimensionScores(
        Prevalence.CRITICAL,
        ChainUtility.CRITICAL,
        AILeverage.HIGH,
        BlastRadius.HIGH,
        ImpactProximity.HIGH,
    )
    assert score_finding(s) == pytest.approx(8.625, abs=1e-3)


def test_stress_test_rsa_timing_side_channel_low_cps() -> None:
    """Timing side-channel in RSA: high standalone CVSS but low CPS.

    Expected CPS ~ 3.25 per the stress test.
    Inputs: P=1 C=1 A=1 B=2 I=2
    """
    s = DimensionScores(
        Prevalence.LOW,
        ChainUtility.LOW,
        AILeverage.LOW,
        BlastRadius.MEDIUM,
        ImpactProximity.MEDIUM,
    )
    assert score_finding(s) == pytest.approx(3.25, abs=1e-3)


def test_stress_test_verbose_errors_moderate_cps() -> None:
    """Verbose errors: traditionally Informational, CPS surfaces moderate risk.

    Expected CPS ~ 6.00 per the stress test.
    Inputs: P=4 C=2 A=3 B=2 I=1
    """
    s = DimensionScores(
        Prevalence.CRITICAL,
        ChainUtility.MEDIUM,
        AILeverage.HIGH,
        BlastRadius.MEDIUM,
        ImpactProximity.LOW,
    )
    assert score_finding(s) == pytest.approx(6.00, abs=1e-3)


def test_stress_test_hardcoded_credentials() -> None:
    """Hardcoded AWS credentials in public repo.

    Expected CPS ~ 5.75 per the stress test.
    Inputs: P=3 C=1 A=2 B=3 I=4
    """
    s = DimensionScores(
        Prevalence.HIGH,
        ChainUtility.LOW,
        AILeverage.MEDIUM,
        BlastRadius.HIGH,
        ImpactProximity.CRITICAL,
    )
    assert score_finding(s) == pytest.approx(5.75, abs=1e-3)


def test_stress_test_trivial_csrf_negligible() -> None:
    """CSRF on theme-change endpoint: rubric correctly produces low score.

    Expected CPS ~ 2.125 per the stress test.
    Inputs: P=3 C=0 A=1 B=1 I=0
    """
    s = DimensionScores(
        Prevalence.HIGH,
        ChainUtility.NONE,
        AILeverage.LOW,
        BlastRadius.LOW,
        ImpactProximity.NONE,
    )
    assert score_finding(s) == pytest.approx(2.125, abs=1e-3)


# ---------------------------------------------------------------------------
# Chain aggregation
# ---------------------------------------------------------------------------


def test_chain_empty_input_is_zero() -> None:
    assert score_chain([]) == 0.0


def test_chain_single_finding_equals_individual_score() -> None:
    assert score_chain([7.5]) == pytest.approx(7.5, abs=1e-9)


def test_chain_basic_aggregation() -> None:
    """CH-001-style chain: max=8.25 + 0.1*(6.75+6.50) = 9.575."""
    assert score_chain([8.25, 6.75, 6.50]) == pytest.approx(9.575, abs=1e-3)


def test_chain_caps_at_ten() -> None:
    """Chains that mathematically exceed 10 are capped (saturated)."""
    # 9.0 + 0.1 * (8 + 8 + 8) = 11.4, must clamp to 10.0
    assert score_chain([9.0, 8.0, 8.0, 8.0]) == 10.0


def test_chain_floors_at_zero() -> None:
    assert score_chain([0.0, 0.0]) == 0.0


# ---------------------------------------------------------------------------
# Interpretive bands
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        (0.0, "Negligible"),
        (2.5, "Negligible"),
        (2.6, "Low"),
        (5.0, "Low"),
        (5.1, "Moderate"),
        (7.5, "Moderate"),
        (7.6, "High"),
        (10.0, "High"),
    ],
)
def test_band_boundaries(value: float, expected: str) -> None:
    assert band(value) == expected


# ---------------------------------------------------------------------------
# Float-safety: weights sum exactly
# ---------------------------------------------------------------------------


def test_weights_sum_to_one() -> None:
    from cps_engine.rubric import (
        WEIGHT_AI_LEVERAGE,
        WEIGHT_BLAST_RADIUS,
        WEIGHT_CHAIN_UTILITY,
        WEIGHT_IMPACT_PROXIMITY,
        WEIGHT_PREVALENCE,
    )
    total = (
        WEIGHT_PREVALENCE
        + WEIGHT_CHAIN_UTILITY
        + WEIGHT_AI_LEVERAGE
        + WEIGHT_BLAST_RADIUS
        + WEIGHT_IMPACT_PROXIMITY
    )
    assert math.isclose(total, 1.0, abs_tol=1e-12)
