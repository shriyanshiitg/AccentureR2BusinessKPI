"""C5 §7 Acceptance Tests — 9 tests covering gateway, retrieval, confidence boost cap."""
import os
import pytest
import tempfile

# Point all C5 tests to a temp DB so they don't collide with demo data
@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.duckdb")
    monkeypatch.setenv("PRAXIS_DB_PATH", db_path)
    # Patch the module-level DB_PATH in gateway
    import praxis.c5_memory.gateway as gw
    monkeypatch.setattr(gw, "DB_PATH", db_path)
    yield db_path


def _register(finding_id: str):
    from praxis.c5_memory.gateway import register_finding_id
    register_finding_id(finding_id)


# --- Test 1: demo fixture admitted via same gateway ---
def test_c5_demo_fixture_admitted_preapproved():
    from praxis.c5_memory.gateway import (
        admit_decision_memory, admit_outcome_memory, AdmissionResult
    )
    _register("FIND-KPI-zone_gmv-Z003-20260815-01")

    dm = {
        "decision_memory_id": "DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01",
        "finding_id": "FIND-KPI-zone_gmv-Z003-20260815-01",
        "driver_type": "dark_store_stockout_rate",
        "grain_key": "DS041",
        "grain_level": "store",
        "original_confidence_band": "LOW",
        "action_taken": "L2 cross-store transfer",
        "validation_status": "demo_preapproved",
        "demo_fixture": True,
        "created_at": "2026-08-15T18:00:00+05:30",
    }
    dr = admit_decision_memory(dm)
    assert dr["status"] == AdmissionResult.ADMITTED

    om = {
        "outcome_memory_id": "OUT-DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01-01",
        "decision_memory_id": "DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01",
        "observed_outcome": "DS041 stockout returned to baseline within 36h",
        "outcome_matches_hypothesis": True,
        "observed_at": "2026-08-17T12:00:00+05:30",
        "demo_fixture": True,
        "created_at": "2026-08-17T12:05:00+05:30",
    }
    or_ = admit_outcome_memory(om)
    assert or_["status"] == AdmissionResult.ADMITTED


# --- Test 2: live record cannot enter as 'approved' ---
def test_c5_live_record_cannot_self_approve():
    from praxis.c5_memory.gateway import admit_decision_memory, AdmissionResult
    _register("FIND-LIVE-001")

    dm = {
        "decision_memory_id": "DEC-FIND-LIVE-001-01",
        "finding_id": "FIND-LIVE-001",
        "driver_type": "dark_store_stockout_rate",
        "grain_key": "DS041",
        "grain_level": "store",
        "original_confidence_band": "LOW",
        "action_taken": "some action",
        "validation_status": "approved",  # violation — live record must enter as 'pending'
        "demo_fixture": False,
        "created_at": "2026-08-15T18:00:00+05:30",
    }
    result = admit_decision_memory(dm)
    assert result["status"] == AdmissionResult.REJECTED
    assert "pending" in result["reason"].lower()


# --- Test 3: exact-grain retrieval ---
def test_c5_exact_grain_retrieval():
    from praxis.c5_memory.gateway import (
        admit_decision_memory, admit_outcome_memory, retrieve_memory, AdmissionResult
    )
    _register("FIND-KPI-zone_gmv-Z003-20260815-01")
    dm = {
        "decision_memory_id": "DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01",
        "finding_id": "FIND-KPI-zone_gmv-Z003-20260815-01",
        "driver_type": "dark_store_stockout_rate",
        "grain_key": "DS041",
        "grain_level": "store",
        "original_confidence_band": "LOW",
        "action_taken": "L2",
        "validation_status": "demo_preapproved",
        "demo_fixture": True,
        "created_at": "2026-08-15T18:00:00+05:30",
    }
    admit_decision_memory(dm)
    om = {
        "outcome_memory_id": "OUT-DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01-01",
        "decision_memory_id": "DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01",
        "observed_outcome": "recovered",
        "outcome_matches_hypothesis": True,
        "observed_at": "2026-08-17T12:00:00+05:30",
        "demo_fixture": True,
        "created_at": "2026-08-17T12:05:00+05:30",
    }
    admit_outcome_memory(om)

    result = retrieve_memory("dark_store_stockout_rate", "zone_gmv", "DS041", "store")
    assert result["matched"] is True
    assert result["match_scope"] == "exact_grain"
    assert result["representative_decision_memory_id"] == "DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01"


# --- Test 4: hard cap — single precedent cannot reach HIGH from LOW ---
def test_c5_band_cap_single_precedent():
    from praxis.c3_reasoning.confidence import compute_confidence, ConfidenceBand
    from praxis.c5_memory.gateway import compute_memory_points
    mem_points = compute_memory_points(confirmed_count=1, contradicted_count=0)
    assert mem_points == 12  # C5 §4.1

    # Pre-memory raw score that puts us in LOW (e.g., 16)
    raw_pre = 16.0
    # With memory: 16 + 12 = 28 → naive band = LOW still (< 40); no jump needed here
    # Test the case where naive would jump two levels:
    # Pre-memory = 35 (LOW), raw_with_memory = 47 (MEDIUM), max_rise = 1 → allowed
    conf = compute_confidence(
        kpi_id="zone_gmv",
        test_statistic=3.5, test_type="z_score",
        contribution_pct=55.0, no_dominant_contributor=False,
        cv_supports=1, cv_supports_fresh=True, cv_contradicts=1,
        cv_missing=False, evaluated_on_stale=False,
        partial_excluded=False, conflicting_input=False,
        memory_points=12.0, confirmed_precedent_count=1, contradicted_precedent_count=0,
    )
    # Single confirmed precedent: max_rise = 1. Cannot jump from LOW to HIGH
    assert conf.band != ConfidenceBand.HIGH


# --- Test 5: contradicted precedent is admitted and lowers confidence ---
def test_c5_contradicted_admitted_and_informative():
    from praxis.c5_memory.gateway import (
        admit_decision_memory, admit_outcome_memory, retrieve_memory, AdmissionResult
    )
    _register("FIND-KPI-zone_gmv-Z003-20260820-01")
    dm = {
        "decision_memory_id": "DEC-FIND-KPI-zone_gmv-Z003-20260820-01-01",
        "finding_id": "FIND-KPI-zone_gmv-Z003-20260820-01",
        "driver_type": "dark_store_stockout_rate",
        "grain_key": "DS041",
        "grain_level": "store",
        "original_confidence_band": "LOW",
        "action_taken": "L1 restock",
        "validation_status": "demo_preapproved",
        "demo_fixture": True,
        "created_at": "2026-08-20T12:00:00+05:30",
    }
    admit_decision_memory(dm)
    om = {
        "outcome_memory_id": "OUT-DEC-FIND-KPI-zone_gmv-Z003-20260820-01-01-01",
        "decision_memory_id": "DEC-FIND-KPI-zone_gmv-Z003-20260820-01-01",
        "observed_outcome": "restock did not resolve dip — demand spike was actual cause",
        "outcome_matches_hypothesis": False,  # contradicted
        "observed_at": "2026-08-22T12:00:00+05:30",
        "demo_fixture": True,
        "created_at": "2026-08-22T12:05:00+05:30",
    }
    or_ = admit_outcome_memory(om)
    assert or_["status"] == AdmissionResult.ADMITTED  # contradicted still admitted

    result = retrieve_memory("dark_store_stockout_rate", "zone_gmv", "DS041", "store")
    assert result["contradicted_precedent_count"] >= 1


# --- Test 6: no outcome row → prior_outcome_observed = null, memory_points = 0 ---
def test_c5_no_outcome_row_is_silence_not_contradiction():
    from praxis.c5_memory.gateway import (
        admit_decision_memory, retrieve_memory
    )
    _register("FIND-KPI-zone_gmv-Z003-20260819-01")
    dm = {
        "decision_memory_id": "DEC-FIND-KPI-zone_gmv-Z003-20260819-01-01",
        "finding_id": "FIND-KPI-zone_gmv-Z003-20260819-01",
        "driver_type": "dark_store_stockout_rate",
        "grain_key": "DS041",
        "grain_level": "store",
        "original_confidence_band": "LOW",
        "action_taken": "pending action",
        "validation_status": "pending",
        "demo_fixture": False,
        "created_at": "2026-08-19T12:00:00+05:30",
    }
    admit_decision_memory(dm)
    # Intentionally do NOT add an outcome record
    result = retrieve_memory("dark_store_stockout_rate", "zone_gmv", "DS041", "store")
    assert result["prior_outcome_observed"] is None    # silence, not contradiction
    assert result["confirmed_precedent_count"] == 0
    assert result["contradicted_precedent_count"] == 0


# --- Test 7: empty retrieval → matched=false, never an error ---
def test_c5_empty_retrieval_is_explicit_not_error():
    from praxis.c5_memory.gateway import retrieve_memory
    result = retrieve_memory("dark_store_stockout_rate", "zone_gmv", "DS_NONEXISTENT", "store")
    assert result["matched"] is False
    assert result["match_scope"] == "none"
    assert result["representative_decision_memory_id"] is None


# --- Test 8: mixed signal penalty applied ---
def test_c5_mixed_signal_penalty():
    from praxis.c5_memory.gateway import compute_memory_points
    # 1 confirmed + 1 contradicted → 12 - 12 - 5 = -5
    pts = compute_memory_points(confirmed_count=1, contradicted_count=1)
    assert pts == -5


# --- Test 9: unresolvable finding_id is rejected ---
def test_c5_unresolvable_finding_id_rejected():
    from praxis.c5_memory.gateway import admit_decision_memory, AdmissionResult
    # Do NOT register this finding_id
    dm = {
        "decision_memory_id": "DEC-ORPHAN-01",
        "finding_id": "FIND-DOES-NOT-EXIST",
        "driver_type": "dark_store_stockout_rate",
        "grain_key": "DS041",
        "grain_level": "store",
        "original_confidence_band": "LOW",
        "action_taken": "some action",
        "validation_status": "pending",
        "demo_fixture": False,
        "created_at": "2026-08-15T18:00:00+05:30",
    }
    result = admit_decision_memory(dm)
    assert result["status"] == AdmissionResult.REJECTED
    assert "lineage" in result["reason"].lower()
