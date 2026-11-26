#!/usr/bin/env bash
set -euo pipefail
job=${1:?pass completed unchanged Batch B ingestion Job name}
echo "+ kubectl -n rahbar logs job/$job | grep -E 'verification complete|incremental update|indexer finished'"
kubectl -n rahbar logs "job/$job" | grep -E 'verification complete|incremental update|indexer finished'
