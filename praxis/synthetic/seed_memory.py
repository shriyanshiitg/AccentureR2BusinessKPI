"""Seed C5 memory with the S1 Decision 1 + Outcome 1 demo fixtures.

Must be run before Decision 3 (S2) demo to populate the memory store.
Per C5 §2: demo_preapproved entry path through the same gateway.
Per C5 §5.1: DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01 canonical IDs.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from praxis.c1_data_foundation.lineage import (
    finding_id, kpi_instance_id, decision_memory_id, outcome_memory_id
)
from praxis.c5_memory.gateway import (
    admit_decision_memory, admit_outcome_memory, register_finding_id
)


IST = timezone(timedelta(hours=5, minutes=30))


def seed_decision1_memory(verbose: bool = True) -> dict:
    """
    Seed the S1 Decision 1 + confirmed Outcome 1 fixtures into C5 memory.
    Returns {decision_result, outcome_result}.
    """
    # Build canonical IDs per C1 §14
    kpi_inst = kpi_instance_id("zone_gmv", "Z003", "20260815")
    find_id = finding_id(kpi_inst, seq=1)
    dm_id = decision_memory_id(find_id, seq=1)
    om_id = outcome_memory_id(dm_id, seq=1)

    # Register the finding_id in lineage registry first
    register_finding_id(find_id)

    # C5 §5.1 exact records
    decision_record = {
        "decision_memory_id": dm_id,
        "finding_id": find_id,
        "driver_type": "dark_store_stockout_rate",
        "grain_key": "DS041",
        "grain_level": "store",
        "original_confidence_band": "LOW",
        "action_taken": (
            "L2 — cross-store transfer of SKU-2207 and 3 related SKUs into DS041, "
            "authorized by Zone Business Head"
        ),
        "validation_status": "demo_preapproved",
        "demo_fixture": True,
        "created_at": "2026-08-15T18:00:00+05:30",
    }

    outcome_record = {
        "outcome_memory_id": om_id,
        "decision_memory_id": dm_id,
        "observed_outcome": (
            "DS041 stockout rate for SKU-2207 and related SKUs returned to baseline "
            "within 36 hours of the transfer landing; Z003 daily GMV recovered to within "
            "2% of baseline over the following 2 days."
        ),
        "outcome_matches_hypothesis": True,
        "observed_at": "2026-08-17T12:00:00+05:30",
        "demo_fixture": True,
        "created_at": "2026-08-17T12:05:00+05:30",
    }

    dr = admit_decision_memory(decision_record)
    or_ = admit_outcome_memory(outcome_record)

    if verbose:
        print(f"[C5 Seed] Decision 1 → {dr['status']} ({dr['reason']})")
        print(f"[C5 Seed] Outcome 1  → {or_['status']} ({or_['reason']})")
        print(f"[C5 Seed] DM ID: {dm_id}")
        print(f"[C5 Seed] OM ID: {om_id}")

    return {
        "decision_result": dr,
        "outcome_result": or_,
        "decision_memory_id": dm_id,
        "outcome_memory_id": om_id,
        "finding_id": find_id,
    }


if __name__ == "__main__":
    result = seed_decision1_memory(verbose=True)
    print(f"\nSeed complete: {result}")
