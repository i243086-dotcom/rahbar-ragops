from __future__ import annotations

import json

from app.trace import TraceRecord, TraceSink


def test_trace_sink_writes_one_json_line_per_record(tmp_path, monkeypatch):
    monkeypatch.setenv("POD_NAME", "api-test-1")
    sink = TraceSink(str(tmp_path))
    sink.write(TraceRecord(
        trace_id="trace-1", user_query="What is the CGPA rule?",
        embedding_model="nomic-embed-text", embedding_version="v1",
        collection_name="rahbar-v1",
    ))

    lines = (tmp_path / "api-test-1.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["trace_id"] == "trace-1"


def test_trace_record_retains_prompt_and_context() -> None:
    record = TraceRecord(
        trace_id="trace-2", user_query="Question", embedding_model="nomic",
        embedding_version="v1", collection_name="collection",
        context=[{"chunk_id": "c1", "text": "Evidence"}],
        prompt=[{"role": "user", "content": "Evidence"}],
    )
    assert record.payload()["context"][0]["chunk_id"] == "c1"
    assert record.payload()["prompt"][0]["role"] == "user"
