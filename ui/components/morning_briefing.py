"""
Morning Briefing page — the HOME screen.
Priority queue of KPI movements with materiality ranks.
Consumes run_all_kpis() output from pipeline.py (deterministic).

Language policy: NO technical jargon on this screen.
UX redesign: inline [Investigate →] button per material KPI row.
The old bottom investigation banner has been removed (redundant).
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

import streamlit as st

from ui.components.design_system import (
    badge, freshness_dot, section_label, empty_state
)

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
_DELTA_SIGN = {True: ("neg", "↓"), False: ("pos", "↑"), None: ("zero", "—")}


def render_morning_briefing(
    alert_queue: List[Dict],
    pipeline_result=None,
    on_investigate: Optional[Callable] = None,
    on_run_scenario: Optional[Callable] = None,
):
    """Full Morning Briefing page."""

    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown('<div class="prx-page-title">Good morning.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Here\'s what needs your attention today '
        '— Mon, 1 Sep 2026 · 09:15 IST.</div>',
        unsafe_allow_html=True,
    )

    # ── Summary scan bar ──────────────────────────────────────────────────────
    n_total    = len(alert_queue)
    n_material = sum(1 for k in alert_queue if k.get("status") == "MATERIAL")
    n_action   = sum(1 for k in alert_queue
                     if k.get("status") == "MATERIAL" and k.get("severity", 0) >= 4)

    brief_text = (
        f"{n_material} business movement{'s' if n_material != 1 else ''} require attention "
        f"— {n_total - n_material} KPI{'s are' if (n_total - n_material) != 1 else ' is'} on track."
        if n_material > 0
        else f"All {n_total} KPIs are within normal range. No action required."
    )
    mat_color = "var(--red-600)"   if n_material > 0 else "var(--green-600)"
    act_color = "var(--amber-600)" if n_action   > 0 else "var(--green-600)"

    st.markdown(f"""
<div class="prx-scan-bar">
  <div>
    <div class="prx-scan-label">Today's Decision Brief</div>
    <div class="prx-scan-meta">{brief_text}</div>
  </div>
  <div class="prx-scan-stat-wrap">
    <div class="prx-scan-stat">
      <div class="prx-scan-stat-num" style="color:var(--purple-800)">{n_total}</div>
      <div class="prx-scan-stat-label" style="color:var(--purple-700)">KPIs monitored</div>
    </div>
    <div class="prx-scan-stat">
      <div class="prx-scan-stat-num" style="color:{mat_color}">{n_material}</div>
      <div class="prx-scan-stat-label" style="color:{mat_color}">Material movements</div>
    </div>
    <div class="prx-scan-stat">
      <div class="prx-scan-stat-num" style="color:{act_color}">{n_action}</div>
      <div class="prx-scan-stat-label" style="color:{act_color}">Require action</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── KPI priority queue ────────────────────────────────────────────────────
    st.markdown(section_label("KPI PRIORITY QUEUE — Zone Z003 · Week 33"),
                unsafe_allow_html=True)

    if not alert_queue:
        st.markdown(empty_state("No KPI data", "Run the morning pipeline.", "◉"),
                    unsafe_allow_html=True)
        return

    # Wrap the whole queue in a card container
    st.markdown('<div class="prx-card" style="padding:0;overflow:hidden;">', unsafe_allow_html=True)

    for i, kpi in enumerate(alert_queue, 1):
        status      = kpi.get("status", "NON_MATERIAL")
        bdg_cls, bdg_txt = _STATUS_BADGE.get(status, ("muted", status))
        icon        = _STATUS_ICON.get(status, "⚪")
        is_material = (status == "MATERIAL")

        delta_pct = kpi.get("delta_pct")
        if delta_pct is not None:
            is_neg = delta_pct < 0
            color  = "#DC2626" if is_neg else "#059669"
            arrow  = "↓" if is_neg else "↑"
            delta_str = f'<span style="font-size:.875rem;font-weight:700;color:{color};">{arrow} {abs(delta_pct):.1f}%</span>'
        else:
            delta_str = '<span style="color:#9CA3AF;">—</span>'

        fresh_html = freshness_dot(
            kpi.get("freshness", "Fresh").lower(),
            kpi.get("freshness_ago", "")
        )

        left_border = "border-left:3px solid #DC2626;" if is_material else \
                      "border-left:3px solid #059669;" if status == "NON_MATERIAL" else \
                      "border-left:3px solid #E5E7EB;"

        row_html = f"""
<div style="display:flex;align-items:center;gap:1rem;
     padding:.9375rem 1.375rem 0 1.375rem;
     border-bottom:1px solid var(--border-soft);{left_border}">
  <div style="font-size:.625rem;font-weight:700;color:#9CA3AF;
       width:1.25rem;text-align:center;flex-shrink:0;">{i}</div>
  <div style="font-size:1rem;flex-shrink:0;">{icon}</div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:.9rem;font-weight:600;color:#111827;
         letter-spacing:-.01em;">{kpi['kpi_name']}</div>
    <div style="font-size:.625rem;color:#9CA3AF;margin-top:.125rem;">
      {kpi.get('source','—')}</div>
  </div>
  <div style="text-align:right;flex-shrink:0;width:5.5rem;">
    <div style="font-size:1rem;font-weight:700;color:#111827;
         letter-spacing:-.02em;font-family:'Plus Jakarta Sans','Inter',sans-serif;">
      {kpi.get('actual_display','—')}</div>
    <div style="font-size:.5625rem;color:#9CA3AF;">vs expected</div>
  </div>
  <div style="width:4.5rem;text-align:right;flex-shrink:0;">{delta_str}</div>
  <div style="width:6rem;flex-shrink:0;">{fresh_html}</div>
  <div style="width:8rem;flex-shrink:0;">{badge(bdg_txt, bdg_cls)}</div>
</div>"""
        st.markdown(row_html, unsafe_allow_html=True)

        # ── Inline Investigate button — only for material KPIs ────────────────
        if is_material:
            _, btn_col, _ = st.columns([0.05, 0.22, 0.73])
            with btn_col:
                if st.button(
                    "⌕  Investigate →",
                    key=f"inv_{i}_{kpi.get('kpi_id', i)}",
                    type="primary",
                    use_container_width=True,
                ):
                    # Auto-run S1 if no active result, then navigate
                    if st.session_state.get("pipeline_result") is None:
                        from praxis.orchestration.pipeline import run_pipeline
                        from praxis.synthetic.generator import get_scenario
                        with st.spinner("Running analysis…"):
                            r = run_pipeline(
                                scenario=get_scenario("s1"),
                                persona=st.session_state.persona,
                            )
                            st.session_state.pipeline_result = r
                            st.session_state.scenario_name   = "s1"
                    st.session_state.page = "Active Investigation"
                    st.rerun()
        else:
            # Spacing for non-material rows
            st.markdown('<div style="padding-bottom:.25rem;"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Organisational memory insight strip ───────────────────────────────────
    _render_learning_insight()


def _render_learning_insight():
    """Compact strip showing memory status — introduces the learning loop."""
    memory_count = 0
    try:
        from praxis.c5_memory.gateway import _get_conn
        conn   = _get_conn()
        result = conn.execute(
            "SELECT COUNT(*) FROM outcome_memory WHERE outcome_matches_hypothesis = TRUE"
        ).fetchone()
        if result:
            memory_count = result[0]
        conn.close()
    except Exception:
        pass

    session_count = len(st.session_state.get("past_decisions", []))
    total = memory_count + session_count

    if total > 0:
        mem_pts       = min(12 + 6 * (total - 1), 25)
        insight_text  = (
            f"Praxis has <b>{total}</b> validated decision record"
            f"{'s' if total != 1 else ''} in organisational memory. "
            f"The next matching investigation will receive a <b>+{mem_pts} pt confidence boost</b> — "
            f"automatically, without any user action."
        )
    else:
        insight_text = (
            "No validated decisions yet. Run a Signature Demo, approve the recommendation, "
            "then confirm the outcome to begin building organisational memory."
        )

    st.markdown(f"""
<div style="background:#F5F3FF;border:1px solid #E9D5FF;border-radius:10px;
     padding:1rem 1.375rem;margin-top:1.5rem;
     display:flex;align-items:center;gap:.875rem;">
  <span style="font-size:1.5rem;flex-shrink:0;
       filter:drop-shadow(0 0 6px rgba(124,58,237,.35));">⊗</span>
  <div>
    <div style="font-size:.8125rem;font-weight:700;color:#5B21B6;
         margin-bottom:.25rem;">Praxis Learning Loop</div>
    <div style="font-size:.75rem;color:#7C3AED;line-height:1.6;">{insight_text}</div>
  </div>
</div>
""", unsafe_allow_html=True)
