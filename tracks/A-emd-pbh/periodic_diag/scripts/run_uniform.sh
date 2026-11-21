#!/usr/bin/env bash
# periodic_diag: the uniform-mesh variants U0..U7 of JOURNAL.md, one after the other, with the
# threaded processor build of release core-v0.6 (scripts/cpu_run.sh).
#   run_uniform.sh <outdir> <threads> <case> [<case> ...]
# Cases (each changes the deck inputs/diag_uniform.athinput by the overrides listed here):
#   U0  as the deck (P0L data)            U1  time/cfl_number = 0.5
#   U2  zero shift (shift_Gamma = 0)       U3  lapse_leak = 0 (pure 1+log)
#   U4  TSC deposit, no filter             U5  the S1 data (mu = 0.3, e = 0.2)
#   U6  time/cfl_number = 0.65             U7  time/cfl_number = 0.8
#   U8  zero shift (relaxed lapse, leak 20) U9  zero shift, lapse_leak = 5 (JOURNAL entry 10)
# G cases: the lapse frozen (lapse_oplog 0, lapse_advect 0, lapse_leak 0), JOURNAL entry 2:
#   G0  Gamma-driver, cfl 1.0              G1  time/cfl_number = 0.5
#   G2  zero shift                         G3  the S1 data
#   G4  TSC deposit, no filter
# A case that stops on the guard (exit 3) or otherwise is recorded and the next one runs.
set -uo pipefail
OUT=$1; T=$2; shift 2
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=/data/haiyangw/nrpic
DECK=$HERE/../inputs/diag_uniform.athinput
P0=$REPO/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
S1=$REPO/scratch/A-emd-pbh/A-emd-pbh-20261115-155802-9a6596f/S_mu0.3
export ATHENA_EXE=$REPO/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
export THREADS=$T PLACES=auto
p0=(problem/id_file=$P0/fields.bin particles/particle_file=$P0/particles.nrp)
s1=(problem/id_file=$S1/fields.bin particles/particle_file=$S1/particles.nrp)
geo=(z4c/lapse_oplog=0.0 z4c/lapse_advect=0.0 z4c/lapse_leak=0.0)
for c in "$@"; do
  case $c in
    U0) args=("${p0[@]}") ;;
    U1) args=("${p0[@]}" time/cfl_number=0.5) ;;
    U2) args=("${p0[@]}" z4c/shift_Gamma=0.0 z4c/shift_eta=0.0 z4c/shift_advect=0.0) ;;
    U3) args=("${p0[@]}" z4c/lapse_leak=0.0) ;;
    U4) args=("${p0[@]}" particles/deposit_shape=tsc particles/nfilter=0
              particles/filter_compensate=false) ;;
    U5) args=("${s1[@]}") ;;
    U6) args=("${p0[@]}" time/cfl_number=0.65) ;;
    U7) args=("${p0[@]}" time/cfl_number=0.8) ;;
    U8) args=("${p0[@]}" z4c/shift_Gamma=0.0 z4c/shift_eta=0.0 z4c/shift_advect=0.0) ;;
    U9) args=("${p0[@]}" z4c/shift_Gamma=0.0 z4c/shift_eta=0.0 z4c/shift_advect=0.0
              z4c/lapse_leak=5.0) ;;
    G0) args=("${p0[@]}" "${geo[@]}") ;;
    G1) args=("${p0[@]}" "${geo[@]}" time/cfl_number=0.5) ;;
    G2) args=("${p0[@]}" "${geo[@]}" z4c/shift_Gamma=0.0 z4c/shift_eta=0.0
              z4c/shift_advect=0.0) ;;
    G3) args=("${s1[@]}" "${geo[@]}") ;;
    G4) args=("${p0[@]}" "${geo[@]}" particles/deposit_shape=tsc particles/nfilter=0
              particles/filter_compensate=false) ;;
    *) echo "unknown case $c"; continue ;;
  esac
  mkdir -p "$OUT/$c"
  echo "== $c $(date -Is) ${args[*]}"
  "$REPO/scripts/cpu_run.sh" "$OUT/$c" "$DECK" "${args[@]}"
  echo "== $c exit $? $(date -Is)"
  grep -E "Terminat|reason:|time=.*cycle=" "$OUT/$c/athena.log" | tail -n 4
done
exit 0
