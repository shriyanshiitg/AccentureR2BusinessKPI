"""
Scenario Launcher — one-click demo scenarios.
Maps scenario names to descriptions and expected outcomes.
"""

from __future__ import annotations

from typing import Callable, Optional

import streamlit as st

from ui.components.design_system import section_label, callout, badge


SCENARIOS = [
    {
        "id": "s1",
        "label": "S1 — Canonical Stockout (Cold Start)",
        "tagline": "DS041 stockout · 2026-08-15 · Zone Z003",
        "what": "Zone GMV drops ₹3.8L. DS041 dark store is in stockout. "
                "No prior memory exists. Praxis reasons from first principles.",
        "expected": "QUALIFY · confidence ~60 · cross-store transfer recommended · no memory boost",
        "signature": True,
        "memory": False,
        "badge": "critical",
    },
    {
        "id": "s2",
        "label": "S2 — With Validated Memory (Decision 3)",
        "tagline": "Same pattern · 2026-08-22 · Validated precedent present",
        "what": "Comparable GMV decline. The S1 decision was approved, outcome confirmed. "
                "Praxis retrieves the validated memory record.",
        "expected": "ANSWER · confidence ~72 (+12 from memory) · sharper recommendation",
        "signature": True,
        "memory": True,
        "badge": "critical",
    },
    {
        "id": "insufficient_history",
        "label": "S3 — Insufficient History (Abstention)",
        "tagline": "New store DS099 · < 3 history days",
        "what": "KPI movement detected but baseline cannot be established. "
                "Praxis demonstrates responsible abstention rather than fabricating a conclusion.",
        "expected": "ABSTAIN · Praxis refuses to recommend without adequate evidence",
        "signature": False,
        "memory": False,
        "badge": "warning",
    },
    {
        "id": "no_dominant",
        "label": "S4 — No Dominant Contributor",
        "tagline": "Diffuse multi-driver pattern",
        "what": "GMV decline from multiple equally-weighted causes. "
                "Praxis cannot identify a dominant driver — qualifies its output.",
        "expected": "QUALIFY · no_dominant_contributor cap applied · confidence capped at MEDIUM",
        "signature": False,
        "memory": False,
        "badge": "warning",
    },
    {
        "id": "challenge",
        "label": "S5 — Contradicted Hypothesis",
        "tagline": "Customer voice contradicts stockout hypothesis",
        "what": "Stockout quantitatively dominant, but customer voice records contradict. "
                "Praxis reduces confidence and qualifies recommendation.",
        "expected": "QUALIFY · cv_contradicts hard cap · confidence reduced",
        "signature": False,
        "memory": False,
        "badge": "warning",
    },
    {
        "id": "unscripted",
        "label": "S6 — Unscripted (Genericity Test)",
        "tagline": "Random zone / store / event combination",
        "what": "New KPI, new zone, new event pattern — not pre-engineered. "
                "Proves the pipeline is fully generic — no KPI-specific branches.",
        "expected": "Variable outcome · demonstrates generic pipeline architecture",
        "signature": False,
        "memory": False,
        "badge": "info",
    },
]


def render_scenario_launcher(on_run: Optional[Callable] = None):
    """Full Scenario Launcher page."""

    st.markdown('<div class="prx-page-title">Scenario Launcher</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">One-click demo scenarios. Each launches the complete '
        'Praxis analysis pipeline and navigates to the investigation workspace.</div>',
        unsafe_allow_html=True
    )

    # Signature Demo spotlight
    st.markdown(section_label("SIGNATURE DEMO — THE MEMORY PROOF"), unsafe_allow_html=True)
    st.markdown(callout(
        "<b>For judging:</b> Run S1 first (cold start). Navigate to Recommendation → Approve → "
        "navigate to Past Decisions → Submit outcome as 'Confirmed'. Then run S2 (with memory). "
        "The confidence delta (+12 pts) is the proof that Praxis used validated experience.",
        kind="purple", icon="⬡"
    ), unsafe_allow_html=True)

    # Signature demo pair
    col1, col2 = st.columns(2)
    for col, s in zip([col1, col2], SCENARIOS[:2]):
        with col:
            _render_scenario_card(s, on_run)

    # Other scenarios
    st.markdown(section_label("ADDITIONAL SCENARIOS — ARCHITECTURAL COVERAGE"), unsafe_allow_html=True)

    for row_start in range(2, len(SCENARIOS), 2):
        row = SCENARIOS[row_start:row_start + 2]
        cols = st.columns(len(row))
        for col, s in zip(cols, row):
            with col:
                _render_scenario_card(s, on_run)

    # Architecture diagram (technical reference)
    st.markdown(section_label("PIPELINE ARCHITECTURE — For Technical Review"), unsafe_allow_html=True)
    st.markdown("""
<div class="prx-card">
  <div style="display:flex;align-items:center;gap:0;overflow-x:auto;padding:.5rem 0;">
    <div style="flex-shrink:0;text-align:center;padding:0 .75rem;">
      <div style="font-size:.875rem;font-weight:700;color:#0F1117;">C1</div>
      <div style="font-size:.625rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;">Data Foundation</div>
      <div style="font-size:.6875rem;color:#6B7280;margin-top:.25rem;">KPI contracts<br>Entitlements<br>Lineage</div>
    </div>
    <div style="color:#D1D5DB;font-size:1.25rem;padding:0 .25rem;">→</div>
    <div style="flex-shrink:0;text-align:center;padding:0 .75rem;">
      <div style="font-size:.875rem;font-weight:700;color:#0F1117;">C2</div>
      <div style="font-size:.625rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;">Statistical Investigation</div>
      <div style="font-size:.6875rem;color:#6B7280;margin-top:.25rem;">Baseline · Detection<br>Decomposition<br>Segmentation</div>
    </div>
    <div style="color:#D1D5DB;font-size:1.25rem;padding:0 .25rem;">→</div>
    <div style="flex-shrink:0;text-align:center;padding:0 .75rem;background:#F5F3FF;border-radius:6px;">
      <div style="font-size:.875rem;font-weight:700;color:#6B21A8;">C5 (hook)</div>
      <div style="font-size:.625rem;color:#6B7280;text-transform:uppercase;letter-spacing:.05em;">Memory Retrieval</div>
      <div style="font-size:.6875rem;color:#6B7280;margin-top:.25rem;">DuckDB gateway<br>Retrieve precedent<br>Compute memory_pts</div>
    </div>
    <div style="color:#D1D5DB;font-size:1.25rem;padding:0 .25rem;">→</div>
    <div style="flex-shrink:0;text-align:center;padding:0 .75rem;">
      <div style="font-size:.875rem;font-weight:700;color:#0F1117;">C3</div>
      <div style="font-size:.625rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;">Evidence & Reasoning</div>
      <div style="font-size:.6875rem;color:#6B7280;margin-top:.25rem;">Retrieval (BM25+emb)<br>Confidence (det.)<br>LLM: wording only</div>
    </div>
    <div style="color:#D1D5DB;font-size:1.25rem;padding:0 .25rem;">→</div>
    <div style="flex-shrink:0;text-align:center;padding:0 .75rem;">
      <div style="font-size:.875rem;font-weight:700;color:#0F1117;">C4</div>
      <div style="font-size:.625rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;">Decision Engine</div>
      <div style="font-size:.6875rem;color:#6B7280;margin-top:.25rem;">Lever catalogue<br>Rights matrix (det.)<br>LLM: narrative only</div>
    </div>
    <div style="color:#D1D5DB;font-size:1.25rem;padding:0 .25rem;">→</div>
    <div style="flex-shrink:0;text-align:center;padding:0 .75rem;background:#EFF6FF;border-radius:6px;">
      <div style="font-size:.875rem;font-weight:700;color:#1D4ED8;">C5 (admit)</div>
      <div style="font-size:.625rem;color:#6B7280;text-transform:uppercase;letter-spacing:.05em;">Memory Governance</div>
      <div style="font-size:.6875rem;color:#6B7280;margin-top:.25rem;">Gateway validation<br>Admission/quarantine<br>Supersession</div>
    </div>
    <div style="color:#D1D5DB;font-size:1.25rem;padding:0 .25rem;">→</div>
    <div style="flex-shrink:0;text-align:center;padding:0 .75rem;">
      <div style="font-size:.875rem;font-weight:700;color:#0F1117;">C6</div>
      <div style="font-size:.625rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;">UI / Experience</div>
      <div style="font-size:.6875rem;color:#6B7280;margin-top:.25rem;">Persona rendering<br>No recomputation<br>Canonical package only</div>
    </div>
  </div>
  <div style="margin-top:.875rem;font-size:.6875rem;color:#9CA3AF;border-top:1px solid #F3F4F6;padding-top:.625rem;">
    C2, C3 confidence, C4 lever selection — all deterministic. C3 claim wording, C4 narrative — LLM only. UI (C6) consumes canonical DecisionPackage; zero recomputation.
  </div>
</div>
""", unsafe_allow_html=True)


def _render_scenario_card(s: dict, on_run: Optional[Callable]):
    """Render a single scenario card with a run button."""
    sig_html = '<br><span class="prx-badge purple" style="margin-top:.375rem;">Signature Demo</span>' if s["signature"] else ""
    mem_html = '· Memory ON' if s["memory"] else '· Cold Start'

    st.markdown(f"""
<div class="prx-card" style="min-height:180px;">
  <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.375rem;">
    <span class="prx-badge {s['badge']}">{s['id'].upper().replace("_"," ")}</span>
    {("" if not s["memory"] else '<span class="prx-badge purple">Memory ON</span>')}
  </div>
  <div style="font-size:.9375rem;font-weight:700;color:#0F1117;margin-bottom:.25rem;">{s['label']}</div>
  <div style="font-size:.6875rem;color:#9CA3AF;margin-bottom:.5rem;">{s['tagline']}</div>
  <div style="font-size:.8125rem;color:#6B7280;line-height:1.5;margin-bottom:.625rem;">{s['what']}</div>
  <div style="font-size:.6875rem;color:#374151;background:#F9FAFB;border-radius:4px;padding:.375rem .625rem;">
    <b>Expected:</b> {s['expected']}
  </div>
  {sig_html}
</div>
""", unsafe_allow_html=True)

    if st.button(f"▶ Run {s['id'].upper()}", key=f"launch_{s['id']}", use_container_width=True,
                 type="primary" if s["signature"] else "secondary"):
        if on_run:
            on_run(s["id"], s["memory"])
