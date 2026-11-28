#!/usr/bin/env python3
"""Run the Assignment 03 Part B suite twice and write a timestamped result JSON."""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml

HERE = Path(__file__).resolve().parent
QUERY_PREFIX = "search_query: "
LABEL_VALUES = {"faithful", "unfaithful", "partial"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"{path} is empty; run eval/phase4_inputs.py after human sign-off")
    return rows


def normalise(value: object) -> str:
    return " ".join(str(value or "").casefold().split())


def section_matches(expected: object, actual: object) -> bool:
    a, b = normalise(expected), normalise(actual)
    if a == b:
        return True
    short, long_value = (a, b) if len(a) <= len(b) else (b, a)
    if not short or not long_value.startswith(short) or len(long_value) == len(short):
        return False
    next_char = long_value[len(short)]
    return not next_char.isalnum() and not (
        next_char == "." and long_value[len(short) + 1 : len(short) + 2].isdigit()
    )


def passage_matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    if normalise(expected.get("source")) != normalise(actual.get("source")):
        return False
    if not section_matches(expected.get("section"), actual.get("section")):
        return False
    expected_page, actual_page = expected.get("page"), actual.get("page")
    return expected_page is None or actual_page is None or expected_page == actual_page


def relevance(expected: list[dict[str, Any]], actual: dict[str, Any]) -> bool:
    return any(passage_matches(item, actual) for item in expected)


def retrieval_metrics(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    recall3: list[float] = []
    recall5: list[float] = []
    reciprocal_ranks: list[float] = []
    ndcg5: list[float] = []
    for row in rows:
        expected = row["question"].get("relevant") or []
        if not expected:
            continue
        retrieved = row["response"].get("retrieved") or []
        for cutoff, bucket in ((3, recall3), (5, recall5)):
            found = sum(
                1 for item in expected if any(passage_matches(item, got) for got in retrieved[:cutoff])
            )
            bucket.append(found / len(expected))
        ranks = [i + 1 for i, got in enumerate(retrieved) if relevance(expected, got)]
        reciprocal_ranks.append(1.0 / min(ranks) if ranks else 0.0)
        gains = [1.0 if relevance(expected, got) else 0.0 for got in retrieved[:5]]
        dcg = sum(gain / math.log2(rank + 2) for rank, gain in enumerate(gains))
        ideal = sum(1.0 / math.log2(rank + 2) for rank in range(min(5, len(expected))))
        ndcg5.append(dcg / ideal if ideal else 0.0)
    return {
        "recall_at_3": mean(recall3),
        "recall_at_5": mean(recall5),
        "mrr": mean(reciprocal_ranks),
        "ndcg_at_5": mean(ndcg5),
    }


def citation_is_valid(citation: dict[str, Any], retrieved: list[dict[str, Any]]) -> bool:
    return any(passage_matches(citation, item) for item in retrieved)


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 4)
    value = ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)
    return round(value, 4)


def mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 6) if values else None


def answer_metrics(rows: list[dict[str, Any]]) -> dict[str, float | int | None]:
    valid, citation_total = 0, 0
    abstention: list[float] = []
    proxy: list[float] = []
    latencies = [float(row["latency_ms"]) for row in rows]
    for row in rows:
        question, response = row["question"], row["response"]
        citations = response.get("citations") or []
        retrieved = response.get("retrieved") or []
        citation_total += len(citations)
        valid_count = sum(1 for item in citations if citation_is_valid(item, retrieved))
        valid += valid_count
        if question.get("must_abstain"):
            ok = not response.get("answered_from_context") and not citations
            abstention.append(float(ok))
            proxy.append(float(ok))
        else:
            grounded = bool(response.get("answered_from_context")) and bool(citations) and (
                valid_count == len(citations)
            )
            proxy.append(float(grounded))
    return {
        "citation_validity": round(valid / citation_total, 6) if citation_total else None,
        "citations_checked": citation_total,
        "abstention_correctness": mean(abstention),
        "faithfulness_citation_proxy": mean(proxy),
        "latency_p50_ms": percentile(latencies, 0.50),
        "latency_p95_ms": percentile(latencies, 0.95),
    }


def typo_query(text: str, seed: int) -> str:
    rng = random.Random(f"{seed}:{text}")
    words = text.split()
    choices = [index for index, word in enumerate(words) if len(word.strip("?,.")) >= 6]
    if not choices:
        return text
    index = rng.choice(choices)
    word = words[index]
    position = rng.randrange(1, max(2, len(word) - 1))
    words[index] = word[:position] + word[position + 1 :]
    return " ".join(words)


def ask(client: httpx.Client, api: str, question: str) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    response = client.post(f"{api.rstrip('/')}/api/ask", json={"question": question})
    response.raise_for_status()
    return response.json(), round((time.perf_counter() - started) * 1000, 4)


def run_questions(
    client: httpx.Client,
    api: str,
    questions: list[dict[str, Any]],
    *,
    seed: int,
    noisy: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for question in questions:
        text = typo_query(str(question["question"]), seed) if noisy else str(question["question"])
        response, latency_ms = ask(client, api, text)
        rows.append(
            {
                "id": question["id"],
                "query": text,
                "question": question,
                "response": response,
                "latency_ms": latency_ms,
            }
        )
        print(f"  {question['id']:<8} {latency_ms:>9.1f} ms  {text[:66]}")
    return rows


def cosine(a: list[float], b: list[float]) -> float:
    numerator = sum(x * y for x, y in zip(a, b, strict=True))
    denominator = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return numerator / denominator if denominator else 0.0


def embed(client: httpx.Client, ollama: str, model: str, texts: list[str]) -> tuple[list[list[float]], float]:
    started = time.perf_counter()
    response = client.post(
        f"{ollama.rstrip('/')}/api/embed",
        json={"model": model, "input": [QUERY_PREFIX + text for text in texts]},
    )
    response.raise_for_status()
    vectors = [[float(value) for value in vector] for vector in response.json()["embeddings"]]
    elapsed_ms = (time.perf_counter() - started) * 1000
    return vectors, elapsed_ms


def embedding_metrics(client: httpx.Client, ollama: str, model: str, pairs_path: Path) -> dict[str, Any]:
    pairs = (yaml.safe_load(pairs_path.read_text(encoding="utf-8")) or {}).get("pairs", [])
    if len(pairs) < 15:
        raise ValueError("embedding evaluation requires at least 15 paraphrase/unrelated pairs")
    texts = [str(value) for pair in pairs for value in (pair["a"], pair["b"], pair["unrelated"])]
    vectors, elapsed_ms = embed(client, ollama, model, texts)
    paraphrase, unrelated = [], []
    for index in range(len(pairs)):
        first, second, other = vectors[index * 3 : index * 3 + 3]
        paraphrase.append(cosine(first, second))
        unrelated.append(cosine(first, other))
    deterministic, _ = embed(client, ollama, model, [texts[0], texts[0]])
    largest_difference = max(abs(a - b) for a, b in zip(*deterministic, strict=True))
    para_mean, unrelated_mean = mean(paraphrase), mean(unrelated)
    assert para_mean is not None and unrelated_mean is not None
    return {
        "model": model,
        "pairs": len(pairs),
        "mean_paraphrase_cosine": para_mean,
        "mean_unrelated_cosine": unrelated_mean,
        "cosine_gap": round(para_mean - unrelated_mean, 6),
        "embedding_ms_per_text": round(elapsed_ms / len(texts), 6),
        "determinism_largest_absolute_difference": round(largest_difference, 12),
    }


def metric_delta(first: dict[str, Any], second: dict[str, Any]) -> dict[str, float]:
    deltas: dict[str, float] = {}
    for key in sorted(first.keys() & second.keys()):
        if isinstance(first[key], (int, float)) and isinstance(second[key], (int, float)):
            deltas[key] = round(float(second[key]) - float(first[key]), 6)
    return deltas


def load_traces(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    files = [path] if path.is_file() else sorted(path.glob("*.jsonl"))
    traces: dict[str, dict[str, Any]] = {}
    for file_path in files:
        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            trace_id = str(row.get("trace_id", ""))
            if trace_id:
                traces[trace_id] = row
    return traces


def write_label_packet(rows: list[dict[str, Any]], traces: dict[str, dict[str, Any]], path: Path) -> None:
    lines = [
        "# Answer-faithfulness labels",
        "",
        "For each selected item, judge whether the answer is fully supported by the shown retrieved",
        "context. Record the decision in `answer_labels.yaml`; do not edit this generated packet.",
        "",
    ]
    for row in rows:
        response = row["response"]
        trace = traces.get(str(response.get("request_id", "")), {})
        lines.extend(
            [
                f"## {row['id']}",
                "",
                f"**Question:** {row['query']}",
                "",
                f"**Answer:** {response.get('answer', '')}",
                "",
                f"**Citations:** `{json.dumps(response.get('citations') or [], ensure_ascii=False)}`",
                "",
                "**Retrieved context:**",
                "",
                "```text",
                str(trace.get("context") or json.dumps(response.get("retrieved") or [], indent=2)),
                "```",
                "",
                "**Human label:** faithful / partial / unfaithful (enter in YAML)",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def human_label_metrics(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    labels = data.get("labels") or []
    by_id = {str(row["id"]): row for row in rows}
    problems: list[str] = []
    scored: list[float] = []
    agreement: list[float] = []
    seen: set[str] = set()
    for label in labels:
        if not label.get("label"):
            continue
        qid = str(label.get("id", ""))
        value = label.get("label")
        if qid not in by_id or qid in seen:
            problems.append(f"invalid or duplicate label id: {qid}")
            continue
        seen.add(qid)
        if value not in LABEL_VALUES or not label.get("reviewer") or not label.get("reviewed_on"):
            problems.append(f"{qid}: label, reviewer, and reviewed_on are required")
            continue
        score = {"faithful": 1.0, "partial": 0.5, "unfaithful": 0.0}[value]
        scored.append(score)
        proxy_faithful = answer_metrics([by_id[qid]])["faithfulness_citation_proxy"] == 1.0
        agreement.append(float(proxy_faithful == (value == "faithful")))
    if len(seen) < 8:
        problems.append(f"{len(seen)} human labels supplied; at least 8 are required")
    if problems:
        raise ValueError("; ".join(problems))
    return {
        "labels": len(seen),
        "human_faithfulness": mean(scored),
        "citation_proxy_human_agreement": mean(agreement),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, help="RAHBAR API base URL")
    parser.add_argument("--host", help="optional Host header for Ingress")
    parser.add_argument("--ollama", required=True, help="Ollama base URL reachable from this process")
    parser.add_argument("--embed-model", default="nomic-embed-text")
    parser.add_argument("--golden", type=Path, default=HERE / "golden.jsonl")
    parser.add_argument("--pairs", type=Path, default=HERE / "paraphrase_pairs.yaml")
    parser.add_argument("--labels", type=Path, default=HERE / "human_inputs" / "answer_labels.yaml")
    parser.add_argument("--traces", type=Path, help="trace JSONL file or directory for label context")
    parser.add_argument("--results-dir", type=Path, default=HERE / "results")
    parser.add_argument("--seed", type=int, default=4032)
    parser.add_argument("--timeout", type=float, default=900.0)
    args = parser.parse_args()

    questions = load_jsonl(args.golden)
    counts = Counter(str(row.get("category")) for row in questions)
    if len(questions) < 25 or any(counts[key] < value for key, value in {"answerable": 15, "abstain": 5, "hard": 5}.items()):
        raise ValueError(f"golden distribution is incomplete: {len(questions)} questions, {dict(counts)}")
    headers = {"Host": args.host} if args.host else {}
    runs: list[dict[str, Any]] = []
    all_rows: list[list[dict[str, Any]]] = []
    with httpx.Client(timeout=args.timeout, headers=headers) as client:
        for run_number in (1, 2):
            print(f"\nRUN {run_number}/2: embeddings")
            embedding = embedding_metrics(client, args.ollama, args.embed_model, args.pairs)
            print(f"RUN {run_number}/2: clean golden questions")
            clean = run_questions(client, args.api, questions, seed=args.seed, noisy=False)
            print(f"RUN {run_number}/2: deterministic typo-noise questions")
            noisy = run_questions(client, args.api, questions, seed=args.seed, noisy=True)
            clean_retrieval, noisy_retrieval = retrieval_metrics(clean), retrieval_metrics(noisy)
            runs.append(
                {
                    "run": run_number,
                    "seed": args.seed,
                    "embedding": embedding,
                    "retrieval": clean_retrieval,
                    "retrieval_noise": noisy_retrieval,
                    "retrieval_noise_delta": metric_delta(clean_retrieval, noisy_retrieval),
                    "answers": answer_metrics(clean),
                }
            )
            all_rows.append(clean)

    traces = load_traces(args.traces)
    packet = HERE / "human_inputs" / "LABEL_ANSWERS.md"
    write_label_packet(all_rows[0], traces, packet)
    result: dict[str, Any] = {
        "schema_version": 1,
        "phase": 4,
        "generated_at": datetime.now(UTC).isoformat(),
        "run_context": {
            "api": args.api,
            "embed_model": args.embed_model,
            "temperature_requirement": 0,
            "fixed_seed": args.seed,
            "questions": len(questions),
            "distribution": dict(counts),
            "noise": "one deterministic character deletion in a word of length >= 6",
        },
        "runs": runs,
        "stochasticity_delta_run2_minus_run1": {
            "embedding": metric_delta(runs[0]["embedding"], runs[1]["embedding"]),
            "retrieval": metric_delta(runs[0]["retrieval"], runs[1]["retrieval"]),
            "retrieval_noise": metric_delta(runs[0]["retrieval_noise"], runs[1]["retrieval_noise"]),
            "answers": metric_delta(runs[0]["answers"], runs[1]["answers"]),
        },
        "human_faithfulness": None,
        "limitations": [
            "Faithfulness is provisional until at least eight real human labels are supplied.",
            "The automatic faithfulness value is explicitly a citation-grounding proxy, not an LLM judge.",
        ],
    }
    label_data = (yaml.safe_load(args.labels.read_text(encoding="utf-8")) or {}).get("labels") or []
    completed_labels = [row for row in label_data if row.get("label")]
    if completed_labels:
        result["human_faithfulness"] = human_label_metrics(args.labels, all_rows[0])
        result["limitations"] = [result["limitations"][1]]
    args.results_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = args.results_dir / f"phase4_offline_evaluation_{stamp}.json"
    result["result_file"] = output.name
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote {output}")
    print(f"Refreshed human label packet: {packet}")
    return 0 if result["human_faithfulness"] is not None else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, httpx.HTTPError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

