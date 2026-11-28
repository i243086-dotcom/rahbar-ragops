# RAHBAR RAGOps — Assignment 03

Status: Phase 1 working draft. Numerical cells are populated only from committed result JSON.

## Page 1 — System overview

Names and roll numbers: **PENDING OWNER INPUT**. Repository: <https://github.com/i243086-dotcom/rahbar-ragops>.

Architecture: Kubernetes API Deployment reads a versioned Chroma collection; an ingestion Job is the sole writer. Persistent volumes hold the data lifecycle and traces. An evaluation Job applies a ConfigMap-driven release gate before controlled rollout.

## Page 2 — Figure 3 stage mapping

| Paper stage | Pipeline responsibility | Evidence file | Remaining work |
| --- | --- | --- | --- |
| Ingest | Kubernetes indexer Job/CronJob is sole Chroma writer | `k8s/base/indexer-job.yaml` | Phase 2 incremental manifest |
| Verify | Post-extraction pre-chunk checks | Phase 2 | Four checks and reports |
| Update data lake | Batch A/B, quarantine, archive PVCs | `k8s/base/ragops-storage.yaml` | Phase 2 lifecycle logic |
| Update retrieval sources | Chroma StatefulSet and pinned identity | `k8s/base/chroma-statefulset.yaml` | Phase 2 scoped updates |
| Offline testing | Evaluation results PVC | `k8s/base/ragops-storage.yaml` | Phase 4 suite and Job |
| Live testing | Per-query stdout and persistent JSONL traces | `api/app/trace.py` | Phase 3 full trace |
| Check coverage | Planned trace/golden similarity check | Phase 7 | Not implemented |

## Page 3 — Table 2 qualities

| Quality | Measurement | Threshold | Evidence |
| --- | --- | --- | --- |
| Adaptability | Candidate versus baseline suite | Phase 5 decision | Pending experiment |
| Monitorability | Trace summary and coverage | Phase 7/8 decision | Trace sink exists |
| Observability | Latency, similarity, abstention, cache, injection | Phase 3 decision | Trace schema established |
| Traceability | Query record and reconstruction | Every query; exact rebuild | Phase 3 pending |
| Reliability | Readiness, persistence, rollout | All replicas ready; PVC survives restart | `eval/results/phase1_platform.json` |

## Page 4 — Part A

Batch B verification is captured in `eval/results/phase2_data_lifecycle.json`: 4 of 10 remaining
documents passed and 6 failed. The checks caught two exact duplicates, one near duplicate, one
truncated file, missing title metadata, and an older academic-rules version. The unchanged rerun
embedded 0 chunks; a changed library document embedded/replaced 1; deletion removed 1 gardening
chunk and left a 4-chunk collection. Archive restoration is an explicit, SHA-256-verified helper.

## Page 5 — Part B

The executable Phase 4 suite is implemented in `eval/phase4_eval.py`. The measured run used 15
paraphrase/unrelated pairs and two runs with seed 4032. Both runs measured recall@5 0.25,
citation validity 1.0, abstention correctness 1.0, and p95 latency 17,912.8 ms on run 2.
The result is `eval/results/phase4_offline_evaluation_20261128T144142Z.json`. Eight human labels
were recorded in `eval/human_inputs/answer_labels.yaml`; a scoring rerun is still required to
populate human faithfulness in the final result.

## Page 6 — Parts C and F

Phase 5 now has a standalone threshold-driven gate in `eval/phase5_gate.py`; thresholds are also
committed as `k8s/base/phase5-gate-configmap.yaml`. The C1/C2 screenshots and release decision
remain pending real baseline/candidate Phase 4 result files.

## Page 7 — Parts D and E

Trace records now include the query, retrieval identity and scores, rank order, exact context,
full prompt/hash, model settings, citations, guardrail actions, cache outcome, and per-stage
latency. Three Kubernetes samples replayed with matching hashes. An injected Batch B document was
retrieved; its instruction-like sentence was removed from the stored prompt and logged. These are
mechanics measurements only: the committed run uses the stub generator because live Ollama
generation was stalled. Coverage/drift and real-model trace metrics remain pending later phases.

## Page 8 — Short answers and contributions

Short answers (a)–(f): **DRAFT — team must rewrite in its own words after real results exist.** Contributions and AI statement require human confirmation and Git evidence.

