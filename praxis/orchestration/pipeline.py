"""Praxis orchestration pipeline — C1 → C2 → C3 → C4 (+C5 hook).

One function: run_pipeline(scenario_data) → PipelineResult
Handles the S1 stockout scenario and arbitrary synthetic scenarios.
"""
from __future__ import annotations

import os
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
load_dotenv()

from praxis.c1_data_foundation.schemas import DataState
from praxis.c1_data_foundation.entitlements import EntitlementContext, Persona
from praxis.c2_analytical.planner import run_investigation
from praxis.c3_reasoning.hypothesis_package import build_hypothesis_package
from praxis.c4_decision.narrative import build_decision_package
from praxis.c5_memory.gateway import retrieve_memory, register_finding_id
from praxis.llm.client import GroqLLMClient
from praxis.orchestration.telemetry import Telemetry


IST = timezone(timedelta(hours=5, minutes=30))


class PipelineResult:
    def __init__(self):
        self.finding_id: Optional[str] = None
        self.evidence_package = None
        self.hypothesis_package = None
        self.decision_package = None
        self.memory_result: Optional[Dict] = None
        self.telemetry_summary: Optional[Dict] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "finding_id": self.finding_id,
            "evidence_package": self.evidence_package.to_dict() if self.evidence_package else None,
            "hypothesis_package": self.hypothesis_package.to_dict() if self.hypothesis_package else None,
            "decision_package": self.decision_package.to_dict() if self.decision_package else None,
            "memory_result": self.memory_result,
            "telemetry": self.telemetry_summary,
            "error": self.error,
        }


def run_pipeline(
    scenario: Dict[str, Any],
    persona: str = Persona.ZONE_BUSINESS_HEAD,
    use_memory: bool = True,
    run_id: Optional[str] = None,
    log_path: str = "data/telemetry.jsonl",
) -> PipelineResult:
    """
    Run the full Praxis pipeline for one scenario.

    scenario dict keys:
      kpi_id, grain_key, period, actual_value, data_state,
      history, numerator, denominator, driver_observations,
      store_kpi_values, baseline_data, actual_data,
      cv_records, zone_id, source_version,
      zone_gmv_delta (optional), leading_store_id (optional),
      sku_info (optional)
    """
    run_id = run_id or str(uuid.uuid4())[:8]
    telemetry = Telemetry(log_path=log_path)
    telemetry.start_run(run_id, scenario_name(scenario), finding_id=None)

    result = PipelineResult()

    # --- Init LLM client ---
    api_key = os.environ.get("GROQ_API_KEY", "")
    llm_client = None
    if api_key:
        try:
            llm_client = GroqLLMClient(api_key=api_key, telemetry=telemetry)
        except Exception as e:
            pass  # fall through to deterministic mode

    try:
        # =========================================================
        # PHASE 1 — C2: Statistical Investigation
        # =========================================================
        t0 = time.perf_counter()

        ep = run_investigation(
            kpi_id=scenario["kpi_id"],
            grain_key=scenario["grain_key"],
            period=scenario["period"],
            actual_value=scenario["actual_value"],
            data_state=DataState(scenario.get("data_state", "FRESH")),
            history=scenario.get("history", []),
            numerator=scenario.get("numerator"),
            denominator=scenario.get("denominator"),
            driver_observations=scenario.get("driver_observations"),
            store_kpi_values=scenario.get("store_kpi_values"),
            baseline_data=scenario.get("baseline_data"),
            actual_data=scenario.get("actual_data"),
            partial_excluded=scenario.get("partial_excluded"),
            conflicting_input=scenario.get("conflicting_input", False),
            source_version=scenario.get("source_version", "v1"),
        )
        result.evidence_package = ep
        result.finding_id = ep.finding_id
        telemetry._finding_id = ep.finding_id

        # Register the finding_id in C5 lineage registry
        register_finding_id(ep.finding_id)

        telemetry.record_phase(
            "c2_investigation", ep.terminal_outcome,
            (time.perf_counter() - t0) * 1000,
            {"kpi_id": scenario["kpi_id"], "grain_key": scenario["grain_key"]},
        )

        # =========================================================
        # PHASE 2 — C5: Memory Retrieval (hook, before C3 scoring)
        # =========================================================
        memory_result = None
        if use_memory and ep.terminal_outcome == "EVALUATED":
            t0 = time.perf_counter()
            # Identify leading driver from decomposition
            leading_driver = None
            if ep.decomposition:
                drivers = ep.decomposition.get("drivers", [])
                if drivers:
                    leading_driver = drivers[0]["driver_name"]

            if leading_driver:
                memory_result = retrieve_memory(
                    driver_type=leading_driver,
                    kpi_id=scenario["kpi_id"],
                    grain_key=scenario.get("leading_store_id", scenario["grain_key"]),
                    grain_level="store" if scenario.get("leading_store_id") else "zone",
                    store_to_zone=scenario.get("store_to_zone", {}),
                )
            telemetry.record_phase(
                "c5_memory_retrieval",
                "matched" if (memory_result and memory_result.get("matched")) else "no_match",
                (time.perf_counter() - t0) * 1000,
                {"matched": memory_result.get("matched") if memory_result else False},
            )

        result.memory_result = memory_result

        # =========================================================
        # PHASE 3 — C3: Hypothesis + Confidence
        # =========================================================
        t0 = time.perf_counter()

        hp = build_hypothesis_package(
            evidence_package=ep,
            cv_records=scenario.get("cv_records", []),
            zone_id=scenario.get("zone_id", scenario["grain_key"]),
            llm_client=llm_client,
            memory_result=memory_result,
        )
        result.hypothesis_package = hp

        telemetry.record_phase(
            "c3_reasoning", hp.decision.get("outcome", "UNKNOWN"),
            (time.perf_counter() - t0) * 1000,
            {
                "hypothesis_count": len(hp.hypotheses),
                "leading_hyp": hp.decision.get("leading_hypothesis_id"),
            },
        )

        # =========================================================
        # PHASE 4 — C4: Decision Package + Narratives
        # =========================================================
        t0 = time.perf_counter()

        detection = ep.detection or {}
        dp = build_decision_package(
            hypothesis_package=hp,
            kpi_id=scenario["kpi_id"],
            grain_key=scenario["grain_key"],
            period=scenario["period"],
            delta_abs=detection.get("delta_absolute", 0),
            delta_relative=detection.get("delta_relative", 0),
            leading_store_id=scenario.get("leading_store_id"),
            persona=persona,
            llm_client=llm_client,
            zone_gmv_delta=scenario.get("zone_gmv_delta") if persona == Persona.ZONE_BUSINESS_HEAD else None,
            sku_info=scenario.get("sku_info"),
        )
        result.decision_package = dp

        telemetry.record_phase(
            "c4_decision", dp.source_decision_outcome,
            (time.perf_counter() - t0) * 1000,
            {"lever": dp.actions[0].controllable_lever if dp.actions else None},
        )

        final_outcome = dp.source_decision_outcome

    except Exception as e:
        result.error = str(e)
        final_outcome = "ERROR"
        import traceback
        result.error = traceback.format_exc()

    result.telemetry_summary = telemetry.end_run(final_outcome)
    return result


def scenario_name(scenario: Dict) -> str:
    return f"{scenario.get('kpi_id', 'unknown')}@{scenario.get('grain_key', '?')}-{scenario.get('period', '?')}"


# ---------------------------------------------------------------------------
# Multi-KPI Alert Queue — Gap 1 (G1) fix
# ---------------------------------------------------------------------------

# Simulated zone-level KPI state for the morning briefing scan (2026-08-15 week).
# Each entry represents one KPI's current observation vs. its baseline.
# In a production system these would be fetched from the data layer; here
# they are deterministic prototype values consistent with the S1 scenario.

_KPI_ALERT_DATA = [
    {
        "kpi_id": "zone_gmv",
        "kpi_name": "Zone GMV",
        "actual_display": "₹21.0L",
        "delta_display": "−₹7.0L",
        "delta_pct": -25.0,
        "z_score": 5.0,
        "status": "MATERIAL",
        "severity": 5,   # 1–5, drives sort order
        "outcome": "root_cause_identified",
        "outcome_label": "Root cause identified",
        "method": "z-score · deterministic",
        "source": "SRC-OMS · hourly",
        "freshness": "Fresh",
        "freshness_ago": "47 min ago",
    },
    {
        "kpi_id": "dark_store_stockout_rate",
        "kpi_name": "Stockout Rate · DS041",
        "actual_display": "42%",
        "delta_display": "+38pp",
        "delta_pct": +38.0,
        "z_score": 4.2,
        "status": "MATERIAL",
        "severity": 4,
        "outcome": "primary_driver",
        "outcome_label": "Primary driver of GMV gap",
        "method": "proportion-z · deterministic",
        "source": "SRC-INV · 15-min cadence",
        "freshness": "Fresh",
        "freshness_ago": "2h ago",
    },
    {
        "kpi_id": "delivery_sla_adherence",
        "kpi_name": "Delivery SLA Adherence",
        "actual_display": "71%",
        "delta_display": "−12pp",
        "delta_pct": -12.0,
        "z_score": 2.8,
        "status": "MATERIAL",
        "severity": 3,
        "outcome": "abstain_sparse",
        "outcome_label": "Abstain · sparse rider history",
        "method": "proportion-z · deterministic",
        "source": "SRC-DEL · 15-min cadence",
        "freshness": "Stale",
        "freshness_ago": "7h ago · GPS lag",
    },
    {
        "kpi_id": "order_conversion_rate",
        "kpi_name": "Order Conversion Rate",
        "actual_display": "5.8%",
        "delta_display": "+0.1pp",
        "delta_pct": +0.1,
        "z_score": 0.3,
        "status": "NON_MATERIAL",
        "severity": 0,
        "outcome": "non_material",
        "outcome_label": "Within normal range",
        "method": "proportion-z · deterministic",
        "source": "SRC-SESS+OMS · 1h cadence",
        "freshness": "Fresh",
        "freshness_ago": "1h ago",
    },
    {
        "kpi_id": "repeat_purchase_rate",
        "kpi_name": "Repeat Purchase Rate",
        "actual_display": "—",
        "delta_display": "—",
        "delta_pct": None,
        "z_score": None,
        "status": "MONTHLY",
        "severity": 0,
        "outcome": "monthly_not_yet",
        "outcome_label": "Monthly KPI · data not yet available",
        "method": "relative-change · deterministic",
        "source": "SRC-OMS · daily",
        "freshness": "Fresh",
        "freshness_ago": "24h cadence",
    },
]


def run_all_kpis() -> List[Dict]:
    """
    G1 fix: Run materiality detection across all monitored KPIs and return
    a ranked alert queue sorted by severity (highest first).

    In the prototype this returns pre-computed values consistent with the
    S1 scenario. The pipeline architecture already supports running each
    KPI independently via run_pipeline() — this function would call that
    for each KPI in production.

    Returns: List[Dict] sorted by severity descending.
    """
    return sorted(_KPI_ALERT_DATA, key=lambda x: x["severity"], reverse=True)
