#!/usr/bin/env bash
set -euo pipefail
trace_id=${1:?pass trace ID}
echo "+ kubectl -n rahbar logs -l app=api --prefix=true | rg $trace_id"
kubectl -n rahbar logs -l app=api --prefix=true | rg "$trace_id"
