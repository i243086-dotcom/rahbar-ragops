#!/usr/bin/env python3
"""Apply the Part C release gate to measured baseline and candidate JSON results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def metric(result: dict[str, Any], name: str) -> float | None:
    """Read Phase 4 metrics or the compact candidate format."""
    if name in result and isinstance(result[name], (int, float)):
        return float(result[name])
    for section in ("answers", "retrieval", "metrics"):
        value = result.get(section, {}).get(name)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def evaluate(baseline: dict[str, Any], candidate: dict[str, Any], thresholds: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    baseline_recall = metric(baseline, "recall_at_5")
    candidate_recall = metric(candidate, "recall_at_5")
    if baseline_recall is None or candidate_recall is None:
        failures.append("recall_at_5 is missing from baseline or candidate")
    elif baseline_recall - candidate_recall > float(thresholds["max_recall_at_5_drop"]):
        failures.append(
            f"recall@5 drop {baseline_recall - candidate_recall:.4f} exceeds "
            f"{float(thresholds['max_recall_at_5_drop']):.4f}"
        )
    # Prefer the human-reviewed score when available; the citation proxy is a
    # provisional fallback until human labels have been recorded.
    faithfulness = metric(candidate, "human_faithfulness")
    if faithfulness is None:
        faithfulness = metric(candidate, "faithfulness_citation_proxy")
    if faithfulness is None:
        failures.append("candidate faithfulness is missing")
    elif faithfulness < float(thresholds["min_faithfulness"]):
        failures.append(
            f"faithfulness {faithfulness:.4f} is below {float(thresholds['min_faithfulness']):.4f}"
        )
    latency = metric(candidate, "latency_p95_ms")
    if latency is None:
        failures.append("candidate latency_p95_ms is missing")
    elif latency > float(thresholds["max_latency_p95_ms"]):
        failures.append(
            f"p95 latency {latency:.2f} ms exceeds {float(thresholds['max_latency_p95_ms']):.2f} ms"
        )
    baseline_abstain = metric(baseline, "abstention_correctness")
    candidate_abstain = metric(candidate, "abstention_correctness")
    if baseline_abstain is None or candidate_abstain is None:
        failures.append("abstention_correctness is missing from baseline or candidate")
    elif candidate_abstain - baseline_abstain < float(thresholds["min_abstention_correctness_delta"]):
        failures.append(
            f"abstention correctness changed from {baseline_abstain:.4f} to {candidate_abstain:.4f}"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path, default=Path(__file__).with_name("phase5_gate.yaml"))
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    thresholds = yaml.safe_load(args.thresholds.read_text(encoding="utf-8")) or {}
    failures = evaluate(baseline, candidate, thresholds)
    print(f"baseline={args.baseline}")
    print(f"candidate={args.candidate}")
    print(f"thresholds={args.thresholds}")
    if failures:
        print("GATE FAILED")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

