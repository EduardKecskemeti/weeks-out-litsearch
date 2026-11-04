#!/usr/bin/env bash
# Rebuild every result file from the raw OpenAlex snapshot in data/raw/.
# Needs only Python 3.8+ (standard library). Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"

echo "[1/3] merge   data/raw -> build/merged_v2.json"
"$PY" scripts/merge.py
echo "[2/3] clean   build/merged_v2.json -> build/clean_v2.json + results/removed_records.tsv"
"$PY" scripts/clean.py
echo "[3/3] export  build/clean_v2.json -> results/dataset1_* and results/dataset2_*"
"$PY" scripts/build.py
echo "done. Run: $PY scripts/verify.py"
