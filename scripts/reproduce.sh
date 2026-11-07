#!/usr/bin/env bash
# Rebuild every result file from the raw snapshot in data/raw/ (OpenAlex, Scopus and WoS identifiers).
# Needs only Python 3.8+ (standard library). Run from anywhere.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"

echo "[1/4] merge   data/raw -> build/merged_v2.json"
"$PY" scripts/merge.py
echo "[2/4] clean   build/merged_v2.json -> build/clean_v2.json + results/removed_records.tsv"
"$PY" scripts/clean.py
echo "[3/4] merge databases  + data/raw/scopus_ta.tsv + data/raw/wos_ta.tsv -> build/combined.json + results/flow.tsv"
"$PY" scripts/merge_db.py
echo "[4/4] export  build/combined.json -> results/dataset1_* and results/dataset2_*"
"$PY" scripts/build.py
echo "done. Run: $PY scripts/verify.py"
