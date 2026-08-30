# Praxis R2 — C3: Evidence & Reasoning Method
**Owner:** Reasoning & Retrieval Engineer (C3)
**Depends on (fixed ground truth, not re-derived here):** `C1_Data_Semantic_Foundation_v2.md` — every 🔒 LOCKED item, all 5 KPI YAML contracts, §6 conflict policy, §7.1 Customer Voice matching window, §7.2 day→month eligibility rule, §13 data-state model, §14 lineage ID scheme. `04_C2_Analytical_Investigation_Method.md` — the 5-operator catalogue, the §9 `EvidencePackage` schema, and its terminal outcomes.
**Out of scope here (owned by C4 — Decision & Persona Designer):** business-lever/action mapping, persona narrative construction. **Out of scope here (owned by C5 — Memory & Governance Engineer, later):** memory storage, admission, supersession. §8 defines the interface C5 will plug into; it implements nothing of C5's.

---

## 0. Ground-truth discrepancy — stated, not silently resolved

The task brief describes C2 as having **6 terminal outcomes**, naming `METHOD_NOT_APPLICABLE` alongside the other five. C2's own §9 `EvidencePackage.terminal_outcome` enum, however, lists only **five** values: `EVALUATED, SKIPPED, NON_MATERIAL, INSUFFICIENT_HISTORY, NO_DOMINANT_CONTRIBUTOR`. This is not a contradiction once C2 §4 step (e.ii) is read closely: `METHOD_NOT_APPLICABLE` is explicitly "not a hard stop" — it is a **nested sub-outcome of `decomposition.pvm`** (`pvm.applicable=false, pvm.method_not_applicable_reason=...`), and it always co-occurs with a top-level `terminal_outcome=EVALUATED` (the driver-mapped split still ran; only the PVM cross-check was structurally skipped).

**C3's handling (stated, not defaulted silently):** C3 treats the top-level `EvidencePackage.terminal_outcome` enum (5 values, per C2 §9's concrete schema) as authoritative for routing §3 hypothesis generation and §7 abstention, since the schema is the field-level contract C2 actually hands off. `METHOD_NOT_APPLICABLE` is read at the nested `decomposition.pvm` level and affects C3 only in one way: **it removes the PVM cross-check as a corroborating signal for the confidence formula (§7) for the 4 non-additive KPIs** — it is not itself a hypothesis-generation or abstention trigger. This resolution is flagged here rather than assumed so C4/C5 don't inherit an undocumented interpretation.

---

## 1. Hypothesis object schema

A hypothesis is a **claim under evaluation**, never a fact. That distinction is enforced at the schema level via the mandatory `claim_status` field below (not left to a comment or to prose in the UI layer).

```yaml
hypothesis:
  hypothesis_id: string              # HYP-{finding_id}-{seq}, e.g. HYP-FIND-KPI-zone_gmv-Z003-20260815-01-01
  finding_id: string                 # C2 EvidencePackage.finding_id this hypothesis explains
  kpi_instance_id: string            # passthrough from EvidencePackage
  claim: string                      # short natural-language statement of the proposed explanation
  claim_status: enum[UNDER_EVALUATION]   # 🔒 constant, single-value enum by design —
                                          # a hypothesis can never transition out of "claim" at
                                          # this layer; "supported"/"contradicted" (below) describe
                                          # evidentiary state, not promotion to fact. C4/persona
                                          # copy must not restate a supported hypothesis as settled.
  scope:
    grain_key: string                # dark_store_id or zone_id, per kpi_id's C1 §5 grain
    period: string                   # ISO date or year-month, per kpi_id
  driver_type: enum                  # MUST be a member of this kpi_id's C1 §5 `drivers` list, or
                                      # the literal value "residual" for the unexplained-bucket
                                      # hypothesis (§2). Never an invented driver. 🔒 inherited constraint.
  source_contribution:
    contribution_pct: decimal | null # from C2 decomposition.drivers[].contribution_pct, or
                                      # decomposition.residual_pct for the residual hypothesis
    estimation_method: string        # passthrough of C2's method string — never re-derived by C3
  expected_supporting_evidence:
    customer_voice_signal_terms: list[string]  # query-template seed terms, §3
    expected_direction: enum[negative, positive, neutral]  # direction of KPI movement this
                                      # driver_type would predict, used to score directional
                                      # agreement with retrieved evidence (§5)
    temporal_expectation:
      window_start: date             # C1 §7.1 D-7
      window_end: date                # C1 §7.1 D+2
  status: enum[candidate, supported, contradicted, unresolved]
    # candidate    — generated, not yet evaluated against Customer Voice (§3→§6 transition point)
    # supported    — §6 challenge logic found corroborating evidence, no unresolved contradiction
    # contradicted — §6 found evidence directly conflicting with the claim
    # unresolved   — evidence retrieved is Stale/Partial/Conflicting/Missing/mixed enough that
    #                neither supported nor contradicted can be asserted (§6)
  confidence:
    score: int                       # 0–100, §7 formula
    band: enum[HIGH, MEDIUM, LOW, INSUFFICIENT]
  evidence_refs: list[string]        # evidence_object.evidence_id (§4), populated after §3→§6
  memory_hook: object | null         # §8 — always present as a keyed slot, null payload today
```

---

## 2. Bounded hypothesis-generation rules

The LLM never sees raw C1/C2 data and never invents a `driver_type`. It receives one `EvidencePackage` and proposes hypotheses **only within the driver slots C2 already populated.**

**Generation rule, by `terminal_outcome`:**

| `EvidencePackage.terminal_outcome` | Hypothesis generation behavior |
|---|---|
| `EVALUATED`, `dominant_driver` present | One hypothesis per driver in `decomposition.drivers[]` with `contribution_pct ≥ 15%` (floor 🧪 prototype assumption — below this, a driver's contribution is noise-adjacent relative to the 30% dominance bar and cluttering the hypothesis set with sub-15% entries adds no decision value). **Plus** one `driver_type="residual"` hypothesis if `decomposition.residual_pct ≥ 20%` (🧪 prototype assumption — a residual this large is itself a material unexplained-variance signal worth surfacing, not silently dropped). Below 20% residual, no residual hypothesis is generated; the number is still carried in the `HypothesisPackage` (§11) as metadata. |
| `EVALUATED`, `decomposition.pvm.applicable=false` (i.e. `METHOD_NOT_APPLICABLE` nested) | Same rule as above — the driver-mapped split still exists per C2 §3; only the PVM corroboration signal is absent from §7's confidence formula (§0). |
| `NO_DOMINANT_CONTRIBUTOR` | **Widen, never force a pick.** Generate one hypothesis for every driver at or above the 15% floor (typically 2–4, since by definition none reached the 30% dominance bar) as **co-candidate hypotheses**, all initialized `status=candidate` with no implicit ranking beyond `contribution_pct` order. The residual hypothesis rule above still applies independently. C3 must not synthesize a false "leading" hypothesis out of the largest of several roughly-equal contributors — this is the same reasoning C2 §3 used to justify the 30% bar in the first place, restated at the hypothesis layer. |
| `INSUFFICIENT_HISTORY` | **No hypothesis generation at all.** Zero hypothesis objects created. Handled entirely as an abstention case, §7. |
| `SKIPPED` | **No hypothesis generation.** The underlying KPI-instance data was `Missing`/`Invalid`; there is nothing to explain. Abstention, §7. |
| `NON_MATERIAL` | **No hypothesis generation.** There is no movement to explain — C2 already determined this is normal variance. This is itself a valid, confident **answer** ("no material movement detected"), not an abstention, but it produces no `Hypothesis` object since there is no gap to attribute. Represented in the `HypothesisPackage` (§11) as an `answer_without_hypothesis` record. |

**Explicit non-goal:** C3 does not re-run or second-guess C2's materiality gate, driver-list membership, or the 30%/15%/20% dominance-and-floor logic beyond the two 🧪 floors introduced here (15% inclusion floor, 20% residual-hypothesis floor) — both of which govern *whether a hypothesis object gets created*, not *whether a movement is material*, which remains entirely C2's decision.

---

## 3. Customer Voice retrieval architecture

C1's constraints are restated, not renegotiated:
- **Grain:** zone-level only at source, no `dark_store_id` (C1 §2.3, §10).
- **Matching window** for a finding on day D: `record.ts ∈ [D−7, D+2]` (C1 §7.1) — for month-grain findings (RPR), C3 anchors D at the **month-end date** of the target month (the last calendar day the RPR figure covers), since C1 does not define a day-anchor for month-grain evidence matching and one is required to apply §7.1's window at all. This anchor choice is a 🧪 **C3 prototype assumption**, stated here because C1/C2 leave it open.
- **Labeling requirement:** any Customer Voice evidence surfaced to a Dark-Store Ops Manager view carries the `unverified, zone-wide, text-matched` label **as a field on the evidence object itself** (§4), not only in UI copy — so the label survives serialization, caching, and any future C4/C5 consumer.

**Retrieval mechanism — hybrid (lexical + semantic), stated with rationale:**

Customer Voice is low-volume (weekly, irregular cadence per C1 §2.3), short free text, and domain-narrow (quick-commerce order/delivery/stock complaints). Two failure modes matter equally here:
1. **Pure semantic/embedding retrieval** over-generalizes on a small, domain-narrow corpus — it will happily surface a "the app crashed" complaint as similar to "the app was slow," which is a false corroboration for a stockout hypothesis.
2. **Pure lexical/keyword retrieval** misses paraphrase (a customer writing "still waiting, never showed up" for a late-delivery complaint if the query template only contains "SLA" or "delayed").

**C3's mechanism:** hybrid retrieval — BM25 lexical search over a per-`driver_type` seed-term query template (`expected_supporting_evidence.customer_voice_signal_terms`, §1) combined with embedding cosine similarity over the same records, fused by reciprocal rank fusion (RRF), restricted to the zone's records within the §7.1 window. Query templates are authored per `driver_type`, not per-finding (e.g. `dark_store_stockout_rate` → `["out of stock", "unavailable", "sold out", "couldn't add to cart"]`; `delivery_sla_adherence` → `["late", "never arrived", "still waiting", "delivery delay"]`), so the same template is reused across findings — this is what keeps the retrieval bounded rather than letting an LLM freely query the corpus.

**Support / contradict / contextualize tagging (mechanical, not an LLM judgment call — see §9 boundary table):**
1. Compute directional alignment: does the retrieved record's `source_type`/sentiment polarity (lexicon-scored, not LLM-scored) align with `expected_direction` (§1)?
2. `supports` — aligned polarity **and** matched on the hypothesis's own query template (not a different `driver_type`'s template).
3. `contradicts` — opposite polarity on the same template, or a record explicitly describing a *different* resolved cause for the same complaint category (e.g., a record praising stock availability at the exact zone/window a stockout hypothesis claims caused the movement).
4. `contextualizes` — matched by RRF but polarity-neutral, or matched on a template belonging to a *different* hypothesis in the same finding's set (i.e., relevant background, not evidence for or against this specific claim).
5. `unresolved` (evidence-object relationship value, distinct from hypothesis `status`) — record itself is `Stale`/`Conflicting`/ambiguous polarity.

---

## 4. Evidence object schema — two axes, kept distinct

C1's data-quality axis (`Fresh, Stale, Partial, Missing, Conflicting, Invalid`, §13) and C3's evidence-hypothesis relationship axis (`supports, contradicts, contextualizes, unresolved`, §3) are two independent fields on the same object — never collapsed into one status.

```yaml
evidence_object:
  evidence_id: string                 # EVID-{hypothesis_id}-{seq}
  hypothesis_id: string                # FK to §1 hypothesis this evidence was retrieved for
  source: string                       # "SRC-CV" — the only unstructured source C3 retrieves from
  source_record_id: string             # Customer Voice record_id (C1 §2.3 PK), for lineage
  retrieved_at: timestamp              # ISO-8601, IST

  # axis 1 — data quality / availability (C1 §13, inherited enum, not redefined)
  data_quality_state: enum[Fresh, Stale, Partial, Missing, Conflicting, Invalid]
  as_of_ts: timestamp | null           # required if Stale, per C1 §13

  # axis 2 — evidence-hypothesis relationship (C3-owned, independent of axis 1)
  relationship: enum[supports, contradicts, contextualizes, unresolved]
  relationship_basis: string           # e.g. "polarity-aligned, matched dark_store_stockout_rate template"

  # content
  record_excerpt: string               # short, non-reproducing paraphrase — never the verbatim
                                        # customer text wholesale; C3 synthesizes, doesn't quote at length
  matched_day: date                    # from C1 §2.3 derived field
  source_type: enum[review, chat, social, csat]

  # access / labeling — carried on the object, not left to the UI layer
  access_label: enum[zone_wide_verified_for_zone_head, unverified_zone_wide_text_matched_for_ops]
    # per C1 §10/§16: Zone Business Head sees zone-wide CV natively (no extra label needed since
    # it IS their native scope); Dark-Store Ops Manager view MUST carry the unverified label —
    # 🔒 this field is mandatory and non-optional whenever persona=ops_manager consumes this object.

  # lineage
  lineage_pointer: string              # C1 §14 lineage_edge reference back to SRC-CV record
```

**Worked note on the "don't conflate" requirement:** a single retrieved record can be `data_quality_state=Fresh` (arrived within SLA, no DQ flags) **and** `relationship=contradicts` (polarity opposes the hypothesis) simultaneously — this is the explicit example the task brief calls for, and the schema above makes both fields independently settable with no shared enum to accidentally merge them into.

---

## 5. Challenge logic

Run once per `Hypothesis` (candidate → resolved status transition), for every hypothesis generated per §2. At minimum, three checks — none of which re-litigate C2's quantitative work:

1. **Corroboration/contradiction check.** For the leading hypothesis (highest `contribution_pct`, or — under `NO_DOMINANT_CONTRIBUTOR` — for *each* co-candidate independently, §2), query §3's retrieval and classify every returned record's `relationship`. If ≥1 `supports` and zero `contradicts` → hypothesis moves toward `supported`. If ≥1 `contradicts` → surfaced explicitly (never suppressed, never silently resolved in favor of the quantitative side — this is a hard rule, §7).
2. **Credible-alternative check.** Does any *other* generated hypothesis (§2's candidate set) fit the retrieved Customer Voice evidence at least as well as the leading one? This check is **mandatory, not optional, whenever `terminal_outcome=NO_DOMINANT_CONTRIBUTOR`** (C2 already told C3 there's no statistically dominant quantitative winner; Customer Voice corroboration strength is one of the only remaining signals that could differentiate the co-candidates, and even then only informs confidence, never forces a pick). It also runs for the single-dominant-driver case, at lower priority, to catch cases where quantitative dominance and qualitative evidence disagree.
3. **Conflicting/Stale-widening check.** If any evidence item within the `EvidencePackage` itself (not the CV retrieval — the *upstream* C2 data) carries `conflicting_input=true` or `evaluated_on_stale_input=true`, or `partial_sources_excluded` is non-null, this widens the hypothesis's confidence band (never narrows it, never is silently dropped) — implemented in §7's formula as an explicit penalty term, not a discretionary judgment call.

**Explicit non-goal (restated per the brief):** challenge logic never recomputes PVM splits, never re-derives driver contribution percentages, and never re-checks day→month lag/lookback eligibility — those are settled facts from C2/C1 respectively, consumed as inputs.

---

## 6. Confidence framework

A concrete point formula, computed per hypothesis, 0–100, normalized so the same scale applies across all 5 KPIs despite their different statistical tests (z-score vs. proportion-test p-value vs. relative-change threshold).

```
confidence_score =
    clamp( materiality_strength(0–30)
         + dominance_strength(0–30)
         + customer_voice_score(−20 to +20)
         − data_quality_penalty(0–30)
      , 0, 100)
```

**`materiality_strength` (0–30)** — normalizes each KPI's own §1 test statistic against its own threshold, saturating at 2× the threshold:
- Zone GMV (z-score): `clamp((|z| − 2.5) / 2.5 × 30, 0, 30)`
- Conversion / Stockout / SLA (proportion p-value): `clamp((0.05 − p) / 0.05 × 30, 0, 30)`
- Repeat Purchase Rate (relative-change threshold): `clamp((|Δ_relative| − 0.15) / 0.15 × 30, 0, 30)`, using whichever of the relative/absolute floor actually cleared per C2 §1.

**`dominance_strength` (0–30)** — zero if `no_dominant_contributor=true` (hard rule: no partial credit for "the largest of several roughly-equal drivers," consistent with C2 §3's own reasoning for the 30% bar); otherwise `clamp((contribution_pct − 30) / 70 × 30, 0, 30)` for the specific driver this hypothesis is about.

**`customer_voice_score` (−20 to +20)** — from §5's challenge logic outcome for this hypothesis:
- `+20`: ≥1 `Fresh`, `supports` record, zero `contradicts` records.
- `+10`: only `Stale` or `Partial` `supports` records, or a single weak/ambiguous supporting match.
- `0`: no Customer Voice retrieved at all (`Missing` per C1 §13 — **explicitly not penalized**, since absence of evidence is not evidence of absence, restated from C1 §13's non-negotiable rule).
- `−10`: `contradicts` records present alongside `supports` records (mixed signal — net negative because an unresolved internal conflict is worse than silence).
- `−20`: `contradicts` records present with **zero** `supports` records.

**`data_quality_penalty` (0–30, subtracted)** — from the *upstream* `EvidencePackage` flags (not the CV retrieval): `+15` if `evaluated_on_stale_input=true`; `+10` if `partial_sources_excluded` is non-null; `+20` if `conflicting_input=true`; penalties are additive, capped at 30 total.

**Bands:** `HIGH` ≥ 70, `MEDIUM` 40–69, `LOW` 15–39, `INSUFFICIENT` < 15 (this last is a scoring outcome distinct from the hard-rule `INSUFFICIENT_HISTORY` abstention in §7 — a hypothesis can score into `INSUFFICIENT` even when C2 did produce a baseline, if every component above is weak).

**Hard caps (override the raw score, never let arithmetic alone produce an over-confident answer):**
- `terminal_outcome=NO_DOMINANT_CONTRIBUTOR` → band capped at `MEDIUM`, regardless of computed score, for every co-candidate hypothesis.
- Any hypothesis with a `contradicts`-only Customer Voice signal (§5.1) → band capped at `MEDIUM`, even if the quantitative components alone would compute `HIGH` — a direct qualitative contradiction must visibly qualify the answer, never be arithmetically outvoted into silence.
- `conflicting_input=true` on the source `EvidencePackage` → band capped at `MEDIUM` — C3 does not present a confident single answer built on data C1 itself flagged as unreconciled.
- A hypothesis derived through a §8-forward day→month link whose target RPR finding carries `provisional=true` → band capped at `LOW` — a not-yet-closed month is structurally unstable (C1 §5 says so directly), independent of how strong the day-grain evidence looks.

## 7. Abstention policy — explicit rules, tied to C2's outcomes

The answer/qualify/clarify/abstain decision is a function of `terminal_outcome`, hard caps (§6), and band, in that priority order:

| `terminal_outcome` / condition | Decision | Rationale |
|---|---|---|
| `INSUFFICIENT_HISTORY` | **ABSTAIN** (hard rule, no hypothesis generated, §2) | No baseline exists to test against; there is nothing to have a confidence level *about*. |
| `SKIPPED` | **ABSTAIN** | Underlying C1 data is `Missing`/`Invalid`; nothing to reason on. Always state the reason code (`access-restricted` vs. `not-yet-arrived` vs. `genuinely-absent`, per C1 §13) — never silently abstain without saying why. |
| `NON_MATERIAL` | **ANSWER** ("no material movement detected") | This is C2's own confident conclusion; no hypothesis needed, no confidence scoring needed — it's a clean negative result, not an abstention. |
| `NO_DOMINANT_CONTRIBUTOR` | **QUALIFY**, always presenting the full co-candidate set | Band-capped `MEDIUM` at most (§6); never a forced single pick, per C2's own reasoning for the 30% bar. |
| `EVALUATED`, dominant driver exists, band `HIGH` | **ANSWER**, naming the dominant hypothesis, residual disclosed if generated | Only path that reaches an unqualified answer. |
| `EVALUATED`, band `MEDIUM` (including any hard-capped case) | **QUALIFY** — state the leading hypothesis with the specific caveat that capped it (residual size, staleness, CV contradiction, or provisional RPR linkage) | The caveat itself is a required field on the decision object (§11), not left implicit. |
| `EVALUATED`, band `LOW` | **QUALIFY, weakly** — if `segmentation.ranked_stores` offers a narrowing dimension not yet resolved (e.g., "which store" when zone-level evidence is thin), emit **CLARIFY** instead: surface the narrowing question rather than a low-confidence claim. | A clarifying question is only offered when an actual narrowing input exists (from C2's Operator 4 output) — C3 never invents a question with nothing behind it. |
| Any hypothesis, band `INSUFFICIENT` | **ABSTAIN on that specific hypothesis** (other hypotheses in the same finding's set may still clear a higher band and get answered/qualified independently) | Per-hypothesis, not per-finding — a finding with one strong and one weak hypothesis is not forced to abstain wholesale. |
| Customer Voice `contradicts`-only for the leading hypothesis | Decision forced to at minimum **QUALIFY**, with the contradiction stated explicitly in the response, never suppressed or silently resolved in favor of the quantitative side | Direct requirement from the task brief §7. |
| `conflicting_input=true` on the `EvidencePackage` | Decision forced to at minimum **QUALIFY** | Confidence is widened/downgraded, never treated as clean, per the task brief §7. |

---

## 8. Memory-retrieval hook (forward-compatible, not implemented here)

C5 does not exist yet. The `Hypothesis` object's `memory_hook` field (§1) is a keyed slot with a defined query shape, always populated with the shape below and a `null` result today — so C5 attaches later without redesigning the `Hypothesis` or `HypothesisPackage` schema, the same discipline C1 used for lineage IDs before C5 existed.

```yaml
memory_query:                      # the shape a future C5 lookup would need to answer
  driver_type: string              # must match a governed driver, same constraint as §1
  kpi_id: string
  comparable_scope:
    grain_key: string              # dark_store_id or zone_id — exact match preferred,
                                    # zone-level fallback if store-level has no history
    grain_level: enum[store, zone]
  requested_fields:
    - prior_validation_status      # C1 §14: pending | approved | rejected | demo_preapproved
    - prior_confidence_band
    - prior_outcome_observed        # did the prior decision's predicted effect materialize?
  result: null                     # always null today — no C5 to answer this yet
  result_schema_reserved: true     # signals to C4/C5 that this key is claimed, not available for
                                    # ad hoc reuse
```

When populated by a future C5, a matching prior record raises `customer_voice_score`-adjacent prior confidence and can shorten investigation (per the project's signature-demo requirement) — but that logic is explicitly **not** implemented here; only the query interface is.

---

## 9. LLM / non-LLM boundary, specific to C3

| | LLM does | LLM must never do |
|---|---|---|
| 1 | Propose hypotheses, but only by selecting from §2's governed slots (driver ≥15% floor, residual ≥20% floor) — it fills in `claim` text and `expected_supporting_evidence` phrasing, never a new `driver_type`. | Invent a `driver_type` not on C1 §5's list for that `kpi_id`, or add a hypothesis outside §2's generation rules. |
| 2 | Synthesize retrieved Customer Voice records into a structured, cited summary (`record_excerpt`, paraphrased, not reproduced verbatim per copyright practice). | Compute `confidence_score` or assign a `band` — §6's formula is deterministic code, not an LLM judgment call. |
| 3 | Draft the natural-language `claim` and `relationship_basis` text for a given mechanically-computed `relationship` tag. | Decide `material`/`no_dominant_contributor` — those are C2 facts, consumed, never re-derived. |
| 4 | Explain, in prose, why a hypothesis was capped or qualified (translating §6/§7's rule firing into a sentence). | Decide the answer/qualify/clarify/abstain outcome itself — §7's table is the decision function; the LLM narrates the *already-decided* outcome, it does not choose it. |

---

## 10. Worked example — continuing the S1 scenario

Input: C2's `EvidencePackage` for `FIND-KPI-zone_gmv-Z003-20260815-01` — `terminal_outcome=EVALUATED`, `data_state=FRESH` (no stale/partial/conflicting flags), `dominant_driver=dark_store_stockout_rate` (55.0%), `delivery_sla_adherence` (20.0%), residual 25.0%, `z=-3.78`, one eligible day→month link (`CUST-771204` → `FIND-KPI-repeat_purchase_rate-Z003-202608-01`, `provisional=true`) and one rejected link (`CUST-556190`, `MIN_LAG_VIOLATION`).

### 10.1 Hypothesis generation (§2)
Three hypotheses generated (both drivers clear the 15% floor; residual clears the 20% floor):

| `hypothesis_id` | `driver_type` | `contribution_pct` | initial `status` |
|---|---|---|---|
| `HYP-...-01` | `dark_store_stockout_rate` | 55.0% | candidate |
| `HYP-...-02` | `delivery_sla_adherence` | 20.0% | candidate |
| `HYP-...-03` | `residual` | 25.0% | candidate |

### 10.2 Customer Voice retrieval (§3), window `[2026-08-08, 2026-08-17]`, zone `Z003`

Three illustrative retrieved records (invented content, plausible for the domain):

| `evidence_id` | excerpt (paraphrased) | `data_quality_state` | matched query template | `relationship` |
|---|---|---|---|---|
| `EVID-01-01` | Customer describes repeatedly finding a specific snack item unavailable when ordering from Z003 in mid-August, prompting them to switch apps for that order | Fresh | `dark_store_stockout_rate` template | **supports** (HYP-01) |
| `EVID-02-01` | Customer describes an order arriving well past the promised window on Aug 16 and says they nearly cancelled | Fresh | `delivery_sla_adherence` template | **supports** (HYP-02) |
| `EVID-01-02` | Customer, different record, praises fast restocking and says availability "felt back to normal" by Aug 17 | Stale (near edge of window, `as_of_ts` late) | `dark_store_stockout_rate` template, opposite polarity | **contradicts** (HYP-01), tagged `unresolved`-leaning given staleness |

Per C1 §10, since this scenario's persona view is unspecified, both a Zone Business Head and (if requested) a Dark-Store Ops Manager view are supported; the Ops Manager view of these three records carries `access_label=unverified_zone_wide_text_matched_for_ops` (§4).

### 10.3 Challenge logic (§5) and resulting evidence states
- **HYP-01 (stockout):** one `supports`, one `contradicts` (stale) → mixed signal. Per §6, `customer_voice_score = −10`. `status` → `unresolved` is avoided here because the contradicting record is `Stale` and lower-confidence than the `Fresh` supporting one; C3 records `status=supported` but the contradiction is **not suppressed** — it is carried into the decision object's caveat text per §7's explicit-surfacing rule.
- **HYP-02 (SLA):** one `supports`, zero `contradicts` → `customer_voice_score = +20`, `status=supported`.
- **HYP-03 (residual):** no retrieval attempted — by definition there is no driver-specific query template for "residual"; `status` stays `unresolved` by construction, `customer_voice_score = 0`.

### 10.4 Confidence computation (§6)

**HYP-01 (stockout):**
`materiality_strength = clamp((3.78−2.5)/2.5×30,0,30) = 15.4`
`dominance_strength = clamp((55−30)/70×30,0,30) = 10.7`
`customer_voice_score = −10` (mixed signal)
`data_quality_penalty = 0` (EvidencePackage itself is Fresh/clean)
`confidence_score = clamp(15.4+10.7−10−0,0,100) = 16.1` → band `LOW`.
Hard cap check: contradicting CV evidence exists but is not `contradicts`-only (a `supports` record also exists), so the "contradicts-only → cap MEDIUM" rule does **not** apply here; the raw `LOW` stands.

**HYP-02 (SLA, non-dominant but still a valid contributing hypothesis):**
`materiality_strength = 15.4` (same finding-level statistic)
`dominance_strength = clamp((20−30)/70×30,0,30) = 0` (below the 30% dominance bar — contributes, but the formula gives it zero dominance credit by design, consistent with C2's own bar)
`customer_voice_score = +20`
`confidence_score = clamp(15.4+0+20−0,0,100) = 35.4` → band `LOW`.

**HYP-03 (residual):** not scored numerically — `unresolved` by construction, always `INSUFFICIENT` band (no driver, no CV template, nothing to score); carried through as an open-investigation flag, not a scored claim.

### 10.5 Decision (§7)
`terminal_outcome=EVALUATED` with a dominant driver, but **both** scored hypotheses land in `LOW`. Per §7's table: check for a narrowing dimension from C2's Operator 4 (segmentation) output — C2's §4 worked example already narrowed the zone shortfall to `DS041` as the dominant contributing store. Since that narrowing is already resolved (not an open question), C3 does **not** emit `CLARIFY`; it emits **QUALIFY**, presenting HYP-01 as the leading (highest-`contribution_pct`) hypothesis, with the caveat text stating explicitly: *"Quantitative decomposition points to a stockout event at DS041 as the largest single contributor (55%), but Customer Voice evidence is mixed — one fresh corroborating complaint and one stale record suggesting availability had recovered by the window's end — so this is presented as the leading explanation, not a confirmed one. A secondary SLA-related contributor (20%) is independently corroborated. 25% of the movement remains unexplained."*

### 10.6 RPR-side day→month link
The `CUST-771204` eligible pair (§7.2-compliant, 7-day lag) generates a fourth object: a hypothesis scoped to `FIND-KPI-repeat_purchase_rate-Z003-202608-01`, `driver_type=dark_store_stockout_rate`, `claim="the DS041 stockout event is a candidate contributing factor to a subset of Z003's August repeat-purchase pattern via this customer's reorder timing."` Per §6's hard cap, any hypothesis attached to a `provisional=true` RPR finding is capped at `LOW` regardless of its computed score. Per §7, the decision on this specific RPR-scoped hypothesis is **ABSTAIN** — it is retained as a linked evidentiary note attached to the GMV finding (via the C1 `lineage_edge`), not surfaced as an answerable claim about August's repeat-purchase rate until the month closes and `provisional` clears. The rejected pair (`CUST-556190`, `MIN_LAG_VIOLATION`) produces no hypothesis at all — it never passed C2's eligibility gate, so it never reaches C3.

---

## 11. HypothesisPackage — the C3→C4 handoff schema

```yaml
hypothesis_package:
  finding_id: string                  # FK to C2 EvidencePackage.finding_id
  kpi_instance_id: string
  generated_at: timestamp

  # passthrough pointers — so C4 never re-opens C2/C1's reasoning
  evidence_package_ref: string        # C2 finding_id, full EvidencePackage retrievable by ref
  lineage_chain: list[string]         # C1 §14 chain, passed through unchanged

  # answer_without_hypothesis — populated only for NON_MATERIAL findings (§2)
  answer_without_hypothesis: bool
  answer_without_hypothesis_text: string | null

  # ranked hypotheses — empty list for INSUFFICIENT_HISTORY / SKIPPED / NON_MATERIAL
  hypotheses:
    - hypothesis_id: string
      driver_type: string
      status: enum[candidate, supported, contradicted, unresolved]
      contribution_pct: decimal | null
      confidence_score: int
      confidence_band: enum[HIGH, MEDIUM, LOW, INSUFFICIENT]
      hard_caps_applied: list[string]   # e.g. ["no_dominant_contributor", "cv_contradicts_only",
                                         # "conflicting_input", "provisional_rpr_link"] — empty if none
      supporting_evidence_refs: list[string]
      contradicting_evidence_refs: list[string]
      contextualizing_evidence_refs: list[string]
      memory_hook: object               # §8, null result today

  # the decision — one per finding-level answer, not per hypothesis, except CLARIFY/per-hypothesis
  # abstain which is scoped explicitly
  decision:
    outcome: enum[ANSWER, QUALIFY, CLARIFY, ABSTAIN]
    scope: enum[finding, hypothesis]    # finding-level for ANSWER/QUALIFY/NON_MATERIAL cases;
                                        # hypothesis-level when only some hypotheses in the set abstain
    leading_hypothesis_id: string | null
    caveat_text: string | null          # required whenever outcome=QUALIFY
    clarifying_question: string | null  # required whenever outcome=CLARIFY, must reference a
                                         # real C2 Operator-4 narrowing dimension (§7)
    abstain_reason: string | null       # required whenever outcome=ABSTAIN (per-hypothesis or
                                         # finding-wide)
```

---

## 12. C3 Acceptance Tests

Given→When→Then, matching C1 §18 / C2 §10 style.

1. **Given** an `EvidencePackage` with `terminal_outcome=EVALUATED`, a `dominant_driver` at 55% contribution, and a Customer Voice `supports`-only retrieval result, **when** §6's confidence formula runs, **then** the hypothesis clears `HIGH` and §7's decision is `ANSWER` naming that hypothesis, with any generated residual hypothesis disclosed alongside it, not suppressed.
2. **Given** an `EvidencePackage` with `terminal_outcome=NO_DOMINANT_CONTRIBUTOR` (e.g. three drivers at 22%, 20%, 18%), **when** §2 generates hypotheses, **then** all three co-candidates are created with no forced ranking beyond `contribution_pct` order, and §6/§7 cap every one of them at `MEDIUM` or below with a `QUALIFY` decision — never a single named answer.
3. **Given** an `EvidencePackage` with `terminal_outcome=INSUFFICIENT_HISTORY`, **when** C3 processes the finding, **then** zero `Hypothesis` objects are generated and the `HypothesisPackage.decision.outcome=ABSTAIN` with `abstain_reason` populated from C2's own reason string — no confidence scoring is attempted.
4. **Given** the leading hypothesis has zero `supports` and at least one `contradicts` Customer Voice record, **when** §6/§7 evaluate it, **then** `hard_caps_applied` includes `"cv_contradicts_only"`, the band is capped at `MEDIUM` even if the raw quantitative score alone would compute `HIGH`, and the resulting `caveat_text` explicitly states the contradiction rather than omitting it or silently favoring the quantitative side.
5. **Given** an eligible day→month link (§C1 §7.2, C2 Operator 5) whose target RPR finding carries `provisional=true`, **when** C3 generates the RPR-scoped hypothesis for that link, **then** `hard_caps_applied` includes `"provisional_rpr_link"`, the band is capped at `LOW` regardless of computed score, and the decision for that specific hypothesis is `ABSTAIN` (scope=hypothesis) while the day-grain finding's own decision proceeds independently.
6. **Given** an `EvidencePackage` with `terminal_outcome=NON_MATERIAL`, **when** C3 processes the finding, **then** no `Hypothesis` objects are generated, `answer_without_hypothesis=true`, and `decision.outcome=ANSWER` — this is distinguished from an abstention in the schema and in the decision table (§7).
7. **Given** a `driver_type` proposed by the LLM does not appear in the `kpi_id`'s C1 §5 `drivers` list and is not the literal string `"residual"`, **when** the hypothesis object is validated, **then** it is rejected before being added to the `HypothesisPackage` — the LLM-boundary table (§9) prohibition is enforced structurally, not just by prompt instruction.
8. **Given** a Dark-Store Ops Manager requests the evidence behind a hypothesis, **when** the relevant `evidence_object` is serialized for that persona, **then** `access_label=unverified_zone_wide_text_matched_for_ops` is present on the object itself, not only applied by the UI layer rendering it.

---

## 13. Deliverables index (per task brief §13)

1. Hypothesis object schema — §1
2. Bounded hypothesis-generation rules — §2
3. Customer Voice retrieval architecture — §3
4. Evidence object schema (both axes) — §4
5. Challenge logic — §5
6. Confidence framework + abstention policy — §6–§7
7. Memory-retrieval hook — §8
8. LLM/non-LLM boundary table — §9
9. Worked S1 continuation — §10
10. HypothesisPackage schema — §11
11. Acceptance tests — §12

**Handed to C4:** the `HypothesisPackage` schema (§11) and the worked example's actual decision (§10.5–10.6: `QUALIFY` on the GMV finding with a stated stockout-leading, SLA-secondary caveat; `ABSTAIN` on the provisional RPR-side link) — C4 can build persona narratives and business-lever mapping directly from these without re-opening any C1/C2/C3 reasoning.
