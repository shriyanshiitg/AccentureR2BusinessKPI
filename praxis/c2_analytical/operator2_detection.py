"""C2 §3 — Operator 2: Detection.

Implements the per-KPI materiality policy from C2 §1.

GENERICITY FIX (Task 1): All per-KPI thresholds and detection method
selection are now read from the KPI contract's 'materiality' sub-dict.
The if/else chain on kpi_id string literals has been replaced with a
contract-driven dispatch via get_kpi_materiality_policy().

Any new KPI registered in KPI_CONTRACTS with a valid 'materiality' block
will be handled automatically — no changes required here.

Strict AND rule — never a weighted score.
SKIPPED returned if inputs disqualify.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from praxis.c1_data_foundation.kpi_contracts import get_kpi_materiality_policy, KPI_CONTRACTS
from praxis.c1_data_foundation.schemas import DataState
from praxis.c2_analytical.operator1_baseline import BaselineResult


class DetectionOutcome(str, Enum):
    MATERIAL = "MATERIAL"
    NON_MATERIAL = "NON_MATERIAL"
    SKIPPED = "SKIPPED"


@dataclass
class DetectionResult:
    outcome: DetectionOutcome
    actual_value: Optional[float] = None
    delta_absolute: Optional[float] = None
    delta_relative: Optional[float] = None
    statistically_significant: Optional[bool] = None
    test_statistic: Optional[float] = None
    test_type: Optional[str] = None
    business_impact_value: Optional[float] = None
    business_impact_significant: Optional[bool] = None
    material: Optional[bool] = None
    evaluated_on_stale_input: bool = False
    partial_sources_excluded: Optional[list] = None
    conflicting_input: bool = False
    skip_reason: Optional[str] = None

    @property
    def is_material(self) -> bool:
        return self.material is True


def detect(
    kpi_id: str,
    actual_value: float,
    baseline: BaselineResult,
    data_state: DataState,
    numerator: Optional[float] = None,
    denominator: Optional[float] = None,
    partial_excluded: Optional[list] = None,
    conflicting_input: bool = False,
) -> DetectionResult:
    """
    Run the materiality gate for one KPI instance.
    Reads per-KPI thresholds from the KPI contract's 'materiality' block.
    Returns DetectionResult with outcome in {MATERIAL, NON_MATERIAL, SKIPPED}.
    """
    evaluated_on_stale = data_state == DataState.STALE

    if data_state in (DataState.MISSING, DataState.INVALID):
        return DetectionResult(
            outcome=DetectionOutcome.SKIPPED,
            skip_reason=f"C1 data state={data_state.value}",
        )

    if baseline.is_insufficient:
        return DetectionResult(
            outcome=DetectionOutcome.SKIPPED,
            skip_reason=f"INSUFFICIENT_HISTORY: {baseline.reason}",
        )

    # Read policy from contract — no kpi_id string literals
    try:
        policy = get_kpi_materiality_policy(kpi_id)
    except KeyError:
        return DetectionResult(
            outcome=DetectionOutcome.SKIPPED,
            skip_reason=f"Unknown kpi_id: {kpi_id}",
        )

    stat_test = policy.get("stat_test", "z_score")

    kwargs = dict(
        actual_value=actual_value,
        delta_absolute=actual_value - (baseline.baseline_mean or 0),
        evaluated_on_stale_input=evaluated_on_stale,
        partial_sources_excluded=partial_excluded,
        conflicting_input=conflicting_input,
    )

    if stat_test == "z_score":
        return _detect_additive(baseline, actual_value, policy, **kwargs)
    elif stat_test == "proportion_z":
        return _detect_ratio(baseline, actual_value, numerator, denominator, policy, **kwargs)
    elif stat_test == "relative_change":
        return _detect_relative(baseline, actual_value, policy, **kwargs)
    else:
        return DetectionResult(
            outcome=DetectionOutcome.SKIPPED,
            skip_reason=f"Unknown stat_test={stat_test!r} for kpi_id={kpi_id}",
        )


def _detect_additive(
    baseline: BaselineResult, actual: float, policy: dict, **kwargs
) -> DetectionResult:
    """z-score test for additive KPIs (e.g. zone_gmv)."""
    bm = baseline.baseline_mean or 0
    bs = baseline.baseline_std or 1
    delta_abs = actual - bm
    z_thresh = policy.get("z_threshold", 2.5)
    z = delta_abs / bs if bs > 0 else 0.0
    stat_sig = abs(z) >= z_thresh

    biz_floor_abs = policy.get("biz_floor_abs", 50_000)
    biz_floor_rel = policy.get("biz_floor_rel", 0.02)
    biz_floor = max(biz_floor_abs, biz_floor_rel * bm)
    biz_sig = abs(delta_abs) >= biz_floor
    mat = stat_sig and biz_sig

    return DetectionResult(
        outcome=DetectionOutcome.MATERIAL if mat else DetectionOutcome.NON_MATERIAL,
        actual_value=actual,
        delta_absolute=delta_abs,
        delta_relative=(delta_abs / bm) if bm != 0 else None,
        statistically_significant=stat_sig,
        test_statistic=z,
        test_type="z_score",
        business_impact_value=abs(delta_abs),
        business_impact_significant=biz_sig,
        material=mat,
        **{k: v for k, v in kwargs.items() if k not in ("actual_value", "delta_absolute")},
    )


def _detect_ratio(
    baseline: BaselineResult, actual: float,
    numerator: Optional[float], denominator: Optional[float],
    policy: dict, **kwargs
) -> DetectionResult:
    """Two-proportion z-test for ratio KPIs."""
    pool_n = baseline.pooled_numerator or 0
    pool_d = baseline.pooled_denominator or 1

    if denominator is None or denominator == 0:
        return DetectionResult(
            outcome=DetectionOutcome.SKIPPED,
            skip_reason="denominator is zero or missing",
            **{k: v for k, v in kwargs.items() if k not in ("actual_value", "delta_absolute")},
        )

    denom_floor = policy.get("denom_floor") or 0
    if denom_floor > 0 and denominator < denom_floor:
        return DetectionResult(
            outcome=DetectionOutcome.NON_MATERIAL,
            actual_value=actual,
            delta_absolute=actual - (pool_n / pool_d * 100 if pool_d > 0 else 0),
            statistically_significant=False,
            test_type="proportion_z",
            material=False,
            business_impact_value=None,
            business_impact_significant=False,
            **{k: v for k, v in kwargs.items() if k not in ("actual_value", "delta_absolute")},
        )

    n1 = numerator
    d1 = denominator
    n2 = pool_n / max(baseline.window_size_used, 1)
    d2 = pool_d / max(baseline.window_size_used, 1)

    p1 = n1 / d1 if d1 > 0 else 0
    p2 = n2 / d2 if d2 > 0 else 0
    p_pooled = (n1 + n2) / (d1 + d2) if (d1 + d2) > 0 else 0
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / d1 + 1 / d2)) if d1 > 0 and d2 > 0 else 1
    z = (p1 - p2) / se if se > 0 else 0.0
    p_val = 2 * (1 - _normal_cdf(abs(z)))

    p_thresh = policy.get("p_threshold", 0.05)
    stat_sig = p_val < p_thresh

    baseline_rate = (pool_n / pool_d) * 100 if pool_d > 0 else 0
    delta_abs = actual - baseline_rate

    floor = policy.get("biz_floor_pp", 3.0)
    low_vol_floor = policy.get("low_volume_floor_pp")
    low_vol_thresh = policy.get("low_volume_denom_threshold", 50)
    if low_vol_floor and denominator < low_vol_thresh:
        floor = low_vol_floor
    biz_sig = abs(delta_abs) >= floor

    mat = stat_sig and biz_sig

    return DetectionResult(
        outcome=DetectionOutcome.MATERIAL if mat else DetectionOutcome.NON_MATERIAL,
        actual_value=actual,
        delta_absolute=delta_abs,
        delta_relative=(delta_abs / baseline_rate) if baseline_rate != 0 else None,
        statistically_significant=stat_sig,
        test_statistic=p_val,
        test_type="proportion_z",
        business_impact_value=abs(delta_abs),
        business_impact_significant=biz_sig,
        material=mat,
        **{k: v for k, v in kwargs.items() if k not in ("actual_value", "delta_absolute")},
    )


def _detect_relative(
    baseline: BaselineResult, actual: float, policy: dict, **kwargs
) -> DetectionResult:
    """Relative-change test for month-grain KPIs (e.g. repeat_purchase_rate)."""
    bm = baseline.baseline_mean or 0
    delta_abs = actual - bm
    delta_rel = abs(delta_abs / bm) if bm != 0 else 0

    rel_thresh = policy.get("rel_threshold", 0.15)
    abs_thresh = policy.get("abs_threshold_pp", 5.0)
    biz_floor = policy.get("biz_floor_pp", 3.0)

    stat_sig = delta_rel >= rel_thresh or abs(delta_abs) >= abs_thresh
    biz_sig = abs(delta_abs) >= biz_floor
    mat = stat_sig and biz_sig

    return DetectionResult(
        outcome=DetectionOutcome.MATERIAL if mat else DetectionOutcome.NON_MATERIAL,
        actual_value=actual,
        delta_absolute=delta_abs,
        delta_relative=delta_rel if bm != 0 else None,
        statistically_significant=stat_sig,
        test_statistic=delta_rel,
        test_type="relative_change",
        business_impact_value=abs(delta_abs),
        business_impact_significant=biz_sig,
        material=mat,
        **{k: v for k, v in kwargs.items() if k not in ("actual_value", "delta_absolute")},
    )


def _normal_cdf(z: float) -> float:
    """Approximation of the standard normal CDF."""
    return (1.0 + math.erf(z / math.sqrt(2))) / 2
