# Praxis KPI Intelligence Engine — Winning Prototype Upgrade Plan

## Overview

After deeply reading all 12 specification files, the 76-test codebase, and the competitive gap analysis, here is the verdict:

**The architecture is exceptional.** The C1→C5 pipeline, genericity proof, honest confidence formula, memory loop, and entitlement enforcement are genuinely differentiated.

**The gaps are all presentational/surface-level** — every piece of data is already computed. We just need to surface it correctly to go from "wins on architecture" to "wins on impact storytelling."

---

## Gap Status: What's been addressed vs. what remains

| Gap | Severity | Addressed? | Notes |
|-----|----------|-----------|-------|
| G1: Multi-KPI Alert Queue | CRITICAL | ❌ No | Pipeline runs one KPI at a time. No ranked dashboard |
| G2: Boardroom-ready Action Cards | CRITICAL | ❌ No | `ActionItem` has all 7 fields but no structured UI |
| G3: Cross-KPI Causal Chain | HIGH | ❌ No | Op5 exists but RPR downstream risk never surfaced |
| G4: Learning Loop Visibility | HIGH | ❌ No | Memory DB exists but no log/audit UI |
| G5: LLM vs. Deterministic Audit Trail | HIGH | ❌ No | The LLM=0 showing reads as "broken" not "proof" |
| G6: Store Segmentation Bar Chart | MEDIUM | ❌ No | Data exists, shown as text chips only |
| G7: Counterfactual Sentence | MEDIUM | ❌ No | Arithmetic only, 5 lines missing |
| G8: Op4 Genericity | LOW | ❌ No | Residual `if kpi_id ==` branches at lines 49-61 |

> [!IMPORTANT]
> All gaps from the competitive gap analysis remain **unaddressed**. The repo as pushed by your teammate stopped after the Genericity Audit. We need to implement all 8 gaps.

---

## Proposed Changes

### Priority P0 (Critical — must have for demo)

---

#### 1. Multi-KPI Alert Queue

**New function in pipeline.py:** `run_all_kpis(zone_id, date, persona)` — loops all 5 registered KPI contracts, runs detection, returns ranked results sorted by z-score / severity.

**UI: New "Morning Briefing" tab** in `streamlit_app.py` — the **first tab the user sees** on load:

```
🔴 Zone GMV        −₹7.0L   z=5.0   MATERIAL   → Analyse
🟡 Stockout Rate   +38pp    z=4.2   MATERIAL   → Analyse  
🟠 SLA Adherence   −12pp    z=2.8   MATERIAL   → Low hist
⚪ Conversion      +0.1pp            NON-MATERIAL
⚪ Repeat Purchase  —                Monthly KPI, not yet
```

Each row shows: emoji indicator, KPI name, delta (absolute), z-score, status badge, and a mini action button.

**Files to change:**
- [`pipeline.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/praxis/orchestration/pipeline.py) — add `run_all_kpis()` function
- [`streamlit_app.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) — new Morning Briefing tab as the first/default tab

---

#### 2. Method Audit Trail Component

The **single most differentiating addition** per the gap analysis. Labels every output with its computational method.

**UI Component:**
```
DECOMPOSITION   [DETERMINISTIC] C2 Op3 — contribution decomposition
  ├─ Stockout 54%   [INTERVAL ANALYSIS — deterministic]  
  ├─ SLA 25%        [CORRELATION — deterministic]
  └─ Residual 21%   [UNEXPLAINED]

HYPOTHESIS CLAIM [LLM] groq/llama-3.3-70b → claim text only

CONFIDENCE SCORE [DETERMINISTIC] ms+ds+cvs−dqp+mem
  └─ 72 = 28(mat) + 12.7(dom) + 20(cv) − 0(dqp) + 12(mem)

CV RETRIEVAL    [BM25 + EMBEDDING COSINE + RRF FUSION]
  └─ 3 records retrieved, 2 supporting, 0 contradicting
```

**Files to change:**
- [`streamlit_app.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) — new `render_method_audit()` function + CSS, shown in Evidence Trail tab and Signature Demo tab

---

### Priority P1 (High — strong differentiators)

---

#### 3. Structured Action Card

Replace prose `expected_impact` with a visual card:

```
┌─────────────────────────────────────────────────────────┐
│ Driver:       Dark-store stockout rate (DS041, 55%)     │
│ Lever:        L2 — Cross-store inventory transfer       │
│ Action:       Transfer SKU-2207 from DS043 → DS041      │
│ Owner:        Zone Business Head                        │
│ Confidence:   HIGH · 72/100 (1 confirmed precedent)     │
│ Exp. Impact:  Recover ~₹3.85L of ₹7.0L gap in 24–48h  │
│ Monitor:      Re-check GMV at T+24h and T+48h           │
└─────────────────────────────────────────────────────────┘
```

**Backend change in `narrative.py`:** `_build_expected_impact()` needs to compute `contribution_pct × abs(delta_abs)` and return the recoverable ₹ amount as a deterministic number. Currently it's vague prose.

**Files to change:**
- [`narrative.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/praxis/c4_decision/narrative.py) — fix `_build_expected_impact()` to compute recoverable amount
- [`streamlit_app.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) — new `render_action_card()` component with structured layout

---

#### 4. Counterfactual Sentence

5 lines of arithmetic. Add to `narrative.py` and surface in UI:

> *"Without the DS041 stockout, Zone Z003 GMV would have been ₹24.85L — only ₹3.15L below baseline rather than ₹7.0L below."*

Formula: `counterfactual = actual_value + (abs(delta_abs) × contribution_pct / 100)`

**Files to change:**
- [`narrative.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/praxis/c4_decision/narrative.py) — add `compute_counterfactual()` helper
- [`streamlit_app.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) — render counterfactual in decision view

---

#### 5. Store Segmentation Bar Chart

Replace the three text chips with a visual ranked bar chart:

```
DS041  ████████████████████░░░░  54%   ₹3.85L  ← PRIMARY
DS043  ████████░░░░░░░░░░░░░░░░  23%   ₹1.61L
DS042  ████░░░░░░░░░░░░░░░░░░░░  12%   ₹0.84L
DS044  ░░░░░░░░░░░░░░░░░░░░░░░░   8%   ₹0.56L  [MISSING — excluded]
```

HTML/CSS-only bar chart inside `st.markdown()` — no Plotly dependency needed.

**Files to change:**
- [`streamlit_app.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) — new `render_segmentation_chart()` function + CSS

---

### Priority P2 (Medium — strengthens the story)

---

#### 6. Downstream Risk Flag — Cross-KPI Causal Chain

Add a "Downstream Risk" section to the Signature Demo / Evidence Trail that surfaces:

> *"⚠️ Downstream risk: The DS041 stockout rate (+38pp) is a known driver of Repeat Purchase Rate (monthly lag). If this pattern persists, expect a −5 to −10pp RPR impact in Z003 by end of September 2026."*

This uses `operator5_precedence.py`'s existing logic — we just need to check if the leading driver appears in any other KPI's `drivers` list (from KPI contracts) and surface it.

**Files to change:**
- [`pipeline.py`](file:///c:/Users/ISHIKA MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/praxis/orchestration/pipeline.py) — add `compute_downstream_risks()` that checks KPI contracts
- [`streamlit_app.py`](file:///c:/Users/ISHIKA MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) — render downstream risk box

---

#### 7. Memory Log Tab

A new sub-tab or section showing the full memory audit log from DuckDB:

| Date | Store | Driver | Action Taken | Outcome | Confidence Impact |
|------|-------|--------|-------------|---------|------------------|
| Aug 15 | DS041 | stockout | L2 transfer | ✅ Confirmed | 60→72 (+12 pts) |

Plus the explainer: *"Confidence 60→72: +12 memory points from 1 exact-grain precedent (DS041, confirmed 2026-08-17)"*

**Files to change:**
- [`streamlit_app.py`](file:///c:/Users/ISHIKA MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) — new memory log query + rendering, with prominent feedback button

---

### Priority P3 (Low — polish)

---

#### 8. Fix Op4 Segmentation Genericity

Remove `if kpi_id == "zone_gmv": ... elif kpi_id in (...):` branches and replace with contract-driven logic.

The key insight: all 4 cases currently do the same thing (`contrib = kpi_val.get("delta", 0.0)`). The branching is vestigial — we can read `aggregation_method` from the contract to determine whether to use delta directly vs. pool.

**Files to change:**
- [`operator4_segmentation.py`](file:///c:/Users/ISHIKA MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/praxis/c2_analytical/operator4_segmentation.py) — remove kpi_id branches, read from contracts

---

## Implementation Order

```
Phase 1: Backend additions (don't break tests)
  1. narrative.py — compute_counterfactual() + fix _build_expected_impact()
  2. pipeline.py — run_all_kpis() + compute_downstream_risks()
  3. operator4_segmentation.py — remove kpi_id branches

Phase 2: UI additions (streamlit_app.py)
  4. CSS — new component styles (action card, bar chart, audit trail, alert queue)
  5. Morning Briefing tab (multi-KPI alert queue)
  6. Method Audit Trail component
  7. Action Card component
  8. Store segmentation bar chart
  9. Counterfactual sentence
  10. Downstream risk flag
  11. Memory log tab + prominent feedback

Phase 3: Sidebar update
  12. Update test count (51 → 76 based on GENERICITY_AUDIT)
  13. Add "Last scan: Zone Z003 · 5 KPIs analysed" status line
```

---

## Verification Plan

### Automated Tests
```
pytest tests/ -v   # must still be 76 passed, 0 failed
```

### Manual Demo Verification
1. Load app → Morning Briefing tab loads showing 5 KPIs ranked by severity
2. Click "Signature Demo" → D1 vs D3 comparison still works with memory delta
3. Evidence Trail tab shows Method Audit Trail with all labels
4. Action Card shows recoverable ₹ amount (deterministic computation)
5. Store segmentation shows bar chart with ₹ values
6. Counterfactual sentence appears: "Without DS041 stockout, GMV would have been ₹X"
7. Downstream Risk flag appears linking stockout → RPR
8. Memory log tab shows admit history with confidence delta explanation
9. Ops Manager view still excludes Zone GMV total

---

> [!IMPORTANT]
> The winning demo narrative (from the gap analysis) that we're building toward:
>
> *"On Monday morning, Praxis automatically scanned 5 KPIs for Zone Z003. It flagged Zone GMV as the highest-severity alert at z=5.0. It ran a deterministic decomposition — no LLM involved — and attributed 54% of the ₹7.0L gap to DS041's stockout rate. The LLM was used only to phrase the hypothesis in English. Because we saw this exact pattern two weeks ago and confirmed the root cause, Praxis upgraded its confidence from MEDIUM to HIGH — moving from QUALIFY to ANSWER — and recommended a cross-store transfer expected to recover ₹3.85L within 24 hours. Praxis cost ₹0.00 in LLM tokens. It took 8 seconds."*
