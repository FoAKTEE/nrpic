#!/usr/bin/env bash
# Amplitude scan of tests F and X at N = 16: the amplitudes times 10 and times 1/10, to
# separate second-order effects (proportional to the amplitude, relative to the wave)
# from rounding (inversely proportional) and from truncation (independent).
#   run_ascan.sh           (through nrpic-run; output $NRPIC_RUN_DIR/{flat,exp}_s{10,0p1}/)
# Four serial AthenaK processes in parallel (processor executable of core/requests-b).
set -euo pipefail
out=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
PKG=$WT/tracks/B-emd-gw/waves
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/scratch/core/exe/core_requests-b/athena_cpu}
PY=${PYTHON:-python3}
N=16
MESH="mesh/nx1=$N mesh/nx2=$N mesh/nx3=$N meshblock/nx1=$N meshblock/nx2=$N meshblock/nx3=$N"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
declare -A FL=([s10]="problem/amp=1.0e-5 problem/amp_cross=5.0e-6" [s0p1]="problem/amp=1.0e-7 problem/amp_cross=5.0e-8")
declare -A XI=([s10]="--eps-p 2e-5 --eps-x 1e-5" [s0p1]="--eps-p 2e-7 --eps-x 1e-7")
pids=()
for s in s10 s0p1; do
  d=$out/flat_$s
  mkdir -p "$d"
  ( cd "$d" && "$EXE" -i "$PKG/inputs/flat_oblique.athinput" -d "$d" $MESH ${FL[$s]} \
      > "$d/athena.log" 2>&1; echo "rc=$?" >> "$d/athena.log" ) &
  pids+=($!)
  d=$out/exp_$s
  mkdir -p "$d/ic"
  # shellcheck disable=SC2086
  "$PY" "$PKG/scripts/make_expanding_ic.py" --n $N --out "$d/ic" ${XI[$s]} > "$d/ic.log"
  ( cd "$d" && "$EXE" -i "$PKG/inputs/expanding.athinput" -d "$d" $MESH \
      particles/particle_file="$d/ic/particles.nrp" problem/id_file="$d/ic/fields.bin" \
      > "$d/athena.log" 2>&1; echo "rc=$?" >> "$d/athena.log" ) &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for d in flat_s10 flat_s0p1 exp_s10 exp_s0p1; do echo "== $d: $(grep -E 'zone-cycles/cpu_second|rc=' "$out/$d/athena.log" | tr '\n' ' ')"; done
exit $rc
