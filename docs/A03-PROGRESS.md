# Assignment 03 progress

Last updated: 2026-11-26 (Asia/Karachi)

## Schedule

The working submission deadline is **2026-11-28 23:59 Asia/Karachi**, based on the owner's stated Saturday, 28 November deadline. Target: finish implementation and measured runs on 27 November, then reserve 28 November for teammate review, screenshots, the clean-cluster rehearsal, and final PDF assembly.

| Phase | Status | Evidence / decision |
| --- | --- | --- |
| 0 Bootstrap and A02 audit | Complete; PR pending | Audit/tests/report/cluster and real Ollama smoke test complete; public repository configured |
| 1 Platform baseline | Not started | — |
| 2 Verification and incremental update | Not started | — |
| 3 Trace and guardrail | Not started | — |
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

## Open items

1. Push the Phase 0 branch, open its pull request, and obtain the required teammate approval.
2. Teammate: accept the repository invitation and contribute review/commits that they can explain at the demo.
3. Complete Phases 1–9, measured runs, human-authored/reviewed evaluation items, screenshots, and contribution confirmation.

