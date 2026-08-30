"""C2 §9 — EvidencePackage schema.

The concrete artifact C2 hands to C3 per finding.
One EvidencePackage per KPI-instance evaluated.
Every field is populated or explicitly null — C3 never infers absence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from praxis.c2_analytical.operator1_baseline import BaselineResult, BaselineConfidence
from praxis.c2_analytical.operator2_detection import DetectionResult, DetectionOutcome
from praxis.c2_analytical.operator3_decomposition import DecompositionResult
from praxis.c2_analytical.operator4_segmentation import SegmentationResult
from praxis.c2_analytical.operator5_precedence import PrecedenceResult
from praxis.c1_data_foundation.schemas import DataState


IST = timezone(timedelta(hours=5, minutes=30))


@dataclass
class EvidencePackage:
    # Identity & lineage
    finding_id: str
    kpi_instance_id: str
    kpi_id: str
    grain_key: str
    period: str
    created_at: str
    source_version: str

    # Terminal outcome
    terminal_outcome: str        # EVALUATED | SKIPPED | NON_MATERIAL | INSUFFICIENT_HISTORY | NO_DOMINANT_CONTRIBUTOR
    terminal_outcome_reason: Optional[str]

    # Data-state passthrough (C1 §13)
    data_state: DataState
    evaluated_on_stale_input: bool
    partial_sources_excluded: Optional[List[str]]
    conflicting_input: bool
    conflicting_provenance: Optional[List[str]]

    # Baseline — Operator 1 (null if INSUFFICIENT_HISTORY)
    baseline: Optional[Dict[str, Any]]

    # Detection — Operator 2 (null if SKIPPED or INSUFFICIENT_HISTORY)
    detection: Optional[Dict[str, Any]]

    # Decomposition — Operator 3 (present only if material=true)
    decomposition: Optional[Dict[str, Any]]

    # Segmentation — Operator 4
    segmentation: Optional[Dict[str, Any]]

    # Day→month precedence links — Operator 5
    day_month_links: List[Dict[str, Any]]

    # Lineage
    lineage_chain: List[str]
    lineage_edges: List[Dict[str, Any]]

    @classmethod
    def build(
        cls,
        finding_id: str,
        kpi_instance_id: str,
        kpi_id: str,
        grain_key: str,
        period: str,
        source_version: str,
        data_state: DataState,
        baseline_result: Optional[BaselineResult],
        detection_result: Optional[DetectionResult],
        decomp_result: Optional[DecompositionResult],
        seg_result: Optional[SegmentationResult],
        precedence_results: Optional[List[PrecedenceResult]],
        lineage_chain: List[str],
        lineage_edges: List[Dict],
        partial_excluded: Optional[List[str]] = None,
        conflicting_input: bool = False,
        conflicting_provenance: Optional[List[str]] = None,
    ) -> "EvidencePackage":

        now = datetime.now(tz=IST).isoformat()

        # --- Determine terminal_outcome ---
        if baseline_result and baseline_result.is_insufficient:
            terminal_outcome = "INSUFFICIENT_HISTORY"
            terminal_reason = baseline_result.reason
        elif detection_result and detection_result.outcome.value == "SKIPPED":
            terminal_outcome = "SKIPPED"
            terminal_reason = detection_result.skip_reason
        elif detection_result and detection_result.outcome.value == "NON_MATERIAL":
            terminal_outcome = "NON_MATERIAL"
            terminal_reason = None
        elif decomp_result and decomp_result.no_dominant_contributor:
            terminal_outcome = "NO_DOMINANT_CONTRIBUTOR"
            terminal_reason = "No single driver exceeds 30% dominance threshold"
        else:
            terminal_outcome = "EVALUATED"
            terminal_reason = None

        # --- Baseline block ---
        baseline_block = None
        if baseline_result and not baseline_result.is_insufficient:
            baseline_block = {
                "baseline_mean": baseline_result.baseline_mean,
                "baseline_std": baseline_result.baseline_std,
                "window_size_used": baseline_result.window_size_used,
                "baseline_confidence": (baseline_result.baseline_confidence.value
                                        if baseline_result.baseline_confidence else None),
            }

        # --- Detection block ---
        detection_block = None
        if detection_result and detection_result.outcome.value not in ("SKIPPED",):
            if not (baseline_result and baseline_result.is_insufficient):
                detection_block = {
                    "actual_value": detection_result.actual_value,
                    "delta_absolute": detection_result.delta_absolute,
                    "delta_relative": detection_result.delta_relative,
                    "statistically_significant": detection_result.statistically_significant,
                    "test_statistic": detection_result.test_statistic,
                    "test_type": detection_result.test_type,
                    "business_impact_value": detection_result.business_impact_value,
                    "business_impact_significant": detection_result.business_impact_significant,
                    "material": detection_result.material,
                }

        # --- Decomposition block ---
        decomp_block = None
        if decomp_result:
            pvm = decomp_result.pvm
            decomp_block = {
                "pvm": {
                    "applicable": pvm.applicable,
                    "method_not_applicable_reason": pvm.method_not_applicable_reason,
                    "volume_effect": pvm.volume_effect,
                    "price_effect": pvm.price_effect,
                    "mix_effect": pvm.mix_effect,
                },
                "drivers": [
                    {
                        "driver_name": d.driver_name,
                        "contribution_value": d.contribution_value,
                        "contribution_pct": d.contribution_pct,
                        "method": d.method,
                    }
                    for d in decomp_result.drivers
                ],
                "residual_pct": decomp_result.residual_pct,
                "residual_note": decomp_result.residual_note,
                "dominant_driver": decomp_result.dominant_driver,
                "no_dominant_contributor": decomp_result.no_dominant_contributor,
            }

        # --- Segmentation block ---
        seg_block = None
        if seg_result:
            seg_block = {
                "ranked_stores": [
                    {
                        "dark_store_id": s.dark_store_id,
                        "contribution_value": s.contribution_value,
                        "contribution_pct": s.contribution_pct,
                    }
                    for s in seg_result.ranked_stores
                ],
                "excluded_stores": seg_result.excluded_stores,
            }

        # --- Day-month links ---
        dm_links = []
        for pr in (precedence_results or []):
            dm_links.append({
                "candidate_customer_id": pr.candidate_customer_id,
                "driver_event_ts": pr.driver_event_ts.isoformat() if pr.driver_event_ts else None,
                "subsequent_order_ts": pr.subsequent_order_ts.isoformat() if pr.subsequent_order_ts else None,
                "eligible": pr.eligible,
                "reason": pr.reason,
                "linked_finding_id": pr.linked_finding_id,
            })

        return cls(
            finding_id=finding_id,
            kpi_instance_id=kpi_instance_id,
            kpi_id=kpi_id,
            grain_key=grain_key,
            period=period,
            created_at=now,
            source_version=source_version,
            terminal_outcome=terminal_outcome,
            terminal_outcome_reason=terminal_reason,
            data_state=data_state,
            evaluated_on_stale_input=detection_result.evaluated_on_stale_input if detection_result else False,
            partial_sources_excluded=partial_excluded,
            conflicting_input=conflicting_input,
            conflicting_provenance=conflicting_provenance,
            baseline=baseline_block,
            detection=detection_block,
            decomposition=decomp_block,
            segmentation=seg_block,
            day_month_links=dm_links,
            lineage_chain=lineage_chain,
            lineage_edges=lineage_edges,
        )

    def to_dict(self) -> Dict[str, Any]:
        import dataclasses
        return dataclasses.asdict(self)
