#!/usr/bin/env bash
set -euo pipefail
trace_id=${1:?pass trace ID}
python_bin=${PYTHON_BIN:-}
if [[ -z "$python_bin" ]]; then
  python_bin=$(command -v python3 || command -v python || true)
fi
test -n "$python_bin" || { echo "Python 3 is required; install it with: sudo apt install python3" >&2; exit 127; }
echo "+ $python_bin scripts/replay_trace.py $trace_id"
"$python_bin" scripts/replay_trace.py "$trace_id"
