# RAHBAR RAGOps — Assignment 03

Status: Phase 0 skeleton. All metric cells remain pending until a committed A03 result file exists.

## Page 1 — System overview

Names and roll numbers: **PENDING OWNER INPUT**. Repository: <https://github.com/i243086-dotcom/rahbar-ragops>.

Architecture: Kubernetes API Deployment reads a versioned Chroma collection; an ingestion Job is the sole writer. Persistent volumes hold the data lifecycle and traces. An evaluation Job applies a ConfigMap-driven release gate before controlled rollout.

## Page 2 — Figure 3 stage mapping

Draft stages: ingest, verify, update data lake, update retrieval sources, offline testing, live testing, and coverage checking. File/evidence mappings will be populated phase by phase.

## Page 3 — Table 2 qualities

Draft qualities: adaptability, monitorability, observability, traceability, and reliability. Thresholds remain pending real measurements.

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

