# PRAXIS — Enterprise UI · Page Reference

> **Server:** http://localhost:8501 (running)  
> **Status:** Bug fixed — `UnboundLocalError` in `morning_briefing.py` resolved  
> **Tests:** 76/76 passing

---

## Bug Fixed This Session

**Error:** `UnboundLocalError: cannot access local variable 'st' where it is not associated with a value`

**Root cause:** Inside `_render_top_investigation_banner()` there was a rogue `import streamlit as st` nested inside the button handler. In Python, when a function contains _any_ assignment to a name (including an import), Python treats that name as **local for the entire function** — so `st.markdown(...)` at the top of the function failed because `st` was local but not yet assigned.

**Fix:** Removed `import streamlit as st` and the duplicate `from praxis.orchestration.pipeline import run_pipeline` from inside the button handler. `st` is already imported at module level.

**File:** [`ui/components/morning_briefing.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/morning_briefing.py) · lines 211–221

---

## Complete Page Map

### 🏠 Morning Briefing (Home)
**Route:** Default landing page  
**What you see:**
- Page title "Good morning." with date/time
- **KPI Scan Bar** — 4 KPIs with live status dots, delta display, z-score, method badge, freshness
- **Priority Investigation Banner** — most urgent KPI with What Changed summary, two CTAs:
  - `⌕ Investigate →` — navigates to Active Investigations
  - `▶ Run Signature Demo (S1)` — runs the S1 pipeline and navigates

---

### ⌕ Active Investigations
**Route:** Sidebar → INVESTIGATE → Active Investigations  
**Requires:** A scenario to have been run first  
**What you see:** 7-tab workspace

| Tab | Content |
|-----|---------|
| ① What Changed | 4 metric tiles (Actual, Baseline, Gap, z-score) · Materiality verdict · Data quality flags |
| ② Why It Happened | Driver decomposition bar chart · Store segmentation ranking · Leading hypothesis |
| ③ Evidence | Structured evidence rows (source/statement/freshness) · Customer Voice cards · Temporal links |
| ④ How Praxis Concluded | 9-step method audit trail (det/ret/llm/rule badges + formulas) |
| ⑤ Confidence | Score circle (0–100) · Component breakdown · Hard caps · Uncertainty factors |
| ⑥ Recommendation | Outcome banner · Action card · Counterfactual · Downstream risk · Persona narratives · Approve button |
| ⑦ Signature Demo | D1 vs D3 comparison · Learning loop diagram · Isolation proof |

---

### → Recommended Actions
**Route:** Sidebar → DECISIONS → Recommended Actions  
**What you see:**
- Outcome banner (ANSWER/QUALIFY/CLARIFY/ABSTAIN)
- Full structured action card (driver, lever, owner, authority, confidence, impact, monitoring)
- Zone Business Head narrative (LLM)
- Dark-Store Ops Manager narrative (LLM)
- Approve & Record / Escalate buttons

---

### ⊞ Past Decisions
**Route:** Sidebar → DECISIONS → Past Decisions  
**What you see:**
- Decision log table (date, KPI, driver, action, confidence, outcome, memory status)
- Outcome feedback form → wired to C5 DuckDB gateway

---

### ◈ What Praxis Has Learned
**Route:** Sidebar → LEARNING → What Praxis Has Learned  
**What you see:**
- Full learning loop diagram (Signal → Investigation → Decision → Outcome → Memory → Better Decision)
- C5 gateway governance table (5 admission gates)
- Memory correction / supersession model illustration
- Core differentiator quote card

---

### ⊗ Memory
**Route:** Sidebar → LEARNING → Memory  
**What you see:**
- Confidence points counter (current memory boost)
- Decision Memory Records (from DuckDB)
- Outcome Memory Records (confirmed/rejected)
- Feedback form → Submit Confirmed / Submit Rejected

---

### ≡ Evidence & Audit Trail
**Route:** Sidebar → GOVERNANCE → Evidence & Audit Trail  
**What you see:**
- Lineage chain display
- Claim → Evidence traceability table
- Lineage graph edges (expandable)

---

### ⬡ Data Health
**Route:** Sidebar → GOVERNANCE → Data Health  
**What you see:**
- Summary tiles (Fresh sources: 4, Stale: 2, Missing: 0)
- 6 source cards: SRC-OMS, SRC-INV, SRC-DEL (⚠ stale), SRC-SESS, SRC-CV, SRC-MKT (⚠ stale)
- Stale penalty explanation

---

### ⊕ Access & Entitlements
**Route:** Sidebar → GOVERNANCE → Access & Entitlements  
**Persona-sensitive** — shows different access table for each persona  
**What you see:**
- Role card (Zone Business Head or Dark-Store Ops Manager)
- Access table (what's visible vs. restricted)
- Enforcement architecture explanation
- (Ops Manager only) Request access button

---

### ⊛ Telemetry
**Route:** Sidebar → GOVERNANCE → Telemetry  
**What you see:**
- 4 tiles: Total latency, Deterministic share, LLM processing, Est. cost
- Phase breakdown table with LLM vs Deterministic tags

---

### ▶ Scenario Launcher
**Route:** Sidebar → DEMO → Scenario Launcher  
**What you see:**
- Signature Demo spotlight + judge instructions
- 6 scenario cards with Run buttons:
  - S1 — Canonical Stockout (cold start) · primary
  - S2 — With Validated Memory · primary
  - S3 — Insufficient History (abstention)
  - S4 — No Dominant Contributor
  - S5 — Contradicted Hypothesis
  - S6 — Unscripted (genericity test)
- Full C1→C6 pipeline architecture diagram

---

## Signature Demo — Judge Flow

```
1. Scenario Launcher → ▶ Run S1 (cold start)
   → Investigation Tab ⑥: QUALIFY · confidence 60 · no memory

2. Tab ⑥ → Approve & Record Decision
   → "Decision recorded · ID: DM-XXXXXXXX"

3. Past Decisions → Submit outcome: "Hypothesis confirmed"
   → C5 memory record admitted

4. Scenario Launcher → ▶ Run S2 (with memory)
   → Investigation Tab ⑦ Signature Demo
   → D1: 60 (QUALIFY) vs D3: 72 (ANSWER) · Δ = +12 pts

5. Isolation Proof:
   Same customer voice (+20 both), same quantitative evidence
   The +12 comes ONLY from C5 memory_points
   → Praxis used validated experience to improve the next decision
```

---

## Files

| Component | File |
|-----------|------|
| App shell | [`ui/streamlit_app.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/streamlit_app.py) |
| CSS + helpers | [`ui/components/design_system.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/design_system.py) |
| Home | [`ui/components/morning_briefing.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/morning_briefing.py) |
| Investigation | [`ui/components/investigation.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/investigation.py) |
| Decisions | [`ui/components/decisions.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/decisions.py) |
| Learning | [`ui/components/learning.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/learning.py) |
| Governance | [`ui/components/governance.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/governance.py) |
| Scenarios | [`ui/components/scenario_launcher.py`](file:///c:/Users/ISHIKA%20MANDAL/OneDrive/Desktop/AccentureR2BusinessKPI/ui/components/scenario_launcher.py) |
