"""Structured JSON telemetry — per-finding latency, LLM calls, token usage, cost estimates.
Build Brief §4 requirement.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

IST = timezone(timedelta(hours=5, minutes=30))

# Groq pricing (approximate, llama-3.3-70b-versatile)
COST_PER_1K_PROMPT_TOKENS = 0.00059   # USD
COST_PER_1K_COMPLETION_TOKENS = 0.00079  # USD


class Telemetry:
    def __init__(self, log_path: str = "data/telemetry.jsonl"):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self._log_path = log_path
        self._run_id: Optional[str] = None
        self._run_start: Optional[float] = None
        self._llm_calls: List[Dict] = []
        self._finding_id: Optional[str] = None

    def start_run(self, run_id: str, scenario: str, finding_id: Optional[str] = None):
        self._run_id = run_id
        self._run_start = time.perf_counter()
        self._llm_calls = []
        self._finding_id = finding_id
        self._emit({
            "event": "run_start",
            "run_id": run_id,
            "scenario": scenario,
            "finding_id": finding_id,
        })

    def record_llm_call(self, model: str, prompt_tokens: int,
                        completion_tokens: int, latency_ms: float):
        cost = (
            (prompt_tokens / 1000) * COST_PER_1K_PROMPT_TOKENS
            + (completion_tokens / 1000) * COST_PER_1K_COMPLETION_TOKENS
        )
        record = {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": round(latency_ms, 2),
            "cost_usd": round(cost, 6),
        }
        self._llm_calls.append(record)
        self._emit({"event": "llm_call", "run_id": self._run_id, **record})

    def record_phase(self, phase: str, outcome: str, duration_ms: float,
                     details: Optional[Dict] = None):
        self._emit({
            "event": "phase_complete",
            "run_id": self._run_id,
            "finding_id": self._finding_id,
            "phase": phase,
            "outcome": outcome,
            "duration_ms": round(duration_ms, 2),
            **(details or {}),
        })

    def end_run(self, final_outcome: str, details: Optional[Dict] = None):
        total_ms = (time.perf_counter() - (self._run_start or time.perf_counter())) * 1000
        total_tokens = sum(c["total_tokens"] for c in self._llm_calls)
        total_cost = sum(c["cost_usd"] for c in self._llm_calls)
        total_llm_calls = len(self._llm_calls)

        self._emit({
            "event": "run_complete",
            "run_id": self._run_id,
            "finding_id": self._finding_id,
            "final_outcome": final_outcome,
            "total_latency_ms": round(total_ms, 2),
            "total_llm_calls": total_llm_calls,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            **(details or {}),
        })

        return {
            "run_id": self._run_id,
            "finding_id": self._finding_id,
            "final_outcome": final_outcome,
            "total_latency_ms": round(total_ms, 2),
            "total_llm_calls": total_llm_calls,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
        }

    def _emit(self, record: Dict[str, Any]):
        record["ts"] = datetime.now(tz=IST).isoformat()
        with open(self._log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def summary(self) -> Dict:
        total_ms = (time.perf_counter() - (self._run_start or time.perf_counter())) * 1000
        return {
            "run_id": self._run_id,
            "total_latency_ms": round(total_ms, 2),
            "total_llm_calls": len(self._llm_calls),
            "total_tokens": sum(c["total_tokens"] for c in self._llm_calls),
            "total_cost_usd": round(sum(c["cost_usd"] for c in self._llm_calls), 6),
        }
