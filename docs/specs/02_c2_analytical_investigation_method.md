# Praxis R2 — C2: Analytical Investigation Method
**Owner:** Analytics / Data Scientist (C2)
**Depends on (fixed ground truth, not re-derived here):** `C1_Data_Semantic_Foundation_v2.md` — every 🔒 LOCKED item, all 5 KPI YAML contracts, the §6 conflict policy, §7.2 day→month eligibility rule, §13 data-state model, §14 lineage ID scheme, §17 handoff contract, §18 acceptance tests.
**Out of scope here (owned by C3 — Reasoning & Retrieval Engineer):** hypothesis generation, confidence scoring, abstention policy, challenge logic. This document's output ends at *"is this movement material, and which of C1's declared drivers, with what quantified contribution, explain it"* — stated as evidence, not a ranked or challenged hypothesis.

---

## Changelog — v2 → this revision

Four targeted additions, patched in place. Nothing else in the document was rewritten or restructured.

1. **Operator 1 (§3):** added a hard `INSUFFICIENT_HISTORY` floor, distinct from the existing `baseline_confidence=LOW` tag, so a near-empty history no longer produces a number at all. Wired into the planner (§4) as a new hard-stop check, same tier as `MISSING`/`INVALID`.
2. **Two new terminal outcomes** added alongside the existing `SKIPPED` and `NON_MATERIAL`: `NO_DOMINANT_CONTRIBUTOR` (Operator 3) and `METHOD_NOT_APPLICABLE` (Operator 3, PVM sub-step only). Defined with concrete thresholds in §3 and wired into the planner sequence in §4.
3. **New §10, "C2 Acceptance Tests,"** in C1 §18's Given→When→Then format — one test per operator (5) plus one test per new outcome from items 1–2, for 8 total.
4. **New §9, "EvidencePackage Schema,"** a concrete field-level contract (YAML, in the spirit of C1's §5 KPI contracts) for exactly what C2 hands to C3 per finding, replacing the previous prose-only description in §8.

---

## 0. How C1's open items are handled here

C1 left four items explicitly ❓ OPEN or "requires human decision." None of them block C2, but three of them touch operators built below, so each gets a stated prototype handling rather than a silent default:

| C1 open item | Where it touches C2 | C2's prototype handling |
|---|---|---|
| Minimum customer tenure before counting toward RPR's "active" denominator (§11) | Materiality policy for `repeat_purchase_rate`, Operator 5 | No tenure filter applied — C2 uses C1's literal formula (≥1 completed order in the zone-month = active) as handed off. Every RPR finding carries metadata `tenure_filter=none_applied (C1 §11 OPEN)` so C3/UI can surface it as a live open assumption, not a resolved one. A 30-day-tenure re-run is listed as a §7 sensitivity check, not baked into the primary number. |
| Historical retention window per source (§2, multiple rows) | Operator 1 (baseline/seasonality) | Assume ≥90 days of usable history per store/zone is available for rolling-baseline computation. If a specific store/zone has less (e.g. a new-zone launch), Operator 1 falls back to the shorter window it actually has and tags the resulting call `baseline_confidence=LOW` rather than pretending 90 days exist. |
| GMV/line-item reconciliation tolerance — a concrete number for the `CONFLICTING` flag (§6, §12 row 11) | Operator 3 (Contribution/decomposition), which consumes `SUM(line_gmv)` | C1's DQ table only offers this as an illustration ("e.g. >₹1 or >0.5%"). C2 adopts that illustration literally as the working prototype threshold (flag `CONFLICTING` if `|order.gmv_value − SUM(line_gmv)| > ₹1` **or** `> 0.5%` of `order.gmv_value`, whichever is looser) — explicitly inherited from C1's example, not a new C2 decision, and still pending the product sign-off C1 itself flagged as outstanding. |
| `home_zone_id` fallback for zero-order customers in RPR | Operator 5 (day→month precedence check) | Inherits C1's current stated behavior unchanged: a customer with zero orders in the zone-month is not counted at all. Operator 5 does no zone-reassignment logic of its own — it consumes whatever customer/zone-month membership C1 hands off. |

---

## 1. Materiality policy — per KPI

C1's 5 KPIs split into three analytically distinct shapes: one additive absolute measure (Zone GMV), three day-grain ratios (Conversion, SLA, Stockout — each pooled-ratio, non-additive per §5), and one month-grain, distinct-count, provisional-until-close ratio (Repeat Purchase Rate). A single global z-score threshold does not work across these, so materiality is defined per KPI as a **statistical test AND a business-impact floor**, combined by strict logical AND — never a weighted score, and never one without the other.

**Combination rule (applies to all 5 KPIs):**
`material = statistically_significant(kpi, window) AND business_impact(kpi, window) ≥ floor(kpi)`
A movement that clears the statistical bar but is commercially trivial (e.g. a 2pp stockout move at a low-order store) is **not** material. A movement that is commercially large but statistically indistinguishable from normal variance (e.g. a single noisy low-volume day) is **not** material either. Both gates must pass.

**Data-state precondition (applies before either gate runs, per C1 §13):** if any required input for the KPI-day/KPI-month is `Missing` or `Invalid`, the KPI-instance is skipped from materiality evaluation entirely and flagged — never treated as "no movement." If `Stale`, the test still runs but the resulting call is tagged `evaluated_on_stale_input=true`. If `Partial`, the test runs on the represented subset only, and the output states which `dark_store_id`s/sources were actually included. If `Conflicting`, the KPI-instance is evaluated using C1's authoritative value (§6) but the finding is tagged `conflicting_input=true` so C3 can widen its confidence interval rather than treat the number as clean.

| KPI | Statistical-significance test | Business-impact floor | Notes |
|---|---|---|---|
| **Zone GMV** (additive, day-grain) | z-score of actual vs. rolling baseline: `z = (actual − baseline_mean) / baseline_std`, baseline = same-weekday rolling mean/std over the last N available days (N target 14, min 7 under the §0 retention handling); flag if `|z| ≥ 2.5` | `max(₹50,000, 2% of baseline_mean)` — a floor that scales with zone size so a small zone's noise doesn't get flagged and a large zone's real ₹50K dip doesn't get missed | GMV is the one KPI where the statistical test can run on a single day's absolute value directly — no proportion test needed. |
| **Order Conversion Rate** (ratio, day-grain, pooled) | Two-proportion z-test: numerator/denominator vs. the same rolling-baseline window's pooled numerator/denominator (pooled per §5 aggregation_rule — never averaging daily rates); flag if `p < 0.05` | `≥ 2 percentage points` movement **and** `denominator (cart-add sessions) ≥ 200` for the day | The volume gate exists because a proportion test on a tiny denominator can be "significant" on noise; C1's §9 denominator (all cart-add sessions, converted or not) is used as-is. |
| **Dark-Store Stockout Rate** (ratio, day-grain, interval-weighted) | Proportion test on the interval-weighted rate (§8) vs. rolling baseline; flag if `p < 0.05` | Floor scales inversely with the store's/zone's active-SKU-interval volume that day: `≥ 3pp` for a store/zone with normal SKU-interval volume, `≥ 6pp` if active-SKU-interval volume for the day is in the bottom quartile (low-uptime days are noisier) | Directly implements the brief's "2pp move might be statistically detectable but commercially trivial at a low-GMV store" concern by tying the floor to interval volume, which correlates with store size. |
| **Delivery SLA Adherence** (ratio, day-grain, pooled) | Proportion test vs. rolling baseline pooled rate; flag if `p < 0.05` | `≥ 3pp` **and** `≥ 30 resolved deliveries` for the day (resolved = `delivered_ts` populated per §5 denominator) | In-transit deliveries are excluded from the denominator by C1's own definition; late resolution triggers the §7.1 back-attribution recompute, which re-runs this test against the corrected day. |
| **Repeat Purchase Rate** (month-grain, distinct-count, provisional) | Relative-change threshold, not a proportion z-test — small monthly customer-count changes make a strict p-value unstable, and C1 §5 already flags the month figure as "necessarily provisional until the month closes": flag if `|Δ relative| ≥ 15%` **or** `|Δ absolute| ≥ 5pp` | `≥ 3 percentage points` | Every RPR finding generated before month-close is tagged `provisional=true` in its metadata regardless of whether it clears the bar, so C3 knows not to treat an early-month reading with the same weight as a closed month. |

---

## 2. Detection method selection matrix

One row per KPI: baseline model, the test from §1, and explicit behavior on each C1 data state (§13).

| KPI | Baseline model | Test | Stale | Partial | Missing | Conflicting |
|---|---|---|---|---|---|---|
| Zone GMV | 14-day (min 7) same-weekday rolling mean/std, recomputed from `SUM(line_gmv)` at zone×day grain | z-score vs. baseline | Run test, tag `evaluated_on_stale_input=true`, carry `as_of_ts` into the finding | Run on represented stores only; state explicitly which `dark_store_id`s were excluded that day | **Skip the KPI-day entirely.** Emit `state=MISSING` finding stub with reason code (not-yet-arrived / genuinely-absent / access-restricted); never impute zero | Use C1's authoritative `SUM(line_gmv)` value (§6); tag `conflicting_input=true` |
| Order Conversion Rate | Pooled rolling baseline (SUM numerator, SUM denominator across window, divide once) | Two-proportion z-test | Same as above | If `SRC-SESS` partial but `SRC-OMS` fresh (or vice versa), skip — a pooled ratio needs both sides complete for the day; flag `PARTIAL — denominator/numerator source mismatch` | Skip the day | Not directly applicable (no CONFLICTING state defined at this KPI's own field level — flows through only if an upstream `converted_order_id` referential break exists, in which case treat per C1 §12 row 6, i.e. unconverted, not conflicting) |
| Dark-Store Stockout Rate | Interval-weighted daily rate baseline, rolling window at native store grain, then zone rollup by §8's weighted average | Proportion test on interval-weighted rate | Same as above | Zone rollup computed only from stores with complete interval data that day; missing stores excluded from both numerator and denominator, not zero-filled | Skip the store-day (or zone-day if all constituent stores are missing) | Rare at this KPI (no two-source disagreement modeled); if the active-SKU reconciliation (§6 item 3) can't resolve, flag `CONFLICTING` and skip decomposition until resolved |
| Delivery SLA Adherence | Pooled rolling baseline at store grain, zone rollup by SUM(met)/SUM(total) | Proportion test | Same as above | Rollup excludes stores with incomplete `SRC-DEL` data that day | Skip the day | Not applicable at KPI level; late `delivered_ts` triggers §7.1 back-attribution recompute rather than a conflict flag |
| Repeat Purchase Rate | Direct month-grain distinct-customer computation (never rolled up from weeks, per §5) | Relative-change threshold | Tag `provisional=true` automatically pre-close, `evaluated_on_stale_input=true` if `SRC-OMS` itself is stale | If some days of the month are missing OMS data, the month figure is `PARTIAL` — surfaced as such, never silently computed on an incomplete month as if complete | Skip the month for this zone; do not substitute the store-level Ops-Manager proxy (§5 access note) as a stand-in for the authoritative zone figure | Individual order-level conflicts (§6 item 2) are resolved to the authoritative value before the monthly count runs; the month figure itself doesn't carry a separate conflict state |

---

## 3. Five-operator MVP catalogue

### Operator 1 — Baseline / Seasonality
- **Inputs:** KPI id, grain key (zone/store + date or zone + month), historical values at that grain for a rolling window (§0 assumes ≥90 days available; falls back to what exists).
- **Outputs:** either (a) `baseline_mean`, `baseline_std` (or pooled numerator/denominator sums for ratio KPIs), `window_size_used`, `baseline_confidence ∈ {HIGH, LOW}`; or (b) a terminal `outcome=INSUFFICIENT_HISTORY` with no numeric baseline at all — see hard floor below.
- **Hard floor — `INSUFFICIENT_HISTORY` (new):** below a fixed minimum, the operator does not return a number with a confidence tag; it returns a distinct terminal outcome instead, because a std/relative-change computed from almost no data isn't "low confidence," it's not a measurement.
  - **Day-grain KPIs (Zone GMV, Conversion, Stockout, SLA):** fewer than **3 clean same-weekday days** in the lookback → `outcome=INSUFFICIENT_HISTORY, reason="<3 clean days"`. *Why 3:* a standard deviation needs at least 2 degrees of freedom to mean anything at all; 2 raw points can only ever describe a single gap, not a spread, so any z-score built on them is manufacturing precision the data doesn't support. 3–6 clean days still clears this floor but is tagged `baseline_confidence=LOW` (unchanged from before); ≥7 is `HIGH` (target window 14, per §0).
  - **Repeat Purchase Rate (month-grain):** **zero** prior clean months → `outcome=INSUFFICIENT_HISTORY, reason="no prior month to compare"` — a relative-change test is structurally undefined with no comparison point, not just noisy. Exactly **1** prior clean month still clears the floor but is tagged `baseline_confidence=LOW`; ≥2 is `HIGH`.
  - This floor exists specifically for new-zone/new-store launches (§0's retention-window handling already anticipates thin history; this makes "thin" and "too thin to use" two different, explicitly distinguished states).
- **Assumptions:** same-weekday matching for day-grain KPIs (a Tuesday compares to prior Tuesdays, not to Monday) to avoid conflating weekly seasonality with anomaly; ratio KPIs pool raw numerator/denominator across the window before dividing, never average daily rates (§5 non-additivity notes, all four ratio KPIs).
- **Failure modes:** if the window itself contains `Stale`/`Partial` days, those days are excluded from the baseline computation (not included as if clean) and `window_size_used` reflects only clean days; if the resulting clean-day/clean-month count is at or above the hard floor but below the `HIGH` threshold, the operator returns `baseline_confidence=LOW` and downstream materiality (§1) still runs, annotated accordingly — never blocked outright, since C1's "missing ≠ negative evidence" principle extends to "thin baseline ≠ no baseline." Below the hard floor, the operator returns `INSUFFICIENT_HISTORY` and the planner (§4) stops the pipeline at that point, exactly as it already does for `MISSING`/`INVALID` C1 data states.

### Operator 2 — Detection
- **Inputs:** actual value/ratio for the target grain+period (from C1, with its data state attached), baseline output from Operator 1, the §1 test and floor for that KPI.
- **Outputs:** `statistically_significant (bool, with z or p)`, `business_impact_value`, `business_impact_significant (bool)`, `material (bool)` = AND of both.
- **Assumptions:** the §1 combination rule is a strict AND, never a weighted score; thresholds are the ones declared in §1, not re-tuned per call.
- **Failure modes:** if C1's input state is `Missing` or `Invalid`, Operator 2 does not run the test at all — it returns `material=SKIPPED, reason=<state>` and this must propagate as a distinct output value from `material=false`, so downstream code cannot conflate "checked, not material" with "never checked." On `Conflicting` input, the test runs against C1's authoritative value only, with `conflicting_input=true` carried into the output.

### Operator 3 — Contribution / Decomposition
- **Inputs:** materiality finding from Operator 2 (must be `material=true` to run — decomposition on a non-material or skipped movement is wasted work and risks manufacturing a false narrative around noise); the KPI's declared `drivers` list (from C1 §5 YAML — this operator never invents a driver not on that list); line-item/segment-level data needed for the specific KPI (`SUM(line_gmv)` at SKU/store segment for Zone GMV; session/order traces for Conversion; interval data for Stockout; delivery-event traces for SLA).
- **Outputs:** for Zone GMV specifically — a Price/Volume/Mix (PVM) split of the total gap, computed by recomputing `SUM(gmv)/SUM(units)` at each segment's *own* grain (never averaging a pre-computed ASP across a rollup, per C1's explicit non-additivity note in §5); for all KPIs — a mapped contribution estimate against each declared driver, expressed as a percentage of the total gap, summing to 100% including an explicit residual/unexplained bucket; every number carries a stated estimation method, not just a value.
- **Two additional named outcomes (new), checked as sub-steps of this operator rather than upstream, since both are structural facts about the decomposition itself, not about whether the movement is material:**
  - **`METHOD_NOT_APPLICABLE` (structural, checked first):** the PVM sub-step specifically requires an additive, units×price KPI. Per C1 §5's `additivity` field, only Zone GMV is `additive`; the other four KPIs are `non-additive (ratio)` or `non-additive (distinct-count ratio)`. Before attempting a PVM split, Operator 3 checks this flag: if `additivity != additive`, it skips the PVM sub-step entirely and tags `pvm.applicable=false, pvm.method_not_applicable_reason="non-additive KPI (§5 additivity)"`. This does **not** stop the operator — the driver-mapped contribution split (the operator's other output) still runs normally; only the PVM cross-check is structurally inapplicable.
  - **`NO_DOMINANT_CONTRIBUTOR` (threshold, checked after the driver split is computed):** if the single largest named driver's contribution is **below 30% of the total movement**, the operator does not present a decomposition table implying a lead cause — it returns `outcome=NO_DOMINANT_CONTRIBUTOR, dominant_driver=null` alongside the (still-reported) per-driver percentages. *Why 30%:* below that, the largest driver isn't meaningfully bigger than "one of several roughly-equal contributors plus noise," and handing C3 a ranked table with a token #1 driver at, say, 22% risks it being read as a finding rather than a diffuse, unresolved movement. The full per-driver breakdown and residual are still handed to C3 either way — this outcome only withholds the implicit "this is the driver" framing, it never withholds the underlying numbers.
- **Assumptions:** decomposition is evidence, not causal proof — C2 never asserts "X caused Y," only "X pattern is consistent with Z% of the gap" (causal framing is explicitly C3's job per the task brief). The GMV/line-item reconciliation tolerance from §0 is applied before any segment-level `SUM(line_gmv)` is trusted for decomposition.
- **Failure modes:** if any segment's underlying data is `Partial`, the decomposition is computed on the represented segments only and the residual bucket is widened (not shrunk) to absorb the uncertainty, with a note identifying which segment was excluded; if the *overall* KPI-instance is `Missing`, Operator 3 does not run at all (it cannot be reached — Operator 2 would already have returned `SKIPPED`); if a required segment's data is `Conflicting`, that segment's contribution is reported with an explicit wider uncertainty band rather than a point estimate.

### Operator 4 — Segmentation
- **Inputs:** zone-level material finding, C1's store→zone rollup rule for the specific KPI (§4, §8 — e.g. interval-weighted average for stockout, pooled-ratio for conversion/SLA, additive sum for GMV).
- **Outputs:** ranked list of stores within the zone by contribution to the zone-level movement, computed using the *exact* rollup rule C1 defines for that KPI (never a simple mean of store rates for ratio KPIs — C1 §18 acceptance test 4 is explicit about this).
- **Assumptions:** segmentation stops at store grain for this MVP (no SKU-level drill beyond what Operator 3 already needs for GMV decomposition); Repeat Purchase Rate segmentation uses the Ops-Manager store proxy *only* as a labeled non-authoritative view, never as an input to the zone-level finding itself (§5 access note).
- **Failure modes:** a store with `Missing` data for the day/month is excluded from the ranking entirely (not ranked as zero-contribution, which would misrepresent it as "this store had no issue" when the truth is "no data").

### Operator 5 — Day → Month Precedence Check
- **Inputs:** a candidate day-grain driver event (with `customer_id`, `event_ts`, `dark_store_id`), the target month-grain RPR movement's customer cohort (from C1, per §11's zone-attribution rule), C1's §7.2 parameters (min 1-day lag, max 45-day lookback, customer-level precedence).
- **Outputs:** `eligible (bool)`, and if eligible, a `candidate_driver_link` lineage edge from the day-grain finding to the month-grain finding.
- **Assumptions:** this is an *implementation*, not a redesign, of §7.2 — C2 does not add its own lag window or precedence logic. Zone-level or store-level co-occurrence within the same month, without customer-level linkage, is rejected by construction (C1 §18 acceptance test 9), not filtered out by a C2-side heuristic.
- **Failure modes:** if the candidate customer's linkage to the event is itself `Missing` or `Partial` (e.g. the event can't be resolved to a specific `customer_id`), the pair is marked `ineligible, reason=UNRESOLVED_CUSTOMER_LINKAGE`, not silently dropped without a reason code; if the customer is not part of the target month's active/repeat cohort at all, `ineligible, reason=CUSTOMER_NOT_IN_COHORT`.

---

## 4. Investigation planner

Rule-based sequencing, not a fixed decision tree — the sequence depends on KPI type, movement pattern, and the data state actually returned by C1 at each step.

```
1. For each KPI-instance due for evaluation (per its grain + comparison window, §1):
     a. Run Operator 1 (Baseline).
        - If outcome=INSUFFICIENT_HISTORY (new) → stop here, same tier as
          MISSING/INVALID below. Emit an INSUFFICIENT_HISTORY record with the
          clean-day/clean-month count and reason. Do not proceed to step (b)
          or Operator 2 — there is no baseline to test the actual value against.
        - If baseline_confidence=LOW, continue anyway but carry the flag
          forward — never block on a thin-but-usable baseline.
     b. Check C1's data state for the instance.
        - MISSING or INVALID  → stop here. Emit a SKIPPED record with reason code.
                                  Do not proceed to Operator 2.
        - STALE               → proceed, tag evaluated_on_stale_input=true.
        - PARTIAL             → proceed on the represented subset, tag which
                                  sources/stores are excluded.
        - CONFLICTING         → proceed using C1's authoritative value, tag
                                  conflicting_input=true.
        - FRESH               → proceed normally.
     c. Run Operator 2 (Detection) using the §1 test + floor for this KPI.
     d. If material=false → stop here. Emit a NON-MATERIAL record (still logged,
        needed for §5 precision/recall evaluation) — do not run Operators 3–5.
     e. If material=true:
        i.  Run Operator 4 (Segmentation) first if the KPI is evaluated at zone
            grain and a store-level breakdown is possible — this narrows *where*
            before Operator 3 spends effort on *why*, and is cheap relative to
            decomposition.
        ii. Run Operator 3 (Contribution/Decomposition) against C1's declared
            driver list for this KPI, using the narrowed store/segment scope
            from (i) where applicable.
            - First check C1 §5's `additivity` field for this kpi_id: if
              non-additive, skip the PVM sub-step and tag
              outcome=METHOD_NOT_APPLICABLE (new) on the pvm component only —
              the driver-mapped split below still runs.
            - After the driver split is computed, check the largest single
              driver's share: if it is <30% of the total movement, tag
              outcome=NO_DOMINANT_CONTRIBUTOR (new) instead of presenting a
              ranked table with an implied lead cause — the full per-driver
              numbers and residual still pass through unchanged.
        iii.If the KPI is Zone GMV, Conversion, Stockout, or SLA (day-grain) AND
            a plausible day→month linkage is worth checking (i.e. C3's downstream
            hypothesis space includes RPR), run Operator 5 against the current
            month's RPR cohort. This step is optional per-instance — it only runs
            when the driver identified in (ii) is a candidate type listed in RPR's
            own drivers list (§5: delivery_sla_adherence, dark_store_stockout_rate,
            order_conversion_rate — lagged, subject to §7.2).
     f. Emit the finding (FIND-KPI-... per §14) with full lineage: source →
        transformation → KPI evaluation → finding, plus any candidate_driver_link
        edges from step (iii). Populate the finding as an EvidencePackage (§9).
2. Never reorder step (b) after (c) — a data-state check always precedes the
   statistical test, per C1's "missing ≠ negative evidence" rule; running a
   test against imputed/defaulted data and only checking state afterward is
   the exact failure mode C1 §13 forbids.
3. INSUFFICIENT_HISTORY (step a), SKIPPED (step b), and NON_MATERIAL (step d)
   are all hard stops at their respective tiers — none of them fall through to
   later steps. METHOD_NOT_APPLICABLE and NO_DOMINANT_CONTRIBUTOR (step e.ii)
   are not hard stops; they are sub-outcomes attached to an otherwise-complete
   Operator 3 run, because the movement is already known to be material by the
   time either is checked.
```

---

## 5. Worked S1 scenario — end to end

**Signal.** Zone GMV, zone `Z003`, day `2026-08-15`.

**Step 1 — Baseline (Operator 1).** 14-day same-weekday rolling mean for Z003: `baseline_mean = ₹18,40,000`, `baseline_std = ₹45,000` (illustrative rolling volatility for this synthetic zone; `window_size_used = 14`, `baseline_confidence = HIGH`).

**Step 2 — Data state.** `SRC-OMS` fresh for the day; no `Partial`/`Conflicting`/`Missing` flags on the relevant orders. Proceed normally.

**Step 3 — Detection (Operator 2).**
- Actual = ₹16,70,000. Δ = −₹1,70,000 (**−9.24%**).
- `z = (16,70,000 − 18,40,000) / 45,000 = −3.78` → `|z| ≥ 2.5` → **statistically significant**.
- Business floor = `max(₹50,000, 2% of 18,40,000 = ₹36,800) = ₹50,000`. `|Δ| = ₹1,70,000 ≥ ₹50,000` → **business-impact significant**.
- `material = true`.
- KPI instance ID (C1 §14 format): **`KPI-zone_gmv-Z003-20260815`**.

**Step 4 — Segmentation (Operator 4).** Store-level breakdown of the zone shortfall (additive rollup, §4) points to `DS041` as the dominant contributor, with the remaining stores in Z003 showing movement within normal range.

**Step 5 — Decomposition (Operator 3), against Zone GMV's declared drivers** (`dark_store_stockout_rate, delivery_sla_adherence, order_conversion_rate, discount_applied, competitor_dark_store_opening, demand_spike` — C1 §5):

*Zone-level PVM cross-check first* (recomputing ASP as `SUM(gmv)/SUM(units)` at zone grain, never averaging a pre-computed ASP): baseline units 40,000 @ ASP ₹46.00; actual units 37,150 @ ASP ₹44.96. Volume effect `= (37,150 − 40,000) × 46.00 = −₹1,31,100` (≈77% of Δ); price/ASP effect `= (44.96 − 46.00) × 37,150 = −₹38,600` (≈23% of Δ) — sum ≈ −₹1,69,700, within rounding of the observed −₹1,70,000 gap. This confirms the movement is predominantly volume-driven, with a smaller ASP/discount component — consistent with a supply-side (stockout) event rather than a demand-side price change.

*Driver-mapped split* (quantified contribution with explicit uncertainty — not a confirmed cause; that judgment is C3's):

| Driver (from C1 §5 list) | Estimated contribution | Method / evidence |
|---|---|---|
| `dark_store_stockout_rate` | **−₹93,500 (55.0%)** | `DS041`, `SKU-2207` + 3 related SKUs, collapsed active/stockout intervals (§8) show ~14.5 of 24 active-SKU-hours in stockout that day, feeding `KPI-dark_store_stockout_rate-DS041-20260815`. Estimated via counterfactual: expected units at pre-stockout run-rate minus actual units sold during the stockout window, valued at those SKUs' own ASP — **lost units, not a price effect**, per the segmentation this decomposition must respect. |
| `delivery_sla_adherence` | **−₹34,000 (20.0%)** | Same-day SLA breaches at `DS041` (elevated dispatch delay correlated with reduced same-session reorder/upsell and some checkout-time cart abandonment when the app surfaced a longer ETA) — estimated from cancelled/abandoned high-value carts at `DS041` on the day. |
| Residual / unexplained | **−₹42,500 (25.0%)** | Broadly corresponds to the zone-aggregate ASP/discount drift identified in the PVM cross-check above plus ordinary demand noise not attributable to a specific driver event. Explicitly left as residual rather than force-fit to `discount_applied`, `competitor_dark_store_opening`, or `demand_spike` — C2 has no direct evidence isolating those three for this specific day; C3 should treat this bucket as open investigation space, not as evidence against those drivers. |
| **Total** | **−₹1,70,000 (100%)** | Sums exactly to the observed gap by construction; the two named drivers plus residual are the full accounting, not independent claims. |

**Step 6 — Day→Month precedence check (Operator 5).** Candidate: does the `DS041` stockout event on `2026-08-15` (customer-resolved instances of it) qualify as an eligible candidate explanation for a Repeat Purchase Rate movement in `Z003` for August 2026?

- **Eligible pair:** customer `CUST-771204` was affected by the `SKU-2207` stockout at `DS041` on `2026-08-15T11:40:00+05:30` (same event traced in C1 §14's lineage example via `stock_event_id=SE-9931`). Their next order in Z003 is `order_ts = 2026-08-22`, and they also have a prior order on `2026-08-03`, making them a 2-order (repeat) customer in August's cohort. Check: customer-level linkage ✓; `driver_event_ts (2026-08-15) < subsequent_order_ts (2026-08-22)` ✓; lag = 7 days ≥ 1-day minimum ✓; lookback well within 45 days ✓. **→ ELIGIBLE.**
- **Rejected pair (illustrating C1 §18 acceptance test 9):** customer `CUST-556190` also shows up at `DS041` on `2026-08-15`, but their only other August order is on `2026-08-15` itself (same-day association, 0-day lag). Same-month co-occurrence alone, without the ≥1-day minimum lag, is explicitly rejected by §7.2. **→ INELIGIBLE, reason = MIN_LAG_VIOLATION.**

**Finding IDs handed to C3:**
- `FIND-KPI-zone_gmv-Z003-20260815-01` — the material Zone GMV finding (§ Step 3–5 above).
- `FIND-KPI-dark_store_stockout_rate-DS041-20260815-01` — the upstream stockout finding referenced by the decomposition (same ID as C1 §14's own worked lineage example, reused here rather than re-minted, since it is the same underlying event).
- `FIND-KPI-repeat_purchase_rate-Z003-202608-01` — the RPR-side finding the eligible day→month link attaches to, tagged `provisional=true` (August not yet closed as of the analysis date).
- Lineage edge: `(from_id=FIND-KPI-dark_store_stockout_rate-DS041-20260815-01, to_id=FIND-KPI-repeat_purchase_rate-Z003-202608-01, edge_type=candidate_driver_link)` — stored in C1's generic `lineage_edge` table (§14), so C3's hypothesis/evidence objects and any later Memory-persona decision/outcome records attach without a schema change.

---

## 6. Data-state handling summary (cross-reference)

This is stated per-operator in §3 (each operator's "Failure modes"); the cross-cutting rule that governs all of them:

- **Missing/Invalid → skip, never zero.** No operator in this catalogue ever substitutes zero, a null-defaulted value, or "absence of signal" for a `Missing` input (C1 §13, restated at the planner level in §4 step 1b).
- **Stale → run, but tag.** Every operator that consumes a `Stale` input still runs — C1 hands stale data downstream deliberately, not to be discarded — but every output derived from it carries `evaluated_on_stale_input=true` through to the finding.
- **Partial → run on the represented subset, state the gap.** Every partial-input output explicitly lists which stores/sources were excluded, rather than presenting a silently-narrowed number as if it were complete.
- **Conflicting → use C1's authoritative value, tag the disagreement.** C2 never re-resolves a conflict C1 already declared unreconcilable (§6) — it uses the authoritative figure C1 designates and passes the conflict flag + both provenances through so C3 can widen uncertainty rather than treat the number as clean.

---

## 7. Evaluation metrics

- **Detection precision/recall.** Against a labeled synthetic eval set containing the §5 worked example (`Z003`, `2026-08-15`, labeled MATERIAL) and at least one deliberately non-material counter-example — e.g. `Z003`, `2026-08-20`: baseline ₹18,50,000, actual ₹18,10,000, Δ = −₹40,000 (−2.2%), `z = −0.89` (below the 2.5 threshold) and `₹40,000 < ₹50,000` floor → correctly `material=false`. Precision = TP/(TP+FP), recall = TP/(TP+FN), computed over the full labeled set the synthetic-data generator produces (ground truth = whether an anomaly was actually injected for that KPI-instance).
- **Driver-ranking top-3 hit rate.** For each material finding, rank the KPI's declared drivers (§5 list, e.g. 6 for Zone GMV) by `|estimated contribution|`. Hit = the synthetic generator's actually-injected driver(s) appear within the top 3 ranked declared drivers. In the §5 worked example: ranked by magnitude, `dark_store_stockout_rate` (55%) and `delivery_sla_adherence` (20%) are ranks 1–2 of the 6 declared drivers → both injected drivers land in the top 3 → hit.
- **Contribution/decomposition error.** `MAPE = mean(|estimated_contribution − ground_truth_contribution|) / |total_movement|` across the eval set, computed against the synthetic generator's known injected effect sizes (available because the demo dataset is synthetic and ground truth is authored, not observed) — this is only measurable pre-launch/in-demo; a production version would need a slower proxy (e.g. analyst-labeled contribution review) since real-world ground truth for "true contribution" doesn't exist independently of the decomposition itself.

---

## 8. Summary — what this hands to C3

Per the task brief's requirement, C3 receives, before its own brief is drafted:
1. The worked example's driver-contribution numbers (§5, Step 5 table) — quantified, with stated estimation method and an explicit residual bucket, never presented as confirmed causes.
2. The confirmed day→month eligibility link (§5, Step 6) — one eligible pair, one rejected pair, both with stated reasons.
3. The exact finding IDs and the lineage edge connecting them (§5, "Finding IDs handed to C3"), stored in C1's generic edge table so no schema change is needed downstream.
4. The full materiality/detection/decomposition/segmentation/precedence machinery (§1–§4) that produced them, so C3 can trust the inputs it's building hypothesis and evidence-state objects against rather than re-deriving any of it.

---

## 9. EvidencePackage schema (new)

The concrete artifact C2 hands to C3 per finding — one `EvidencePackage` per KPI-instance evaluated, regardless of which terminal outcome it lands on. Every field below is populated or explicitly nulled; C3 never has to infer absence from a missing key. Format mirrors C1's §5 KPI-contract style (a machine-readable schema, not just a table description).

```yaml
evidence_package:
  # identity & lineage
  finding_id: string              # C1 §14 format: FIND-{kpi_instance_id}-{seq}
  kpi_instance_id: string         # C1 §14 format: KPI-{kpi_id}-{grain_key}-{period}
  kpi_id: enum[zone_gmv, order_conversion_rate, dark_store_stockout_rate,
               delivery_sla_adherence, repeat_purchase_rate]
  grain_key: string                # e.g. Z003, DS041 — per this kpi_id's C1 §5 grain field
  period: string                   # ISO date (day-grain KPIs) or ISO year-month (RPR)
  created_at: timestamp            # ISO-8601, IST
  source_version: string           # propagated from the C1 lineage record, §14

  # terminal outcome — every EvidencePackage has exactly one
  terminal_outcome: enum[EVALUATED, SKIPPED, NON_MATERIAL, INSUFFICIENT_HISTORY,
                          NO_DOMINANT_CONTRIBUTOR]
  terminal_outcome_reason: string | null
    # required whenever terminal_outcome != EVALUATED — e.g. the C1 data-state
    # code for SKIPPED, "<3 clean days" for INSUFFICIENT_HISTORY, etc.

  # data-state passthrough (C1 §13) — always populated regardless of outcome
  data_state: enum[FRESH, STALE, PARTIAL, MISSING, CONFLICTING, INVALID]
  evaluated_on_stale_input: bool
  partial_sources_excluded: list[string] | null   # dark_store_id/source ids, if PARTIAL
  conflicting_input: bool
  conflicting_provenance: list[string] | null      # both source values + provenance, if CONFLICTING

  # baseline — Operator 1 (§3). Null if terminal_outcome=INSUFFICIENT_HISTORY.
  baseline:
    baseline_mean: decimal | null
    baseline_std: decimal | null
    window_size_used: int
    baseline_confidence: enum[HIGH, LOW] | null

  # detection — Operator 2 (§3). Null if terminal_outcome in
  # {SKIPPED, INSUFFICIENT_HISTORY}.
  detection:
    actual_value: decimal
    delta_absolute: decimal
    delta_relative: decimal
    statistically_significant: bool
    test_statistic: decimal          # z or p, per this kpi_id's §1 test
    business_impact_value: decimal
    business_impact_significant: bool
    material: bool

  # decomposition — Operator 3 (§3). Present only if material=true.
  decomposition:
    pvm:
      applicable: bool                                # false for the 4 non-additive KPIs
      method_not_applicable_reason: string | null      # e.g. "non-additive KPI (§5 additivity)"
      volume_effect: decimal | null
      price_effect: decimal | null
      mix_effect: decimal | null
    drivers:
      - driver_name: string           # must be a member of this kpi_id's C1 §5 `drivers` list
        contribution_value: decimal
        contribution_pct: decimal
        method: string                # estimation method / evidence description
    residual_pct: decimal
    residual_note: string
    dominant_driver: string | null    # null if no driver clears the 30% dominance threshold (§3)
    no_dominant_contributor: bool     # true iff dominant_driver is null

  # segmentation — Operator 4 (§3). Null if not applicable at this KPI's grain.
  segmentation:
    ranked_stores: list[{dark_store_id, contribution_value, contribution_pct}] | null
    excluded_stores: list[string]     # Missing-data stores, excluded not zero-filled

  # day→month precedence links — Operator 5 (§3). Empty list if none checked/applicable.
  day_month_links:
    - candidate_customer_id: string
      driver_event_ts: timestamp
      subsequent_order_ts: timestamp | null
      eligible: bool
      reason: string                  # e.g. MIN_LAG_VIOLATION, CUSTOMER_NOT_IN_COHORT
      linked_finding_id: string | null   # the RPR-side finding_id this attaches to, if eligible

  # lineage — C1 §14 generic edge-table references
  lineage_chain: list[string]         # ordered IDs, source → transformation → KPI → finding
  lineage_edges:
    - from_id: string
      to_id: string
      edge_type: string
```

Applied to the §5 worked example, the `zone_gmv` finding's `EvidencePackage` would carry `terminal_outcome=EVALUATED`, `decomposition.pvm.applicable=true` (Zone GMV is C1's one additive KPI), `decomposition.dominant_driver="dark_store_stockout_rate"` (55% clears the 30% floor, so `no_dominant_contributor=false`), one `day_month_links` entry with `eligible=true` for `CUST-771204` and one with `eligible=false, reason=MIN_LAG_VIOLATION` for `CUST-556190`, and `lineage_edges` containing the `candidate_driver_link` to the RPR finding — i.e., every number already walked through in §5, now in the exact shape C3 receives it.

---

## 10. C2 Acceptance Tests

In C1 §18's Given→When→Then format. At least one test per operator; tests 2 and 6–7 specifically cover the new outcomes added in this revision.

1. **Given** a store with 14+ days of clean same-weekday history for Zone GMV, **when** Operator 1 runs, **then** it returns `baseline_confidence=HIGH` with a numeric `baseline_mean`/`baseline_std`, not a terminal outcome.
2. **Given** a store with only 1 day of history (e.g. a store that went live yesterday), **when** Operator 1 runs, **then** it returns `outcome=INSUFFICIENT_HISTORY` with `reason="<3 clean days"` — **not** a `baseline_confidence=LOW` number — and the planner stops before Operator 2 runs.
3. **Given** a KPI-instance whose required C1 input is `state=MISSING`, **when** the planner reaches step (b), **then** it emits a `SKIPPED` record and does not invoke Operator 2, Operator 3, Operator 4, or Operator 5.
4. **Given** a Zone GMV day where `|z| < 2.5` (statistically insignificant) even though the ₹ gap exceeds the business floor, **when** Operator 2 evaluates materiality, **then** the AND rule yields `material=false` and the record is emitted as `NON_MATERIAL`, not partially flagged.
5. **Given** a material Zone GMV finding, **when** Operator 3 runs its PVM sub-step, **then** it recomputes ASP as `SUM(gmv)/SUM(units)` at the target segment grain rather than averaging a pre-computed ASP across the rollup (C1 §5 non-additivity note).
6. **Given** a material Dark-Store Stockout Rate finding (a non-additive ratio KPI per C1 §5), **when** Operator 3 checks the `additivity` field before decomposing, **then** it skips the PVM sub-step and tags `pvm.applicable=false, method_not_applicable_reason="non-additive KPI (§5 additivity)"`, while still producing the driver-mapped contribution split.
7. **Given** a material finding whose largest single named driver contributes 22% of the total movement (no driver clears 30%), **when** Operator 3 finishes the driver split, **then** it returns `outcome=NO_DOMINANT_CONTRIBUTOR, dominant_driver=null` while still passing through the full per-driver percentages and residual — it does not silently present the 22% driver as if it were a lead cause.
8. **Given** a zone-level material finding with one constituent store's data in `state=MISSING` for the day, **when** Operator 4 ranks stores by contribution, **then** that store is excluded from the ranked list entirely, not included with a zero-contribution value.
9. **Given** a candidate day-grain driver event and a specific customer's subsequent order 7 days later within the same month, **when** Operator 5 checks eligibility, **then** it returns `eligible=true` (customer-level linkage, ≥1-day lag, ≤45-day lookback all satisfied, per C1 §7.2).
10. **Given** a candidate day-grain driver event and the same customer's only other order on the identical calendar day (0-day lag), **when** Operator 5 checks eligibility, **then** it returns `eligible=false, reason=MIN_LAG_VIOLATION` — same-day/same-month co-occurrence alone is rejected by construction (C1 §18 acceptance test 9), not accepted with a caveat.
