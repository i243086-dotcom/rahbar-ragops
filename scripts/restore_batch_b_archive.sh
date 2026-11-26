#!/usr/bin/env bash
set -euo pipefail

document=${1:?pass an archived Batch B filename}
case "$document" in
  11-academic-rules-2026.md) ;;
  *) echo "refusing non-demo archive target: $document" >&2; exit 2 ;;
esac

kubectl -n rahbar delete pod batch-b-restore --ignore-not-found --wait=true
kubectl -n rahbar run batch-b-restore --image=busybox:1.36 --restart=Never \
  --overrides='{"spec":{"securityContext":{"runAsUser":10001,"runAsGroup":10001,"fsGroup":10001},"containers":[{"name":"batch-b-restore","image":"busybox:1.36","command":["sh","-c","cp /archive/batch-b/'"$document"' /batch-b/restored-'"$document"' && sha256sum /batch-b/restored-'"$document"'"],"volumeMounts":[{"name":"archive","mountPath":"/archive"},{"name":"batch-b","mountPath":"/batch-b"}]}],"volumes":[{"name":"archive","persistentVolumeClaim":{"claimName":"archive"}},{"name":"batch-b","persistentVolumeClaim":{"claimName":"data-lake-batch-b"}}]}}'
kubectl -n rahbar wait --for=jsonpath='{.status.phase}'=Succeeded pod/batch-b-restore --timeout=120s
kubectl -n rahbar logs batch-b-restore
kubectl -n rahbar delete pod batch-b-restore --wait=true
echo "PASS restored archived lifecycle fixture: $document"
