# Assignment 02 baseline audit

Audited from commit `aa1bd0c` of the read-only source repository on 2026-11-26.

## Actual architecture and contracts

| Area | A02 implementation | A03 consequence |
| --- | --- | --- |
| API | FastAPI in `api/app`; `POST /api/ask`, `/healthz`, `/readyz`, `/metrics` | Reuse; extend answer path with full trace object |
| Models | Generation `llama3.2:3b`; embeddings `nomic-embed-text`; host Ollama at `host.minikube.internal:11434` | Pin both model and version; eval temperature/seed must become deterministic |
| Vector store | Chroma `chromadb/chroma:1.0.12`, StatefulSet/PVC, collection `rahbar` | Reuse persistence; replace full rebuild with manifest-driven incremental operations |
| Collection pin | Collection metadata stores `embed_model`, dimension, `index_id`; readiness rejects mismatch | Preserve and add embedding version/collection version |
| Chunk metadata | `source`, `section`, `page`, `doc_version`, `superseded` | Add `doc_id`, `status`, `title`, `content_hash`, `embed_model`, `embed_version`, `collection` |
| Indexing | Separate Python indexer; Kubernetes Job and weekly CronJob; full temporary-collection rebuild and swap | Sole-writer design is good; add verify/quarantine/archive/restore and zero-embedding unchanged runs |
| Retrieval | Cosine retrieval plus exact-term boost; default metadata filter excludes `superseded=true`; older-version intent can include it | Reuse filter behavior, migrate to `status=active`, trace filters and reranking order |
| Cache | Redis semantic cache with threshold, TTL, safe-cache policy and invalidation on reindex | Reuse; disable/bypass for evaluation and trace hit/miss |
| Logs | Structured JSON to stdout with request id and selected retrieval fields | Insufficient for D1; add JSONL trace to stdout and PVC, one file per pod |
| Guardrails | Query/document injection pattern checks, prompt delimiters, retrieved-evidence neutralization, citation reconciliation | Reuse, but write each action into the trace and test the planted Batch B injection |
| Evaluation | YAML golden set; recall@3/@5, citation validity, abstention and injection checks; hard-coded gate in `run_eval.py` | Partial foundation only; A03 requires JSONL provenance, all three levels, stochasticity, noise test, external gate config and results history |
| Kubernetes | API/UI Deployments, Chroma StatefulSet, Redis Deployment, PVCs, indexer Job/CronJob, Services, Ingress, ConfigMap, NetworkPolicies, HPA | Strong baseline; add A03 volumes, eval Job, candidate Deployment/Service, literal release identity in pod template, gate ConfigMap |
| Resources | Requests/limits exist, with A02 evidence notes | Re-measure during A03 ingest/eval and cite committed raw output |

## A03 gap table

| Item | State | Evidence in A02 | Missing work |
| --- | --- | --- | --- |
| A1 verification | Missing | Extraction errors are merely logged/skipped | Four checks per document with reasons, quarantine, run reports |
| A2 incremental update | Missing | `store.py` rebuilds/swaps the entire collection | Manifest, zero embeds unchanged, document-scoped replace/delete, orphan proof, archive/restore |
| Batch B | Missing | Fixture corpus only | Reproducible >=10-document planted batch and `PLANTED.md` |
| B golden set | Partial | `eval/golden.yaml` has A02 questions/types | `golden.jsonl`, >=25 composition/provenance, human creation/review protocol |
| B module tests | Missing | Embedder unit tests only | Similarity groups, timing, determinism from real model |
| B component tests | Partial | recall@3/@5 | MRR, nDCG@5, noise delta |
| B end-to-end | Partial | citation validity and abstention | Faithfulness, latency percentiles, human judge agreement |
| B stochasticity | Missing | None | Two fixed-seed full runs and metric deltas |
| C1 change | Partial | A02 chunk experiment exists | One A03 baseline/candidate experiment across all three levels and isolated collections |
| C2 release gate | Partial | Gate constants live in `eval/run_eval.py` | YAML thresholds, standalone exit-code gate, measured fail/pass cases, ConfigMap mount |
| C3 rollout | Partial | RollingUpdate already uses `maxUnavailable: 0`; A02 rollback evidence exists | Candidate Deployment/Service, gate-controlled promotion, bad release/undo with post-undo trace identity |
| D1 trace | Missing | JSON application logs contain request id, chunks/scores, cache and limited guard data | Complete per-query schema/record including prompt and stage latencies, stdout plus PVC |
| D2 trace tool | Missing | None | Trace-id lookup and exact prompt/context rebuild |
| D3 trace metrics | Partial | Prometheus exposes latency/cache/abstention/injection counters | Windowed trace report and similarity distribution/p95 per stage |
| D4 guardrail logging | Partial | Guardrails and counters exist | Explicit guardrail actions in trace plus Batch B test |
| D5 trace root cause | Missing | A02 failure analysis is not A03 trace-only evidence | Select real failure and write five-line analysis from one trace |
| E1 live log | Missing | None | >=40 reviewed usage-like queries |
| E2 coverage | Missing | None | Calibrated embedding coverage, uncovered topics and failing exit status |
| E3 data drift | Missing | None | Ingest Batch B and compare three-level results |
| E4 close gap | Missing | None | >=6 honest new golden questions and measured improvement |
| F1 deploy/persistence | Partial | API Deployment, Chroma StatefulSet/PVC, Redis PVC, corpus PVC | Data lake/quarantine/archive/results/traces PVC plan and persistence proof |
| F2 Jobs | Partial | Indexer Job/CronJob exist | Eval Job, persistent results, external gate ConfigMap and flip demo |
| F3 controlled release | Partial | Rolling strategy exists | Candidate service/collection and gated promotion/rollback proof |
| F4 cluster observability | Partial | JSON stdout and `/metrics` exist | Trace PVC and trace JSON lines; port-forward evidence |
| F5 resources | Partial | A02 static values/evidence | New `kubectl top` measurements during A03 workloads and justified final values |
| G report | Missing | A02 docs only | Scripted exactly-8-page body, result-fed tables/figures, screenshot appendix |

## Risks inherited from A02

- The cloned development requirements omitted Starlette 1.10's `httpx2` TestClient backend. With
  the deprecated legacy `httpx` fallback, route tests stalled at lifespan startup. Phase 0 pins
  `httpx2==2.16.2` in `api/requirements-dev.txt`; production dependencies and runtime code are
  unchanged.
- `TEMPERATURE` defaults to 0.2, so evaluation must override it to 0 and add an Ollama seed.
- API and indexer currently consume collection/model identity only through a ConfigMap. The live Deployment pod template needs literal `COLLECTION_NAME`, `EMBED_MODEL`, and `EMBED_VERSION` values so `rollout undo` restores them.
- The API NetworkPolicy allows Chroma access, but Kubernetes NetworkPolicy cannot express read-only HTTP semantics. Code and RBAC/service design must remain the enforcement boundary, while only indexer code contains write operations.
- A02 results and documentation include historical values; none may be reused as A03 measurements without a fresh A03 run and committed result file.

