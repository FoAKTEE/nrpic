#!/usr/bin/env bash
# Package step-limit, test T4 on processors: Track A's refined periodic deck
# (inputs/peak_leak.athinput: 64^3 root, four static levels, finest dx 0.0195, the P0L data
# with its 317 tracked particles) at cfl_number 1.0, as card job 4799 of Track A (run
# A-20261121-131600-02b5d41: jump at t = 2.5, guard stop at t = 4.8), on the threaded
# processor build of this branch, with line outputs every 0.1 and constraint statistics
# every cycle.  About 14 to 21 s per cycle on 6 to 4 threads.
#   run_refined.sh <outdir> <threads> <exe> <case> [<case> ...]
#   R0   as job 4799 (no dt_gauge), to t = 2.7
#   R0g  with z4c/dt_gauge = 0.9, to t = 3.0
#   R1   Track A's remedy cfl_number 0.5, no dt_gauge, to t = 3.0
set -uo pipefail
OUT=$1; T=$2; EXE=$3; shift 3
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$HERE/../../../.." && pwd)
DECK=$HERE/inputs/peak_leak.athinput
P0=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
export ATHENA_EXE=$EXE
export THREADS=$T PLACES=auto
common=(problem/id_file=$P0/fields.bin particles/particle_file=$P0/particles_track.nrp
        particles/traj_ntrack=317 particles/cstat_dcycle=1 time/ndiag=1
        output2/dt=0.1 output3/dt=0.1 output7/dt=1000.0)
for c in "$@"; do
  case $c in
    R0)  args=("${common[@]}" time/cfl_number=1.0 time/tlim=2.7) ;;
    R0g) args=("${common[@]}" time/cfl_number=1.0 time/tlim=3.0 z4c/dt_gauge=0.9) ;;
    R1)  args=("${common[@]}" time/cfl_number=0.5 time/tlim=3.0) ;;
    *) echo "unknown case $c"; continue ;;
  esac
  mkdir -p "$OUT/$c"
  echo "== $c $(date -Is) ${args[*]}"
  "$REPO/scripts/cpu_run.sh" "$OUT/$c" "$DECK" "${args[@]}"
  echo "== $c exit $? $(date -Is)"
  grep -E "Z4c step limit|Terminat|reason:|time=.*cycle=" "$OUT/$c/athena.log" | tail -n 8
done
exit 0
