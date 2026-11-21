#!/usr/bin/env bash
# Analyses of the package faces as one registered run: each argument is NAME=SPEC where
# SPEC is a file of this directory under specs/ holding one analysis command per line
# (python3 scripts of this directory with their arguments; $OUT is replaced by the run's
# output directory). Outputs: $NRPIC_RUN_DIR/<results and figures>, copied into
# results/ and figs/ of the package by hand afterwards.
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
OUT=${NRPIC_RUN_DIR:?run through nrpic-run}
mkdir -p "$OUT/results" "$OUT/figs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
rc=0
for spec in "$@"; do
  while IFS= read -r line; do
    [[ -z $line || $line == \#* ]] && continue
    cmd=${line//\$OUT/$OUT}
    echo "### $cmd"
    # shellcheck disable=SC2086
    (cd "$HERE" && python3 $cmd) || { echo "### exit $?"; rc=1; }
  done < "$HERE/specs/$spec"
done
exit $rc
