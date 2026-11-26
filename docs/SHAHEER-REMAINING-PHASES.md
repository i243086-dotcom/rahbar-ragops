# Shaheer's Assignment 03 handoff guide

This is the ordered handoff for the remaining work on Assignment 03. Work from your own GitHub
account (`m-shaheer-shoaib`), make your own commits, and review PRs yourself. Do not change the
read-only `a02` remote and never commit tokens, `.env` files, downloaded corpus files, or model
credentials.

## 1. One-time setup on your laptop

First accept the collaborator invitation to `i243086-dotcom/rahbar-ragops`. Then open WSL/Ubuntu
or a Bash terminal and run:

```bash
git clone https://github.com/i243086-dotcom/rahbar-ragops.git
cd rahbar-ragops
git config user.name "Muhammad Shaheer Shoaib"
git config user.email "YOUR_GITHUB_EMAIL"
git config core.autocrlf input
git remote -v
git fetch origin --prune
git branch -a
```

Do not push to `main`. The open PRs are stacked, so inspect them in order: #1, #2, #3, and #4.
For work based on the current checkpoint:

```bash
git switch --track origin/feat/phase-4-offline-evaluation
git pull --ff-only
```

If that branch is not available yet, use the newest available Phase 3 branch, then create a
personal branch:

```bash
git switch --track origin/feat/phase-3-trace-observability
git switch -c shaheer/phase-4-human-evaluation
```

Install and check the local toolchain before editing anything:

```bash
make install PY=python3.12
make test
make lint
kubectl config current-context
kubectl -n rahbar get all,pvc,configmap,cronjob,job
```

If your cluster does not exist, follow [`k8s/README.md`](../k8s/README.md). You need Docker,
minikube, kubectl, Ollama with `nomic-embed-text` and `llama3.2:3b`, and a host address reachable
from minikube. All demonstrations must run on Kubernetes, not Docker Compose.

## 2. Rules for every phase

1. Read `AGENTS.md`, `docs/A03-PROGRESS.md`, and the relevant assignment section first.
2. Create one small branch from the latest agreed branch, for example:

   ```bash
   git switch -c shaheer/phase-4-human-inputs
   ```

3. Run tests before pushing. Record machine output only in `eval/results/` or `traces/`.
4. Never write made-up measurements, screenshots, reviews, labels, names, or teammate claims.
5. Commit under your own identity, push your branch, and open a PR. Ask Ayaan to review it.

   ```bash
   git status --short
   git add <only-the-files-you-changed>
   git commit -m "docs: add reviewed phase 4 human inputs"
   git push -u origin shaheer/phase-4-human-inputs
   gh pr create --base feat/phase-4-offline-evaluation --fill
   ```

6. For every required screenshot: run the command in a maximized terminal, keep the command and
   complete output visible, take an uncropped screenshot, save the PNG to the listed path, then
   commit it from your own branch.

   ```bash
   git add docs/screenshots/<file>.png
   git commit -m "docs: add <item> evidence screenshot"
   git push
   ```

If a command produces more than one terminal screen, capture sequential images such as `B1-1.png`
and `B1-2.png`; do not crop or fabricate output.

## 3. Finished phases: screenshots you can capture now

These scripts and Job names are already available on the current cluster.

```bash
cd ~/rahbar-ragops  # or your actual clone directory
scripts/shots/F1.sh
scripts/shots/A1.sh ingest-batch-b-j7n7x
scripts/shots/A2.sh ingest-batch-b-q4hhg
scripts/shots/D1.sh 24e0339e33ea425d975aa51e37bab629
scripts/shots/D2.sh 24e0339e33ea425d975aa51e37bab629
```

Save them as:

```text
docs/screenshots/F1_cluster_resources.png
docs/screenshots/A1_verification_batch_b.png
docs/screenshots/A2_unchanged_zero_embeddings.png
docs/screenshots/D1_full_trace.png
docs/screenshots/D2_trace_rebuild.png
```

If your own cluster has different Job names, find the equivalent completed Jobs first:

```bash
kubectl -n rahbar get jobs --sort-by=.metadata.creationTimestamp
```

Use your own completed Job name in the screenshot command.

## 4. Phase 4 — offline testing at three levels

This phase cannot be completed honestly without human input.

### Your required human contributions

- Write at least four of the eight required **human-written** golden questions in your own words.
- Review at least four synthetic questions: accept, edit, or reject each one.
- Label at least four answer-faithfulness samples after the evaluation run.

Do not let anyone pre-fill your name, date, question wording, review verdict, or label.

When the Phase 4 templates are committed, fill the blank files assigned to you under
`eval/human_inputs/`, then commit them. The evaluator must contain at least 25 questions total:
15 answerable, 5 abstain, 5 hard; all entries must cite their source/page and be labelled `human`
or `synthetic`.

Run the complete evaluation twice with fixed seeds. The final Phase 4 script will write timestamped
results under `eval/results/` and measure embeddings, retrieval, answers, noise, and variation.

Screenshot target after the evaluation script is committed:

```text
docs/screenshots/B1_evaluation_summary.png
```

Use the exact `scripts/shots/B1.sh` command supplied by the Phase 4 PR; do not substitute a
manually edited result file.

## 5. Phase 5 — change experiment and release gate

Compare one explicit candidate change against the measured Phase 4 baseline. Do not alter more
than one major pipeline variable at once. The gate thresholds must live in a ConfigMap and must
produce both a real failure and a real pass.

Expected screenshots after the Phase 5 scripts are committed:

```bash
scripts/shots/C1.sh   # failed gate
scripts/shots/C2.sh   # passed gate
scripts/shots/F2.sh   # completed ingestion Job logs
scripts/shots/F3.sh   # completed evaluation Job logs
scripts/shots/F4.sh   # ConfigMap threshold changes gate outcome
```

Save them under the corresponding `docs/screenshots/C1_gate_fail.png`, `C2_gate_pass.png`,
`F2_ingestion_job.png`, `F3_evaluation_job.png`, and `F4_configmap_gate_flip.png` paths.

## 6. Phase 6 — controlled Kubernetes release and resources

Run the candidate as its own Deployment, Service, and collection. Only release after the gate
passes. Show a stopped candidate and a real `kubectl rollout undo`; do not bypass the gate.

Take these screenshots from your own cluster after the scripts are committed:

```bash
scripts/shots/F5.sh   # kubectl rollout status
scripts/shots/F6.sh   # rollout undo plus new trace showing restored identity
```

Measure resource usage before changing requests/limits. Copy only measured values into the
report and the committed result JSON.

## 7. Phase 7 — live-query coverage and drift

Create 40 realistic live queries: about 28 in-domain and at least 12 uncovered-topic queries.
They are test data, not claims that real users submitted them. Run coverage before and after adding
at least six new golden questions from uncovered topics. The coverage script must fail below its
documented threshold.

Required screenshots once supplied by the Phase 7 PR:

```bash
scripts/shots/E1.sh   # before new golden questions
scripts/shots/E2.sh   # after new golden questions
```

Save to `docs/screenshots/E1_coverage_before.png` and
`docs/screenshots/E2_coverage_after.png`.

## 8. Phase 8 — final metrics and hardening

Run trace summary over a documented window and check: top-1 similarity distribution, abstention
rate, cache hit rate, p95 latency per stage, and injection attempts flagged. Choose one wrong or
abstained Phase 4 answer and write the root cause using only its trace. Commit the trace summary
and the root-cause evidence; do not infer missing fields.

## 9. Phase 9 — final report and demo handoff

- Confirm every number in the report exists in a committed result file.
- Keep the report body at **8 A4 pages or fewer**; screenshots are an appendix.
- Add both members' real names, roll numbers, and contribution table only after both confirm them.
- Include the 2–3 line AI statement accurately.
- Verify the README contains commands for Parts A–F.
- Rehearse on a clean minikube cluster: deploy, ingest unseen documents, run evaluation Job, open
  a trace, and demonstrate an abstention.

## 10. Review responsibilities

Review the stacked PRs in order and approve only after reading their verification output:

```bash
gh pr view 1 --repo i243086-dotcom/rahbar-ragops
gh pr view 2 --repo i243086-dotcom/rahbar-ragops
gh pr view 3 --repo i243086-dotcom/rahbar-ragops
gh pr view 4 --repo i243086-dotcom/rahbar-ragops
```

Use GitHub's **Review changes** button to approve or request changes. Your own commits and reviews
are required evidence that both group members contributed and can explain the work in the demo.
