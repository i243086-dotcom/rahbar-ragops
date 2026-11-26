#!/usr/bin/env python3
"""Capture Phase 1 platform evidence directly from the live Kubernetes API."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "rahbar"


def kubectl_json(*args: str) -> dict:
    completed = subprocess.run(
        ["kubectl", "-n", NAMESPACE, *args, "-o", "json"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(completed.stdout)


def kubectl(*args: str) -> str:
    completed = subprocess.run(
        ["kubectl", "-n", NAMESPACE, *args],
        check=True, capture_output=True, text=True,
    )
    return completed.stdout.strip()


def env_map(deployment: dict) -> dict[str, str]:
    env = deployment["spec"]["template"]["spec"]["containers"][0]["env"]
    return {item["name"]: item["value"] for item in env if "value" in item}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "eval/results/phase1_platform.json")
    args = parser.parse_args()

    deployment = kubectl_json("get", "deployment", "api")
    statefulset = kubectl_json("get", "statefulset", "chroma")
    claims = kubectl_json("get", "pvc")["items"]
    cronjob = kubectl_json("get", "cronjob", "reindex")
    trace_line = kubectl(
        "exec", "deployment/api", "--", "sh", "-c",
        f"grep -h {args.trace_id} /traces/*.jsonl",
    ).splitlines()[-1]
    marker_output = kubectl(
        "run", "phase1-capture-reader", "--image=busybox:1.36", "--restart=Never",
        "--rm", "-i", "--quiet",
        "--overrides={\"spec\":{\"containers\":[{\"name\":\"phase1-capture-reader\","
        "\"image\":\"busybox:1.36\",\"command\":[\"cat\","
        "\"/archive/phase1-marker.txt\"],\"volumeMounts\":[{\"name\":\"archive\","
        "\"mountPath\":\"/archive\"}]}],\"volumes\":[{\"name\":\"archive\","
        "\"persistentVolumeClaim\":{\"claimName\":\"archive\"}}]}}",
    )
    marker = marker_output.splitlines()[0]

    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "cluster": "minikube/rahbar",
        "api": {
            "kind": deployment["kind"],
            "ready_replicas": deployment["status"].get("readyReplicas", 0),
            "identity_env": env_map(deployment),
        },
        "vector_store": {
            "kind": statefulset["kind"],
            "ready_replicas": statefulset["status"].get("readyReplicas", 0),
            "claim_templates": [item["metadata"]["name"]
                                for item in statefulset["spec"]["volumeClaimTemplates"]],
        },
        "persistent_claims": {
            item["metadata"]["name"]: item["status"]["phase"] for item in claims
        },
        "cronjob": {
            "schedule": cronjob["spec"]["schedule"],
            "concurrency_policy": cronjob["spec"]["concurrencyPolicy"],
        },
        "persistence_proof": {"archive_marker_after_replacement_pod": marker},
        "trace_proof": json.loads(trace_line),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"api_ready={payload['api']['ready_replicas']}")
    print(f"pvc_bound={sum(value == 'Bound' for value in payload['persistent_claims'].values())}")
    print(f"trace_id={args.trace_id}")
    print(f"persistence_marker={marker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
