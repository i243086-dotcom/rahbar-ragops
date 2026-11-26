# Kubernetes runbook

All assignment demonstrations run on Kubernetes. Docker is used only to build images for minikube.

## Fresh local cluster

```bash
minikube start -p rahbar --driver=docker --cpus=4 --memory=6144
minikube -p rahbar addons enable metrics-server
minikube -p rahbar addons enable ingress
docker build -t rahbar-api:dev api
docker build -t rahbar-indexer:dev indexer
docker build -t rahbar-ui:dev ui
minikube -p rahbar image load rahbar-api:dev rahbar-indexer:dev rahbar-ui:dev
OLLAMA_HOST_IP=<host-address-reachable-from-minikube> make apply OVERLAY=dev CORPUS=corpus/raw
kubectl -n rahbar rollout status deployment/api --timeout=10m
kubectl -n rahbar rollout status deployment/ui --timeout=10m
```

The API is a read-only Chroma client. Only the indexer Job/CronJob has ingestion code and write
responsibility. Persistent claims retain Chroma data, Batch A/B, quarantine, archive, evaluation
results, and traces. API replicas emit traces to stdout and `/traces/<pod>.jsonl`.

## Inspect and prove persistence

```bash
kubectl -n rahbar get all,pvc,configmap,cronjob,job
scripts/shots/F1.sh
```

The F1 helper writes a marker to the archive claim, deletes its temporary writer pod, mounts the
same claim in a replacement pod, and verifies the marker. It does not alter production documents.
