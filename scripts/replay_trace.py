#!/usr/bin/env python3
"""Print the exact stored context and prompt for a trace ID; no model call occurs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def read_lines(trace_id: str, path: Path | None) -> list[str]:
    if path is not None:
        return path.read_text(encoding="utf-8").splitlines()
    command = ["kubectl", "-n", "rahbar", "exec", "deployment/api", "--", "sh", "-c",
               f"grep -h {trace_id} /traces/*.jsonl"]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout.splitlines()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace_id")
    parser.add_argument("--file", type=Path, help="local JSONL file; omit to read the trace PVC")
    args = parser.parse_args()
    record = next((json.loads(line) for line in read_lines(args.trace_id, args.file)
                   if json.loads(line).get("trace_id") == args.trace_id), None)
    if record is None:
        raise SystemExit(f"trace not found: {args.trace_id}")
    prompt = record.get("prompt", [])
    actual_hash = hashlib.sha256(json.dumps(prompt, sort_keys=True).encode()).hexdigest()
    print(json.dumps({
        "trace_id": args.trace_id,
        "context": record.get("context", []),
        "prompt": prompt,
        "prompt_hash": record.get("prompt_hash"),
        "reconstructed_prompt_hash": actual_hash,
        "hash_matches": actual_hash == record.get("prompt_hash"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
