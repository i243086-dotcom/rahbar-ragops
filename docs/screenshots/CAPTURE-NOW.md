# Human screenshot capture — 28 November 2026

The working agreement requires human screenshots. Run each command in WSL from
the repository root, maximize the terminal, and use Windows Snipping Tool to save
the actual visible command and output under `docs/screenshots/`. Scroll and take
additional numbered captures when output cannot fit; do not crop away errors.

## Available now

Completed ingestion (F2):

```bash
bash scripts/shots/F2.sh indexer-1795866567039807708
```

Save as `F2_ingestion_job.png` (and numbered continuations). Include the final
incremental update with zero embedded chunks and collection count 584.
This is Batch A re-ingestion evidence; it does not replace Batch B A2 evidence.

Cluster resources and archive persistence (F1):

```bash
bash scripts/shots/F1.sh
```

Save resource output as `F1_cluster_resources.png` and persistence PASS output
as `F1_archive_persistence.png`. The script creates temporary marker writer and
reader pods and removes them after verification.

## After evaluation finishes

```bash
bash scripts/shots/F3.sh phase4-evaluation-pc2zv
```

Save as `F3_evaluation_job.png` and numbered continuations. A Job may exit 2
after producing results because human labels are pending; preserve that status.
Do not describe it as a complete human-reviewed evaluation until labels exist.

B1, C1/C2, E1/E2, F4/F5/F6 still require their actual corresponding runs.
Do not substitute a resources screenshot or a successful query for these items.
