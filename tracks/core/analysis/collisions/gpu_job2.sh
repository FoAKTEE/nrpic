#!/usr/bin/env bash
# Card runs of the work package coll2 in one allocation (short jobs), by part:
#   (from the root of the worktree)
#   sbatch -p preempt --gres=gpu:1 -c 2 -t 00:30:00 -J core-coll2 -o <log> \
#          tracks/core/analysis/collisions/gpu_job2.sh <part> <card exe> <release card exe> <python>
#   part R  regression: five existing set-ups against the release executable; the
#           collisional box tests of wave 1 (options absent) against their card outputs
#   part N  the new tests: gradient (three cases), replay of the coll_energy cases,
#           equilibrium in the potential well
#   part C  the relativistic cluster at Knudsen number 3 with coll_energy = cell and
#           = particle (collision cells of 2 M)
# Each test is a registered run (runreg.py --card); its card time is its wall time
# inside the allocation.
set -uo pipefail
PART=$1; EXE=$2; BASE=$3; PY=$4
REPO=${SLURM_SUBMIT_DIR:?submit with sbatch from the root of the worktree}
[[ -f $REPO/tracks/core/analysis/collisions/common.py ]] || { echo "not a worktree: $REPO"; exit 1; }
R=tracks/core/analysis/rng
C=tracks/core/analysis/collisions
S=/data/haiyangw/nrpic/scratch/core
cd "$REPO"
nvidia-smi -L
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2

if [[ $PART == R ]]; then
  $PY $R/runreg.py --card --kind production \
    --purpose "R on one A100: five existing set-ups, executable of core/collisions-2 (options absent) against the release executable core-v0.3" \
    --input "$BASE" --input "$EXE" --input $R/run_regression.py -- \
    $PY "{repo}/$R/run_regression.py" --base "$BASE" --new "$EXE"
  $PY $C/rerun_wave1.py "$S/tmp/coll2/rerun_wave1_card.json" --exe "$EXE" --python $PY --card \
    --tests rate,relax,repro,conv_dt,curved
fi
if [[ $PART == N ]]; then
  $PY $R/runreg.py --card --kind production \
    --purpose "G1 G2 on one A100: one collision step in the static conformal metric, cases psi_iso, well_tolman, well_shift, psi_iso_hot, both modes" \
    --input "$EXE" --input $C/run_gradient.py -- \
    $PY "{repo}/$C/run_gradient.py" "{out}" --exe "$EXE" --nproc 2 --n 2000000 \
    --ref $S/core-20261115-160136-819d588/ref.json --ref $S/core-20261115-160137-819d588/ref.json \
    --ref $S/core-20261115-160139-819d588/ref.json --cases psi_iso,well_tolman,well_shift,psi_iso_hot
  $PY $R/runreg.py --card --kind production \
    --purpose "G2e on one A100: replay of single collision steps by the Python twin, wave-1 cases and the cases of coll_energy" \
    --input "$EXE" --input $C/run_replay.py -- \
    $PY "{repo}/$C/run_replay.py" "{out}" --exe "$EXE" --nproc 2 --new --n 6000
  $PY $R/runreg.py --card --kind production \
    --purpose "G4 on one A100: equilibrium in the potential well with streaming and collisions, both modes, two seeds" \
    --input "$EXE" --input $C/run_tolman.py -- \
    $PY "{repo}/$C/run_tolman.py" "{out}" --exe "$EXE" --nproc 2
fi
if [[ $PART == C ]]; then
  $PY $R/runreg.py --card --kind production \
    --purpose "P11 with coll_energy on one A100: relativistic cluster y_c = 0.819 at Knudsen number 3, collision cells of 2 M, coll_energy = cell and = particle, 150 M" \
    --input "$EXE" --input $C/run_cluster.py -- \
    $PY "{repo}/$C/run_cluster.py" "{out}" --exe "$EXE" --kn 3 --skip-null --energy cell,particle
fi
echo "gpu_job2 part $PART finished"
