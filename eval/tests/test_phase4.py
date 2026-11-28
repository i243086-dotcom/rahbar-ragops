from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inputs = load_module("phase4_inputs", ROOT / "eval" / "phase4_inputs.py")
evaluation = load_module("phase4_eval", ROOT / "eval" / "phase4_eval.py")


def passage(source: str = "rules.pdf", section: str = "5.4", page: int = 24) -> dict:
    return {"source": source, "section": section, "page": page}


def test_section_prefix_does_not_confuse_1_2_and_1_21() -> None:
    assert evaluation.section_matches("5.4", "5.4 Academic Warning")
    assert not evaluation.section_matches("1.2", "1.21 Attendance")


def test_retrieval_metrics_use_rank_and_multiple_relevant_passages() -> None:
    rows = [
        {
            "question": {"relevant": [passage(), passage("other.pdf", "2", 3)]},
            "response": {
                "retrieved": [
                    passage("miss.pdf", "x", 1),
                    passage(),
                    passage("other.pdf", "2 Details", 3),
                ]
            },
        }
    ]
    result = evaluation.retrieval_metrics(rows)
    assert result["recall_at_3"] == 1.0
    assert result["mrr"] == 0.5
    assert 0.6 < result["ndcg_at_5"] < 1.0


def test_noise_is_deterministic() -> None:
    text = "What attendance percentage is required for graduation?"
    assert evaluation.typo_query(text, 4032) == evaluation.typo_query(text, 4032)
    assert evaluation.typo_query(text, 4032) != text


def test_input_assembler_refuses_missing_human_work() -> None:
    candidates = [
        {
            "id": f"syn{i:02}",
            "category": "answerable",
            "question": "A sufficiently long synthetic question?",
            "source_type": "synthetic",
            "must_abstain": False,
            "relevant": [passage()],
        }
        for i in range(1, 18)
    ]
    rows, problems = inputs.assemble([], candidates, [])
    assert len(rows) == 17
    assert any("human questions" in problem for problem in problems)
    assert any("synthetic reviews" in problem for problem in problems)


def test_answer_metrics_check_abstention_and_citations() -> None:
    rows = [
        {
            "latency_ms": 10,
            "question": {"must_abstain": False},
            "response": {
                "answered_from_context": True,
                "retrieved": [passage()],
                "citations": [passage()],
            },
        },
        {
            "latency_ms": 20,
            "question": {"must_abstain": True},
            "response": {"answered_from_context": False, "retrieved": [], "citations": []},
        },
    ]
    result = evaluation.answer_metrics(rows)
    assert result["citation_validity"] == 1.0
    assert result["abstention_correctness"] == 1.0
    assert result["faithfulness_citation_proxy"] == 1.0

