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

Verification, Batch B, incremental update, orphan, archive, and restore results: pending Phase 2 result JSON.

## Page 5 — Part B

Module, component, end-to-end, noise, stochasticity, and judge-agreement results: pending Phase 4 result JSON.

## Page 6 — Parts C and F

Change experiment, gate, release decision, rollout/rollback, and resources: pending Phases 5–6 result JSON.

## Page 7 — Parts D and E

Trace metrics, guardrail evidence, root cause, data drift, and coverage: pending Phases 3, 7, and 8 result JSON.

## Page 8 — Short answers and contributions

Short answers (a)–(f): **DRAFT — team must rewrite in its own words after real results exist.** Contributions and AI statement require human confirmation and Git evidence.

