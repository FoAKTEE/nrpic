#!/usr/bin/env bash
# periodic_diag: the seeded frozen-lapse cases G5, G6 of JOURNAL.md entry 4 (uniform 64^3
# mesh, white noise 1e-10 in every evolved field: inputs/diag_uniform_seed.athinput), to t = 10, with the threaded processor
# build of release core-v0.6. Same deck and conventions as run_uniform.sh.
#   run_uniform2.sh <outdir> <threads> <case> [<case> ...]
#   G5  Gamma-driver, cfl 1.0, noise        G6  as G5 with time/cfl_number = 0.6
set -uo pipefail
OUT=$1; T=$2; shift 2
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=/data/haiyangw/nrpic
DECK=$HERE/../inputs/diag_uniform_seed.athinput
P0=$REPO/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
export ATHENA_EXE=$REPO/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
export THREADS=$T PLACES=auto
p0=(problem/id_file=$P0/fields.bin particles/particle_file=$P0/particles.nrp)
geo=(z4c/lapse_oplog=0.0 z4c/lapse_advect=0.0 z4c/lapse_leak=0.0)
for c in "$@"; do
  case $c in
    G5) args=("${p0[@]}" "${geo[@]}") ;;
    G6) args=("${p0[@]}" "${geo[@]}" time/cfl_number=0.6) ;;
    *) echo "unknown case $c"; continue ;;
  esac
  mkdir -p "$OUT/$c"
  echo "== $c $(date -Is) ${args[*]}"
  "$REPO/scripts/cpu_run.sh" "$OUT/$c" "$DECK" "${args[@]}"
  echo "== $c exit $? $(date -Is)"
  grep -E "Terminat|reason:|time=.*cycle=" "$OUT/$c/athena.log" | tail -n 4
done
exit 0
