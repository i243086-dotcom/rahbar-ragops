#!/usr/bin/env bash
set -euo pipefail
job=${1:?pass completed Batch B ingestion Job name}
echo "+ kubectl -n rahbar logs job/$job"
kubectl -n rahbar logs "job/$job"
echo "+ kubectl -n rahbar run reader to print persistent verification report"
kubectl -n rahbar run a1-reader --image=busybox:1.36 --restart=Never --rm -i --quiet \
  --overrides='{"spec":{"restartPolicy":"Never","containers":[{"name":"reader","image":"busybox:1.36","command":["sh","-c","cat /results/verification-*.json | head -c 12000"],"volumeMounts":[{"name":"results","mountPath":"/results"}]}],"volumes":[{"name":"results","persistentVolumeClaim":{"claimName":"eval-results"}}]}}'
