"""Synthetic data generator — parameterized by seed, date range, and scenario type.

Produces:
  S1 scenario: DS041 stockout on 2026-08-15 (Z003) — the canonical demo scenario
  S2 scenario: Same pattern 2026-08-22 (Decision 3 demo) — 7 days later
  INSUFFICIENT_HISTORY scenario: new store DS099 with < 3 history days
  NO_DOMINANT_CONTRIBUTOR scenario: diffuse multi-driver pattern
  UNSCRIPTED scenario (seed-driven): random zone/store/event combination

All scenarios are returned as pipeline-ready dicts consumable by run_pipeline().
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional


IST = timezone(timedelta(hours=5, minutes=30))

# Canonical entity reference data
ZONES = {
    "Z003": {"zone_name": "Koramangala", "city": "Bangalore"},
    "Z007": {"zone_name": "Whitefield", "city": "Bangalore"},
    "Z012": {"zone_name": "Andheri West", "city": "Mumbai"},
}

STORES_BY_ZONE = {
    "Z003": ["DS041", "DS042", "DS043"],
    "Z007": ["DS071", "DS072"],
    "Z012": ["DS121", "DS122", "DS123"],
}

STORE_TO_ZONE = {
    "DS041": "Z003", "DS042": "Z003", "DS043": "Z003",
    "DS071": "Z007", "DS072": "Z007",
    "DS121": "Z012", "DS122": "Z012", "DS123": "Z012",
    "DS099": "Z003",  # new store for INSUFFICIENT_HISTORY
}

SKUS = {
    "SKU-2207": {"name": "Amul Butter 500g", "category": "dairy", "price": 275.0},
    "SKU-1104": {"name": "Aavin Milk 1L", "category": "dairy", "price": 65.0},
    "SKU-3310": {"name": "Britannia Bread", "category": "bakery", "price": 45.0},
}

# Customer Voice templates per scenario
CV_STOCKOUT_TEXTS_CANONICAL = [
    "Amul butter was out of stock again, had to cancel my order. Very disappointing.",
    "Product unavailable at checkout, app showed available but wasn't in stock.",
    "Out of stock for the third time this week. Switched to another app.",
]
CV_STOCKOUT_TEXTS = CV_STOCKOUT_TEXTS_CANONICAL  # alias for other consumers
CV_SLA_TEXTS = [
    "Order took 45 minutes, app said 15. Very late delivery.",
    "Rider never showed up, had to cancel",
    "Still waiting for my order after 1 hour, absolutely unacceptable",
]
CV_POSITIVE_TEXTS = [
    "Great quick delivery today, very impressed!",
    "Order arrived exactly on time, will order again",
    "Fast service as always",
]


def _ist_ts(d: date, hour: int = 12, minute: int = 0) -> datetime:
    return datetime(d.year, d.month, d.day, hour, minute, 0, tzinfo=IST)


def build_history(
    kpi_id: str, grain_key: str, anchor: date,
    baseline_mean: float, baseline_std: float,
    n_days: int = 14, rng: random.Random = None,
    data_state: str = "FRESH",
) -> List[Dict]:
    """Build n_days of same-weekday history for a KPI."""
    if rng is None:
        rng = random.Random(42)
    history = []
    weekday = anchor.weekday()
    d = anchor - timedelta(days=1)
    count = 0
    while count < n_days:
        if d.weekday() == weekday:
            val = max(0, rng.gauss(baseline_mean, baseline_std))
            history.append({
                "period": str(d),
                "value": val,
                "numerator": val if kpi_id in ("dark_store_stockout_rate", "order_conversion_rate",
                                               "delivery_sla_adherence") else None,
                "denominator": 500 if kpi_id in ("order_conversion_rate",
                                                  "delivery_sla_adherence") else (
                    1000 if kpi_id == "dark_store_stockout_rate" else None),
                "state": data_state,
            })
            count += 1
        d -= timedelta(days=1)
    return history


def _cv_stockout_records(zone_id: str, anchor: date) -> List[Dict]:
    """
    Generate IDENTICAL-sentiment stockout CV records anchored to the scenario date.
    Same 3 canonical texts used in both S1 and S2 — dates shift with anchor so they
    stay inside the [anchor-7, anchor+2] retrieval window.
    NO contradicting records — CV score will be exactly +20 in both scenarios.
    This makes memory the SOLE differentiator between Decision 1 and Decision 3.
    """
    records = []
    for i, text in enumerate(CV_STOCKOUT_TEXTS_CANONICAL):
        rec_date = anchor - timedelta(days=i + 1)   # D-1, D-2, D-3
        records.append({
            "record_id": f"CV-{zone_id}-{anchor}-{i}",
            "zone_id": zone_id,
            "customer_id": f"CUST-{1000 + i}",
            "ts": _ist_ts(rec_date, 10 + i).isoformat(),
            "source_type": "review",
            "text": text,
            "matched_day": str(rec_date),
            "matched_week": rec_date.strftime("%G-W%V"),
            "data_quality_state": "Fresh",
        })
    return records


def _cv_records(zone_id: str, anchor: date, scenario: str) -> List[Dict]:
    """Generate Customer Voice records for non-demo scenarios."""
    texts = CV_SLA_TEXTS[:2] if "sla" in scenario else (
        CV_POSITIVE_TEXTS[:2] if "positive" in scenario else CV_STOCKOUT_TEXTS_CANONICAL[:2]
    )
    records = []
    for i, text in enumerate(texts):
        rec_date = anchor - timedelta(days=i)
        records.append({
            "record_id": f"CV-{zone_id}-{anchor}-{i}",
            "zone_id": zone_id,
            "customer_id": f"CUST-{1000 + i}",
            "ts": _ist_ts(rec_date, 10 + i).isoformat(),
            "source_type": "review",
            "text": text,
            "matched_day": str(rec_date),
            "matched_week": rec_date.strftime("%G-W%V"),
            "data_quality_state": "Fresh",
        })
    return records


# ---------------------------------------------------------------------------
# S1 — Canonical stockout scenario (Decision 1, no memory)
# ---------------------------------------------------------------------------

def build_s1_scenario() -> Dict[str, Any]:
    """
    S1: Zone Z003 GMV dip on 2026-08-15 driven by DS041 stockout rate spike.
    This is the canonical demo scenario from C1/C2/C5 worked examples.
    """
    anchor = date(2026, 8, 15)
    rng = random.Random(42)

    # GMV: baseline 2.8M/day, actual 2.1M (25% drop)
    baseline_mean = 2_800_000.0
    baseline_std = 140_000.0
    actual_gmv = 2_100_000.0

    history = build_history("zone_gmv", "Z003", anchor, baseline_mean, baseline_std, rng=rng)

    # Decomposition: stockout_rate = 55%, sla = 25%, residual = 20%
    total_gap = actual_gmv - baseline_mean  # ≈ -700_000
    driver_observations = {
        "dark_store_stockout_rate": {
            "value_gap": total_gap * 0.55,
            "method": "active-SKU-interval analysis, DS041 vs DS042/DS043 comparison",
        },
        "delivery_sla_adherence": {
            "value_gap": total_gap * 0.25,
            "method": "SLA breach rate elevated, dispatch delay correlated",
        },
    }

    store_kpi_values = {
        "DS041": {"value": 0.42, "delta": total_gap * 0.55, "state": "FRESH"},
        "DS042": {"value": 0.04, "delta": 0, "state": "FRESH"},
        "DS043": {"value": 0.06, "delta": 0, "state": "FRESH"},
    }

    # CRITICAL: Use canonical stockout records with NO contradicting signal.
    # S1 and S2 use identical texts so CV score = +20 in both.
    # Memory (+12) is then the SOLE confidence differentiator.
    cv = _cv_stockout_records("Z003", anchor)

    return {
        "kpi_id": "zone_gmv",
        "grain_key": "Z003",
        "period": str(anchor),
        "actual_value": actual_gmv,
        "data_state": "FRESH",
        "history": history,
        "numerator": actual_gmv,
        "denominator": None,
        "driver_observations": driver_observations,
        "store_kpi_values": store_kpi_values,
        "baseline_data": {"units": 28000, "gmv": baseline_mean},
        "actual_data": {"units": 21000, "gmv": actual_gmv},
        "cv_records": cv,
        "zone_id": "Z003",
        "leading_store_id": "DS041",
        "zone_gmv_delta": actual_gmv - baseline_mean,
        "store_to_zone": STORE_TO_ZONE,
        "sku_info": SKUS["SKU-2207"],
        "source_version": "SRC-OMS-v2026-08-15",
        "partial_excluded": None,
        "conflicting_input": False,
    }


# ---------------------------------------------------------------------------
# S2 — Decision 3 scenario (with memory, same driver, same store, 7 days later)
# ---------------------------------------------------------------------------

def build_s2_scenario() -> Dict[str, Any]:
    """
    S2: Same stockout pattern at DS041 on 2026-08-22 (7 days after S1).
    When pipeline runs WITH memory, should retrieve Decision 1's outcome
    and boost confidence from LOW to MEDIUM.
    """
    anchor = date(2026, 8, 22)
    rng = random.Random(99)

    baseline_mean = 2_800_000.0
    baseline_std = 140_000.0
    actual_gmv = 2_175_000.0  # slightly less severe than S1

    history = build_history("zone_gmv", "Z003", anchor, baseline_mean, baseline_std, rng=rng)

    total_gap = actual_gmv - baseline_mean  # ≈ -625_000
    driver_observations = {
        "dark_store_stockout_rate": {
            "value_gap": total_gap * 0.55,
            "method": "active-SKU-interval analysis, DS041 vs peers",
        },
        "delivery_sla_adherence": {
            "value_gap": total_gap * 0.25,
            "method": "SLA breach rate elevated",
        },
    }

    store_kpi_values = {
        "DS041": {"value": 0.39, "delta": total_gap * 0.55, "state": "FRESH"},
        "DS042": {"value": 0.05, "delta": 0, "state": "FRESH"},
        "DS043": {"value": 0.05, "delta": 0, "state": "FRESH"},
    }

    # CRITICAL: Same canonical stockout texts as S1 — no contradicting signal.
    # The ONLY difference from D1 is memory_points = +12 (1 confirmed precedent).
    cv = _cv_stockout_records("Z003", anchor)

    return {
        "kpi_id": "zone_gmv",
        "grain_key": "Z003",
        "period": str(anchor),
        "actual_value": actual_gmv,
        "data_state": "FRESH",
        "history": history,
        "numerator": actual_gmv,
        "denominator": None,
        "driver_observations": driver_observations,
        "store_kpi_values": store_kpi_values,
        "baseline_data": {"units": 27500, "gmv": baseline_mean},
        "actual_data": {"units": 21800, "gmv": actual_gmv},
        "cv_records": cv,
        "zone_id": "Z003",
        "leading_store_id": "DS041",
        "zone_gmv_delta": actual_gmv - baseline_mean,
        "store_to_zone": STORE_TO_ZONE,
        "sku_info": SKUS["SKU-2207"],
        "source_version": "SRC-OMS-v2026-08-22",
        "partial_excluded": None,
        "conflicting_input": False,
    }


# ---------------------------------------------------------------------------
# INSUFFICIENT_HISTORY scenario (new store)
# ---------------------------------------------------------------------------

def build_insufficient_history_scenario() -> Dict[str, Any]:
    anchor = date(2026, 8, 20)
    # Only 2 history days — below MIN_CLEAN_DAYS=3 floor
    history = build_history("zone_gmv", "DS099", anchor, 300_000, 30_000, n_days=2)

    return {
        "kpi_id": "zone_gmv",
        "grain_key": "DS099",
        "period": str(anchor),
        "actual_value": 200_000.0,
        "data_state": "FRESH",
        "history": history,
        "numerator": 200_000.0,
        "denominator": None,
        "driver_observations": {},
        "store_kpi_values": {},
        "cv_records": [],
        "zone_id": "Z003",
        "leading_store_id": "DS099",
        "zone_gmv_delta": -100_000.0,
        "store_to_zone": STORE_TO_ZONE,
        "source_version": "SRC-OMS-v2026-08-20",
    }


# ---------------------------------------------------------------------------
# NO_DOMINANT_CONTRIBUTOR scenario
# ---------------------------------------------------------------------------

def build_no_dominant_contributor_scenario() -> Dict[str, Any]:
    anchor = date(2026, 8, 18)
    rng = random.Random(77)

    baseline_mean = 1_500_000.0
    baseline_std = 75_000.0
    actual_gmv = 1_150_000.0

    history = build_history("zone_gmv", "Z007", anchor, baseline_mean, baseline_std, rng=rng)

    total_gap = actual_gmv - baseline_mean  # ≈ -350_000
    # Diffuse: three drivers each ~25%, residual 25% — no single driver > 30%
    driver_observations = {
        "dark_store_stockout_rate": {
            "value_gap": total_gap * 0.25,
            "method": "interval analysis",
        },
        "delivery_sla_adherence": {
            "value_gap": total_gap * 0.25,
            "method": "pooled ratio",
        },
        "order_conversion_rate": {
            "value_gap": total_gap * 0.25,
            "method": "proportion test",
        },
    }

    store_kpi_values = {
        "DS071": {"value": 0.12, "delta": total_gap * 0.5, "state": "FRESH"},
        "DS072": {"value": 0.08, "delta": total_gap * 0.5, "state": "FRESH"},
    }

    return {
        "kpi_id": "zone_gmv",
        "grain_key": "Z007",
        "period": str(anchor),
        "actual_value": actual_gmv,
        "data_state": "FRESH",
        "history": history,
        "numerator": actual_gmv,
        "denominator": None,
        "driver_observations": driver_observations,
        "store_kpi_values": store_kpi_values,
        "cv_records": _cv_records("Z007", anchor, "mixed"),
        "zone_id": "Z007",
        "leading_store_id": "DS071",
        "zone_gmv_delta": actual_gmv - baseline_mean,
        "store_to_zone": STORE_TO_ZONE,
        "source_version": "SRC-OMS-v2026-08-18",
    }


# ---------------------------------------------------------------------------
# UNSCRIPTED scenario — driven by seed, not pre-scripted
# ---------------------------------------------------------------------------

def build_unscripted_scenario(seed: int = 42) -> Dict[str, Any]:
    """
    Generate a coherent unscripted scenario not pre-computed by the design team.
    Uses the seed to drive all random choices.
    """
    rng = random.Random(seed)

    # Random zone, store, date
    zone_id = rng.choice(list(ZONES.keys()))
    stores = STORES_BY_ZONE[zone_id]
    lead_store = rng.choice(stores)
    # Random date in Aug-Sep 2026 (at least 14 days into the future from anchor)
    base = date(2026, 8, 1)
    offset = rng.randint(20, 55)
    anchor = base + timedelta(days=offset)

    # Random severity
    severity_pct = rng.uniform(0.12, 0.35)
    baseline_mean = rng.uniform(800_000, 3_500_000)
    baseline_std = baseline_mean * 0.05
    actual_gmv = baseline_mean * (1 - severity_pct)

    history = build_history("zone_gmv", zone_id, anchor, baseline_mean, baseline_std, rng=rng)

    total_gap = actual_gmv - baseline_mean

    # Random driver distribution that sums to 1.0
    d1 = rng.uniform(0.35, 0.60)  # leading driver always > 30%
    d2 = rng.uniform(0.15, 0.30)
    residual = 1.0 - d1 - d2

    # Random driver types from governed list
    governed = ["dark_store_stockout_rate", "delivery_sla_adherence", "order_conversion_rate"]
    drivers_chosen = rng.sample(governed, 2)

    driver_observations = {
        drivers_chosen[0]: {
            "value_gap": total_gap * d1,
            "method": "statistical decomposition (unscripted)",
        },
        drivers_chosen[1]: {
            "value_gap": total_gap * d2,
            "method": "statistical decomposition (unscripted)",
        },
    }

    store_kvi = {}
    for s in stores:
        frac = rng.uniform(0.1, 0.5)
        store_kvi[s] = {
            "value": rng.uniform(0.03, 0.40),
            "delta": total_gap * frac / len(stores),
            "state": "FRESH",
        }

    scenario_tag = f"stockout" if "stockout" in drivers_chosen[0] else "sla"
    cv = _cv_records(zone_id, anchor, scenario_tag)

    return {
        "kpi_id": "zone_gmv",
        "grain_key": zone_id,
        "period": str(anchor),
        "actual_value": actual_gmv,
        "data_state": "FRESH",
        "history": history,
        "numerator": actual_gmv,
        "denominator": None,
        "driver_observations": driver_observations,
        "store_kpi_values": store_kvi,
        "baseline_data": {"units": int(baseline_mean / 100), "gmv": baseline_mean},
        "actual_data": {"units": int(actual_gmv / 100), "gmv": actual_gmv},
        "cv_records": cv,
        "zone_id": zone_id,
        "leading_store_id": lead_store,
        "zone_gmv_delta": actual_gmv - baseline_mean,
        "store_to_zone": STORE_TO_ZONE,
        "source_version": f"SRC-OMS-v{anchor}",
        "_unscripted_seed": seed,
        "_unscripted_zone": zone_id,
        "_unscripted_store": lead_store,
        "_unscripted_anchor": str(anchor),
    }


def build_challenge_scenario() -> Dict[str, Any]:
    """
    Challenge Scenario: Zone Z003 GMV dip 2026-08-16, but Customer Voice
    CONTRADICTS the stockout hypothesis — customers complain about app UX,
    not out-of-stock items. The system should band the stockout hypothesis
    at LOW/MEDIUM with status='contradicted', demonstrating CV challenge logic.
    """
    anchor = date(2026, 8, 16)
    rng = random.Random(77)

    baseline_mean = 2_800_000.0
    baseline_std = 140_000.0
    actual_gmv = 2_200_000.0  # -21.4% drop

    history = build_history("zone_gmv", "Z003", anchor, baseline_mean, baseline_std, rng=rng)
    total_gap = actual_gmv - baseline_mean  # -600_000

    driver_observations = {
        "dark_store_stockout_rate": {
            "value_gap": total_gap * 0.55,
            "method": "active-SKU-interval analysis",
        },
        "delivery_sla_adherence": {
            "value_gap": total_gap * 0.30,
            "method": "SLA breach rate elevated",
        },
    }

    store_kpi_values = {
        "DS041": {"value": 0.08, "delta": total_gap * 0.20, "state": "FRESH"},
        "DS042": {"value": 0.06, "delta": total_gap * 0.20, "state": "FRESH"},
        "DS043": {"value": 0.07, "delta": total_gap * 0.15, "state": "FRESH"},
    }

    # CONTRADICTING CV: customers explicitly say items were AVAILABLE but app was broken.
    # This should challenge and contradict the stockout hypothesis.
    cv = [
        {
            "record_id": f"CV-Z003-{anchor}-contra-0",
            "zone_id": "Z003",
            "customer_id": "CUST-7001",
            "ts": _ist_ts(anchor - timedelta(days=1), 10).isoformat(),
            "source_type": "review",
            "text": "Items were available but the checkout kept failing, not out of stock at all.",
            "matched_day": str(anchor - timedelta(days=1)),
            "matched_week": (anchor - timedelta(days=1)).strftime("%G-W%V"),
            "data_quality_state": "Fresh",
        },
        {
            "record_id": f"CV-Z003-{anchor}-contra-1",
            "zone_id": "Z003",
            "customer_id": "CUST-7002",
            "ts": _ist_ts(anchor - timedelta(days=1), 12).isoformat(),
            "source_type": "csat",
            "text": "App crashed during payment. All products showed as in stock. Not a supply issue.",
            "matched_day": str(anchor - timedelta(days=1)),
            "matched_week": (anchor - timedelta(days=1)).strftime("%G-W%V"),
            "data_quality_state": "Fresh",
        },
        {
            "record_id": f"CV-Z003-{anchor}-contra-2",
            "zone_id": "Z003",
            "customer_id": "CUST-7003",
            "ts": _ist_ts(anchor - timedelta(days=1), 14).isoformat(),
            "source_type": "review",
            "text": "Technical glitch — order wouldn't go through but everything was in stock.",
            "matched_day": str(anchor - timedelta(days=1)),
            "matched_week": (anchor - timedelta(days=1)).strftime("%G-W%V"),
            "data_quality_state": "Fresh",
        },
    ]

    return {
        "kpi_id": "zone_gmv",
        "grain_key": "Z003",
        "period": str(anchor),
        "actual_value": actual_gmv,
        "data_state": "FRESH",
        "history": history,
        "numerator": actual_gmv,
        "denominator": None,
        "driver_observations": driver_observations,
        "store_kpi_values": store_kpi_values,
        "baseline_data": {"units": 28000, "gmv": baseline_mean},
        "actual_data": {"units": 22000, "gmv": actual_gmv},
        "cv_records": cv,
        "zone_id": "Z003",
        "leading_store_id": "DS041",
        "zone_gmv_delta": actual_gmv - baseline_mean,
        "store_to_zone": STORE_TO_ZONE,
        "sku_info": SKUS["SKU-2207"],
        "source_version": "SRC-OMS-v2026-08-16",
        "partial_excluded": None,
        "conflicting_input": False,
    }




def get_scenario(name: str, seed: int = 42) -> Dict[str, Any]:
    """Entry point: name in {s1, s2, insufficient_history, no_dominant, unscripted, challenge}."""
    if name == "s1":
        return build_s1_scenario()
    elif name == "s2":
        return build_s2_scenario()
    elif name == "insufficient_history":
        return build_insufficient_history_scenario()
    elif name == "no_dominant":
        return build_no_dominant_contributor_scenario()
    elif name == "unscripted":
        return build_unscripted_scenario(seed=seed)
    elif name == "challenge":
        return build_challenge_scenario()
    else:
        raise ValueError(
            f"Unknown scenario: {name!r}. "
            f"Valid: s1, s2, insufficient_history, no_dominant, unscripted, challenge"
        )

