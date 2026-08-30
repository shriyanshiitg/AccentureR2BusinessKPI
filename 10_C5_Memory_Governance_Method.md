# Praxis R2 — C5: Memory & Governance Method
**Owner:** Memory & Governance Engineer (C5)
**Depends on (fixed ground truth, not re-derived here):** `C1_Data_Semantic_Foundation_v2.md` §14 (lineage/ID scheme, `validation_status` enum), §13 (data-state vocabulary, "missing ≠ negative evidence"). `06_C3_Reasoning_Retrieval_Method.md` §8 (`memory_hook` / `memory_query`, `result_schema_reserved=true`), §6 (the `confidence_score` formula this component extends, additively, never rewritten). `08_C4_Decision_Persona_Method.md` (the actual S1 `DecisionPackage`, used verbatim as the seed record).
**Out of scope here:** UI/orchestration (C6) — this document hands C6 the schemas and the worked Decision 1→3 sequence; C6 wires the memory-toggle demo UI around it.
**Decision Classification Ledger:** as C1–C4 — 🔒 LOCKED / 🧪 PROTOTYPE ASSUMPTION / ❓ OPEN.

---

## 0. What this component has to prove

A real S1 finding — `FIND-KPI-zone_gmv-Z003-20260815-01`, `QUALIFY`/`LOW`, stockout at DS041 leading — gets validated by a later observed outcome, becomes governed memory, and measurably (not decoratively) improves a comparable later finding's confidence. The boost must be **earned from a confirmed outcome, not from a prior record merely existing**, and it must be **explicitly capped**, because N=1 is not statistically robust evidence. Both constraints are enforced in the arithmetic below, not left as prose caveats.

---

## 1. Memory record schema

Both objects use C1 §14's ID scheme and both carry a mandatory `demo_fixture: bool` — the honesty mechanism the Business Brief requires, so the system's own audit trail can always distinguish seeded-for-demo memory from a genuinely captured live decision.

```yaml
DecisionMemory:
  decision_memory_id: string        # DEC-{finding_id}-{seq}, C1 §14 style
  finding_id: string                 # FK, C1 §14 finding ID
  driver_type: string                 # must be a governed driver per C1 §5 / C3 §1's constraint
  grain_key: string                   # dark_store_id or zone_id
  grain_level: enum[store, zone]
  original_confidence_band: enum[HIGH, MEDIUM, LOW, INSUFFICIENT]  # from C4's DecisionPackage.actions[].confidence, verbatim
  action_taken: string                 # the lever actually executed (C4 §1 lever id + concrete action text)
  validation_status: enum[pending, approved, rejected, demo_preapproved]  # C1's existing enum, unchanged
  demo_fixture: bool                   # 🔒 mandatory, no default
  created_at: timestamp                # ISO-8601, IST

OutcomeMemory:
  outcome_memory_id: string           # OUT-{decision_memory_id}-{seq}
  decision_memory_id: string           # FK, must resolve to an admitted DecisionMemory (§2)
  observed_outcome: string              # concrete, e.g. "DS041 stockout rate returned to baseline
                                          # within 36h of restock; GMV recovered over next 2 days"
  outcome_matches_hypothesis: bool       # did reality confirm the leading hypothesis this decision acted on?
  observed_at: timestamp
  demo_fixture: bool                    # 🔒 mandatory, no default
  created_at: timestamp
```

**Design note:** `demo_fixture` is carried on *both* objects independently rather than inherited, because a live `DecisionMemory` could in principle later receive a fixture-seeded `OutcomeMemory` during testing (or vice versa) — collapsing them into one flag on one object would hide that combination from audit. 🔒 LOCKED.

---

## 2. Memory Admission Gateway

One function, two entry points — **this is a locked design constraint restated from the Business Brief, not an aspiration**: the demo seed enters `DecisionMemory`/`OutcomeMemory` through the exact same `admit_decision_memory()` / `admit_outcome_memory()` gateway functions a live decision/outcome pair would use. `demo_preapproved` is a value the gateway accepts as a caller-supplied entry state; it is not a separate code path that bypasses validation.

```
admit_decision_memory(record) -> ADMITTED | QUARANTINED | REJECTED
```

| Check | Outcome if failed |
|---|---|
| `finding_id` resolves via C1 §14 lineage lookup | REJECTED — cannot attach memory to a finding that doesn't exist |
| `demo_fixture` is non-null (`true`/`false`, not omitted) | REJECTED — mandatory field, structural not instructional |
| `driver_type` is a governed driver (C1 §5 list, or `"residual"`) | REJECTED — same inherited constraint as C3 §1 |
| `decision_memory_id` not already present (idempotency) | QUARANTINED (duplicate) — held, not silently overwritten, same spirit as C1 §12's duplicate-`order_id` handling |
| `validation_status` supplied by caller is one of the 4 enum values | REJECTED if not — no new values invented here |
| **Entry-state rule:** if `demo_fixture=true`, the gateway accepts `validation_status=demo_preapproved` as the entry state; if `demo_fixture=false`, the gateway accepts only `validation_status=pending` as the entry state — a live decision cannot self-declare `approved` on entry | REJECTED if a live (`demo_fixture=false`) record is submitted with anything other than `pending` |
| All checks pass | ADMITTED |

```
admit_outcome_memory(record) -> ADMITTED | QUARANTINED | REJECTED
```

| Check | Outcome if failed |
|---|---|
| `decision_memory_id` resolves to an ADMITTED `DecisionMemory` | REJECTED — cannot attach an outcome to a decision that was itself rejected or never admitted |
| Referenced `DecisionMemory.validation_status ≠ rejected` | REJECTED — a rejected decision's outcome is not governed memory (§3 excludes it from retrieval anyway; refusing admission keeps the store from accumulating orphaned records) |
| `demo_fixture` non-null | REJECTED |
| `outcome_matches_hypothesis` non-null (`true`/`false`) | REJECTED — this field is never optional; "no outcome yet" is represented by the **absence** of an `OutcomeMemory` row, not by a null boolean inside one (§3 distinguishes these two cases explicitly) |
| `outcome_memory_id` not already present | QUARANTINED (duplicate) |
| All checks pass | **ADMITTED regardless of whether `outcome_matches_hypothesis` is `true` or `false`** — a contradicted outcome is admitted exactly like a confirmed one; rejection is never a function of *which way* the outcome came out (§2.1) |

### 2.1 Contradicted precedents are admitted, retrievable, and directionally informative — never discarded

A record with `outcome_matches_hypothesis=false` is **not** rejected, quarantined, or treated as a failed memory. It is admitted through the identical gateway and remains retrievable. Per §3/§4, it is used to **lower** confidence on a comparable future hypothesis, the mirror image of a confirmed precedent — a confirmed-wrong guess is informative in the opposite direction, not informationless.

This is explicitly distinct from **genuinely-insufficient-evidence**: a `DecisionMemory` that was admitted but has *no* `OutcomeMemory` row at all yet (outcome not yet observed). That case is not "contradicted" and is not "confirmed" — it is silence, and per C1 §13's non-negotiable rule ("missing ≠ negative evidence"), silence is scored as **zero** contribution, never as a penalty. The three states — confirmed / contradicted / no-outcome-yet — are kept structurally distinct all the way through retrieval (§3) and the confidence formula (§4); none of them collapses into another. 🔒 LOCKED.

---

## 3. Retrieval — answering C3's reserved `memory_query`

C3 §8 fixed the query shape (`driver_type`, `kpi_id`, `comparable_scope.grain_key/grain_level`, `requested_fields`) and reserved `result` (`result_schema_reserved=true`). This section defines the actual populated `result` object — filling the slot, not renaming or relocating it.

```
retrieve_memory(driver_type, kpi_id, grain_key, grain_level) -> MemoryQueryResult
```

**Matching order (per C3's own stated fallback rule):**
1. Exact `grain_key` match among ADMITTED `DecisionMemory` records with matching `driver_type` (and same `kpi_id` family) whose `validation_status ≠ rejected`.
2. If none found, fall back to `grain_level=zone`: any admitted record whose `grain_key` resolves to the same zone (store-level records roll up to their `zone_id` via C1's canonical entity model for this fallback only — the original `grain_key` is preserved in the returned record, never rewritten to the zone).
3. If still none, return an explicit empty result — **never an error, never a null crash** — because most findings early in the system's life will have nothing to match against (this is the expected steady state, not an edge case).

```yaml
MemoryQueryResult:
  matched: bool
  match_scope: enum[exact_grain, zone_fallback, none]
  prior_validation_status: enum[pending, approved, rejected, demo_preapproved] | null
  prior_confidence_band: enum[HIGH, MEDIUM, LOW, INSUFFICIENT] | null   # most-recent matched DecisionMemory's original_confidence_band
  prior_outcome_observed: bool | null   # true=confirmed, false=contradicted, null=matched decision(s) exist but none has an outcome yet
  confirmed_precedent_count: int         # distinct admitted DecisionMemory ids with an ADMITTED, outcome_matches_hypothesis=true OutcomeMemory
  contradicted_precedent_count: int      # same, outcome_matches_hypothesis=false
  representative_decision_memory_id: string | null   # exact-grain match preferred; most-recent otherwise
  demo_fixture_involved: bool            # true if any contributing record has demo_fixture=true — surfaced, never hidden, for audit transparency
```

`rejected` `DecisionMemory` records are excluded from matching entirely (§2, admission-gateway note) — a decision the business itself vetoed doesn't inform future confidence about whether the *hypothesis* was right. If `matched=false`, every other field is `null`/`0` and this is the literal empty-result contract C3 needs to safely compute `memory_points=0` (§4). 🔒 LOCKED.

---

## 4. The confidence-boost extension — additive term, plugged into C3 §6

Applies **only when `memory_hook.result.matched=true`**. This is an additive term on top of C3's existing `confidence_score`; none of C3's own components (`materiality_strength`, `dominance_strength`, `customer_voice_score`, `data_quality_penalty`) are touched.

### 4.1 The point term

```
memory_points =
    confirmed_component(confirmed_precedent_count)
  − contradicted_component(contradicted_precedent_count)
  − mixed_signal_penalty                          # only if both counts > 0

confirmed_component(n) = clamp(12 + 6×(n−1), 0, 25)   for n ≥ 1, else 0
contradicted_component(n) = clamp(12 + 6×(n−1), 0, 25) for n ≥ 1, else 0
mixed_signal_penalty = 5 if confirmed_precedent_count > 0 AND contradicted_precedent_count > 0, else 0

raw_score_with_memory = clamp(raw_score(C3 §6) + memory_points, 0, 100)
```

**Reasoning for the numbers:** +12 for a first confirmed precedent is deliberately modest relative to C3's own component ranges (0–30 each) — a single real-world confirmation is worth roughly a third of a maxed-out component, not a dominant share of the score. The +6-per-additional-precedent tapering with a +25 ceiling means confirmations have diminishing marginal value (consistent with the statistical intuition that the 2nd, 3rd... independent confirmation adds less new information than the 1st). The contradicted side mirrors this exactly, since a confirmed-wrong guess is exactly as informative in the opposite direction (§2.1). The `mixed_signal_penalty` is the same design principle C3 §6 already applies to its own `customer_voice_score` (an unresolved internal conflict is worse than silence) — restated here for consistency, not reinvented. 🧪 PROTOTYPE ASSUMPTION — concrete numbers, same status as C4's ₹15,000/2-rider thresholds: illustrative, product sign-off pending.

### 4.2 The hard cap — structural, not arithmetic-only (§0's actual requirement)

Band indices: `INSUFFICIENT=0, LOW=1, MEDIUM=2, HIGH=3` (C3 §6 thresholds, unchanged).

```
pre_memory_band_index   = band_index(raw_score)                    # C3's own score, no memory
naive_band_index        = band_index(raw_score_with_memory)        # after adding memory_points

max_rise   = min(confirmed_precedent_count, 2)   # 1 precedent → at most +1 band; ≥2 independent
                                                   # confirmed precedents → at most +2 bands (only
                                                   # path that can reach HIGH from LOW)
max_fall   = min(contradicted_precedent_count, 2)

final_band_index = clamp(naive_band_index,
                          pre_memory_band_index − max_fall,
                          pre_memory_band_index + max_rise)
final_band_index = clamp(final_band_index, 0, 3)
final_confidence_band = band(final_band_index)
```

If `final_band_index ≠ naive_band_index`, `hard_caps_applied` (C3 §11's list on the `Hypothesis` object) gains `"memory_boost_capped_n={confirmed_precedent_count}"` — the same discipline C3 §6 already uses for its own hard caps: documented on the object, never a silent clamp. **A single confirmed precedent (N=1) can never move `LOW→HIGH` directly, regardless of how large `raw_score_with_memory` computes** — `max_rise=1` makes that arithmetically impossible, not just discouraged. 🔒 LOCKED — this is the exact requirement from the task brief §4, expressed as code, not prose.

---

## 5. Worked example — Decision 1 → Decision 3

### 5.1 Decision 1 (already real, from C1–C4)

`FIND-KPI-zone_gmv-Z003-20260815-01`, `QUALIFY`, leading hypothesis `dark_store_stockout_rate` at DS041, `contribution_pct=55.0%`, C3's computed `confidence_score=16.1` → `LOW`. Zone Business Head authorizes **L2** (cross-store transfer) per C4 §7.1's narrative.

**DecisionMemory (live, real record):**
```yaml
decision_memory_id: DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01
finding_id: FIND-KPI-zone_gmv-Z003-20260815-01
driver_type: dark_store_stockout_rate
grain_key: DS041
grain_level: store
original_confidence_band: LOW
action_taken: "L2 — cross-store transfer of SKU-2207 and 3 related SKUs into DS041, authorized by Zone Business Head"
validation_status: demo_preapproved     # per the signature-demo entry rule, §2
demo_fixture: true
created_at: 2026-08-15T18:00:00+05:30
```

**Seed the outcome**, run through the §2 gateway:
```yaml
outcome_memory_id: OUT-DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01-01
decision_memory_id: DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01
observed_outcome: "DS041 stockout rate for SKU-2207 and related SKUs returned to baseline
                    within 36 hours of the transfer landing; Z003 daily GMV recovered to within
                    2% of baseline over the following 2 days."
outcome_matches_hypothesis: true
observed_at: 2026-08-17T12:00:00+05:30
demo_fixture: true
created_at: 2026-08-17T12:05:00+05:30
```
Both admitted via §2's checks (finding resolves, `driver_type` governed, `demo_fixture=true` present, `validation_status=demo_preapproved` matches the fixture entry rule).

### 5.2 Decision 3 — a comparable later finding

A week later, a comparable stockout pattern recurs at the same store: `FIND-KPI-zone_gmv-Z003-20260822-01`, dominant driver `dark_store_stockout_rate` at DS041 again (`contribution_pct=55%`), `z=−4.9` (a somewhat sharper dip this time), Customer Voice again mixed (one `Fresh` `supports`, one weaker `contradicts` — the same evidentiary pattern as Decision 1's window, not manufactured to be cleaner).

**C3's own computation, unaffected by memory (§6, unchanged formula):**
```
materiality_strength = clamp((4.9−2.5)/2.5×30, 0, 30) = 28.80
dominance_strength    = clamp((55−30)/70×30, 0, 30)   = 10.71
customer_voice_score  = −10                              (mixed, same pattern as Decision 1)
data_quality_penalty  = 0
raw_score             = clamp(28.80+10.71−10−0, 0, 100) = 29.51  →  LOW  (pre-memory)
```

**C5's retrieval (§3):** query `{driver_type: dark_store_stockout_rate, kpi_id: zone_gmv, grain_key: DS041, grain_level: store}` → exact-grain match on `DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01`. `confirmed_precedent_count=1`, `contradicted_precedent_count=0`, `prior_outcome_observed=true`, `match_scope=exact_grain`, `demo_fixture_involved=true` (surfaced, not hidden — this precedent is demo-seeded and the audit trail says so).

**C5's confidence extension (§4):**
```
memory_points = confirmed_component(1) − 0 − 0 = 12
raw_score_with_memory = clamp(29.51 + 12, 0, 100) = 41.51

pre_memory_band_index = band_index(29.51) = LOW (1)
naive_band_index      = band_index(41.51) = MEDIUM (2)
max_rise = min(1, 2) = 1        → allowed delta = +1 level
actual delta = +1 level         → within cap, no clamp triggered
final_confidence_band = MEDIUM
```
**Counterfactual sanity check (shows the cap is real, not decorative):** even if the raw score computed by C3 alone had been, say, 60 (already near `HIGH`), `raw_score_with_memory = 72` would naively land in `HIGH` (band index 3) — but `max_rise=1` from `pre_memory_band_index` (`MEDIUM`, if the raw score alone were 60) forces `final_band_index ≤ 3`... more concretely, starting from a `LOW` raw score as here, `max_rise=1` caps the *ceiling* at `MEDIUM` (index 2) no matter how large `raw_score_with_memory` computes — a single precedent structurally cannot produce `HIGH` from a `LOW` starting point. Reaching `HIGH` from `LOW` would require `confirmed_precedent_count ≥ 2` (independent precedents), per §4.2.

**C3's decision (§7, unchanged): still `QUALIFY`, not `ANSWER`** — `MEDIUM` doesn't clear the `HIGH` threshold `ANSWER` requires, so the memory boost never manufactures an unqualified answer out of one precedent, exactly what §0 forbids.

### 5.3 Side-by-side artifact — the literal on-screen comparison

| | **Decision 1** (no memory) | **Decision 3** (with memory) |
|---|---|---|
| C2 operators run | Full: detection, PVM decomposition, segmentation, Customer Voice matching, day→month eligibility | **Identical, full set — memory never shortcuts C2's detection/materiality gate** |
| `memory_hook.result` | `matched=false` (C5 didn't exist yet) | `matched=true`, `match_scope=exact_grain`, 1 confirmed precedent |
| C3 raw `confidence_score` (unaffected by memory) | 16.1 | 29.51 |
| `memory_points` | n/a | +12 |
| Final `confidence_score` | 16.1 | 41.51 |
| `confidence_band` | **LOW** | **MEDIUM** |
| `hard_caps_applied` (memory-related) | — | none triggered (actual rise = allowed rise = 1 level) |
| C3 `decision.outcome` | QUALIFY | QUALIFY (never ANSWER — cap prevents that) |
| C4 lever (`driver_type→lever` mapping, unchanged, §1) | L2 — cross-store transfer | L2 — cross-store transfer (same deterministic mapping; lever choice is never influenced by memory) |
| Caveat framing (C4 §3/§6, LLM only rephrases, never softens the band) | Heavily hedged: "offered as a reasonable next step, not a certainty," recommends pairing with a follow-up investigation (L7-adjacent) if the gap persists | Less hedged: this exact driver/lever/store combination has one directly confirmed precedent; still explicitly not treated as certain (MEDIUM, not HIGH), but the caveat can state the precedent plainly instead of speculating |
| Follow-up/escalation load | Monitoring plan pairs the transfer with an open follow-up-investigation contingency | Monitoring plan narrows to a single confirmatory re-check, since the causal story already played out once at this exact store |

This is the demo's signature moment: identical upstream investigation depth, a materially different, arithmetically-justified confidence outcome downstream.

---

## 6. LLM / non-LLM boundary, specific to C5

| | Deterministic (this component) | Never delegated to an LLM |
|---|---|---|
| Schema validation, gateway admit/quarantine/reject logic | ✅ pure rule evaluation | — |
| Retrieval matching (exact-grain → zone-fallback → empty) | ✅ pure lookup | — |
| `memory_points` arithmetic and the band-level hard cap | ✅ pure formula | — |
| Narrating a retrieved memory into persona-facing prose (e.g., "this is the second time DS041 has had this exact pattern") | — | This is C4's/the persona-narrative layer's job (C4 §6), not C5's — C5 hands back a structured `MemoryQueryResult`, never a sentence |

The entire C5 component — schema, admission gateway, retrieval matching, and the confidence-boost formula — is deterministic logic with zero LLM involvement, the same trust/governance category as C1's validation and C2's statistics. 🔒 LOCKED.

---

## 7. C5 Acceptance Tests

Given→When→Then, matching C1 §18 / C2 §10 / C3 §12 / C4 §8 house style.

1. **Given** the S1 `DecisionPackage` and a plausible confirming outcome, both tagged `demo_fixture=true`, **when** they are submitted to `admit_decision_memory()`/`admit_outcome_memory()`, **then** both are ADMITTED, the `DecisionMemory` lands at `validation_status=demo_preapproved`, and the `OutcomeMemory` carries `outcome_matches_hypothesis=true` — through the same gateway a live pair would use, not a separate path.
2. **Given** a live (`demo_fixture=false`) `DecisionMemory` submitted with `validation_status=approved`, **when** it reaches the gateway, **then** it is REJECTED — a live record may only enter at `pending`; only a later, separate approval step (out of scope here) may move it to `approved`/`rejected`.
3. **Given** Decision 3's `memory_query` (`driver_type=dark_store_stockout_rate`, `grain_key=DS041`, `grain_level=store`), **when** retrieval runs against an admitted Decision 1 record at the same `grain_key`, **then** `match_scope=exact_grain` and `representative_decision_memory_id` resolves to `DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01`.
4. **Given** a single confirmed precedent (`confirmed_precedent_count=1`) and a `raw_score_with_memory` that would naively compute two band levels above `pre_memory_band_index`, **when** §4.2's cap is applied, **then** `final_band_index` is clamped to exactly one level above `pre_memory_band_index`, and `hard_caps_applied` records `"memory_boost_capped_n=1"`.
5. **Given** a `DecisionMemory`/`OutcomeMemory` pair with `outcome_matches_hypothesis=false` (a contradicted precedent), **when** a comparable future `memory_query` is run, **then** the record is retrievable (`contradicted_precedent_count ≥ 1`, not silently dropped) and `memory_points` in §4.1 computes as negative for that contribution, never zero and never discarded.
6. **Given** a `DecisionMemory` with no corresponding `OutcomeMemory` row at all, **when** it is the only matching record for a query, **then** `prior_outcome_observed=null` (not `false`), `confirmed_precedent_count=0`, `contradicted_precedent_count=0`, and `memory_points=0` — genuinely-insufficient-evidence is never scored as contradiction.
7. **Given** a `memory_query` whose `driver_type`/`grain_key` combination has no admitted precedent at either store or zone level, **when** retrieval runs, **then** it returns `{matched: false, match_scope: none, ...all other fields null/0}` — an explicit empty result, never a thrown error.
8. **Given** both a confirmed and a contradicted precedent match the same query (`confirmed_precedent_count≥1` and `contradicted_precedent_count≥1`), **when** `memory_points` is computed, **then** the `mixed_signal_penalty` of 5 is applied on top of the net of the two components, consistent with C3 §6's own mixed-signal design for `customer_voice_score`.
9. **Given** a `DecisionMemory` referencing a `finding_id` that does not resolve via C1 §14 lineage, **when** it is submitted to the gateway, **then** it is REJECTED before ever entering the memory store — an unresolvable lineage reference is never silently admitted.

---

## 8. Deliverables index (per task brief §8)

1. `DecisionMemory` / `OutcomeMemory` schemas, with mandatory `demo_fixture` — §1
2. Memory Admission Gateway rules, including contradicted-precedent handling — §2, §2.1
3. Retrieval logic answering C3's exact `memory_query` shape — §3
4. Confidence-boost formula (additive term, explicit cap, stated reasoning) — §4
5. Worked Decision 1 → Decision 3 sequence with the side-by-side comparison — §5
6. LLM/non-LLM boundary statement — §6
7. Acceptance tests — §7

**Handed to C6:** the final `DecisionMemory`/`OutcomeMemory` schemas (§1), the gateway's two-entry-point contract (§2), and the worked Decision 1→3 sequence with its side-by-side artifact (§5.3) — everything C6 needs to build the demo's memory-toggle UI without re-deriving any of this component's logic.
