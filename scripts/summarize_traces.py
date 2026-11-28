#!/usr/bin/env python3
"""Summarise JSONL query traces for a time window without calling an LLM."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import quantiles


def percentile95(values: list[float]) -> float:
    if not values:
        return 0.0
    return values[0] if len(values) == 1 else quantiles(values, n=100)[94]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    scores = [float(item["score"]) for row in rows for item in row.get("retrieved", [])]
    stages = {stage: [float(row.get("latency_ms", {}).get(stage, 0.0)) for row in rows
                      if stage in row.get("latency_ms", {})]
              for stage in ("embedding", "retrieval", "generation", "total")}
    payload = {
        "traces": len(rows),
        "top1_similarity": [row["retrieved"][0]["score"] for row in rows if row.get("retrieved")],
        "top1_similarity_distribution": {"count": len(scores), "min": min(scores, default=0.0),
                                            "max": max(scores, default=0.0)},
        "abstention_rate": (sum(row.get("outcome") == "abstained_or_fallback" for row in rows) /
                            len(rows) if rows else 0.0),
        "cache_hit_rate": (sum(row.get("cache") == "hit" for row in rows) / len(rows) if rows else 0.0),
        "injection_attempts_flagged": sum(bool(row.get("guardrail_actions")) for row in rows),
        "p95_latency_ms": {stage: round(percentile95(values), 3) for stage, values in stages.items()},
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
