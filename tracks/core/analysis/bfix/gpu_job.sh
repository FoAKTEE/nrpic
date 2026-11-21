#!/bin/bash
# Card job of work package bfix: test T4 (tracks/core/analysis/bfix/t4_card.py) as one
# registered run on one A100. Submit from the worktree after the processor run of T3:
#   sbatch --export=ALL,T3DIR=<output dir of T3>,IC256=<dir of the 256x256x16 data> \
#       tracks/core/analysis/bfix/gpu_job.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH -t 00:30:00
#SBATCH -J core-bfix
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/bfix/slurm-%j.out
WT=/data/haiyangw/nrpic/wt/core-bfix
NEW=$WT/.work/exe/athena_gpu_w1
BASE=/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena
export OMP_NUM_THREADS=2
nvidia-smi -L
cd "$WT" || exit 1
"$WT/.venv/bin/python" tracks/core/tools/run_registered.py \
  --purpose "T4: new options on a card (job $SLURM_JOB_ID): oblique wave N=16..128, byte regression of three set-ups without deposit against the release card executable, thin boxes and jitter of T3, thin box 256x256x16" \
  --kind scouting --cores 2 --card-hours 0.5 --tag T4 \
  --input "$NEW" --input "$BASE" --input "$WT/problems/tests/lw_oblique.athinput" \
  --input "$WT/problems/cosmo/east.athinput" --input "$IC256/particles.nrp" \
  --input "$IC256/fields.bin" \
  -- "$WT/.venv/bin/python" "$WT/tracks/core/analysis/bfix/t4_card.py" --exe-new "$NEW" \
     --exe-base "$BASE" --t3-dir "$T3DIR" --ic256 "$IC256" --out .
echo "gpu_job finished"
