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
    """Sticky enterprise header with brand, persona, zone, period, status."""
    persona_display = PERSONA_DISPLAY.get(st.session_state.persona, "Business Leader")
    st.markdown(f"""
<div class="prx-app-header">
  <div style="display:flex;align-items:center;gap:1.5rem;">
    <div class="prx-wordmark">⬡ <span>PRAXIS</span>
      <span class="prx-wordmark-sub">KPI Intelligence to Action</span>
    </div>
  </div>
  <div class="prx-header-ctx">
    <span class="prx-ctx-item">👤 <b>{persona_display}</b></span>
    <span class="prx-ctx-item">📍 <b>{st.session_state.zone}</b></span>
    <span class="prx-ctx-item">📅 <b>{st.session_state.period}</b></span>
    <span class="prx-ctx-item"><span class="prx-status-dot green"></span> <b>Operational</b></span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar Navigation ───────────────────────────────────────────────────────

NAV_SECTIONS = {
    "HOME": ["Morning Briefing"],
    "INVESTIGATE": ["Active Investigations"],
    "DECISIONS": ["Recommended Actions", "Past Decisions"],
    "LEARNING": ["What Praxis Has Learned", "Memory"],
    "GOVERNANCE": ["Evidence & Audit Trail", "Data Health",
                   "Access & Entitlements", "Telemetry"],
    "DEMO": ["Scenario Launcher"],
}


def _render_sidebar():
    """Render the enterprise sidebar."""
    with st.sidebar:
        # Logo
        st.markdown("""
<div class="prx-sidebar-logo">
  ⬡ <span>PRAXIS</span>
  <span class="prx-sidebar-logo-sub">KPI Intelligence to Action</span>
</div>""", unsafe_allow_html=True)

        # Persona selector
        persona_option = st.selectbox(
            "Active Persona",
            ["Business Leader", "Operations Manager"],
            index=0 if st.session_state.persona == Persona.ZONE_BUSINESS_HEAD else 1,
            label_visibility="collapsed",
        )
        new_persona = PERSONA_FROM_DISPLAY.get(persona_option, Persona.ZONE_BUSINESS_HEAD)
        if new_persona != st.session_state.persona:
            st.session_state.persona = new_persona
            st.session_state.persona_label = persona_option
            st.rerun()

        st.markdown('<div class="prx-sidebar-divider"></div>', unsafe_allow_html=True)

        # Navigation
        all_pages = [p for pages in NAV_SECTIONS.values() for p in pages]
        for section, pages in NAV_SECTIONS.items():
            st.markdown(f'<div class="prx-sidebar-group">{section}</div>',
                        unsafe_allow_html=True)
            for page in pages:
                icon = _page_icon(page)
                if st.button(f"{icon}  {page}", key=f"nav_{page}",
                             use_container_width=True,
                             type="primary" if st.session_state.page == page else "secondary"):
                    st.session_state.page = page
                    st.rerun()


def _page_icon(page: str) -> str:
    icons = {
        "Morning Briefing":       "◉",
        "Active Investigations":  "⌕",
        "Recommended Actions":    "→",
        "Past Decisions":         "⊞",
        "What Praxis Has Learned":"◈",
        "Memory":                 "⊗",
        "Evidence & Audit Trail": "≡",
        "Data Health":            "⬡",
        "Access & Entitlements":  "⊕",
        "Telemetry":              "⊛",
        "Scenario Launcher":      "▶",
    }
    return icons.get(page, "·")


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

    elif page == "Active Investigations":
        if result is None:
            _no_result_state("Active Investigations",
                             "No investigation is active.",
                             "Run a scenario from the Scenario Launcher or click Investigate in the Morning Briefing.")
        else:
            render_investigation(result=result, persona=persona)

    elif page == "Recommended Actions":
        if result is None:
            _no_result_state("Recommended Actions",
                             "No analysis has been run yet.",
                             "Open the Scenario Launcher and run the Signature Demo to see recommended actions.")
        else:
            from ui.components.decisions import render_recommended_actions
            render_recommended_actions(result=result, persona=persona,
                                       on_approve=_approve_decision)

    elif page == "Past Decisions":
        from ui.components.decisions import render_past_decisions
        render_past_decisions(decisions=st.session_state.past_decisions)

    elif page == "What Praxis Has Learned":
        from ui.components.learning import render_learning_page
        render_learning_page(result=result)

    elif page == "Memory":
        from ui.components.learning import render_memory_page
        render_memory_page(result=result, on_feedback=_submit_feedback)

    elif page == "Evidence & Audit Trail":
        from ui.components.governance import render_audit_trail
        render_audit_trail(result=result)

    elif page == "Data Health":
        from ui.components.governance import render_data_health
        render_data_health()

    elif page == "Access & Entitlements":
        from ui.components.governance import render_entitlements
        render_entitlements(persona=persona)

    elif page == "Telemetry":
        from ui.components.governance import render_telemetry
        render_telemetry(result=result)

    elif page == "Scenario Launcher":
        render_scenario_launcher(
            on_run=lambda name, mem: _run_and_navigate(name, mem)
        )


def _navigate_to_investigation():
    st.session_state.page = "Active Investigations"
    st.rerun()


def _run_and_navigate(name: str, use_memory: bool):
    _run_scenario(name, use_memory)
    st.session_state.page = "Active Investigations"
    st.rerun()


def _no_result_state(title: str, message: str, hint: str):
    from ui.components.design_system import empty_state
    st.markdown(f'<div class="prx-page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(empty_state(message, hint, "○"), unsafe_allow_html=True)
    if st.button("→ Open Scenario Launcher"):
        st.session_state.page = "Scenario Launcher"
        st.rerun()


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
