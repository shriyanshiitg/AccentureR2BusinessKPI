"""C2 §3 — Operator 5: Day → Month Precedence Check.

Implements C1 §7.2 exactly:
- Customer-level linkage required
- Strict precedence: driver_event_ts < subsequent_order_ts
- Minimum 1-day lag
- Maximum 45-day lookback from start of month M's evaluation window
- Same-month co-occurrence alone is rejected
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timedelta, timezone
from typing import Optional


IST = timezone(timedelta(hours=5, minutes=30))

MIN_LAG_DAYS = 1       # C1 §7.2
MAX_LOOKBACK_DAYS = 45  # C1 §7.2 (prototype assumption)


@dataclass
class PrecedenceResult:
    eligible: bool
    reason: str
    candidate_customer_id: Optional[str] = None
    driver_event_ts: Optional[datetime] = None
    subsequent_order_ts: Optional[datetime] = None
    linked_finding_id: Optional[str] = None  # RPR finding_id, if eligible


def check_precedence(
    customer_id: str,
    driver_event_ts: datetime,
    subsequent_order_ts: Optional[datetime],
    month_year: int,
    month_month: int,
    rpr_finding_id: Optional[str] = None,
) -> PrecedenceResult:
    """
    Check if a candidate day-grain driver event is eligible as a
    candidate explanation for a month-grain RPR movement.

    Parameters
    ----------
    customer_id : str
    driver_event_ts : datetime (event when the driver affected this customer)
    subsequent_order_ts : datetime | None (customer's next order after the event)
    month_year, month_month : the target RPR month (M)
    rpr_finding_id : the FIND-... id of the RPR finding this would link to
    """
    if driver_event_ts.tzinfo is None:
        driver_event_ts = driver_event_ts.replace(tzinfo=IST)
    driver_event_ts = driver_event_ts.astimezone(IST)

    # Month M evaluation window start
    month_start = datetime(month_year, month_month, 1, tzinfo=IST)

    # 1. Customer-level linkage — required (we have customer_id here)
    if not customer_id:
        return PrecedenceResult(
            eligible=False,
            reason="UNRESOLVED_CUSTOMER_LINKAGE",
            candidate_customer_id=customer_id,
        )

    # 2. Strict precedence: driver_event_ts < subsequent_order_ts
    if subsequent_order_ts is None:
        return PrecedenceResult(
            eligible=False,
            reason="NO_SUBSEQUENT_ORDER",
            candidate_customer_id=customer_id,
            driver_event_ts=driver_event_ts,
        )

    if subsequent_order_ts.tzinfo is None:
        subsequent_order_ts = subsequent_order_ts.replace(tzinfo=IST)
    subsequent_order_ts = subsequent_order_ts.astimezone(IST)

    if driver_event_ts >= subsequent_order_ts:
        return PrecedenceResult(
            eligible=False,
            reason="PRECEDENCE_VIOLATION",
            candidate_customer_id=customer_id,
            driver_event_ts=driver_event_ts,
            subsequent_order_ts=subsequent_order_ts,
        )

    # 3. Minimum 1-day lag
    lag_days = (subsequent_order_ts.date() - driver_event_ts.date()).days
    if lag_days < MIN_LAG_DAYS:
        return PrecedenceResult(
            eligible=False,
            reason="MIN_LAG_VIOLATION",
            candidate_customer_id=customer_id,
            driver_event_ts=driver_event_ts,
            subsequent_order_ts=subsequent_order_ts,
        )

    # 4. Maximum 45-day lookback from start of month M
    lookback = (month_start.date() - driver_event_ts.date()).days
    if lookback > MAX_LOOKBACK_DAYS:
        return PrecedenceResult(
            eligible=False,
            reason=f"LOOKBACK_EXCEEDED ({lookback} days > {MAX_LOOKBACK_DAYS})",
            candidate_customer_id=customer_id,
            driver_event_ts=driver_event_ts,
            subsequent_order_ts=subsequent_order_ts,
        )

    return PrecedenceResult(
        eligible=True,
        reason="ALL_CHECKS_PASSED",
        candidate_customer_id=customer_id,
        driver_event_ts=driver_event_ts,
        subsequent_order_ts=subsequent_order_ts,
        linked_finding_id=rpr_finding_id,
    )
