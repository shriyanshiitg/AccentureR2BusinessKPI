"""C5 — Memory & Governance.
Implements C5 §1-4:
- DecisionMemory and OutcomeMemory schemas
- Memory Admission Gateway (admit_decision_memory / admit_outcome_memory)
- Retrieval (exact-grain → zone fallback → empty)
- Confidence boost formula with hard band cap
"""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import duckdb

from praxis.c1_data_foundation.schemas import ValidationStatus

IST = timezone(timedelta(hours=5, minutes=30))
DB_PATH = os.environ.get("PRAXIS_DB_PATH", "data/praxis.duckdb")


def _get_conn():
    os.makedirs("data", exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS decision_memory (
        decision_memory_id VARCHAR PRIMARY KEY,
        finding_id VARCHAR NOT NULL,
        driver_type VARCHAR NOT NULL,
        grain_key VARCHAR NOT NULL,
        grain_level VARCHAR NOT NULL,
        original_confidence_band VARCHAR NOT NULL,
        action_taken VARCHAR NOT NULL,
        validation_status VARCHAR NOT NULL,
        demo_fixture BOOLEAN NOT NULL,
        created_at VARCHAR NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS outcome_memory (
        outcome_memory_id VARCHAR PRIMARY KEY,
        decision_memory_id VARCHAR NOT NULL,
        observed_outcome VARCHAR NOT NULL,
        outcome_matches_hypothesis BOOLEAN NOT NULL,
        observed_at VARCHAR NOT NULL,
        demo_fixture BOOLEAN NOT NULL,
        created_at VARCHAR NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS lineage_registry (
        entity_id VARCHAR PRIMARY KEY,
        entity_type VARCHAR NOT NULL,
        created_at VARCHAR NOT NULL
    )
    """)


def register_finding_id(finding_id: str):
    """Register a finding_id in the lineage registry (C5 §2 check 1)."""
    conn = _get_conn()
    now = datetime.now(tz=IST).isoformat()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO lineage_registry VALUES (?, 'finding', ?)",
            [finding_id, now]
        )
    except Exception:
        conn.execute(
            "INSERT INTO lineage_registry VALUES (?, 'finding', ?) ON CONFLICT DO NOTHING",
            [finding_id, now]
        )
    conn.close()


def _finding_exists(conn, finding_id: str) -> bool:
    rows = conn.execute(
        "SELECT 1 FROM lineage_registry WHERE entity_id = ? AND entity_type = 'finding'",
        [finding_id]
    ).fetchall()
    return len(rows) > 0


# GENERICITY FIX (Task 1): derive from KPI contracts at import time.
# Any new KPI's drivers are included automatically — no edits needed here.
from praxis.c1_data_foundation.kpi_contracts import get_all_governed_drivers as _gad
GOVERNED_DRIVERS = _gad()

VALID_VALIDATION_STATUSES = {v.value for v in ValidationStatus}


# ---------------------------------------------------------------------------
# C5 §2 — Memory Admission Gateway
# ---------------------------------------------------------------------------

class AdmissionResult:
    ADMITTED = "ADMITTED"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


def admit_decision_memory(record: Dict[str, Any]) -> Dict[str, str]:
    """
    C5 §2 gateway: admit, quarantine, or reject a DecisionMemory record.
    Returns {"status": ..., "reason": ...}
    """
    conn = _get_conn()

    def _reject(reason: str):
        conn.close()
        return {"status": AdmissionResult.REJECTED, "reason": reason}

    def _quarantine(reason: str):
        conn.close()
        return {"status": AdmissionResult.QUARANTINED, "reason": reason}

    # Check 1: finding_id resolves via C1 §14 lineage lookup
    fid = record.get("finding_id")
    if not fid or not _finding_exists(conn, fid):
        return _reject("finding_id not found in lineage registry (C5 §2 check 1)")

    # Check 2: demo_fixture is non-null (True or False, not missing)
    if "demo_fixture" not in record or record["demo_fixture"] is None:
        return _reject("demo_fixture is mandatory (C5 §2 check 2)")

    # Check 3: driver_type is governed or 'residual'
    dt = record.get("driver_type", "")
    if dt not in GOVERNED_DRIVERS:
        return _reject(f"driver_type '{dt}' not a governed driver (C5 §2 check 3)")

    # Check 4: idempotency
    dmid = record.get("decision_memory_id")
    if not dmid:
        return _reject("decision_memory_id is required")
    existing = conn.execute(
        "SELECT 1 FROM decision_memory WHERE decision_memory_id = ?", [dmid]
    ).fetchall()
    if existing:
        return _quarantine(f"duplicate decision_memory_id={dmid!r}")

    # Check 5: validation_status is a valid enum value
    vs = record.get("validation_status", "")
    if vs not in VALID_VALIDATION_STATUSES:
        return _reject(f"validation_status={vs!r} not in enum (C5 §2 check 5)")

    # Check 6: entry-state rule
    demo = record.get("demo_fixture", False)
    if demo and vs not in ("demo_preapproved", "pending"):
        return _reject(
            "demo_fixture=True records must enter with validation_status="
            "'demo_preapproved' or 'pending' (C5 §2 check 6)"
        )
    if not demo and vs != "pending":
        return _reject(
            "live (demo_fixture=False) records must enter with validation_status='pending' "
            "(C5 §2 check 6)"
        )

    # All checks pass → ADMITTED
    now = datetime.now(tz=IST).isoformat()
    conn.execute(
        """INSERT INTO decision_memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            dmid,
            fid,
            dt,
            record.get("grain_key", ""),
            record.get("grain_level", "store"),
            record.get("original_confidence_band", ""),
            record.get("action_taken", ""),
            vs,
            bool(demo),
            record.get("created_at", now),
        ]
    )
    conn.close()
    return {"status": AdmissionResult.ADMITTED, "reason": "all checks passed"}


def admit_outcome_memory(record: Dict[str, Any]) -> Dict[str, str]:
    """
    C5 §2 gateway: admit, quarantine, or reject an OutcomeMemory record.
    """
    conn = _get_conn()

    def _reject(reason: str):
        conn.close()
        return {"status": AdmissionResult.REJECTED, "reason": reason}

    def _quarantine(reason: str):
        conn.close()
        return {"status": AdmissionResult.QUARANTINED, "reason": reason}

    # Check 1: decision_memory_id resolves to an ADMITTED DecisionMemory
    dmid = record.get("decision_memory_id")
    dm_rows = conn.execute(
        "SELECT validation_status FROM decision_memory WHERE decision_memory_id = ?",
        [dmid]
    ).fetchall()
    if not dm_rows:
        return _reject(
            f"decision_memory_id={dmid!r} not found (C5 §2 outcome check 1)"
        )

    # Check 2: referenced DecisionMemory.validation_status != rejected
    vs = dm_rows[0][0]
    if vs == "rejected":
        return _reject(
            "Referenced DecisionMemory was rejected — cannot attach outcome (C5 §2 check 2)"
        )

    # Check 3: demo_fixture non-null
    if "demo_fixture" not in record or record["demo_fixture"] is None:
        return _reject("demo_fixture is mandatory (C5 §2 check 3)")

    # Check 4: outcome_matches_hypothesis non-null (bool)
    omh = record.get("outcome_matches_hypothesis")
    if omh is None:
        return _reject(
            "outcome_matches_hypothesis must be true or false (C5 §2 check 4); "
            "'no outcome yet' is represented by absence of a row, not null inside one"
        )

    # Check 5: idempotency
    omid = record.get("outcome_memory_id")
    if not omid:
        return _reject("outcome_memory_id is required")
    existing = conn.execute(
        "SELECT 1 FROM outcome_memory WHERE outcome_memory_id = ?", [omid]
    ).fetchall()
    if existing:
        return _quarantine(f"duplicate outcome_memory_id={omid!r}")

    # All checks pass → ADMITTED (regardless of which way outcome_matches_hypothesis went)
    now = datetime.now(tz=IST).isoformat()
    conn.execute(
        """INSERT INTO outcome_memory VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            omid,
            dmid,
            record.get("observed_outcome", ""),
            bool(omh),
            record.get("observed_at", now),
            bool(record.get("demo_fixture")),
            record.get("created_at", now),
        ]
    )
    conn.close()
    return {"status": AdmissionResult.ADMITTED, "reason": "all checks passed"}


# ---------------------------------------------------------------------------
# C5 §3 — Retrieval
# ---------------------------------------------------------------------------

def retrieve_memory(driver_type: str, kpi_id: str, grain_key: str,
                    grain_level: str, store_to_zone: Dict[str, str] = None) -> Dict:
    """
    C5 §3 retrieval: exact-grain → zone fallback → empty result.
    Returns a MemoryQueryResult dict (never throws).
    """
    conn = _get_conn()

    try:
        _empty = {
            "matched": False,
            "match_scope": "none",
            "prior_validation_status": None,
            "prior_confidence_band": None,
            "prior_outcome_observed": None,
            "confirmed_precedent_count": 0,
            "contradicted_precedent_count": 0,
            "representative_decision_memory_id": None,
            "demo_fixture_involved": False,
        }

        # Step 1: exact grain_key match, same driver_type, kpi_id family, not rejected
        rows = conn.execute("""
            SELECT dm.decision_memory_id, dm.validation_status, dm.original_confidence_band,
                   dm.demo_fixture, dm.grain_key
            FROM decision_memory dm
            WHERE dm.driver_type = ?
              AND dm.grain_key = ?
              AND dm.validation_status != 'rejected'
            ORDER BY dm.created_at DESC
        """, [driver_type, grain_key]).fetchall()

        match_scope = "exact_grain"
        if not rows and store_to_zone and grain_level == "store":
            # Step 2: zone fallback
            zone_id = store_to_zone.get(grain_key)
            if zone_id:
                rows = conn.execute("""
                    SELECT dm.decision_memory_id, dm.validation_status, dm.original_confidence_band,
                           dm.demo_fixture, dm.grain_key
                    FROM decision_memory dm
                    WHERE dm.driver_type = ?
                      AND dm.validation_status != 'rejected'
                      AND dm.grain_key IN (
                          SELECT grain_key FROM decision_memory WHERE grain_key LIKE ?
                      )
                    ORDER BY dm.created_at DESC
                """, [driver_type, f"{zone_id}%"]).fetchall()
            match_scope = "zone_fallback"

        if not rows:
            conn.close()
            return _empty

        # Count confirmed and contradicted precedents
        rep_dm_id = rows[0][0]
        rep_vs = rows[0][1]
        rep_band = rows[0][2]
        demo_fixture_involved = any(r[3] for r in rows)
        dm_ids = [r[0] for r in rows]

        # Fetch outcomes
        placeholders = ", ".join("?" * len(dm_ids))
        outcomes = conn.execute(f"""
            SELECT decision_memory_id, outcome_matches_hypothesis
            FROM outcome_memory
            WHERE decision_memory_id IN ({placeholders})
        """, dm_ids).fetchall()

        confirmed_count = sum(1 for _, omh in outcomes if omh is True)
        contradicted_count = sum(1 for _, omh in outcomes if omh is False)

        # prior_outcome_observed:
        # true=confirmed, false=contradicted, null=no outcome row at all
        dm_ids_with_outcomes = {r[0] for r in outcomes}
        any_outcome_for_rep = rep_dm_id in dm_ids_with_outcomes
        if any_outcome_for_rep:
            rep_outcomes = [omh for did, omh in outcomes if did == rep_dm_id]
            prior_outcome_observed = rep_outcomes[0] if rep_outcomes else None
        else:
            prior_outcome_observed = None

        conn.close()
        return {
            "matched": True,
            "match_scope": match_scope,
            "prior_validation_status": rep_vs,
            "prior_confidence_band": rep_band,
            "prior_outcome_observed": prior_outcome_observed,
            "confirmed_precedent_count": confirmed_count,
            "contradicted_precedent_count": contradicted_count,
            "representative_decision_memory_id": rep_dm_id,
            "demo_fixture_involved": demo_fixture_involved,
        }

    except Exception as e:
        conn.close()
        # C5 §3: never throw, return explicit empty result
        return {
            "matched": False,
            "match_scope": "none",
            "prior_validation_status": None,
            "prior_confidence_band": None,
            "prior_outcome_observed": None,
            "confirmed_precedent_count": 0,
            "contradicted_precedent_count": 0,
            "representative_decision_memory_id": None,
            "demo_fixture_involved": False,
            "_retrieval_error": str(e),
        }


# ---------------------------------------------------------------------------
# C5 §4 — Confidence boost computation (standalone, used in c3 too)
# ---------------------------------------------------------------------------

def compute_memory_points(confirmed_count: int, contradicted_count: int) -> float:
    """C5 §4.1 — memory_points arithmetic."""
    def _component(n):
        return min(12 + 6 * (n - 1), 25) if n >= 1 else 0
    conf = _component(confirmed_count)
    contra = _component(contradicted_count)
    mixed = 5 if confirmed_count > 0 and contradicted_count > 0 else 0
    return conf - contra - mixed
