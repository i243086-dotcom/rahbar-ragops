#!/usr/bin/env bash
set -euo pipefail
job=${1:?pass completed unchanged Batch B ingestion Job name}
echo "+ kubectl -n rahbar logs job/$job"
kubectl -n rahbar logs "job/$job" | rg 'verification complete|incremental update|indexer finished'
