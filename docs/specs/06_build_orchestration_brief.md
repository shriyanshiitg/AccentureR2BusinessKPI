# Praxis R2 — Build & Orchestration Brief
**Owner persona:** Build & Orchestration Engineer (maps to C6)
**Depends on:** All five prior documents (C1–C5) — every schema, formula, gateway rule, and acceptance-test suite in them is fixed ground truth to *implement*, not redesign.
**This brief is different from C1–C5.** Those were design documents. This one's deliverable is running code plus a demo. "Worked example" becomes "must actually run." "Acceptance tests" stop being Given→When→Then prose and become real automated tests.

---

## 0. The one requirement that overrides everything else below

**The system must produce a coherent result for a scenario your team did not hand-script**, through the real pipeline (C1 validation → C2 statistics → C3 reasoning → C4 narrative → C5 memory), not by replaying the S1 numbers that appear throughout the design docs. If a judge picks a different date or store and nothing happens, the prototype has failed the core R2 requirement regardless of how good the design documents are. Build and test against this before polishing anything else.

---

## 1. Lock the tech stack — one choice per layer, no options tables

Recommended, adjust only with a real reason: Python + FastAPI for orchestration; DuckDB for structured tables (Orders, Sessions, Rider/Inventory, City/Zone/Store dimensions); in-memory `rank_bm25` + `sentence-transformers` for Customer Voice retrieval (C3's hybrid+RRF design) — no vector DB needed given C1's stated low volume; Groq for the bounded LLM calls; Streamlit for the UI; a structured JSON logger for telemetry. State your final choices explicitly in the repo README.

## 2. Synthetic data generator — build this first, parameterized

Generate data matching C1's exact schemas: Orders, Sessions, Rider Ops, Customer Voice, Zone/Store dimensions. Requirements:
- At least 3 dark stores in zone Z003 (for C2's segmentation operator to have something to rank), 14+ days of clean rolling history (C2's baseline window), and the specific S1 scenario (DS041 stockout, 2026-08-15) as one generated event among others, not the only data that exists.
- A second, comparable stockout scenario at a plausible later date for the Decision 3 demo (C5 §5).
- At least one genuinely sparse-history case (a store with <3 days of data) and one case that should land `NO_DOMINANT_CONTRIBUTOR` — these are the CLARIFY/INSUFFICIENT_HISTORY scenarios the design supports but hasn't been demonstrated yet; generate them so QA can actually exercise C3's abstention paths, not just its logic.
- Parameterize the generator (seed, date range, event injection) so it can produce a scenario nobody on the team hand-picked, for the §0 resilience test.

## 3. Implement C1 as runnable validation code

The 18-row data-quality gate (C1 §12), the KPI semantic contracts as executable formulas (not just YAML descriptions), the calendar/grain reconciliation rules, and the entitlement row-filters. Run C1's own §18 acceptance tests as real automated tests against your generated data.

## 4. Implement C2's operator catalogue and planner

All 5 operators, the materiality policy per KPI, and the investigation planner's conditional sequencing. Run C2's §10 acceptance tests (including the two `INSUFFICIENT_HISTORY`/`NO_DOMINANT_CONTRIBUTOR` tests) as real automated tests.

## 5. Implement C3's hypothesis generation, retrieval, and confidence scoring

Bounded LLM call for hypothesis phrasing and Customer Voice synthesis only — the confidence formula and abstention decision table are code, not prompts. Run C3's §12 acceptance tests, including the LLM-boundary enforcement test (test 7: a `driver_type` outside C1's governed list gets rejected structurally, not by hoping the prompt worked).

## 6. Implement C4's lever mapping and persona narratives

Deterministic lever lookup table, decision-rights matrix, and the two persona narrative templates. Run C4's §8 acceptance tests, specifically test 8 — an Ops Manager narrative must never leak the zone-level GMV figure; test this against generated output, not just review it by eye.

## 7. Implement C5's memory gateway, retrieval, and confidence-boost extension

The two-entry-point admission gateway, exact-grain→zone-fallback retrieval, and the capped boost formula. Run C5's §7 acceptance tests, especially test 4 (the cap actually holds) and test 5 (a contradicted precedent lowers, not disappears).

## 8. Orchestration

Wire C1→C2→C3→C4(+C5 hook) as one state machine per finding, matching the pipeline every component's document already assumes. Log every stage transition.

## 9. Telemetry — the R2 requirement that's been open since the strategy phase

Per-finding latency, LLM call count, token usage, and estimated cost. Surface this somewhere in the UI, even minimally — Round 2 explicitly asks for it and nothing built so far has covered it.

## 10. The demo UI

Streamlit. Centerpiece: the Decision 1 vs. Decision 3 side-by-side view (C5 §5.3's exact table, rendered live from real pipeline runs, not pasted as static text). Secondary views: the two persona narratives, toggleable; an "under investigation" view for ABSTAIN findings (per C4 §3's proactive-surfacing decision); a role switcher demonstrating the entitlement filter live (C1 §15 / C4 test 8).

## 11. Acceptance — the §0 resilience test, made concrete

Run the full pipeline against at least one scenario from your generator that no one on the team pre-computed by hand. Confirm the output is internally consistent (materiality, decomposition, confidence, narrative all agree with each other) even though nobody scripted the numbers. This is your actual proof against the hardcoding risk — keep the output and be ready to show it if asked.

---

## 12. Deliverables expected back

1. Locked tech stack, stated in the repo README
2. Synthetic data generator (parameterized, multiple scenarios)
3. C1–C5 implemented as running code, with all five acceptance-test suites passing as real automated tests
4. Orchestration state machine
5. Telemetry logging + minimal UI surface for it
6. Streamlit demo UI, centered on the live Decision 1 vs. Decision 3 comparison
7. One resilience-test run against an unscripted scenario, kept as evidence

**This is the last brief before QA/Demo.** Once this comes back working, the remaining personas (QA & Adversarial Tester, Demo & Pitch Director) work against a real running system instead of design documents.
