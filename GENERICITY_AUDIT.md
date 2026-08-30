# Genericity Audit — Task 1

**Date:** 2026-08-30  
**Auditor:** Praxis Team  
**Outcome:** 4 hardcodes found and fixed. 25 new genericity tests added. All 76 tests pass.

---

## What "generic" means here

The pipeline is generic if adding a new KPI requires only one action:
registering it in `KPI_CONTRACTS` in `c1_data_foundation/kpi_contracts.py`.
No operator code should branch on a `kpi_id` string literal.

---

## Findings

### FINDING 1 — `operator2_detection.py`: hardcoded if/else chain on `kpi_id`

**Severity:** HIGH — any new KPI silently fell into an `else: SKIPPED` branch.

**Before:**
```python
if kpi_id == "zone_gmv":
    return _detect_gmv(...)
elif kpi_id == "order_conversion_rate":
    return _detect_ratio_proportion(..., business_floor_pp=2.0, denom_floor=200)
elif kpi_id == "dark_store_stockout_rate":
    return _detect_ratio_proportion(..., business_floor_pp=3.0, low_volume_floor_pp=6.0)
elif kpi_id == "delivery_sla_adherence":
    return _detect_ratio_proportion(..., business_floor_pp=3.0, denom_floor=30)
elif kpi_id == "repeat_purchase_rate":
    return _detect_rpr(...)
else:
    return DetectionResult(outcome=SKIPPED, skip_reason=f"Unknown kpi_id: {kpi_id}")
```

All thresholds (`z_threshold=2.5`, `biz_floor_abs=50_000`, `biz_floor_rel=0.02`,
`business_floor_pp`, `denom_floor`, `low_volume_floor_pp`) were hardcoded as
function call arguments duplicated across branches.

**Fix:** Each KPI contract now has a `materiality` sub-dict containing all
thresholds. The operator reads `get_kpi_materiality_policy(kpi_id)` and dispatches
on `policy["stat_test"]` (`z_score` | `proportion_z` | `relative_change`).

```python
policy = get_kpi_materiality_policy(kpi_id)   # reads contract
stat_test = policy.get("stat_test", "z_score")
if stat_test == "z_score":
    return _detect_additive(baseline, actual_value, policy, ...)
elif stat_test == "proportion_z":
    return _detect_ratio(baseline, actual_value, ..., policy, ...)
elif stat_test == "relative_change":
    return _detect_relative(baseline, actual_value, policy, ...)
```

---

### FINDING 2 — `operator1_baseline.py`: hardcoded `DAY_GRAIN_KPIS` and `RATIO_KPIS` sets

**Severity:** HIGH — sets were string-literal lists; any new day-grain ratio KPI
would have been treated as additive (wrong pooled computation).

**Before:**
```python
DAY_GRAIN_KPIS = {
    "zone_gmv", "order_conversion_rate",
    "dark_store_stockout_rate", "delivery_sla_adherence"
}
RATIO_KPIS = {
    "order_conversion_rate", "dark_store_stockout_rate", "delivery_sla_adherence"
}
...
if kpi_id == "repeat_purchase_rate":
    return _compute_month_baseline(history)
else:
    return _compute_day_baseline(kpi_id, ...)

# Inside _compute_day_baseline:
if kpi_id in RATIO_KPIS:
    ...pool numerator/denominator...
else:
    ...mean of values...
```

**Fix:** Reads `grain_type` and `aggregation_method` from the contract at call time:
```python
grain_type = get_grain_type(kpi_id)                  # "day" | "month"
contract_agg = get_contract(kpi_id)["aggregation_method"]
is_ratio = contract_agg in ("ratio",)                # "additive" → False

if grain_type == "month":
    return _compute_month_baseline(history)
else:
    return _compute_day_baseline(kpi_id, ..., is_ratio=is_ratio)
```

---

### FINDING 3 — `c5_memory/gateway.py`: hardcoded `GOVERNED_DRIVERS` set

**Severity:** MEDIUM — a new KPI's driver names would have been rejected by the
C5 admission gateway even though they were legitimate governed drivers.

**Before:**
```python
GOVERNED_DRIVERS = {
    "dark_store_stockout_rate", "stockout", "delivery_sla_adherence",
    "rider_capacity", "dispatch_delay", "catchment_density",
    "weather", "order_conversion_rate", "discount_applied",
    "competitor_dark_store_opening", "demand_spike", "residual",
}
```

**Fix:** Derived at import time from `get_all_governed_drivers()`, which unions all
`drivers` lists from `KPI_CONTRACTS`:
```python
from praxis.c1_data_foundation.kpi_contracts import get_all_governed_drivers as _gad
GOVERNED_DRIVERS = _gad()
```

---

### FINDING 4 — `c3_reasoning/retrieval.py`: hardcoded `DRIVER_QUERY_TEMPLATES` dict

**Severity:** LOW — a new KPI's drivers would have returned empty CV query terms
(silently, not an error), degrading retrieval quality.

**Before:** Static dict with 7 hardcoded entries.

**Fix:** `_build_driver_query_templates()` seeds from each contract's `cv_query_terms`
field then applies explicit overrides. New KPI terms are picked up automatically.

---

### NOT A VIOLATION — `operator3_decomposition.py`

`decompose()` already reads `governed_drivers = set(KPI_CONTRACTS.get(kpi_id, {}).get("drivers", []))`.
This was correctly generic from the start. No change needed.

---

### NOT A VIOLATION — `c3_reasoning/generator.py`

`generate_hypotheses()` already reads `governed_drivers` from `KPI_CONTRACTS.get(kpi_id, {})`.
Correctly generic. No change needed.

---

### NOT A VIOLATION — `c4_decision/decision_package.py`

`select_lever()` maps driver names → levers. This is a domain table (driver semantics),
not KPI-name branching. New KPI drivers either map to an existing lever or fall through
to the default `L8_monitor_no_action`. This is correct by design.

---

### NOT A VIOLATION — `c3_reasoning/confidence.py`

Formula parameters (`ms`, `ds`, `cvs`, `dqp`) are computed from numeric inputs
(z-score, contribution_pct, cv counts, etc.) with no KPI name references. Correctly
generic.

---

## Proof: `cart_abandonment_rate` — 6th KPI added with zero operator changes

```
cart_abandonment_rate = 1 − order_conversion_rate
grain  : zone_id × date
source : SRC-SESS + SRC-OMS
drivers: dark_store_stockout_rate, delivery_sla_predicted_at_checkout,
         price_sensitivity, discount_applied, demand_spike
stat_test: proportion_z (p < 0.05, biz_floor=3pp, denom_floor=150)
```

**Changes required:** Only `kpi_contracts.py` — the contract entry itself.

**Pipeline behaviour verified (all 25 tests pass):**

| Stage | Test | Outcome |
|-------|------|---------|
| C1 contract lookup | `test_cart_abandonment_rate_registered` | ✅ |
| C1 materiality policy | `test_materiality_policy_readable` | ✅ |
| C2 baseline (ratio path) | `test_pooled_numerator_denominator_present_for_ratio_kpi` | ✅ |
| C2 detection (MATERIAL) | `test_material_detection_on_new_kpi` | ✅ |
| C2 detection (NON_MATERIAL) | `test_non_material_on_stable_new_kpi` | ✅ |
| C2 decomposition (driver filter) | `test_non_governed_driver_rejected` | ✅ |
| C3 hypothesis generation | `test_hypotheses_generated` | ✅ |
| C3 driver governance | `test_hypothesis_driver_is_governed` | ✅ |
| C4 lever selection | `test_stockout_driver_maps_to_cross_store_transfer` | ✅ |
| C5 governed drivers | `test_new_kpi_drivers_in_governed_set` | ✅ |
| Full C1→C5 pipeline (EVALUATED) | `test_pipeline_runs_to_evaluated` | ✅ |
| Full pipeline (INSUFFICIENT) | `test_pipeline_returns_insufficient_with_no_history` | ✅ |
| Full pipeline (SKIPPED) | `test_pipeline_skips_missing_data_state` | ✅ |

---

## Test results

```
tests/test_c1.py          15 passed
tests/test_c2.py          10 passed
tests/test_c3.py           8 passed
tests/test_c4.py           8 passed
tests/test_c5.py           9 passed
tests/test_resilience.py   1 passed
tests/test_genericity.py  25 passed
─────────────────────────────────
TOTAL                     76 passed
```

All 51 pre-existing tests continue to pass (zero regressions).

---

## Summary

The engine is now provably generic. The KPI YAML contract is the single source
of truth for:
- Which detection method to use (z-score / proportion-z / relative-change)
- All numerical thresholds (z threshold, pp floor, denom floor, vol floor)
- Grain type (day / month) driving baseline operator routing
- Which drivers are governed (C2 Op3 filter + C5 admission gateway)
- CV retrieval query terms

No operator code needs to know a KPI's name in advance.
