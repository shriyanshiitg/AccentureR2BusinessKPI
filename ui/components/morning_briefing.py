"""
Morning Briefing page — the HOME screen.
Priority queue of KPI movements with materiality ranks.
Consumes run_all_kpis() output from pipeline.py (deterministic).

Language policy: NO technical jargon on this screen (no z-score, STL, C2 Operator etc).
All language must be business-readable.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import streamlit as st

from ui.components.design_system import (
    badge, freshness_dot, outcome_pill, section_label, callout, empty_state
)


# ── Materiality status → badge mapping ───────────────────────────
_STATUS_BADGE = {
    "MATERIAL":     ("critical", "Requires Attention"),
    "NON_MATERIAL": ("muted",    "On Track"),
    "MONTHLY":      ("pending",  "Monthly KPI"),
    "STALE":        ("warning",  "Stale Data"),
    "MISSING":      ("warning",  "Data Unavailable"),
}

_STATUS_ICON = {
    "MATERIAL":     "🔴",
    "NON_MATERIAL": "🟢",
    "MONTHLY":      "⚪",
    "STALE":        "🟡",
    "MISSING":      "⚪",
}

_DELTA_SIGN = {
    True:  ("neg", "↓"),
    False: ("pos", "↑"),
    None:  ("zero", "—"),
}


def render_morning_briefing(
    alert_queue: List[Dict],
    pipeline_result=None,
    on_investigate: Optional[Callable] = None,
    on_run_scenario: Optional[Callable] = None,
):
    """Full Morning Briefing page."""


    # ── Page header ──────────────────────────────────────────────────────────
    now_str = "Mon, 1 Sep 2026 · 09:15 IST"
    st.markdown(f'<div class="prx-page-title">Good morning.</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="prx-page-sub">Here\'s what needs your attention today — {now_str}.</div>',
        unsafe_allow_html=True,
    )

    # ── Decision brief summary bar ─────────────────────────────────────────
    n_total    = len(alert_queue)
    n_material = sum(1 for k in alert_queue if k.get("status") == "MATERIAL")
    n_action   = sum(1 for k in alert_queue
                     if k.get("status") == "MATERIAL" and k.get("severity", 0) >= 4)
    if n_material > 0:
        brief_text = (f"{n_material} business movement{'s' if n_material != 1 else ''} require "
                      f"attention — {n_total - n_material} KPI{'s are' if (n_total - n_material) != 1 else ' is'} on track.")
    else:
        brief_text = f"All {n_total} KPIs are within normal range. No action required."

    st.markdown(f"""
<div class="prx-scan-bar">
  <div>
    <div class="prx-scan-label">Today's Decision Brief</div>
    <div class="prx-scan-meta">{brief_text}</div>
  </div>
  <div style="display:flex;gap:1.5rem;flex-shrink:0;">
    <div style="text-align:center;">
      <div style="font-size:1.5rem;font-weight:700;color:#5B21B6;">{n_total}</div>
      <div style="font-size:.625rem;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:.05em;">KPIs monitored</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:1.5rem;font-weight:700;color:#DC2626;">{n_material}</div>
      <div style="font-size:.625rem;font-weight:700;color:#B91C1C;text-transform:uppercase;letter-spacing:.05em;">Material movements</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:1.5rem;font-weight:700;color:#D97706;">{n_action}</div>
      <div style="font-size:.625rem;font-weight:700;color:#B45309;text-transform:uppercase;letter-spacing:.05em;">Require action</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Priority queue ──────────────────────────────────────────────────
    st.markdown(section_label("KPI PRIORITY QUEUE — Zone Z003 · Week 33"), unsafe_allow_html=True)

    # Table header — no statistical signal column
    st.markdown("""
<div class="prx-queue-wrap">
  <div class="prx-queue-header">
    <span></span>
    <span></span>
    <span>KPI</span>
    <span>Actual vs Expected</span>
    <span>Movement</span>
    <span>Data Freshness</span>
    <span>Priority</span>
    <span>Next Step</span>
  </div>
""", unsafe_allow_html=True)

    # Queue rows — no z-score column, no method meta
    rows_html = ""
    for i, kpi in enumerate(alert_queue, 1):
        status = kpi.get("status", "NON_MATERIAL")
        bdg_cls, bdg_txt = _STATUS_BADGE.get(status, ("muted", status))
        icon = _STATUS_ICON.get(status, "⚪")

        delta_pct = kpi.get("delta_pct")
        if delta_pct is not None:
            is_neg = delta_pct < 0
            cls, arrow = _DELTA_SIGN[is_neg]
            delta_html = f'<div class="prx-queue-delta {cls}">{arrow} {abs(delta_pct):.1f}%</div>'
        else:
            delta_html = '<div class="prx-queue-delta zero">—</div>'

        fresh = kpi.get("freshness", "Fresh").lower()
        fresh_html = freshness_dot(fresh, kpi.get("freshness_ago", ""))

        outcome_label = kpi.get("outcome_label", "Monitor")
        outcome_style = (
            "color:#DC2626;font-weight:700;" if status == "MATERIAL" else
            "color:#6B7280;"
        )

        rows_html += f"""
<div class="prx-queue-row">
  <div class="prx-queue-priority">{i}</div>
  <div class="prx-queue-icon">{icon}</div>
  <div>
    <div class="prx-queue-name">{kpi['kpi_name']}</div>
    <div class="prx-queue-meta">{kpi.get('source','—')}</div>
  </div>
  <div class="prx-queue-values">
    <div class="prx-queue-actual">{kpi.get('actual_display','—')}</div>
    <div class="prx-queue-vs">vs expected</div>
  </div>
  {delta_html}
  <div>{fresh_html}</div>
  <div>{badge(bdg_txt, bdg_cls)}</div>
  <div style="font-size:.75rem;{outcome_style}">{outcome_label}</div>
</div>"""

    st.markdown(rows_html + "</div>", unsafe_allow_html=True)

    # ── Priority investigation banner ─────────────────────────────────────
    top = alert_queue[0] if alert_queue else None
    if top and top.get("status") == "MATERIAL":
        _render_top_investigation_banner(top, on_investigate)

    # ── Learning insight ────────────────────────────────────────────────
    _render_learning_insight()


def _render_top_investigation_banner(kpi: Dict, on_investigate: Optional[Callable]):
    """Show the most urgent KPI with a one-click investigate CTA."""
    st.markdown(section_label("PRIORITY INVESTIGATION"), unsafe_allow_html=True)

    delta_pct = kpi.get("delta_pct", 0) or 0
    delta_dir = "below" if delta_pct < 0 else "above"

    st.markdown(f"""
<div class="prx-inv-panel">
  <div class="prx-inv-panel-head">
    <div class="prx-inv-panel-title">
      🔴&nbsp; {kpi['kpi_name']} · Material Movement
    </div>
    <span class="prx-badge critical">Requires Action</span>
  </div>
  <div class="prx-inv-panel-body">
    <div style="margin-bottom:1rem;">
      <div style="font-size:.75rem;color:#6B7280;margin-bottom:.25rem;">WHAT CHANGED</div>
      <div style="font-size:1.125rem;font-weight:600;color:#0F1117;">
        {kpi['kpi_name']} is <span style="color:#DC2626;">{abs(delta_pct):.0f}% {delta_dir} expected performance</span>
        — movement is outside normal range for this KPI.
      </div>
      <div style="font-size:.8125rem;color:#6B7280;margin-top:.375rem;">
        Current: <b>{kpi.get('actual_display','—')}</b> &nbsp;·&nbsp;
        Freshness: {freshness_dot(kpi.get('freshness','Fresh').lower(), kpi.get('freshness_ago',''))}
        &nbsp;·&nbsp; Source: {kpi.get('source','—')}
      </div>
    </div>
    <div style="display:flex;gap:2rem;padding:0.875rem;background:#F9FAFB;border-radius:6px;margin-bottom:1rem;font-size:.8125rem;color:#374151;">
      <div><div style="font-size:.5625rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.1875rem;">Analysis</div><div>Quantitative pattern analysis — fully automated</div></div>
      <div><div style="font-size:.5625rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.1875rem;">Driver Analysis</div><div>Root cause identified — investigate for details</div></div>
      <div><div style="font-size:.5625rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.1875rem;">Recommended Action</div><div>Cross-store inventory reallocation</div></div>
    </div>
    <div style="font-size:.75rem;color:#6B7280;font-style:italic;">
      Click <b>Investigate</b> to open the full analysis with evidence, confidence assessment, and recommended action.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 5])
    with col1:
        if st.button("⌭  Investigate →", type="primary", key="mb_investigate", use_container_width=True):
            if on_investigate:
                on_investigate()
    with col2:
        if st.button("▶  Run Signature Demo (S1)", key="mb_run_demo", use_container_width=True):
            from praxis.orchestration.pipeline import run_pipeline
            from praxis.synthetic.generator import get_scenario
            scenario = get_scenario("s1")
            with st.spinner("Running analysis…"):
                result = run_pipeline(scenario=scenario, persona=st.session_state.persona)
                st.session_state.pipeline_result = result
                st.session_state.scenario_name = "s1"
            st.session_state.page = "Active Investigations"
            st.rerun()


def _render_learning_insight():
    """Compact learning/memory insight — introduces the closed-loop differentiator."""
    memory_count = 0
    try:
        from praxis.c5_memory.gateway import _get_conn
        conn = _get_conn()
        result = conn.execute(
            "SELECT COUNT(*) FROM outcome_memory WHERE outcome_matches_hypothesis = TRUE"
        ).fetchone()
        if result:
            memory_count = result[0]
    except Exception:
        pass

    session_count = len(st.session_state.get("past_decisions", []))
    total = memory_count + session_count

    if total > 0:
        insight_text = (f"Praxis has <b>{total}</b> validated decision record"
                        f"{'s' if total != 1 else ''} from similar situations — "
                        "these will inform today's recommendations.")
    else:
        insight_text = ("No validated decisions yet. Approve and confirm the outcome of your "
                        "first investigation to begin building organisational memory.")

    st.markdown(f"""
<div style="background:#F5F3FF;border:1px solid #E9D5FF;border-radius:8px;
     padding:.875rem 1.25rem;margin-top:1.25rem;
     display:flex;align-items:center;gap:.875rem;">
  <span style="font-size:1.375rem;flex-shrink:0;">⊗</span>
  <div>
    <div style="font-size:.8125rem;font-weight:600;color:#5B21B6;margin-bottom:.1875rem;">Organisational Experience</div>
    <div style="font-size:.75rem;color:#7C3AED;line-height:1.5;">{insight_text}</div>
  </div>
</div>
""", unsafe_allow_html=True)
