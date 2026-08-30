"""LLM Client — Groq wrapper (bounded per C3 §9 / C4 §6 boundary tables).

Only exposed methods:
  - generate_text(prompt, max_tokens) -> str

Structural guarantees:
  - max_tokens hard-capped at 512 (structural, not configurable)
  - Response cache (SHA-256 keyed) prevents redundant API calls for identical prompts
  - Cache is in-process only (no persistence) — safe for demo, appropriate for prototype
  - temperature=0.3 for factual bounded generation
  - All calls are logged through the telemetry module
"""
from __future__ import annotations

import hashlib
import os
import time
from typing import Dict, Optional, Tuple


GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS_HARD_LIMIT = 512   # structural cap — never configurable
CACHE_MAX_ENTRIES = 256       # evict LRU when full (simple FIFO for prototype)

# Module-level in-process cache: {cache_key: (text, prompt_tokens, completion_tokens)}
_response_cache: Dict[str, Tuple[str, int, int]] = {}
_cache_hits: int = 0
_cache_misses: int = 0


def _cache_key(prompt: str, max_tokens: int) -> str:
    """Deterministic cache key: SHA-256 of (prompt + max_tokens + model)."""
    payload = f"{GROQ_MODEL}|{max_tokens}|{prompt}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def get_cache_stats() -> Dict:
    return {
        "cache_hits": _cache_hits,
        "cache_misses": _cache_misses,
        "cache_size": len(_response_cache),
        "hit_rate": (
            round(_cache_hits / (_cache_hits + _cache_misses), 3)
            if (_cache_hits + _cache_misses) > 0 else 0.0
        ),
    }


class GroqLLMClient:
    def __init__(self, api_key: Optional[str] = None, telemetry=None):
        from groq import Groq
        key = api_key or os.environ.get("GROQ_API_KEY", "")
        self._client = Groq(api_key=key)
        self._telemetry = telemetry

    def generate_text(self, prompt: str, max_tokens: int = 200) -> str:
        """Call Groq and return the generated text.

        Uses in-process SHA-256 cache to avoid redundant API calls for identical prompts.
        Cache hits are recorded in telemetry with latency=0ms, cost=0.
        """
        global _cache_hits, _cache_misses

        max_tokens = min(max_tokens, MAX_TOKENS_HARD_LIMIT)
        key = _cache_key(prompt, max_tokens)

        # --- Cache hit ---
        if key in _response_cache:
            _cache_hits += 1
            text, pt, ct = _response_cache[key]
            if self._telemetry:
                self._telemetry.record_llm_call(
                    model=f"{GROQ_MODEL}[cached]",
                    prompt_tokens=0,     # no API call made
                    completion_tokens=0,
                    latency_ms=0.0,
                )
            return text

        # --- Cache miss: call Groq ---
        _cache_misses += 1
        t0 = time.perf_counter()

        response = self._client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3,   # low temperature for factual bounded generation
        )

        latency_ms = (time.perf_counter() - t0) * 1000
        text = response.choices[0].message.content.strip()
        usage = response.usage

        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0

        if self._telemetry:
            self._telemetry.record_llm_call(
                model=GROQ_MODEL,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
            )

        # Evict oldest if at capacity (simple FIFO)
        if len(_response_cache) >= CACHE_MAX_ENTRIES:
            oldest_key = next(iter(_response_cache))
            del _response_cache[oldest_key]

        _response_cache[key] = (text, prompt_tokens, completion_tokens)
        return text
