# BUILD_DECISIONS.md — Praxis R2 Autonomous Build Log

Every item here follows the protocol in 00_Master_Handoff §4:
what was ambiguous → what was chosen → why.
Entries are append-only, newest at the top.

---

## BD-001 — GMV/line-item reconciliation tolerance
- **Ambiguous:** C1 §12 row 11 states the tolerance as illustrative ("e.g. >₹1 or >0.5%"), not a fixed number.
- **Chosen:** `|order.gmv_value − SUM(line_gmv)| > ₹1 OR > 0.5% of order.gmv_value` — the exact illustration from C1, adopted literally.
- **Why:** C2 §0 explicitly inherits this as C2's own prototype threshold ("adopts that illustration literally as the working prototype threshold"). Using it here is a direct implementation of C2's own stated decision, not a new C6 choice.

## BD-002 — Customer tenure filter for Repeat Purchase Rate
- **Ambiguous:** C1 §11 leaves minimum customer tenure before counting toward RPR's active denominator as ❓ OPEN.
- **Chosen:** No tenure filter applied. Any customer with ≥1 completed order in the zone-month is counted as "active" per C1's literal formula.
- **Why:** C2 §0 states exactly this handling and requires every RPR finding to carry `tenure_filter=none_applied (C1 §11 OPEN)` metadata. Implemented as specified.

## BD-003 — Month-end evidence anchor for RPR (Customer Voice window)
- **Ambiguous:** C1 §7.1's `[D−7, D+2]` window is defined for day-grain findings. C3 §3 notes that for month-grain RPR findings, "C1 does not define a day-anchor for month-grain evidence matching and one is required."
- **Chosen:** Anchor D = last calendar day of the target month (month-end).
- **Why:** C3 §3 explicitly states this as a prototype assumption. Direct implementation.

## BD-004 — ₹15,000 / 2-rider auto-execution ceilings
- **Ambiguous:** C4 §2 flags these as ❓ OPEN for product sign-off.
- **Chosen:** ₹15,000 per-SKU-store restock ceiling; 2 additional riders per shift ceiling.
- **Why:** C4 §2 sets these as the prototype defaults pending product sign-off. Kept exactly as specified.

## BD-005 — ABSTAIN finding surfacing
- **Ambiguous:** C4 §3 resolves this as a prototype assumption.
- **Chosen:** ABSTAIN findings are query-visible only; never pushed to proactive alert channel.
- **Why:** C4 §3's explicit prototype assumption. Direct implementation.

## BD-006 — LLM layer
- **Chosen:** Groq API (llama-3.3-70b-versatile model) for bounded LLM calls per C3 §9 / C4 §6 boundary tables. API key provided by user.
- **Why:** Build Brief §1 recommends Groq. Key provided directly.

## BD-007 — Historical retention assumption
- **Ambiguous:** C1 §2 marks retention window per source as ❓ OPEN.
- **Chosen:** 90 days for all sources in the synthetic generator (matching C2 §0's stated assumption for baseline computation).
- **Why:** C2 §0 explicitly states "assume ≥90 days of usable history per store/zone is available" as its prototype handling. Generator produces this.

## BD-008 — Embedding model for Customer Voice retrieval
- **Ambiguous:** Build Brief §1 says "sentence-transformers" but doesn't specify which model.
- **Chosen:** `all-MiniLM-L6-v2` — fast, small, well-suited to short domain-narrow text (quick-commerce complaints).
- **Why:** Smallest model that handles the domain; C3 §3 explicitly notes CV is "low-volume, short free text, domain-narrow." A larger model would not improve precision on this corpus meaningfully.

## BD-009 — DuckDB persistence path
- **Chosen:** `data/praxis.duckdb` — created at first run, reused across runs.
- **Why:** Enables the memory state to persist between pipeline runs so the Decision 1 → Decision 3 demo works across Streamlit sessions.

## BD-010 — Second stockout date for Decision 3 demo
- **Ambiguous:** Build Brief §2 says "a plausible later date."
- **Chosen:** 2026-08-22 (7 days after S1's 2026-08-15). Same weekday (Saturday), same store (DS041), same driver type (dark_store_stockout_rate).
- **Why:** 7 days satisfies C1 §7.2's ≥1-day lag and ≤45-day lookback. Same weekday matters for Operator 1's same-weekday baseline assumption. Makes the Decision 3 comparison cleanest.
