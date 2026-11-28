#!/usr/bin/env python3
"""Capture Part A evidence from completed Kubernetes ingestion Jobs."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "rahbar"


def run(*args: str) -> str:
    completed = subprocess.run(["kubectl", "-n", NAMESPACE, *args], check=True,
                               capture_output=True, text=True)
    return completed.stdout


def events(job: str) -> list[dict]:
    return [json.loads(line) for line in run("logs", f"job/{job}").splitlines()
            if line.startswith("{")]


def result_file(filename: str) -> dict:
    override = json.dumps({
        "spec": {
            "restartPolicy": "Never",
            "containers": [{
                "name": "reader", "image": "busybox:1.36",
                "command": ["cat", f"/results/{filename}"],
                "volumeMounts": [{"name": "results", "mountPath": "/results"}],
            }],
            "volumes": [{"name": "results", "persistentVolumeClaim": {"claimName": "eval-results"}}],
        }
    })
    output = run("run", "phase2-capture-reader", "--image=busybox:1.36", "--restart=Never",
                 "--rm", "-i", "--quiet", f"--overrides={override}")
    # `kubectl run --rm -i` may echo the same logs after a streaming fallback.
    # Decode the first complete JSON value only.
    start = output.index("{")
    value, _ = json.JSONDecoder().raw_decode(output[start:])
    return value


def archive_sha256(filename: str) -> str:
    override = json.dumps({
        "spec": {
            "restartPolicy": "Never",
            "containers": [{
                "name": "reader", "image": "busybox:1.36",
                "command": ["sha256sum", f"/archive/batch-b/{filename}"],
                "volumeMounts": [{"name": "archive", "mountPath": "/archive"}],
            }],
            "volumes": [{"name": "archive", "persistentVolumeClaim": {"claimName": "archive"}}],
        }
    })
    output = run("run", "phase2-archive-reader", "--image=busybox:1.36", "--restart=Never",
                 "--rm", "-i", "--quiet", f"--overrides={override}")
    return next(line for line in output.splitlines() if line.startswith(tuple("0123456789abcdef")))


def incremental(events_: list[dict]) -> dict:
    return next(event for event in events_ if event["msg"] == "incremental update")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first", required=True)
    parser.add_argument("--unchanged", required=True)
    parser.add_argument("--changed", required=True)
    parser.add_argument("--deleted", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--archived", default="11-academic-rules-2026.md")
    parser.add_argument("--out", type=Path,
                        default=ROOT / "eval/results/phase2_data_lifecycle.json")
    args = parser.parse_args()
    runs = {name: events(job) for name, job in {
        "first": args.first, "unchanged": args.unchanged,
        "changed": args.changed, "deleted": args.deleted,
    }.items()}
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "cluster": "minikube/rahbar",
        "jobs": {name: {"job": getattr(args, name), "events": items,
                         "incremental": incremental(items)} for name, items in runs.items()},
        "verification_report": result_file(args.report),
        "final_manifest": result_file("batch-b-index-manifest.json"),
        "archive_proof": {"file": args.archived, "sha256": archive_sha256(args.archived)},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"unchanged_embedded={payload['jobs']['unchanged']['incremental']['chunks_embedded']}")
    print(f"changed_embedded={payload['jobs']['changed']['incremental']['chunks_embedded']}")
    print(f"deleted_chunks={payload['jobs']['deleted']['incremental']['chunks_deleted']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
