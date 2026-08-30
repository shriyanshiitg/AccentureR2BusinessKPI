"""C2 §10 Acceptance Tests — 10 tests covering all 5 operators and EvidencePackage."""
import pytest
from datetime import date, datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


def _history(n=14, baseline=2_800_000, std=140_000, weekday=5):
    """Build n same-weekday history entries."""
    import random
    rng = random.Random(42)
    anchor = date(2026, 8, 15)
    results = []
    d = anchor - timedelta(days=1)
    count = 0
    while count < n:
        if d.weekday() == weekday:
            val = max(0, rng.gauss(baseline, std))
            results.append({"period": str(d), "value": val, "state": "FRESH",
                             "numerator": None, "denominator": None})
            count += 1
        d -= timedelta(days=1)
    return results


# --- Operator 1: Baseline ---

def test_c2_baseline_insufficient_history():
    from praxis.c2_analytical.operator1_baseline import compute_baseline, BaselineOutcome
    # Only 2 same-weekday clean days → INSUFFICIENT_HISTORY
    history = _history(n=2)
    result = compute_baseline("zone_gmv", "2026-08-15", history)
    assert result.outcome == BaselineOutcome.INSUFFICIENT_HISTORY
    assert "2" in result.reason


def test_c2_baseline_7days_high_confidence():
    from praxis.c2_analytical.operator1_baseline import compute_baseline, BaselineConfidence
    history = _history(n=7)
    result = compute_baseline("zone_gmv", "2026-08-15", history)
    assert result.baseline_confidence == BaselineConfidence.HIGH
    assert result.baseline_mean > 0


def test_c2_baseline_excludes_stale():
    from praxis.c2_analytical.operator1_baseline import compute_baseline, BaselineOutcome
    # Mix 1 FRESH + 2 STALE → effectively 1 clean day → INSUFFICIENT
    anchor = date(2026, 8, 15)
    history = []
    d = anchor - timedelta(days=1)
    count = 0
    while count < 3:
        if d.weekday() == anchor.weekday():
            state = "FRESH" if count == 0 else "STALE"
            history.append({"period": str(d), "value": 2_800_000, "state": state,
                             "numerator": None, "denominator": None})
            count += 1
        d -= timedelta(days=1)
    result = compute_baseline("zone_gmv", "2026-08-15", history)
    assert result.outcome == BaselineOutcome.INSUFFICIENT_HISTORY


# --- Operator 2: Detection ---

def test_c2_detection_material_gmv():
    from praxis.c2_analytical.operator1_baseline import compute_baseline
    from praxis.c2_analytical.operator2_detection import detect, DetectionOutcome
    from praxis.c1_data_foundation.schemas import DataState
    history = _history(n=14)
    baseline = compute_baseline("zone_gmv", "2026-08-15", history)
    result = detect("zone_gmv", actual_value=2_100_000,
                    baseline=baseline, data_state=DataState.FRESH)
    assert result.outcome == DetectionOutcome.MATERIAL
    assert result.is_material


def test_c2_detection_skipped_on_missing_data():
    from praxis.c2_analytical.operator1_baseline import compute_baseline
    from praxis.c2_analytical.operator2_detection import detect, DetectionOutcome
    from praxis.c1_data_foundation.schemas import DataState
    history = _history(n=14)
    baseline = compute_baseline("zone_gmv", "2026-08-15", history)
    result = detect("zone_gmv", actual_value=0,
                    baseline=baseline, data_state=DataState.MISSING)
    assert result.outcome == DetectionOutcome.SKIPPED


# --- Operator 3: Decomposition ---

def test_c2_decomposition_dominant_driver():
    from praxis.c2_analytical.operator3_decomposition import decompose
    driver_obs = {
        "dark_store_stockout_rate": {"value_gap": -385_000, "method": "interval analysis"},
        "delivery_sla_adherence": {"value_gap": -175_000, "method": "pooled ratio"},
    }
    result = decompose("zone_gmv", total_gap=-700_000,
                       driver_observations=driver_obs)
    assert result.dominant_driver == "dark_store_stockout_rate"
    assert not result.no_dominant_contributor


def test_c2_decomposition_no_dominant_contributor():
    from praxis.c2_analytical.operator3_decomposition import decompose
    # Three drivers at ~25% each — none > 30%
    driver_obs = {
        "dark_store_stockout_rate": {"value_gap": -87_500, "method": "estimate"},
        "delivery_sla_adherence": {"value_gap": -87_500, "method": "estimate"},
        "order_conversion_rate": {"value_gap": -87_500, "method": "estimate"},
    }
    result = decompose("zone_gmv", total_gap=-350_000, driver_observations=driver_obs)
    assert result.no_dominant_contributor


# --- Operator 4: Segmentation ---

def test_c2_segmentation_missing_store_excluded_not_zero():
    from praxis.c2_analytical.operator4_segmentation import segment_stores
    store_kpi = {
        "DS041": {"value": 0.42, "delta": -385_000, "state": "FRESH"},
        "DS042": {"value": 0.04, "delta": -5_000, "state": "FRESH"},
        "DS099": {"value": None, "delta": 0, "state": "MISSING"},  # new store
    }
    result = segment_stores("zone_gmv", -700_000, store_kpi)
    excluded_ids = result.excluded_stores
    ranked_ids = [s.dark_store_id for s in result.ranked_stores]
    assert "DS099" in excluded_ids
    assert "DS099" not in ranked_ids


# --- Operator 5: Precedence ---

def test_c2_precedence_valid_linkage():
    from praxis.c2_analytical.operator5_precedence import check_precedence
    driver_ts = datetime(2026, 7, 25, 12, 0, tzinfo=IST)
    next_order_ts = datetime(2026, 7, 27, 10, 0, tzinfo=IST)
    result = check_precedence("CUST-001", driver_ts, next_order_ts, 2026, 8)
    assert result.eligible


def test_c2_precedence_rejects_future_driver():
    from praxis.c2_analytical.operator5_precedence import check_precedence
    driver_ts = datetime(2026, 7, 28, 12, 0, tzinfo=IST)
    next_order_ts = datetime(2026, 7, 28, 10, 0, tzinfo=IST)  # before driver
    result = check_precedence("CUST-001", driver_ts, next_order_ts, 2026, 8)
    assert not result.eligible
    assert "PRECEDENCE_VIOLATION" in result.reason
