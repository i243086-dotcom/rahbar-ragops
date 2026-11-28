# Screenshot checklist

Humans capture these from the local minikube cluster. Each script must print its command before running it, show complete compact output, and save no fabricated evidence.

| ID | Required evidence | Target file | Phase | Status |
| --- | --- | --- | ---: | --- |
| A1 | Batch B verification, each check with reasons | `docs/screenshots/A1_verification_batch_b.png` | 2 | Script ready; human capture pending (`scripts/shots/A1.sh ingest-batch-b-j7n7x`) |
| A2 | Unchanged second ingestion: zero embedded, deletion/orphan counts visible | `docs/screenshots/A2_unchanged_zero_embeddings.png` | 2 | Script ready; human capture pending (`scripts/shots/A2.sh ingest-batch-b-q4hhg`) |
| B1 | Three-level evaluation summary | `docs/screenshots/B1_evaluation_summary.png` | 4 | Script ready; run `bash scripts/shots/B1.sh [result-json]` after human labels and the real evaluation |
| C1 | Gate failing | `docs/screenshots/C1_gate_fail.png` | 5 | Scripts ready; run `bash scripts/shots/C1.sh <baseline> <bad-candidate>` |
| C2 | Gate passing | `docs/screenshots/C2_gate_pass.png` | 5 | Scripts ready; run `bash scripts/shots/C2.sh <baseline> <passing-candidate>` |
| D1 | One complete trace record | `docs/screenshots/D1_full_trace.png` | 3 | Script ready; human capture pending (`scripts/shots/D1.sh 24e0339e33ea425d975aa51e37bab629`) |
| D2 | Trace tool rebuilds prompt/context | `docs/screenshots/D2_trace_rebuild.png` | 3 | Script ready; human capture pending (`scripts/shots/D2.sh 24e0339e33ea425d975aa51e37bab629`) |
| E1 | Coverage before | `docs/screenshots/E1_coverage_before.png` | 7 | Pending |
| E2 | Coverage after | `docs/screenshots/E2_coverage_after.png` | 7 | Pending |
| F1 | All resources plus archive-PVC survival across pod deletion | `docs/screenshots/F1_cluster_resources.png` | 1 | Human inventory captures saved 2026-11-28 (also F1_cluster_resources_2.png); archive-PVC survival capture still pending |
| F2 | Completed ingestion Job logs | `docs/screenshots/F2_ingestion_job.png` | 5 | Human screenshot supplied 2026-11-28; Complete 1/1, zero new embeddings, collection 584, indexer finished |
| F3 | Completed evaluation Job logs | `docs/screenshots/F3_evaluation_job.png` | 5 | Pending |
| F4 | Gate result before/after ConfigMap edit | `docs/screenshots/F4_configmap_gate_flip.png` | 5 | Pending |
| F5 | Rolling update status | `docs/screenshots/F5_rollout_status.png` | 6 | Pending |
| F6 | Rollout undo and new trace with prior identity | `docs/screenshots/F6_rollout_undo_trace.png` | 6 | Pending |

Optional extras: delete-orphan proof, archive/restore proof, and guardrail trace.

