#!/bin/bash
# Verifier of B-emd-gw, claim C6: linear TT waves in a periodic box with AthenaK's Z4c,
# production numerics of tracks/B-emd-gw/periodic_z4c/inputs/lw_x.athinput (read-only,
# used with command-line overrides), processor executable of release core-v0.3.
#
#   v4_lw_runs.sh OUTDIR
#
# Cases (each in OUTDIR/<name>/, run in parallel, one thread each, at most 8 at a time):
#   x_N{16,32,64,128}  k = (1,0,0), thin box N x 4 x 4, 10 periods, dumps every 0.5
#   x_N32_long         k = (1,0,0), 50 periods, dumps every 5
#   ob_N{16,32}        k = (1,1,0), N x N x 4, 5 periods, x-slice tables, 10 dumps
#                      (input ../inputs/lw_oblique.athinput: lw_x.athinput with kx2 = 1,
#                      x2max = 1; slices along x)
set -u
OUT=${1:?outdir}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
IN=/data/haiyangw/nrpic/wt/B-emd-gw/tracks/B-emd-gw/periodic_z4c/inputs/lw_x.athinput
INOB=/data/haiyangw/nrpic/wt/B-emd-gw/tracks/B-emd-gw/stage/G0/verifier/inputs/lw_oblique.athinput
mkdir -p "$OUT"
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false

run() {  # name, input, overrides...
  local name=$1 inp=$2; shift 2
  mkdir -p "$OUT/$name"
  ( cd "$OUT/$name" && /usr/bin/time -v "$EXE" -i "$inp" -d . "$@" > athena.log 2> time.log;
    echo "exit $?" >> athena.log )
}

thin() {  # N tlim dt name
  local N=$1 T=$2 DT=$3 name=$4
  local w; w=$(python3 -c "print(4.0/$N)")
  local s; s=$(python3 -c "print(1.5/$N)")
  run "$name" "$IN" mesh/nx1=$N meshblock/nx1=$N mesh/x2max=$w mesh/x3max=$w \
      output1/slice_x2=$s output1/slice_x3=$s output1/dt=$DT output2/dt=$DT time/tlim=$T
}

oblique() {  # N name
  local N=$1 name=$2
  local w; w=$(python3 -c "print(4.0/$N)")
  local s; s=$(python3 -c "print(1.5/$N)")
  run "$name" "$INOB" mesh/nx1=$N meshblock/nx1=$N mesh/nx2=$N meshblock/nx2=$N \
      mesh/x3max=$w output1/slice_x2=$s output1/slice_x3=$s \
      output1/dt=0.35355339059327373 output2/dt=0.35355339059327373 time/tlim=5
}

thin 16 10 0.5 x_N16 &
thin 32 10 0.5 x_N32 &
thin 64 10 0.5 x_N64 &
thin 128 10 0.5 x_N128 &
thin 32 50 5 x_N32_long &
oblique 16 ob_N16 &
oblique 32 ob_N32 &
wait
grep -H "exit" "$OUT"/*/athena.log
