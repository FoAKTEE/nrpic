#!/usr/bin/env bash
# Package step-limit, test T3: Track A's uniform-mesh reproducer (inputs/diag_uniform.athinput,
# the physics of its card deck on the 64^3 root mesh, cfl_number 1.0 with dt_lightspeed 0.25)
# without and with <z4c> dt_gauge, on the threaded processor build of this branch.
#   run_uniform.sh <outdir> <threads> <exe> <case> [<case> ...]
#   G0   lapse frozen, Gamma-driver (Track A's G0: grid-scale growth of the shift)
#   G0g  the same with z4c/dt_gauge = 0.9
#   U0   relaxed 1+log lapse (lapse_leak 20) and Gamma-driver (Track A's U0: stiff relaxation)
#   U0g  the same with z4c/dt_gauge = 0.9
# Cases run one after the other; a case that stops on the guard (exit 3) is recorded and
# the next one runs.
set -uo pipefail
OUT=$1; T=$2; EXE=$3; shift 3
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$HERE/../../../.." && pwd)
DECK=$HERE/inputs/diag_uniform.athinput
P0=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
export ATHENA_EXE=$EXE
export THREADS=$T PLACES=auto
p0=(problem/id_file=$P0/fields.bin particles/particle_file=$P0/particles.nrp)
geo=(z4c/lapse_oplog=0.0 z4c/lapse_advect=0.0 z4c/lapse_leak=0.0)
for c in "$@"; do
  case $c in
    G0)  args=("${p0[@]}" "${geo[@]}") ;;
    G0g) args=("${p0[@]}" "${geo[@]}" z4c/dt_gauge=0.9) ;;
    U0)  args=("${p0[@]}") ;;
    U0g) args=("${p0[@]}" z4c/dt_gauge=0.9) ;;
    *) echo "unknown case $c"; continue ;;
  esac
  mkdir -p "$OUT/$c"
  echo "== $c $(date -Is) ${args[*]}"
  "$REPO/scripts/cpu_run.sh" "$OUT/$c" "$DECK" "${args[@]}"
  echo "== $c exit $? $(date -Is)"
  grep -E "Z4c step limit|Terminat|reason:|time=.*cycle=" "$OUT/$c/athena.log" | tail -n 8
done
exit 0
