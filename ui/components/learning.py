"""
Learning pages — What Praxis Has Learned + Memory.
Demonstrates the closed learning loop and governed memory.
Consumes C5 gateway DuckDB records directly.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import streamlit as st

from ui.components.design_system import (
    section_label, callout, badge, empty_state,
    memory_card_html, method_badge
)


# ────────────────────────────────────────────────────────────────────────────
# What Praxis Has Learned
# ────────────────────────────────────────────────────────────────────────────

def render_learning_page(result=None):
    """The 'What Praxis Has Learned' page — memory as organizational knowledge."""

    st.markdown('<div class="prx-page-title">What Praxis Has Learned</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Every approved decision and recorded outcome becomes '
        'governed organizational experience. Praxis does not accumulate opinions — '
        'it accumulates <b>validated, traceable evidence</b>.</div>',
        unsafe_allow_html=True
    )

    # The learning loop
    st.markdown(section_label("THE PRAXIS LEARNING LOOP"), unsafe_allow_html=True)
    st.markdown("""
<div class="prx-loop">
  <div class="prx-loop-node">
    <div class="prx-loop-icon">📊</div>
    <div class="prx-loop-label">KPI Signal</div>
    <div class="prx-loop-sub">Detected by C2</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node">
    <div class="prx-loop-icon">🔍</div>
    <div class="prx-loop-label">Investigation</div>
    <div class="prx-loop-sub">C2 + C3 analysis</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node active">
    <div class="prx-loop-icon">→</div>
    <div class="prx-loop-label">Decision</div>
    <div class="prx-loop-sub">C4 recommendation</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node">
    <div class="prx-loop-icon">📋</div>
    <div class="prx-loop-label">Action Taken</div>
    <div class="prx-loop-sub">Approved by user</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node">
    <div class="prx-loop-icon">✓</div>
    <div class="prx-loop-label">Outcome</div>
    <div class="prx-loop-sub">Observed &amp; recorded</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node memory-node">
    <div class="prx-loop-icon">⊗</div>
    <div class="prx-loop-label">Memory</div>
    <div class="prx-loop-sub">C5 · Governed admission</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node active">
    <div class="prx-loop-icon">↑</div>
    <div class="prx-loop-label">Better Decision</div>
    <div class="prx-loop-sub">Higher confidence next time</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Memory admission pipeline
    st.markdown(section_label("MEMORY GOVERNANCE PIPELINE — C5 Gateway"), unsafe_allow_html=True)
    st.markdown("""
<div class="prx-table-wrap">
  <table class="prx-table">
    <thead><tr><th>Step</th><th>Gate</th><th>Rule</th><th>If Fails</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>Lineage check</td><td>finding_id must exist in C1 lineage registry</td><td>REJECTED</td></tr>
      <tr><td>2</td><td>Driver governance</td><td>driver_type must be a governed driver from KPI contracts</td><td>REJECTED</td></tr>
      <tr><td>3</td><td>Idempotency</td><td>No duplicate decision_memory_id admitted</td><td>QUARANTINED</td></tr>
      <tr><td>4</td><td>Entry-state rule</td><td>Live records enter as 'pending'; demo fixtures as 'demo_preapproved'</td><td>REJECTED</td></tr>
      <tr><td>5</td><td>Outcome linkage</td><td>Outcome must link to an ADMITTED (non-rejected) DecisionMemory</td><td>REJECTED</td></tr>
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)

    st.markdown(callout(
        "<b>User feedback does not directly become truth.</b> "
        "Feedback enters as an OutcomeMemory record that passes through the C5 gateway. "
        "The gateway validates lineage, checks the referenced DecisionMemory status, "
        "enforces idempotency, and only then ADMITS the record. "
        "Admitted outcome records influence future confidence arithmetic — not LLM instructions.",
        kind="info", icon="ℹ"
    ), unsafe_allow_html=True)

    # Memory correction / supersession
    st.markdown(section_label("MEMORY CORRECTION — Supersession Model"), unsafe_allow_html=True)
    st.markdown("""
<div class="prx-card">
  <div style="font-size:.75rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;
              letter-spacing:.05em;margin-bottom:1rem;">ILLUSTRATION — How Praxis handles incorrect prior knowledge</div>

  <div style="display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:.75rem;align-items:center;">
    <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:6px;padding:.875rem;">
      <div style="font-size:.5625rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.25rem;">Previous Belief (now superseded)</div>
      <div style="font-size:.8125rem;font-weight:600;color:#6B7280;text-decoration:line-through;margin-bottom:.25rem;">"Competitor promotion caused the decline."</div>
      <span class="prx-mem-status-badge superseded">Superseded</span>
    </div>
    <div style="font-size:1.25rem;color:#D1D5DB;">→</div>
    <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:6px;padding:.875rem;">
      <div style="font-size:.5625rem;font-weight:700;color:#92400E;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.25rem;">New Evidence</div>
      <div style="font-size:.8125rem;color:#78350F;line-height:1.5;">Competitor promotion confirmed NOT active during the period (verified via external data feed).</div>
    </div>
    <div style="font-size:1.25rem;color:#D1D5DB;">→</div>
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:6px;padding:.875rem;">
      <div style="font-size:.5625rem;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.25rem;">Corrected Knowledge</div>
      <div style="font-size:.8125rem;font-weight:600;color:#166534;margin-bottom:.25rem;">"DS041 stockout was the dominant supported driver."</div>
      <span class="prx-mem-status-badge confirmed">Validated</span>
    </div>
  </div>

  <div style="margin-top:1rem;font-size:.75rem;color:#6B7280;line-height:1.6;">
    The superseded record is <b>not deleted</b> — it is preserved with status='superseded'.
    The historical audit trail remains intact. Future retrieval uses the corrected record.
    The memory gateway does not allow silent overwriting of admitted records.
  </div>
</div>
""", unsafe_allow_html=True)

    # Key differentiator
    st.markdown(section_label("THE CORE DIFFERENTIATOR"), unsafe_allow_html=True)
    st.markdown("""
<div class="prx-callout purple">
  <span class="prx-callout-icon">⬡</span>
  <div class="prx-callout-body">
    <b>"Every AI-BI tool tells you what happened once.<br>
    Praxis is the only one that remembers what happened last time
    and gets smarter before you ask again."</b><br><br>
    <span style="font-size:.8125rem;">
    Decision 1: Cold start · QUALIFY · confidence 60<br>
    Outcome: ₹3.2L recovered · validated<br>
    Decision 3: Memory retrieved · ANSWER · confidence 72<br>
    Delta = +12 pts from 1 confirmed precedent (C5 §4 formula)
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# Memory
# ────────────────────────────────────────────────────────────────────────────

def render_memory_page(result=None, on_feedback: Optional[Callable] = None):
    """The Memory page — DuckDB admission history."""

    st.markdown('<div class="prx-page-title">Memory</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Governed organizational experience — validated decisions and outcomes '
        'stored in the C5 DuckDB memory layer.</div>',
        unsafe_allow_html=True
    )

    # Load records from DuckDB
    decision_records = []
    outcome_records = []
    try:
        from praxis.c5_memory.gateway import _get_conn
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM decision_memory ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        cols = ["decision_memory_id", "finding_id", "driver_type", "grain_key",
                "grain_level", "original_confidence_band", "action_taken",
                "validation_status", "demo_fixture", "created_at"]
        decision_records = [dict(zip(cols, r)) for r in rows]

        out_rows = conn.execute(
            "SELECT * FROM outcome_memory ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
        out_cols = ["outcome_memory_id", "decision_memory_id", "observed_outcome",
                    "outcome_matches_hypothesis", "observed_at", "demo_fixture", "created_at"]
        outcome_records = [dict(zip(out_cols, r)) for r in out_rows]
        conn.close()
    except Exception as e:
        st.warning(f"Could not load memory records: {e}")

    # Confidence explainer
    confirmed = sum(1 for r in outcome_records if r.get("outcome_matches_hypothesis"))
    if confirmed > 0:
        mem_pts = min(12 + 6 * (confirmed - 1), 25)
        st.markdown(callout(
            f"<b>Memory currently contributes +{mem_pts} confidence points</b> to the next "
            f"DS041 / dark_store_stockout_rate finding. "
            f"Formula: min(12 + 6×(n−1), 25) where n = {confirmed} confirmed precedent(s). "
            "This is applied deterministically in the C3 confidence formula.",
            kind="ok", icon="⊗"
        ), unsafe_allow_html=True)

    # Decision memory records
    st.markdown(section_label(f"DECISION MEMORY RECORDS ({len(decision_records)})"), unsafe_allow_html=True)

    if not decision_records:
        st.markdown(empty_state(
            "No memory records yet",
            "Run a scenario, approve a recommendation, and the decision will be admitted to memory.",
            "⊗"
        ), unsafe_allow_html=True)
    else:
        for rec in decision_records:
            st.markdown(memory_card_html(rec), unsafe_allow_html=True)

    # Outcome memory records
    st.markdown(section_label(f"OUTCOME MEMORY RECORDS ({len(outcome_records)})"), unsafe_allow_html=True)

    if not outcome_records:
        st.markdown(callout(
            "No outcome records yet. Submit feedback from the Past Decisions page "
            "after observing the real-world result of an approved decision.",
            kind="info", icon="ℹ"
        ), unsafe_allow_html=True)
    else:
        for rec in outcome_records:
            matches = rec.get("outcome_matches_hypothesis")
            status_cls = "confirmed" if matches else "rejected"
            status_lbl = "Hypothesis Confirmed" if matches else "Hypothesis Rejected"
            st.markdown(f"""
<div class="prx-card-sm">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.375rem;">
    <span style="font-size:.875rem;font-weight:600;color:#0F1117;">
      Outcome · DM: {rec.get('decision_memory_id','?')}
    </span>
    <span class="prx-mem-status-badge {status_cls}">{status_lbl}</span>
  </div>
  <div style="font-size:.75rem;color:#6B7280;line-height:1.6;">
    <b>Observed:</b> {rec.get('observed_outcome','—')}<br>
    <b>Recorded at:</b> {rec.get('created_at','?')[:16]}
  </div>
</div>""", unsafe_allow_html=True)

    # Feedback form
    st.markdown(section_label("SUBMIT OUTCOME FEEDBACK"), unsafe_allow_html=True)
    st.markdown(callout(
        "Feedback is <b>lightweight</b> but <b>governed</b>. "
        "It passes through the C5 gateway before influencing future confidence. "
        "The gateway validates lineage, checks for duplicates, and enforces entry-state rules.",
        kind="info", icon="ℹ"
    ), unsafe_allow_html=True)

    dm_id_input = st.text_input(
        "Decision Memory ID",
        value=st.session_state.get("last_admitted_dm_id", "") or
              (decision_records[0].get("decision_memory_id", "") if decision_records else ""),
        key="mem_dm_id_input"
    )
    observed_text = st.text_input(
        "Observed outcome",
        value="₹3.2L recovered via cross-store transfer",
        key="mem_observed_text"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Mark as Confirmed (hypothesis correct)", type="primary", key="mem_confirm"):
            if on_feedback:
                on_feedback(True, dm_id_input, observed_text)
                st.rerun()
    with col2:
        if st.button("✗ Mark as Rejected (hypothesis wrong)", key="mem_reject"):
            if on_feedback:
                on_feedback(False, dm_id_input, observed_text)
                st.rerun()

    fb = st.session_state.get("feedback_msg")
    if fb:
        cls, msg = fb
        html_cls = "prx-feedback-ok" if cls == "ok" else "prx-feedback-err"
        st.markdown(f'<div class="{html_cls}">{msg}</div>', unsafe_allow_html=True)
        st.session_state.feedback_msg = None


def render_learning(result=None, on_feedback=None):
    """
    Merged 'Memory & Learning' page.
    Tab 1: Learning loop — what Praxis has learned (narrative + governance).
    Tab 2: Memory records — DuckDB records + feedback form.
    """
    st.markdown('<div class="prx-page-title">Memory &amp; Learning</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Every approved decision becomes governed organizational experience. '
        'Praxis accumulates <b>validated, traceable evidence</b> — not opinions.</div>',
        unsafe_allow_html=True
    )

    tab_loop, tab_mem = st.tabs(["⊗  Learning Loop", "≡  Memory Records"])

    with tab_loop:
        render_learning_page(result=result)

    with tab_mem:
        render_memory_page(result=result, on_feedback=on_feedback)

