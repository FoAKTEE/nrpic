#!/bin/bash
# Card job of the initial-data solver tests (T5): the cases named in CASES with the card
# executable EXE (a copy of the build, so that a rebuild does not change what runs),
# each registered by run_tests.py under the name <case>_card.
# Submit from the worktree:
#   sbatch --export=ALL,EXE=<athena_gpu>,CASES=<a,b,...> tracks/core/analysis/idsolve/card_job.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH -t 00:20:00
#SBATCH -J core-ids
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/idsolve/slurm/card-%j.out
WT=/data/haiyangw/nrpic/wt/core-idsolve
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
date -u +"start %Y-%m-%dT%H:%M:%SZ"
.venv/bin/python tracks/core/analysis/idsolve/run_tests.py --exe "$EXE" --only "$CASES" \
    --suffix _card --jobs 1 --runs tracks/core/analysis/idsolve/runs_card.json
date -u +"end %Y-%m-%dT%H:%M:%SZ"
echo "card_job finished"
