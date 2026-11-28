#!/usr/bin/env bash
# Batch 34 processor smoke tests before the card members (periodic_threshold JOURNAL 2026-11-27):
#   SM-q: deck peak_leak.athinput with the quarter-amplitude data (S1L-q, A2Q);
#   SM-F: deck peak_leak_f.athinput (new finder lines: flow = shear, 4000 it, polish 100) with S1L's data.
# Release core-v0.8 processor executable, a few cycles, the finder from t = 0 every 2 cycles so that
# searches with diagnostics = true run and the new <fastflow> lines are parsed.
#   smoke_b34.sh <name> <deck> <data dir with fields.bin, particles.nrp> <outdir> [nlim] [extra overrides...]
set -euo pipefail
NAME=$1; DECK=$2; DATA=$3; OUT=$4; NLIM=${5:-4}; shift 5 || true
EXE=/data/haiyangw/nrpic/.work/build_cpu_v08/src/athena
export OMP_NUM_THREADS=1
mkdir -p "$OUT/$NAME"
rc=0
"$EXE" -i "$DECK" -d "$OUT/$NAME" problem/id_file=$DATA/fields.bin \
    particles/particle_file=$DATA/particles.nrp "$@" \
    time/nlim=$NLIM fastflow/start_time_0=0.0 fastflow/find_every=2 > "$OUT/$NAME/athena.log" 2>&1 || rc=$?
echo "$NAME exit $rc"
grep -i -E "cycle=|dt=|guard|horizon|error|warn|Terminat|gauge|particles from|flow" "$OUT/$NAME/athena.log" | tail -n 25
ls "$OUT/$NAME" | head -40
for f in "$OUT/$NAME"/*.horizon_status_0.txt; do [ -f "$f" ] && { echo "== $f"; cat "$f"; }; done
exit $rc
