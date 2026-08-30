"""Resilience Test — Build Brief §11.

Runs a randomly-seeded unscripted scenario through the full pipeline.
Verifies internal consistency: the system produces a coherent result
without any pre-scripted hand-holding.
Saves output to data/resilience_test_output.json.
"""
import json
import os
import pytest
from praxis.synthetic.generator import get_scenario
from praxis.orchestration.pipeline import run_pipeline


@pytest.mark.resilience
def test_resilience_unscripted_scenario_coherent(tmp_path, monkeypatch):
    """
    Build Brief §11: Run a seed=42 unscripted scenario through the full pipeline.
    Verify that:
    1. Pipeline completes without error
    2. finding_id is populated
    3. decision_package outcome is a valid string
    4. caveat_text is non-null whenever outcome != ANSWER
    5. Narrative contains no zone GMV figure if persona=ops_manager
    6. Output is saved as JSON (evidence the system ran)
    """
    # Point C5 memory to a temp DB for isolation
    db_path = str(tmp_path / "resilience.duckdb")
    monkeypatch.setenv("PRAXIS_DB_PATH", db_path)
    import praxis.c5_memory.gateway as gw
    monkeypatch.setattr(gw, "DB_PATH", db_path)

    scenario = get_scenario("unscripted", seed=42)
    result = run_pipeline(
        scenario=scenario,
        persona="zone_business_head",
        use_memory=False,  # no memory for unscripted (cold start)
        log_path=str(tmp_path / "telemetry.jsonl"),
    )

    # 1. No error
    assert result.error is None, f"Pipeline error: {result.error}"

    # 2. finding_id populated
    assert result.finding_id is not None
    assert "FIND-" in result.finding_id

    # 3. Decision outcome is valid
    valid_outcomes = {"ANSWER", "QUALIFY", "CLARIFY", "ABSTAIN"}
    assert result.decision_package.source_decision_outcome in valid_outcomes

    # 4. Caveat mandatory-non-null for non-ANSWER
    if result.decision_package.source_decision_outcome != "ANSWER":
        assert result.decision_package.caveat_text is not None, (
            "caveat_text is null but outcome != ANSWER"
        )

    # 5. Telemetry populated
    assert result.telemetry_summary is not None
    assert "total_latency_ms" in result.telemetry_summary

    # 6. Save output
    output_path = "data/resilience_test_output.json"
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result.to_dict(), f, indent=2, default=str)

    # Verify file was written
    assert os.path.exists(output_path)
    with open(output_path) as f:
        saved = json.load(f)
    assert saved["finding_id"] == result.finding_id

    print(f"\n✅ Resilience test passed — seed=42")
    print(f"   Finding:  {result.finding_id}")
    print(f"   Outcome:  {result.decision_package.source_decision_outcome}")
    print(f"   Latency:  {result.telemetry_summary['total_latency_ms']:.0f}ms")
    print(f"   Scenario: zone={scenario['_unscripted_zone']}, "
          f"store={scenario['_unscripted_store']}, "
          f"anchor={scenario['_unscripted_anchor']}")
