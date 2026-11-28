#!/usr/bin/env python3
"""Capture selected live trace records and their deterministic summary."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace_ids", nargs="+")
    parser.add_argument("--traces-out", type=Path,
                        default=ROOT / "traces/phase3_samples.jsonl")
    parser.add_argument("--out", type=Path,
                        default=ROOT / "eval/results/phase3_trace_observability.json")
    args = parser.parse_args()
    completed = subprocess.run(
        ["kubectl", "-n", "rahbar", "exec", "deployment/api", "--", "sh", "-c",
         "cat /traces/*.jsonl"], check=True, capture_output=True, text=True,
    )
    wanted = set(args.trace_ids)
    rows = [json.loads(line) for line in completed.stdout.splitlines() if line]
    selected = [row for row in rows if row.get("trace_id") in wanted]
    missing = wanted - {row["trace_id"] for row in selected}
    if missing:
        raise SystemExit(f"missing trace IDs: {sorted(missing)}")
    args.traces_out.parent.mkdir(parents=True, exist_ok=True)
    args.traces_out.write_text("".join(json.dumps(row) + "\n" for row in selected), encoding="utf-8")
    scores = [item["score"] for row in selected for item in row.get("retrieved", [])]
    stages = {stage: sorted(row.get("latency_ms", {}).get(stage, 0.0) for row in selected)
              for stage in ("embedding", "retrieval", "generation", "total")}
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "cluster": "minikube/rahbar",
        "trace_ids": args.trace_ids,
        "run_context": "Kubernetes API temporary stub generator; Batch B collection for injected-document trace",
        "trace_count": len(selected),
        "top1_similarity_distribution": {
            "count": len(scores), "min": min(scores, default=0.0), "max": max(scores, default=0.0),
        },
        "abstention_rate": sum(row.get("outcome") == "abstained_or_fallback" for row in selected) / len(selected),
        "cache_hit_rate": sum(row.get("cache") == "hit" for row in selected) / len(selected),
        "injection_attempts_flagged": sum(bool(row.get("guardrail_actions")) for row in selected),
        "p95_latency_ms": {stage: values[-1] for stage, values in stages.items()},
        "replay": {
            row["trace_id"]: hashlib.sha256(
                json.dumps(row.get("prompt", []), sort_keys=True).encode()
            ).hexdigest() == row.get("prompt_hash") for row in selected
        },
        "injected_document_trace": next((row for row in selected
                                         if "retrieved_instruction_removed:1" in row.get("guardrail_actions", [])), None),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.traces_out}")
    print(f"wrote {args.out}")
    print(f"replay_ok={all(payload['replay'].values())}")
    print(f"injection_flagged={payload['injection_attempts_flagged']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
