# Praxis — Competitive Gap Analysis
### Where We Win, Where We Fall Short, and What to Build Next

**Evaluation lens:** Senior BA at McKinsey / Accenture judging a hackathon final  
**Date:** 2026-08-30

---

## Executive Summary

Our solution is **architecturally sound and technically honest** — arguably the most principled separation of LLM vs. deterministic logic in the room. The 76-test suite, genericity proof, and C5 memory loop are genuine differentiators.

But the problem statement explicitly asks evaluators to score *intelligence-to-action* — the full chain from alert through recommendation through outcome tracking. We have built the **reasoning engine** well. We have not built the **action intelligence** layer strongly enough, and we have a nearly invisible **cross-KPI causal story**.

**If we submit today, we win on architecture. We lose on impact storytelling.**

---

## Scoring Map: Requirement vs. Current State

| Requirement | Weight | Our State | Gap |
|---|---|---|---|
| 1. Detect & prioritise material KPI movements | High | ⚠️ Partial | One KPI at a time, no ranked alert queue |
| 2. Reconcile heterogeneous sources | High | ✅ Strong | GPS staleness penalty demonstrated |
| 3. Identify & rank explanatory drivers | High | ✅ Strong | Decomposition, PVM, segmentation done |
| 4. Persona-specific narratives + traceable evidence | High | ✅ Strong | Zone Head + Ops Manager, lineage chain |
| 5. Communicate uncertainty / abstain | High | ✅ Excellent | 4 distinct abstention scenarios |
| 6. Recommend practical actions | High | ⚠️ Weak | Levers exist; ROI and monitoring plan buried |
| 7. Learn from feedback | Medium | ⚠️ Partial | D1→D3 proof, but no visible learning curve |
| 8. Security / cost / latency constraints | Medium | ✅ Good | Entitlements, cache, telemetry |

---

## Gap 1 (CRITICAL) — No Multi-KPI Alert Queue

**What the problem asks:** *"Detects and **prioritises** material KPI movements"* — plural.

**What we do:** The user clicks a single scenario button. There is no view showing "here are the 3 KPIs that moved materially this week, ranked by severity." There is no proactive surface. The engine is entirely reactive.

**What a winning solution shows:**
A panel that, on load, runs detection across all 5 KPIs for the week and presents:
```
🔴 Zone GMV        −25%   z=5.0   MATERIAL   → root cause identified
🟡 Stockout Rate   +38pp  z=4.2   MATERIAL   → evidence gathering
🟢 SLA Adherence   −12pp  z=2.8   MATERIAL   → abstain (sparse history)
⚪ Conversion Rate  +0.1pp         NON-MATERIAL
⚪ Repeat Purchase  (monthly — no data yet)
```
This is what a BI head sees on Monday morning. Without it, we look like a demo toy.

**Effort to fix:** Medium. The pipeline already runs each KPI independently. A `run_all_kpis()` function that loops over all registered KPIs and returns ranked detection results is ~50 lines.

---

## Gap 2 (CRITICAL) — Action Recommendations Are Not Boardroom-Ready

**What the problem asks:** *"driver → controllable lever → action → **expected impact** → owner → confidence → monitoring plan"*

**What we do:** We have all 7 fields in the `ActionItem` dataclass. They appear in narrative prose. Nobody can read them at a glance during a live demo.

**The killer slide format (not prose, but structured):**

```
RECOMMENDED ACTION
┌─────────────────────────────────────────────────────────┐
│ Driver:    Dark-store stockout rate (DS041, 55%)        │
│ Lever:     L2 — Cross-store inventory transfer          │
│ Action:    Transfer 200 units SKU-2207 from DS043→DS041 │
│ Owner:     Zone Business Head (crosses store scope)     │
│ Confidence: HIGH · 72/100 (1 confirmed precedent)       │
│ Exp. Impact: Recover ~₹3.5L of ₹7.0L gap in 24–48h    │  ← MISSING
│ Monitor:   Re-check GMV at T+24h and T+48h              │
│ If wrong:  Trigger L7 manual investigation              │
└─────────────────────────────────────────────────────────┘
```

The **"Exp. Impact: Recover ~₹3.5L"** line is currently vague. We need a deterministic counterfactual: if stockout_rate returns to baseline (4%), contribution model says GMV recovers by attribution_pct × total_gap.

**Effort to fix:** Low. The data is already there — compute `contribution_pct × abs(delta_absolute)` and show as the recoverable amount.

---

## Gap 3 (HIGH) — No Cross-KPI Causal Chain

**What the problem asks:** *"Multiple interacting drivers such as price, volume, mix, marketing, supply..."* — interactions, plural.

**What we do:** Each KPI is analyzed independently. We note that stockout_rate is a driver of zone_gmv, but we never **visually demonstrate the causal chain**:

```
DS041 Stockout Rate ↑38pp
        ↓ (contributes 54%)
Zone GMV ↓ ₹7.0L (−25%)
        ↓ (implied downstream)
Repeat Purchase Rate (risk: −8pp next month)
```

This is the business story that makes a CFO lean forward. "Your stockout problem today is your churn problem next month."

We have `operator5_precedence.py` which handles day→month links for RPR. This is already architecturally there — we are just not surfacing it narratively or visually.

**Effort to fix:** Medium. Add a "Downstream Risk" section to the decision package that flags when an active driver (e.g., stockout) appears in another KPI's driver list (e.g., RPR). Purely rule-based.

---

## Gap 4 (HIGH) — Learning Loop Is Invisible

**What the problem asks:** *"Mechanism to learn from analyst and business-user feedback."*

**What we demonstrate:** D1 (60/QUALIFY) → D3 (72/HIGH/ANSWER) via memory. This is correct and impressive.

**What we're missing:** The narrative. Right now the comparison is shown as a side-by-side table. It doesn't answer: *"How does the system get smarter over time?"*

A winning answer adds:
1. A **memory log** tab showing every admitted decision + outcome, when it was confirmed, and how it affected subsequent confidence
2. A **"Why did confidence change?"** explainer: `Confidence 60→72: +12 memory points from 1 exact-grain precedent (DS041, confirmed 2026-08-17)`
3. A **feedback entry form** that is visually prominent — not just two buttons buried below the timeline

**Effort to fix:** Low. The data is already in DuckDB. Query and display it.

---

## Gap 5 (HIGH) — LLM vs. Deterministic Boundary Not Visually Demonstrated

**What the problem asks:** *"Teams should explicitly demonstrate when they use deterministic logic, SQL, business rules, statistics, traditional ML, causal inference, retrieval or LLMs — and why."*

**What we do:** The telemetry panel shows `LLM calls: 0 / Tokens: 0` (because cache hits). That's actually our strongest proof — but it reads as *"the LLM is broken."*

**What we need:** A **Method Audit Trail** component that labels every output:

```
DECOMPOSITION   [DETERMINISTIC] C2 Op3 — contribution decomposition
  ├─ Stockout 54%   [INTERVAL ANALYSIS — deterministic]
  ├─ SLA 25%        [CORRELATION — deterministic]
  └─ Residual 21%   [UNEXPLAINED — no forced attribution]

HYPOTHESIS CLAIM [LLM] groq/llama-3.3-70b → claim text only
  └─ "Stockout pattern at Z003 accounts for ~54%..."

CONFIDENCE SCORE [DETERMINISTIC FORMULA] ms+ds+cvs−dqp+mem
  └─ 72 = 28 (mat) + 12.7 (dom) + 20 (cv) − 0 (dqp) + 12 (mem)

CV RETRIEVAL     [BM25 + EMBEDDING COSINE + RRF FUSION]
  └─ 3 records retrieved, 2 supporting, 0 contradicting
```

This is the single most differentiating thing we can add in 2 hours. It directly answers what every evaluator will ask.

**Effort to fix:** Low. All this data is already computed. Just surface it.

---

## Gap 6 (MEDIUM) — Segmentation Is Not Visually Strong

**What the problem asks:** *"Contribution analysis"* — we have it. But in the UI the store-level ranking (DS041 → 54%) appears as a tiny chip, not a ranked bar chart.

A ranked visualization showing:
```
DS041  ████████████████████░░░░  54%   ₹3.9L
DS043  ████████░░░░░░░░░░░░░░░░  23%   ₹1.7L
DS042  ████░░░░░░░░░░░░░░░░░░░░  12%   ₹0.9L
DS044  ░░░░░░░░░░░░░░░░░░░░░░░░   8%   ₹0.6L  [MISSING — excluded]
```
...takes 20 minutes to build and makes the demo 5x more credible to a non-technical judge.

---

## Gap 7 (MEDIUM) — No Counterfactual / Scenario

**What a top solution adds:** *"Without the DS041 stockout, Zone Z003 GMV would have been ₹28.0L — only ₹0.5L below baseline rather than ₹7.0L below."*

This is a counterfactual: `baseline_value - (total_gap × (1 - top_driver_contribution_pct))`.

Purely arithmetic. Takes 5 lines. But it's the sentence that gets quoted in every debrief.

---

## Gap 8 (LOW) — Operator 4 Has a Residual Hardcode

`operator4_segmentation.py` still has `if kpi_id == "zone_gmv"` / `elif kpi_id in (...)` branches (lines 49–61). This is technically fine for the demo but inconsistent with the genericity audit we just filed. Worth a 10-minute fix to read from contract.

---

## What We Do Exceptionally Well (Defend These)

These are our genuine moat vs. every other team:

1. **Honest uncertainty propagation** — QUALIFY/ANSWER/ABSTAIN driven by a formula with hard caps. Most teams will have LLM say "I'm not sure." We have `band = ConfidenceBand.MEDIUM` enforced structurally.

2. **Memory that proves itself** — D1 60/QUALIFY → D3 72/ANSWER is the killer demo moment. No other team will have a working memory loop with a live DB write and a mathematical proof that CV score is identical.

3. **Non-negotiable entitlements** — Zone GMV total structurally absent from Ops Manager narrative (not instructed away, enforced in code). Evaluators who probe this will be impressed.

4. **Genuine lineage** — Every finding has a 5-node chain from SRC-OMS to FIND-ID. This is real audit trail, not a diagram.

5. **76 tests / genericity proof** — No other team has a test suite. The `test_genericity.py` proof is publishable.

6. **LLM economics honesty** — $0.00 cost shown with cache hit. Token count is real. Most teams will have no idea what their LLM cost was.

---

## Priority Build List (ranked by impact/effort ratio)

| Priority | What | Impact | Effort | Where |
|---|---|---|---|---|
| P0 | Multi-KPI Alert Dashboard (ranked detection across all KPIs on load) | 🔴 Critical | 2h | New pipeline function + UI panel |
| P0 | Method Audit Trail component (deterministic / LLM / retrieval labels on every output) | 🔴 Critical | 1.5h | UI component, data already exists |
| P1 | Structured Action Card (lever + recoverable ₹ + owner + 24/48h monitor) | 🟠 High | 1h | C4 + UI |
| P1 | Counterfactual sentence ("Without DS041 stockout, GMV would have been ₹28L") | 🟠 High | 0.5h | C4 computation |
| P1 | Store segmentation bar chart (ranked contributors with ₹ and % per store) | 🟠 High | 0.5h | UI only |
| P2 | Downstream Risk flag (stockout today → RPR risk next month) | 🟡 Medium | 1h | C4 rule-based |
| P2 | Memory log tab (full DuckDB query, admit history, feedback effect) | 🟡 Medium | 1h | UI + DuckDB query |
| P3 | Fix Op4 segmentation genericity (remove kpi_id string literals) | 🟢 Low | 0.5h | operator4_segmentation.py |

---

## The One Slide That Wins

If we fix P0s and P1s, our live demo narrative becomes:

> "On Monday morning, Praxis automatically scanned 5 KPIs for Zone Z003. It flagged Zone GMV as the highest-severity alert at z=5.0.
>
> It then ran a deterministic decomposition — no LLM involved — and attributed 54% of the ₹7.0L gap to DS041's stockout rate via interval-weighted analysis. The LLM was used only to phrase the hypothesis in English.
>
> Because we saw this exact pattern two weeks ago and confirmed the root cause, Praxis upgraded its confidence from MEDIUM to HIGH — moving from QUALIFY to ANSWER — and recommended a cross-store transfer expected to recover ₹3.9L within 24 hours.
>
> When the Zone Head clicks 'Confirmed Correct', that outcome is written to memory and will boost confidence again next time we see the same driver at the same grain.
>
> Praxis cost ₹0.00 in LLM tokens for this finding. It took 8 seconds."

That is a winning narrative. We have 90% of the infrastructure to deliver it.

---

> [!IMPORTANT]
> **Recommended next action:** Build the Multi-KPI Alert Dashboard (P0) first — it reframes the entire product from "single-scenario tool" to "always-on intelligence engine." Everything else is additive.

