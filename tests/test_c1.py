"""C1 §18 Acceptance Tests — 15 tests covering DQ gate, KPI contracts, entitlements, lineage."""
import pytest
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal

IST = timezone(timedelta(hours=5, minutes=30))

KNOWN_STORES = {"DS041", "DS042", "DS043"}
KNOWN_CUSTOMERS = {"CUST-001", "CUST-002", "CUST-003"}
KNOWN_ORDERS = {"ORD-001", "ORD-002"}
KNOWN_SKUS = {"SKU-2207", "SKU-1104"}


def _make_order(**overrides):
    base = {
        "order_id": "ORD-001",
        "zone_id": "Z003",
        "dark_store_id": "DS041",
        "customer_id": "CUST-001",
        "order_ts": datetime(2026, 8, 15, 12, 0, tzinfo=IST),
        "gmv_value": 500.0,
        "discount_applied": 0.1,
        "order_status": "completed",
        "source_version": "v1",
        "ingested_at": datetime(2026, 8, 15, 13, 0, tzinfo=IST),
        "units_sold": 5,
        "sku_line_items": [
            {"order_line_id": "L1", "order_id": "ORD-001", "sku_id": "SKU-2207",
             "units_sold": 5, "unit_price_at_sale": 275.0, "line_gmv": 500.0}
        ],
    }
    base.update(overrides)
    return base


# --- DQ Gate Tests ---

def test_c1_dq_valid_order_passes():
    from praxis.c1_data_foundation.dq_gate import check_order
    report = check_order(_make_order(), KNOWN_STORES, KNOWN_STORES, KNOWN_CUSTOMERS)
    assert report.final_action.value == "PASS", f"Expected PASS, got {report.failed_checks()}"


def test_c1_dq_missing_required_field_blocks():
    from praxis.c1_data_foundation.dq_gate import check_order, DQAction
    order = _make_order()
    del order["order_id"]
    report = check_order(order, KNOWN_STORES, KNOWN_STORES, KNOWN_CUSTOMERS)
    assert report.final_action == DQAction.BLOCK


def test_c1_dq_unknown_store_blocks():
    from praxis.c1_data_foundation.dq_gate import check_order, DQAction
    order = _make_order(dark_store_id="DS999")
    report = check_order(order, KNOWN_STORES, KNOWN_STORES, KNOWN_CUSTOMERS)
    assert report.final_action == DQAction.BLOCK


def test_c1_dq_discount_out_of_range_quarantines():
    from praxis.c1_data_foundation.dq_gate import check_order, DQAction
    order = _make_order(discount_applied=1.5)
    report = check_order(order, KNOWN_STORES, KNOWN_STORES, KNOWN_CUSTOMERS)
    assert report.final_action == DQAction.QUARANTINE


def test_c1_dq_gmv_line_reconciliation_warn():
    from praxis.c1_data_foundation.dq_gate import check_order, DQAction
    # GMV=600 but line_gmv=500 → diff=100 > max(1, 3) → WARN
    order = _make_order(gmv_value=600.0)
    report = check_order(order, KNOWN_STORES, KNOWN_STORES, KNOWN_CUSTOMERS)
    failed = [r.rule for r in report.failed_checks()]
    assert "gmv_line_reconciliation" in failed


def test_c1_dq_completed_order_zero_lines_blocks():
    from praxis.c1_data_foundation.dq_gate import check_order, DQAction
    order = _make_order(sku_line_items=[])
    report = check_order(order, KNOWN_STORES, KNOWN_STORES, KNOWN_CUSTOMERS)
    assert report.final_action == DQAction.BLOCK


def test_c1_dq_cart_add_flag_no_ts_quarantines():
    from praxis.c1_data_foundation.dq_gate import check_app_session, DQAction
    session = {
        "session_id": "S001",
        "zone_id": "Z003",
        "session_start_ts": datetime(2026, 8, 15, 10, 0, tzinfo=IST),
        "cart_add_flag": True,
        "cart_add_ts": None,  # should trigger quarantine
        "source_version": "v1",
        "ingested_at": datetime(2026, 8, 15, 11, 0, tzinfo=IST),
    }
    report = check_app_session(session, KNOWN_ORDERS)
    assert report.final_action == DQAction.QUARANTINE


# --- KPI Contract Tests ---

def test_c1_kpi_zone_gmv_additive():
    from praxis.c1_data_foundation.kpi_contracts import compute_zone_gmv
    orders = [
        {"order_id": "O1", "zone_id": "Z003", "order_status": "completed",
         "sku_line_items": [{"line_gmv": 500.0}]},
        {"order_id": "O2", "zone_id": "Z003", "order_status": "completed",
         "sku_line_items": [{"line_gmv": 300.0}]},
        {"order_id": "O3", "zone_id": "Z003", "order_status": "cancelled",
         "sku_line_items": [{"line_gmv": 200.0}]},  # excluded
    ]
    kpiv = compute_zone_gmv(orders, "Z003", date(2026, 8, 15))
    assert kpiv.value == 800.0  # only completed orders


def test_c1_kpi_rpr_formula_with_tenure_note():
    from praxis.c1_data_foundation.kpi_contracts import compute_repeat_purchase_rate
    orders = [
        {"order_id": "O1", "zone_id": "Z003", "order_status": "completed",
         "customer_id": "C1", "order_ts": datetime(2026, 8, 10, tzinfo=IST)},
        {"order_id": "O2", "zone_id": "Z003", "order_status": "completed",
         "customer_id": "C1", "order_ts": datetime(2026, 8, 20, tzinfo=IST)},
        {"order_id": "O3", "zone_id": "Z003", "order_status": "completed",
         "customer_id": "C2", "order_ts": datetime(2026, 8, 15, tzinfo=IST)},
    ]
    kpiv = compute_repeat_purchase_rate(orders, "Z003", 2026, 8)
    assert kpiv.numerator == 1   # C1 has 2 orders, C2 has 1
    assert kpiv.denominator == 2  # 2 active customers
    assert "tenure_filter" in kpiv.metadata
    assert "none_applied" in kpiv.metadata["tenure_filter"]


def test_c1_kpi_unknown_kpi_raises():
    from praxis.c1_data_foundation.kpi_contracts import get_contract
    with pytest.raises(KeyError, match="UNKNOWN_KPI"):
        get_contract("nonexistent_kpi")


# --- Entitlement Tests ---

def test_c1_entitlement_ops_manager_no_zone_gmv():
    from praxis.c1_data_foundation.entitlements import (
        EntitlementContext, Persona, can_access_zone_gmv_total
    )
    ctx = EntitlementContext(Persona.DARK_STORE_OPS_MANAGER, assigned_store="DS041")
    assert not can_access_zone_gmv_total(ctx)


def test_c1_entitlement_zone_head_can_see_zone_gmv():
    from praxis.c1_data_foundation.entitlements import (
        EntitlementContext, Persona, can_access_zone_gmv_total
    )
    ctx = EntitlementContext(Persona.ZONE_BUSINESS_HEAD, assigned_zone="Z003")
    assert can_access_zone_gmv_total(ctx)


def test_c1_entitlement_ops_manager_requires_store():
    from praxis.c1_data_foundation.entitlements import EntitlementContext, Persona
    with pytest.raises(ValueError):
        EntitlementContext(Persona.DARK_STORE_OPS_MANAGER)


# --- Lineage Tests ---

def test_c1_lineage_ids_deterministic():
    from praxis.c1_data_foundation.lineage import kpi_instance_id, finding_id
    kpi_inst = kpi_instance_id("zone_gmv", "Z003", "20260815")
    assert kpi_inst == "KPI-zone_gmv-Z003-20260815"
    fid = finding_id(kpi_inst, seq=1)
    assert fid == "FIND-KPI-zone_gmv-Z003-20260815-01"


def test_c1_lineage_canonical_s1_id():
    """C5 §5.1 exact ID from the worked example."""
    from praxis.c1_data_foundation.lineage import (
        kpi_instance_id, finding_id, decision_memory_id, outcome_memory_id
    )
    kpi_inst = kpi_instance_id("zone_gmv", "Z003", "20260815")
    fid = finding_id(kpi_inst)
    dm_id = decision_memory_id(fid)
    om_id = outcome_memory_id(dm_id)
    assert dm_id == "DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01"
    assert om_id == "OUT-DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01-01"
