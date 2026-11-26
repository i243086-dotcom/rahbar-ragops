#!/usr/bin/env bash
set -euo pipefail

document=${1:?pass a Batch B filename}
case "$document" in
  09-irrelevant-gardening.md) ;;
  *) echo "refusing non-demo deletion target: $document" >&2; exit 2 ;;
esac

kubectl -n rahbar delete pod batch-b-delete --ignore-not-found --wait=true
sed -e 's/name: corpus-loader/name: batch-b-delete/' \
    -e 's/{name: corpus,/{name: batch-b,/' \
    -e 's/- name: corpus$/- name: batch-b/' \
    -e 's|mountPath: /corpus|mountPath: /data-lake/batch-b|' \
    -e 's/claimName: corpus/claimName: data-lake-batch-b/' \
    k8s/base/corpus-loader.yaml | kubectl create -f -
kubectl -n rahbar wait --for=condition=Ready pod/batch-b-delete --timeout=180s
kubectl -n rahbar exec batch-b-delete -- rm "/data-lake/batch-b/$document"
kubectl -n rahbar delete pod batch-b-delete --wait=true
echo "Deleted recoverable demo document from Batch B PVC: $document"
