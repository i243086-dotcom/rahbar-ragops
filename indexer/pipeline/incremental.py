"""A2 document-scoped Chroma updates backed by a persistent manifest."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from .config import IndexerSettings
from .models import Chunk
from .store import BATCH, get_client


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"documents": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def update_incrementally(
    chunks_by_document: dict[str, list[Chunk]], hashes: dict[str, str],
    settings: IndexerSettings, manifest_path: Path,
    embedder: Callable[[list[str], IndexerSettings], list[list[float]]],
    client: Any | None = None,
) -> dict[str, Any]:
    previous = load_manifest(manifest_path)
    old_documents = previous.get("documents", {})
    current_sources = set(chunks_by_document)
    old_sources = set(old_documents)
    changed = sorted(source for source in current_sources
                     if old_documents.get(source, {}).get("content_hash") != hashes[source])
    unchanged = sorted(current_sources - set(changed))
    deleted = sorted(old_sources - current_sources)
    changed_chunks = [chunk for source in changed for chunk in chunks_by_document[source]]
    vectors = embedder([chunk.text for chunk in changed_chunks], settings)
    if len(vectors) != len(changed_chunks):
        raise RuntimeError("embedding count mismatch during incremental update")

    db = client or get_client(settings)
    dimension = len(vectors[0]) if vectors else int(previous.get("dimension", 0))
    metadata = {
        "hnsw:space": "cosine", "embed_model": settings.embed_model,
        "dimension": dimension, "index_id": uuid.uuid4().hex[:12],
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "chunk_size": settings.chunk_size, "chunk_overlap": settings.chunk_overlap,
        "chunk_count": sum(len(items) for items in chunks_by_document.values()),
    }
    # Chroma can answer its HTTP health endpoint before the collection
    # endpoint is ready during a fresh StatefulSet start. Retry transient
    # 404/connection failures so the ingestion Job does not lose its only
    # attempt to a startup race.
    last_error: Exception | None = None
    for attempt in range(6):
        try:
            collection = db.get_or_create_collection(settings.collection, metadata=metadata)
            break
        except Exception as exc:  # chromadb-client exposes several HTTP error types
            last_error = exc
            if attempt == 5:
                raise
            time.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"could not create Chroma collection: {last_error!r}")
    for source in changed + deleted:
        old_ids = old_documents.get(source, {}).get("chunk_ids", [])
        if old_ids:
            collection.delete(ids=old_ids)
    offset = 0
    for start in range(0, len(changed_chunks), BATCH):
        part = changed_chunks[start:start + BATCH]
        part_vectors = vectors[offset:offset + len(part)]
        collection.upsert(
            ids=[chunk.id for chunk in part], documents=[chunk.text for chunk in part],
            embeddings=part_vectors, metadatas=[chunk.metadata() for chunk in part],
        )
        offset += len(part)
    # Chroma accepts hnsw:space only at collection creation; sending it to modify is
    # interpreted as an attempted distance-function change even when the value is identical.
    collection.modify(metadata={key: value for key, value in metadata.items()
                                if key != "hnsw:space"})

    documents = {
        source: {"content_hash": hashes[source],
                 "chunk_ids": [chunk.id for chunk in chunks_by_document[source]],
                 "chunk_count": len(chunks_by_document[source])}
        for source in sorted(current_sources)
    }
    manifest = {"collection": settings.collection, "embed_model": settings.embed_model,
                "dimension": dimension, "documents": documents}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "changed_documents": changed, "unchanged_documents": unchanged,
        "deleted_documents": deleted, "chunks_embedded": len(changed_chunks),
        "chunks_deleted": sum(len(old_documents[source].get("chunk_ids", []))
                              for source in changed + deleted if source in old_documents),
        "collection_count": int(collection.count()),
    }
