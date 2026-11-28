#!/usr/bin/env python3
"""Validate human sign-offs and assemble the immutable Phase 4 golden JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
HUMAN_DIR = HERE / "human_inputs"
VALID_CATEGORIES = {"answerable", "abstain", "hard"}
VALID_VERDICTS = {"accept", "edit", "reject"}
REQUIRED_COUNTS = {"answerable": 15, "abstain": 5, "hard": 5}


def load_yaml(path: Path, key: str) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = data.get(key, [])
    if not isinstance(rows, list):
        raise ValueError(f"{path}: {key!r} must be a list")
    return rows


def valid_iso_date(value: object) -> bool:
    try:
        date.fromisoformat(str(value))
    except ValueError:
        return False
    return True


def validate_question(q: dict[str, Any], *, human: bool) -> list[str]:
    qid = str(q.get("id", "?"))
    problems: list[str] = []
    if len(str(q.get("question", "")).strip()) < 10:
        problems.append(f"{qid}: question must contain genuine wording")
    category = q.get("category")
    if category not in VALID_CATEGORIES:
        problems.append(f"{qid}: category must be one of {sorted(VALID_CATEGORIES)}")
    if q.get("source_type") != ("human" if human else "synthetic"):
        problems.append(f"{qid}: source_type does not match its input file")
    must_abstain = bool(q.get("must_abstain"))
    relevant = q.get("relevant") or []
    if category == "abstain" and (not must_abstain or relevant):
        problems.append(f"{qid}: abstain entries require must_abstain=true and relevant=[]")
    if category != "abstain" and (must_abstain or not relevant):
        problems.append(f"{qid}: answerable/hard entries require ground-truth passages")
    for passage in relevant:
        if not passage.get("source"):
            problems.append(f"{qid}: each relevant passage requires source")
        if passage.get("page") is not None and not isinstance(passage.get("page"), int):
            problems.append(f"{qid}: passage page must be an integer or null for section-only sources")
        if not str(passage.get("section", "")).strip():
            problems.append(f"{qid}: each relevant passage requires section")
    if human:
        if not str(q.get("author", "")).strip():
            problems.append(f"{qid}: author must be entered by the human author")
        if not valid_iso_date(q.get("written_on")):
            problems.append(f"{qid}: written_on must be a real ISO date")
    return problems


def apply_reviews(
    candidates: list[dict[str, Any]], reviews: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    by_id = {str(row.get("id")): dict(row) for row in candidates}
    problems: list[str] = []
    seen: set[str] = set()
    for review in reviews:
        qid = str(review.get("id", ""))
        if qid not in by_id:
            problems.append(f"review {qid!r}: unknown synthetic id")
            continue
        if qid in seen:
            problems.append(f"review {qid!r}: duplicate review")
        seen.add(qid)
        verdict = review.get("verdict")
        if verdict not in VALID_VERDICTS:
            problems.append(f"review {qid}: verdict must be accept, edit, or reject")
        if not str(review.get("reviewer", "")).strip():
            problems.append(f"review {qid}: reviewer is required")
        if not valid_iso_date(review.get("reviewed_on")):
            problems.append(f"review {qid}: reviewed_on must be a real ISO date")
        if verdict == "edit":
            edited = str(review.get("edited_question", "")).strip()
            if len(edited) < 10:
                problems.append(f"review {qid}: edit requires edited_question")
            else:
                by_id[qid]["question"] = edited
        if verdict == "reject":
            by_id.pop(qid, None)
    if len(seen) < 8:
        problems.append(f"synthetic reviews: {len(seen)} completed; at least 8 are required")
    return list(by_id.values()), problems


def assemble(
    human_questions: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    problems: list[str] = []
    for question in human_questions:
        problems.extend(validate_question(question, human=True))
    for question in candidates:
        problems.extend(validate_question(question, human=False))
    reviewed, review_problems = apply_reviews(candidates, reviews)
    problems.extend(review_problems)
    if len(human_questions) < 8:
        problems.append(f"human questions: {len(human_questions)} completed; at least 8 are required")
    rows = reviewed + human_questions
    ids = [str(row.get("id")) for row in rows]
    if len(ids) != len(set(ids)):
        problems.append("question ids must be unique across human and synthetic inputs")
    counts = Counter(str(row.get("category")) for row in rows)
    for category, required in REQUIRED_COUNTS.items():
        if counts[category] < required:
            problems.append(f"{category}: {counts[category]} questions; need at least {required}")
    if len(rows) < 25:
        problems.append(f"golden set: {len(rows)} questions; need at least 25")
    return sorted(rows, key=lambda row: str(row["id"])), problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--human", type=Path, default=HUMAN_DIR / "human_questions.yaml")
    parser.add_argument("--synthetic", type=Path, default=HUMAN_DIR / "synthetic_candidates.yaml")
    parser.add_argument("--reviews", type=Path, default=HUMAN_DIR / "synthetic_reviews.yaml")
    parser.add_argument("--out", type=Path, default=HERE / "golden.jsonl")
    parser.add_argument("--check", action="store_true", help="validate without writing output")
    args = parser.parse_args()
    rows, problems = assemble(
        load_yaml(args.human, "questions"),
        load_yaml(args.synthetic, "questions"),
        load_yaml(args.reviews, "reviews"),
    )
    counts = Counter(str(row.get("category")) for row in rows)
    print(f"Phase 4 inputs: {len(rows)} questions; {dict(counts)}")
    if problems:
        for problem in problems:
            print(f"  WAITING  {problem}")
        print("Human checkpoint incomplete; golden.jsonl was not written.")
        return 2
    if not args.check:
        args.out.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        print(f"Wrote validated golden set: {args.out}")
    else:
        print("Phase 4 human inputs are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

