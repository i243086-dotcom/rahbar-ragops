from __future__ import annotations

import json
from pathlib import Path

from pipeline.models import Document, Page
from pipeline.verify import verify_documents, write_report


def document(source: str, text: str, version: str = "2026") -> Document:
    return Document(source, version, False, [Page(source, 1, text)])


def metadata(source: str, **extra):
    return {"file": source, "name": source.removesuffix(".md"), "doc_version": "2026",
            "document_id": source.removesuffix(".md"), **extra}


def test_verification_reports_all_four_checks_and_quarantines_failure(tmp_path: Path) -> None:
    good_path = tmp_path / "good.md"
    bad_path = tmp_path / "bad.md"
    good_path.write_text("A complete academic policy with enough useful text for students.")
    bad_path.write_text("short")
    inputs = [
        (good_path, document("good.md", good_path.read_text()), metadata("good.md")),
        (bad_path, document("bad.md", bad_path.read_text()), metadata("bad.md", name="")),
    ]
    quarantine = tmp_path / "quarantine"
    results = verify_documents(inputs, [[1.0, 0.0], [0.0, 1.0]], quarantine)
    assert results[0].passed
    assert not results[1].passed
    assert set(results[1].checks) == {"quality", "completeness", "recency", "uniqueness"}
    assert (quarantine / "bad.md").exists()
    assert (quarantine / "bad.md.verification.json").exists()


def test_exact_near_duplicate_and_newer_version_are_detected(tmp_path: Path) -> None:
    text = "Academic policy text long enough to pass the extraction quality verification."
    paths = [tmp_path / name for name in ("old.md", "copy.md", "near.md", "new.md")]
    for path in paths:
        path.write_text(text if path.name != "near.md" else text + " Minor edit.")
    inputs = [
        (paths[0], document("old.md", text, "2025"), metadata("old.md", document_id="rules", doc_version="2025")),
        (paths[1], document("copy.md", text), metadata("copy.md")),
        (paths[2], document("near.md", text + " Minor edit."), metadata("near.md")),
        (paths[3], document("new.md", text, "2026"), metadata("new.md", document_id="rules")),
    ]
    results = verify_documents(inputs, [[1.0, 0.0], [0.0, 1.0], [0.001, 0.999], [0.0, 1.0]],
                               tmp_path / "quarantine")
    assert not results[0].checks["recency"].passed
    assert not results[1].checks["uniqueness"].passed
    assert not results[2].checks["uniqueness"].passed
    report = tmp_path / "report.json"
    write_report(results, report, "test-run")
    assert json.loads(report.read_text())["summary"]["failed"] == 4
