# Praxis R2 — Master Handoff & Autonomous Build Protocol
**Read this document first, before any other file in this bundle.**
This project was built by working through nine specialized AI personas in sequence, each reasoning from a narrow, focused brief and handing concrete output to the next. That process is now finished. From here, the build runs without anyone supervising it step by step — this document exists to make that safe.

---

## 1. File manifest — attach all of these, in this order

| # | File | What it is | Required? |
|---|---|---|---|
| 1 | The original Accenture R2 problem statement (PDF) | Ground truth above all five component specs — the only authority left if something genuinely isn't covered below | **Required** |
| 2 | `Praxis_Business_and_Signature_Story_Brief_Edited.md` | Domain, KPIs, personas, competitive positioning, and the exact signature-demo script the whole build exists to demonstrate | **Required** |
| 3 | `C1_Data_Semantic_Foundation_v2.md` | Schemas, entities, KPI contracts, entitlements, lineage — everything downstream depends on this | **Required** |
| 4 | `04_C2_Analytical_Investigation_Method.md` (patched version, not the original v2) | Materiality, detection, decomposition operators | **Required** |
| 5 | `06_C3_Reasoning_Retrieval_Method.md` | Hypothesis generation, evidence, confidence, abstention | **Required** |
| 6 | `08_C4_Decision_Persona_Method.md` | Business levers, decision rights, persona narratives | **Required** |
| 7 | `10_C5_Memory_Governance_Method.md` | Memory schema, admission gateway, the confidence-boost mechanism the signature demo depends on | **Required** |
| 8 | `11_Build_Orchestration_Brief.md` | The actual build instructions — tech stack, build order, acceptance bar | **Required** |
| 9 | This document | Navigation, open-items index, stuck-state protocol | **Required** |

**Not needed — superseded, don't attach:** the original numbered task briefs I wrote to *produce* C1–C5 (the "Analytical Method Brief," "Reasoning & Retrieval Brief," "Decision & Persona Brief," "Memory & Governance Brief"). Everything load-bearing in them is already restated inside C1–C5's own "depends on" sections. Attaching them adds bulk without adding information now that the outputs exist.

## 2. Authority order, if anything ever appears to conflict

Each document explicitly built on the ones before it, so if a real conflict is ever found (unlikely, given how much cross-checking already happened — see §3), resolve in this order: **the original PS > Business Brief > C1 > C2 > C3 > C4 > C5 > the Build Brief.** A downstream document is never allowed to silently override an upstream one; if C6/Antigravity finds what looks like a contradiction, it should be logged explicitly (see §4), not quietly resolved in whichever direction is easiest to code.

## 3. Known open items — indexed, not restated

Every 🧪 PROTOTYPE ASSUMPTION and ❓ OPEN item across C1–C5 is already resolved with stated reasoning *within its own document* — nothing below is new information, this is just a map so it doesn't have to be found by searching five long files under time pressure:

- **C1:** four open items (customer tenure filter, historical retention window, GMV/line-item reconciliation tolerance, `home_zone_id` fallback) — see C1's own "How open items are handled" section, and each KPI YAML's inherited notes.
- **C2:** the `INSUFFICIENT_HISTORY` clean-day floor and the `NO_DOMINANT_CONTRIBUTOR` 30% dominance bar — see the patched C2's Operator 1 and Operator 3 sections and its §0 changelog.
- **C3:** the month-end evidence-window anchor for RPR, the 15%/20% hypothesis-generation floors, the confidence-band thresholds and hard caps — see C3 §1–§2 and §6–§7.
- **C4:** the ₹15,000/2-rider auto-execution ceilings (explicitly flagged ❓ OPEN for real product sign-off, adopted as a stated prototype default), and the ABSTAIN/NON_MATERIAL proactive-surfacing decisions — see C4 §2–§3.
- **C5:** the confidence-boost cap logic and its constants — see C5 §4.

**Rule for the build:** treat every one of these as decided. Do not re-open or second-guess them mid-implementation. If the actual demo needs a different number (e.g., the ₹15,000 ceiling doesn't suit the generated data), adjust the *value* but keep the *mechanism and reasoning* — and log the change (§4).

## 4. Protocol for anything not covered — this is the part that matters most

Nobody is available to answer questions during this build. When Antigravity hits something genuinely not resolved by the PS, the Business Brief, or C1–C5:

1. **Do not stall waiting for clarification that isn't coming.**
2. **Make a concrete, defensible choice** — the same discipline every document in this bundle already used. Don't leave a TODO or a placeholder.
3. **Tag and log it** — a running `BUILD_DECISIONS.md` (or equivalent) in the repo, one line per decision: what was ambiguous, what was chosen, why. This is exactly the 🔒/🧪/❓ discipline C1 started, continued into the code itself.
4. **Prefer the choice that keeps the system honest over the choice that looks better in a demo.** If a shortcut would make a scenario look more confident than the actual logic justifies, don't take it — every document in this bundle exists specifically to prevent manufactured confidence; a build-time shortcut that reintroduces it defeats the entire point.

## 5. If time runs short — cut in this order, not randomly

Highest to lowest priority to keep, if something has to give:
1. The synthetic data generator and a genuinely unscripted resilience-test run (Build Brief §0/§11) — without this, nothing else can be trusted.
2. The full C1→C5 pipeline running end to end on at least the S1 scenario.
3. The Decision 1 → Decision 3 memory comparison (the signature moment — this is the project's actual differentiation, protect it before UI polish).
4. Both persona narratives, correctly entitlement-filtered.
5. Telemetry display, UI polish, the second/third demonstration scenarios (CLARIFY, INSUFFICIENT_HISTORY as their own worked cases).

Do not cut from the top of this list to spend more time on the bottom.

## 6. The one acceptance bar that overrides all others

Restated from the Build Brief because it's the most important sentence in this whole bundle: **the system must produce a coherent result for a scenario nobody hand-scripted, through the real pipeline.** If that doesn't hold, nothing else — however polished — actually demonstrates what Round 2 is asking for.
