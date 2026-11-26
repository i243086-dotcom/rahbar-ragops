#!/usr/bin/env python3
"""Capture Phase 0 Kubernetes proof from live API responses and indexer logs."""

from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ask(api: str, question: str) -> dict:
    body = json.dumps({"question": question}).encode()
    request = urllib.request.Request(
        f"{api.rstrip('/')}/api/ask", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:  # noqa: S310
        return json.load(response)


def indexer_events(job: str) -> list[dict]:
    completed = subprocess.run(
        ["kubectl", "logs", "-n", "rahbar", f"job/{job}"],
        check=True, capture_output=True, text=True,
    )
    return [json.loads(line) for line in completed.stdout.splitlines() if line.startswith("{")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:18000")
    parser.add_argument("--job", required=True)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "eval/results/phase0_baseline.json")
    args = parser.parse_args()

    events = indexer_events(args.job)
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "cluster": "minikube/rahbar",
        "indexer_job": args.job,
        "indexer_events": events,
        "cited_query": ask(args.api, "What CGPA puts an undergraduate student on academic warning?"),
        "abstention_query": ask(args.api, "How do I apply for a hostel room?"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"indexer_events={len(events)}")
    print(f"cited={bool(payload['cited_query']['citations'])}")
    print(f"abstained={not payload['abstention_query']['answered_from_context']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
