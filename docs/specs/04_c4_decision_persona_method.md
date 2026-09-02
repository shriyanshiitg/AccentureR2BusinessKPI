# Praxis R2 — C4: Decision & Persona Method
**Owner:** Decision & Persona Designer (C4)
**Depends on (fixed ground truth, not re-derived here):** `C1_Data_Semantic_Foundation_v2.md` — persona table (§15), entitlement enforcement, KPI `drivers` lists (§5), Customer Voice evidence role (§10). `04_C2_Analytical_Investigation_Method.md` (patched) — the five-operator catalogue and `EvidencePackage` schema (§9). `06_C3_Reasoning_Retrieval_Method.md` — the `HypothesisPackage` schema (§11), all four `decision.outcome` values, and the worked S1 example's actual output (§10.5–10.6), treated as fixed.
**Out of scope here:** memory storage/admission/supersession (C5); UI rendering/orchestration (C6). This document defines the `DecisionPackage` content and the two persona narratives; C6 renders what C4 produces.
**Decision Classification Ledger:** as C1–C3, every consequential call below is tagged 🔒 LOCKED (implement exactly as specified), 🧪 PROTOTYPE ASSUMPTION (deliberate synthetic-demo simplification), or ❓ OPEN (requires a product decision C4 cannot make unilaterally).

---

## 0. The actual worked example this document builds from

C3's S1 outcome for `FIND-KPI-zone_gmv-Z003-20260815-01` is **not** a confident answer:

- `decision.outcome = QUALIFY`, `scope = finding`
- Leading hypothesis `HYP-FIND-KPI-zone_gmv-Z003-20260815-01-01` — `driver_type=dark_store_stockout_rate`, `contribution_pct=55.0%`, `confidence.band=LOW` (`score=16.1`), capped further in spirit (not arithmetically, since 16.1 is already inside `LOW`) by a mixed Customer Voice signal (one `Fresh` `supports` record, one `Stale` `contradicts` record).
- Secondary hypothesis `HYP-...-02` — `driver_type=delivery_sla_adherence`, `contribution_pct=20.0%`, `confidence.band=LOW` (`score=35.4`), independently corroborated (`+20` CV score, `Fresh` `supports`, zero `contradicts`).
- Residual hypothesis `HYP-...-03` — `contribution_pct=25.0%`, `status=unresolved` by construction, `confidence.band=INSUFFICIENT`.
- `caveat_text` (C3 §10.5, verbatim, this is the caveat C4 must never drop): *"Quantitative decomposition points to a stockout event at DS041 as the largest single contributor (55%), but Customer Voice evidence is mixed — one fresh corroborating complaint and one stale record suggesting availability had recovered by the window's end — so this is presented as the leading explanation, not a confirmed one. A secondary SLA-related contributor (20%) is independently corroborated. 25% of the movement remains unexplained."*
- A separate RPR-side hypothesis (day→month link via `CUST-771204` to `FIND-KPI-repeat_purchase_rate-Z003-202608-01`) is `decision.outcome=ABSTAIN`, `scope=hypothesis`, `provisional=true`, `hard_caps_applied=["provisional_rpr_link"]`, band forced to `LOW` regardless of computed score.

**Consequence for C4's design:** persona narrative construction must not quietly manufacture more confidence than C3 computed. A fluent recommendation sentence can sound authoritative regardless of the underlying band. Per §0 of the task brief, this has to be structurally prevented — the schema in §4 below makes the caveat field mandatory-non-null whenever `outcome≠ANSWER`, and §6 makes the LLM's boundary explicit, so no persona narrative for this finding can ever read as an unqualified `ANSWER`.

---

## 1. Business lever / action catalogue

Eight levers, each tagged with the `driver_type`(s) from C1 §5's KPI `drivers` lists it is a plausible response to. C4 does not invent drivers — every tag below is a literal member of some KPI's C1 `drivers` list, or the literal value `"residual"`/a structural condition (per C3 §1's `driver_type` constraint, inherited here).

| # | Lever | Plausible `driver_type` response to | Grain | Notes |
|---|---|---|---|---|
| L1 | Restock a specific SKU at a specific dark store | `dark_store_stockout_rate` (also `stockout` at the KPI-8's own driver level) | store × SKU | The direct, narrowest response to a stockout-attributed finding. |
| L2 | Cross-store inventory transfer (move stock from a neighboring store with surplus) | `dark_store_stockout_rate` | store pair, within zone | Only viable when a neighboring store's inventory state (C1 §13) is `Fresh`/known-surplus for the same SKU; crosses the Ops Manager's single-store entitlement boundary (C1 §15) by construction — see §2. |
| L3 | Add rider capacity for a shift | `rider_capacity` (feeds `delivery_sla_adherence`; also listed as a `dark_store_stockout_rate` driver via replenishment-delivery capacity) | store × shift | Responds to SLA-attributed findings where the underlying cause is dispatch/rider throughput, not stock itself. |
| L4 | Approve a time-boxed local promo | `order_conversion_rate`, `discount_applied`, `demand_spike`, `competitor_dark_store_opening` | zone (or store, if C1's store-level conversion detail is used) | Demand-side lever; never the correct response to a supply-side (stockout) finding — see §3 rendering rule. |
| L5 | Adjust dispatch scheduling / rider shift pattern for a catchment-density or weather-driven SLA dip | `catchment_density`, `weather`, `dispatch_delay` | store × shift | Distinct from L3: L3 adds headcount, L5 reschedules existing capacity. Useful when the driver is structural (density/weather) rather than a capacity shortfall. |
| L6 | Flag a competitor dark-store opening for zone-level pricing/promo strategy review | `competitor_dark_store_opening` | zone | Escalation-adjacent: C4 does not decide pricing strategy, it routes the signal to the Zone Business Head for a strategic call outside the auto-executable lever set. |
| L7 | Escalate an unresolved/contradicted finding for manual investigation | any — specifically triggered by `hard_caps_applied` containing `cv_contradicts_only`, `conflicting_input`, or by `terminal_outcome=NO_DOMINANT_CONTRIBUTOR`/`SKIPPED` | finding or hypothesis | The correct response whenever C3's own evidence disagrees with itself; never paired with an auto-executed action in the same `DecisionPackage`. |
| L8 | Monitor, no action | any `LOW`-band finding without a contradiction/conflict hard cap, any `CLARIFY`, any `NON_MATERIAL` | finding or hypothesis | The **default**, not a fallback of last resort. Per §0's discipline, a `LOW`-band finding recommending an executable action is the failure mode this catalogue exists to prevent — see §3. |

---

## 2. Decision rights matrix — concrete thresholds

C1 §15 already draws a hard **entitlement** boundary: the Dark-Store Ops Manager's row-level scope is `dark_store_id = user.assigned_store` only, with explicit restriction on "zone-level totals/rollups" and "cross-store aggregation." C4 treats this as a **floor that thresholds narrow further, never as a boundary thresholds can widen** — 🔒 LOCKED, inherited from C1, not a C4 decision.

**Rule 1 (🔒 LOCKED, inherited):** any lever whose scope crosses a store boundary, or whose action type is explicitly reserved to the Zone Business Head per C1 §15/the task brief (cross-store transfer, promo authorization), is **never** auto-executable by a Dark-Store Ops Manager regardless of INR value. Scope, not size, is the first gate.

**Rule 2 (🧪 PROTOTYPE ASSUMPTION — concrete numbers, product sign-off pending):** within the store-scoped levers the Ops Manager *is* entitled to touch, a further INR/count ceiling determines auto-execution vs. escalation:

| Lever | Auto-executable by Dark-Store Ops Manager | Escalates to Zone Business Head |
|---|---|---|
| L1 — Restock specific SKU at own store | Single restock order ≤ **₹15,000** (per SKU-store action) | Order > ₹15,000, or restock request touching >5 SKUs in one action (bundling risk) |
| L2 — Cross-store inventory transfer | **Never** (Rule 1 — crosses store scope) | Always |
| L3 — Add rider capacity for a shift, own store | ≤ **2 additional riders** per shift | > 2 riders per shift, or any change spanning >1 shift |
| L4 — Approve time-boxed local promo | **Never** (Rule 1 — pricing/discount authority is Zone-level per the task brief) | Always |
| L5 — Adjust dispatch/shift scheduling, own store | Reschedule within existing approved headcount | Any request that implicitly increases headcount (routes through L3's ceiling instead) |
| L6 — Flag competitor opening for strategy review | **Never** (informational escalation only, no execution) | Always (routing, not approval) |
| L7 — Escalate unresolved/contradicted finding | Either persona may trigger the escalation itself (raising a flag is not an executable action) | Zone Business Head owns disposition of the escalation |
| L8 — Monitor, no action | Either persona, no approval required | N/A |

**Reasoning for the ₹15,000 / 2-rider numbers:** these are illustrative prototype ceilings, not derived from a cost model neither source brief supplies. They are set deliberately low relative to the zone's daily GMV scale (Z003's baseline is ~₹18.4L/day, so ₹15,000 is ~0.08% of one day's zone GMV) so that the auto-execution path stays genuinely low-risk, and any restock large enough to plausibly move the KPI meaningfully routes through Zone Business Head review rather than an automated ceiling. **This is explicitly ❓ OPEN for product sign-off** — same status as C1's own GMV reconciliation tolerance (C1 §"Requires human/product decision") and C2's inherited literal adoption of C1's illustrative number (C2 §0) — C4 follows that project-wide pattern rather than inventing a differently-justified number.

---

## 3. Decision.outcome → narrative template mapping

A distinct rendering rule per C3 outcome, plus the `NON_MATERIAL` `answer_without_hypothesis` case. Every rule below routes through the DecisionPackage schema (§4) so the constraint is structural, not just a template-authoring convention.

| `decision.outcome` | Narrative rule | Lever selection |
|---|---|---|
| `ANSWER` | Confident recommendation, single leading action stated plainly. `confidence.band` is passed through and displayed even here — `ANSWER` only occurs at `HIGH` band per C3 §7, so display is a confirmation, not a hedge. | Deterministic mapping (§1) from the named hypothesis's `driver_type` to its lever(s); highest-scoring lever if multiple map. |
| `QUALIFY` | Recommendation still offered, but `caveat_text` (C3's field, verbatim or lightly rendered for persona register — **never dropped, never paraphrased into something softer**) is rendered inline in the narrative body, not a footnote. **This is the S1 case — built first, §7.** | Same deterministic mapping as `ANSWER`, but the `DecisionPackage.confidence` field carries the `QUALIFY`-level band (`LOW`/`MEDIUM`), and the narrative template must not use action language stronger than the lever's own "auto-executable" framing allows (see §6 boundary). |
| `CLARIFY` | No action recommended. C3's `clarifying_question` is rendered as the actual next step ("we need X before recommending an action"), sourced from a real C2 Operator-4 narrowing dimension per C3 §7 — C4 never invents a clarifying question of its own. | `L8` (monitor) only, with the clarifying question attached as the "what would unlock a recommendation" field. |
| `ABSTAIN` | State plainly, per `abstain_reason`, that evidence is insufficient or contradictory. **Never rendered as a proactive alert** — see decision below. | `L7` (escalate) if `abstain_reason` implies a contradiction/conflict worth investigating; `L8` (monitor, no action) if the reason is simply `INSUFFICIENT_HISTORY`/`SKIPPED` with nothing yet to investigate. |

**ABSTAIN proactive-surfacing decision (❓ OPEN in the source docs, resolved here 🧪 PROTOTYPE ASSUMPTION):** an abstained finding is **not** pushed to either persona's proactive/alert channel. Reasoning: `ABSTAIN` by definition means C3 has nothing confident to say — pushing "we don't know" as an interruptive alert trains the persona to distrust or ignore the alert channel over time, which is the same noise-risk the brief flags. Instead, abstained findings are retained and **query-visible only** — they appear if the persona explicitly asks ("what's going on with Z003 GMV this week") or browses an "under investigation" view, where the `abstain_reason` is shown plainly. The one exception: if `abstain_reason` corresponds to an access-restriction state (C1 §13 `MISSING — access-restricted`), the persona sees this the same way — never as an alert, but never silently hidden either, since C1 §15's partial-evidence rule requires the response to "explicitly identify which evidence was unavailable and why" whenever the persona does query.

**`NON_MATERIAL` / `answer_without_hypothesis` surfacing decision (❓ OPEN in the source docs, resolved here 🧪 PROTOTYPE ASSUMPTION):** surfaced, but **passively, not as a proactive alert** — included in the relevant persona's periodic status roll-up (weekly for Zone Business Head, in-workflow daily view for Ops Manager) as a "no material movement" line item, never suppressed entirely. Reasoning: unlike `ABSTAIN`, `NON_MATERIAL` is C3's own confident conclusion (C3 §7: "this is C2's own confident conclusion... a clean negative result, not an abstention"), so it carries real information value ("this KPI is behaving normally") without the noise risk of an "insufficient evidence" push. It is withheld from the interruptive alert channel for the same reason `ANSWER`-band confident findings above a materiality floor *are* pushed there and non-movements are not: an alert channel exists to flag things that need attention, and "nothing happened" does not.

---

## 4. DecisionPackage schema

```yaml
decision_package:
  # identity & lineage — the pointer chain back through C3 → C2 → C1, nothing here
  # is un-traceable to its source (task brief §4 requirement)
  decision_package_id: string          # DEC-{finding_id}-{seq}, C1 §14 ID-scheme style
  finding_id: string                   # FK to C2 EvidencePackage.finding_id
  hypothesis_package_ref: string       # FK to C3 HypothesisPackage — full object retrievable by ref
  evidence_package_ref: string         # FK to C2 EvidencePackage — passthrough, C3 already carries this
  lineage_chain: list[string]          # C1 §14 chain, passed through unchanged (source → ... → finding)
  generated_at: timestamp              # ISO-8601, IST

  # outcome passthrough — never re-derived, never re-decided at this layer
  source_decision_outcome: enum[ANSWER, QUALIFY, CLARIFY, ABSTAIN]   # C3 HypothesisPackage.decision.outcome, verbatim
  source_decision_scope: enum[finding, hypothesis]                    # C3 HypothesisPackage.decision.scope, verbatim

  # the locked action fields (task brief §4) — one row per recommended lever,
  # empty list for CLARIFY/ABSTAIN outcomes (§3)
  actions:
    - driver: string                   # driver_type from the named C3 hypothesis; must be a member
                                        # of this kpi_id's C1 §5 drivers list, or "residual" — same
                                        # inherited constraint as C3 §1, never invented here
      controllable_lever: enum[L1_restock_sku_store, L2_cross_store_transfer,
                                L3_add_rider_capacity, L4_approve_local_promo,
                                L5_adjust_dispatch_schedule, L6_flag_competitor_opening,
                                L7_escalate_for_investigation, L8_monitor_no_action]
      action: string                   # concrete, persona-appropriate instruction text
      expected_impact: string          # qualitative or bounded-quantitative statement — never
                                        # a point estimate stronger than the source confidence.band
                                        # would justify (§6 boundary)
      owner: enum[zone_business_head, dark_store_ops_manager]   # per §2's decision-rights matrix;
                                        # matches the requesting persona's rights, or the escalation
                                        # target if the lever exceeds their threshold
      confidence: enum[HIGH, MEDIUM, LOW, INSUFFICIENT]   # 🔒 DIRECT PASSTHROUGH of the named
                                        # hypothesis's C3 confidence.band — never a new number
                                        # computed at this layer (task brief §4 requirement,
                                        # enforced structurally: this field has no formula, only
                                        # an assignment from HypothesisPackage.hypotheses[].confidence_band)
      monitoring_plan: string          # what signal would confirm/refute this action's premise —
                                        # e.g. "re-check DS041 stockout rate and Z003 GMV in 3 days"

  # mandatory-non-null caveat enforcement (§0, §6) — structural, not instructional
  caveat_text: string | null           # 🔒 MUST be non-null whenever source_decision_outcome != ANSWER;
                                        # verbatim or lightly-rendered from C3 HypothesisPackage.decision.caveat_text
                                        # (QUALIFY) / .clarifying_question (CLARIFY) / .abstain_reason (ABSTAIN)
  caveat_source_field: enum[caveat_text, clarifying_question, abstain_reason, none]  # which C3 field populated the above

  # persona-narrative rendering targets — filled by §5/§6's rendering process, not by this schema itself
  narrative_zone_business_head: string | null
  narrative_dark_store_ops_manager: string | null
```

**Validation rule attached to this schema (enforced at construction, not left to the LLM):** a `DecisionPackage` with `source_decision_outcome != ANSWER` and `caveat_text = null` is invalid and must be rejected before it reaches either narrative renderer. This is the mechanism referenced in §0 — see §8 test 5 for the corresponding acceptance test.

---

## 5. Two persona narratives — rendering the same DecisionPackage twice

Per C1 §15's entitlement matrix: Zone Business Head gets zone-wide framing, GMV/margin-scale impact language, strategic-reallocation-level actions (L2/L4/L6, plus above-threshold L1/L3), weekly-cadence delivery. Dark-Store Ops Manager gets single-store/SKU-level detail, operational task framing (L1/L3/L5 within threshold, L7/L8), in-workflow delivery.

**The difference is granularity, authority, and action type — not just tone**, and one entitlement consequence must be respected structurally: because a `zone_gmv` finding is zone-grain, and C1 §5's `zone_gmv.access` contract restricts the Dark-Store Ops Manager to "own `dark_store_id` contribution to zone GMV only; no visibility into other stores or the zone total," **the Ops Manager narrative must never state the zone-level GMV shortfall figure** (₹1,70,000 / −9.24%) — only the store-attributable pieces already surfaced in C2's decomposition (the DS041 stockout interval detail, the DS041-attributed SLA breaches). This is an entitlement-filtering rule applied at render time, inherited from C1 §15, not a C4-invented restriction.

---

## 6. LLM / non-LLM boundary, specific to C4

| | LLM does | LLM must never do |
|---|---|---|
| 1 | Phrases the narrative sentence and structures the recommendation in persona-appropriate register (zone-strategic vs. store-operational), given the already-selected lever and already-passed-through confidence band. | Choose the lever — lever selection is the deterministic `driver_type → controllable_lever` mapping of §1, a lookup table, not a generation task. |
| 2 | Explains, in prose, *why* a recommendation carries a given caveat (translating `caveat_text`/`clarifying_question`/`abstain_reason` into persona-appropriate sentences). | Set or soften the `confidence` value — §4's schema makes this field a direct passthrough assignment from `HypothesisPackage.hypotheses[].confidence_band`, with no LLM-writable path to it. |
| 3 | Selects which already-computed `expected_impact` qualifiers to foreground for a given persona's decision-rights scope (e.g., Ops Manager sees store-level impact language, Zone Head sees zone-level). | Override or soften `source_decision_outcome`. If C3 says `QUALIFY`, the LLM cannot render `ANSWER`-style unqualified language — enforced structurally via §4's mandatory-non-null `caveat_text` validation, not by instruction alone: a narrative-generation call that receives a `QUALIFY` package with a populated `caveat_text` and omits that text from its output fails a post-generation containment check (the rendered narrative string must contain the caveat's key clauses) before it is allowed to reach the persona. |
| 4 | Drafts the `monitoring_plan` text for a given action, given the finding's own re-check cadence conventions (day-grain KPIs → check in days, month-grain RPR → check at month-close). | Invent a `driver_type`, a lever outside §1's catalogue, or a decision-rights owner outside §2's matrix. |

---

## 7. Worked example — both personas, the actual S1 QUALIFY outcome

**Source:** `DecisionPackage` for `FIND-KPI-zone_gmv-Z003-20260815-01`, `source_decision_outcome=QUALIFY`, leading hypothesis `HYP-...-01` (`dark_store_stockout_rate`, 55%, `LOW`), secondary `HYP-...-02` (`delivery_sla_adherence`, 20%, `LOW`), residual 25% unresolved. `caveat_text` per C3 §10.5, verbatim per §4's schema rule.

### 7.1 Zone Business Head narrative

> **Z003 — Zone GMV, Aug 15: leading explanation identified, confidence LOW**
>
> Zone GMV for Z003 came in at ₹16,70,000 against a ₹18,40,000 baseline — a ₹1,70,000 (−9.2%) shortfall that is both statistically significant and above the zone's business-impact floor. Store-level segmentation points to DS041 as the dominant contributor within the zone.
>
> The leading explanation is a stockout event at DS041 (SKU-2207 and three related SKUs), estimated to account for roughly 55% of the shortfall. **This is presented as the leading explanation, not a confirmed one** — Customer Voice evidence is mixed: one fresh complaint corroborates ongoing unavailability, but one stale record suggests availability had already recovered by the end of the evidence window. A secondary, independently corroborated contributor is delivery-SLA breaches at DS041 (~20% of the shortfall). 25% of the movement remains unexplained and is not attributed to any specific driver.
>
> **Recommended action:** approve a cross-store inventory transfer of SKU-2207 (and related SKUs) into DS041 from a neighboring store with surplus stock (**L2** — requires your authorization; outside Ops Manager's single-store scope regardless of order size). Given the LOW confidence on the leading driver, this is offered as a reasonable next step, not a certainty — recommend pairing with a monitoring check rather than a larger reallocation commitment.
>
> **Confidence: LOW.** **Monitoring plan:** re-check DS041 stockout rate and Z003 GMV in 3 days; if the gap persists after the transfer, the 25% residual and the SLA contributor both warrant a follow-up investigation (**L7**).
>
> *Separately, and not counted toward this recommendation's confidence:* a customer-level link to August's Repeat Purchase Rate movement exists (one customer, 7-day lag, otherwise eligible) but is not yet answerable — the month hasn't closed, so this stays flagged for review after month-close rather than folded into today's number.

### 7.2 Dark-Store Ops Manager narrative (DS041)

> **Your store — possible stockout impact, Aug 15: confidence LOW**
>
> SKU-2207 and 3 related SKUs at your store spent roughly 14.5 of 24 active-SKU-hours in a stockout state on Aug 15. This pattern is estimated to be a leading contributor to a broader zone-level sales shortfall that day — **but this is a leading explanation, not a confirmed one.** One customer complaint about unavailability lines up with the timing; a separate, older piece of feedback suggests stock had already recovered by the following day, so the picture is mixed, not settled.
>
> Your store also had some same-day delivery-SLA breaches on Aug 15, which independently look like a real (corroborated) contributing factor — worth keeping an eye on separately from the stockout question.
>
> **Recommended action:** submit a restock request for SKU-2207 and the related SKUs. *(If the order value is ≤₹15,000, this is within your auto-executable threshold — go ahead and place it. If it's larger, or touches more than 5 SKUs, route it to your Zone Business Head for approval — **L1** at-threshold / **escalate** above it.)* A cross-store transfer from a neighboring store, if that's the faster fix, needs Zone Business Head sign-off either way (**L2**).
>
> **Confidence: LOW.** **Monitoring plan:** re-check your store's stockout rate for these SKUs in the next few days to see whether the restock resolves it.

Both narratives carry the same `LOW`-band caveat, worded for their audience's decision rights and granularity — neither upgrades the finding into a confident single-cause story, and the Ops Manager version never states the zone-level ₹1,70,000/−9.2% figure per §5's entitlement-filtering rule.

---

## 8. C4 Acceptance Tests

Given→When→Then, matching C1 §18 / C2 §10 / C3 §12 house style.

1. **Given** a `DecisionPackage` with `source_decision_outcome=QUALIFY` and a populated `caveat_text`, **when** both persona narratives are rendered, **then** each narrative's output text contains the caveat's key clauses (leading-not-confirmed framing, the mixed CV signal, the secondary contributor, the residual) — never dropped from either narrative.
2. **Given** a `DecisionPackage` with `source_decision_outcome=CLARIFY`, **when** a narrative is rendered for either persona, **then** the output contains no `controllable_lever` action stronger than `L8` (monitor) and instead surfaces C3's `clarifying_question` verbatim as the stated next step.
3. **Given** a `DecisionPackage` with `source_decision_outcome=ABSTAIN`, **when** the finding is processed, **then** it is not pushed to either persona's proactive alert channel — it is retrievable only via an explicit query or the "under investigation" view, with `abstain_reason` shown plainly there.
4. **Given** a lever recommendation for a Dark-Store Ops Manager exceeds the §2 threshold for that lever (e.g., a restock order >₹15,000, or any `L2`/`L4`/`L6` lever), **when** the `DecisionPackage.actions[].owner` is assigned, **then** `owner=zone_business_head`, never `dark_store_ops_manager`, regardless of the requesting persona.
5. **Given** a `DecisionPackage` with `source_decision_outcome != ANSWER`, **when** the package is validated before narrative rendering, **then** construction fails if `caveat_text = null` — the mandatory-non-null rule (§4) is enforced structurally, not left to the LLM to remember.
6. **Given** the `DecisionPackage.actions[].confidence` field, **when** it is populated, **then** its value exactly equals the corresponding hypothesis's `HypothesisPackage.hypotheses[].confidence_band` from C3 — no independent computation, re-scoring, or rounding at this layer.
7. **Given** a `DecisionPackage` with `source_decision_outcome=NON_MATERIAL` (`answer_without_hypothesis=true` upstream), **when** it is surfaced to either persona, **then** it appears only in the periodic passive status roll-up, never in the proactive/interruptive alert channel.
8. **Given** a `zone_gmv` `DecisionPackage` rendered for a Dark-Store Ops Manager, **when** the narrative is generated, **then** the output text never contains the zone-level absolute GMV shortfall figure — only store-attributable detail already present in the source decomposition, per C1 §5's `zone_gmv.access` entitlement contract.

---

## 9. Deliverables index (per task brief §9)

1. Business lever/action catalogue with `driver_type` mapping — §1
2. Decision rights matrix with concrete thresholds — §2
3. Outcome → narrative template mapping (all 4 outcomes, plus the `NON_MATERIAL` decision) — §3
4. `DecisionPackage` schema — §4
5. Two full persona narratives for the actual S1 `QUALIFY` outcome — §7
6. LLM/non-LLM boundary table — §6
7. Acceptance tests — §8

**Handed to C5:** the `DecisionPackage` schema (§4) and the actual S1 decision (§0, §7) — C5 can build the seeded historical decision/outcome record the signature demo depends on directly from this output, using C1 §14's `DEC-FIND-...-01-01` / `OUT-DEC-...-01` ID scheme and `validation_status=demo_preapproved` entry point, without re-opening any C1/C2/C3/C4 reasoning.
