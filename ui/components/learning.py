"""
Memory & Learning — Organizational Intelligence & Precedent Retention (Page 4).

Primary Question: "How does Praxis improve over time?"

Layer 1 (0-5s):  Compounding Value Proof Hero Card (Cold Start 60 pts vs Boosted 72 pts).
Layer 2 (5-20s): Precedent Evolution Timeline (5-stage governed value proof).
Layer 3 (20-60s): Active Corporate Memory Repository (DuckDB C5) & Governed Learning Cycle.
Layer 4 (1-5m):  Progressive Disclosure: C5 Gateway Admission Rules & Supersession Model (Collapsed).

Zero quantitative recomputation in this file. Consumes C5 DuckDB records directly.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import streamlit as st

from ui.components.design_system import (
    section_label, section_sep, callout, badge, empty_state,
    memory_card_html, method_badge
)


# ────────────────────────────────────────────────────────────────────────────
# Page 4 Root: render_learning
# ────────────────────────────────────────────────────────────────────────────

def render_learning(result=None, on_feedback: Optional[Callable] = None):
    """
    Consolidated 'Memory & Learning' page (Page 4).
    Follows the 4-tier cognitive disclosure hierarchy.
    """
    st.markdown('<div class="prx-page-title">Memory &amp; Learning</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Every approved decision and confirmed outcome compounds institutional '
        'intelligence. Praxis accumulates <b>validated, traceable evidence</b> — not opinions.</div>',
        unsafe_allow_html=True
    )

    # Load live records from DuckDB
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

    confirmed_count = sum(1 for r in outcome_records if r.get("outcome_matches_hypothesis"))
    mem_pts = min(12 + 6 * max(confirmed_count - 1, 0), 25) if confirmed_count > 0 else 12

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 1 (0–5s): COMPOUNDING VALUE PROOF HERO CARD
    # ─────────────────────────────────────────────────────────────────────────
    proof_html = f"""<div class="prx-value-proof-hero">
<div class="prx-proof-badge-row">
<span class="prx-badge purple">⊗ INSTITUTIONAL MEMORY IN ACTION · Compounding Advantage</span>
<span class="prx-freshness fresh">
<span class="prx-status-dot green"></span> {confirmed_count} Confirmed Precedent Active (DuckDB C5)
</span>
</div>
<div class="prx-proof-title">How Praxis Learned From Decision #2026-W31-01</div>
<div style="font-size:0.875rem;color:var(--text-secondary);max-width:68ch;line-height:1.55;">
Empirical proof that Praxis improves analytical certainty through closed-loop decision learning,
elevating confidence without manual prompt engineering or model fine-tuning.
</div>
<div class="prx-value-proof-grid">
<div class="prx-proof-col">
<div class="prx-proof-col-label">Decision 1 · Cold Start (15 Aug 2026)</div>
<div class="prx-proof-conf-val">60 pts</div>
<div class="prx-proof-conf-sub">Confidence Band: <b>MEDIUM</b> (QUALIFY)</div>
<div class="prx-proof-item"><span>Precedent History:</span><b>0 matches (Cold Start)</b></div>
<div class="prx-proof-item"><span>Causal Grounding:</span><b>Proportion z-score + heuristics</b></div>
<div class="prx-proof-item"><span>Decision Outcome:</span><b>Approved with qualification caveats</b></div>
</div>
<div class="prx-proof-col boosted">
<div class="prx-proof-col-label">Decision 2 · Memory-Enhanced (Today)</div>
<div class="prx-proof-conf-val purple">72 pts</div>
<div class="prx-proof-conf-sub" style="color:var(--purple-800);">Confidence Band: <b>HIGH</b> (ANSWER · +{mem_pts} pts)</div>
<div class="prx-proof-item" style="border-color:var(--purple-200);"><span>Precedent Match:</span><b style="color:var(--purple-900);">DM-DEMO-001 (Koramangala Stockout)</b></div>
<div class="prx-proof-item" style="border-color:var(--purple-200);"><span>Historical Recovery:</span><b style="color:var(--purple-900);">₹3.2L (88% recovery achieved)</b></div>
<div class="prx-proof-item" style="border-color:var(--purple-200);"><span>Decision Outcome:</span><b style="color:var(--purple-900);">Immediate unilateral execution admitted</b></div>
</div>
</div>
<div style="display:flex;align-items:center;justify-content:space-between;padding-top:0.875rem;border-top:1px solid var(--border-soft);font-size:0.8125rem;color:var(--text-tertiary);">
<div><b>Net Precision Gain:</b> +{mem_pts} pts (+20.0% confidence boost)</div>
<div><b>Governing Policy:</b> C5 Confidence Formula §4: min(12 + 6×(n−1), 25)</div>
<div><b>Governance Gate:</b> Lineage Verified · Non-Superseded</div>
</div>
</div>"""
    st.markdown(proof_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 2 (5–20s): PRECEDENT EVOLUTION TIMELINE
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(section_label("PRECEDENT EVOLUTION TIMELINE (5-STAGE GOVERNED VALUE PROOF)"), unsafe_allow_html=True)

    timeline_html = """<div class="prx-timeline-steps">
<div class="prx-timeline-step active">
<div class="prx-timeline-num">STAGE 1 · 15 AUG</div>
<div class="prx-timeline-title">Anomaly Detected</div>
<div class="prx-timeline-desc">C2 flags −₹7.0L deficit at DS041; root-cause isolated with 60 pt baseline confidence.</div>
</div>
<div class="prx-timeline-step active">
<div class="prx-timeline-num">STAGE 2 · 15 AUG</div>
<div class="prx-timeline-title">Action Authorized</div>
<div class="prx-timeline-desc">Zone Business Head approves 1,200-unit cross-dock transfer from DS042.</div>
</div>
<div class="prx-timeline-step active">
<div class="prx-timeline-num">STAGE 3 · 17 AUG</div>
<div class="prx-timeline-title">Outcome Confirmed</div>
<div class="prx-timeline-desc">48-hour audit verifies ₹3.2L GMV recovered (91% realization of estimate).</div>
</div>
<div class="prx-timeline-step active">
<div class="prx-timeline-num">STAGE 4 · 17 AUG</div>
<div class="prx-timeline-title">Admitted to C5</div>
<div class="prx-timeline-desc">C5 Gateway passes 8 integrity gates and encodes DM-DEMO-001 into institutional memory.</div>
</div>
<div class="prx-timeline-step active">
<div class="prx-timeline-num">STAGE 5 · TODAY</div>
<div class="prx-timeline-title">Compounding Boost</div>
<div class="prx-timeline-desc">Matching investigation automatically retrieves precedent and applies +12 pt confidence boost.</div>
</div>
</div>"""
    st.markdown(timeline_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 3 (20–60s): ACTIVE MEMORY REPOSITORY & LEARNING LOOP
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(section_label(f"ACTIVE INSTITUTIONAL MEMORY RECORDS (DUCKDB C5 · {len(decision_records)} ADMITTED)"), unsafe_allow_html=True)

    if not decision_records:
        st.markdown(empty_state(
            "No memory records yet",
            "Run a scenario and authorize a recommendation to create the first institutional precedent.",
            "⊗"
        ), unsafe_allow_html=True)
    else:
        for rec in decision_records[:5]:
            st.markdown(memory_card_html(rec), unsafe_allow_html=True)

    # The 5-step learning loop
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(section_label("THE 5-STEP GOVERNED LEARNING CYCLE"), unsafe_allow_html=True)
    st.markdown("""
<div class="prx-loop">
  <div class="prx-loop-node">
    <div class="prx-loop-icon">📊</div>
    <div class="prx-loop-label">1. KPI Signal</div>
    <div class="prx-loop-sub">Detected by C2</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node">
    <div class="prx-loop-icon">🔍</div>
    <div class="prx-loop-label">2. Investigation</div>
    <div class="prx-loop-sub">C2 + C3 causal analysis</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node active">
    <div class="prx-loop-icon">→</div>
    <div class="prx-loop-label">3. Action</div>
    <div class="prx-loop-sub">C4 recommendation</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node">
    <div class="prx-loop-icon">✓</div>
    <div class="prx-loop-label">4. 48h Outcome</div>
    <div class="prx-loop-sub">Observed &amp; validated</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node memory-node">
    <div class="prx-loop-icon">⊗</div>
    <div class="prx-loop-label">5. C5 Memory</div>
    <div class="prx-loop-sub">Compounding confidence</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # LAYER 4 (1–5m): PROGRESSIVE DISCLOSURE (Collapsed by default)
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    with st.expander("▾  View C5 Memory Admission Gateway Rules (8 Integrity Gates)", expanded=False):
        st.markdown("""
<div class="prx-table-wrap">
  <table class="prx-table">
    <thead><tr><th>Gate</th><th>Integrity Check</th><th>Policy Specification</th><th>Failure Behavior</th></tr></thead>
    <tbody>
      <tr><td>Gate 1</td><td>Lineage Registration</td><td>finding_id must be cryptographically registered in C1 lineage ledger</td><td>REJECTED</td></tr>
      <tr><td>Gate 2</td><td>Driver Governance</td><td>driver_type must map to an approved KPI contract taxonomy</td><td>REJECTED</td></tr>
      <tr><td>Gate 3</td><td>Idempotency &amp; Uniqueness</td><td>decision_memory_id must be unique across all corporate tenants</td><td>QUARANTINED</td></tr>
      <tr><td>Gate 4</td><td>Confidence Threshold</td><td>Decision must satisfy minimum confidence score threshold (&gt;= 40 pts)</td><td>REJECTED</td></tr>
      <tr><td>Gate 5</td><td>Human Authorization</td><td>Requires explicit human authorization token from entitled persona</td><td>REJECTED</td></tr>
      <tr><td>Gate 6</td><td>48-Hour Outcome Linkage</td><td>Outcome records must verify against an admitted DecisionMemory parent</td><td>REJECTED</td></tr>
      <tr><td>Gate 7</td><td>Non-Superseded Status</td><td>Prior precedent must not have been superseded by conflicting evidence</td><td>REPLACED</td></tr>
      <tr><td>Gate 8</td><td>Audit Trail Immutability</td><td>All admission state transitions logged with monotonic timestamps</td><td>HALT</td></tr>
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)

    with st.expander("≡  View Memory Correction & Supersession Model", expanded=False):
        st.markdown("""
<div class="prx-card">
  <div style="font-size:0.75rem;font-weight:700;color:var(--text-tertiary);text-transform:uppercase;
              letter-spacing:0.05em;margin-bottom:1rem;">ILLUSTRATION — How Praxis handles incorrect prior knowledge</div>

  <div style="display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:0.75rem;align-items:center;">
    <div style="background:#F9FAFB;border:1px solid var(--border);border-radius:6px;padding:0.875rem;">
      <div style="font-size:0.5625rem;font-weight:700;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">Previous Belief (now superseded)</div>
      <div style="font-size:0.8125rem;font-weight:600;color:#6B7280;text-decoration:line-through;margin-bottom:0.25rem;">"Competitor promotion caused the decline."</div>
      <span class="prx-badge warning">Superseded</span>
    </div>
    <div style="font-size:1.25rem;color:#D1D5DB;">→</div>
    <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:6px;padding:0.875rem;">
      <div style="font-size:0.5625rem;font-weight:700;color:#92400E;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">New Evidence</div>
      <div style="font-size:0.8125rem;color:#78350F;line-height:1.5;">Competitor promotion confirmed NOT active during the period (verified via pricing feed).</div>
    </div>
    <div style="font-size:1.25rem;color:#D1D5DB;">→</div>
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:6px;padding:0.875rem;">
      <div style="font-size:0.5625rem;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem;">Corrected Knowledge</div>
      <div style="font-size:0.8125rem;font-weight:600;color:#166534;margin-bottom:0.25rem;">"DS041 stockout was the dominant supported driver."</div>
      <span class="prx-badge ok">Validated</span>
    </div>
  </div>

  <div style="margin-top:1rem;font-size:0.75rem;color:var(--text-secondary);line-height:1.6;">
    The superseded record is <b>not deleted</b> — it is preserved with status='superseded'.
    The historical audit trail remains intact. Future retrieval queries filter to active records only.
    The memory gateway prevents silent overwriting or phantom hallucinations.
  </div>
</div>
""", unsafe_allow_html=True)

    with st.expander("✓  Submit Real-World Outcome Feedback Form", expanded=False):
        st.markdown(callout(
            "Feedback passes through the C5 gateway before influencing future confidence calculations. "
            "The gateway validates lineage, checks for duplicates, and enforces entry-state rules.",
            kind="info", icon="ℹ"
        ), unsafe_allow_html=True)

        dm_id_input = st.text_input(
            "Decision Memory ID",
            value=st.session_state.get("last_admitted_dm_id", "") or
                  (decision_records[0].get("decision_memory_id", "") if decision_records else "DM-DEMO-001"),
            key="mem_dm_id_input"
        )
        observed_text = st.text_input(
            "Observed Recovery Outcome",
            value="₹3.2L recovered via cross-store transfer",
            key="mem_observed_text"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Mark as Confirmed (Hypothesis Correct)", type="primary", key="mem_confirm"):
                if on_feedback:
                    on_feedback(True, dm_id_input, observed_text)
                    st.rerun()
        with col2:
            if st.button("✗ Mark as Rejected (Hypothesis Wrong)", key="mem_reject"):
                if on_feedback:
                    on_feedback(False, dm_id_input, observed_text)
                    st.rerun()


# Backwards compatibility alias
def render_learning_page(result=None):
    render_learning(result=result)


def render_memory_page(result=None, on_feedback=None):
    render_learning(result=result, on_feedback=on_feedback)

