#!/usr/bin/env bash
# GPU runs of the test-particle cluster campaign (docs/results_cluster_test.md), all
# through scripts/gpu_run.sh with TIME=00:20:00 and JOB_NAME=tpc.
#
#   problems/cluster_test/run_campaign.sh [name ...]          blocking, one after another
#   CHAIN=<jobid|none> problems/cluster_test/run_campaign.sh [name ...]
#        queue the runs at once with gpu_run.sh's BATCH=1 mode, each job depending on the
#        previous one (--dependency=afterany), so that only one of them runs at a time;
#        the first waits for job <jobid>.  BATCH=1 copies the executable into the run
#        directory at submission (provenance).  The input file itself is read when the
#        job starts.
#
# A run whose latest log ends with "Terminating on time limit" and exit=0 is skipped.
# Particle files: problems/cluster_test/make_campaign_ic.py -> runs/cluster_test/ic/
set -uo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$REPO"
IC=$REPO/runs/cluster_test/ic
MESH=problems/cluster_test/cluster_mesh.athinput
ANA=problems/cluster_test/cluster_analytic.athinput
export ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v2/src/athena
export TIME=00:20:00
export JOB_NAME=tpc
WALL=00:18:00            # athena's own wall-clock stop, before the Slurm limit

declare -A INP ARGS
ORDER=()
run_def() { local name=$1 inp=$2; shift 2; INP[$name]=$inp; ARGS[$name]="$*"; ORDER+=("$name"); }

for a in 0.9 0.0; do
  run_def mesh_a${a}_n10000_mid   $MESH particles/particle_file=$IC/bound_a${a}_n10000.nrp particles/bh_spin=$a
  run_def ana_a${a}_mid           $ANA  particles/particle_file=$IC/bound_a${a}_all.nrp particles/bh_spin=$a
done
for a in 0.0 0.9; do
  run_def plunge_a${a}_mid        $MESH particles/particle_file=$IC/plunge_a${a}_n10000.nrp particles/bh_spin=$a particles/snap_dt=1.0 time/tlim=500.0
done
for a in 0.9 0.0; do
  run_def mesh_a${a}_n10000_boris $MESH particles/particle_file=$IC/bound_a${a}_n10000.nrp particles/bh_spin=$a particles/pusher=boris
  run_def ana_a${a}_boris         $ANA  particles/particle_file=$IC/bound_a${a}_all.nrp particles/bh_spin=$a particles/pusher=boris
done
for a in 0.9 0.0; do
  run_def mesh_a${a}_n1000_mid    $MESH particles/particle_file=$IC/bound_a${a}_n1000.nrp particles/bh_spin=$a
  run_def mesh_a${a}_n100_mid     $MESH particles/particle_file=$IC/bound_a${a}_n100.nrp particles/bh_spin=$a
done
for a in 0.9 0.0; do
  run_def ana_a${a}_bchol         $ANA  particles/particle_file=$IC/bound_a${a}_all.nrp particles/bh_spin=$a particles/pusher=boris particles/triad=cholesky
done
for a in 0.0 0.9; do
  run_def plunge_a${a}_boris      $MESH particles/particle_file=$IC/plunge_a${a}_n10000.nrp particles/bh_spin=$a particles/snap_dt=1.0 time/tlim=500.0 particles/pusher=boris
done

done_ok() {
  local log=runs/cluster_test/$1/athena.log
  [[ -f $log ]] && grep -q "Terminating on time limit" "$log" && grep -q "# exit=0" "$log"
}

names=("$@")
[[ ${#names[@]} -eq 0 ]] && names=("${ORDER[@]}")
echo "# $(date -Is) exe md5 $(md5sum "$ATHENA_EXE" | cut -d' ' -f1) $ATHENA_EXE"
prev=${CHAIN:-}
for n in "${names[@]}"; do
  [[ -n ${INP[$n]:-} ]] || { echo "unknown run $n" >&2; continue; }
  if done_ok "$n"; then echo "== $n: done, skipped"; continue; fi
  echo "== $n: $(date -Is) submitting"
  echo "   scripts/gpu_run.sh runs/cluster_test/$n ${INP[$n]} ${ARGS[$n]} -t $WALL"
  if [[ -n ${CHAIN:-} ]]; then
    dep=""
    [[ -n $prev && $prev != none ]] && dep="--dependency=afterany:$prev"
    # shellcheck disable=SC2086
    out=$(BATCH=1 SLURM_EXTRA="$dep" scripts/gpu_run.sh runs/cluster_test/$n ${INP[$n]} \
            ${ARGS[$n]} -t $WALL)
    echo "   $out ($dep)"
    prev=$(sed -n 's/^submitted job \([0-9]*\).*/\1/p' <<< "$out")
    [[ -n $prev ]] || { echo "submission failed" >&2; exit 1; }
  else
    # shellcheck disable=SC2086
    scripts/gpu_run.sh runs/cluster_test/$n ${INP[$n]} ${ARGS[$n]} -t $WALL
    echo "== $n: $(date -Is) finished rc=$?"
  fi
done
