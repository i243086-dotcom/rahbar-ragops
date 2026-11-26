# RAHBAR RAGOps working agreement

This file preserves the operating rules supplied for Assignment 03. The authoritative assignment is `../inputs/Assignment_03.md`; re-read it at the start of every phase. If this file conflicts with the assignment, the assignment wins and the conflict must be reported.

## 1. How to work

- Work only in the numbered phase requested by the owner. At every phase end, stop and report: files built; commands and real outputs; PR/review status; report update and body page count; screenshot tasks; human tasks with steps/time; risks; and `Reply 'next' to continue.`
- Keep this file plus `docs/A03-PROGRESS.md`, `docs/A02-AUDIT.md`, `docs/AI-USAGE.md`, `docs/screenshots/CHECKLIST.md`, and `docs/TEAMMATE-TASKS.md` current and committed each phase.
- Use small commits. Never leave the branch broken at a phase checkpoint.
- Diagnose Kubernetes in this order: `kubectl get pods`, `kubectl describe pod` (Events), then `kubectl logs` (and `--previous` when relevant). Preserve and disclose failures.
- Install missing tools when safe. If installation fails, give the owner the exact command. Keep project artifacts in this repository.
- All demos and measured runs use Kubernetes/minikube. Docker-only or Compose demos receive zero.

## 2. Integrity rules

- Every reported number must come from a real run of this pipeline and a committed result under `eval/results/` or `traces/`. Never invent, estimate, or hand-edit measurements. `docs/report/build_report.py` must read result JSON and populate numerical report tables.
- Never commit credentials. Use ignored local files and checked-in placeholders. Scan the complete Git history before every push.
- Never impersonate teammate `m-shaheer-shoaib`, use his identity, or forge co-author trailers.
- Never fabricate human questions, reviews, labels, contribution claims, or sign-offs.
- The Assignment 02 repository is a read-only source. Do not push or otherwise modify it.

## 3. Human-work protocol

- Human golden questions: prepare `eval/human_inputs/WRITE_QUESTIONS.md` with at least 12 verified topic/document/page prompts and answer criteria, but no question wording. A human writes at least 8 questions in `human_questions.yaml`; only then import them as source `human`.
- Synthetic review: generate questions and `REVIEW_SYNTHETIC.md` with blank accept/edit/reject verdicts. Record reviewer and date only after a human fills them. At least 8 synthetic questions require review.
- Judge agreement: after a full run, prepare `LABEL_ANSWERS.md` containing question, context, answer, and a blank faithful yes/no/partial field. Compute agreement only after a human labels at least 8 answers.
- Ask the owner for both members' names and roll numbers and for contribution confirmation before finalizing page 1/page 8.
- Teammate commits must be made by the teammate from his account. Keep short, safe, exact tasks in `docs/TEAMMATE-TASKS.md` (questions, synthetic review, answer labels, small Batch B/README work, and PR reviews).
- Humans take every required screenshot. Scripts under `scripts/shots/` must print the command and then full compact output. Never claim a screenshot exists until a human saves it.
- Stop at each required human sign-off and wait.

## 4. GitHub workflow

- Target public repository: `i243086-dotcom/rahbar-ragops`, seeded once from `i243086-dotcom/rahbar` while preserving history. Invite `m-shaheer-shoaib` with push permission.
- Protect `main`: PR required, one approving review, stale approvals dismissed, no force-push/deletion, enforced for admins.
- Configure Git identity as the authenticated owner and `i243086@isb.nu.edu.pk`; use `core.autocrlf=input`.
- Apart from the one initial seed push, never push directly to `main`. Each phase uses `feat/phase-N-short-name`, small commits, and a PR listing changes, exact verification, assignment coverage, and screenshot expectations.
- Merge only when `gh pr view <n> --json reviewDecision,mergeable` reports approval and mergeability. Use squash merge and delete the branch. Never bypass protection. If the next phase is requested before approval, ask whether to stack it on the unmerged branch.

## 5. Screenshot protocol

For each item, add `scripts/shots/<ID>.sh`, list exact human capture steps, and update `docs/screenshots/CHECKLIST.md`. Required evidence:

- A1 Batch B verification by document/check/reason; A2 unchanged second ingestion with zero embeddings; optional orphan-delete and archive/restore evidence.
- B1 one summary containing module, component, and end-to-end results.
- C1 failing gate; C2 passing gate.
- D1 complete trace JSON; D2 trace tool rebuilding context/prompt.
- E1 coverage before; E2 coverage after new questions.
- F1 all resources/PVCs/ConfigMaps/CronJobs/Jobs; F2 completed ingestion logs; F3 completed evaluation logs; F4 ConfigMap threshold edit changing gate outcome; F5 rollout status; F6 rollout undo plus a new trace proving the prior collection/embedding version.

At Phase 9, assemble the labeled PNGs into the appendix PDF and list anything missing.

## Project and team context

- Owner: GitHub `i243086-dotcom`, email `i243086@isb.nu.edu.pk`.
- Teammate: GitHub `m-shaheer-shoaib`.
- A02 source: <https://github.com/i243086-dotcom/rahbar> (read-only).
- Local root: `/mnt/d/ragops-workspace/rahbar-ragops`.
- Namespace: `rahbar`; Ollama provides generation and embeddings; Chroma is the vector store; Redis is the semantic cache.
- Global invariants: config via environment/ConfigMap, fixed evaluation seeds, temperature zero for evaluation, API read-only against Chroma, ingestion Job sole writer, full required chunk metadata, and the A02 embedding-pin guardrail.

