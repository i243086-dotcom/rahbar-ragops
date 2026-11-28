#!/usr/bin/env bash
set -euo pipefail

namespace=rahbar
marker="phase1-persistence-$(date -u +%Y%m%dT%H%M%SZ)"

echo '+ kubectl -n rahbar get all,pvc,configmap,cronjob,job'
kubectl -n "$namespace" get all,pvc,configmap,cronjob,job

echo '+ create writer pod, write archive marker, and delete pod'
kubectl -n "$namespace" delete pod phase1-pvc-writer --ignore-not-found
kubectl -n "$namespace" run phase1-pvc-writer --image=busybox:1.36 --restart=Never \
  --overrides='{"spec":{"securityContext":{"runAsUser":10001,"runAsGroup":10001,"fsGroup":10001},"containers":[{"name":"phase1-pvc-writer","image":"busybox:1.36","command":["sh","-c","echo '"$marker"' > /archive/phase1-marker.txt"],"volumeMounts":[{"name":"archive","mountPath":"/archive"}]}],"volumes":[{"name":"archive","persistentVolumeClaim":{"claimName":"archive"}}]}}'
kubectl -n "$namespace" wait --for=jsonpath='{.status.phase}'=Succeeded pod/phase1-pvc-writer --timeout=120s
kubectl -n "$namespace" delete pod phase1-pvc-writer --wait=true

echo '+ create replacement reader pod and verify the same PVC marker'
kubectl -n "$namespace" delete pod phase1-pvc-reader --ignore-not-found
kubectl -n "$namespace" run phase1-pvc-reader --image=busybox:1.36 --restart=Never \
  --overrides='{"spec":{"securityContext":{"runAsUser":10001,"runAsGroup":10001,"fsGroup":10001},"containers":[{"name":"phase1-pvc-reader","image":"busybox:1.36","command":["cat","/archive/phase1-marker.txt"],"volumeMounts":[{"name":"archive","mountPath":"/archive"}]}],"volumes":[{"name":"archive","persistentVolumeClaim":{"claimName":"archive"}}]}}'
kubectl -n "$namespace" wait --for=jsonpath='{.status.phase}'=Succeeded pod/phase1-pvc-reader --timeout=120s
actual="$(kubectl -n "$namespace" logs phase1-pvc-reader)"
test "$actual" = "$marker"
echo "PASS archive PVC survived pod deletion: $actual"
kubectl -n "$namespace" delete pod phase1-pvc-reader --wait=true
