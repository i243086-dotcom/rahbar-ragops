"""Central query-trace model and append-only JSONL sink.

The trace volume is optional for local development. On Kubernetes every API pod
writes to its own file, while the same record is also emitted to stdout.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("rahbar.trace")


@dataclass
class TraceRecord:
    trace_id: str
    user_query: str
    embedding_model: str
    embedding_version: str
    collection_name: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rewritten_query: str | None = None
    retrieved: list[dict[str, Any]] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    reranked_order: list[str] = field(default_factory=list)
    prompt_hash: str | None = None
    prompt: list[dict[str, str]] = field(default_factory=list)
    context: list[dict[str, Any]] = field(default_factory=list)
    model: str = ""
    model_parameters: dict[str, Any] = field(default_factory=dict)
    response: str = ""
    citations: list[dict[str, Any]] = field(default_factory=list)
    guardrail_actions: list[str] = field(default_factory=list)
    latency_ms: dict[str, float] = field(default_factory=dict)
    cache: str = "skipped"
    outcome: str = "started"

    def payload(self) -> dict[str, Any]:
        return asdict(self)


class TraceSink:
    """Write complete trace records to stdout and, when configured, one JSONL file per pod."""

    def __init__(self, trace_dir: str = "") -> None:
        self._lock = threading.Lock()
        self.path: Path | None = None
        if trace_dir:
            pod = os.environ.get("POD_NAME") or os.environ.get("HOSTNAME", "local")
            self.path = Path(trace_dir) / f"{pod}.jsonl"
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, trace: TraceRecord) -> None:
        payload = trace.payload()
        log.info("query_trace", extra={"trace": payload})
        if self.path is not None:
            line = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
            with self._lock, self.path.open("a", encoding="utf-8") as stream:
                stream.write(line)
