#!/usr/bin/env bash
set -euo pipefail
result=${1:-}
python_bin=${PYTHON_BIN:-}
if [[ -z "$python_bin" ]]; then
  python_bin=$(command -v python3 || command -v python || true)
fi
test -n "$python_bin" || { echo "Python 3 is required; install it with: sudo apt install python3" >&2; exit 127; }
if [[ -n "$result" ]]; then
  echo "+ $python_bin scripts/phase4_summary.py $result"
  "$python_bin" scripts/phase4_summary.py "$result"
else
  echo "+ $python_bin scripts/phase4_summary.py"
  "$python_bin" scripts/phase4_summary.py
fi

