from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("phase5_gate", ROOT / "eval" / "phase5_gate.py")
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

THRESHOLDS = {
    "max_recall_at_5_drop": 0.02,
    "min_faithfulness": 0.80,
    "max_latency_p95_ms": 300000,
    "min_abstention_correctness_delta": 0.0,
}


def result(recall: float, faithfulness: float = 1.0, latency: float = 100.0, abstention: float = 1.0):
    return {
        "retrieval": {"recall_at_5": recall},
        "answers": {
            "faithfulness_citation_proxy": faithfulness,
            "latency_p95_ms": latency,
            "abstention_correctness": abstention,
        },
    }


def test_candidate_passes_thresholds() -> None:
    assert gate.evaluate(result(0.80), result(0.79), THRESHOLDS) == []


def test_candidate_fails_real_recall_regression() -> None:
    failures = gate.evaluate(result(0.80), result(0.70), THRESHOLDS)
    assert any("recall@5 drop" in failure for failure in failures)

