#!/usr/bin/env bash
set -euo pipefail
trace_id=${1:?pass trace ID}
echo "+ python scripts/replay_trace.py $trace_id"
python scripts/replay_trace.py "$trace_id"
