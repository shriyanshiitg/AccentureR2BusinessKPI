"""
PRAXIS — KPI Intelligence to Action
====================================
Enterprise-grade decision-intelligence product UI.
Round 2 prototype · Accenture Innovation Challenge 2026

Architecture principle: UI consumes canonical backend objects (PipelineResult,
DecisionPackage, EvidencePackage, HypothesisPackage). No quantitative truth
is computed here. All numerical values originate in C1–C5.

Navigation:
  HOME       → Morning Briefing
  INVESTIGATE → Active Investigations
  DECISIONS  → Recommended Actions / Past Decisions
  LEARNING   → What Praxis Learned / Memory
  GOVERNANCE → Evidence & Audit / Data Health / Entitlements / Telemetry
  DEMO       → Scenario Launcher
"""

from __future__ import annotations

import sys
import os
import datetime

# Make sure praxis package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

# ─── Streamlit page config (must be first) ────────────────────────────────────
st.set_page_config(
    page_title="Praxis — KPI Intelligence to Action",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Inject design system CSS ────────────────────────────────────────────────
from ui.components.design_system import PRAXIS_CSS
st.markdown(PRAXIS_CSS, unsafe_allow_html=True)

# ─── Backend imports ─────────────────────────────────────────────────────────
from praxis.orchestration.pipeline import run_pipeline, run_all_kpis
from praxis.synthetic.generator import get_scenario
from praxis.c1_data_foundation.entitlements import Persona
from praxis.c5_memory.gateway import (
    _get_conn, admit_decision_memory, admit_outcome_memory,
    register_finding_id
)
import uuid

# ─── Page modules ─────────────────────────────────────────────────────────────
from ui.components.morning_briefing import render_morning_briefing
from ui.components.investigation import render_investigation
from ui.components.decisions import render_decisions
from ui.components.learning import render_learning
from ui.components.governance import render_governance
from ui.components.scenario_launcher import render_scenario_launcher


# ─── Session state initialisation ────────────────────────────────────────────

# ─── Persona display names (UI only — backend constants unchanged) ─────────────
PERSONA_DISPLAY = {
    Persona.ZONE_BUSINESS_HEAD:      "Business Leader",
    Persona.DARK_STORE_OPS_MANAGER:  "Operations Manager",
}
PERSONA_FROM_DISPLAY = {v: k for k, v in PERSONA_DISPLAY.items()}


def _init_state():
    defaults = {
        "page":            "Morning Briefing",
        "persona":         Persona.ZONE_BUSINESS_HEAD,
        "persona_label":   "Business Leader",
        "zone":            "Zone Z003 · Koramangala",
        "period":          "Week 33 · Aug 2026",
        "pipeline_result": None,
        "scenario_name":   None,
        "alert_queue":     None,
        "feedback_msg":    None,
        "last_admitted_dm_id": None,
        "past_decisions":  [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ─── Global Header ────────────────────────────────────────────────────────────

def _render_header():
    """Sticky enterprise header with frosted glass, brand, persona pills, status."""
    persona_display = PERSONA_DISPLAY.get(st.session_state.persona, "Business Leader")
    st.markdown(f"""
<div class="prx-app-header">
  <div style="display:flex;align-items:center;gap:0.5rem;">
    <div class="prx-wordmark">
      <div class="prx-wordmark-icon">
        <svg width="13" height="13" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M7 1L13 4.5V10.5L7 14L1 10.5V4.5L7 1Z" fill="white" fill-opacity="0.9"/>
        </svg>
      </div>
      PR<span class="prx-wordmark-accent">AXIS</span>
      <span class="prx-wordmark-sub">KPI Intelligence to Action</span>
    </div>
  </div>
  <div class="prx-header-ctx">
    <span class="prx-ctx-pill">👤 <b>{persona_display}</b></span>
    <span class="prx-ctx-pill">📍 <b>{st.session_state.zone}</b></span>
    <span class="prx-ctx-pill">📅 <b>{st.session_state.period}</b></span>
    <div class="prx-ctx-divider"></div>
    <span class="prx-status-pill"><span class="prx-status-dot green"></span> Operational</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar Navigation ───────────────────────────────────────────────────────

# Redesigned: 5 items across 2 sections. "Scenario Launcher" is NOT a nav item —
# it's a persistent CTA button always visible at the bottom of the sidebar.
NAV_SECTIONS = {
    "WORKSPACE": [
        ("Morning Briefing",      "◉", "Today's KPI alerts"),
        ("Active Investigation",  "⌕", "Current analysis"),
        ("Actions & Decisions",   "✓", "Recommendations · History"),
    ],
    "SYSTEM": [
        ("Memory & Learning",     "⊗", "What Praxis has learned"),
        ("Audit & Governance",    "≡", "Evidence · Data Health · Access"),
    ],
}


def _render_sidebar():
    """Render the enterprise sidebar — 5 items + persistent demo CTA."""
    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────────
        persona_display = PERSONA_DISPLAY.get(st.session_state.persona, "Business Leader")
        st.markdown(f"""
<div class="prx-sidebar-logo">
  <div class="prx-sidebar-logo-mark">
    <div class="prx-sidebar-logo-icon">
      <svg width="12" height="12" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M7 1L13 4.5V10.5L7 14L1 10.5V4.5L7 1Z" fill="white" fill-opacity="0.9"/>
      </svg>
    </div>
    PR<span class="acc">AXIS</span>
  </div>
  <div class="prx-sidebar-logo-sub">KPI Intelligence to Action</div>
</div>
<div class="prx-sidebar-persona">
  <div>
    <span class="prx-sidebar-persona-label">Active Persona</span>
    <span class="prx-sidebar-persona-name">{persona_display}</span>
  </div>
</div>""", unsafe_allow_html=True)

        # Persona selector
        persona_option = st.selectbox(
            "Switch Persona",
            ["Business Leader", "Operations Manager"],
            index=0 if st.session_state.persona == Persona.ZONE_BUSINESS_HEAD else 1,
            label_visibility="collapsed",
            key="persona_select_sidebar",
        )
        new_persona = PERSONA_FROM_DISPLAY.get(persona_option, Persona.ZONE_BUSINESS_HEAD)
        if new_persona != st.session_state.persona:
            st.session_state.persona = new_persona
            st.session_state.persona_label = persona_option
            st.rerun()

        st.markdown('<div class="prx-sidebar-divider"></div>', unsafe_allow_html=True)

        # ── Navigation (5 items) ──────────────────────────────────────────────
        current_page = st.session_state.page
        for section, items in NAV_SECTIONS.items():
            st.markdown(f'<div class="prx-sidebar-group">{section}</div>',
                        unsafe_allow_html=True)
            for page_name, icon, hint in items:
                is_active = (current_page == page_name)
                if st.button(
                    f"{icon}  {page_name}",
                    key=f"nav_{page_name}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    help=hint,
                ):
                    st.session_state.page = page_name
                    st.rerun()

        st.markdown('<div class="prx-sidebar-divider"></div>', unsafe_allow_html=True)

        # ── Persistent Scenario Demo CTA ───────────────────────────────────────
        st.markdown("""
<div class="prx-sidebar-demo-btn">
  <div class="prx-sidebar-demo-label">▶ Live Demo</div>
  <div class="prx-sidebar-demo-title">Run Signature Demo</div>
  <div class="prx-sidebar-demo-sub">S1 → S2 · Memory Proof</div>
</div>""", unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("S1 · Cold Start", key="quick_s1", use_container_width=True):
                _run_and_navigate("s1", False)
        with col_s2:
            if st.button("S2 · Memory", key="quick_s2", use_container_width=True, type="primary"):
                _run_and_navigate("s2", True)

        # ── System status footer ───────────────────────────────────────────────
        st.markdown("""
<div class="prx-sidebar-footer">
  <div class="prx-sidebar-footer-item"><span>Engine</span><b>C1–C5 Pipeline</b></div>
  <div class="prx-sidebar-footer-item"><span>Tests</span><b style="color:#059669">76 passing</b></div>
  <div class="prx-sidebar-footer-item"><span>LLM</span><b>Gemini 1.5 Flash</b></div>
</div>""", unsafe_allow_html=True)


# ─── Main routing ─────────────────────────────────────────────────────────────

def main():
    _render_header()
    _render_sidebar()

    page = st.session_state.page
    result = st.session_state.pipeline_result
    persona = st.session_state.persona
    alert_queue = _get_alert_queue()

    if page == "Morning Briefing":
        render_morning_briefing(
            alert_queue=alert_queue,
            pipeline_result=result,
            on_investigate=lambda: _navigate_to_investigation(),
            on_run_scenario=lambda name, mem: _run_and_navigate(name, mem),
        )

    elif page == "Active Investigation":
        if result is None:
            _no_result_state(
                "Active Investigation",
                "No investigation is running.",
                "Use the 'Run Signature Demo' button in the sidebar to launch an analysis.",
            )
        else:
            render_investigation(result=result, persona=persona)

    elif page == "Actions & Decisions":
        # Merged: Recommended Actions + Past Decisions in one page with tabs
        from ui.components.decisions import render_decisions
        render_decisions(
            result=result,
            persona=persona,
            decisions=st.session_state.past_decisions,
            on_approve=_approve_decision,
            on_feedback=_submit_feedback,
        )

    elif page == "Memory & Learning":
        # Merged: What Praxis Learned + Memory records
        from ui.components.learning import render_learning
        render_learning(result=result, on_feedback=_submit_feedback)

    elif page == "Audit & Governance":
        # Merged: Evidence + Data Health + Access + Telemetry
        from ui.components.governance import render_governance
        render_governance(result=result, persona=persona)

    # Legacy routes kept for backward compat (team members may link to these)
    elif page in ("Recommended Actions", "Past Decisions"):
        st.session_state.page = "Actions & Decisions"
        st.rerun()
    elif page in ("What Praxis Has Learned", "Memory"):
        st.session_state.page = "Memory & Learning"
        st.rerun()
    elif page in ("Evidence & Audit Trail", "Data Health", "Access & Entitlements", "Telemetry"):
        st.session_state.page = "Audit & Governance"
        st.rerun()
    elif page == "Scenario Launcher":
        # Redirect to sidebar demo — the launcher is now inline
        st.session_state.page = "Morning Briefing"
        st.rerun()

    elif page == "Active Investigations":   # legacy name
        st.session_state.page = "Active Investigation"
        st.rerun()


def _navigate_to_investigation():
    st.session_state.page = "Active Investigation"
    st.rerun()


# ─── Run pipeline helper ──────────────────────────────────────────────────────

def _run_scenario(name: str, use_memory: bool = True):
    """Run a named scenario and cache result in session state."""
    scenario = get_scenario(name)
    with st.spinner("Running Praxis analysis…"):
        result = run_pipeline(
            scenario=scenario,
            persona=st.session_state.persona,
            use_memory=use_memory,
        )
    st.session_state.pipeline_result = result
    st.session_state.scenario_name = name
    return result


# ─── Morning Briefing data ────────────────────────────────────────────────────

def _get_alert_queue():
    if st.session_state.alert_queue is None:
        st.session_state.alert_queue = run_all_kpis()
    return st.session_state.alert_queue




def _run_and_navigate(name: str, use_memory: bool):
    _run_scenario(name, use_memory)
    st.session_state.page = "Active Investigation"
    st.rerun()


def _no_result_state(title: str, message: str, hint: str):
    from ui.components.design_system import empty_state
    st.markdown(f'<div class="prx-page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(empty_state(message, hint, "○"), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("▶ S1 · Cold Start Demo", type="primary"):
            _run_and_navigate("s1", False)
    with col2:
        if st.button("▶ S2 · Memory Demo", type="primary"):
            _run_and_navigate("s2", True)


def _approve_decision(result):
    """Record the approved decision to DuckDB via C5 gateway."""
    if result is None or result.evidence_package is None:
        return
    ep = result.evidence_package
    dp = result.decision_package
    hp = result.hypothesis_package

    fid = ep.finding_id
    dm_id = f"DM-{str(uuid.uuid4())[:8].upper()}"
    leading_driver = "residual"
    confidence_band = "MEDIUM"
    if hp and hp.hypotheses:
        leading_driver = hp.hypotheses[0].get("driver_type", "residual")
        confidence_band = hp.hypotheses[0].get("confidence_band", "MEDIUM")

    action_taken = "L2_cross_store_transfer"
    if dp and dp.actions:
        action_taken = dp.actions[0].controllable_lever

    record = {
        "decision_memory_id": dm_id,
        "finding_id": fid,
        "driver_type": leading_driver,
        "grain_key": ep.kpi_instance_id or ep.grain_key,
        "grain_level": "zone",
        "original_confidence_band": confidence_band,
        "action_taken": action_taken,
        "validation_status": "pending",
        "demo_fixture": False,
        "created_at": datetime.datetime.now().isoformat(),
    }
    try:
        res = admit_decision_memory(record)
        if res["status"] == "ADMITTED":
            st.session_state.last_admitted_dm_id = dm_id
            # Add to past decisions log
            st.session_state.past_decisions.append({
                "dm_id": dm_id,
                "date": datetime.date.today().strftime("%d %b %Y"),
                "kpi": ep.kpi_id,
                "driver": leading_driver,
                "action": action_taken,
                "confidence": confidence_band,
                "outcome": "Pending",
                "status": "Pending",
            })
            st.session_state.feedback_msg = ("ok", f"Decision recorded · ID: {dm_id} · Praxis memory updated.")
        else:
            st.session_state.feedback_msg = ("warn", f"Recorded with note: {res['reason']}")
    except Exception as e:
        st.session_state.feedback_msg = ("err", str(e))


def _submit_feedback(outcome_matches: bool, dm_id: str, observed_outcome: str):
    """Submit outcome feedback to C5 gateway."""
    if not dm_id:
        st.session_state.feedback_msg = ("err", "No decision ID available — run an investigation and approve first.")
        return
    om_id = f"OM-{str(uuid.uuid4())[:8].upper()}"
    record = {
        "outcome_memory_id": om_id,
        "decision_memory_id": dm_id,
        "observed_outcome": observed_outcome,
        "outcome_matches_hypothesis": outcome_matches,
        "observed_at": datetime.datetime.now().isoformat(),
        "demo_fixture": False,
        "created_at": datetime.datetime.now().isoformat(),
    }
    try:
        res = admit_outcome_memory(record)
        if res["status"] == "ADMITTED":
            st.session_state.feedback_msg = ("ok", f"Outcome recorded · {om_id} · Memory updated for future retrieval.")
            # Update past decisions
            for d in st.session_state.past_decisions:
                if d["dm_id"] == dm_id:
                    d["outcome"] = observed_outcome
                    d["status"] = "Confirmed" if outcome_matches else "Contradicted"
        else:
            st.session_state.feedback_msg = ("warn", f"Feedback with note: {res['reason']}")
    except Exception as e:
        st.session_state.feedback_msg = ("err", str(e))


if __name__ == "__main__":
    main()
