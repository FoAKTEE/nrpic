#!/usr/bin/env bash
# Final regression of work package omp under threads (entries 2, 5, 6 of JOURNAL-omp.md):
# every regression case with the threaded build O3 at 1, 4 and 16 threads (two runs each
# at 4 and 16 for repeatability), compared with one thread of the same executable; then
# the deposit cases with private copies (deposit_threads = private) at 1, 4, 16 threads,
# two runs each, against the same one-thread reference (reused, not run again).
#   regress_threads.sh [exe-label]      (run inside the output directory)
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
X=${1:-O3}
"$PY" "$HERE/regress.py" --ref "$X:1" --configs "$X:4" "$X:4#2" "$X:16" "$X:16#2" \
    --pairs "$X:4#2=$X:4" "$X:16#2=$X:16" --out ./atomic
rc1=$?
"$PY" "$HERE/regress.py" --ref "$X:1" --cases dep,east,os,newton \
    --configs "$X:4" "$X:16" "$X:1:::priv" "$X:4:::priv" "$X:4:::priv#2" "$X:16:::priv" "$X:16:::priv#2" \
    --pairs "$X:4:::priv#2=$X:4:::priv" "$X:16:::priv#2=$X:16:::priv" \
            "$X:4:::priv=$X:4" "$X:16:::priv=$X:16" \
    --reuse ./atomic --out ./priv
rc2=$?
echo "atomic: exit $rc1, private: exit $rc2"
exit $(( rc1 | rc2 ))
