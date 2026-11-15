#!/bin/bash
# Analysis of the scans: digitize the 2404 figures (into the run directory), then S1, S1+S2, Kerr.
#   bash run_analysis.sh <outdir> <s1.npz> <s2.npz> <s3.npz> <s4.npz>
set -euo pipefail
OUT=$1; S1=$2; S2=$3; S3=$4; S4=$5
HERE=$(cd "$(dirname "$0")" && pwd)
PY=/data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python
FIG=/data/haiyangw/nrpic/kb-data/raw/arxiv/2404.16270/v1/src/Figures
mkdir -p "$OUT/digitized"
for f in sep_fraction v8-asymp frac-surv-Rgr-2; do
  python3 -I "$HERE/digitize_2404.py" "$FIG/$f.pdf" "$OUT/digitized/$f.json"
done
$PY -I "$HERE/analysis_s1.py" "$S1" "$OUT/digitized" "$OUT"
$PY -I "$HERE/analysis_strong.py" "$S1" "$S2" "$OUT"
$PY -I "$HERE/analysis_kerr.py" "$S1" "$S3" "$S4" "$OUT"
