#!/usr/bin/env bash
set -euo pipefail
echo "+ kubectl -n rahbar patch configmap rahbar-config (TEMPERATURE=0.2 CACHE_ENABLED=true)"
kubectl -n rahbar patch configmap rahbar-config --type merge \
  -p '{"data":{"TEMPERATURE":"0.2","CACHE_ENABLED":"true"}}'
echo "+ kubectl -n rahbar rollout restart deployment/api"
kubectl -n rahbar rollout restart deployment/api
echo "+ kubectl -n rahbar rollout status deployment/api --timeout=180s"
kubectl -n rahbar rollout status deployment/api --timeout=180s

