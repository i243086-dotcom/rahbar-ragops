# Assignment 03 progress

Last updated: 2026-11-26 (Asia/Karachi)

## Schedule

The submission deadline is **pending owner confirmation**. A backward plan cannot be dated honestly until the owner supplies the date, time, and timezone. Default safety policy: finish Phase 9 at least 48 hours before submission; reserve the last 24 hours for clean-cluster rehearsal and the preceding 24 hours for teammate reviews, screenshots, and PDF assembly.

| Phase | Status | Evidence / decision |
| --- | --- | --- |
| 0 Bootstrap and A02 audit | In progress | Local audit/tests/report/cluster complete; real Ollama smoke test and GitHub operations blocked |
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
- GitHub CLI authentication is invalid. Repo creation, collaborator invite, protection, push, PR, and review remain blocked until `gh auth login -h github.com` is completed by the owner.
- Docker access is intentionally blocked inside the managed sandbox but works with approved host access. Docker server 29.9.2 reports 8 CPUs and 8,155,459,584 bytes memory.
- Minikube profile `rahbar` is running Kubernetes 1.37.0 with Docker, Calico, 6144 MB and 4 CPUs. Calico, metrics-server and ingress pods reached Running.
- The three A02 images built and loaded. The stub overlay deployed; its indexer Job completed with 3 chunks in 2.3 seconds and the API/UI rollouts completed.
- A Kubernetes query produced a cited stub response. The out-of-scope hostel query also produced an answer because the stub retriever always returns fixed high-scoring passages; this is not accepted as the required abstention proof. Real-model proof remains pending.
- Host Ollama is not listening on `localhost:11434`. The official installer was inspected, but local installation needs a sudo password; no unattended privilege bypass was attempted.
- A safer Docker fallback bound only to minikube's host gateway was attempted. The main `ollama/ollama` image layer made no observable progress for several minutes and the pull was cancelled cleanly; no Ollama container was created.
- The public A02 corpus was fetched locally (ignored `corpus/raw/`) and all 9 documents pass `corpus/fetch.py --verify` against the tracked manifest.
- Python is 3.12.3. Poppler is installed. `kubectl kustomize` is available (v5.8.1); a separate Kustomize binary is unnecessary. Kubeconform v0.8.0 is installed under ignored `.tools/` and validated all 29 production resources with 0 invalid/errors/skips.
- ReportLab 4.2.5 is pinned for the report. `docs/report/report_body.pdf` builds as exactly 8 A4 pages. The production Kustomize overlay renders successfully.
- Baseline verification: 63 API tests passed, 30 indexer tests passed, Ruff passed, and mypy passed for 30 API plus 11 indexer source files. Tests require approved host execution because the managed sandbox blocks AnyIO's cross-thread event-loop wakeup.
- Starlette 1.10 warns that its legacy `httpx` TestClient backend is deprecated. `httpx2==2.16.2` is now pinned as a dev-only dependency; production code/dependencies are unchanged.

## Measurement ledger

Only real pipeline measurements go here. Phase 0 has no A03 quality metrics yet.

| Metric | Value | Result file | Run context |
| --- | ---: | --- | --- |
| None yet | — | — | Phase 0 bootstrap |

## Open items

1. Owner: provide the assignment deadline (date, time, timezone).
2. Owner: run `gh auth login -h github.com` and confirm.
3. Start Ollama with required models and make it reachable from minikube (cluster creation is complete).
4. Create/push `i243086-dotcom/rahbar-ragops`, invite teammate, protect `main`, and open Phase 0 PR.
5. Fetch/verify the real corpus and prove A02 on Kubernetes with real cited and abstaining answers.

