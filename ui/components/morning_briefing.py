"""
Morning Briefing — Executive Decision Briefing (Page 1).

Primary Question: "What needs my attention right now?"

Layer 1 (0-5s):  Urgent Operational Incident Hero Card (dominates the page).
Layer 2 (5-15s): Stable Operations & Continuous Monitoring Grid (calm 2-column chips).
Layer 3 (15-30s): Compounding Organizational Memory Reassurance Banner.

Zero quantitative recomputation in this file. Consumes canonical pipeline outputs.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional
import streamlit as st

from ui.components.design_system import (
    badge, freshness_dot, section_label, empty_state
)
from praxis.c1_data_foundation.entitlements import Persona
from praxis.synthetic.generator import get_scenario
from praxis.orchestration.pipeline import run_pipeline


def render_morning_briefing(
    alert_queue: List[Dict],
    pipeline_result=None,
    on_investigate: Optional[Callable] = None,
    on_run_scenario: Optional[Callable] = None,
):
    """Full Executive Morning Briefing page."""
    persona = st.session_state.get("persona", Persona.ZONE_BUSINESS_HEAD)
    is_ops_manager = (persona == Persona.DARK_STORE_OPS_MANAGER)

    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown('<div class="prx-page-title">Good morning.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Mon, 1 Sep 2026 · 09:15 IST — Zone Z003 (Koramangala) '
        'Executive Operations Briefing.</div>',
        unsafe_allow_html=True,
    )

    if not alert_queue:
        st.markdown(empty_state("No KPI data available", "Run the morning pipeline to monitor KPIs.", "◉"),
                    unsafe_allow_html=True)
        return

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 1 (0–5s): PRIMARY OPERATIONAL INCIDENT HERO CARD
    # ─────────────────────────────────────────────────────────────────────────
    if is_ops_manager:
        incident_badge = "🔴 ACTION REQUIRED · Store DS041 Incident"
        incident_title = "Stockout Rate at DS041 spiked to 42.0% (+38.0pp Gap)"
        incident_cause = (
            "Root cause identified: <b>Acute replenishment delay</b> for Dairy & Fresh "
            "produce lines at Dark Store DS041 (Koramangala South)."
        )
        stat1_label, stat1_val, stat1_sub = "ACTUAL VS BASELINE", "42.0% vs 4.0%", "Baseline: 4.0% normal"
        stat2_label, stat2_val, stat2_sub = "MATERIALITY GAP", "+38.0pp Gap", "Critical operational impact"
        stat3_label, stat3_val, stat3_sub = "OPERATIONAL SCOPE", "Dark Store DS041", "Koramangala South · Dairy & Fresh"
    else:
        incident_badge = "🔴 ACTION REQUIRED · Primary Operational Incident"
        incident_title = "Zone GMV is ₹3.5L below baseline target (−7.8% Deficit)"
        incident_cause = (
            "Root cause identified: <b>76.2% of gap isolated</b> to acute inventory "
            "stockout at Dark Store DS041 (Koramangala South) across Dairy & Fresh SKUs."
        )
        stat1_label, stat1_val, stat1_sub = "ACTUAL VS TARGET", "₹41.5L vs ₹45.0L", "Baseline target ₹45.0L"
        stat2_label, stat2_val, stat2_sub = "FINANCIAL DEFICIT", "−₹3.5L Deficit", "Severity 5 / Critical"
        stat3_label, stat3_val, stat3_sub = "OPERATIONAL SCOPE", "Store DS041", "Koramangala South · Stockout"

    hero_html = f"""
<div class="prx-incident-hero">
  <div class="prx-incident-badge-row">
    <span class="prx-badge critical">{incident_badge}</span>
    <span class="prx-freshness fresh">
      <span class="prx-status-dot green"></span> Fresh · 47 min ago (SRC-OMS)
    </span>
  </div>
  <div class="prx-incident-title">{incident_title}</div>
  <div class="prx-incident-cause">{incident_cause}</div>
  <div class="prx-incident-stats">
    <div class="prx-incident-stat-box">
      <div class="prx-incident-stat-label">{stat1_label}</div>
      <div class="prx-incident-stat-value">{stat1_val}</div>
      <div class="prx-incident-stat-sub">{stat1_sub}</div>
    </div>
    <div class="prx-incident-stat-box">
      <div class="prx-incident-stat-label">{stat2_label}</div>
      <div class="prx-incident-stat-value red">{stat2_val}</div>
      <div class="prx-incident-stat-sub">{stat2_sub}</div>
    </div>
    <div class="prx-incident-stat-box">
      <div class="prx-incident-stat-label">{stat3_label}</div>
      <div class="prx-incident-stat-value">{stat3_val}</div>
      <div class="prx-incident-stat-sub">{stat3_sub}</div>
    </div>
  </div>
</div>
"""
    st.markdown(hero_html, unsafe_allow_html=True)

    # Hero Card CTA Actions (Anchored directly beneath the incident hero)
    col_cta1, col_cta2, _ = st.columns([0.32, 0.32, 0.36])
    with col_cta1:
        if st.button(
            "⌕  Investigate Root Cause & Action →",
            key="hero_investigate_cta",
            type="primary",
            use_container_width=True,
        ):
            if on_investigate:
                on_investigate()
            else:
                if st.session_state.get("pipeline_result") is None:
                    with st.spinner("Running full causal investigation…"):
                        r = run_pipeline(
                            scenario=get_scenario("s1"),
                            persona=st.session_state.persona,
                        )
                        st.session_state.pipeline_result = r
                        st.session_state.scenario_name = "s1"
                st.session_state.page = "Active Investigation"
                st.rerun()

    with col_cta2:
        if st.button(
            "▶  Run S2 (Memory Boost Demo)",
            key="hero_s2_cta",
            use_container_width=True,
        ):
            if on_run_scenario:
                on_run_scenario("s2", True)
            else:
                with st.spinner("Executing S2 with Corporate Memory…"):
                    r = run_pipeline(
                        scenario=get_scenario("s2"),
                        persona=st.session_state.persona,
                        use_memory=True,
                    )
                    st.session_state.pipeline_result = r
                    st.session_state.scenario_name = "s2"
                st.session_state.page = "Active Investigation"
                st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 2 (5–15s): STABLE OPERATIONS & CONTINUOUS MONITORING GRID
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        section_label("STABLE OPERATIONS & CONTINUOUS MONITORING (4 MONITORED KPIS)"),
        unsafe_allow_html=True,
    )

    # Static stable metrics defining the calm 2-column grid
    stable_chips_html = """
<div class="prx-stable-grid">
  <div class="prx-kpi-chip">
    <div>
      <div class="prx-kpi-chip-name">Delivery SLA Adherence</div>
      <div class="prx-kpi-chip-source">SRC-DEL · 15-min cadence</div>
    </div>
    <div>
      <div class="prx-kpi-chip-val">96.4%</div>
      <div class="prx-kpi-chip-status">
        <span class="prx-status-dot green"></span> Stable · On Track
      </div>
    </div>
  </div>

  <div class="prx-kpi-chip">
    <div>
      <div class="prx-kpi-chip-name">Order Conversion Rate</div>
      <div class="prx-kpi-chip-source">SRC-SESS+OMS · 1h cadence</div>
    </div>
    <div>
      <div class="prx-kpi-chip-val">5.8%</div>
      <div class="prx-kpi-chip-status">
        <span class="prx-status-dot green"></span> +0.1pp · Normal
      </div>
    </div>
  </div>

  <div class="prx-kpi-chip">
    <div>
      <div class="prx-kpi-chip-name">Stockout Rate · DS042 (North)</div>
      <div class="prx-kpi-chip-source">SRC-INV · 15-min cadence</div>
    </div>
    <div>
      <div class="prx-kpi-chip-val">2.1%</div>
      <div class="prx-kpi-chip-status">
        <span class="prx-status-dot green"></span> Healthy (&lt;4% target)
      </div>
    </div>
  </div>

  <div class="prx-kpi-chip">
    <div>
      <div class="prx-kpi-chip-name">Customer Satisfaction (CSAT)</div>
      <div class="prx-kpi-chip-source">SRC-CRM · Daily cadence</div>
    </div>
    <div>
      <div class="prx-kpi-chip-val">4.7 / 5.0</div>
      <div class="prx-kpi-chip-status">
        <span class="prx-status-dot green"></span> Stable · Benchmark
      </div>
    </div>
  </div>
</div>
"""
    st.markdown(stable_chips_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 3 (15–30s): ORGANIZATIONAL MEMORY REASSURANCE BANNER
    # ─────────────────────────────────────────────────────────────────────────
    _render_learning_insight()


def _render_learning_insight():
    """Compact strip showing memory status — introduces the compounding learning loop."""
    memory_count = 0
    try:
        from praxis.c5_memory.gateway import _get_conn
        conn = _get_conn()
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
        mem_pts = min(12 + 6 * (total - 1), 25)
        insight_title = "Compounding Organizational Memory Active"
        insight_text = (
            f"Praxis has <b>{total} validated decision record{'s' if total != 1 else ''}</b> "
            f"in institutional memory. The next matching investigation will receive an automatic "
            f"<b>+{mem_pts} pt confidence boost</b> without manual model retraining."
        )
    else:
        insight_title = "Organizational Memory Initializing"
        insight_text = (
            "No validated decisions recorded yet. Once you approve today's recommendation and confirm "
            "the 48-hour recovery outcome, Praxis will encode this pattern into permanent institutional memory."
        )

    st.markdown(f"""
<div class="prx-memory-banner">
  <div class="prx-memory-banner-icon">⊗</div>
  <div>
    <div class="prx-memory-banner-title">{insight_title}</div>
    <div class="prx-memory-banner-text">{insight_text}</div>
  </div>
</div>
""", unsafe_allow_html=True)
