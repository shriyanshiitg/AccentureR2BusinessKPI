"""C1 §12 — 18-row Data Quality Gate.

Each check returns a DQResult with severity and action.
BLOCK   = excluded from all downstream computation
QUARANTINE = excluded from KPI computation, retained for investigation
WARN    = included but flagged
PASS    = no flag
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DQAction(str, Enum):
    BLOCK = "BLOCK"
    QUARANTINE = "QUARANTINE"
    WARN = "WARN"
    PASS = "PASS"


@dataclass
class DQResult:
    check_id: int
    rule: str
    severity: Severity
    action: DQAction
    passed: bool
    detail: str = ""


@dataclass
class DQReport:
    record_type: str
    record_id: str
    results: List[DQResult] = field(default_factory=list)

    @property
    def final_action(self) -> DQAction:
        """Worst action among all failed checks."""
        priority = {DQAction.BLOCK: 3, DQAction.QUARANTINE: 2,
                    DQAction.WARN: 1, DQAction.PASS: 0}
        worst = DQAction.PASS
        for r in self.results:
            if not r.passed and priority[r.action] > priority[worst]:
                worst = r.action
        return worst

    @property
    def passes(self) -> bool:
        return self.final_action == DQAction.PASS

    def failed_checks(self) -> List[DQResult]:
        return [r for r in self.results if not r.passed]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
IST_OFFSET = 5.5 * 3600  # seconds

def _now_ist() -> datetime:
    from datetime import timezone, timedelta
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(tz=ist)


def check_order(record: Dict[str, Any], known_stores: set, known_zones: set,
                known_customers: set) -> DQReport:
    """Run all applicable DQ checks against an order dict."""
    report = DQReport("Order", record.get("order_id", "UNKNOWN"))

    def _add(check_id: int, rule: str, severity: Severity,
              action: DQAction, passed: bool, detail: str = ""):
        report.results.append(DQResult(check_id, rule, severity, action, passed, detail))

    # 1 — schema / required fields
    required = ["order_id", "zone_id", "dark_store_id", "customer_id",
                "order_ts", "gmv_value", "discount_applied", "order_status",
                "source_version", "ingested_at", "units_sold"]
    missing = [f for f in required if f not in record or record[f] is None]
    _add(1, "required_fields", Severity.CRITICAL, DQAction.BLOCK,
         len(missing) == 0, f"Missing: {missing}")

    # 2 — duplicate PK handled at batch level; skip here (planner level)

    # 4 — referential integrity: dark_store_id in dimension
    dsid = record.get("dark_store_id")
    _add(4, "dark_store_ref", Severity.CRITICAL, DQAction.BLOCK,
         dsid in known_stores, f"Unknown dark_store_id: {dsid}")

    # 5 — referential integrity: customer_id in dimension
    cust = record.get("customer_id")
    _add(5, "customer_ref", Severity.HIGH, DQAction.QUARANTINE,
         cust in known_customers, f"Unknown customer_id: {cust}")

    # 9 — range: units_sold >= 0, gmv_value >= 0
    usold = record.get("units_sold", 0)
    gmv = record.get("gmv_value", 0)
    _add(9, "range_units_gmv", Severity.CRITICAL, DQAction.BLOCK,
         usold >= 0 and float(gmv) >= 0,
         f"units_sold={usold}, gmv_value={gmv}")

    # 8 — discount_applied in [0,1]
    disc = float(record.get("discount_applied", 0))
    _add(8, "discount_range", Severity.HIGH, DQAction.QUARANTINE,
         0 <= disc <= 1, f"discount_applied={disc}")

    # 14 — order_status valid enum
    valid_statuses = {"completed", "cancelled", "failed"}
    status = record.get("order_status", "")
    _add(14, "order_status_enum", Severity.HIGH, DQAction.QUARANTINE,
         status in valid_statuses, f"order_status={status!r}")

    # 12 — timestamp in the future (clock skew, >5 min)
    ots = record.get("order_ts")
    if isinstance(ots, datetime):
        skew = (ots.timestamp() - _now_ist().timestamp()) > 300
        _add(12, "clock_skew", Severity.MEDIUM, DQAction.QUARANTINE,
             not skew, f"order_ts appears {ots} in the future")

    # 16 — completed order must have >= 1 line item
    if status == "completed":
        lines = record.get("sku_line_items", [])
        _add(16, "completed_has_lines", Severity.CRITICAL, DQAction.BLOCK,
             len(lines) >= 1, "completed order has zero line items")

    # 11 — gmv_value vs SUM(line_gmv): tolerance >₹1 or >0.5% (BD-001)
    lines = record.get("sku_line_items", [])
    if lines:
        sum_line_gmv = sum(float(l.get("line_gmv", 0)) for l in lines)
        diff = abs(float(gmv) - sum_line_gmv)
        tolerance_abs = 1.0
        tolerance_pct = 0.005 * float(gmv) if float(gmv) > 0 else 0
        conflict = diff > max(tolerance_abs, tolerance_pct)
        _add(11, "gmv_line_reconciliation", Severity.MEDIUM, DQAction.WARN,
             not conflict,
             f"order.gmv_value={gmv} vs SUM(line_gmv)={sum_line_gmv:.2f}, diff={diff:.2f}")

    return report


def check_inventory_event(record: Dict[str, Any], known_stores: set,
                           known_skus: set) -> DQReport:
    report = DQReport("InventoryEvent", record.get("stock_event_id", "UNKNOWN"))

    def _add(check_id, rule, severity, action, passed, detail=""):
        report.results.append(DQResult(check_id, rule, severity, action, passed, detail))

    required = ["stock_event_id", "dark_store_id", "sku_id", "ts",
                 "stock_level", "stockout_flag"]
    missing = [f for f in required if f not in record or record[f] is None]
    _add(1, "required_fields", Severity.CRITICAL, DQAction.BLOCK,
         len(missing) == 0, f"Missing: {missing}")

    _add(4, "dark_store_ref", Severity.CRITICAL, DQAction.BLOCK,
         record.get("dark_store_id") in known_stores, "Unknown dark_store_id")

    _add(5, "sku_ref", Severity.HIGH, DQAction.QUARANTINE,
         record.get("sku_id") in known_skus, "Unknown sku_id")

    sl = record.get("stock_level", 0)
    _add(7, "stock_level_non_negative", Severity.HIGH, DQAction.QUARANTINE,
         int(sl) >= 0, f"stock_level={sl}")

    # 18 — duplicate event at (dark_store_id, sku_id, ts) handled at batch level
    return report


def check_delivery_event(record: Dict[str, Any], known_orders: set) -> DQReport:
    report = DQReport("DeliveryEvent", record.get("delivery_event_id", "UNKNOWN"))

    def _add(check_id, rule, severity, action, passed, detail=""):
        report.results.append(DQResult(check_id, rule, severity, action, passed, detail))

    required = ["delivery_event_id", "order_id", "dark_store_id", "rider_id",
                "dispatch_ts", "sla_target_mins"]
    missing = [f for f in required if f not in record or record[f] is None]
    _add(1, "required_fields", Severity.CRITICAL, DQAction.BLOCK,
         len(missing) == 0, f"Missing: {missing}")

    # 15 — orphan delivery event
    _add(15, "order_ref", Severity.CRITICAL, DQAction.BLOCK,
         record.get("order_id") in known_orders, "order_id not in known orders")

    # 10 — delivered_ts >= dispatch_ts
    dts = record.get("dispatch_ts")
    delts = record.get("delivered_ts")
    if delts and dts and isinstance(dts, datetime) and isinstance(delts, datetime):
        _add(10, "delivered_after_dispatch", Severity.HIGH, DQAction.QUARANTINE,
             delts >= dts, f"delivered_ts={delts} < dispatch_ts={dts}")

    slat = record.get("sla_target_mins", 1)
    _add(9, "sla_target_positive", Severity.CRITICAL, DQAction.BLOCK,
         int(slat) > 0, f"sla_target_mins={slat}")

    return report


def check_app_session(record: Dict[str, Any], known_orders: set) -> DQReport:
    report = DQReport("AppSession", record.get("session_id", "UNKNOWN"))

    def _add(check_id, rule, severity, action, passed, detail=""):
        report.results.append(DQResult(check_id, rule, severity, action, passed, detail))

    required = ["session_id", "zone_id", "session_start_ts",
                "cart_add_flag", "source_version", "ingested_at"]
    missing = [f for f in required if f not in record or record[f] is None]
    _add(1, "required_fields", Severity.CRITICAL, DQAction.BLOCK,
         len(missing) == 0, f"Missing: {missing}")

    # 17 — cart_add_flag=true with null cart_add_ts
    caf = record.get("cart_add_flag", False)
    cats = record.get("cart_add_ts")
    _add(17, "cart_add_ts_required", Severity.HIGH, DQAction.QUARANTINE,
         not (caf and cats is None), "cart_add_flag=true but cart_add_ts is null")

    # 6 — converted_order_id set but order doesn't exist
    coid = record.get("converted_order_id")
    if coid:
        _add(6, "converted_order_ref", Severity.MEDIUM, DQAction.WARN,
             coid in known_orders,
             f"converted_order_id={coid!r} not found — treated as unconverted")

    return report
