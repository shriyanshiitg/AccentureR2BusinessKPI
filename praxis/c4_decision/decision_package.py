"""C4 §1-4 — Decision Package: lever catalogue, rights matrix, and DecisionPackage schema.

Deterministic lever lookup (driver_type → controllable_lever).
C4 §6 LLM boundary: LLM phrases narratives; lever selection and confidence passthrough are code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from praxis.c1_data_foundation.lineage import decision_package_id
from praxis.c3_reasoning.hypothesis_package import HypothesisPackage

IST = timezone(timedelta(hours=5, minutes=30))

# ---------------------------------------------------------------------------
# C4 §1 — 8-lever catalogue
# ---------------------------------------------------------------------------
LEVERS = {
    "L1_restock_sku_store": {
        "description": "Restock a specific SKU at a specific dark store",
        "driver_types": ["dark_store_stockout_rate", "stockout"],
        "grain": "store × SKU",
    },
    "L2_cross_store_transfer": {
        "description": "Cross-store inventory transfer (move stock from neighboring store with surplus)",
        "driver_types": ["dark_store_stockout_rate"],
        "grain": "store pair, within zone",
        "requires_zone_head": True,  # crosses single-store scope always
    },
    "L3_add_rider_capacity": {
        "description": "Add rider capacity for a shift",
        "driver_types": ["rider_capacity", "delivery_sla_adherence",
                         "dark_store_stockout_rate"],
        "grain": "store × shift",
    },
    "L4_approve_local_promo": {
        "description": "Approve a time-boxed local promo",
        "driver_types": ["order_conversion_rate", "discount_applied",
                         "demand_spike", "competitor_dark_store_opening"],
        "grain": "zone",
        "requires_zone_head": True,
    },
    "L5_adjust_dispatch_schedule": {
        "description": "Adjust dispatch scheduling / rider shift pattern",
        "driver_types": ["catchment_density", "weather", "dispatch_delay"],
        "grain": "store × shift",
    },
    "L6_flag_competitor_opening": {
        "description": "Flag competitor dark-store opening for zone-level pricing/promo strategy review",
        "driver_types": ["competitor_dark_store_opening"],
        "grain": "zone",
        "requires_zone_head": True,
    },
    "L7_escalate_for_investigation": {
        "description": "Escalate unresolved/contradicted finding for manual investigation",
        "driver_types": ["__any__"],
        "grain": "finding or hypothesis",
    },
    "L8_monitor_no_action": {
        "description": "Monitor, no action",
        "driver_types": ["__any__"],
        "grain": "finding or hypothesis",
        "is_default": True,
    },
}


# C4 §2 decision-rights thresholds (BD-004)
RIGHTS_MATRIX = {
    "L1_restock_sku_store": {
        "ops_manager_auto": True,
        "ops_manager_ceiling": 15000,   # ₹ per SKU-store (BD-004)
        "ops_manager_sku_ceiling": 5,   # max 5 SKUs in one action
        "zone_head_always": False,
    },
    "L2_cross_store_transfer": {
        "ops_manager_auto": False,      # Rule 1: crosses store scope
        "zone_head_always": True,
    },
    "L3_add_rider_capacity": {
        "ops_manager_auto": True,
        "ops_manager_ceiling_riders": 2,  # ≤2 additional riders per shift (BD-004)
        "zone_head_always": False,
    },
    "L4_approve_local_promo": {
        "ops_manager_auto": False,
        "zone_head_always": True,
    },
    "L5_adjust_dispatch_schedule": {
        "ops_manager_auto": True,       # within existing approved headcount
        "zone_head_always": False,
    },
    "L6_flag_competitor_opening": {
        "ops_manager_auto": False,
        "zone_head_always": True,
    },
    "L7_escalate_for_investigation": {
        "ops_manager_auto": True,
        "zone_head_always": False,
    },
    "L8_monitor_no_action": {
        "ops_manager_auto": True,
        "zone_head_always": False,
    },
}


def select_lever(driver_type: str, decision_outcome: str) -> str:
    """
    Deterministic driver_type → lever mapping (C4 §6 LLM never chooses lever).
    """
    if decision_outcome == "CLARIFY":
        return "L8_monitor_no_action"
    if decision_outcome == "ABSTAIN":
        return "L7_escalate_for_investigation"

    lever_map = {
        "dark_store_stockout_rate": "L2_cross_store_transfer",  # preferred for zone head
        "stockout": "L1_restock_sku_store",
        "delivery_sla_adherence": "L3_add_rider_capacity",
        "rider_capacity": "L3_add_rider_capacity",
        "dispatch_delay": "L5_adjust_dispatch_schedule",
        "catchment_density": "L5_adjust_dispatch_schedule",
        "weather": "L5_adjust_dispatch_schedule",
        "order_conversion_rate": "L4_approve_local_promo",
        "discount_applied": "L4_approve_local_promo",
        "competitor_dark_store_opening": "L6_flag_competitor_opening",
        "demand_spike": "L4_approve_local_promo",
        "residual": "L7_escalate_for_investigation",
    }
    return lever_map.get(driver_type, "L8_monitor_no_action")


def assign_owner(lever_id: str, persona: str,
                 restock_value: Optional[float] = None,
                 rider_count: Optional[int] = None) -> str:
    """
    Determine action owner per C4 §2 decision rights matrix.
    Returns "zone_business_head" or "dark_store_ops_manager".
    Scope is the first gate — never widened by value.
    """
    rights = RIGHTS_MATRIX.get(lever_id, {})

    if rights.get("zone_head_always"):
        return "zone_business_head"

    if persona == "dark_store_ops_manager" and rights.get("ops_manager_auto"):
        # Check value ceilings
        if lever_id == "L1_restock_sku_store":
            if restock_value and restock_value > rights.get("ops_manager_ceiling", 15000):
                return "zone_business_head"
        if lever_id == "L3_add_rider_capacity":
            if rider_count and rider_count > rights.get("ops_manager_ceiling_riders", 2):
                return "zone_business_head"
        return "dark_store_ops_manager"

    return "zone_business_head"


@dataclass
class ActionItem:
    driver: str
    controllable_lever: str
    action: str
    expected_impact: str
    owner: str
    confidence: str    # direct passthrough from C3 band — no recomputation
    monitoring_plan: str


@dataclass
class DecisionPackage:
    decision_package_id: str
    finding_id: str
    hypothesis_package_ref: str
    evidence_package_ref: str
    lineage_chain: List[str]
    generated_at: str

    source_decision_outcome: str   # C3 verbatim
    source_decision_scope: str

    actions: List[ActionItem]

    # mandatory-non-null when outcome != ANSWER (C4 §4 structural rule)
    caveat_text: Optional[str]
    caveat_source_field: str  # caveat_text | clarifying_question | abstain_reason | none

    narrative_zone_business_head: Optional[str]
    narrative_dark_store_ops_manager: Optional[str]

    def validate(self):
        """C4 §4 validation — raises if caveat_text is null when required."""
        if (self.source_decision_outcome != "ANSWER"
                and self.caveat_text is None):
            raise ValueError(
                f"DecisionPackage validation failed: caveat_text is null but "
                f"source_decision_outcome={self.source_decision_outcome!r} (not ANSWER). "
                f"C4 §4 mandatory-non-null rule violated."
            )

    def to_dict(self) -> Dict:
        import dataclasses
        return dataclasses.asdict(self)
