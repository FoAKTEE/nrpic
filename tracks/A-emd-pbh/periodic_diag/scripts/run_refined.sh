#!/usr/bin/env bash
# periodic_diag: the refined-mesh variants R0..R2 of JOURNAL.md: the card deck
# periodic_threshold/inputs/peak_leak.athinput itself (64^3 root, four static levels, P0L data
# with its 317 tracked particles, as card job 4799), on the threaded processor build of
# release core-v0.6, with line outputs every 0.1 time units and constraint statistics every
# cycle.
#   run_refined.sh <outdir> <threads> <case> [<case> ...]
#   R0  as card job 4799, to t = 2.7          R1  time/cfl_number = 0.5, to t = 5.0
#   R2  zero shift (shift_Gamma = 0), to t = 3.0
set -uo pipefail
OUT=$1; T=$2; shift 2
REPO=/data/haiyangw/nrpic
DECK=$REPO/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput
P0=$REPO/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
export ATHENA_EXE=$REPO/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
export THREADS=$T PLACES=auto
common=(problem/id_file=$P0/fields.bin particles/particle_file=$P0/particles_track.nrp
        particles/traj_ntrack=317 particles/cstat_dcycle=1 time/ndiag=1
        output2/dt=0.1 output3/dt=0.1 output7/dt=1000.0)
for c in "$@"; do
  case $c in
    R0) args=("${common[@]}" time/tlim=2.7) ;;
    R1) args=("${common[@]}" time/tlim=5.0 time/cfl_number=0.5) ;;
    R2) args=("${common[@]}" time/tlim=3.0 z4c/shift_Gamma=0.0 z4c/shift_eta=0.0
              z4c/shift_advect=0.0) ;;
    *) echo "unknown case $c"; continue ;;
  esac
  mkdir -p "$OUT/$c"
  echo "== $c $(date -Is) ${args[*]}"
  "$REPO/scripts/cpu_run.sh" "$OUT/$c" "$DECK" "${args[@]}"
  echo "== $c exit $? $(date -Is)"
  grep -E "Terminat|reason:|time=.*cycle=" "$OUT/$c/athena.log" | tail -n 4
done
exit 0
