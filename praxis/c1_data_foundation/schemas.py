"""C1 Data & Semantic Foundation — Pydantic schemas for all canonical entities.
Implements C1 §2–3 exact field definitions.
"""
from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enumerations — all locked per C1 §2 and §13
# ---------------------------------------------------------------------------

class OrderStatus(str, Enum):
    completed = "completed"
    cancelled = "cancelled"
    failed = "failed"


class SourceType(str, Enum):
    review = "review"
    chat = "chat"
    social = "social"
    csat = "csat"


class CustomerStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    churned = "churned"


class StoreStatus(str, Enum):
    live = "live"
    paused = "paused"
    closed = "closed"


class DataState(str, Enum):
    """C1 §13 — six data states, no silent defaults."""
    FRESH = "FRESH"
    STALE = "STALE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    CONFLICTING = "CONFLICTING"
    INVALID = "INVALID"


class ValidationStatus(str, Enum):
    """C1 §14 — used by C5 memory."""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    demo_preapproved = "demo_preapproved"


class GrainLevel(str, Enum):
    store = "store"
    zone = "zone"


# ---------------------------------------------------------------------------
# Dimension entities
# ---------------------------------------------------------------------------

class Zone(BaseModel):
    zone_id: str
    zone_name: str
    city: str


class DarkStore(BaseModel):
    dark_store_id: str
    zone_id: str
    store_name: str
    lat: float
    lon: float
    go_live_date: date
    status: StoreStatus


class SKU(BaseModel):
    sku_id: str
    sku_name: str
    category: str
    list_price: Decimal
    active_flag: bool


class Customer(BaseModel):
    customer_id: str
    home_zone_id: Optional[str] = None
    signup_ts: datetime
    customer_status: CustomerStatus


# ---------------------------------------------------------------------------
# Fact / Event entities
# ---------------------------------------------------------------------------

class OrderLineItem(BaseModel):
    order_line_id: str
    order_id: str
    sku_id: str
    units_sold: int = Field(ge=0)
    unit_price_at_sale: Decimal
    line_gmv: Decimal


class Order(BaseModel):
    order_id: str
    zone_id: str
    dark_store_id: str
    customer_id: str
    session_id: Optional[str] = None
    order_ts: datetime
    sku_line_items: List[OrderLineItem] = Field(default_factory=list)
    units_sold: int = Field(ge=0)
    gmv_value: Decimal
    discount_applied: Decimal = Field(ge=0, le=1)   # fraction [0,1] per C1 §1
    order_status: OrderStatus
    source_version: str
    ingested_at: datetime


class DeliveryEvent(BaseModel):
    delivery_event_id: str          # = order_id per C1 §2.2
    order_id: str
    dark_store_id: str
    rider_id: str
    dispatch_ts: datetime
    delivered_ts: Optional[datetime] = None
    sla_target_mins: int = Field(gt=0)
    sla_met: Optional[bool] = None   # null while in-transit


class InventoryEvent(BaseModel):
    stock_event_id: str
    dark_store_id: str
    sku_id: str
    ts: datetime
    stock_level: int = Field(ge=0)
    stockout_flag: bool


class AppSession(BaseModel):
    session_id: str
    customer_id: Optional[str] = None
    zone_id: str
    dark_store_id: Optional[str] = None
    session_start_ts: datetime
    cart_add_flag: bool
    cart_add_ts: Optional[datetime] = None
    converted_order_id: Optional[str] = None
    source_version: str
    ingested_at: datetime

    @model_validator(mode="after")
    def cart_add_ts_required_if_flag(self) -> "AppSession":
        """C1 §12 row 17 — cart_add_flag=true with null cart_add_ts is quarantinable."""
        if self.cart_add_flag and self.cart_add_ts is None:
            raise ValueError("cart_add_ts is required when cart_add_flag=true (C1 §12 row 17)")
        return self


class CustomerVoiceRecord(BaseModel):
    record_id: str
    zone_id: str
    customer_id: Optional[str] = None
    ts: datetime
    source_type: SourceType
    text: str
    matched_day: date
    matched_week: str   # ISO week string e.g. "2026-W33"
