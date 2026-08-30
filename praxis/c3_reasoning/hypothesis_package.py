"""C3 §11 — HypothesisPackage: the C3→C4 handoff schema.

Assembles all C3 outputs into a single, C4-consumable package.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from praxis.c2_analytical.evidence_package import EvidencePackage
from praxis.c3_reasoning.generator import Hypothesis, generate_hypotheses
from praxis.c3_reasoning.challenge import challenge_hypotheses
from praxis.c3_reasoning.confidence import (
    ConfidenceBand, ConfidenceResult, DecisionOutcome,
    compute_confidence, decide_outcome,
)


IST = timezone(timedelta(hours=5, minutes=30))


@dataclass
class HypothesisPackage:
    finding_id: str
    kpi_instance_id: str
    generated_at: str

    # Passthrough pointers
    evidence_package_ref: str
    lineage_chain: List[str]

    # NON_MATERIAL case
    answer_without_hypothesis: bool
    answer_without_hypothesis_text: Optional[str]

    # Ranked hypotheses
    hypotheses: List[Dict]

    # Decision (finding-level or per-hypothesis for partial abstains)
    decision: Dict

    def to_dict(self) -> Dict:
        import dataclasses
        return dataclasses.asdict(self)


def build_hypothesis_package(
    evidence_package: EvidencePackage,
    cv_records: List[Dict],
    zone_id: str,
    llm_client=None,
    memory_result: Optional[Dict] = None,   # C5 MemoryQueryResult dict
) -> HypothesisPackage:
    """
    Full C3 processing pipeline:
    1. Generate hypotheses (bounded)
    2. Retrieve + challenge Customer Voice
    3. Score confidence
    4. Apply hard caps
    5. Decide outcome
    6. Build HypothesisPackage
    """
    ep = evidence_package
    now = datetime.now(tz=IST).isoformat()

    # NON_MATERIAL — confident negative result, no hypotheses
    if ep.terminal_outcome == "NON_MATERIAL":
        return HypothesisPackage(
            finding_id=ep.finding_id,
            kpi_instance_id=ep.kpi_instance_id,
            generated_at=now,
            evidence_package_ref=ep.finding_id,
            lineage_chain=ep.lineage_chain,
            answer_without_hypothesis=True,
            answer_without_hypothesis_text=(
                f"No material movement detected for {ep.kpi_id} at "
                f"{ep.grain_key} on {ep.period}. This is C2's own confident "
                f"conclusion — normal variance."
            ),
            hypotheses=[],
            decision={
                "outcome": DecisionOutcome.ANSWER.value,
                "scope": "finding",
                "leading_hypothesis_id": None,
                "caveat_text": None,
                "clarifying_question": None,
                "abstain_reason": None,
            },
        )

    # INSUFFICIENT_HISTORY or SKIPPED — abstain
    if ep.terminal_outcome in ("INSUFFICIENT_HISTORY", "SKIPPED"):
        reason = ep.terminal_outcome_reason or ep.terminal_outcome
        return HypothesisPackage(
            finding_id=ep.finding_id,
            kpi_instance_id=ep.kpi_instance_id,
            generated_at=now,
            evidence_package_ref=ep.finding_id,
            lineage_chain=ep.lineage_chain,
            answer_without_hypothesis=False,
            answer_without_hypothesis_text=None,
            hypotheses=[],
            decision={
                "outcome": DecisionOutcome.ABSTAIN.value,
                "scope": "finding",
                "leading_hypothesis_id": None,
                "caveat_text": None,
                "clarifying_question": None,
                "abstain_reason": reason,
            },
        )

    # Generate hypotheses
    hypotheses = generate_hypotheses(ep, llm_client=llm_client)

    if not hypotheses:
        return HypothesisPackage(
            finding_id=ep.finding_id,
            kpi_instance_id=ep.kpi_instance_id,
            generated_at=now,
            evidence_package_ref=ep.finding_id,
            lineage_chain=ep.lineage_chain,
            answer_without_hypothesis=False,
            answer_without_hypothesis_text=None,
            hypotheses=[],
            decision={
                "outcome": DecisionOutcome.ABSTAIN.value,
                "scope": "finding",
                "leading_hypothesis_id": None,
                "caveat_text": None,
                "clarifying_question": None,
                "abstain_reason": "No hypotheses generated from decomposition",
            },
        )

    # Challenge (CV retrieval + polarity tagging)
    hypotheses, evidence_objects = challenge_hypotheses(
        hypotheses=hypotheses,
        cv_records=cv_records,
        zone_id=zone_id,
        terminal_outcome=ep.terminal_outcome,
        evaluated_on_stale=ep.evaluated_on_stale_input,
        partial_excluded=bool(ep.partial_sources_excluded),
        conflicting_input=ep.conflicting_input,
    )

    # Score confidence for each hypothesis
    no_dominant = ep.terminal_outcome == "NO_DOMINANT_CONTRIBUTOR"
    detection = ep.detection or {}
    test_stat = detection.get("test_statistic", 0.0)
    test_type = detection.get("test_type", "z_score")

    # Memory boost from C5
    mem_points = 0.0
    confirmed_count = 0
    contradicted_count = 0
    if memory_result and memory_result.get("matched"):
        confirmed_count = memory_result.get("confirmed_precedent_count", 0)
        contradicted_count = memory_result.get("contradicted_precedent_count", 0)
        # Compute memory_points per C5 §4.1
        def _mem_component(n):
            if n >= 1:
                return min(12 + 6 * (n - 1), 25)
            return 0
        conf_comp = _mem_component(confirmed_count)
        contra_comp = _mem_component(contradicted_count)
        mixed = 5 if confirmed_count > 0 and contradicted_count > 0 else 0
        mem_points = conf_comp - contra_comp - mixed

    hyp_dicts = []
    leading_hyp = None
    leading_score = -1

    for hyp in hypotheses:
        # Collect CV signals for this hypothesis
        evs = [e for e in evidence_objects if e["hypothesis_id"] == hyp.hypothesis_id]
        sup_fresh = sum(1 for e in evs if e["relationship"] == "supports"
                        and e["data_quality_state"] == "Fresh")
        sup_any = sum(1 for e in evs if e["relationship"] == "supports")
        contra = sum(1 for e in evs if e["relationship"] == "contradicts")
        cv_missing = len(evs) == 0

        conf = compute_confidence(
            kpi_id=ep.kpi_id,
            test_statistic=test_stat,
            test_type=test_type,
            contribution_pct=abs(hyp.contribution_pct or 0),
            no_dominant_contributor=no_dominant,
            cv_supports=sup_any,
            cv_supports_fresh=sup_fresh > 0,
            cv_contradicts=contra,
            cv_missing=cv_missing,
            evaluated_on_stale=ep.evaluated_on_stale_input,
            partial_excluded=bool(ep.partial_sources_excluded),
            conflicting_input=ep.conflicting_input,
            provisional_rpr_link=any(
                lk.get("eligible") and lk.get("linked_finding_id") and
                "repeat_purchase_rate" in str(lk.get("linked_finding_id", ""))
                for lk in ep.day_month_links
            ),
            memory_points=mem_points if not hyp.is_residual else 0.0,
            confirmed_precedent_count=confirmed_count,
            contradicted_precedent_count=contradicted_count,
        )

        hyp.confidence_score = int(conf.raw_score)
        hyp.confidence_band = conf.band.value
        hyp.hard_caps_applied = conf.hard_caps_applied

        sup_evs = [e["evidence_id"] for e in evs if e["relationship"] == "supports"]
        contra_evs = [e["evidence_id"] for e in evs if e["relationship"] == "contradicts"]
        ctx_evs = [e["evidence_id"] for e in evs if e["relationship"] == "contextualizes"]

        hyp_dict = {
            "hypothesis_id": hyp.hypothesis_id,
            "driver_type": hyp.driver_type,
            "claim": hyp.claim,
            "claim_status": hyp.claim_status,
            "status": hyp.status,
            "contribution_pct": hyp.contribution_pct,
            "confidence_score": hyp.confidence_score,
            "confidence_band": hyp.confidence_band,
            "hard_caps_applied": hyp.hard_caps_applied,
            "supporting_evidence_refs": sup_evs,
            "contradicting_evidence_refs": contra_evs,
            "contextualizing_evidence_refs": ctx_evs,
            "memory_hook": hyp.memory_hook,
            "is_residual": hyp.is_residual,
            "confidence_components": conf.components,
        }
        hyp_dicts.append(hyp_dict)

        if not hyp.is_residual and conf.band.index > leading_score:
            leading_score = conf.band.index
            leading_hyp = hyp_dict

    # Determine finding-level decision
    leading_band = ConfidenceBand(leading_hyp["confidence_band"]) if leading_hyp else ConfidenceBand.INSUFFICIENT
    has_clarify_dim = bool(ep.segmentation and ep.segmentation.get("ranked_stores"))

    outcome = decide_outcome(
        terminal_outcome=ep.terminal_outcome,
        band=leading_band,
        hard_caps=leading_hyp.get("hard_caps_applied", []) if leading_hyp else [],
        has_clarifying_dimension=has_clarify_dim,
    )

    # Build caveat text for QUALIFY
    caveat_text = None
    if outcome in (DecisionOutcome.QUALIFY, DecisionOutcome.CLARIFY):
        caveat_text = _build_caveat(leading_hyp, hyp_dicts, ep, llm_client, memory_result)

    clarifying_q = None
    if outcome == DecisionOutcome.CLARIFY and ep.segmentation:
        top_stores = ep.segmentation.get("ranked_stores", [])
        if top_stores:
            clarifying_q = (
                f"Could you confirm whether the pattern is concentrated at "
                f"{top_stores[0]['dark_store_id']} specifically, or spread across "
                f"multiple stores in {ep.grain_key}?"
            )

    abstain_reason = None
    if outcome == DecisionOutcome.ABSTAIN:
        abstain_reason = ep.terminal_outcome_reason or ep.terminal_outcome

    return HypothesisPackage(
        finding_id=ep.finding_id,
        kpi_instance_id=ep.kpi_instance_id,
        generated_at=now,
        evidence_package_ref=ep.finding_id,
        lineage_chain=ep.lineage_chain,
        answer_without_hypothesis=False,
        answer_without_hypothesis_text=None,
        hypotheses=hyp_dicts,
        decision={
            "outcome": outcome.value,
            "scope": "finding",
            "leading_hypothesis_id": leading_hyp["hypothesis_id"] if leading_hyp else None,
            "caveat_text": caveat_text,
            "clarifying_question": clarifying_q,
            "abstain_reason": abstain_reason,
            "memory_context": {
                "matched": memory_result.get("matched") if memory_result else False,
                "confirmed_precedents": confirmed_count,
                "contradicted_precedents": contradicted_count,
                "demo_fixture_involved": memory_result.get("demo_fixture_involved") if memory_result else False,
            } if memory_result else None,
        },
    )


def _build_caveat(leading_hyp, all_hyps, ep, llm_client, memory_result) -> str:
    """Build the mandatory caveat text for QUALIFY outcomes."""
    if not leading_hyp:
        return "Evidence is insufficient to draw a conclusion."

    driver = leading_hyp.get("driver_type", "unknown driver")
    pct = leading_hyp.get("contribution_pct", 0)
    band = leading_hyp.get("confidence_band", "LOW")
    contra_evs = leading_hyp.get("contradicting_evidence_refs", [])
    sup_evs = leading_hyp.get("supporting_evidence_refs", [])
    caps = leading_hyp.get("hard_caps_applied", [])

    # Secondary contributors
    secondary = [h for h in all_hyps
                 if h["hypothesis_id"] != leading_hyp["hypothesis_id"]
                 and not h.get("is_residual") and (h.get("contribution_pct") or 0) >= 15]

    residual_hyp = next((h for h in all_hyps if h.get("is_residual")), None)
    residual_pct = residual_hyp["contribution_pct"] if residual_hyp else ep.decomposition.get("residual_pct", 0) if ep.decomposition else 0

    # Memory context
    mem_sentence = ""
    if memory_result and memory_result.get("matched") and memory_result.get("confirmed_precedent_count", 0) > 0:
        mem_sentence = (
            f" One prior confirmed precedent for this driver at this store "
            f"has been retrieved from memory — this raises confidence from LOW to MEDIUM, "
            f"but a single precedent is not treated as confirmation (C5 §4.2 cap)."
        )

    if llm_client:
        try:
            secondary_str = ", ".join(
                f"{h['driver_type']} (~{h['contribution_pct']:.0f}%)"
                for h in secondary
            )
            prompt = (
                f"Write a 3-4 sentence caveat for a KPI intelligence report. "
                f"The leading explanation is '{driver}' contributing ~{pct:.0f}% "
                f"to a {ep.kpi_id} decline at {ep.grain_key} on {ep.period}. "
                f"Confidence band is {band}. "
                f"{'Customer Voice has mixed evidence (contradicting records exist).' if contra_evs else 'Customer Voice provides supporting evidence.' if sup_evs else 'No Customer Voice evidence available.'} "
                f"{'Secondary contributors: ' + secondary_str + '.' if secondary_str else ''} "
                f"Residual unexplained: ~{residual_pct:.0f}%. "
                f"Hard caps applied: {caps}. "
                f"Frame this as a qualified, not certain, finding. Be concise and honest."
            )
            llm_caveat = llm_client.generate_text(prompt, max_tokens=200)
            return llm_caveat + mem_sentence
        except Exception:
            pass

    # Deterministic fallback
    cv_sentence = ""
    if contra_evs and sup_evs:
        cv_sentence = "Customer Voice evidence is mixed — corroborating and contradicting signals both exist."
    elif contra_evs:
        cv_sentence = "Customer Voice evidence contradicts this explanation."
    elif sup_evs:
        cv_sentence = "Customer Voice evidence independently supports this explanation."
    else:
        cv_sentence = "No Customer Voice evidence is available for this period."

    secondary_str = ""
    if secondary:
        secondary_str = " Secondary contributors: " + "; ".join(
            f"{h['driver_type']} (~{abs(h['contribution_pct']):.0f}%)"
            for h in secondary
        ) + "."

    residual_str = f" {residual_pct:.0f}% of the movement remains unexplained." if residual_pct > 5 else ""

    return (
        f"Quantitative decomposition points to '{driver}' as the largest single contributor "
        f"(~{abs(pct):.0f}%), but this is presented as the leading explanation, not a confirmed one. "
        f"{cv_sentence}"
        f"{secondary_str}"
        f"{residual_str}"
        f"{mem_sentence}"
    )
