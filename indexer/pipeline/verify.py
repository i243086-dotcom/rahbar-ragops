"""A1 verification between extraction and chunking.

Every check returns an explicit pass/fail and reasons. Failed documents are
copied to quarantine and never reach chunking or the vector store.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .models import Document

NEAR_DUPLICATE_THRESHOLD = 0.985


@dataclass(frozen=True)
class Check:
    passed: bool
    reasons: list[str]


@dataclass
class Verification:
    source: str
    document_id: str
    content_hash: str
    checks: dict[str, Check]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks.values())

    def payload(self) -> dict[str, Any]:
        return {**asdict(self), "passed": self.passed}


def normalized_text(document: Document) -> str:
    return "\n".join(page.text.strip() for page in document.pages).strip()


def content_hash(document: Document) -> str:
    normalized = " ".join(normalized_text(document).lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def cosine(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    denom = math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right))
    return dot / denom if denom else 0.0


def _quality(document: Document) -> Check:
    text = normalized_text(document)
    reasons = []
    if len(text) < 40:
        reasons.append("empty_or_too_short")
    if text and text.count("\ufffd") / len(text) > 0.01:
        reasons.append("garbled_replacement_characters")
    printable = sum(char.isprintable() or char.isspace() for char in text)
    if text and printable / len(text) < 0.95:
        reasons.append("garbled_non_printable_ratio")
    return Check(not reasons, reasons or ["usable_extraction"])


def _completeness(document: Document, metadata: dict[str, Any]) -> Check:
    reasons = []
    required = {
        "source": metadata.get("file") or document.source,
        "title": metadata.get("name") or metadata.get("title"),
        "date_or_version": metadata.get("date") or metadata.get("doc_version"),
        "page_count": len(document.pages),
    }
    for field, value in required.items():
        if value in (None, "", 0):
            reasons.append(f"missing_{field}")
    expected_pages = metadata.get("page_count")
    if expected_pages is not None and int(expected_pages) != len(document.pages):
        reasons.append(f"page_count_mismatch_expected_{expected_pages}_actual_{len(document.pages)}")
    if metadata.get("truncated") is True:
        reasons.append("metadata_marks_truncated")
    return Check(not reasons, reasons or ["required_metadata_and_page_count_present"])


def verify_documents(
    documents: list[tuple[Path, Document, dict[str, Any]]], vectors: list[list[float]],
    quarantine_dir: Path, archive_dir: Path | None = None,
) -> list[Verification]:
    if len(documents) != len(vectors):
        raise ValueError("one verification embedding is required per document")
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    if archive_dir is not None:
        archive_dir.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    accepted_vectors: list[tuple[str, list[float]]] = []
    newest: dict[str, str] = {}
    for _, document, metadata in documents:
        key = str(metadata.get("document_id") or metadata.get("family") or document.source)
        newest[key] = max(newest.get(key, ""), document.doc_version)

    results: list[Verification] = []
    for index, (path, document, metadata) in enumerate(documents):
        digest = content_hash(document)
        doc_id = str(metadata.get("document_id") or metadata.get("family") or path.stem)
        exact_reasons = [f"exact_duplicate_of:{hashes[digest]}"] if digest in hashes else []
        near = [other for other, vector in accepted_vectors
                if cosine(vectors[index], vector) >= NEAR_DUPLICATE_THRESHOLD]
        unique_reasons = exact_reasons or ([f"near_duplicate_of:{near[0]}"] if near else [])
        recency_reasons = []
        if document.doc_version < newest.get(doc_id, document.doc_version):
            recency_reasons.append(f"newer_version_detected:{newest[doc_id]}")
        checks = {
            "quality": _quality(document),
            "completeness": _completeness(document, metadata),
            "recency": Check(not recency_reasons, recency_reasons or ["latest_version"]),
            "uniqueness": Check(not unique_reasons, unique_reasons or ["unique"]),
        }
        result = Verification(path.name, doc_id, digest, checks)
        results.append(result)
        hashes.setdefault(digest, path.name)
        accepted_vectors.append((path.name, vectors[index]))
        if not result.passed:
            only_recency = (not checks["recency"].passed and
                            all(checks[name].passed for name in ("quality", "completeness", "uniqueness")))
            destination = archive_dir if only_recency and archive_dir is not None else quarantine_dir
            target = destination / path.name
            if path.exists() and path.resolve() != target.resolve():
                shutil.copy2(path, target)
            (destination / f"{path.name}.verification.json").write_text(
                json.dumps(result.payload(), indent=2) + "\n", encoding="utf-8")
    return results


def write_report(results: list[Verification], path: Path, run_id: str) -> None:
    payload = {
        "run_id": run_id,
        "documents": [result.payload() for result in results],
        "summary": {
            "total": len(results),
            "passed": sum(result.passed for result in results),
            "failed": sum(not result.passed for result in results),
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
