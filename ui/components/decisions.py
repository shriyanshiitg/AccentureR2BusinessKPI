"""
Decisions pages — Recommended Actions + Past Decisions.
Consumes canonical DecisionPackage. Zero recomputation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import streamlit as st

from ui.components.design_system import (
    outcome_pill, badge, section_label, callout, action_row, empty_state,
    method_badge, conf_bar
)
from praxis.c1_data_foundation.entitlements import Persona
from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS


def _kpi_name(kpi_id: str) -> str:
    return KPI_CONTRACTS.get(kpi_id, {}).get("name", kpi_id.replace("_", " ").title())


# ────────────────────────────────────────────────────────────────────────────
# Recommended Actions
# ────────────────────────────────────────────────────────────────────────────

def render_recommended_actions(result, persona: str, on_approve: Optional[Callable] = None):
    """Render the Recommended Actions page from a PipelineResult."""

    if result is None or result.error:
        st.markdown(empty_state("No recommendation available", "Run a scenario first.", "→"),
                    unsafe_allow_html=True)
        return

    ep = result.evidence_package
    hp = result.hypothesis_package
    dp = result.decision_package

    if dp is None:
        st.markdown(empty_state("No decision package", "Pipeline did not produce a decision.", "→"),
                    unsafe_allow_html=True)
        return

    kpi_name = _kpi_name(ep.kpi_id if ep else "zone_gmv")
    outcome  = dp.source_decision_outcome

    st.markdown(f'<div class="prx-page-title">Recommended Actions — {kpi_name}</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="prx-page-sub">Period: {ep.period if ep else "—"} · Zone: {ep.grain_key if ep else "—"}</div>',
        unsafe_allow_html=True)

    # Outcome banner
    outcome_color = {
        "ANSWER": "#F0FDF4", "QUALIFY": "#FFFBEB",
        "CLARIFY": "#F5F3FF", "ABSTAIN": "#FEF2F2"
    }.get(outcome, "#F9FAFB")
    st.markdown(f"""
<div style="background:{outcome_color};border-radius:8px;padding:1rem 1.25rem;
     margin-bottom:1.25rem;display:flex;align-items:center;gap:1rem;">
  {outcome_pill(outcome)}
  <span style="font-size:.875rem;color:#374151;">
    {"Praxis has sufficient confidence. Specific action recommended." if outcome=="ANSWER" else
     "Qualified recommendation — review caveat before acting." if outcome=="QUALIFY" else
     "Additional data required before Praxis can recommend." if outcome=="CLARIFY" else
     "Insufficient evidence — Praxis will not recommend without adequate confidence."}
  </span>
</div>
""", unsafe_allow_html=True)

    if dp.caveat_text:
        st.markdown(callout(f"<b>Important caveat:</b> {dp.caveat_text}", "warn", "⚠"),
                    unsafe_allow_html=True)

    # Action card for each action
    for i, act in enumerate(dp.actions):
        lever_label  = act.controllable_lever.replace("_", " ").title()
        driver_label = act.driver.replace("_", " ").title()
        owner_label  = act.owner.replace("_", " ").title()

        conf_score = 0
        band = act.confidence
        if hp and hp.hypotheses:
            conf_score = hp.hypotheses[0].get("confidence_score", 0)
            band = hp.hypotheses[0].get("confidence_band", "MEDIUM")

        st.markdown(f"""
<div class="prx-action-card">
  <div class="prx-action-card-head">
    Action #{i+1} &nbsp;·&nbsp;
    <span style="color:#9CA3AF;font-size:.6875rem;">Decision authority verified by policy</span>
  </div>
  {action_row("Primary Driver", driver_label)}
  {action_row("Business Lever", lever_label, "purple")}
  {action_row("Recommended Action", act.action)}
  {action_row("Action Owner", owner_label)}
  {action_row("Decision Authority", "Cross-store scope — requires senior approval" if "zone" in act.owner else "Within-store scope — operations manager authority")}
  {action_row("Confidence", f"{band} · {conf_score:.0f}/100", "success" if conf_score >= 70 else "warn" if conf_score >= 40 else "")}
  {action_row("Expected Impact", act.expected_impact, "success")}
  {action_row("Monitoring Plan", act.monitoring_plan)}
</div>""", unsafe_allow_html=True)

    # Persona narrative — active persona shown by default, other in expander
    st.markdown(section_label("WHAT THIS MEANS FOR YOU"), unsafe_allow_html=True)

    active_narr = (
        dp.narrative_zone_business_head
        if persona == Persona.ZONE_BUSINESS_HEAD
        else dp.narrative_dark_store_ops_manager
    )
    other_narr = (
        dp.narrative_dark_store_ops_manager
        if persona == Persona.ZONE_BUSINESS_HEAD
        else dp.narrative_zone_business_head
    )
    other_label = (
        "Operations Manager perspective"
        if persona == Persona.ZONE_BUSINESS_HEAD
        else "Business Leader perspective"
    )

    if active_narr:
        st.markdown(f"""
<div class="prx-card">
  <div class="prx-narrative" style="margin:0;">{active_narr}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(callout(
            "Narrative not available — LLM may be offline. All quantitative conclusions remain valid.",
            "warn", "⚠"
        ), unsafe_allow_html=True)

    if other_narr:
        with st.expander(f"View {other_label}"):
            st.markdown(f'<div class="prx-narrative">{other_narr}</div>',
                        unsafe_allow_html=True)

    # Approve / reject
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        if st.button("✓ Approve & Record Decision", type="primary", key="rec_approve"):
            if on_approve:
                on_approve(result)
                st.rerun()
    with col2:
        if st.button("✗ Escalate for Review", key="rec_reject"):
            st.session_state.feedback_msg = ("warn", "Decision escalated. No memory record created.")

    fb = st.session_state.get("feedback_msg")
    if fb:
        with col3:
            cls, msg = fb
            html_cls = "prx-feedback-ok" if cls == "ok" else "prx-feedback-err"
            st.markdown(f'<div class="{html_cls}">{msg}</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# Past Decisions
# ────────────────────────────────────────────────────────────────────────────

def render_past_decisions(decisions: List[Dict]):
    """Render the Past Decisions timeline."""

    st.markdown('<div class="prx-page-title">Past Decisions</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">A record of every decision Praxis has supported. '
        'Outcomes are captured and fed back into the C5 governed memory.</div>',
        unsafe_allow_html=True
    )

    # Demo fixture decisions
    fixture_decisions = [
        {
            "dm_id": "DM-DEMO-001",
            "date": "15 Aug 2026",
            "kpi": "zone_gmv",
            "driver": "dark_store_stockout_rate",
            "action": "L2_cross_store_transfer",
            "confidence": "MEDIUM",
            "outcome": "₹3.2L recovered (91% of estimate)",
            "status": "Confirmed",
        },
    ]

    all_decisions = fixture_decisions + (decisions or [])

    if not all_decisions:
        st.markdown(empty_state(
            "No past decisions",
            "Approve a recommendation to create the first decision record.",
            "⊞"
        ), unsafe_allow_html=True)
        return

    # Table
    st.markdown("""
<div class="prx-table-wrap">
  <table class="prx-table">
    <thead>
      <tr>
        <th>Date</th>
        <th>KPI</th>
        <th>Driver</th>
        <th>Action Taken</th>
        <th>Confidence</th>
        <th>Observed Outcome</th>
        <th>Memory Status</th>
      </tr>
    </thead>
    <tbody>
""", unsafe_allow_html=True)

    rows_html = ""
    for d in all_decisions:
        kpi_n    = _kpi_name(d.get("kpi", "zone_gmv"))
        drv      = d.get("driver", "?").replace("_", " ").title()
        act      = d.get("action", "?").replace("_", " ").title()
        conf     = d.get("confidence", "?")
        outcome  = d.get("outcome", "Pending")
        status   = d.get("status", "Pending")
        cls      = "ok" if status == "Confirmed" else "warn" if status == "Pending" else "crit"
        fixture  = " · demo fixture" if "DEMO" in d.get("dm_id","") else ""

        rows_html += f"""
<tr>
  <td><span class="mono">{d.get('date','—')}</span></td>
  <td>{kpi_n}</td>
  <td>{drv}</td>
  <td>{act}</td>
  <td class="{cls}">{conf}</td>
  <td>{outcome}</td>
  <td><span class="prx-mem-status-badge {"confirmed" if status=="Confirmed" else "pending"}">{status}{fixture}</span></td>
</tr>"""

    st.markdown(rows_html + "</tbody></table></div>", unsafe_allow_html=True)

    # Outcome feedback
    st.markdown(section_label("RECORD WHAT HAPPENED"), unsafe_allow_html=True)
    st.markdown(callout(
        "Recording an outcome closes the learning loop. "
        "<b>Confirmed outcomes</b> strengthen Praxis confidence in future similar situations. "
        "<b>Rejected outcomes</b> reduce confidence and flag the prior reasoning for review.",
        kind="info", icon="ℹ"
    ), unsafe_allow_html=True)

    dm_id = st.session_state.get("last_admitted_dm_id", "")
    if not dm_id and all_decisions:
        dm_id = all_decisions[-1].get("dm_id", "")

    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        observed = st.text_input("Observed outcome", value="₹3.2L recovered via DS043→DS041 transfer",
                                 key="outcome_text")
    with col2:
        outcome_type = st.radio("Outcome type", ["Hypothesis confirmed", "Hypothesis rejected"],
                                horizontal=True, key="outcome_radio")
    with col3:
        st.write("")
        if st.button("Submit Outcome Feedback", type="primary", key="submit_outcome"):
            import ui.streamlit_app as app
            matches = outcome_type == "Hypothesis confirmed"
            app._submit_feedback(matches, dm_id, observed)
            st.rerun()


# ────────────────────────────────────────────────────────────────────────────
# Render helper used by main app
# ────────────────────────────────────────────────────────────────────────────

def render_decisions(result, persona: str):
    """Default decisions view (forwards to recommended actions)."""
    render_recommended_actions(result=result, persona=persona)
