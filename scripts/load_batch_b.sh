#!/usr/bin/env bash
set -euo pipefail
source_dir=${1:-corpus/batch_b}
test -d "$source_dir"

kubectl -n rahbar delete pod batch-b-loader --ignore-not-found --wait=true
sed -e 's/name: corpus-loader/name: batch-b-loader/' \
    -e 's/{name: corpus,/{name: batch-b,/' \
    -e 's/- name: corpus$/- name: batch-b/' \
    -e 's|mountPath: /corpus|mountPath: /data-lake/batch-b|' \
    -e 's/claimName: corpus/claimName: data-lake-batch-b/' \
    k8s/base/corpus-loader.yaml | kubectl create -f -
kubectl -n rahbar wait --for=condition=Ready pod/batch-b-loader --timeout=180s
kubectl -n rahbar cp "$source_dir/." batch-b-loader:/data-lake/batch-b
kubectl -n rahbar delete pod batch-b-loader --wait=true
echo "Loaded $source_dir into PVC data-lake-batch-b"
