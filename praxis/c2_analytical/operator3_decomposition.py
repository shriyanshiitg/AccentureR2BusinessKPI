"""C2 §3 — Operator 3: Contribution / Decomposition.

Implements:
- PVM (Price/Volume/Mix) split for zone_gmv (the one additive KPI)
- Driver-mapped contribution split for all 5 KPIs
- METHOD_NOT_APPLICABLE: skips PVM for non-additive KPIs (C1 §5 additivity field)
- NO_DOMINANT_CONTRIBUTOR: if largest driver < 30% of total movement
- Residual bucket explicitly populated, never force-fit
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS


DOMINANCE_THRESHOLD = 0.30  # C2 §3: 30% dominance bar


@dataclass
class DriverContribution:
    driver_name: str
    contribution_value: float
    contribution_pct: float
    method: str


@dataclass
class PVMResult:
    applicable: bool
    method_not_applicable_reason: Optional[str] = None
    volume_effect: Optional[float] = None
    price_effect: Optional[float] = None
    mix_effect: Optional[float] = None


@dataclass
class DecompositionResult:
    pvm: PVMResult
    drivers: List[DriverContribution] = field(default_factory=list)
    residual_pct: float = 0.0
    residual_note: str = ""
    dominant_driver: Optional[str] = None
    no_dominant_contributor: bool = False


def decompose(
    kpi_id: str,
    total_gap: float,
    driver_observations: Dict[str, Dict],
    baseline_data: Optional[Dict] = None,
    actual_data: Optional[Dict] = None,
) -> DecompositionResult:
    """
    Perform contribution / decomposition for a material finding.

    driver_observations: {driver_name: {
        'numerator_gap': float,   # for ratio drivers
        'value_gap': float,       # for additive drivers
        'method': str,
        'evidence': str,
    }}
    baseline_data / actual_data: required for PVM on zone_gmv.
    """
    contract = KPI_CONTRACTS.get(kpi_id, {})
    is_additive = contract.get("additivity") == "additive"
    governed_drivers = set(contract.get("drivers", []))

    # --- PVM sub-step ---
    pvm = _compute_pvm(kpi_id, is_additive, total_gap, baseline_data, actual_data)

    # --- Driver-mapped contribution split ---
    drivers = []
    total_explained = 0.0

    for driver_name, obs in driver_observations.items():
        # Enforce governed driver list (C2 §3 / C3 §1 inherited constraint)
        if driver_name not in governed_drivers and driver_name != "residual":
            continue  # silently skip non-governed drivers (structural enforcement)

        val = obs.get("value_gap", 0.0)
        pct = (abs(val) / abs(total_gap) * 100) if total_gap != 0 else 0
        # Keep sign from val for direction
        signed_pct = (val / abs(total_gap) * 100) if total_gap != 0 else 0
        drivers.append(DriverContribution(
            driver_name=driver_name,
            contribution_value=val,
            contribution_pct=signed_pct,
            method=obs.get("method", "estimated"),
        ))
        total_explained += abs(val)

    # Sort by absolute contribution descending
    drivers.sort(key=lambda d: abs(d.contribution_value), reverse=True)

    # Residual
    residual_val = abs(total_gap) - total_explained
    if abs(total_gap) > 0:
        residual_pct = (residual_val / abs(total_gap)) * 100
    else:
        residual_pct = 0.0
    # Ensure residual_pct doesn't go negative (floating point)
    residual_pct = max(0.0, residual_pct)

    # Normalize pcts to sum to 100
    total_driver_pct = sum(abs(d.contribution_pct) for d in drivers) + residual_pct
    if total_driver_pct > 0 and abs(total_driver_pct - 100) > 0.5:
        scale = 100.0 / total_driver_pct
        for d in drivers:
            d.contribution_pct *= scale
            d.contribution_value *= scale
        residual_pct *= scale

    residual_note = (
        "Residual represents unexplained variance not attributable to any single "
        "governed driver — C2 does not force-fit this to discount_applied, "
        "competitor_dark_store_opening, or demand_spike without direct evidence."
    )

    # --- NO_DOMINANT_CONTRIBUTOR check ---
    dominant_driver = None
    no_dominant = True
    if drivers:
        top = drivers[0]
        # Use absolute pct for dominance check
        if abs(top.contribution_pct) / 100 >= DOMINANCE_THRESHOLD:
            dominant_driver = top.driver_name
            no_dominant = False

    return DecompositionResult(
        pvm=pvm,
        drivers=drivers,
        residual_pct=residual_pct,
        residual_note=residual_note,
        dominant_driver=dominant_driver,
        no_dominant_contributor=no_dominant,
    )


def _compute_pvm(kpi_id: str, is_additive: bool, total_gap: float,
                 baseline_data: Optional[Dict],
                 actual_data: Optional[Dict]) -> PVMResult:
    """
    C2 §3: PVM only applicable to additive KPIs (zone_gmv only).
    For non-additive KPIs: tag METHOD_NOT_APPLICABLE on pvm component.
    ASP computed as SUM(gmv)/SUM(units) at segment grain — never averaged.
    """
    if not is_additive:
        return PVMResult(
            applicable=False,
            method_not_applicable_reason="non-additive KPI (§5 additivity)",
        )

    if not baseline_data or not actual_data:
        return PVMResult(
            applicable=False,
            method_not_applicable_reason="insufficient PVM input data",
        )

    b_units = float(baseline_data.get("units", 0))
    b_gmv = float(baseline_data.get("gmv", 0))
    a_units = float(actual_data.get("units", 0))
    a_gmv = float(actual_data.get("gmv", 0))

    # ASP = SUM(gmv) / SUM(units) — never averaged pre-computed ASPs
    b_asp = b_gmv / b_units if b_units > 0 else 0
    a_asp = a_gmv / a_units if a_units > 0 else 0

    # Volume effect = (actual_units - baseline_units) * baseline_ASP
    vol_effect = (a_units - b_units) * b_asp
    # Price/ASP effect = (actual_ASP - baseline_ASP) * actual_units
    price_effect = (a_asp - b_asp) * a_units

    return PVMResult(
        applicable=True,
        volume_effect=vol_effect,
        price_effect=price_effect,
        mix_effect=None,  # SKU-mix not decomposed in MVP
    )
