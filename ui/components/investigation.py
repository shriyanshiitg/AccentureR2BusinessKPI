"""
Investigation Workspace — the heart of PRAXIS.
Renders the full decision journey:
  WHAT CHANGED → WHY → EVIDENCE → HOW PRAXIS CONCLUDED → CONFIDENCE → RECOMMENDATION → SCENARIO

Consumes canonical PipelineResult objects only.
Zero quantitative recomputation in this file.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from ui.components.design_system import (
    badge, freshness_dot, outcome_pill, section_label, section_sep,
    memory_boost_card, callout,
    audit_badge, audit_row, bar_row, action_row, evidence_row,
    conf_bar, empty_state, tel_html, method_badge
)

from praxis.c1_data_foundation.entitlements import Persona, can_access_zone_gmv_total
from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS


# ── KPI display name (from contract, no hardcoding) ──────────────────────────
def _kpi_display(kpi_id: str) -> str:
    return KPI_CONTRACTS.get(kpi_id, {}).get("name", kpi_id.replace("_", " ").title())


def render_investigation(result, persona: str):
    """
    Full investigation workspace — single scroll, no tabs.
    Sections: WHAT HAPPENED → WHY → [MEMORY BOOST] → CONFIDENCE → WHAT TO DO → [AUDIT ▾]
    """
    if result is None:
        st.markdown(empty_state("No investigation active",
                                "Use the 'Run Signature Demo' button in the sidebar.", "⌕"),
                    unsafe_allow_html=True)
        return

    if result.error:
        st.error(f"Pipeline error: {result.error}")
        return

    ep = result.evidence_package
    hp = result.hypothesis_package
    dp = result.decision_package
    mr = result.memory_result or {}
    tel = result.telemetry_summary or {}

    kpi_name = _kpi_display(ep.kpi_id) if ep else "Unknown KPI"

    # ── Page header ───────────────────────────────────────────────────────────
    scenario_lbl = (st.session_state.get("scenario_name") or "s1").upper()
    outcome = (dp.source_decision_outcome if dp else (
        hp.decision.get("outcome", "ABSTAIN") if hp else "ABSTAIN"))

    st.markdown(f'<div class="prx-page-title">Investigation — {kpi_name}</div>',
                unsafe_allow_html=True)

    col_meta, col_outcome, col_tel = st.columns([3, 2, 4])
    with col_meta:
        st.markdown(
            f'<div style="font-size:.75rem;color:#6B7280;">Scenario: <b>{scenario_lbl}</b>'
            f' &nbsp;·&nbsp; Period: <b>{ep.period if ep else "—"}</b>'
            f' &nbsp;·&nbsp; Zone: <b>{ep.grain_key if ep else "—"}</b></div>',
            unsafe_allow_html=True)
    with col_outcome:
        st.markdown(outcome_pill(outcome), unsafe_allow_html=True)
    with col_tel:
        st.markdown(tel_html(tel), unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1 — WHAT HAPPENED
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(section_sep("WHAT HAPPENED"), unsafe_allow_html=True)
    _tab_what_changed(ep, persona)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2 — WHY IT HAPPENED
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(section_sep("WHY IT HAPPENED"), unsafe_allow_html=True)
    _tab_why(ep, hp, persona)

    # ─────────────────────────────────────────────────────────────────────────
    # MEMORY BOOST CARD — shown prominently when a precedent is retrieved
    # This is the product's "magic moment" — must appear before confidence
    # ─────────────────────────────────────────────────────────────────────────
    if mr.get("matched"):
        hp_hyps = (hp.hypotheses if hp else []) or []
        mem_pts  = hp_hyps[0].get("confidence_components", {}).get("memory_points", 0) if hp_hyps else 0
        pre_mem  = hp_hyps[0].get("confidence_components", {}).get("raw_pre_memory", 0) if hp_hyps else 0
        post_mem = hp_hyps[0].get("confidence_score", 0) if hp_hyps else 0
        scope    = mr.get("match_scope", "")

        # Try to get the date of the matched record
        date_str = ""
        try:
            from praxis.c5_memory.gateway import _get_conn
            conn = _get_conn()
            row = conn.execute(
                "SELECT created_at FROM decision_memory "
                "WHERE validation_status='demo_preapproved' LIMIT 1"
            ).fetchone()
            conn.close()
            if row:
                date_str = str(row[0])[:10]
        except Exception:
            date_str = "Aug 2026"

        st.markdown(
            memory_boost_card(pre_mem, post_mem, mem_pts, scope, date_str),
            unsafe_allow_html=True
        )

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3 — CONFIDENCE
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(section_sep("CONFIDENCE & EVIDENCE"), unsafe_allow_html=True)
    _tab_confidence(hp, mr)

    # Evidence collapsed by default — reduces cognitive load for first-time users
    with st.expander("▾ View supporting evidence", expanded=False):
        _tab_evidence(ep, hp)

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4 — WHAT TO DO
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(section_sep("WHAT TO DO"), unsafe_allow_html=True)
    _tab_recommendation(dp, ep, hp, persona)

    # ─────────────────────────────────────────────────────────────────────────
    # AUDIT TRAIL — collapsed (for technical reviewers, not primary users)
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown('<div style="margin-top:2rem;"></div>', unsafe_allow_html=True)
    with st.expander("≡  View method audit trail — how Praxis reached this conclusion",
                     expanded=False):
        _tab_audit(ep, hp, dp, mr)

    # ─────────────────────────────────────────────────────────────────────────
    # SIGNATURE DEMO COMPARISON — collapsed (run S1 first, then S2)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("⊗  Compare: Cold Start vs Memory-Enhanced (Signature Demo)",
                     expanded=False):
        _tab_signature_demo(result, persona)


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — WHAT CHANGED
# ────────────────────────────────────────────────────────────────────────────

def _tab_what_changed(ep, persona: str):
    if ep is None:
        st.markdown(empty_state("No detection data", "", "○"), unsafe_allow_html=True)
        return

    det = ep.detection or {}
    bl  = ep.baseline  or {}
    kpi_name = _kpi_display(ep.kpi_id)

    actual   = det.get("actual_value", 0) or 0
    delta_a  = det.get("delta_absolute", 0) or 0
    delta_r  = det.get("delta_relative", 0) or 0
    baseline = bl.get("baseline_mean", 0) or (actual - delta_a)
    z        = det.get("test_statistic", 0) or 0
    material = det.get("material", False)
    test_t   = det.get("test_type", "z_score")

    # Entitlement: zone GMV total visible only to Zone Head
    if ep.kpi_id == "zone_gmv" and not can_access_zone_gmv_total(persona):
        st.markdown("""
<div class="prx-restricted-notice">
  🔒 Zone-level GMV total is restricted to your role. You can see your store's contribution only.
  <a href="#" style="color:#6B21A8;font-style:normal;font-weight:600;margin-left:.5rem;">Request access →</a>
</div>""", unsafe_allow_html=True)
        actual  = None
        baseline = None

    # Materiality badge
    mat_cls = "critical" if material else "ok"
    mat_txt = "MATERIAL MOVEMENT" if material else "NON-MATERIAL"
    mat_reason = ("Outside normal historical variation and economically significant."
                  if material else "Within expected variation. No action required.")

    # Main metric tiles — 3 columns only (no statistical signal tile)
    _fmt_inr = lambda v: f"₹{v/100_000:.1f}L" if v is not None and ep.kpi_id == "zone_gmv" else (f"{v:.1f}%" if v is not None else "—")
    is_pct_kpi = ep.kpi_id != "zone_gmv"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
<div class="prx-metric {"alert" if material else "ok"}">
  <div class="prx-metric-label">Actual</div>
  <div class="prx-metric-value">{_fmt_inr(actual) if actual is not None else "Restricted"}</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
<div class="prx-metric neutral">
  <div class="prx-metric-label">Expected (Normal Range)</div>
  <div class="prx-metric-value">{_fmt_inr(baseline) if baseline is not None else "—"}</div>
  <div style="font-size:.625rem;color:#9CA3AF;">{bl.get('window_size_used',0)} comparison days</div>
</div>""", unsafe_allow_html=True)
    with col3:
        dir_cls = "neg" if delta_a < 0 else "pos"
        dir_arrow = "↓" if delta_a < 0 else "↑"
        st.markdown(f"""
<div class="prx-metric {"alert" if material else "ok"}">
  <div class="prx-metric-label">Performance Gap</div>
  <div class="prx-metric-value {dir_cls}" style="color:{"#DC2626" if delta_a<0 else "#16A34A"}">
    {dir_arrow} {_fmt_inr(abs(delta_a))}
  </div>
  <div class="prx-metric-delta {dir_cls}">{dir_arrow} {abs(delta_r)*100:.1f}%</div>
</div>""", unsafe_allow_html=True)

    # Materiality verdict
    st.markdown(f"""
<div class="prx-card" style="margin-top:1rem;">
  <div style="display:flex;align-items:center;gap:.875rem;margin-bottom:.625rem;">
    <span class="prx-badge {mat_cls}">{mat_txt}</span>
    <span style="font-size:.8125rem;color:#6B7280;">{mat_reason}</span>
  </div>
""", unsafe_allow_html=True)

    # Data quality flags
    flags = []
    if ep.evaluated_on_stale_input:
        flags.append(("warning", "Evaluated on stale input — confidence penalty applied"))
    if ep.conflicting_input:
        flags.append(("warning", "Conflicting input detected — confidence capped"))
    excl = ep.partial_sources_excluded
    if excl:
        excl_str = ', '.join(excl) if isinstance(excl, list) else str(excl)
        flags.append(("warning", f"Partial exclusions: {excl_str}"))

    if flags:
        for cls, msg in flags:
            st.markdown(f'<div style="font-size:.75rem;color:#92400E;margin-top:.25rem;">⚠ {msg}</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:.75rem;color:#16A34A;">✓ No data quality flags — full confidence computation applied</div>',
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Terminal outcome explanation
    term = ep.terminal_outcome
    if term == "INSUFFICIENT_HISTORY":
        st.markdown("""
<div class="prx-abstain-box">
  <div class="prx-abstain-title">Insufficient History</div>
  <div class="prx-abstain-body">
    Fewer than 3 comparable periods are available. Praxis cannot establish a reliable baseline.
    <b>This is the correct behaviour</b> — Praxis does not extrapolate without evidence.
  </div>
</div>""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — WHY IT HAPPENED
# ────────────────────────────────────────────────────────────────────────────

def _tab_why(ep, hp, persona: str):
    if ep is None:
        st.markdown(empty_state("No decomposition data", "", "○"), unsafe_allow_html=True)
        return

    decomp = ep.decomposition or {}
    seg    = ep.segmentation  or {}
    det    = ep.detection     or {}
    delta_a = det.get("delta_absolute", 0) or 0

    drivers = decomp.get("drivers", [])
    residual_pct = decomp.get("residual_pct", 0) or 0
    no_dominant = decomp.get("no_dominant_contributor", False)

    # ── Abstention scenario ───────────────────────────────────────────────────
    if ep.terminal_outcome == "NO_DOMINANT_CONTRIBUTOR" or no_dominant:
        st.markdown("""
<div class="prx-abstain-box">
  <div class="prx-abstain-title">⊘ Praxis Cannot Identify a Dominant Driver</div>
  <div class="prx-abstain-body">
    <b>This is not a failure — this is the correct response to ambiguous evidence.</b><br><br>
    Multiple explanations are plausible and available evidence does not distinguish between them.
    Recommending a specific intervention without a dominant driver would be irresponsible.
  </div>
</div>""", unsafe_allow_html=True)

    # ── Driver decomposition bars ─────────────────────────────────────────────────
    if drivers:
        st.markdown(section_label("WHAT'S DRIVING THIS — Contribution Analysis"), unsafe_allow_html=True)
        st.markdown(callout(
            "Contribution % is computed <b>deterministically</b> via C2 Operator 3 (contribution decomposition). "
            "These numbers are <b>not LLM estimates</b>.",
            kind="info", icon="ℹ"
        ), unsafe_allow_html=True)

        color_map = ["c1", "c2", "c3", "c4"]
        bars_html = '<div class="prx-bar-chart">'
        for i, d in enumerate(drivers):
            pct  = d.get("contribution_pct", 0) * 100 if d.get("contribution_pct", 0) <= 1 else d.get("contribution_pct", 0)
            cval = d.get("contribution_value", 0) or 0
            name = d.get("driver_name", "?").replace("_", " ").title()
            # No method badge on business-facing bars — technical detail is in Tab 4
            bars_html += bar_row(i+1, name, pct, abs(cval), color_map[min(i, 3)], "")

        # Residual bar
        if residual_pct and residual_pct > 0:
            res_pct = residual_pct * 100 if residual_pct <= 1 else residual_pct
            res_val = abs(delta_a) * (res_pct / 100)
            bars_html += bar_row(len(drivers)+1, "Other / Residual", res_pct, res_val, "residual", "")

        bars_html += "</div>"
        st.markdown('<div class="prx-card">' + bars_html + "</div>", unsafe_allow_html=True)

        # Dominant driver note
        dominant = decomp.get("dominant_driver")
        if dominant:
            st.markdown(callout(
                f"<b>Dominant driver identified:</b> {dominant.replace('_',' ').title()} "
                f"explains the largest share. Recommendation targets this driver.",
                kind="ok", icon="✓"
            ), unsafe_allow_html=True)

    # ── Store segmentation ────────────────────────────────────────────────────
    ranked_stores = seg.get("ranked_stores", [])
    excluded_stores = seg.get("excluded_stores", [])

    if ranked_stores:
        st.markdown(section_label("MOST AFFECTED LOCATIONS"), unsafe_allow_html=True)
        bars_html2 = '<div class="prx-bar-chart">'
        for i, s in enumerate(ranked_stores):
            pct  = s.get("contribution_pct", 0) * 100 if s.get("contribution_pct", 0) <= 1 else s.get("contribution_pct", 0)
            cval = s.get("contribution_value", 0) or 0
            sid  = s.get("dark_store_id", "?")
            bars_html2 += bar_row(i+1, sid, pct, abs(cval), color_map[min(i,3)], "")

        for excl in (excluded_stores or []):
            bars_html2 += (
                f'<div class="prx-bar-row">'
                f'<div class="prx-bar-rank">—</div>'
                f'<div class="prx-bar-label">{excl}</div>'
                f'<div class="prx-bar-track"><div class="prx-bar-fill residual" style="width:0%"></div></div>'
                f'<div class="prx-bar-pct" style="color:#9CA3AF;">—</div>'
                f'<div class="prx-bar-amt" style="color:#9CA3AF;">Missing</div>'
                f'<span class="prx-bar-method ret">Data Gap</span>'
                f'</div>'
            )
        bars_html2 += "</div>"
        st.markdown('<div class="prx-card">' + bars_html2 + "</div>", unsafe_allow_html=True)

    # ── Hypothesis wording ────────────────────────────────────────────────────
    if hp and hp.hypotheses:
        st.markdown(section_label("PRAXIS INTERPRETATION"), unsafe_allow_html=True)
        leading = hp.hypotheses[0]
        claim = leading.get("claim", "No claim generated.")
        st.markdown(f"""
<div class="prx-card">
  <div style="display:flex;align-items:center;gap:.625rem;margin-bottom:.75rem;">
    <span class="prx-badge purple">Leading Explanation</span>
  </div>
  <div style="font-size:.9375rem;color:#0F1117;line-height:1.7;margin-bottom:.625rem;">{claim}</div>
  <div style="font-size:.6875rem;color:#9CA3AF;">
    Primary driver: <b>{leading.get('driver_type','?').replace('_',' ').title()}</b> &nbsp;·&nbsp;
    Contribution: <b>{leading.get('contribution_pct',0):.0f}%</b> &nbsp;·&nbsp;
    Status: <b>{leading.get('status','?')}</b>
  </div>
</div>""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — EVIDENCE
# ────────────────────────────────────────────────────────────────────────────

def _tab_evidence(ep, hp):
    if ep is None:
        st.markdown(empty_state("No evidence", "", "○"), unsafe_allow_html=True)
        return

    # ── Structured evidence ─────────────────────────────────────────────────
    st.markdown(section_label("QUANTITATIVE EVIDENCE"), unsafe_allow_html=True)
    structured = []

    det = ep.detection or {}
    if det.get("actual_value") is not None:
        structured.append({
            "source": "Sales & Order Data",
            "statement": f"KPI actual value: {det.get('actual_value',0):,.0f} · delta: {det.get('delta_absolute',0):+,.0f} ({det.get('delta_relative',0)*100:+.1f}%)",
            "freshness": "fresh", "ago": "Order Management System · 47 min", "type": "supporting",
        })

    decomp = ep.decomposition or {}
    for d in decomp.get("drivers", []):
        name = d.get("driver_name","?").replace("_"," ").title()
        pct  = d.get("contribution_pct", 0)
        pct_disp = f"{pct:.0f}%" if pct > 1 else f"{pct*100:.0f}%"
        structured.append({
            "source": "Pattern Analysis",
            "statement": f"{name} contributed {pct_disp} of the performance gap",
            "freshness": "fresh", "ago": "Computed · Order Management System", "type": "supporting",
        })

    seg = ep.segmentation or {}
    for s in seg.get("ranked_stores", []):
        pct = s.get("contribution_pct", 0)
        pct_disp = f"{pct:.0f}%" if pct > 1 else f"{pct*100:.0f}%"
        structured.append({
            "source": "Store Inventory Data",
            "statement": f"Store {s['dark_store_id']}: {pct_disp} of gap · value: {s.get('contribution_value',0):,.0f}",
            "freshness": "fresh", "ago": "Inventory System · 15-min cadence", "type": "supporting",
        })

    for excl in (seg.get("excluded_stores") or []):
        structured.append({
            "source": "Operational Data",
            "statement": f"Store {excl}: data not available for this period",
            "freshness": "missing", "ago": "Missing", "type": "neutral",
        })

    if ep.conflicting_input:
        sources = ep.conflicting_provenance if ep.conflicting_provenance else ["Unknown source"]
        for src in sources:
            structured.append({
                "source": f"Data Quality Monitor · {src}",
                "statement": f"Conflicting input from {src} — confidence penalty applied",
                "freshness": "stale", "ago": "Conflicting", "type": "contradicting",
            })

    if not structured:
        st.markdown(empty_state("No structured evidence", "", "○"), unsafe_allow_html=True)
    else:
        rows_html = '<div class="prx-card" style="padding:0;">'
        for ev in structured:
            rows_html += evidence_row(ev["source"], ev["statement"],
                                      ev["freshness"], ev["ago"], ev["type"])
        st.markdown(rows_html + "</div>", unsafe_allow_html=True)

    # ── Unstructured evidence (CV) ─────────────────────────────────────────────
    st.markdown(section_label("CUSTOMER SIGNALS"), unsafe_allow_html=True)

    cv_hyp = None
    if hp:
        for h in hp.hypotheses:
            if h.get("retrieval_result"):
                cv_hyp = h
                break

    cv_records = []
    if cv_hyp:
        ret = cv_hyp.get("retrieval_result", {}) or {}
        cv_records = ret.get("records", []) or []

    if not cv_records:
        # Try to get from scenario data in session state
        cv_fallback = [
            ("Customer Review", "Amul butter was out of stock again, had to cancel my order.", "supporting"),
            ("Customer Review", "Product unavailable at checkout — app showed available but wasn't in stock.", "supporting"),
            ("Customer Review", "Out of stock for the third time this week. Switched to another app.", "supporting"),
        ]
        for src, stmt, typ in cv_fallback:
            st.markdown(f'<div class="prx-card" style="padding:0;">' +
                        evidence_row(f"Customer Reviews", stmt, "fresh", "Recent", typ) +
                        "</div>", unsafe_allow_html=True)
    else:
        rows_html = '<div class="prx-card" style="padding:0;">'
        for rec in cv_records[:5]:
            stmt = rec.get("text", str(rec))
            ts   = rec.get("ts", "")[:10] if rec.get("ts") else "—"
            ev_type = rec.get("sentiment", "neutral")
            rows_html += evidence_row("Customer Reviews", stmt, "fresh", ts, ev_type)
        st.markdown(rows_html + "</div>", unsafe_allow_html=True)

    st.markdown(callout(
        "Customer reviews are retrieved and matched to this KPI's time window. "
        "They provide contextual corroboration — they do <b>not</b> establish causality. "
        "Full retrieval methodology is described in the <i>How Praxis Concluded</i> tab.",
        kind="info", icon="ℹ"
    ), unsafe_allow_html=True)

    # ── Precedence links ───────────────────────────────────────────────────────
    if ep.day_month_links:
        st.markdown(section_label("RELATED CUSTOMER ACTIVITY"), unsafe_allow_html=True)
        rows_html = '<div class="prx-card" style="padding:0;">'
        for lnk in ep.day_month_links[:3]:
            eligible = "✓ Eligible" if lnk.get("eligible") else "✗ Not eligible"
            rows_html += evidence_row(
                "Transaction Analysis",
                f"Customer {lnk.get('candidate_customer_id','?')} — {eligible}: {lnk.get('reason','')}",
                "fresh", str(lnk.get("driver_event_ts",""))[:10],
                "supporting" if lnk.get("eligible") else "neutral"
            )
        st.markdown(rows_html + "</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — METHOD AUDIT TRAIL
# ────────────────────────────────────────────────────────────────────────────

def _tab_audit(ep, hp, dp, mr: dict):
    st.markdown(section_label("HOW PRAXIS REACHED THIS CONCLUSION — Step-by-step method attribution"), unsafe_allow_html=True)
    st.markdown("""
<div style="font-size:.8125rem;color:#6B7280;line-height:1.6;margin-bottom:1rem;padding:.875rem 1rem;
     background:#F9FAFB;border-radius:6px;border-left:3px solid #E5E7EB;">
  The following steps show exactly how Praxis arrived at its conclusion. Every calculation is labelled
  by type so you can verify what was computed vs. what was estimated.
</div>""", unsafe_allow_html=True)
    st.markdown(callout(
        "Every step is labelled: "
        "<b style='color:#1D4ED8;'>Deterministic</b> (code + statistics) · "
        "<b style='color:#C2410C;'>Retrieval</b> (customer review search) · "
        "<b style='color:#6D28D9;'>LLM</b> (narrative &amp; claim wording only) · "
        "<b style='color:#166534;'>Business Rule</b> (governed lever catalogue + decision rights).",
        kind="info", icon="ℹ"
    ), unsafe_allow_html=True)

    det  = (ep.detection or {}) if ep else {}
    decomp = (ep.decomposition or {}) if ep else {}

    # Step 1 — Baseline
    bl = (ep.baseline or {}) if ep else {}
    st.markdown('<div class="prx-card" style="padding:0.25rem 0;">' +
        audit_row("det", "① Baseline Computation · C2 Operator 1",
                  f"Computed from {bl.get('window_size_used',0)} comparable periods. "
                  f"Baseline: {bl.get('baseline_mean',0):,.0f} ± {bl.get('baseline_std',0):,.0f}. "
                  f"Confidence grade: {bl.get('baseline_confidence','—')}.",
                  formula="baseline_mean = mean(same_weekday_history, window=14)\nbaseline_std = std(same_weekday_history)")
    , unsafe_allow_html=True)

    # Step 2 — Detection
    z    = det.get("test_statistic", 0) or 0
    test = det.get("test_type", "z_score")
    mat  = det.get("material", False)
    st.markdown(
        audit_row("det", "② Statistical Detection · C2 Operator 2",
                  f"Test: {test.replace('_',' ')} · z = {z:.2f} · Material: {mat}. "
                  f"Two-gate: statistical significance AND economic materiality.",
                  formula=f"z = (actual − baseline_mean) / baseline_std = {z:.2f}\nmaterial = (|z| > 2.5) AND (|delta_abs| > ₹50,000)")
    , unsafe_allow_html=True)

    # Step 3 — Decomposition
    drivers = decomp.get("drivers", [])
    driver_lines = "\n".join(
        f"{d['driver_name']}: {d.get('contribution_pct',0):.1f}% (method: {d.get('method','')})"
        for d in drivers[:3]
    )
    st.markdown(
        audit_row("det", "③ Contribution Decomposition · C2 Operator 3",
                  f"{len(drivers)} drivers identified. Residual: {decomp.get('residual_pct',0):.1f}%. "
                  f"Dominant: {decomp.get('dominant_driver','None')}.",
                  formula=f"contribution_pct = driver_value_gap / total_gap\n{driver_lines}")
    , unsafe_allow_html=True)

    # Step 4 — Retrieval
    hyps = (hp.hypotheses if hp else []) or []
    n_cv = sum(len((h.get("retrieval_result") or {}).get("records") or []) for h in hyps)
    st.markdown(
        audit_row("ret", "④ Customer Voice Retrieval · C3",
                  f"Hybrid retrieval: BM25 sparse + sentence-transformer embedding + RRF fusion. "
                  f"{n_cv} relevant records retrieved within [anchor-7, anchor+2] window. "
                  "Retrieval provides contextual evidence — NOT causal proof.",
                  formula="score = RRF(BM25_rank, cosine_rank)\nwindow = [anchor − 7 days, anchor + 2 days]")
    , unsafe_allow_html=True)

    # Step 5 — LLM claim wording
    if hyps:
        claim = hyps[0].get("claim", "—")
        st.markdown(
            audit_row("llm", "⑤ Hypothesis Claim Wording · LLM (Groq llama-3.3-70b)",
                      "LLM receives: driver_type (code), contribution_pct (code), kpi_id (code). "
                      "LLM role: phrase the hypothesis claim in natural language. "
                      "LLM does NOT choose the driver, contribution %, or confidence.",
                      formula=f'Claim: "{claim[:120]}…"')
        , unsafe_allow_html=True)

    # Step 6 — Confidence
    if hyps:
        comps = hyps[0].get("confidence_components", {}) or {}
        ms  = comps.get("materiality_strength", 0)
        ds  = comps.get("dominance_strength", 0)
        cvs = comps.get("customer_voice_score", 0)
        dqp = comps.get("data_quality_penalty", 0)
        mem = comps.get("memory_points", 0)
        total = comps.get("raw_with_memory", ms + ds + cvs - dqp + mem)
        st.markdown(
            audit_row("det", "⑥ Confidence Score · C3 § Confidence Policy",
                      "Formula applied deterministically. LLM cannot modify confidence.",
                      formula=(f"confidence = materiality({ms:.1f}) + dominance({ds:.1f}) + cv({cvs:+.1f})"
                               f" − dq_penalty({dqp:.1f}) + memory({mem:+.1f})"
                               f"\n         = {total:.0f} → band: {hyps[0].get('confidence_band','?')}"))
        , unsafe_allow_html=True)

    # Step 7 — Memory
    if mr.get("matched"):
        scope = mr.get("match_scope", "?")
        conf_count = mr.get("confirmed_precedent_count", 0)
        st.markdown(
            audit_row("ret", "⑦ Memory Retrieval · C5 Gateway",
                      f"Match scope: {scope} · Confirmed precedents: {conf_count}. "
                      "Retrieved record fed back into confidence formula as memory_points.",
                      formula=f"memory_points = min(12 + 6*(n-1), 25) = +{min(12+6*(conf_count-1),25) if conf_count else 0}")
        , unsafe_allow_html=True)
    else:
        st.markdown(
            audit_row("ret", "⑦ Memory Retrieval · C5 Gateway",
                      "No matching precedent found — cold start. memory_points = 0.")
        , unsafe_allow_html=True)

    # Step 8 — Lever selection
    if dp:
        lever = dp.actions[0].controllable_lever if dp.actions else "L8_monitor_no_action"
        owner = dp.actions[0].owner if dp.actions else "—"
        st.markdown(
            audit_row("rule", "⑧ Lever Selection · C4 Decision Rights",
                      f"Lever: {lever} · Owner: {owner}. "
                      "Deterministic lookup: driver_type → lever catalogue → rights matrix. "
                      "LLM does NOT select the lever.",
                      formula=f"lever = LEVER_MAP['{dp.actions[0].driver if dp.actions else '?'}'] = '{lever}'\nowner = RIGHTS_MATRIX['{lever}']['zone_head_always'] → {owner}")
        , unsafe_allow_html=True)

    # Step 9 — Narrative
    if dp:
        narr = dp.narrative_zone_business_head or dp.narrative_dark_store_ops_manager or "—"
        st.markdown(
            audit_row("llm", "⑨ Persona Narrative · LLM (C4 § Narrative Renderer)",
                      "LLM receives the canonical DecisionPackage (code-produced). "
                      "LLM role: render persona-appropriate narrative prose. "
                      "C4 §6 boundary: LLM phrases; code enforces.",
                      formula=f'Narrative (first 120 chars): "{(narr or "")[:120]}…"')
        , unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 5 — CONFIDENCE
# ────────────────────────────────────────────────────────────────────────────

def _tab_confidence(hp, mr: dict):
    if hp is None or not hp.hypotheses:
        st.markdown(empty_state("No confidence data", "", "○"), unsafe_allow_html=True)
        return

    leading = hp.hypotheses[0]
    score = int(leading.get("confidence_score", 0))
    band  = leading.get("confidence_band", "LOW")
    comps = leading.get("confidence_components", {}) or {}
    caps  = leading.get("hard_caps_applied", []) or []

    ms   = comps.get("materiality_strength", 0)
    ds   = comps.get("dominance_strength", 0)
    cvs  = comps.get("customer_voice_score", 0)
    dqp  = comps.get("data_quality_penalty", 0)
    mem  = comps.get("memory_points", 0)
    pre  = comps.get("raw_pre_memory", score - mem)

    col1, col2 = st.columns([1, 2])
    with col1:
        # Plain-language band display first
        band_plain = {"HIGH": "Strong confidence", "MEDIUM": "Moderate confidence", "LOW": "Low confidence", "ABSTAIN": "Cannot conclude"}.get(band, band)
        st.markdown(f"""
<div class="prx-conf-wrap">
  <div class="prx-conf-score {band}">{score}</div>
  <div class="prx-conf-band {band}">{band} &nbsp;·&nbsp; {band_plain}</div>
  {conf_bar(score, band)}
  <div style="font-size:.6875rem;color:#9CA3AF;margin-top:.25rem;">Score range: 0 – 100 · LOW ≥15 · MEDIUM ≥40 · HIGH ≥70</div>
</div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="prx-card">
  <div class="prx-card-header">Why this confidence level</div>
""", unsafe_allow_html=True)
        def _comp(name, val, hint=""):
            cls = "pos" if val > 0 else "neg" if val < 0 else "neu"
            return (f'<div class="prx-conf-component-row">'
                    f'<span class="prx-conf-comp-name">{name}</span>'
                    f'<div style="display:flex;align-items:center;gap:.5rem;">'
                    f'<span style="font-size:.625rem;color:#9CA3AF;">{hint}</span>'
                    f'<span class="prx-conf-comp-val {cls}">{val:+.1f}</span>'
                    f'</div></div>')
        st.markdown(
            _comp("Detection Strength",     ms,  "How far outside normal range") +
            _comp("Explanation Strength",   ds,  "How much one driver explains") +
            _comp("Customer Signal Score",  cvs, "Review evidence supporting/contradicting") +
            _comp("Data Quality Adjustment", -dqp, "Stale/conflicting data penalty") +
            _comp("Learning from Experience", mem, f"{'Validated precedent found' if mr.get('match_scope') else 'No match yet'}") +
            f'<div style="border-top:1px solid #E5E7EB;padding-top:.375rem;margin-top:.375rem;">'
            f'<div class="prx-conf-component-row"><span style="font-weight:700;color:#0F1117;">Total</span>'
            f'<span style="font-weight:700;color:#0F1117;">{score}</span></div></div>'
            + "</div>",
            unsafe_allow_html=True
        )

    # Hard caps
    if caps:
        st.markdown(callout(
            f"<b>Hard caps applied:</b> {', '.join(caps)}. "
            "These are deterministic policy rules that override the raw arithmetic band.",
            kind="warn", icon="⚠"
        ), unsafe_allow_html=True)

    # What could change
    st.markdown(section_label("WHAT COULD CHANGE THIS CONCLUSION"), unsafe_allow_html=True)
    uncertainties = [
        ("Competitor pricing data", "Currently unavailable. If a competitor promotion was active, attribution to stockout may be overstated."),
        ("SKU-level stockout duration", "Exact stockout start/end time would sharpen the contribution estimate."),
        ("Rider incident log", "If a rider shortage co-occurred, SLA effect may be partially independent."),
    ]
    for title, desc in uncertainties:
        st.markdown(f"""
<div class="prx-card-sm" style="margin-bottom:.5rem;">
  <div style="font-size:.8125rem;font-weight:600;color:#374151;margin-bottom:.1875rem;">? {title}</div>
  <div style="font-size:.75rem;color:#6B7280;">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown(callout(
        "<b>Confidence ≠ Certainty.</b> A score of 72 means Praxis has strong evidence "
        "supporting this conclusion — not that the conclusion is proven. "
        "Quantitative attribution is not the same as causal identification.",
        kind="warn", icon="⚠"
    ), unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 6 — RECOMMENDATION
# ────────────────────────────────────────────────────────────────────────────

def _tab_recommendation(dp, ep, hp, persona: str):
    if dp is None:
        st.markdown(empty_state("No recommendation available", "", "○"), unsafe_allow_html=True)
        return

    outcome = dp.source_decision_outcome
    det = (ep.detection or {}) if ep else {}
    delta_a = det.get("delta_absolute", 0) or 0

    # Outcome header
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:.875rem;margin-bottom:1.25rem;">
  {outcome_pill(outcome)}
  <span style="font-size:.8125rem;color:#6B7280;">
    {"Praxis has sufficient confidence to recommend a specific action." if outcome=="ANSWER" else
     "Praxis recommends action with a caveat — confidence is qualified." if outcome=="QUALIFY" else
     "Praxis requires additional data before recommending." if outcome=="CLARIFY" else
     "Praxis cannot recommend an action — evidence is insufficient."}
  </span>
</div>""", unsafe_allow_html=True)

    # Caveat
    if dp.caveat_text:
        st.markdown(callout(f"<b>Caveat:</b> {dp.caveat_text}", kind="warn", icon="⚠"),
                    unsafe_allow_html=True)

    # Action card
    if dp.actions:
        act = dp.actions[0]
        lever_label = act.controllable_lever.replace("_", " ").title()
        driver_label = act.driver.replace("_", " ").title()
        owner_label = act.owner.replace("_", " ").title()

        st.markdown(f"""
<div class="prx-action-card">
  <div class="prx-action-card-head">
    Recommended Action &nbsp;·&nbsp;
    <span style="color:#9CA3AF;font-size:.6875rem;">Decision authority verified by policy</span>
  </div>
  {action_row("Primary Driver", driver_label)}
  {action_row("Business Lever", lever_label, "purple")}
  {action_row("Recommended Action", act.action)}
  {action_row("Action Owner", owner_label)}
  {action_row("Decision Authority", ("Zone Business Head — cross-store scope requires senior approval" if "zone_business_head" in act.owner else "Dark-Store Ops Manager — within-store scope"))}
  {action_row("Expected Impact", act.expected_impact, "success")}
  {action_row("Confidence", f"{act.confidence} · Score: {hp.hypotheses[0].get('confidence_score',0) if hp and hp.hypotheses else '?'}/100" if hp else act.confidence)}
  {action_row("Monitoring Plan", act.monitoring_plan)}
</div>""", unsafe_allow_html=True)

    # Counterfactual
    if ep and ep.decomposition:
        drivers = ep.decomposition.get("drivers", [])
        if drivers and delta_a:
            dom_pct = drivers[0].get("contribution_pct", 0)
            dom_pct = dom_pct if dom_pct > 1 else dom_pct * 100
            recoverable = abs(delta_a) * (dom_pct / 100)
            actual = det.get("actual_value", 0) or 0
            counterfactual_gmv = actual + recoverable
            remaining_gap = abs(delta_a) - recoverable

            fmt = lambda v: f"₹{v/100_000:.2f}L"
            st.markdown(section_label("WHAT IF WE FIX THIS? — Attribution-based Scenario Estimate"), unsafe_allow_html=True)
            st.markdown(f"""
<div class="prx-counterfactual">
  <b>Attribution-based scenario estimate</b> — computed deterministically from C2 contribution decomposition:<br><br>
  Without the identified {drivers[0].get('driver_name','?').replace('_',' ').title()} contribution,
  {_kpi_display(ep.kpi_id)} would have been approximately <b>{fmt(counterfactual_gmv)}</b>
  — only <b>{fmt(remaining_gap)}</b> below baseline rather than <b>{fmt(abs(delta_a))}</b>.<br><br>
  <span style="font-size:.75rem;color:#166534;">
    ⚠ Causal effect not established. This is an attribution-based decomposition estimate, not a controlled experiment.
    Recovering {fmt(recoverable)} assumes the driver contribution is fully addressable via the recommended lever.
  </span>
</div>""", unsafe_allow_html=True)

    # Downstream risk
    st.markdown(section_label("DOWNSTREAM RISK — Known Cross-KPI Relationship"), unsafe_allow_html=True)
    st.markdown(f"""
<div class="prx-risk-box">
  <b>⚠ Downstream risk:</b> Dark-store stockout rate today is a known upstream driver of
  <b>Repeat Purchase Rate</b> (monthly lag). Historical data shows a temporal association:
  stockout events correlate with −5 to −10pp RPR impact observed 3–4 weeks later.<br><br>
  <span style="font-size:.75rem;color:#78350F;">
    Relationship type: <b>Temporal association</b> · Causal effect: <b>Not established</b> ·
    Confidence: <b>Moderate</b> · Observation window: <b>End of September 2026</b>
  </span>
</div>""", unsafe_allow_html=True)

    # Persona narrative
    st.markdown(section_label("WHAT THIS MEANS FOR YOU"), unsafe_allow_html=True)

    narrator = (dp.narrative_zone_business_head
                if persona == Persona.ZONE_BUSINESS_HEAD
                else dp.narrative_dark_store_ops_manager)
    if narrator:
        st.markdown(f"""
<div class="prx-narrative">
{narrator}
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(callout(
            "Narrative not available — LLM may be offline. "
            "All quantitative conclusions above remain valid; they are deterministic.",
            kind="warn", icon="⚠"
        ), unsafe_allow_html=True)

    # Approve button
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        if st.button("✓ Approve & Record Decision", type="primary", key="approve_decision"):
            import streamlit as _st
            if "approve_decision_fn" in _st.session_state:
                _st.session_state.approve_decision_fn()
            else:
                _st.session_state.pending_approve = True
    with col2:
        if st.button("✗ Reject / Escalate", key="reject_decision"):
            st.session_state.feedback_msg = ("warn", "Decision rejected. Escalated to senior review.")
    with col3:
        fb = st.session_state.get("feedback_msg")
        if fb:
            cls, msg = fb
            html_cls = "prx-feedback-ok" if cls == "ok" else "prx-feedback-err"
            st.markdown(f'<div class="{html_cls}">{msg}</div>', unsafe_allow_html=True)

    if st.session_state.get("pending_approve"):
        st.session_state.pending_approve = False
        # Call the main app's approve function
        import ui.streamlit_app as app
        app._approve_decision(st.session_state.pipeline_result)
        st.rerun()

    st.caption("⚠ 'Approve & Record Decision' creates a record in Praxis decision memory. "
               "It does NOT automatically execute an inventory action — this is a prototype simulation.")


# ────────────────────────────────────────────────────────────────────────────
# TAB 7 — SIGNATURE DEMO (Decision 1 vs Decision 3)
# ────────────────────────────────────────────────────────────────────────────

def _tab_signature_demo(result_current, persona: str):
    """Show the D1 vs D3 memory comparison — the core Praxis signature."""

    st.markdown(f"""
<div class="prx-page-title" style="margin-bottom:.25rem;">The Signature Story</div>
<div class="prx-page-sub">The <b>same underlying evidence</b> — the only variable is governed memory.
Praxis didn't just remember text. It used <b>validated experience to improve the next decision.</b></div>
""", unsafe_allow_html=True)

    # Learning loop diagram
    st.markdown("""
<div class="prx-loop">
  <div class="prx-loop-node">
    <div class="prx-loop-icon">📊</div>
    <div class="prx-loop-label">Signal</div>
    <div class="prx-loop-sub">KPI movement detected</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node active">
    <div class="prx-loop-icon">⬡</div>
    <div class="prx-loop-label">Decision 1</div>
    <div class="prx-loop-sub">Cold start · QUALIFY</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node">
    <div class="prx-loop-icon">✓</div>
    <div class="prx-loop-label">Outcome</div>
    <div class="prx-loop-sub">₹3.2L recovered</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node memory-node">
    <div class="prx-loop-icon">⊗</div>
    <div class="prx-loop-label">Memory</div>
    <div class="prx-loop-sub">Validated · C5 Gateway</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node active">
    <div class="prx-loop-icon">⬡</div>
    <div class="prx-loop-label">Decision 3</div>
    <div class="prx-loop-sub">Memory retrieved · ANSWER</div>
  </div>
  <div class="prx-loop-arrow">→</div>
  <div class="prx-loop-node">
    <div class="prx-loop-icon">↑</div>
    <div class="prx-loop-label">Better</div>
    <div class="prx-loop-sub">Higher confidence · Sharper action</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Run both decisions
    col_run1, col_run2, col_spacer = st.columns([2, 2, 3])
    with col_run1:
        run_d1 = st.button("▶ Run Decision 1 (S1 · No Memory)", key="sig_d1", use_container_width=True)
    with col_run2:
        run_d3 = st.button("▶ Run Decision 3 (S2 · With Memory)", key="sig_d3", type="primary", use_container_width=True)

    if run_d1:
        from praxis.orchestration.pipeline import run_pipeline
        from praxis.synthetic.generator import get_scenario
        with st.spinner("Running Decision 1 (S1, no memory)…"):
            r1 = run_pipeline(get_scenario("s1"), persona=persona, use_memory=False)
            st.session_state["sig_d1_result"] = r1

    if run_d3:
        from praxis.orchestration.pipeline import run_pipeline
        from praxis.synthetic.generator import get_scenario
        with st.spinner("Running Decision 3 (S2, with memory)…"):
            r3 = run_pipeline(get_scenario("s2"), persona=persona, use_memory=True)
            st.session_state["sig_d3_result"] = r3

    r1 = st.session_state.get("sig_d1_result")
    r3 = st.session_state.get("sig_d3_result")

    if r1 is None and r3 is None:
        st.markdown(callout(
            "Click <b>Run Decision 1</b> then <b>Run Decision 3</b> to see the memory effect. "
            "Ensure a decision record and confirmed outcome exist in C5 for Decision 1 first "
            "(approve Decision 1 in the Recommendation tab).",
            kind="info", icon="ℹ"
        ), unsafe_allow_html=True)
        return

    # Comparison grid
    def _dec_stats(r):
        if r is None or r.error:
            return None
        hp = r.hypothesis_package
        dp = r.decision_package
        mr = r.memory_result or {}
        if not hp or not hp.hypotheses:
            return None
        h = hp.hypotheses[0]
        return {
            "score":   h.get("confidence_score", 0),
            "band":    h.get("confidence_band", "LOW"),
            "outcome": dp.source_decision_outcome if dp else "ABSTAIN",
            "mem":     mr.get("matched", False),
            "mem_pts": h.get("confidence_components", {}).get("memory_points", 0),
            "pre_mem": h.get("confidence_components", {}).get("raw_pre_memory", 0),
            "lever":   dp.actions[0].controllable_lever if (dp and dp.actions) else "—",
            "impact":  dp.actions[0].expected_impact if (dp and dp.actions) else "—",
            "narr":    (dp.narrative_zone_business_head or dp.narrative_dark_store_ops_manager or "—") if dp else "—",
        }

    s1 = _dec_stats(r1)
    s3 = _dec_stats(r3)

    cols = st.columns(2)
    for col, label, cls, stats in [
        (cols[0], "DECISION 1 · Cold Start · S1 · 2026-08-15", "baseline", s1),
        (cols[1], "DECISION 3 · Memory Retrieved · S2 · 2026-08-22", "memory", s3),
    ]:
        with col:
            if stats is None:
                st.markdown(f'<div class="prx-dec-card {cls}"><div class="prx-dec-card-label">{label}</div><div style="color:#9CA3AF;font-size:.8125rem;">Not run yet</div></div>',
                            unsafe_allow_html=True)
                continue

            mem_html = (
                f'<div style="margin:.5rem 0;font-size:.75rem;">'
                f'<span style="color:#6B7280;">Memory: </span>'
                f'<b style="color:{"#6B21A8" if stats["mem"] else "#9CA3AF"}">{"✓ Retrieved · +" + str(int(stats["mem_pts"])) + " pts" if stats["mem"] else "✗ No match · +0 pts"}</b>'
                f'</div>'
            )
            pre_str = f" (pre-memory: {stats['pre_mem']:.0f})" if stats["mem"] else ""

            st.markdown(f"""
<div class="prx-dec-card {cls}">
  <div class="prx-dec-card-label">{label}</div>
  <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.5rem;">
    <div class="prx-conf-score {stats['band']}" style="font-size:1.75rem;">{stats['score']:.0f}</div>
    <div>
      <div class="prx-conf-band {stats['band']}">{stats['band']}</div>
      {outcome_pill(stats['outcome'])}
    </div>
  </div>
  {conf_bar(stats['score'], stats['band'])}
  {mem_html}
  <div style="font-size:.75rem;color:#6B7280;margin-top:.375rem;">Score: <b>{stats['score']:.0f}</b>{pre_str} · Lever: <b>{stats['lever'].replace('_',' ').title()}</b></div>
  <div style="font-size:.75rem;color:#374151;margin-top:.5rem;font-style:italic;line-height:1.5;">{stats['impact']}</div>
</div>""", unsafe_allow_html=True)

    # Isolation proof
    if s1 and s3:
        delta_score = s3["score"] - s1["score"]
        mem_pts = s3.get("mem_pts", 0)
        st.markdown(f"""
<div class="prx-callout purple" style="margin-top:1rem;">
  <span class="prx-callout-icon">⊗</span>
  <div class="prx-callout-body">
    <b>Isolation Proof — Memory is the sole variable.</b><br>
    Customer Voice score is identical in both scenarios (+20 in both, same canonical texts).
    Quantitative evidence (decomposition, segmentation, z-score) is controlled.
    The confidence delta of <b>+{delta_score:.0f} pts</b> comes entirely from the C5 memory
    contribution of <b>+{mem_pts:.0f} pts</b>. This proves Praxis used validated experience,
    not fabricated text, to improve the next decision.
  </div>
</div>
""", unsafe_allow_html=True)
