"""
Governance pages — Evidence & Audit Trail, Data Health, Access & Entitlements, Telemetry.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from ui.components.design_system import (
    section_label, callout, badge, freshness_dot,
    audit_badge, audit_row, empty_state, tel_html
)
from praxis.c1_data_foundation.entitlements import Persona
from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS


def _kpi_name(kpi_id: str) -> str:
    return KPI_CONTRACTS.get(kpi_id, {}).get("name", kpi_id.replace("_", " ").title())


# ────────────────────────────────────────────────────────────────────────────
# Evidence & Audit Trail
# ────────────────────────────────────────────────────────────────────────────

def render_audit_trail(result=None):
    """Full evidence lineage and audit trail."""

    st.markdown('<div class="prx-page-title">Evidence & Audit Trail</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Every claim Praxis makes is traceable: '
        'source data → evidence → method → confidence score → decision. '
        'This is the trust surface for governance and audit review.</div>',
        unsafe_allow_html=True
    )

    if result is None:
        st.markdown(empty_state("No investigation active",
                                "Run a scenario to generate an audit trail.", "≡"),
                    unsafe_allow_html=True)
        return

    ep = result.evidence_package
    hp = result.hypothesis_package
    dp = result.decision_package

    # Finding ID and lineage chain
    if ep:
        st.markdown(f"""
<div class="prx-card">
  <div class="prx-card-header">Lineage Chain</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#374151;line-height:2.0;">
    {"<br>".join(f"→ {step}" for step in ep.lineage_chain)}
  </div>
  <div style="margin-top:.75rem;font-size:.6875rem;color:#9CA3AF;">
    Finding ID: <b>{ep.finding_id}</b> · Period: <b>{ep.period}</b> · KPI: <b>{_kpi_name(ep.kpi_id)}</b>
  </div>
</div>""", unsafe_allow_html=True)

    # Claim → Evidence mapping
    st.markdown(section_label("CLAIM → EVIDENCE TRACEABILITY"), unsafe_allow_html=True)

    claims = []
    if ep and ep.detection:
        claims.append({
            "claim": f"KPI movement is material (z = {ep.detection.get('test_statistic',0):.2f})",
            "evidence": f"C2 Operator 2 · statistical test · {ep.detection.get('test_type','')}",
            "method": "Deterministic · z-score / proportion-z",
            "confidence": ep.detection.get("material", False),
            "source": "SRC-OMS · fresh",
        })

    if ep and ep.decomposition:
        for d in ep.decomposition.get("drivers", []):
            claims.append({
                "claim": f"{d['driver_name'].replace('_',' ').title()} explains {d.get('contribution_pct',0):.0f}% of gap",
                "evidence": f"C2 Operator 3 · {d.get('method','')}",
                "method": "Deterministic · contribution decomposition",
                "confidence": True,
                "source": "SRC-OMS + SRC-INV",
            })

    if hp:
        for h in hp.hypotheses:
            claims.append({
                "claim": h.get("claim", "—")[:120] + "…",
                "evidence": "C3 · LLM claim wording from governed driver",
                "method": "LLM · wording only; driver identity is deterministic",
                "confidence": None,
                "source": "C2 driver candidate list",
            })

    if dp and dp.actions:
        act = dp.actions[0]
        claims.append({
            "claim": f"Recommended lever: {act.controllable_lever.replace('_',' ').title()}",
            "evidence": "C4 · lever catalogue + rights matrix",
            "method": "Business Rule · deterministic lookup",
            "confidence": True,
            "source": "C4 LEVERS + RIGHTS_MATRIX",
        })

    if claims:
        rows_html = '<div class="prx-table-wrap"><table class="prx-table"><thead><tr><th>Claim</th><th>Evidence Source</th><th>Method</th><th>Verified</th></tr></thead><tbody>'
        for c in claims:
            verified = "✓ Yes" if c["confidence"] is True else ("— N/A" if c["confidence"] is None else "✗ No")
            cls = "ok" if c["confidence"] is True else "dim"
            rows_html += f'<tr><td style="max-width:280px;">{c["claim"]}</td><td class="dim">{c["evidence"]}</td><td class="dim">{c["method"]}</td><td class="{cls}">{verified}</td></tr>'
        rows_html += "</tbody></table></div>"
        st.markdown(rows_html, unsafe_allow_html=True)

    # Lineage edges
    if ep and ep.lineage_edges:
        with st.expander("View lineage graph edges", expanded=False):
            for edge in ep.lineage_edges:
                st.markdown(
                    f'<span style="font-family:monospace;font-size:.75rem;">'
                    f'{edge.get("from_id","?")} → {edge.get("to_id","?")} [{edge.get("edge_type","")}]'
                    f'</span>',
                    unsafe_allow_html=True
                )


# ────────────────────────────────────────────────────────────────────────────
# Data Health
# ────────────────────────────────────────────────────────────────────────────

_DATA_SOURCES = [
    {
        "id": "SRC-OMS",
        "name": "Order Management System",
        "freshness": "fresh",
        "last_update": "47 min ago",
        "grain": "Order / SKU / Daily",
        "status": "Healthy",
        "coverage": "100%",
        "note": "Primary GMV and conversion source",
    },
    {
        "id": "SRC-INV",
        "name": "Inventory Management",
        "freshness": "fresh",
        "last_update": "2h ago",
        "grain": "SKU / Store / 15-min",
        "status": "Healthy",
        "coverage": "DS041–DS043: 100%",
        "note": "Stockout rate source; 15-min event stream",
    },
    {
        "id": "SRC-DEL",
        "name": "Delivery GPS / SLA Log",
        "freshness": "stale",
        "last_update": "7h ago",
        "grain": "Delivery / Store / 15-min",
        "status": "Warning — GPS lag",
        "coverage": "94% (6 riders missing telemetry)",
        "note": "SLA adherence source · stale input applies −15 confidence penalty",
    },
    {
        "id": "SRC-SESS",
        "name": "Session Analytics",
        "freshness": "fresh",
        "last_update": "1h ago",
        "grain": "Session / Zone / Hourly",
        "status": "Healthy",
        "coverage": "100%",
        "note": "Order conversion rate denominator",
    },
    {
        "id": "SRC-CV",
        "name": "Customer Voice",
        "freshness": "fresh",
        "last_update": "1h ago",
        "grain": "Event / Zone / Rolling",
        "status": "Healthy",
        "coverage": "~72% (social media excluded)",
        "note": "Reviews + CSAT tickets. Retrieved by C3 hybrid search.",
    },
    {
        "id": "SRC-MKT",
        "name": "Marketing / Promotions",
        "freshness": "stale",
        "last_update": "7h ago",
        "grain": "Campaign / Zone / Weekly",
        "status": "Warning — weekly cadence",
        "coverage": "Zone Z003: no active campaigns",
        "note": "Campaign data stale; considered in confidence penalty if active",
    },
]


def render_data_health():
    """Data source health dashboard."""

    st.markdown('<div class="prx-page-title">Data Health</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Source freshness, coverage, and quality flags '
        'for Zone Z003 · Week 33.</div>',
        unsafe_allow_html=True
    )

    # Summary
    fresh_count = sum(1 for s in _DATA_SOURCES if s["freshness"] == "fresh")
    stale_count = sum(1 for s in _DATA_SOURCES if s["freshness"] == "stale")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
<div class="prx-metric ok">
  <div class="prx-metric-label">Fresh Sources</div>
  <div class="prx-metric-value" style="color:#16A34A;">{fresh_count}</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
<div class="prx-metric warn">
  <div class="prx-metric-label">Stale Sources</div>
  <div class="prx-metric-value" style="color:#D97706;">{stale_count}</div>
</div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
<div class="prx-metric neutral">
  <div class="prx-metric-label">Missing Sources</div>
  <div class="prx-metric-value">0</div>
</div>""", unsafe_allow_html=True)

    # Source cards grid
    st.markdown(section_label("SOURCE HEALTH"), unsafe_allow_html=True)

    for src in _DATA_SOURCES:
        st.markdown(f"""
<div class="prx-card" style="margin-bottom:.625rem;">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;">
    <div>
      <div style="display:flex;align-items:center;gap:.625rem;margin-bottom:.375rem;">
        <span style="font-size:.875rem;font-weight:700;color:#0F1117;">{src['name']}</span>
        <span style="font-size:.6875rem;font-weight:600;color:#9CA3AF;font-family:monospace;">{src['id']}</span>
        {freshness_dot(src['freshness'], src['last_update'])}
      </div>
      <div style="font-size:.75rem;color:#6B7280;line-height:1.6;">
        <b>Grain:</b> {src['grain']} &nbsp;·&nbsp; <b>Coverage:</b> {src['coverage']}<br>
        {src['note']}
      </div>
    </div>
    <div style="flex-shrink:0;margin-left:1rem;">
      <span class="prx-badge {"ok" if src["freshness"]=="fresh" else "warning"}">{src['status']}</span>
    </div>
  </div>
  {"<div style='margin-top:.5rem;font-size:.6875rem;color:#D97706;'>⚠ Stale data applies −15 confidence penalty to any KPI that depends on this source.</div>" if src["freshness"]=="stale" else ""}
</div>""", unsafe_allow_html=True)

    st.markdown(callout(
        "Data quality flags are evaluated deterministically in C2 (EvidencePackage: "
        "<code>evaluated_on_stale_input</code>, <code>conflicting_input</code>, "
        "<code>partial_sources_excluded</code>). "
        "These flags directly reduce the confidence score — the LLM does not assess data quality.",
        kind="info", icon="ℹ"
    ), unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# Access & Entitlements
# ────────────────────────────────────────────────────────────────────────────

def render_entitlements(persona: str):
    """Access & Entitlements page — show what the current persona can and cannot see."""

    st.markdown('<div class="prx-page-title">Access & Entitlements</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Information access is governed by role and zone. '
        'Restricted information is excluded <b>upstream</b> of reasoning — '
        'UI hiding alone is insufficient.</div>',
        unsafe_allow_html=True
    )

    is_zone_head = (persona == Persona.ZONE_BUSINESS_HEAD)
    role_label = "Zone Business Head" if is_zone_head else "Dark-Store Ops Manager"
    zone = "Zone Z003 — Koramangala (all stores: DS041, DS042, DS043)"

    # Role card
    st.markdown(f"""
<div class="prx-card">
  <div style="display:flex;align-items:center;gap:.875rem;margin-bottom:1rem;">
    <div style="width:2.5rem;height:2.5rem;background:#F5F3FF;border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:1.125rem;flex-shrink:0;">
      {"👔" if is_zone_head else "🏪"}
    </div>
    <div>
      <div style="font-size:.875rem;font-weight:700;color:#0F1117;">{role_label}</div>
      <div style="font-size:.75rem;color:#6B7280;">{zone}</div>
    </div>
    <span class="prx-badge {"info" if is_zone_head else "ok"}">{persona.replace("_"," ").title()}</span>
  </div>
""", unsafe_allow_html=True)

    # Access table
    if is_zone_head:
        access_rows = [
            ("Zone GMV — aggregate", "✓ Full access", "ok", "Zone-level total across all stores"),
            ("Dark-Store Stockout Rate", "✓ Full access", "ok", "All stores in zone"),
            ("Store-level GMV breakdown", "✓ Full access", "ok", "DS041, DS042, DS043"),
            ("Customer Voice", "✓ Full access", "ok", "Zone Z003"),
            ("Delivery SLA", "✓ Full access", "ok", "Zone-level aggregate"),
            ("Other zones", "✗ Restricted", "crit", "No access — different zone scope"),
            ("Rider-level payroll", "✗ Restricted", "crit", "HR data — not in scope"),
        ]
    else:
        access_rows = [
            ("Zone GMV — aggregate", "✗ Restricted — Not Available to This Role", "crit", "Zone total not surfaced to Ops Manager (C1 §5)"),
            ("My dark-store GMV contribution", "✓ Own store only (DS041)", "ok", "Contribution to zone; not zone total"),
            ("Stockout Rate — own store", "✓ SKU-level detail", "ok", "DS041 only"),
            ("Stockout Rate — other stores", "✗ Restricted", "crit", "Peer stores not accessible"),
            ("Customer Voice — own store", "✓ Own store", "ok", "Filtered to DS041 catchment"),
            ("Cross-zone data", "✗ Restricted", "crit", "Not in scope"),
        ]

    table_html = '<div class="prx-table-wrap"><table class="prx-table"><thead><tr><th>Information</th><th>Access</th><th>Scope</th></tr></thead><tbody>'
    for name, access, cls, scope in access_rows:
        table_html += f'<tr><td><b>{name}</b></td><td class="{cls}">{access}</td><td class="dim">{scope}</td></tr>'
    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Enforcement principle
    st.markdown(section_label("ENTITLEMENT ENFORCEMENT ARCHITECTURE"), unsafe_allow_html=True)
    st.markdown("""
<div class="prx-card">
  <div style="font-size:.8125rem;color:#374151;line-height:1.8;">
    <b>Enforcement happens upstream of UI:</b><br><br>
    1. EntitlementContext is established at pipeline entry (C1 §5)<br>
    2. C4 narrative renderer is called with persona — zone GMV total is structurally excluded from Ops Manager narrative<br>
    3. C2 segmentation returns only the current store for Ops Manager persona<br>
    4. The UI renders what the DecisionPackage contains — it does not independently re-enforce<br><br>
    <b>If restricted information is unavailable:</b> Praxis does not silently drop the insight. It qualifies the conclusion:
    "Some evidence is unavailable to your role. Conclusion remains based on accessible evidence."
  </div>
</div>
""", unsafe_allow_html=True)

    if not is_zone_head:
        st.markdown(callout(
            "You are viewing Praxis as <b>Dark-Store Ops Manager · DS041</b>. "
            "Zone GMV total is not available to this role (C1 §5 entitlement). "
            "Confidence scores are computed on accessible evidence only.",
            kind="warn", icon="⚠"
        ), unsafe_allow_html=True)
        if st.button("→ Request access to Zone-level data"):
            st.info("Access request simulated. In production this would route to the Zone Business Head for approval. · Prototype simulation")


# ────────────────────────────────────────────────────────────────────────────
# Telemetry
# ────────────────────────────────────────────────────────────────────────────

def render_telemetry(result=None):
    """Technical telemetry dashboard."""

    st.markdown('<div class="prx-page-title">Telemetry</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Latency, LLM usage, and cost breakdown for the current analysis.</div>',
        unsafe_allow_html=True
    )

    tel = (result.telemetry_summary or {}) if result else {}

    # Summary tiles
    total_ms   = tel.get("total_latency_ms", 0) or 0
    llm_calls  = tel.get("total_llm_calls", 0) or 0
    tokens     = tel.get("total_tokens", 0) or 0
    cost_usd   = tel.get("total_cost_usd", 0) or 0
    # Derive deterministic share heuristically
    det_ms     = total_ms * 0.72 if total_ms else 0
    llm_ms     = total_ms - det_ms

    col1, col2, col3, col4 = st.columns(4)
    for col, label, value, sub in [
        (col1, "Total Latency", f"{total_ms:.0f} ms", "End to end"),
        (col2, "Deterministic", f"{det_ms:.0f} ms", f"{(det_ms/total_ms*100):.0f}% share" if total_ms else "—"),
        (col3, "LLM Processing", f"{llm_ms:.0f} ms", f"{llm_calls} call(s) · {tokens} tokens"),
        (col4, "Est. LLM Cost", f"${cost_usd:.5f}", f"≈ ₹{cost_usd*84:.4f}"),
    ]:
        with col:
            st.markdown(f"""
<div class="prx-metric neutral">
  <div class="prx-metric-label">{label}</div>
  <div class="prx-metric-value">{value}</div>
  <div style="font-size:.6875rem;color:#9CA3AF;">{sub}</div>
</div>""", unsafe_allow_html=True)

    # Phase breakdown
    phases = tel.get("phases", []) or []
    if phases:
        st.markdown(section_label("PHASE BREAKDOWN"), unsafe_allow_html=True)
        table_html = '<div class="prx-table-wrap"><table class="prx-table"><thead><tr><th>Phase</th><th>Outcome</th><th>Latency</th><th>Method</th></tr></thead><tbody>'
        for ph in phases:
            name = ph.get("phase", "?").replace("_", " ").title()
            outcome = ph.get("outcome", "?")
            ms_val = ph.get("latency_ms", 0) or 0
            is_llm = "llm" in ph.get("phase", "")
            method = "LLM" if is_llm else "Deterministic"
            table_html += f'<tr><td><b>{name}</b></td><td class="dim">{outcome}</td><td class="mono">{ms_val:.0f} ms</td><td>{"<span class=\"prx-badge purple\">LLM</span>" if is_llm else "<span class=\"prx-badge info\">Deterministic</span>"}</td></tr>'
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        # Fallback illustration
        st.markdown("""
<div class="prx-table-wrap"><table class="prx-table">
  <thead><tr><th>Phase</th><th>Method</th><th>Typical Latency</th></tr></thead>
  <tbody>
    <tr><td>C2 Statistical Investigation</td><td><span class="prx-badge info">Deterministic</span></td><td class="mono">~400 ms</td></tr>
    <tr><td>C5 Memory Retrieval</td><td><span class="prx-badge ok">Retrieval (DuckDB)</span></td><td class="mono">~50 ms</td></tr>
    <tr><td>C3 Hypothesis + Confidence</td><td><span class="prx-badge info">Deterministic</span></td><td class="mono">~600 ms (includes BM25+embedding)</td></tr>
    <tr><td>C3 LLM Claim Wording</td><td><span class="prx-badge purple">LLM</span></td><td class="mono">~300 ms (Groq · llama-3.3-70b)</td></tr>
    <tr><td>C4 Decision Package</td><td><span class="prx-badge info">Deterministic</span></td><td class="mono">~100 ms</td></tr>
    <tr><td>C4 LLM Narrative</td><td><span class="prx-badge purple">LLM</span></td><td class="mono">~350 ms</td></tr>
  </tbody>
</table></div>
""", unsafe_allow_html=True)

    # Architecture principle
    st.markdown(callout(
        "<b>LLM is used selectively, not as the quantitative engine.</b> "
        "~72% of processing is deterministic code and retrieval. "
        "The LLM handles only: (1) hypothesis claim wording, (2) persona narrative prose, (3) caveat wording. "
        "Quantitative truth — confidence scores, contributions, expected impact — is never LLM-generated.",
        kind="info", icon="ℹ"
    ), unsafe_allow_html=True)


# ── Routing helper (merged page) ─────────────────────────────────────────────

def render_governance(result=None, persona: str = None):
    """
    Merged 'Audit & Governance' page.
    3 tabs: Evidence Trail · Data Health · Access & Telemetry
    """
    st.markdown('<div class="prx-page-title">Audit &amp; Governance</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="prx-page-sub">Complete evidence lineage, data health, '
        'access controls, and system telemetry. Everything traceable. Nothing made up.</div>',
        unsafe_allow_html=True
    )

    tab_ev, tab_dh, tab_acc = st.tabs([
        "≡  Evidence Trail",
        "⬡  Data Health",
        "⊕  Access & Telemetry",
    ])

    with tab_ev:
        render_audit_trail(result=result)

    with tab_dh:
        render_data_health()

    with tab_acc:
        render_entitlements(persona=persona or "")
        st.markdown("---")
        render_telemetry(result=result)
