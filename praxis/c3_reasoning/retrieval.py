"""C3 §3 — Customer Voice Hybrid Retrieval.

Hybrid BM25 + embedding cosine similarity, fused by RRF.
Query templates per driver_type (bounded — never free LLM querying).
Restricted to zone's records within C1 §7.1 window [D-7, D+2].
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

# BM25
from rank_bm25 import BM25Okapi

# Sentence transformers (loaded lazily)
_encoder = None


def _get_encoder():
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer
        _encoder = SentenceTransformer("all-MiniLM-L6-v2")
    return _encoder


# ---------------------------------------------------------------------------
# Per-driver query templates — merged from KPI contracts (genericity fix) +
# explicit overrides for drivers whose terms don't map 1-to-1 to a single KPI.
# ---------------------------------------------------------------------------
def _build_driver_query_templates() -> dict:
    """Derive query templates from KPI contract cv_query_terms.
    GENERICITY: any new KPI's terms are picked up automatically.
    """
    from praxis.c1_data_foundation.kpi_contracts import KPI_CONTRACTS
    templates: Dict[str, List[str]] = {}

    # Seed from each contract's cv_query_terms (keyed by each driver)
    for contract in KPI_CONTRACTS.values():
        terms = contract.get("cv_query_terms", [])
        if not terms:
            continue
        for driver in contract.get("drivers", []):
            if driver not in templates:
                templates[driver] = list(terms)

    # Explicit per-driver overrides / additions (original entries preserved)
    _explicit: Dict[str, List[str]] = {
        "dark_store_stockout_rate": [
            "out of stock", "unavailable", "sold out", "couldn't add to cart",
            "not available", "item missing", "product unavailable",
        ],
        "delivery_sla_adherence": [
            "late", "never arrived", "still waiting", "delivery delay",
            "took too long", "late delivery", "delayed order",
        ],
        "order_conversion_rate": [
            "couldn't complete order", "checkout failed", "abandoned cart",
            "app crash", "couldn't place order",
        ],
        "discount_applied": ["coupon", "promo", "discount", "offer", "deal"],
        "rider_capacity": ["rider", "delivery person", "no rider", "long wait"],
        "competitor_dark_store_opening": [
            "other app", "switched", "competitor", "better option",
        ],
        "demand_spike": ["surge", "high demand", "busy", "unavailable due to demand"],
        "residual": [],
    }
    templates.update(_explicit)
    return templates


DRIVER_QUERY_TEMPLATES: Dict[str, List[str]] = _build_driver_query_templates()


def _tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokenizer."""
    import re
    return re.findall(r'\b\w+\b', text.lower())


def _cosine_similarity(a, b) -> float:
    """Numpy-free cosine similarity for small vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_customer_voice(
    driver_type: str,
    zone_id: str,
    anchor_date: date,
    cv_records: List[Dict],
    top_k: int = 5,
) -> List[Dict]:
    """
    Retrieve relevant Customer Voice records for a hypothesis.

    Parameters
    ----------
    driver_type : governed driver name or 'residual'
    zone_id : filter to this zone (C1 §2.3 — zone-level grain only)
    anchor_date : D in C1 §7.1 window [D-7, D+2]
    cv_records : list of Customer Voice record dicts
    top_k : max records to return

    Returns
    -------
    List of record dicts with added 'retrieval_score', 'query_template_used'
    """
    if driver_type == "residual" or driver_type not in DRIVER_QUERY_TEMPLATES:
        return []  # No retrieval for residual (C3 §10.3)

    # 1. Filter: zone + time window [D-7, D+2]
    window_start = anchor_date - timedelta(days=7)
    window_end = anchor_date + timedelta(days=2)

    candidates = []
    for rec in cv_records:
        if rec.get("zone_id") != zone_id:
            continue
        md = rec.get("matched_day")
        if isinstance(md, str):
            md = date.fromisoformat(md)
        if md and window_start <= md <= window_end:
            candidates.append(rec)

    if not candidates:
        return []

    query_terms = DRIVER_QUERY_TEMPLATES[driver_type]
    if not query_terms:
        return []

    query_text = " ".join(query_terms)

    # 2. BM25 scoring
    tokenized_docs = [_tokenize(r.get("text", "")) for r in candidates]
    bm25 = BM25Okapi(tokenized_docs)
    query_tokens = _tokenize(query_text)
    bm25_scores = bm25.get_scores(query_tokens)

    # 3. Embedding cosine similarity
    try:
        enc = _get_encoder()
        doc_texts = [r.get("text", "") for r in candidates]
        embeddings = enc.encode([query_text] + doc_texts)
        query_emb = embeddings[0]
        doc_embs = embeddings[1:]
        cos_scores = [_cosine_similarity(list(query_emb), list(de)) for de in doc_embs]
    except Exception:
        cos_scores = [0.0] * len(candidates)

    # 4. RRF fusion
    # Rank each list, compute RRF score = sum(1 / (k + rank))
    k = 60  # standard RRF constant

    bm25_ranked = sorted(range(len(candidates)), key=lambda i: bm25_scores[i], reverse=True)
    cos_ranked = sorted(range(len(candidates)), key=lambda i: cos_scores[i], reverse=True)

    bm25_rank = {idx: rank + 1 for rank, idx in enumerate(bm25_ranked)}
    cos_rank = {idx: rank + 1 for rank, idx in enumerate(cos_ranked)}

    rrf_scores = {
        i: 1.0 / (k + bm25_rank[i]) + 1.0 / (k + cos_rank[i])
        for i in range(len(candidates))
    }

    # 5. Take top_k
    top_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)[:top_k]

    result = []
    for idx in top_indices:
        rec = dict(candidates[idx])
        rec["retrieval_score"] = rrf_scores[idx]
        rec["query_template_used"] = driver_type
        result.append(rec)

    return result
