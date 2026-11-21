#!/bin/bash
# Card check of work package clump: byte regression of the card executable on set-ups
# without deposit, and the smeared curvature on the card against the processor runs
# (tracks/core/analysis/clump/card_check.py).  A few minutes of one A100.
#   sbatch tracks/core/analysis/clump/card_check_job.sh <T1 run id> <T3 run id>
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH -t 00:12:00
#SBATCH -J core-clump
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/clump/slurm/card_check-%j.out
WT=/data/haiyangw/nrpic/wt/core-clump
B=/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena
N=$WT/.work/build_gpu/src/athena
PY=$WT/.venv/bin/python
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
$PY tracks/core/analysis/rng/runreg.py --card --kind scouting \
  --purpose "Test G of JOURNAL-clump.md: card executable of core/clump-curvature, byte regression without deposit against build_gpu_v03 and the smeared curvature against the processor runs $1, $2 (job $SLURM_JOB_ID)" \
  --input $B --input $N --input problems/tests/clump_static.athinput \
  -- $PY {repo}/tracks/core/analysis/clump/card_check.py --base $B --new $N --t1 "$1" --t3 "$2" --out {out}
echo "card_check_job finished"
