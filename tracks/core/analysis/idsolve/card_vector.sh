#!/bin/bash
# Card job of the vector equation (test V4): the moving Gaussian at 64 cells, mode code,
# with the card executable EXE (a copy of the build), registered by run_registered.py.
# Submit from the worktree:
#   sbatch --export=ALL,EXE=<athena_gpu> tracks/core/analysis/idsolve/card_vector.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH -t 00:15:00
#SBATCH -J core-idv
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/idsolve/slurm/card-vec-%j.out
WT=/data/haiyangw/nrpic/wt/core-idsolve
IC=/data/haiyangw/nrpic/scratch/core/idsolve_ic
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
date -u +"start %Y-%m-%dT%H:%M:%SZ"
.venv/bin/python tracks/core/tools/run_registered.py \
    --purpose "initial-data solver, test V4: moving Gaussian with the vector equation on a card (gboost_code_n64)" \
    --tag idsolve-gboost_code_n64_card --card-hours 0.01 \
    --input problems/idsolve/gaussian_boost.athinput --input $IC/gauss_h0p25_u0p1.nrp -- \
    "$EXE" -i gaussian_boost.athinput mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 \
    meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 particles/id_residual=code \
    particles/particle_file=gauss_h0p25_u0p1.nrp
date -u +"end %Y-%m-%dT%H:%M:%SZ"
echo "card_vector finished"
