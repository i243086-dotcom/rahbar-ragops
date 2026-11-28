#!/usr/bin/env python3
"""Print the compact three-level Phase 4 table used by screenshot B1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def value(row: dict[str, Any], key: str) -> str:
    item = row.get(key)
    return "PENDING" if item is None else str(item)


def latest_result(directory: Path) -> Path:
    files = sorted(directory.glob("phase4_offline_evaluation_*.json"))
    if not files:
        raise FileNotFoundError(f"no Phase 4 result in {directory}")
    return files[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", nargs="?", type=Path)
    parser.add_argument("--results-dir", type=Path, default=Path("eval/results"))
    args = parser.parse_args()
    try:
        path = args.result or latest_result(args.results_dir)
    except FileNotFoundError as exc:
        print(f"INCOMPLETE: {exc}", file=sys.stderr)
        return 2
    result = json.loads(path.read_text(encoding="utf-8"))
    run = result["runs"][0]
    embedding, retrieval, noise, answers = (
        run["embedding"], run["retrieval"], run["retrieval_noise"], run["answers"]
    )
    print("PART B - THREE-LEVEL OFFLINE EVALUATION")
    print(f"result={path}")
    print(f"questions={result['run_context']['questions']} distribution={result['run_context']['distribution']}")
    print("LEVEL       METRIC                              VALUE")
    print(f"module      paraphrase cosine                   {value(embedding, 'mean_paraphrase_cosine')}")
    print(f"module      unrelated cosine                    {value(embedding, 'mean_unrelated_cosine')}")
    print(f"module      cosine gap                          {value(embedding, 'cosine_gap')}")
    print(f"module      embedding ms/text                   {value(embedding, 'embedding_ms_per_text')}")
    print(f"module      largest deterministic difference    {value(embedding, 'determinism_largest_absolute_difference')}")
    print(f"component   recall@3                            {value(retrieval, 'recall_at_3')}")
    print(f"component   recall@5                            {value(retrieval, 'recall_at_5')}")
    print(f"component   MRR                                 {value(retrieval, 'mrr')}")
    print(f"component   nDCG@5                              {value(retrieval, 'ndcg_at_5')}")
    print(f"noise       recall@5                            {value(noise, 'recall_at_5')}")
    print(f"noise       MRR                                 {value(noise, 'mrr')}")
    print(f"end-to-end  citation validity                   {value(answers, 'citation_validity')}")
    print(f"end-to-end  abstention correctness              {value(answers, 'abstention_correctness')}")
    print(f"end-to-end  latency p50 ms                      {value(answers, 'latency_p50_ms')}")
    print(f"end-to-end  latency p95 ms                      {value(answers, 'latency_p95_ms')}")
    human = result.get("human_faithfulness") or {}
    print(f"end-to-end  human faithfulness                  {value(human, 'human_faithfulness')}")
    print(f"agreement   citation proxy vs human             {value(human, 'citation_proxy_human_agreement')}")
    print(f"variation   run2-run1                           {result['stochasticity_delta_run2_minus_run1']}")
    if not human:
        print("INCOMPLETE: at least eight real answer labels are still required", file=sys.stderr)
        return 2
    print("PHASE 4 COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())

