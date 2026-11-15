#!/bin/bash
# Card job 3 of the work package "gauge": the Einstein-Straus data with T = 2 M (ES) and
# the collapse of the bound ball with T = 0.5 M (L3), both with a wall-clock limit.
# (Job 1 was submitted with other relaxation times for these two; its tags are listed in
# skip_tags.txt and are not run.)
#   sbatch tracks/core/analysis/gauge/gpu_job3.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH -t 00:22:00
#SBATCH -J core-gauge
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/gauge/gpu_job3-%j.out
WT=/data/haiyangw/nrpic/wt/core-gauge
PY=$WT/.venv/bin/python
G=$WT/tracks/core/analysis/gauge
EXE=/data/haiyangw/nrpic/scratch/core/gauge/exe/athena_gpu_b4430da
SRC=b4430da
IC=/data/haiyangw/nrpic/scratch/core/id/ic_ball
ES=/data/haiyangw/nrpic/scratch/core/gauge/ic_es
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
date
$PY $G/grun.py --gpu --exe $EXE --source-commit $SRC --time 00:20:00 --tag gc-es-leak2 \
  --purpose "Einstein-Straus data of Track D for 30 M, lapse relaxation T = 2 M (test ES)" \
  --inputs $ES/es.nrp $ES/es.tab $ES/es.json $ES/es_reference.csv \
  --athinput $WT/problems/es/es_gauge.athinput particles/particle_file=$ES/es.nrp \
  problem/comp0_file=$ES/es.tab z4c/lapse_leak=0.5 -t 00:08:00
date
NT=$(python3 -c "import json;print(json.load(open('$IC/t2_bound_h0p25.json'))['traj_ntrack'])")
$PY $G/grun.py --gpu --exe $EXE --source-commit $SRC --time 00:20:00 --tag gc-collapse-leak05 \
  --purpose "bound expanding ball through turnaround and collapse to a black hole, new lapse T = 0.5 M (test L3)" \
  --inputs $IC/t2_bound_h0p25.nrp $IC/t2_bound_h0p25.tab $IC/t2_bound_h0p25.json \
  --athinput $WT/problems/ball/ball_collapse.athinput particles/traj_ntrack=$NT \
  particles/particle_file=$IC/t2_bound_h0p25.nrp problem/comp0_file=$IC/t2_bound_h0p25.tab \
  z4c/lapse_leak=2.0 -t 00:10:00
date
echo "gpu_job3 finished"
