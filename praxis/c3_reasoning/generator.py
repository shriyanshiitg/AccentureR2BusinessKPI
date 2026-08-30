"""C3 §2 — Bounded Hypothesis Generator.

LLM proposes claim text only — driver_type selection is structural.
Enforces:
- Only driver_types from C1 §5 drivers list (or "residual")
- 15% inclusion floor for driver hypotheses
- 20% residual-hypothesis floor
- NO_DOMINANT_CONTRIBUTOR: all drivers above 15% become co-candidates
- INSUFFICIENT_HISTORY / SKIPPED / NON_MATERIAL: no hypotheses generated

C3 §9 LLM boundary: LLM fills 'claim' text and 'expected_supporting_evidence'
phrasing only. Driver type, contribution %, status = structural code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional

from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS
from praxis.c1_data_foundation.lineage import hypothesis_id
from praxis.c2_analytical.evidence_package import EvidencePackage
from praxis.c3_reasoning.retrieval import DRIVER_QUERY_TEMPLATES


DRIVER_INCLUSION_FLOOR = 15.0   # C3 §2 — 15% floor (prototype assumption)
RESIDUAL_HYPOTHESIS_FLOOR = 20.0  # C3 §2 — 20% residual floor (prototype assumption)


@dataclass
class Hypothesis:
    hypothesis_id: str
    finding_id: str
    kpi_instance_id: str
    claim: str                      # LLM-generated prose (or deterministic template)
    claim_status: str = "UNDER_EVALUATION"  # always — per C3 §1
    grain_key: str = ""
    period: str = ""
    driver_type: str = ""           # governed driver or "residual"
    contribution_pct: Optional[float] = None
    estimation_method: str = ""
    expected_supporting_evidence: Dict = field(default_factory=dict)
    status: str = "candidate"       # candidate | supported | contradicted | unresolved
    confidence_score: int = 0
    confidence_band: str = "INSUFFICIENT"
    hard_caps_applied: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    memory_hook: Optional[Dict] = None
    is_residual: bool = False


def generate_hypotheses(
    evidence_package: EvidencePackage,
    llm_client=None,                # optional — stub used if None
) -> List[Hypothesis]:
    """
    Generate bounded hypothesis objects from an EvidencePackage.
    Returns empty list for INSUFFICIENT_HISTORY / SKIPPED / NON_MATERIAL.

    LLM is called only to generate the 'claim' natural-language text.
    All structural decisions (driver_type, contribution_pct) are code.
    """
    ep = evidence_package
    to = ep.terminal_outcome

    # Terminal outcomes that produce no hypotheses
    if to in ("INSUFFICIENT_HISTORY", "SKIPPED", "NON_MATERIAL"):
        return []

    governed_drivers = set(KPI_CONTRACTS.get(ep.kpi_id, {}).get("drivers", []))

    hypotheses = []
    seq = 1

    decomp = ep.decomposition
    if not decomp:
        return []

    drivers = decomp.get("drivers", [])
    residual_pct = decomp.get("residual_pct", 0.0)
    no_dominant = decomp.get("no_dominant_contributor", False)

    # Determine anchor date for evidence window
    try:
        anchor = date.fromisoformat(ep.period)
    except Exception:
        # Month-grain RPR: use month-end (BD-003)
        parts = ep.period.split("-")
        import calendar
        yr, mo = int(parts[0]), int(parts[1])
        last_day = calendar.monthrange(yr, mo)[1]
        anchor = date(yr, mo, last_day)

    for drv in drivers:
        driver_name = drv["driver_name"]
        pct = abs(drv.get("contribution_pct", 0.0))

        # Enforce governed driver constraint (C3 §9 — structural, not prompt)
        if driver_name not in governed_drivers and driver_name != "residual":
            continue  # reject non-governed driver

        # Inclusion floor
        if pct < DRIVER_INCLUSION_FLOOR:
            continue

        hyp_id = hypothesis_id(ep.finding_id, seq)
        seq += 1

        claim = _build_claim(driver_name, ep.kpi_id, ep.grain_key, ep.period,
                             pct, drv.get("method", ""), llm_client)

        # Expected evidence window (C1 §7.1)
        window_start = anchor - timedelta(days=7)
        window_end = anchor + timedelta(days=2)

        hyp = Hypothesis(
            hypothesis_id=hyp_id,
            finding_id=ep.finding_id,
            kpi_instance_id=ep.kpi_instance_id,
            claim=claim,
            grain_key=ep.grain_key,
            period=ep.period,
            driver_type=driver_name,
            contribution_pct=drv.get("contribution_pct"),
            estimation_method=drv.get("method", ""),
            expected_supporting_evidence={
                "customer_voice_signal_terms": DRIVER_QUERY_TEMPLATES.get(driver_name, []),
                "expected_direction": "negative",
                "temporal_expectation": {
                    "window_start": str(window_start),
                    "window_end": str(window_end),
                },
            },
            memory_hook=_build_memory_hook(driver_name, ep.kpi_id, ep.grain_key),
        )
        hypotheses.append(hyp)

    # Residual hypothesis — if residual_pct >= 20%
    if residual_pct >= RESIDUAL_HYPOTHESIS_FLOOR:
        hyp_id = hypothesis_id(ep.finding_id, seq)
        seq += 1
        hyp = Hypothesis(
            hypothesis_id=hyp_id,
            finding_id=ep.finding_id,
            kpi_instance_id=ep.kpi_instance_id,
            claim=(
                f"A portion of the {ep.kpi_id} movement ({residual_pct:.1f}%) "
                f"remains unexplained by the governed driver set. This residual "
                f"is flagged as an open investigation area, not attributed to any "
                f"specific driver without evidence."
            ),
            grain_key=ep.grain_key,
            period=ep.period,
            driver_type="residual",
            contribution_pct=residual_pct,
            estimation_method="unexplained residual from decomposition",
            expected_supporting_evidence={
                "customer_voice_signal_terms": [],
                "expected_direction": "neutral",
                "temporal_expectation": {},
            },
            status="unresolved",  # always unresolved by construction
            is_residual=True,
        )
        hypotheses.append(hyp)

    return hypotheses


def _build_claim(
    driver_type: str, kpi_id: str, grain_key: str, period: str,
    contribution_pct: float, method: str, llm_client
) -> str:
    """
    Build the natural-language claim text.
    If LLM is available, call it (bounded to claim phrasing only).
    Otherwise use a deterministic template.
    """
    if llm_client:
        try:
            prompt = (
                f"Write one concise sentence (under 40 words) describing a hypothesis that "
                f"'{driver_type}' drove approximately {contribution_pct:.0f}% of a {kpi_id} "
                f"movement at {grain_key} during {period}. "
                f"Evidence basis: {method}. "
                f"Frame it as a hypothesis under evaluation, not a confirmed fact. "
                f"Do not invent numbers not provided."
            )
            return llm_client.generate_text(prompt, max_tokens=80)
        except Exception:
            pass  # fall through to template

    # Deterministic template (BD-006)
    direction = "decrease"
    templates = {
        "dark_store_stockout_rate": (
            f"A stockout pattern at {grain_key} is estimated to account for "
            f"~{contribution_pct:.0f}% of the {kpi_id} movement on {period}, "
            f"based on active-SKU-interval analysis."
        ),
        "delivery_sla_adherence": (
            f"Delivery SLA breaches at {grain_key} are estimated to contribute "
            f"~{contribution_pct:.0f}% of the {kpi_id} movement on {period}, "
            f"based on same-day dispatch and checkout-abandonment patterns."
        ),
        "order_conversion_rate": (
            f"A conversion rate dip at {grain_key} is estimated to account for "
            f"~{contribution_pct:.0f}% of the {kpi_id} movement on {period}."
        ),
        "residual": (
            f"An unexplained residual of ~{contribution_pct:.0f}% remains "
            f"after attributing known drivers."
        ),
    }
    return templates.get(
        driver_type,
        f"'{driver_type}' is a candidate contributor (~{contribution_pct:.0f}%) "
        f"to the {kpi_id} movement at {grain_key} on {period}.",
    )


def _build_memory_hook(driver_type: str, kpi_id: str, grain_key: str) -> Dict:
    """C3 §8 — memory hook slot; always present, result=null today (C5 fills it)."""
    return {
        "driver_type": driver_type,
        "kpi_id": kpi_id,
        "comparable_scope": {
            "grain_key": grain_key,
            "grain_level": "store" if grain_key.startswith("DS") else "zone",
        },
        "requested_fields": [
            "prior_validation_status",
            "prior_confidence_band",
            "prior_outcome_observed",
        ],
        "result": None,
        "result_schema_reserved": True,
    }
