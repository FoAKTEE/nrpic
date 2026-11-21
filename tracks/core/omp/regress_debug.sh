#!/usr/bin/env bash
# P12: the OpenMP build with Kokkos debug mode and View bounds checking (DEBUG=1
# scripts/build_cpu_omp.sh .work/build_omp_dbg) on the deposit cases at 4 threads, with
# atomic additions and with private copies, compared with one thread of O3 (reused from the
# final regression run given as $1, its directory atomic/).
#   regress_debug.sh <output dir of regress_threads.sh>      (run inside the output directory)
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
"$PY" "$HERE/regress.py" --ref O3:1 --cases dep,east,newton,coll \
    --configs D:4 "D:4:::priv" --reuse "$1/atomic" --jobs 2 --out ./debug
