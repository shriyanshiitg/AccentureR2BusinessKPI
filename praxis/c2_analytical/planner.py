"""C2 §4 — Investigation Planner.

Rule-based sequencing per C2 §4.
Never reorders step (b) after (c) — data-state check always precedes statistical test.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS
from praxis.c1_data_foundation.lineage import (
    kpi_instance_id, finding_id, lineage_edge, transformation_id, dataset_version_id
)
from praxis.c1_data_foundation.schemas import DataState
from praxis.c2_analytical.operator1_baseline import compute_baseline, BaselineOutcome
from praxis.c2_analytical.operator2_detection import (
    detect, DetectionOutcome, DetectionResult
)
from praxis.c2_analytical.operator3_decomposition import decompose
from praxis.c2_analytical.operator4_segmentation import segment_stores
from praxis.c2_analytical.operator5_precedence import check_precedence
from praxis.c2_analytical.evidence_package import EvidencePackage


IST = timezone(timedelta(hours=5, minutes=30))


def run_investigation(
    kpi_id: str,
    grain_key: str,
    period: str,
    actual_value: float,
    data_state: DataState,
    history: List[Dict],
    numerator: Optional[float] = None,
    denominator: Optional[float] = None,
    driver_observations: Optional[Dict] = None,
    store_kpi_values: Optional[Dict] = None,
    baseline_data: Optional[Dict] = None,
    actual_data: Optional[Dict] = None,
    precedence_candidates: Optional[List[Dict]] = None,
    rpr_finding_id: Optional[str] = None,
    rpr_month_year: Optional[int] = None,
    rpr_month_month: Optional[int] = None,
    partial_excluded: Optional[List[str]] = None,
    conflicting_input: bool = False,
    conflicting_provenance: Optional[List[str]] = None,
    source_version: str = "v1",
) -> EvidencePackage:
    """
    Run the full investigation for one KPI-instance.
    Returns an EvidencePackage regardless of outcome.
    """
    # Build lineage IDs
    kpi_inst_id = kpi_instance_id(kpi_id, grain_key, period.replace("-", ""))
    find_id = finding_id(kpi_inst_id)
    src_id = KPI_CONTRACTS.get(kpi_id, {}).get("source", "SRC-UNK")
    dsv_id = dataset_version_id(src_id, period)
    trans_id = transformation_id("AGG", grain_key, period.replace("-", ""))
    lineage_chain = [src_id, dsv_id, trans_id, kpi_inst_id, find_id]
    edges = [
        lineage_edge(src_id, dsv_id, "batch_version"),
        lineage_edge(dsv_id, trans_id, "transformation"),
        lineage_edge(trans_id, kpi_inst_id, "kpi_evaluation"),
        lineage_edge(kpi_inst_id, find_id, "finding"),
    ]

    # --- Step a: Operator 1 (Baseline) ---
    baseline = compute_baseline(kpi_id, period, history)

    if baseline.outcome == BaselineOutcome.INSUFFICIENT_HISTORY:
        # Hard stop — same tier as MISSING/INVALID
        return EvidencePackage.build(
            finding_id=find_id,
            kpi_instance_id=kpi_inst_id,
            kpi_id=kpi_id,
            grain_key=grain_key,
            period=period,
            source_version=source_version,
            data_state=data_state,
            baseline_result=baseline,
            detection_result=None,
            decomp_result=None,
            seg_result=None,
            precedence_results=None,
            lineage_chain=lineage_chain,
            lineage_edges=edges,
            partial_excluded=partial_excluded,
        )

    # --- Step b: C1 data-state check ---
    # MISSING / INVALID → stop before Operator 2
    if data_state in (DataState.MISSING, DataState.INVALID):
        skipped = DetectionResult(
            outcome=DetectionOutcome.SKIPPED,
            skip_reason=f"C1 data state={data_state.value}",
        )
        return EvidencePackage.build(
            finding_id=find_id,
            kpi_instance_id=kpi_inst_id,
            kpi_id=kpi_id,
            grain_key=grain_key,
            period=period,
            source_version=source_version,
            data_state=data_state,
            baseline_result=baseline,
            detection_result=skipped,
            decomp_result=None,
            seg_result=None,
            precedence_results=None,
            lineage_chain=lineage_chain,
            lineage_edges=edges,
            partial_excluded=partial_excluded,
        )

    # --- Step c: Operator 2 (Detection) ---
    detection = detect(
        kpi_id=kpi_id,
        actual_value=actual_value,
        baseline=baseline,
        data_state=data_state,
        numerator=numerator,
        denominator=denominator,
        partial_excluded=partial_excluded,
        conflicting_input=conflicting_input,
    )

    # --- Step d: Non-material → stop ---
    if detection.outcome == DetectionOutcome.NON_MATERIAL:
        return EvidencePackage.build(
            finding_id=find_id,
            kpi_instance_id=kpi_inst_id,
            kpi_id=kpi_id,
            grain_key=grain_key,
            period=period,
            source_version=source_version,
            data_state=data_state,
            baseline_result=baseline,
            detection_result=detection,
            decomp_result=None,
            seg_result=None,
            precedence_results=None,
            lineage_chain=lineage_chain,
            lineage_edges=edges,
            partial_excluded=partial_excluded,
            conflicting_input=conflicting_input,
        )

    # --- Step e.i: Operator 4 (Segmentation) ---
    seg_result = None
    if store_kpi_values:
        total_delta = detection.delta_absolute or 0
        seg_result = segment_stores(kpi_id, total_delta, store_kpi_values)

    # --- Step e.ii: Operator 3 (Decomposition) ---
    decomp_result = None
    if driver_observations:
        total_gap = detection.delta_absolute or 0
        decomp_result = decompose(
            kpi_id=kpi_id,
            total_gap=total_gap,
            driver_observations=driver_observations,
            baseline_data=baseline_data,
            actual_data=actual_data,
        )

    # --- Step e.iii: Operator 5 (Day → Month precedence) ---
    precedence_results = []
    if precedence_candidates and rpr_finding_id and rpr_month_year and rpr_month_month:
        for cand in precedence_candidates:
            from datetime import datetime
            dev_ts = cand.get("driver_event_ts")
            if isinstance(dev_ts, str):
                dev_ts = datetime.fromisoformat(dev_ts)
            sord_ts = cand.get("subsequent_order_ts")
            if isinstance(sord_ts, str):
                sord_ts = datetime.fromisoformat(sord_ts)

            pr = check_precedence(
                customer_id=cand.get("customer_id", ""),
                driver_event_ts=dev_ts,
                subsequent_order_ts=sord_ts,
                month_year=rpr_month_year,
                month_month=rpr_month_month,
                rpr_finding_id=rpr_finding_id,
            )
            precedence_results.append(pr)

            # Add lineage edge for eligible links
            if pr.eligible and pr.linked_finding_id:
                edges.append(lineage_edge(
                    find_id, pr.linked_finding_id, "candidate_driver_link"
                ))

    return EvidencePackage.build(
        finding_id=find_id,
        kpi_instance_id=kpi_inst_id,
        kpi_id=kpi_id,
        grain_key=grain_key,
        period=period,
        source_version=source_version,
        data_state=data_state,
        baseline_result=baseline,
        detection_result=detection,
        decomp_result=decomp_result,
        seg_result=seg_result,
        precedence_results=precedence_results,
        lineage_chain=lineage_chain,
        lineage_edges=edges,
        partial_excluded=partial_excluded,
        conflicting_input=conflicting_input,
        conflicting_provenance=conflicting_provenance,
    )
