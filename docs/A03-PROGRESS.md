# Assignment 03 progress

Last updated: 2026-11-26 (Asia/Karachi)

## Schedule

The working submission deadline is **2026-11-28 23:59 Asia/Karachi**, based on the owner's stated Saturday, 28 November deadline. Target: finish implementation and measured runs on 27 November, then reserve 28 November for teammate review, screenshots, the clean-cluster rehearsal, and final PDF assembly.

| Phase | Status | Evidence / decision |
| --- | --- | --- |
| 0 Bootstrap and A02 audit | Complete; PR pending | Audit/tests/report/cluster and real Ollama smoke test complete; public repository configured |
| 1 Platform baseline | Complete; PR pending | Deployment/StatefulSet/Services, nine bound PVCs, CronJob, trace sink, and pod-replacement persistence proof |
| 2 Verification and incremental update | Complete; PR pending | Real Batch B verification, unchanged/changed/deleted lifecycle jobs, archive/restore helper |
| 3 Trace and guardrail | Complete; PR pending | Full JSONL records, replay tool, summary metrics, injected-document trace |
| 4 Three-level offline testing | Not started | Human sign-offs required |
| 5 Change experiment and gate | Not started | — |
| 6 Controlled release and resources | Not started | — |
| 7 Drift and coverage | Not started | Human live-query review required |
| 8 Trace metrics and hardening | Not started | — |
| 9 Report and demo | Not started | Human screenshots and contribution confirmation required |

## Phase 0 findings and decisions

- `inputs/Assignment_03.md` is authoritative and has been read. The supplied plan says exactly 8 body pages; the assignment says at most 8, so the stricter exactly-8 target is adopted.
- The RAGOps paper sections 3.2, 4.2, 5.1, 6.2, Figure 3, Table 1, and Table 2 were extracted with Poppler and reviewed.
- A02 was cloned with history from the public repository; its source remote must not receive pushes.
- Git identity is `i243086-dotcom <i243086@isb.nu.edu.pk>` and `core.autocrlf=input`.
- The public repository is `https://github.com/i243086-dotcom/rahbar-ragops`; full A02 history is preserved. `main` is protected with one approving review required, administrators included, and force-push/deletion disabled. Teammate `m-shaheer-shoaib` has a pending push-access invitation.
- Docker access is intentionally blocked inside the managed sandbox but works with approved host access. Docker server 29.9.2 reports 8 CPUs and 8,155,459,584 bytes memory.
- Minikube profile `rahbar` is running Kubernetes 1.37.0 with Docker, Calico, 6144 MB and 4 CPUs. Calico, metrics-server and ingress pods reached Running.
- The three A02 images built and loaded. The real dev overlay deployed against Windows Ollama, reachable from minikube at `172.23.96.1:11434`, using `llama3.2:3b` and `nomic-embed-text`.
- The real indexer Job processed 9 documents into 665 chunks/vectors (dimension 768), including 41 OCR pages, in 677.1 seconds. Storage amplification was 1.059.
- A live Kubernetes query returned the correct 2.00 CGPA warning threshold with a citation to the June 2026 academic handbook, page 24. A hostel-room question produced no citations and `answered_from_context=false`, proving real abstention. The machine-captured payload and indexer JSON events are committed in `eval/results/phase0_baseline.json`.
- The public A02 corpus was fetched locally (ignored `corpus/raw/`) and all 9 documents pass `corpus/fetch.py --verify` against the tracked manifest.
- Python is 3.12.3. Poppler is installed. `kubectl kustomize` is available (v5.8.1); a separate Kustomize binary is unnecessary. Kubeconform v0.8.0 is installed under ignored `.tools/` and validated all 29 production resources with 0 invalid/errors/skips.
- ReportLab 4.2.5 is pinned for the report. `docs/report/report_body.pdf` builds as exactly 8 A4 pages. The production Kustomize overlay renders successfully.
- Baseline verification: 63 API tests passed, 30 indexer tests passed, Ruff passed, and mypy passed for 30 API plus 11 indexer source files. Tests require approved host execution because the managed sandbox blocks AnyIO's cross-thread event-loop wakeup.
- Starlette 1.10 warns that its legacy `httpx` TestClient backend is deprecated. `httpx2==2.16.2` is now pinned as a dev-only dependency; production code/dependencies are unchanged.

## Measurement ledger

Only real pipeline measurements go here. Phase 0 establishes deployment and ingestion baselines; A03 quality metrics begin in later phases.

| Metric | Value | Result file | Run context |
| --- | ---: | --- | --- |
| Indexed documents | 9 | `eval/results/phase0_baseline.json` | Real Kubernetes indexer Job |
| Embedded chunks/vectors | 665 | `eval/results/phase0_baseline.json` | `nomic-embed-text`, 768 dimensions |
| OCR pages | 41 | `eval/results/phase0_baseline.json` | Real corpus extraction |
| Indexer duration | 677.1 s | `eval/results/phase0_baseline.json` | Minikube `rahbar` |
| Storage amplification | 1.059 | `eval/results/phase0_baseline.json` | Stored/original word ratio |
| API ready replicas | 3 | `eval/results/phase1_platform.json` | Phase 1 minikube deployment |
| Chroma ready replicas | 1 | `eval/results/phase1_platform.json` | StatefulSet with persistent claim |
| Bound persistent claims | 9 | `eval/results/phase1_platform.json` | Includes data lake, quarantine, archive, results, traces |
| Batch B verification | 4 pass / 6 fail | `eval/results/phase2_data_lifecycle.json` | 10 remaining documents after deletion proof |
| Unchanged re-ingestion | 0 embedded chunks | `eval/results/phase2_data_lifecycle.json` | Same accepted corpus |
| Changed document | 1 embedded / 1 replaced | `eval/results/phase2_data_lifecycle.json` | `10-library-hours.md` only |
| Deleted document | 0 embedded / 1 deleted | `eval/results/phase2_data_lifecycle.json` | No gardening-vector orphan |
| Trace samples | 3 | `eval/results/phase3_trace_observability.json` | Kubernetes trace/replay verification |
| Prompt replay | 3/3 hashes match | `eval/results/phase3_trace_observability.json` | Stored prompt equals reconstructed hash |
| Injection actions flagged | 2 | `eval/results/phase3_trace_observability.json` | Query-shaped and retrieved Batch B instruction |

## Phase 3 observability decisions

- Each completed query trace records the original query, retrieval identity, filters, retrieved
  chunk/document/version/score references, rank order, full prompt plus SHA-256, context, model
  parameters, answer/citations, guardrail actions, stage latency, and cache outcome.
- `scripts/replay_trace.py <trace-id>` reads the persistent trace volume and verifies the stored
  prompt hash. `scripts/summarize_traces.py --input <jsonl>` emits top-1 similarity, abstention,
  cache, injection, and p95 stage-latency metrics.
- The committed Phase 3 samples were captured through the Kubernetes API with the deterministic
  stub generator because Windows Ollama generation stalled while embeddings stayed reachable. The
  result explicitly labels this run context; it is not used as a real-model quality claim.
- A Batch B collection trace retrieved `08-injected-instruction.md`; its stored prompt replaces
  the instruction with `[instruction-like text removed]` and records
  `retrieved_instruction_removed:1`. The stub response also masks this text.

## Phase 2 data-management decisions

- Verification happens after extraction and before chunking. It produces one JSON report per run,
  with quality, completeness, recency, and uniqueness checks and explicit reasons.
- Batch B contains 11 tracked fixtures (at least ten): two exact copies, one near copy, a truncated
  text file, missing metadata, a newer academic-rules version, an injected instruction, irrelevant
  retrieval noise, and an older archive/restore fixture.
- The real Batch B Job accepted five documents on its initial successful run and rejected six;
  duplicate, near-duplicate, truncated, missing-title, and older-version reasons are committed in
  `eval/results/phase2_data_lifecycle.json`. Failed items are copied to quarantine; the older
  version is copied to archive.
- A persistent `index-manifest.json` maps document hashes to chunk IDs. The second unchanged Job
  embedded zero chunks. A one-document update embedded/replaced one chunk; deleting the gardening
  fixture removed its sole stored chunk, reducing the collection from five to four.
- `scripts/restore_batch_b_archive.sh 11-academic-rules-2026.md` restores the archived, tracked
  lifecycle fixture to Batch B for the rollback demonstration. It is deliberately limited to that
  fixture and prints its SHA-256 proof.

## Phase 1 platform decisions

- The API remains a three-replica Deployment and Chroma remains a one-replica StatefulSet. The ingestion Job/CronJob is the only component containing vector-store write code.
- Dedicated persistent claims now hold Batch A, Batch B, quarantine, archive, evaluation results, and traces. The existing corpus, Chroma, and Redis claims remain intact.
- `COLLECTION_NAME`, `EMBED_MODEL`, and `EMBED_VERSION` are literal pod-template environment values, so Deployment revision history captures retrieval identity for later rollout undo.
- A central `TraceRecord` is emitted as JSON to stdout and appended to one JSONL file per API pod on the trace claim. Phase 3 will complete prompt/context reconstruction and trace metrics.
- The F1 script wrote an archive marker, deleted its writer pod, mounted the same claim in a replacement reader, and verified the marker. Machine-captured cluster and trace evidence is in `eval/results/phase1_platform.json`; the human screenshot is still pending.
- The first post-rollout query timed out because the applied NetworkPolicy retained the default minikube gateway CIDR instead of the Windows Ollama address. After correcting it to `172.23.96.1/32`, the query again returned the correct 2.00 CGPA answer and page-24 citation.

## Open items

1. Obtain teammate approval for the Phase 0 and Phase 1 pull requests.
2. Teammate: accept the repository invitation and contribute review/commits that they can explain at the demo.
3. Complete Phases 1–9, measured runs, human-authored/reviewed evaluation items, screenshots, and contribution confirmation.

