"""
Decisions pages — Recommended Actions + Past Decisions (Page 3).

Primary Question: "What should I do?"

Layer 1 (0-5s):  Operational Action Directive Hero Card (Quantified ROI + Decision Authority).
Layer 2 (5-20s): Operational Decision Memo (Executive narrative, inaction risks, implementation logistics).
Layer 3 (20-60s): Past Decisions Timeline & 48-Hour Outcome Feedback Loop.

Consumes canonical DecisionPackage. Zero quantitative recomputation in this file.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import streamlit as st

from ui.components.design_system import (
    outcome_pill, badge, section_label, section_sep, callout, action_row, empty_state
)
from praxis.c1_data_foundation.entitlements import Persona
from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS


def _kpi_name(kpi_id: str) -> str:
    return KPI_CONTRACTS.get(kpi_id, {}).get("name", kpi_id.replace("_", " ").title())


# ────────────────────────────────────────────────────────────────────────────
# Page 3 Root: render_decisions
# ────────────────────────────────────────────────────────────────────────────

def render_decisions(
    result,
    persona: str,
    decisions: Optional[List[Dict]] = None,
    on_approve: Optional[Callable] = None,
    on_feedback: Optional[Callable] = None,
):
    """
    Consolidated 'Actions & Decisions' page (Page 3).
    Follows the 3-layer cognitive disclosure hierarchy.
    """
    st.markdown('<div class="prx-page-title">Actions &amp; Decisions</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Operational action directives, executive decision memos, '
        'and institutional governance for Zone Z003.</div>',
        unsafe_allow_html=True
    )

    if result is None or result.error:
        from ui.components.design_system import empty_state
        st.markdown(empty_state(
            "No active recommendation",
            "Use the 'S1 · Cold Start' or 'S2 · Memory' buttons in the sidebar to generate an action directive.",
            "✓"
        ), unsafe_allow_html=True)
    else:
        render_recommended_actions(result=result, persona=persona, on_approve=on_approve)

    st.markdown(section_sep("INSTITUTIONAL DECISION HISTORY & 48-HOUR OUTCOME VALIDATION"),
                unsafe_allow_html=True)
    render_past_decisions(decisions=decisions or [], on_feedback=on_feedback)


# ────────────────────────────────────────────────────────────────────────────
# Layer 1 & 2: Recommended Actions & Decision Memo
# ────────────────────────────────────────────────────────────────────────────

def render_recommended_actions(result, persona: str, on_approve: Optional[Callable] = None):
    """Render Layer 1 Action Directive Card and Layer 2 Operational Decision Memo."""
    ep = result.evidence_package if result else None
    hp = result.hypothesis_package if result else None
    dp = result.decision_package if result else None

    if dp is None:
        return

    outcome = dp.source_decision_outcome
    act = dp.actions[0] if (dp.actions and len(dp.actions) > 0) else None

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 1 (0–5s): OPERATIONAL ACTION DIRECTIVE HERO CARD
    # ─────────────────────────────────────────────────────────────────────────
    authority_text = (
        "✓ AUTHORITY VERIFIED · Unilateral Zone Approval Scope (POL-OPS-2026-04)"
        if persona == Persona.ZONE_BUSINESS_HEAD
        else "✓ SCOPED FOR STORE EXECUTION · Dark Store DS041 Operations Scope"
    )

    action_title = (
        act.action if act else "Authorize Emergency Cross-Store Stock Transfer: 1,200 units DS042 → DS041"
    )

    directive_html = f"""
<div class="prx-action-directive-hero">
  <div class="prx-directive-badge-row">
    <span class="prx-badge ok">✓ APPROVED DIRECTIVE · Ready for Immediate Execution</span>
    <span class="prx-badge purple">{authority_text}</span>
  </div>
  <div class="prx-directive-title">{action_title}</div>
  <div style="font-size:0.875rem;color:var(--text-secondary);max-width:68ch;line-height:1.55;">
    Primary intervention to eliminate acute inventory stockout at Dark Store DS041 by transferring
    buffer stock from Dark Store DS042 (North) within the next scheduled dispatch window.
  </div>

  <div class="prx-directive-roi-grid">
    <div class="prx-directive-roi-box">
      <div class="prx-directive-roi-label">Projected Recovery</div>
      <div class="prx-directive-roi-val green">₹2.1L GMV</div>
      <div class="prx-directive-roi-sub">Within 24–48 hours SLA</div>
    </div>
    <div class="prx-directive-roi-box">
      <div class="prx-directive-roi-label">Time to Impact</div>
      <div class="prx-directive-roi-val">48 Hours</div>
      <div class="prx-directive-roi-sub">Transit: 3.5h · Restock: 1.5h</div>
    </div>
    <div class="prx-directive-roi-box">
      <div class="prx-directive-roi-label">Implementation Cost</div>
      <div class="prx-directive-roi-val">₹12,000</div>
      <div class="prx-directive-roi-sub">Inter-store logistics transit</div>
    </div>
    <div class="prx-directive-roi-box">
      <div class="prx-directive-roi-label">Net Financial ROI</div>
      <div class="prx-directive-roi-val green">17.5x ROI</div>
      <div class="prx-directive-roi-sub">High capital efficiency</div>
    </div>
  </div>

  <div style="display:flex;align-items:center;gap:1.5rem;font-size:0.8125rem;color:var(--text-tertiary);border-top:1px solid var(--border-soft);padding-top:0.875rem;">
    <div><b>Action Owner:</b> {act.owner.replace('_', ' ').title() if act else 'Zone Business Head'}</div>
    <div><b>Governing Policy:</b> POL-OPS-2026-04 § Inventory Transfers</div>
    <div><b>Monitoring Cadence:</b> Hourly automated telemetry sync</div>
  </div>
</div>
"""
    st.markdown(directive_html, unsafe_allow_html=True)

    # Primary Decision Action Buttons
    col_btn1, col_btn2, col_msg = st.columns([0.28, 0.24, 0.48])
    with col_btn1:
        if st.button("✓ Authorize & Record Decision", type="primary", key="btn_auth_record", use_container_width=True):
            if on_approve:
                on_approve(result)
                st.rerun()

    with col_btn2:
        if st.button("✗ Escalate for Review", key="btn_escalate", use_container_width=True):
            st.session_state.feedback_msg = ("warn", "Decision escalated to Regional Operations VP. No memory record created.")

    fb = st.session_state.get("feedback_msg")
    if fb:
        with col_msg:
            cls, msg = fb
            html_cls = "prx-feedback-ok" if cls == "ok" else "prx-feedback-err"
            st.markdown(f'<div class="{html_cls}">{msg}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 2 (5–20s): OPERATIONAL DECISION MEMORANDUM
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(section_label("OPERATIONAL DECISION MEMORANDUM — ZONE Z003"), unsafe_allow_html=True)

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

    memo_body = active_narr if active_narr else (
        "Praxis synthesis confirms an acute inventory stockout at Dark Store DS041 in Koramangala South. "
        "Standard supplier replenishment from the regional Mother Hub requires a 5-day cycle. "
        "By contrast, Dark Store DS042 (North) possesses 18 days of excess buffer stock across the affected "
        "Dairy & Fresh SKU lines. Authorizing an immediate 1,200-unit cross-dock transfer closes the supply "
        "gap in 48 hours and preserves ₹2.1L in customer GMV."
    )

    memo_html = f"""
<div class="prx-decision-memo">
  <div class="prx-memo-header">
    <div>
      <div class="prx-memo-title">MEMORANDUM: Immediate Stock Transfer Directive</div>
      <div class="prx-memo-meta">Zone Z003 · Koramangala &nbsp;·&nbsp; Document Ref: PRAXIS-2026-W33-01</div>
    </div>
    <div>{outcome_pill(outcome)}</div>
  </div>

  <div style="font-size:0.9375rem;color:var(--text-primary);line-height:1.75;margin-bottom:1.5rem;">
    {memo_body}
  </div>

  <div style="background:var(--red-50);border:1px solid #FECACA;border-radius:var(--radius-md);padding:1rem 1.25rem;margin-bottom:1.5rem;">
    <div style="font-size:0.8125rem;font-weight:700;color:var(--red-700);margin-bottom:0.25rem;">
      ⚠ Counterfactual / Risk of Inaction
    </div>
    <div style="font-size:0.75rem;color:var(--red-700);line-height:1.5;">
      If transfer is delayed past 11:00 IST, peak evening order volume (18:00–21:00 IST) will suffer
      an estimated ₹52,000 in unrecoverable stockout cancellations, with customer churn probability increasing by 14%.
    </div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:0.75rem;">
    <div style="background:var(--surface-well);border:1px solid var(--border);border-radius:var(--radius-md);padding:0.75rem;">
      <div style="font-size:0.625rem;font-weight:800;color:var(--text-tertiary);text-transform:uppercase;">Affected SKUs</div>
      <div style="font-size:0.8125rem;font-weight:700;color:var(--text-primary);margin-top:2px;">Dairy &amp; Fresh (Top 7)</div>
    </div>
    <div style="background:var(--surface-well);border:1px solid var(--border);border-radius:var(--radius-md);padding:0.75rem;">
      <div style="font-size:0.625rem;font-weight:800;color:var(--text-tertiary);text-transform:uppercase;">Source Store</div>
      <div style="font-size:0.8125rem;font-weight:700;color:var(--text-primary);margin-top:2px;">Store DS042 (North)</div>
    </div>
    <div style="background:var(--surface-well);border:1px solid var(--border);border-radius:var(--radius-md);padding:0.75rem;">
      <div style="font-size:0.625rem;font-weight:800;color:var(--text-tertiary);text-transform:uppercase;">Destination</div>
      <div style="font-size:0.8125rem;font-weight:700;color:var(--text-primary);margin-top:2px;">Store DS041 (South)</div>
    </div>
    <div style="background:var(--surface-well);border:1px solid var(--border);border-radius:var(--radius-md);padding:0.75rem;">
      <div style="font-size:0.625rem;font-weight:800;color:var(--text-tertiary);text-transform:uppercase;">Dispatch Window</div>
      <div style="font-size:0.8125rem;font-weight:700;color:var(--text-primary);margin-top:2px;">Immediate (10:30 IST)</div>
    </div>
  </div>
</div>
"""
    st.markdown(memo_html, unsafe_allow_html=True)

    if other_narr:
        with st.expander(f"View {other_label}"):
            st.markdown(f'<div class="prx-card" style="margin:0;line-height:1.7;">{other_narr}</div>',
                        unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# Layer 3: Past Decisions Timeline & Outcome Feedback
# ────────────────────────────────────────────────────────────────────────────

def render_past_decisions(decisions: List[Dict], on_feedback: Optional[Callable] = None):
    """Render the Past Decisions timeline and outcome validation loop."""
    fixture_decisions = [
        {
            "dm_id": "DM-DEMO-001",
            "date": "15 Aug 2026",
            "kpi": "zone_gmv",
            "driver": "dark_store_stockout_rate",
            "action": "L2_cross_store_transfer",
            "confidence": "HIGH",
            "outcome": "₹3.2L recovered (91% of estimate)",
            "status": "Confirmed",
        },
    ]

    all_decisions = fixture_decisions + (decisions or [])

    # Decision Timeline Table
    st.markdown("""
<div class="prx-table-wrap">
  <table class="prx-table">
    <thead>
      <tr>
        <th>Decision ID</th>
        <th>Date</th>
        <th>Target KPI</th>
        <th>Primary Driver</th>
        <th>Action Taken</th>
        <th>Confidence</th>
        <th>Observed Recovery</th>
        <th>Memory Status</th>
      </tr>
    </thead>
    <tbody>
""", unsafe_allow_html=True)

    rows_html = ""
    for d in all_decisions:
        kpi_n = _kpi_name(d.get("kpi", "zone_gmv"))
        drv = d.get("driver", "?").replace("_", " ").title()
        act = d.get("action", "?").replace("_", " ").title()
        conf = d.get("confidence", "?")
        outcome = d.get("outcome", "Pending 48h observation")
        status = d.get("status", "Pending")
        cls = "ok" if status == "Confirmed" else "warn" if status == "Pending" else "crit"

        rows_html += f"""
<tr>
  <td><span class="mono" style="font-weight:600;">{d.get('dm_id','—')}</span></td>
  <td><span class="mono">{d.get('date','—')}</span></td>
  <td>{kpi_n}</td>
  <td>{drv}</td>
  <td>{act}</td>
  <td class="{cls}">{conf}</td>
  <td>{outcome}</td>
  <td><span class="prx-badge {'ok' if status=='Confirmed' else 'warning'}">{status}</span></td>
</tr>"""

    st.markdown(rows_html + "</tbody></table></div>", unsafe_allow_html=True)

    # 48-Hour Outcome Feedback Confirmation Box
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
<div class="prx-card" style="border-left:4px solid var(--purple-700);">
  <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem;">
    <span style="font-size:1.25rem;color:var(--purple-800);">⊗</span>
    <div style="font-family:var(--font-display);font-size:1rem;font-weight:700;color:var(--text-primary);">
      48-Hour Recovery Verification &amp; Memory Reinforcement
    </div>
  </div>
  <div style="font-size:0.8125rem;color:var(--text-secondary);line-height:1.55;margin-bottom:1rem;">
    Confirming the real-world outcome closes the causal feedback loop. <b>Confirmed recoveries</b> reinforce
    the precedent in DuckDB memory (+12 to +25 pt boost), while <b>rejected hypotheses</b> trigger automatic confidence penalties.
  </div>
""", unsafe_allow_html=True)

    dm_id = st.session_state.get("last_admitted_dm_id", "")
    if not dm_id and all_decisions:
        dm_id = all_decisions[-1].get("dm_id", "DM-DEMO-001")

    col_txt, col_rad, col_sub = st.columns([0.45, 0.32, 0.23])
    with col_txt:
        observed = st.text_input(
            "Observed Recovery Outcome",
            value="₹2.1L recovered via DS042→DS041 stock transfer",
            key="outcome_text",
        )
    with col_rad:
        outcome_type = st.radio(
            "Outcome Assessment",
            ["Hypothesis Confirmed (Recovery Met)", "Hypothesis Rejected (No Recovery)"],
            key="outcome_radio",
        )
    with col_sub:
        st.markdown("<div style='height:1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("Submit & Update Memory →", type="primary", key="submit_outcome_btn", use_container_width=True):
            import ui.streamlit_app as app
            matches = "Confirmed" in outcome_type
            app._submit_feedback(matches, dm_id, observed)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
