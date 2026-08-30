"""
test_genericity.py — Task 1 proof: the engine is general, not hardcoded.

Evidence: we add a 6th KPI (cart_abandonment_rate) *only* to KPI_CONTRACTS,
with zero changes to any operator code, and confirm the full C1→C5 pipeline
produces correct, differentiated results for it.

If this test passes it proves:
  1. C1  — contract is found without code changes
  2. C2  — baseline + detection operators route correctly from contract fields
  3. C3  — hypotheses are generated from the contract's driver list
  4. C4  — lever is selected from the driver (no new mapping needed)
  5. C5  — governed_drivers includes the new KPI's drivers automatically
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, timedelta
from praxis.c1_data_foundation.kpi_contracts import (
    KPI_CONTRACTS, get_contract, get_kpi_materiality_policy,
    get_grain_type, get_all_governed_drivers, aggregation_rule,
)
from praxis.c1_data_foundation.schemas import DataState
from praxis.c2_analytical.operator1_baseline import compute_baseline
from praxis.c2_analytical.operator2_detection import detect, DetectionOutcome
from praxis.c2_analytical.operator3_decomposition import decompose
from praxis.c3_reasoning.generator import generate_hypotheses
from praxis.c4_decision.decision_package import select_lever
from praxis.c5_memory.gateway import GOVERNED_DRIVERS
from praxis.c2_analytical.planner import run_investigation


# ---------------------------------------------------------------------------
# 1. Contract registration
# ---------------------------------------------------------------------------

class TestContractRegistration:
    def test_cart_abandonment_rate_registered(self):
        """cart_abandonment_rate appears in KPI_CONTRACTS."""
        assert "cart_abandonment_rate" in KPI_CONTRACTS

    def test_six_kpis_total(self):
        """There are now 6 registered KPIs."""
        assert len(KPI_CONTRACTS) == 6

    def test_contract_has_required_genericity_fields(self):
        """The new KPI has all genericity-required fields."""
        c = get_contract("cart_abandonment_rate")
        assert "grain_type" in c, "grain_type is required"
        assert "aggregation_method" in c, "aggregation_method is required"
        assert "materiality" in c, "materiality is required"
        assert "drivers" in c, "drivers is required"
        assert "cv_query_terms" in c, "cv_query_terms is required"

    def test_materiality_policy_readable(self):
        """get_kpi_materiality_policy() returns a non-empty dict."""
        policy = get_kpi_materiality_policy("cart_abandonment_rate")
        assert isinstance(policy, dict)
        assert "stat_test" in policy
        assert policy["stat_test"] == "proportion_z"

    def test_grain_type(self):
        assert get_grain_type("cart_abandonment_rate") == "day"

    def test_aggregation_rule_from_contract(self):
        """aggregation_rule() no longer uses a hardcoded dict — reads contract."""
        rule = aggregation_rule("cart_abandonment_rate")
        assert "Cart Abandonment Rate" in rule
        assert "Pooled-ratio" in rule  # aggregation_method=ratio

    def test_aggregation_rule_all_kpis(self):
        """Every registered KPI has a valid aggregation_rule string."""
        for kpi_id in KPI_CONTRACTS:
            rule = aggregation_rule(kpi_id)
            assert isinstance(rule, str) and len(rule) > 0, f"Empty rule for {kpi_id}"


# ---------------------------------------------------------------------------
# 2. C2 Operator 1 — baseline handles new KPI generically
# ---------------------------------------------------------------------------

class TestBaseline:
    def _make_history(self, n_days: int, base_rate: float = 35.0):
        """Generate n_days of same-weekday history for a ratio KPI."""
        target = date(2026, 8, 15)
        history = []
        for i in range(1, n_days + 1):
            d = target - timedelta(weeks=i)
            history.append({
                "period": str(d),
                "value": base_rate,
                "numerator": base_rate * 10,     # e.g. 350 abandoned out of 1000
                "denominator": 1000.0,
                "state": "FRESH",
            })
        return history

    def test_insufficient_history_below_3_days(self):
        history = self._make_history(2)
        result = compute_baseline("cart_abandonment_rate", "2026-08-15", history)
        assert result.is_insufficient

    def test_ok_baseline_with_3_days(self):
        history = self._make_history(3)
        result = compute_baseline("cart_abandonment_rate", "2026-08-15", history)
        assert not result.is_insufficient
        assert result.baseline_mean is not None

    def test_pooled_numerator_denominator_present_for_ratio_kpi(self):
        """Baseline correctly pools num/den for a ratio KPI without code changes."""
        history = self._make_history(5)
        result = compute_baseline("cart_abandonment_rate", "2026-08-15", history)
        assert result.pooled_numerator is not None
        assert result.pooled_denominator is not None


# ---------------------------------------------------------------------------
# 3. C2 Operator 2 — detection routes correctly without kpi_id branching
# ---------------------------------------------------------------------------

class TestDetection:
    def _make_baseline(self, mean: float, std: float, pool_n: float, pool_d: float):
        from praxis.c2_analytical.operator1_baseline import BaselineResult, BaselineOutcome, BaselineConfidence
        return BaselineResult(
            outcome=BaselineOutcome.OK,
            baseline_mean=mean,
            baseline_std=std,
            pooled_numerator=pool_n,
            pooled_denominator=pool_d,
            window_size_used=5,
            baseline_confidence=BaselineConfidence.HIGH,
        )

    def test_material_detection_on_new_kpi(self):
        """A large spike in cart_abandonment_rate is detected as MATERIAL."""
        baseline = self._make_baseline(
            mean=35.0, std=3.0,
            pool_n=3500.0, pool_d=10000.0,
        )
        # Actual: 55% abandonment vs 35% baseline — big spike, large denom
        result = detect(
            kpi_id="cart_abandonment_rate",
            actual_value=55.0,
            baseline=baseline,
            data_state=DataState.FRESH,
            numerator=1100.0,   # 1100 abandoned out of 2000 sessions
            denominator=2000.0,
        )
        assert result.outcome == DetectionOutcome.MATERIAL, (
            f"Expected MATERIAL, got {result.outcome}; "
            f"p_val={result.test_statistic}, delta={result.delta_absolute}"
        )

    def test_non_material_on_stable_new_kpi(self):
        """A negligible change is correctly classified NON_MATERIAL."""
        baseline = self._make_baseline(
            mean=35.0, std=3.0,
            pool_n=3500.0, pool_d=10000.0,
        )
        result = detect(
            kpi_id="cart_abandonment_rate",
            actual_value=35.5,  # only 0.5pp change — below 3pp floor
            baseline=baseline,
            data_state=DataState.FRESH,
            numerator=710.0,
            denominator=2000.0,
        )
        assert result.outcome == DetectionOutcome.NON_MATERIAL, (
            f"Expected NON_MATERIAL, got {result.outcome}"
        )

    def test_unknown_kpi_returns_skipped(self):
        """Completely unknown kpi_id returns SKIPPED gracefully."""
        from praxis.c2_analytical.operator1_baseline import BaselineResult, BaselineOutcome, BaselineConfidence
        baseline = BaselineResult(
            outcome=BaselineOutcome.OK,
            baseline_mean=50.0, baseline_std=5.0,
            window_size_used=5,
            baseline_confidence=BaselineConfidence.HIGH,
        )
        result = detect(
            kpi_id="nonexistent_kpi_xyz",
            actual_value=60.0,
            baseline=baseline,
            data_state=DataState.FRESH,
        )
        assert result.outcome == DetectionOutcome.SKIPPED


# ---------------------------------------------------------------------------
# 4. C2 Operator 3 — decomposition uses contract's driver list
# ---------------------------------------------------------------------------

class TestDecomposition:
    def test_non_governed_driver_rejected(self):
        """A driver not in the cart_abandonment_rate contract is silently rejected."""
        result = decompose(
            kpi_id="cart_abandonment_rate",
            total_gap=-200.0,
            driver_observations={
                "dark_store_stockout_rate": {
                    "value_gap": -120.0,
                    "method": "test",
                    "evidence": "test",
                },
                "some_made_up_driver": {  # not in contract.drivers
                    "value_gap": -80.0,
                    "method": "test",
                    "evidence": "test",
                },
            }
        )
        driver_names = [d.driver_name for d in result.drivers]
        assert "some_made_up_driver" not in driver_names, \
            "Non-governed driver should be rejected by decompose()"
        assert "dark_store_stockout_rate" in driver_names


# ---------------------------------------------------------------------------
# 5. C3 — hypotheses generated from new KPI contract drivers
# ---------------------------------------------------------------------------

class TestHypothesisGeneration:
    def _make_evidence_package(self):
        """Minimal EvidencePackage for cart_abandonment_rate."""
        from praxis.c2_analytical.evidence_package import EvidencePackage
        from praxis.c2_analytical.operator1_baseline import BaselineResult, BaselineOutcome, BaselineConfidence
        from praxis.c2_analytical.operator2_detection import DetectionResult, DetectionOutcome
        from praxis.c2_analytical.operator3_decomposition import (
            DecompositionResult, DriverContribution, PVMResult
        )

        baseline = BaselineResult(
            outcome=BaselineOutcome.OK,
            baseline_mean=35.0, baseline_std=3.0,
            window_size_used=5,
            baseline_confidence=BaselineConfidence.HIGH,
        )
        detection = DetectionResult(
            outcome=DetectionOutcome.MATERIAL,
            actual_value=55.0,
            delta_absolute=20.0,
            delta_relative=0.57,
            statistically_significant=True,
            test_statistic=0.001,
            test_type="proportion_z",
            business_impact_value=20.0,
            business_impact_significant=True,
            material=True,
        )
        decomp = DecompositionResult(
            pvm=PVMResult(applicable=False,
                          method_not_applicable_reason="non-additive KPI (§5 additivity)"),
            drivers=[
                DriverContribution(
                    driver_name="dark_store_stockout_rate",
                    contribution_value=-14.0,
                    contribution_pct=-70.0,
                    method="interval_analysis",
                )
            ],
            residual_pct=30.0,
            residual_note="test residual",
            dominant_driver="dark_store_stockout_rate",
            no_dominant_contributor=False,
        )
        ep = EvidencePackage.build(
            finding_id="FIND-TEST-cart-001",
            kpi_instance_id="KPI-cart-001",
            kpi_id="cart_abandonment_rate",
            grain_key="Z001",
            period="2026-08-15",
            source_version="v1",
            data_state=DataState.FRESH,
            baseline_result=baseline,
            detection_result=detection,
            decomp_result=decomp,
            seg_result=None,
            precedence_results=None,
            lineage_chain=["SRC-SESS", "KPI-cart-001", "FIND-TEST-cart-001"],
            lineage_edges=[],
        )
        return ep


    def test_hypotheses_generated(self):
        """generate_hypotheses() works for the new KPI."""
        ep = self._make_evidence_package()
        hyps = generate_hypotheses(ep, llm_client=None)
        assert len(hyps) > 0, "Expected at least 1 hypothesis for cart_abandonment_rate"

    def test_hypothesis_driver_is_governed(self):
        """All generated hypothesis driver_types are in the contract's driver list."""
        from praxis.c1_data_foundation.kpi_contracts import get_contract
        ep = self._make_evidence_package()
        hyps = generate_hypotheses(ep, llm_client=None)
        governed = set(get_contract("cart_abandonment_rate")["drivers"]) | {"residual"}
        for h in hyps:
            assert h.driver_type in governed, \
                f"Non-governed driver {h.driver_type!r} in hypothesis"


# ---------------------------------------------------------------------------
# 6. C4 — lever selection works for new KPI's drivers
# ---------------------------------------------------------------------------

class TestLeverSelection:
    def test_stockout_driver_maps_to_cross_store_transfer(self):
        """dark_store_stockout_rate → L2_cross_store_transfer (not KPI-specific)."""
        lever = select_lever("dark_store_stockout_rate", "ANSWER")
        assert lever == "L2_cross_store_transfer"

    def test_price_sensitivity_maps_to_default(self):
        """price_sensitivity (new driver) gracefully maps to default lever."""
        lever = select_lever("price_sensitivity", "ANSWER")
        assert lever == "L8_monitor_no_action"  # default for unknown driver

    def test_discount_applied_maps_to_promo(self):
        """discount_applied → L4_approve_local_promo."""
        lever = select_lever("discount_applied", "ANSWER")
        assert lever == "L4_approve_local_promo"


# ---------------------------------------------------------------------------
# 7. C5 — governed drivers includes new KPI's drivers automatically
# ---------------------------------------------------------------------------

class TestGovernedDrivers:
    def test_new_kpi_drivers_in_governed_set(self):
        """All drivers from cart_abandonment_rate are in GOVERNED_DRIVERS."""
        new_drivers = set(KPI_CONTRACTS["cart_abandonment_rate"]["drivers"])
        for d in new_drivers:
            assert d in GOVERNED_DRIVERS, \
                f"Driver '{d}' from new KPI not in GOVERNED_DRIVERS"

    def test_governed_drivers_is_superset_of_all_contracts(self):
        """GOVERNED_DRIVERS is the union of all driver lists."""
        for kpi_id, contract in KPI_CONTRACTS.items():
            for d in contract.get("drivers", []):
                assert d in GOVERNED_DRIVERS, \
                    f"Driver '{d}' from KPI '{kpi_id}' missing from GOVERNED_DRIVERS"

    def test_residual_always_governed(self):
        assert "residual" in GOVERNED_DRIVERS


# ---------------------------------------------------------------------------
# 8. Full pipeline integration for new KPI
# ---------------------------------------------------------------------------

class TestFullPipelineNewKPI:
    def _make_history(self, n_days: int = 5, base_rate: float = 35.0):
        target = date(2026, 8, 15)
        history = []
        for i in range(1, n_days + 1):
            d = target - timedelta(weeks=i)
            history.append({
                "period": str(d),
                "value": base_rate,
                "numerator": base_rate * 10,
                "denominator": 1000.0,
                "state": "FRESH",
            })
        return history

    def test_pipeline_runs_to_evaluated(self):
        """run_investigation() works end-to-end for cart_abandonment_rate."""
        history = self._make_history(5)
        ep = run_investigation(
            kpi_id="cart_abandonment_rate",
            grain_key="Z001",
            period="2026-08-15",
            actual_value=55.0,         # 55% abandonment vs 35% baseline
            data_state=DataState.FRESH,
            history=history,
            numerator=1100.0,
            denominator=2000.0,
            driver_observations={
                "dark_store_stockout_rate": {
                    "value_gap": -14.0,
                    "method": "interval_analysis",
                    "evidence": "sku gap confirmed",
                },
            },
        )
        # Pipeline must reach EVALUATED — not SKIPPED or INSUFFICIENT
        assert ep.terminal_outcome == "EVALUATED", (
            f"Expected EVALUATED, got {ep.terminal_outcome}"
        )
        assert ep.kpi_id == "cart_abandonment_rate"

    def test_pipeline_returns_insufficient_with_no_history(self):
        """With zero history, pipeline correctly returns INSUFFICIENT_HISTORY."""
        ep = run_investigation(
            kpi_id="cart_abandonment_rate",
            grain_key="Z001",
            period="2026-08-15",
            actual_value=55.0,
            data_state=DataState.FRESH,
            history=[],           # no history → insufficient
            numerator=1100.0,
            denominator=2000.0,
        )
        assert ep.terminal_outcome == "INSUFFICIENT_HISTORY"

    def test_pipeline_skips_missing_data_state(self):
        """With MISSING data state, pipeline stops at C2 without detection."""
        history = self._make_history(5)
        ep = run_investigation(
            kpi_id="cart_abandonment_rate",
            grain_key="Z001",
            period="2026-08-15",
            actual_value=55.0,
            data_state=DataState.MISSING,   # data unavailable
            history=history,
            numerator=1100.0,
            denominator=2000.0,
        )
        assert ep.terminal_outcome == "SKIPPED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
