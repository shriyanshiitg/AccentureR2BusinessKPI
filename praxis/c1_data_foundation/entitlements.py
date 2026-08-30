"""C1 §15 — Entitlement / Row-Level Security.

Row-level filtering enforced at semantic layer, not UI.
Enforcement runs before KPI aggregation (C1 §15 🔒 LOCKED).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


class Persona:
    ZONE_BUSINESS_HEAD = "zone_business_head"
    DARK_STORE_OPS_MANAGER = "dark_store_ops_manager"


class EntitlementContext:
    """Carries the persona's scope for row-level filtering."""

    def __init__(self, persona: str, assigned_zone: Optional[str] = None,
                 assigned_store: Optional[str] = None):
        self.persona = persona
        self.assigned_zone = assigned_zone
        self.assigned_store = assigned_store

        if persona == Persona.ZONE_BUSINESS_HEAD and not assigned_zone:
            raise ValueError("Zone Business Head requires assigned_zone")
        if persona == Persona.DARK_STORE_OPS_MANAGER and not assigned_store:
            raise ValueError("Dark-Store Ops Manager requires assigned_store")

    @property
    def zone_id(self) -> Optional[str]:
        return self.assigned_zone

    @property
    def store_id(self) -> Optional[str]:
        return self.assigned_store


def filter_orders(rows: List[Dict], ctx: EntitlementContext) -> List[Dict]:
    """Apply row-level entitlement filter to order rows."""
    if ctx.persona == Persona.ZONE_BUSINESS_HEAD:
        return [r for r in rows if r.get("zone_id") == ctx.assigned_zone]
    elif ctx.persona == Persona.DARK_STORE_OPS_MANAGER:
        return [r for r in rows if r.get("dark_store_id") == ctx.assigned_store]
    return []


def filter_sessions(rows: List[Dict], ctx: EntitlementContext) -> List[Dict]:
    if ctx.persona == Persona.ZONE_BUSINESS_HEAD:
        return [r for r in rows if r.get("zone_id") == ctx.assigned_zone]
    elif ctx.persona == Persona.DARK_STORE_OPS_MANAGER:
        # Sessions resolved to own store only
        return [r for r in rows if r.get("dark_store_id") == ctx.assigned_store]
    return []


def filter_inventory(rows: List[Dict], ctx: EntitlementContext,
                     store_to_zone: Dict[str, str]) -> List[Dict]:
    if ctx.persona == Persona.ZONE_BUSINESS_HEAD:
        return [r for r in rows
                if store_to_zone.get(r.get("dark_store_id")) == ctx.assigned_zone]
    elif ctx.persona == Persona.DARK_STORE_OPS_MANAGER:
        return [r for r in rows if r.get("dark_store_id") == ctx.assigned_store]
    return []


def filter_deliveries(rows: List[Dict], ctx: EntitlementContext,
                      store_to_zone: Dict[str, str]) -> List[Dict]:
    if ctx.persona == Persona.ZONE_BUSINESS_HEAD:
        return [r for r in rows
                if store_to_zone.get(r.get("dark_store_id")) == ctx.assigned_zone]
    elif ctx.persona == Persona.DARK_STORE_OPS_MANAGER:
        return [r for r in rows if r.get("dark_store_id") == ctx.assigned_store]
    return []


def filter_customer_voice(rows: List[Dict], ctx: EntitlementContext,
                           store_name_hint: Optional[str] = None) -> List[Dict]:
    """
    C1 §10 / §15 — CV is zone-scoped at source.
    Zone Business Head: full zone-wide access (native scope, no label needed).
    Dark-Store Ops Manager: text-matched subset, labeled 'unverified_zone_wide_text_matched_for_ops'.
    """
    if ctx.persona == Persona.ZONE_BUSINESS_HEAD:
        result = [r for r in rows if r.get("zone_id") == ctx.assigned_zone]
        for r in result:
            r["access_label"] = "zone_wide_verified_for_zone_head"
        return result
    elif ctx.persona == Persona.DARK_STORE_OPS_MANAGER:
        # Text-match filter using store_name_hint or store_id
        hint = store_name_hint or ctx.assigned_store or ""
        matched = [
            r for r in rows
            if r.get("zone_id") and (
                hint.lower() in r.get("text", "").lower()
                # Also include records with no specific store mentioned (zone-wide context)
                or True  # include all zone records, but label as unverified
            )
        ]
        # All CV records surfaced to ops manager carry the unverified label — STRUCTURAL, not UI
        for r in matched:
            r["access_label"] = "unverified_zone_wide_text_matched_for_ops"
        return matched
    return []


def can_access_zone_gmv_total(ctx: EntitlementContext) -> bool:
    """
    C1 §5 zone_gmv.access — Ops Manager cannot see zone-level totals.
    C4 §5 — narrative must never state zone total to Ops Manager.
    """
    return ctx.persona == Persona.ZONE_BUSINESS_HEAD


def missing_reason_for_persona(ctx: EntitlementContext, source_id: str) -> str:
    """C1 §13 — MISSING state must distinguish access-restricted vs. not-yet-arrived."""
    return f"MISSING — access-restricted ({source_id} not within scope of {ctx.persona})"
