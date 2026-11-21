#!/usr/bin/env bash
# Second reading of every regression run of work package omp with the measures of the
# predictions (recompare.py), and the figure of the differences (figs.py diff).
#   analyse_regress.sh       (run inside the output directory; writes summary_floor.json
#                             next to each summary.json and figs/thread_diff.{png,pdf})
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
S=/data/haiyangw/nrpic/scratch/core
dirs=("$S/core-20261119-154940-1c3e906" "$S/core-20261119-155520-0bc529f/serial"
      "$S/core-20261119-155520-0bc529f/atomic" "$S/core-20261119-155057-57325bc/atomic"
      "$S/core-20261119-155057-57325bc/priv" "$S/core-20261119-155830-248f393/debug")
"$PY" "$HERE/recompare.py" "${dirs[@]}" > recompare.txt 2>&1; echo "recompare exit $?"
grep -v "^          identity" recompare.txt | grep -c FAIL
mkdir -p figs
"$PY" "$HERE/figs.py" diff --runs "$S/core-20261119-155057-57325bc/atomic" \
    "$S/core-20261119-155520-0bc529f/atomic" "$S/core-20261119-155057-57325bc/priv" \
    --out figs/thread_diff
cp figs/thread_diff.png figs/thread_diff.pdf "$HERE/figs/"
