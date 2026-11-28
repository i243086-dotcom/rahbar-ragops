#!/usr/bin/env bash
set -euo pipefail
baseline=${1:?pass baseline JSON}
candidate=${2:?pass candidate JSON}
echo "+ python eval/phase5_gate.py --baseline $baseline --candidate $candidate"
python eval/phase5_gate.py --baseline "$baseline" --candidate "$candidate"

