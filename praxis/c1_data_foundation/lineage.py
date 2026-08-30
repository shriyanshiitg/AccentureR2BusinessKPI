"""C1 §14 — Lineage ID Builder.

Deterministic ID scheme:
  Source record:   native key (e.g. order_id = ORD-88213)
  Dataset/version: {SRC_ID}-{batch_or_stream_version}
  Transformation:  {STAGE_PREFIX}-{grain_key}-{period}
  KPI evaluation:  KPI-{kpi_id}-{grain_key}-{period}
  Finding:         FIND-{kpi_instance_id}-{seq}
  Decision:        DEC-{finding_id}-{seq}
  Outcome:         OUT-{decision_memory_id}-{seq}
"""
from __future__ import annotations
from typing import List


def kpi_instance_id(kpi_id: str, grain_key: str, period: str) -> str:
    """e.g. KPI-zone_gmv-Z003-20260815"""
    return f"KPI-{kpi_id}-{grain_key}-{period}"


def finding_id(kpi_instance: str, seq: int = 1) -> str:
    """e.g. FIND-KPI-zone_gmv-Z003-20260815-01"""
    return f"FIND-{kpi_instance}-{seq:02d}"


def hypothesis_id(find_id: str, seq: int = 1) -> str:
    """e.g. HYP-FIND-KPI-zone_gmv-Z003-20260815-01-01"""
    return f"HYP-{find_id}-{seq:02d}"


def evidence_id(hyp_id: str, seq: int = 1) -> str:
    """e.g. EVID-HYP-...-01-01"""
    return f"EVID-{hyp_id}-{seq:02d}"


def decision_memory_id(find_id: str, seq: int = 1) -> str:
    """e.g. DEC-FIND-KPI-zone_gmv-Z003-20260815-01-01"""
    return f"DEC-{find_id}-{seq:02d}"


def outcome_memory_id(dec_mem_id: str, seq: int = 1) -> str:
    """e.g. OUT-DEC-FIND-...-01-01"""
    return f"OUT-{dec_mem_id}-{seq:02d}"


def decision_package_id(find_id: str, seq: int = 1) -> str:
    return f"DEC-PKG-{find_id}-{seq:02d}"


def transformation_id(stage_prefix: str, grain_key: str, period: str) -> str:
    """e.g. DZG-Z003-20260815"""
    return f"{stage_prefix}-{grain_key}-{period}"


def dataset_version_id(src_id: str, batch_ts: str) -> str:
    """e.g. SRC-OMS-v2026-08-15-14h"""
    return f"{src_id}-v{batch_ts}"


def build_lineage_chain(source_record_id: str, dataset_version: str,
                         transformation: str, kpi_inst: str, find: str) -> List[str]:
    """Return the ordered chain from source to finding."""
    return [source_record_id, dataset_version, transformation, kpi_inst, find]


# Edge table helpers
def lineage_edge(from_id: str, to_id: str, edge_type: str) -> dict:
    """Create a generic lineage edge dict as specified in C1 §14."""
    from datetime import datetime, timezone, timedelta
    ist = timezone(timedelta(hours=5, minutes=30))
    return {
        "from_id": from_id,
        "to_id": to_id,
        "edge_type": edge_type,
        "created_at": datetime.now(tz=ist).isoformat(),
    }
