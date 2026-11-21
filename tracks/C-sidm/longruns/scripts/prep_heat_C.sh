#!/usr/bin/env bash
# Particle files and batch lists of the conductivity series against cell size and step
# (heat/README.md "Open, for G2"; predictions H.1-H.4 in tracks/C-sidm/JOURNAL.md, batch 5).
# Run from the worktree root through nrpic-run (output under $NRPIC_RUN_DIR):
#   C1: theta 0.003, k lambda 0.2, eps 0.2, 4e6, seeds 6 and 7: dx = lambda/4 (base),
#       lambda/2, lambda/8, and lambda/8 with dt = 0.05 t_coll           (8 cases)
#   C2: the same at k lambda 0.1, seed 6: dx = lambda/4, lambda/2, lambda/8 (3 cases)
# Transverse box and cells fixed as in card A (16 cells of lambda/4).
set -euo pipefail
R=tracks/C-sidm/heat/scripts/run_mode.py
L1=tracks/C-sidm/longruns/inputs/heat_C1.list
L2=tracks/C-sidm/longruns/inputs/heat_C2.list
LY=$(python3 -c "import math; print(16*2*math.pi/0.2/128)")
python3 $R prep --theta 0.003 --kl 0.2 --eps 0.2 --seeds 6 7 --n 4000000 --nsnap 16 --tag TC_ \
  --nt-fixed 16 --ly-fixed "$LY" --list $L1 \
  --variants '[{}, {"dx_frac": 0.5}, {"dx_frac": 0.125}, {"dx_frac": 0.125, "dt_frac": 0.05}]'
python3 $R prep --theta 0.003 --kl 0.1 --eps 0.2 --seeds 6 --n 4000000 --nsnap 16 --tag TC_ \
  --nt-fixed 16 --ly-fixed "$LY" --list $L2 \
  --variants '[{}, {"dx_frac": 0.5}, {"dx_frac": 0.125}]'
wc -l $L1 $L2
