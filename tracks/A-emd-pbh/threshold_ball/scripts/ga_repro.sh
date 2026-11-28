#!/usr/bin/env bash
# Entry 21 of threshold_ball (GA): the smallest processor reproducer of RT2a-A's guard stop.
# RT2a-A (A-20261128-081045-1e001cd, mesh A, faces at 32 + core-v0.6 face set, core-v0.9 card build) stopped at the
# guard at t = 48.140625; this continues its last restart file before the stop (rst/ball.00015.rst, t = 48.0) on the
# v0.9 threaded processor build to tlim 48.5 and prints where it stops.
#   ga_repro.sh <outdir>
set -uo pipefail
OUT=$1
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/athena_cpu_omp
RST=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261128-081045-1e001cd/rst/ball.00015.rst
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
D=$OUT/GA; mkdir -p "$D"
echo "== GA from $RST $(date +%T)"
ATHENA_EXE=$EXE THREADS=4 "$ROOT/scripts/cpu_run.sh" "$D" "$RST" time/tlim=48.5
rc=$?
echo "exit $rc $(date +%T)"
grep -h "the run stops\|first such cell\|MeshBlocks" "$D"/ball.guard.txt 2>/dev/null
grep -E "cycle=[0-9]+ time=" "$D"/athena.log | tail -2
exit 0
