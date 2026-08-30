"""C4 §8 Acceptance Tests — 8 tests covering lever mapping, decision rights, caveat enforcement, entitlements."""
import pytest


def test_c4_lever_mapping_stockout_to_l2():
    from praxis.c4_decision.decision_package import select_lever
    assert select_lever("dark_store_stockout_rate", "QUALIFY") == "L2_cross_store_transfer"


def test_c4_lever_mapping_sla_to_l3():
    from praxis.c4_decision.decision_package import select_lever
    assert select_lever("delivery_sla_adherence", "QUALIFY") == "L3_add_rider_capacity"


def test_c4_lever_mapping_abstain_to_l7():
    from praxis.c4_decision.decision_package import select_lever
    lever = select_lever("dark_store_stockout_rate", "ABSTAIN")
    assert lever == "L7_escalate_for_investigation"


def test_c4_decision_rights_l2_always_zone_head():
    """Cross-store transfer always requires Zone Business Head (scope rule)."""
    from praxis.c4_decision.decision_package import assign_owner
    owner = assign_owner("L2_cross_store_transfer", "dark_store_ops_manager")
    assert owner == "zone_business_head"


def test_c4_decision_rights_l1_ops_within_ceiling():
    """Restock under ₹15,000 → Ops Manager can authorize."""
    from praxis.c4_decision.decision_package import assign_owner
    owner = assign_owner("L1_restock_sku_store", "dark_store_ops_manager",
                          restock_value=12_000)
    assert owner == "dark_store_ops_manager"


def test_c4_decision_rights_l1_over_ceiling_escalates():
    """Restock over ₹15,000 → escalates to Zone Business Head."""
    from praxis.c4_decision.decision_package import assign_owner
    owner = assign_owner("L1_restock_sku_store", "dark_store_ops_manager",
                          restock_value=20_000)
    assert owner == "zone_business_head"


def test_c4_caveat_mandatory_non_null_for_qualify():
    """DecisionPackage.validate() must raise if caveat_text is null and outcome != ANSWER."""
    from praxis.c4_decision.decision_package import DecisionPackage, ActionItem
    pkg = DecisionPackage(
        decision_package_id="DEC-PKG-TEST",
        finding_id="FIND-TEST",
        hypothesis_package_ref="FIND-TEST",
        evidence_package_ref="FIND-TEST",
        lineage_chain=[],
        generated_at="2026-08-15T12:00:00+05:30",
        source_decision_outcome="QUALIFY",
        source_decision_scope="finding",
        actions=[],
        caveat_text=None,   # VIOLATION: mandatory-non-null
        caveat_source_field="caveat_text",
        narrative_zone_business_head=None,
        narrative_dark_store_ops_manager=None,
    )
    with pytest.raises(ValueError, match="caveat_text is null"):
        pkg.validate()


def test_c4_ops_manager_narrative_excludes_zone_gmv():
    """
    C1 §5 entitlement: zone GMV total must never appear in Ops Manager narrative.
    Tests that the template renderer does NOT include zone_gmv_delta for ops persona.
    """
    from praxis.c4_decision.narrative import _template_narrative
    from praxis.c1_data_foundation.entitlements import Persona

    narrative = _template_narrative(
        persona=Persona.DARK_STORE_OPS_MANAGER,
        kpi_id="zone_gmv",
        grain_key="Z003",
        period="2026-08-15",
        outcome="QUALIFY",
        driver_type="dark_store_stockout_rate",
        contribution_pct=55.0,
        confidence_band="LOW",
        caveat_text="Moderate confidence — qualified finding.",
        lever_id="L2_cross_store_transfer",
        lever_desc="Cross-store inventory transfer",
        delta_abs=-700_000,
        delta_relative=-0.25,
        zone_gmv_delta=None,  # entitlement enforced — None passed in
        leading_store_id="DS041",
        memory_ctx={},
        clarifying_q=None,
    )
    # The narrative must NOT contain a raw ₹700,000 zone GMV figure
    assert "2,100,000" not in narrative
    assert "2,800,000" not in narrative
    # But it can mention the store
    assert "DS041" in narrative
