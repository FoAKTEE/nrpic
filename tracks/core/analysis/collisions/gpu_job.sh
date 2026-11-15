#!/usr/bin/env bash
# Card runs of the collision work package in one allocation (short jobs), by part:
#   (from the root of the worktree)
#   sbatch -p preempt --gres=gpu:1 -c 2 -t 00:30:00 -J core-coll -o <log> \
#          tracks/core/analysis/collisions/gpu_job.sh <part> <card exe> <baseline card exe>
#   part A  regression (option absent), rate, relaxation
#   part B  reproducibility (layouts, restart), convergence in the time step
#   part C  homogeneous curved metric, relativistic cluster with and without collisions
# The node has four cores in all: a job that asks for all four keeps the second card
# idle, so ask for two.
# Each test is a registered run (runreg.py --card); its card time is its wall time
# inside the allocation.
set -uo pipefail
PART=$1; EXE=$2; BASE=$3
# sbatch runs a copy of this script from its spool directory: the repository is the
# directory the job was submitted from
REPO=${SLURM_SUBMIT_DIR:?submit with sbatch from the root of the worktree}
[[ -f $REPO/tracks/core/analysis/collisions/common.py ]] || { echo "not a worktree: $REPO"; exit 1; }
R=tracks/core/analysis/rng
C=tracks/core/analysis/collisions
cd "$REPO"
nvidia-smi -L
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2

if [[ $PART == A ]]; then
  python3 $R/runreg.py --card --kind production \
    --purpose "P1 regression on one A100: five existing set-ups, executable with the collision operator (option absent) against the baseline built from 94dc093" \
    --input "$BASE" --input "$EXE" --input $R/run_regression.py -- \
    python3 "{repo}/$R/run_regression.py" --base "$BASE" --new "$EXE"
  python3 $R/runreg.py --card --kind production \
    --purpose "P9 (P2 P3 P4 on one A100): collision rate of a Maxwell-Juttner gas, 1e6 particles, 32^3 cells, theta 0.01 to 10, with and without sub-cycling; conservation; null runs" \
    --input "$EXE" --input problems/tests/coll_box.athinput --input $C/run_rate.py -- \
    python3 "{repo}/$C/run_rate.py" "{out}" --exe "$EXE" --nproc 2
  python3 $R/runreg.py --card --kind production \
    --purpose "P9 (P5 P6 on one A100): relaxation of shells and two-temperature starts to Maxwell-Juttner, entropy estimate, 4e5 particles" \
    --input "$EXE" --input problems/tests/coll_box.athinput --input $C/run_relax.py -- \
    python3 "{repo}/$C/run_relax.py" "{out}" --exe "$EXE" --nproc 2
fi
if [[ $PART == B ]]; then
  python3 $R/runreg.py --card --kind production \
    --purpose "P9 (P7 on one A100): reproducibility of collisional runs for 1, 8, 64 MeshBlocks and across a restart, analytic and mesh metric" \
    --input "$EXE" --input problems/tests/coll_box.athinput --input $C/run_repro.py -- \
    python3 "{repo}/$C/run_repro.py" "{out}" --exe "$EXE" --nproc 2
  python3 $R/runreg.py --card --kind production \
    --purpose "P9 (P8a on one A100): convergence of the two-temperature relaxation in the time step, 4e6 particles" \
    --input "$EXE" --input problems/tests/coll_box.athinput --input $C/run_conv_dt.py -- \
    python3 "{repo}/$C/run_conv_dt.py" "{out}" --exe "$EXE" --nproc 2 --n 4000000
fi
if [[ $PART == C ]]; then
  python3 $R/runreg.py --card --kind production \
    --purpose "P10 on one A100: collisions in a static homogeneous curved metric on the mesh" \
    --input "$EXE" --input $C/run_curved_box.py -- \
    python3 "{repo}/$C/run_curved_box.py" "{out}" --exe "$EXE" --nproc 2
  python3 $R/runreg.py --card --kind production \
    --purpose "P11 on one A100: stable relativistic cluster y_c = 0.819 with and without collisions at large Knudsen number" \
    --input "$EXE" --input $C/run_cluster.py -- \
    python3 "{repo}/$C/run_cluster.py" "{out}" --exe "$EXE"
fi
echo "gpu_job part $PART finished"
