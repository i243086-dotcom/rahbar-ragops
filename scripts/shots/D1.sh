#!/usr/bin/env bash
set -euo pipefail
trace_id=${1:?pass trace ID}
echo "+ kubectl -n rahbar logs -l app=api --prefix=true | grep -F $trace_id"
logs=$(kubectl -n rahbar logs -l app=api --prefix=true || true)
if printf '%s\n' "$logs" | grep -F "$trace_id"; then
  exit 0
fi

python_bin=${PYTHON_BIN:-}
if [[ -z "$python_bin" ]]; then
  python_bin=$(command -v python3 || command -v python || true)
fi
test -n "$python_bin" || { echo "Python 3 is required; install it with: sudo apt install python3" >&2; exit 127; }
echo "Trace is no longer in current pod logs; reading its persistent JSONL record instead."
echo "+ $python_bin scripts/replay_trace.py $trace_id"
"$python_bin" scripts/replay_trace.py "$trace_id"
