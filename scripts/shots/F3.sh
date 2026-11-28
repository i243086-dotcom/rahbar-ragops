#!/usr/bin/env bash
set -euo pipefail
job=${1:?pass evaluation Job name}
echo "+ kubectl -n rahbar get job $job"
kubectl -n rahbar get job "$job"
echo "+ kubectl -n rahbar logs job/$job"
kubectl -n rahbar logs "job/$job"
