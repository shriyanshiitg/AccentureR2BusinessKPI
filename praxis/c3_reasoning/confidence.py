"""C3 §6 — Confidence Formula + Abstention Policy.

Deterministic code — not an LLM judgment call (C3 §9 row 2).
Formula:
  confidence_score = clamp(
      materiality_strength(0-30)
    + dominance_strength(0-30)
    + customer_voice_score(-20 to +20)
    - data_quality_penalty(0-30)
  , 0, 100)

Hard caps applied after arithmetic (C3 §6).
Abstention policy in §7.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ConfidenceBand(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"

    @classmethod
    def from_score(cls, score: int) -> "ConfidenceBand":
        if score >= 70:
            return cls.HIGH
        elif score >= 40:
            return cls.MEDIUM
        elif score >= 15:
            return cls.LOW
        else:
            return cls.INSUFFICIENT

    @property
    def index(self) -> int:
        return {"INSUFFICIENT": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}[self.value]

    @classmethod
    def from_index(cls, idx: int) -> "ConfidenceBand":
        return [cls.INSUFFICIENT, cls.LOW, cls.MEDIUM, cls.HIGH][max(0, min(3, idx))]


class DecisionOutcome(str, Enum):
    ANSWER = "ANSWER"
    QUALIFY = "QUALIFY"
    CLARIFY = "CLARIFY"
    ABSTAIN = "ABSTAIN"


@dataclass
class ConfidenceResult:
    raw_score: float
    band: ConfidenceBand
    hard_caps_applied: List[str]
    components: dict  # for transparency

    # Sub-scores
    materiality_strength: float = 0.0
    dominance_strength: float = 0.0
    customer_voice_score: float = 0.0
    data_quality_penalty: float = 0.0


def compute_confidence(
    kpi_id: str,
    test_statistic: float,        # z-score or p-value or relative-change
    test_type: str,                # "z_score" | "proportion_z" | "relative_change"
    contribution_pct: float,       # this hypothesis's contribution %
    no_dominant_contributor: bool,
    cv_supports: int,              # count of 'supports' records
    cv_supports_fresh: bool,       # True if any supporting record is Fresh
    cv_contradicts: int,           # count of 'contradicts' records
    cv_missing: bool,              # True if CV was simply unavailable
    evaluated_on_stale: bool,
    partial_excluded: bool,
    conflicting_input: bool,
    provisional_rpr_link: bool = False,
    memory_points: float = 0.0,   # C5 additive term
    confirmed_precedent_count: int = 0,
    contradicted_precedent_count: int = 0,
) -> ConfidenceResult:
    """
    Compute the confidence score for a single hypothesis.
    memory_points is 0 when C5 has no match (default) and non-zero when a
    prior record was retrieved.
    """
    hard_caps: List[str] = []

    # ---- materiality_strength (0-30) ----
    if test_type == "z_score":
        ms = _clamp((abs(test_statistic) - 2.5) / 2.5 * 30, 0, 30)
    elif test_type == "proportion_z":
        # p_value: lower p → higher strength
        p = test_statistic
        ms = _clamp((0.05 - p) / 0.05 * 30, 0, 30) if p <= 0.05 else 0.0
    elif test_type == "relative_change":
        ms = _clamp((abs(test_statistic) - 0.15) / 0.15 * 30, 0, 30)
    else:
        ms = 0.0

    # ---- dominance_strength (0-30) ----
    if no_dominant_contributor:
        ds = 0.0  # hard rule: no partial credit
    else:
        ds = _clamp((contribution_pct - 30) / 70 * 30, 0, 30)

    # ---- customer_voice_score (-20 to +20) ----
    if cv_missing:
        cvs = 0.0  # absence of evidence ≠ negative evidence (C1 §13)
    elif cv_contradicts > 0 and cv_supports == 0:
        cvs = -20.0
    elif cv_contradicts > 0 and cv_supports > 0:
        cvs = -10.0  # mixed signal
    elif cv_supports > 0 and cv_supports_fresh:
        cvs = 20.0
    elif cv_supports > 0:
        cvs = 10.0  # only stale/partial supports
    else:
        cvs = 0.0

    # ---- data_quality_penalty (0-30, subtracted) ----
    dqp = 0.0
    if conflicting_input:
        dqp += 20.0
    if evaluated_on_stale:
        dqp += 15.0
    if partial_excluded:
        dqp += 10.0
    dqp = min(dqp, 30.0)

    raw = _clamp(ms + ds + cvs - dqp, 0, 100)

    # Include memory boost (C5 §4 — additive term)
    raw_with_memory = _clamp(raw + memory_points, 0, 100)

    # ---- Hard caps ----
    naive_band = ConfidenceBand.from_score(int(raw_with_memory))
    pre_memory_band = ConfidenceBand.from_score(int(raw))

    # C5 band-level cap
    if memory_points != 0:
        max_rise = min(confirmed_precedent_count, 2)
        max_fall = min(contradicted_precedent_count, 2)
        pre_idx = pre_memory_band.index
        naive_idx = naive_band.index
        clamped_idx = max(pre_idx - max_fall, min(pre_idx + max_rise, naive_idx))
        clamped_idx = max(0, min(3, clamped_idx))
        if clamped_idx != naive_idx:
            hard_caps.append(f"memory_boost_capped_n={confirmed_precedent_count}")
        naive_band = ConfidenceBand.from_index(clamped_idx)

    final_band = naive_band

    # no_dominant_contributor → cap at MEDIUM
    if no_dominant_contributor:
        if final_band == ConfidenceBand.HIGH:
            final_band = ConfidenceBand.MEDIUM
            hard_caps.append("no_dominant_contributor")

    # contradicts-only CV → cap at MEDIUM
    if cv_contradicts > 0 and cv_supports == 0:
        if final_band == ConfidenceBand.HIGH:
            final_band = ConfidenceBand.MEDIUM
            hard_caps.append("cv_contradicts_only")

    # conflicting_input → cap at MEDIUM
    if conflicting_input:
        if final_band == ConfidenceBand.HIGH:
            final_band = ConfidenceBand.MEDIUM
            hard_caps.append("conflicting_input")

    # provisional RPR link → cap at LOW
    if provisional_rpr_link:
        if final_band in (ConfidenceBand.HIGH, ConfidenceBand.MEDIUM):
            final_band = ConfidenceBand.LOW
            hard_caps.append("provisional_rpr_link")

    return ConfidenceResult(
        raw_score=raw_with_memory,
        band=final_band,
        hard_caps_applied=hard_caps,
        components={
            "materiality_strength": ms,
            "dominance_strength": ds,
            "customer_voice_score": cvs,
            "data_quality_penalty": dqp,
            "memory_points": memory_points,
            "raw_pre_memory": raw,
            "raw_with_memory": raw_with_memory,
        },
        materiality_strength=ms,
        dominance_strength=ds,
        customer_voice_score=cvs,
        data_quality_penalty=dqp,
    )


def decide_outcome(
    terminal_outcome: str,
    band: ConfidenceBand,
    hard_caps: List[str],
    has_clarifying_dimension: bool = False,
    abstain_reason: Optional[str] = None,
) -> DecisionOutcome:
    """
    C3 §7 abstention policy — decision function.
    terminal_outcome drives the first check, then band.
    """
    if terminal_outcome == "INSUFFICIENT_HISTORY":
        return DecisionOutcome.ABSTAIN
    if terminal_outcome == "SKIPPED":
        return DecisionOutcome.ABSTAIN
    if terminal_outcome == "NON_MATERIAL":
        return DecisionOutcome.ANSWER  # confident "no movement" — not abstention
    if terminal_outcome == "NO_DOMINANT_CONTRIBUTOR":
        return DecisionOutcome.QUALIFY

    # EVALUATED
    if band == ConfidenceBand.HIGH:
        return DecisionOutcome.ANSWER
    elif band == ConfidenceBand.MEDIUM:
        return DecisionOutcome.QUALIFY
    elif band == ConfidenceBand.LOW:
        if has_clarifying_dimension:
            return DecisionOutcome.CLARIFY
        return DecisionOutcome.QUALIFY
    else:  # INSUFFICIENT
        return DecisionOutcome.ABSTAIN


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))
