from __future__ import annotations

from typing import Any

from pipeline.config import get_settings
from pipeline.incremental import update_incrementally
from pipeline.models import Chunk


class Collection:
    def __init__(self) -> None:
        self.rows: dict[str, Any] = {}
        self.metadata = {}

    def delete(self, ids):
        for item in ids:
            self.rows.pop(item, None)

    def upsert(self, ids, documents, embeddings, metadatas):
        for item in zip(ids, documents, embeddings, metadatas):
            self.rows[item[0]] = item[1:]

    def modify(self, metadata):
        self.metadata = metadata

    def count(self):
        return len(self.rows)


class Client:
    def __init__(self) -> None:
        self.collection = Collection()

    def get_or_create_collection(self, name, metadata):
        return self.collection


def chunks(source: str, count: int) -> list[Chunk]:
    return [Chunk(f"{source}-{i}", f"text {i}", source, "section", 1, "2026", False)
            for i in range(count)]


def test_unchanged_run_embeds_zero_and_changed_run_is_scoped(tmp_path) -> None:
    client = Client()
    calls = []

    def embed(texts, settings):
        calls.append(list(texts))
        return [[1.0, 0.0] for _ in texts]

    manifest = tmp_path / "manifest.json"
    initial = {"a.md": chunks("a.md", 2), "b.md": chunks("b.md", 1)}
    first = update_incrementally(initial, {"a.md": "a1", "b.md": "b1"}, get_settings(),
                                 manifest, embed, client)
    second = update_incrementally(initial, {"a.md": "a1", "b.md": "b1"}, get_settings(),
                                  manifest, embed, client)
    changed = {"a.md": chunks("a.md", 3), "b.md": chunks("b.md", 1)}
    third = update_incrementally(changed, {"a.md": "a2", "b.md": "b1"}, get_settings(),
                                 manifest, embed, client)
    assert first["chunks_embedded"] == 3
    assert second["chunks_embedded"] == 0 and second["unchanged_documents"] == ["a.md", "b.md"]
    assert third["chunks_embedded"] == 3 and third["changed_documents"] == ["a.md"]
    assert len(calls[-1]) == 3


def test_deleted_document_leaves_no_orphan_ids(tmp_path) -> None:
    client = Client()

    def embed(texts, settings):
        return [[1.0] for _ in texts]

    manifest = tmp_path / "manifest.json"
    update_incrementally({"a.md": chunks("a.md", 2), "b.md": chunks("b.md", 1)},
                         {"a.md": "a", "b.md": "b"}, get_settings(), manifest, embed, client)
    result = update_incrementally({"a.md": chunks("a.md", 2)}, {"a.md": "a"},
                                  get_settings(), manifest, embed, client)
    assert result["deleted_documents"] == ["b.md"]
    assert not any(item.startswith("b.md-") for item in client.collection.rows)
