"""C4 §5-6 — Persona Narrative Renderer.

LLM renders the narrative prose.
Code enforces:
- Confidence passthrough from C3 (LLM never recomputes or softens the band)
- Zone GMV total never surfaced to Ops Manager (C1 §5 entitlement, structural enforcement)
- Caveat text is mandatory-non-null for non-ANSWER decisions (structural, not instructional)
- Lever selection by code, not LLM
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from praxis.c1_data_foundation.entitlements import EntitlementContext, Persona, can_access_zone_gmv_total
from praxis.c3_reasoning.hypothesis_package import HypothesisPackage
from praxis.c4_decision.decision_package import (
    LEVERS, select_lever, assign_owner, ActionItem, DecisionPackage, decision_package_id
)


IST = timezone(timedelta(hours=5, minutes=30))


def build_decision_package(
    hypothesis_package: HypothesisPackage,
    kpi_id: str,
    grain_key: str,
    period: str,
    delta_abs: float,        # absolute KPI delta (from C2 detection)
    delta_relative: float,
    leading_store_id: Optional[str],  # top contributing store, from C2 segmentation
    persona: str,
    llm_client=None,
    zone_gmv_delta: Optional[float] = None,  # only visible to zone head
    sku_info: Optional[Dict] = None,
) -> DecisionPackage:
    """
    Build the DecisionPackage, rendering persona-appropriate narratives.
    """
    hp = hypothesis_package
    decision = hp.decision
    outcome = decision.get("outcome", "ABSTAIN")
    leading_hyp_id = decision.get("leading_hypothesis_id")
    caveat_text = decision.get("caveat_text")
    clarifying_q = decision.get("clarifying_question")
    abstain_reason = decision.get("abstain_reason")
    memory_ctx = decision.get("memory_context", {}) or {}

    # Find leading hypothesis
    leading_hyp = next(
        (h for h in hp.hypotheses if h.get("hypothesis_id") == leading_hyp_id),
        None
    )

    driver_type = leading_hyp["driver_type"] if leading_hyp else "residual"
    confidence_band = leading_hyp["confidence_band"] if leading_hyp else "INSUFFICIENT"
    contribution_pct = leading_hyp.get("contribution_pct", 0) if leading_hyp else 0

    # --- Lever selection (code, not LLM) ---
    lever_id = select_lever(driver_type, outcome)
    lever = LEVERS.get(lever_id, LEVERS["L8_monitor_no_action"])

    # --- Action item ---
    # Deterministic action text per driver/lever/persona
    action_text = _build_action_text(
        lever_id, driver_type, grain_key, period, leading_store_id, sku_info, persona
    )
    expected_impact = _build_expected_impact(
        lever_id, kpi_id, delta_abs, delta_relative, llm_client,
        contribution_pct=contribution_pct,
    )
    monitoring_plan = _build_monitoring_plan(lever_id, outcome, memory_ctx)

    ops_owner = assign_owner(lever_id, persona)

    action = ActionItem(
        driver=driver_type,
        controllable_lever=lever_id,
        action=action_text,
        expected_impact=expected_impact,
        owner=ops_owner,
        confidence=confidence_band,  # verbatim passthrough — never softened
        monitoring_plan=monitoring_plan,
    )

    # --- Determine caveat source field ---
    if outcome == "ANSWER":
        caveat_source = "none"
    elif outcome in ("QUALIFY", "CLARIFY"):
        caveat_source = "caveat_text"
    else:
        caveat_source = "abstain_reason"
        caveat_text = abstain_reason

    # --- Persona narratives (LLM or deterministic template) ---
    zone_head_narrative = _render_narrative(
        persona=Persona.ZONE_BUSINESS_HEAD,
        kpi_id=kpi_id,
        grain_key=grain_key,
        period=period,
        outcome=outcome,
        driver_type=driver_type,
        contribution_pct=contribution_pct,
        confidence_band=confidence_band,
        caveat_text=caveat_text,
        lever_id=lever_id,
        lever_desc=lever["description"],
        delta_abs=delta_abs,
        delta_relative=delta_relative,
        zone_gmv_delta=zone_gmv_delta,   # zone head sees this
        leading_store_id=leading_store_id,
        memory_ctx=memory_ctx,
        llm_client=llm_client,
        clarifying_q=clarifying_q,
    )

    ops_narrative = _render_narrative(
        persona=Persona.DARK_STORE_OPS_MANAGER,
        kpi_id=kpi_id,
        grain_key=grain_key,
        period=period,
        outcome=outcome,
        driver_type=driver_type,
        contribution_pct=contribution_pct,
        confidence_band=confidence_band,
        caveat_text=caveat_text,
        lever_id=lever_id,
        lever_desc=lever["description"],
        delta_abs=delta_abs,
        delta_relative=delta_relative,
        zone_gmv_delta=None,  # ENTITLEMENT: ops manager never sees zone GMV total
        leading_store_id=leading_store_id,
        memory_ctx=memory_ctx,
        llm_client=llm_client,
        clarifying_q=clarifying_q,
    )

    pkg_id = decision_package_id(hp.finding_id)
    now = datetime.now(tz=IST).isoformat()

    pkg = DecisionPackage(
        decision_package_id=pkg_id,
        finding_id=hp.finding_id,
        hypothesis_package_ref=hp.finding_id,
        evidence_package_ref=hp.evidence_package_ref,
        lineage_chain=hp.lineage_chain,
        generated_at=now,
        source_decision_outcome=outcome,
        source_decision_scope=decision.get("scope", "finding"),
        actions=[action],
        caveat_text=caveat_text,
        caveat_source_field=caveat_source,
        narrative_zone_business_head=zone_head_narrative,
        narrative_dark_store_ops_manager=ops_narrative,
    )

    # Structural validation — raises if caveat_text violated
    pkg.validate()
    return pkg


def _render_narrative(
    persona: str, kpi_id: str, grain_key: str, period: str,
    outcome: str, driver_type: str, contribution_pct: float,
    confidence_band: str, caveat_text: Optional[str], lever_id: str,
    lever_desc: str, delta_abs: float, delta_relative: float,
    zone_gmv_delta: Optional[float], leading_store_id: Optional[str],
    memory_ctx: Dict, llm_client, clarifying_q: Optional[str] = None,
) -> str:

    # ABSTAIN — identical for both personas, no lever recommendation
    if outcome == "ABSTAIN":
        if persona == Persona.ZONE_BUSINESS_HEAD:
            return (
                f"Zone {grain_key} — {period}\n\n"
                f"Praxis cannot provide a reliable explanation for the movement in "
                f"{kpi_id} at this time.\n\n"
                f"Reason: {caveat_text}\n\n"
                f"Recommended action: Escalate for manual investigation (L7) "
                f"or wait for additional data before drawing conclusions."
            )
        else:
            return (
                f"Store {leading_store_id or grain_key} — {period}\n\n"
                f"Praxis is currently unable to identify the root cause of the "
                f"observed operational issue at your store.\n\n"
                f"Reason: {caveat_text}\n\n"
                f"Please flag this to your Zone Business Head."
            )

    # Attempt LLM narrative (bounded)
    if llm_client:
        try:
            return _llm_narrative(
                llm_client=llm_client,
                persona=persona,
                kpi_id=kpi_id,
                grain_key=grain_key,
                period=period,
                outcome=outcome,
                driver_type=driver_type,
                contribution_pct=contribution_pct,
                confidence_band=confidence_band,
                caveat_text=caveat_text,
                lever_id=lever_id,
                lever_desc=lever_desc,
                delta_abs=delta_abs,
                delta_relative=delta_relative,
                zone_gmv_delta=zone_gmv_delta,
                leading_store_id=leading_store_id,
                memory_ctx=memory_ctx,
                clarifying_q=clarifying_q,
            )
        except Exception:
            pass  # fall through to template

    return _template_narrative(
        persona=persona, kpi_id=kpi_id, grain_key=grain_key, period=period,
        outcome=outcome, driver_type=driver_type, contribution_pct=contribution_pct,
        confidence_band=confidence_band, caveat_text=caveat_text,
        lever_id=lever_id, lever_desc=lever_desc, delta_abs=delta_abs,
        delta_relative=delta_relative, zone_gmv_delta=zone_gmv_delta,
        leading_store_id=leading_store_id, memory_ctx=memory_ctx,
        clarifying_q=clarifying_q,
    )


def _llm_narrative(llm_client, persona, kpi_id, grain_key, period, outcome,
                   driver_type, contribution_pct, confidence_band, caveat_text,
                   lever_id, lever_desc, delta_abs, delta_relative, zone_gmv_delta,
                   leading_store_id, memory_ctx, clarifying_q) -> str:

    gmv_line = ""
    if zone_gmv_delta is not None and persona == Persona.ZONE_BUSINESS_HEAD:
        gmv_line = f"Zone GMV impact: ₹{abs(zone_gmv_delta):,.0f} {'below' if zone_gmv_delta < 0 else 'above'} baseline. "

    store_line = ""
    if leading_store_id and persona == Persona.DARK_STORE_OPS_MANAGER:
        store_line = f"Primary affected store: {leading_store_id}. "
    elif leading_store_id and persona == Persona.ZONE_BUSINESS_HEAD:
        store_line = f"Leading store contributor: {leading_store_id}. "

    mem_line = ""
    if memory_ctx.get("matched") and memory_ctx.get("confirmed_precedents", 0) > 0:
        mem_line = (
            f"Memory context: {memory_ctx['confirmed_precedents']} prior confirmed "
            f"precedent(s) for this exact driver/store combination were retrieved. "
            f"This raises confidence from LOW to MEDIUM (one precedent, C5 §4.2 cap applies). "
        )

    caveat_line = f"Mandatory caveat: {caveat_text}" if caveat_text and outcome != "ANSWER" else ""
    clarify_line = f"Clarifying question to embed: {clarifying_q}" if clarifying_q else ""

    if persona == Persona.ZONE_BUSINESS_HEAD:
        role_context = (
            "You are writing a weekly ops-review narrative for a City/Zone Business Head. "
            "Show zone-wide driver ranking, GMV impact, and confidence band. "
            "Recommend a strategic lever. "
            "Do NOT mention individual SKU details unless they are the dominant driver."
        )
    else:
        role_context = (
            "You are writing an in-app operational task for a Dark-Store Ops Manager. "
            "Focus on single-dark-store, single-SKU granularity. "
            "Give a concrete operational task. "
            "Do NOT state any zone-level GMV total — Ops Manager does not have access to this figure. "
        )

    prompt = (
        f"{role_context}\n\n"
        f"Finding: {kpi_id} at {grain_key} on {period}.\n"
        f"Decision outcome: {outcome}. Confidence band: {confidence_band} (do NOT soften this — report exactly as stated).\n"
        f"Leading driver: {driver_type} (~{contribution_pct:.0f}% contribution).\n"
        f"Recommended lever: {lever_id} — {lever_desc}.\n"
        f"{gmv_line}{store_line}{mem_line}"
        f"{caveat_line}\n"
        f"{clarify_line}\n\n"
        f"Write a concise narrative (4-6 sentences). Be honest, not confident beyond the band."
    )

    return llm_client.generate_text(prompt, max_tokens=300)


def _template_narrative(persona, kpi_id, grain_key, period, outcome, driver_type,
                         contribution_pct, confidence_band, caveat_text, lever_id,
                         lever_desc, delta_abs, delta_relative, zone_gmv_delta,
                         leading_store_id, memory_ctx, clarifying_q) -> str:

    mem_line = ""
    if memory_ctx.get("matched") and memory_ctx.get("confirmed_precedents", 0) > 0:
        mem_line = (
            f"\n\n**Memory context:** {memory_ctx['confirmed_precedents']} prior confirmed "
            f"precedent(s) for this driver/store combination have been retrieved. "
            f"This raises confidence from LOW to MEDIUM. A single precedent is not treated "
            f"as confirmation (C5 §4.2 hard cap)."
        )

    caveat_block = f"\n\n**Caveat ({confidence_band}):** {caveat_text}" if caveat_text and outcome != "ANSWER" else ""
    clarify_block = f"\n\n**Clarifying question:** {clarifying_q}" if clarifying_q else ""

    if persona == Persona.ZONE_BUSINESS_HEAD:
        gmv_text = ""
        if zone_gmv_delta is not None:
            gmv_text = f"Zone GMV is approximately ₹{abs(zone_gmv_delta):,.0f} {'below' if zone_gmv_delta < 0 else 'above'} baseline. "

        store_text = f"The leading contributing store is **{leading_store_id}**. " if leading_store_id else ""

        return (
            f"**Zone {grain_key} — {period} | {kpi_id.replace('_', ' ').upper()}**\n\n"
            f"{gmv_text}"
            f"The leading explanation is **{driver_type.replace('_', ' ')}** "
            f"(~{abs(contribution_pct):.0f}% of the movement), with confidence band **{confidence_band}**. "
            f"{store_text}"
            f"Recommended action: **{lever_id} — {lever_desc}**."
            f"{caveat_block}{clarify_block}{mem_line}"
        )
    else:
        # Ops Manager — never zone GMV total
        store_text = f"at **{leading_store_id}**" if leading_store_id else f"in zone {grain_key}"
        return (
            f"**Store {leading_store_id or grain_key} — {period} | Operational Alert**\n\n"
            f"A **{driver_type.replace('_', ' ')}** pattern has been detected {store_text}. "
            f"Confidence level: **{confidence_band}**. "
            f"Recommended action: **{lever_id} — {lever_desc}**."
            f"{caveat_block}{clarify_block}{mem_line}"
        )


def _build_action_text(lever_id, driver_type, grain_key, period,
                        leading_store_id, sku_info, persona) -> str:
    templates = {
        "L1_restock_sku_store": (
            f"Restock {'SKU ' + sku_info.get('sku_name', 'affected SKU') if sku_info else 'affected SKU(s)'} "
            f"at {leading_store_id or grain_key} by end of day."
        ),
        "L2_cross_store_transfer": (
            f"Authorize cross-store inventory transfer of affected SKU(s) into "
            f"{leading_store_id or grain_key} from neighboring store with surplus inventory."
        ),
        "L3_add_rider_capacity": (
            f"Add up to 2 additional riders to the evening shift at "
            f"{leading_store_id or grain_key} to address delivery SLA breach."
        ),
        "L4_approve_local_promo": (
            f"Approve a 3-day local promotional offer in zone {grain_key} "
            f"to offset the conversion dip."
        ),
        "L5_adjust_dispatch_schedule": (
            f"Adjust dispatch scheduling for {leading_store_id or grain_key} "
            f"to reduce delivery queue depth."
        ),
        "L6_flag_competitor_opening": (
            f"Flag new competitor dark-store opening in zone {grain_key} "
            f"for pricing and promotional strategy review."
        ),
        "L7_escalate_for_investigation": (
            f"Escalate finding for manual investigation — "
            f"evidence is insufficient for a confident recommendation."
        ),
        "L8_monitor_no_action": (
            f"Monitor {grain_key} over the next 48 hours. No action at this time."
        ),
    }
    return templates.get(lever_id, f"Execute {lever_id} at {grain_key}.")


def _build_expected_impact(
    lever_id: str, kpi_id: str, delta_abs: float, delta_relative: float,
    llm_client, contribution_pct: float = 0.0
) -> str:
    """
    Compute a deterministic expected impact string.
    Includes a recoverable ₹ amount where computable (G2 fix).
    contribution_pct × abs(delta_abs) = recoverable portion.
    """
    recoverable = abs(delta_abs) * (abs(contribution_pct) / 100.0) if contribution_pct else 0.0
    rec_L = recoverable / 100_000  # convert to Lakhs
    total_L = abs(delta_abs) / 100_000

    if lever_id == "L2_cross_store_transfer":
        if recoverable > 0 and total_L > 0:
            return (
                f"Recover ~₹{rec_L:.1f}L of ₹{total_L:.1f}L gap within 24–48h "
                f"(stockout contribution: {abs(contribution_pct):.0f}% — deterministic attribution)."
            )
        return (
            f"If the stockout hypothesis is correct, resolving stock at the leading store "
            f"is expected to recover a material portion of the {kpi_id} gap within 24–48 hours."
        )
    if lever_id == "L1_restock_sku_store":
        if recoverable > 0:
            return (
                f"Recover ~₹{rec_L:.1f}L through SKU restocking. "
                f"Availability-driven portion resolves within 4–6 hours."
            )
        return "Restocking affected SKU(s) should recover the availability-driven portion within 4–6 hours."
    if lever_id == "L3_add_rider_capacity":
        return (
            f"Adding riders to the affected shift expected to reduce SLA breaches "
            f"and recover ~₹{rec_L:.1f}L of conversion loss during peak window."
        ) if recoverable > 0 else "Adding riders expected to reduce delivery SLA breaches during peak window."
    if lever_id == "L4_approve_local_promo":
        return (
            f"3-day promo expected to partially offset conversion dip, "
            f"targeting recovery of ~₹{rec_L:.1f}L during promotional window."
        ) if recoverable > 0 else "3-day promo should partially offset the conversion dip in the zone."
    if lever_id == "L7_escalate_for_investigation":
        return "Impact unknown — root cause not yet confirmed."
    if lever_id == "L8_monitor_no_action":
        return "No action; monitor for resolution."
    return f"Expected to address root cause of {kpi_id} movement."


def _build_monitoring_plan(lever_id, outcome, memory_ctx) -> str:
    confirmed = memory_ctx.get("confirmed_precedents", 0) > 0 if memory_ctx else False

    if lever_id in ("L7_escalate_for_investigation", "L8_monitor_no_action"):
        return "Re-evaluate in 24 hours. Flag if movement persists or worsens."

    if confirmed:
        # Narrower monitoring plan when precedent exists
        return (
            "Re-check the leading KPI metric at 24 hours and 48 hours after action. "
            "A prior confirmed precedent for this driver exists — "
            "expect recovery within the same timeline as before."
        )

    if outcome == "QUALIFY":
        return (
            "Monitor the leading KPI metric at 24 hours and 48 hours post-action. "
            "If the gap does not narrow within 48 hours, trigger a follow-up investigation (L7-adjacent). "
            "This recommendation is QUALIFY (not ANSWER); outcome monitoring is mandatory."
        )

    return (
        "Monitor the leading KPI metric at 24 hours and 48 hours post-action. "
        "Record outcome in Praxis memory to inform future similar findings."
    )


def compute_counterfactual(actual_value: float, delta_abs: float, contribution_pct: float) -> Optional[float]:
    """
    Deterministic counterfactual: what would the KPI value have been
    if the leading driver had NOT been present?

    Formula: actual_value + (abs(delta_abs) × contribution_pct / 100)
    i.e. we add back the portion of the gap that the leading driver explains.

    Returns None if inputs are insufficient for a meaningful answer.
    """
    if not contribution_pct or contribution_pct <= 0:
        return None
    recoverable = abs(delta_abs) * (abs(contribution_pct) / 100.0)
    return actual_value + recoverable


def compute_downstream_risks(driver_type: str, kpi_id: str) -> list:
    """
    Rule-based downstream risk detection (G3 fix).
    Returns list of dicts: {kpi_id, kpi_name, lag, description}
    if the active driver appears as a known driver in another KPI's contract.

    Purely deterministic — no LLM involved.
    """
    try:
        from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS
    except ImportError:
        return []

    risks = []
    for other_kpi_id, contract in KPI_CONTRACTS.items():
        if other_kpi_id == kpi_id:
            continue  # skip the current KPI
        if driver_type in contract.get("drivers", []):
            grain_type = contract.get("grain_type", "day")
            lag_str = "monthly lag" if grain_type == "month" else "same-day effect"
            risks.append({
                "affected_kpi_id": other_kpi_id,
                "affected_kpi_name": contract.get("name", other_kpi_id),
                "grain_type": grain_type,
                "lag_description": lag_str,
                "driver_type": driver_type,
            })
    return risks
