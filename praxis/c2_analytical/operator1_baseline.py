"""C2 §3 — Operator 1: Baseline / Seasonality.

Implements:
- Same-weekday rolling mean/std for day-grain KPIs
- Pooled numerator/denominator for ratio KPIs
- INSUFFICIENT_HISTORY hard floor (< 3 clean same-weekday days for day-grain)
- LOW vs HIGH baseline confidence

GENERICITY FIX (Task 1): grain_type and aggregation_method are now read
from the KPI contract at runtime.  No kpi_id string literals here.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

from praxis.c1_data_foundation.kpi_contracts import get_grain_type, get_kpi_materiality_policy

class BaselineConfidence(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class BaselineOutcome(str, Enum):
    OK = "OK"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"


@dataclass
class BaselineResult:
    outcome: BaselineOutcome
    baseline_mean: Optional[float] = None
    baseline_std: Optional[float] = None
    pooled_numerator: Optional[float] = None   # for ratio KPIs
    pooled_denominator: Optional[float] = None  # for ratio KPIs
    window_size_used: int = 0
    baseline_confidence: Optional[BaselineConfidence] = None
    reason: Optional[str] = None  # populated when outcome=INSUFFICIENT_HISTORY

    @property
    def is_insufficient(self) -> bool:
        return self.outcome == BaselineOutcome.INSUFFICIENT_HISTORY


# C2 §3 Operator 1: INSUFFICIENT_HISTORY floor
MIN_CLEAN_DAYS = 3      # below this → INSUFFICIENT_HISTORY, not LOW
HIGH_THRESHOLD_DAYS = 7  # >= 7 clean days → HIGH confidence
TARGET_WINDOW_DAYS = 14  # target


def compute_baseline(
    kpi_id: str,
    target_day_or_month: str,
    history: List[Dict],
) -> "BaselineResult":
    """
    For day-grain KPIs: collect same-weekday clean days from history.
    For month-grain KPIs: collect clean prior months.
    Returns BaselineResult with outcome=INSUFFICIENT_HISTORY if below floor.

    GENERICITY: grain_type is read from the KPI contract, not from a
    hardcoded set of kpi_id string literals.
    """
    grain_type = get_grain_type(kpi_id)          # reads contract
    policy = get_kpi_materiality_policy(kpi_id)  # reads contract
    agg_method = policy.get("stat_test", "proportion_z")
    is_ratio = agg_method in ("proportion_z", "relative_change") or (
        get_grain_type(kpi_id) == "day" and agg_method != "z_score"
    )
    # More precise: read aggregation_method from contract
    from praxis.c1_data_foundation.kpi_contracts import get_contract
    contract_agg = get_contract(kpi_id).get("aggregation_method", "additive")
    is_ratio = contract_agg in ("ratio",)

    if grain_type == "month":
        return _compute_month_baseline(history)
    else:
        return _compute_day_baseline(kpi_id, target_day_or_month, history, is_ratio=is_ratio)


def _compute_day_baseline(kpi_id: str, target_day: str,
                           history: List[Dict],
                           is_ratio: bool = False) -> "BaselineResult":
    from datetime import date
    target = date.fromisoformat(target_day)
    target_weekday = target.weekday()

    clean_days = []
    for h in history:
        if h.get("state") not in ("FRESH", None):
            continue
        try:
            period_date = date.fromisoformat(str(h["period"]))
        except Exception:
            continue
        if period_date >= target:
            continue
        if period_date.weekday() != target_weekday:
            continue
        clean_days.append(h)

    clean_days.sort(key=lambda x: x["period"], reverse=True)
    clean_days = clean_days[:TARGET_WINDOW_DAYS]
    n = len(clean_days)

    if n < MIN_CLEAN_DAYS:
        return BaselineResult(
            outcome=BaselineOutcome.INSUFFICIENT_HISTORY,
            window_size_used=n,
            reason=f"<{MIN_CLEAN_DAYS} clean same-weekday days (found {n})",
        )

    confidence = BaselineConfidence.HIGH if n >= HIGH_THRESHOLD_DAYS else BaselineConfidence.LOW

    if is_ratio:
        total_num = sum(float(h.get("numerator", 0)) for h in clean_days)
        total_den = sum(float(h.get("denominator", 1)) for h in clean_days)
        pooled_rate = (total_num / total_den * 100) if total_den > 0 else 0
        daily_rates = []
        for h in clean_days:
            d = float(h.get("denominator", 1))
            if d > 0:
                daily_rates.append(float(h.get("numerator", 0)) / d * 100)
        mean_val = pooled_rate
        std_val = _std(daily_rates)
        return BaselineResult(
            outcome=BaselineOutcome.OK,
            baseline_mean=mean_val,
            baseline_std=std_val,
            pooled_numerator=total_num,
            pooled_denominator=total_den,
            window_size_used=n,
            baseline_confidence=confidence,
        )
    else:
        values = [float(h.get("value", 0)) for h in clean_days]
        mean_val = sum(values) / len(values)
        std_val = _std(values)
        return BaselineResult(
            outcome=BaselineOutcome.OK,
            baseline_mean=mean_val,
            baseline_std=std_val,
            window_size_used=n,
            baseline_confidence=confidence,
        )


def _compute_month_baseline(history: List[Dict]) -> BaselineResult:
    """
    C2 §3 Operator 1 for RPR (month-grain):
    - 0 clean prior months → INSUFFICIENT_HISTORY
    - 1 clean month → LOW
    - >= 2 clean months → HIGH
    """
    clean_months = [
        h for h in history
        if h.get("state") in ("FRESH", None)
    ]
    n = len(clean_months)

    if n == 0:
        return BaselineResult(
            outcome=BaselineOutcome.INSUFFICIENT_HISTORY,
            window_size_used=0,
            reason="no prior month to compare",
        )

    confidence = BaselineConfidence.HIGH if n >= 2 else BaselineConfidence.LOW
    values = [float(h.get("value", 0)) for h in clean_months]
    mean_val = sum(values) / len(values)
    std_val = _std(values)
    return BaselineResult(
        outcome=BaselineOutcome.OK,
        baseline_mean=mean_val,
        baseline_std=std_val,
        window_size_used=n,
        baseline_confidence=confidence,
    )


def _std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)
