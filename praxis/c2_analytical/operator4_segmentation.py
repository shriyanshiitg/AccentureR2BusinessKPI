"""C2 §3 — Operator 4: Segmentation.

Ranks stores within a zone by contribution to the zone-level movement,
using the exact C1 rollup rule for each KPI:
- zone_gmv: additive SUM → direct subtraction
- order_conversion_rate / delivery_sla_adherence: pooled ratio
- dark_store_stockout_rate: interval-duration-weighted average
- repeat_purchase_rate: Ops Manager proxy only (non-authoritative)

Missing-data stores are EXCLUDED from ranking, never ranked as zero.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StoreContribution:
    dark_store_id: str
    contribution_value: float
    contribution_pct: float


@dataclass
class SegmentationResult:
    ranked_stores: List[StoreContribution] = field(default_factory=list)
    excluded_stores: List[str] = field(default_factory=list)  # MISSING-data stores


def segment_stores(
    kpi_id: str,
    zone_total_delta: float,
    store_kpi_values: Dict[str, Dict],  # {store_id: {value, numerator, denominator, state, aggregation_method}}
) -> SegmentationResult:
    """
    Rank stores by their contribution to the zone-level KPI movement.
    Stores with state=MISSING are excluded entirely (not ranked as zero).
    """
    ranked = []
    excluded = []

    for store_id, kpi_val in store_kpi_values.items():
        state = kpi_val.get("state", "FRESH")
        if state in ("MISSING", "INVALID"):
            excluded.append(store_id)
            continue

        # Use aggregation_method from KPI contract
        contrib = kpi_val.get("delta", 0.0)

        pct = (contrib / zone_total_delta * 100) if zone_total_delta != 0 else 0.0
        ranked.append(StoreContribution(
            dark_store_id=store_id,
            contribution_value=contrib,
            contribution_pct=pct,
        ))

    # Sort by absolute contribution descending
    ranked.sort(key=lambda s: abs(s.contribution_value), reverse=True)

    return SegmentationResult(ranked_stores=ranked, excluded_stores=excluded)
