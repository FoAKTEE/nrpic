#!/usr/bin/env bash
# Rerun of the first paper's two-overdensity case (run jeans/n1e4_v19) with the smeared
# Bowen-York curvature of the clumps: PREPARED, NOT RUN. The orchestrator schedules it.
#
#   tracks/core/analysis/clump/rerun_jeans_mc.sh [--control] [--dry-run] [--kind K]
#
# Run it from the root of a clean core worktree that has this file (the run is
# registered there by harness/bin/nrpic-run, launcher chain, on one card).
#   (default)   problems/jeans/jeans_mc.athinput as it is: the curvature of both clumps
#   --control   the same input, executable and particles with comp1_p1..3 = comp2_p1..3 = 0
#               (K_ij = 0, as in n1e4_v19): separates the effect of the curvature from
#               the change of executable (build_gpu_v7 then, this branch now) and from the
#               run-to-run scatter of card runs with deposition
#   --dry-run   print the manifest, start nothing (nrpic-run submit --dry-run)
#   --kind K    scouting (default) or production (needs the G1 tag of core; nrpic-run
#               checks)
#
# Inputs: the particle file and table of n1e4_v19, staged read-only with their checksums
# in scratch/core/clump-rerun/inputs/ (sha256 below; the generator reproduces both
# bytes: problems/ic/make_ic.py jeans --N 10000 --seed 1 --env-yc 0.907). They are named
# by absolute path on the command line because the chain creates the run directory.
# Executable: the card executable published from branch core/clump-curvature
# (scratch/core/exe/core_clump-curvature/athena_gpu, commit in COMMIT there).
# Cost: n1e4_v19 needed 13 segments of 25 min to reach t = 100 M (5.4 card-hours,
# runs/jeans/n1e4_v19/chain/events.log); here 50-min segments, at most 8 (--gpu-hours
# 8 reserves 8 x 59 min = 7.9 card-hours, below the eight of decision 0014). If the
# chain stops at the segment cap before t = 100 M, resume it (restarts are exact):
#   scripts/submit_chain.sh <rundir> problems/jeans/jeans_mc.athinput  (same args)
# Prediction and what refutes it (written before any run): tracks/core/JOURNAL-clump.md,
# "Prediction for the rerun of the two-overdensity case" and, for the control,
# "Prediction for the control of the rerun".
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
IN=/data/haiyangw/nrpic/scratch/core/clump-rerun/inputs
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_clump-curvature/athena_gpu
DECK=problems/jeans/jeans_mc.athinput
SHA_NRP=7270917fad5381932eb7e3fdb31239d5c565791deadba7c9751f2c6b8973ed9f
SHA_TAB=7ea9ca275a092d93775fd74e4b798eb24fbedaa507d2b168e2e28f4772392c59

control=0; dry=(); kind=scouting
while [[ $# -gt 0 ]]; do
  case $1 in
    --control) control=1 ;;
    --dry-run) dry=(--dry-run) ;;
    --kind) kind=$2; shift ;;
    -h|--help) sed -n '2,31p' "$0"; exit 0 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
  shift
done

check() {  # file, expected sha256
  [[ -f $1 ]] || { echo "missing: $1" >&2; exit 1; }
  local s
  s=$(sha256sum "$1" | cut -d' ' -f1)
  [[ $s == "$2" ]] || { echo "checksum of $1 is $s, expected $2" >&2; exit 1; }
}
check "$IN/particles.nrp" "$SHA_NRP"
check "$IN/envelope.tab" "$SHA_TAB"
[[ -x $EXE && -f $(dirname "$EXE")/READY ]] || { echo "no published executable: $EXE (READY)" >&2; exit 1; }
grep -q '^comp1_p2' "$DECK" || { echo "$DECK has no clump momenta" >&2; exit 1; }

args=("particles/particle_file=$IN/particles.nrp" "problem/comp0_file=$IN/envelope.tab")
if (( control )); then
  for c in 1 2; do for k in 1 2 3; do args+=("problem/comp${c}_p${k}=0.0"); done; done
  purpose="Control of the rerun of jeans/n1e4_v19: the input of the rerun with the clump momenta zero (K_ij = 0 as in n1e4_v19), same executable and particles; separates the curvature from the change of executable and the card scatter"
else
  purpose="Rerun of the first paper's two-overdensity case jeans/n1e4_v19 with the smeared Bowen-York curvature of both clumps (momentum constraint solved for their bulk motion), t = 0 to 100 M; does the remnant-mass excess of 2.5 percent stay"
fi

exec harness/bin/nrpic-run submit --kind "$kind" --gate G2 --launcher chain \
  --gpu-hours 8 --athena-wall 00:50:00 --exe "$EXE" \
  --preregistered "tracks/core/JOURNAL-clump.md" \
  --input "$IN/particles.nrp" --input "$IN/envelope.tab" --particles 10000 \
  --purpose "$purpose" "${dry[@]}" -- "$DECK" "${args[@]}"
