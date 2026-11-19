#!/usr/bin/env bash
# Particle files and batch lists of the two card jobs of the heat package (run from the
# worktree root through nrpic-run; output under $NRPIC_RUN_DIR).
#   A: T8 variants (theta 0.003, k lambda 0.2, eps 0.2, 4e6, transverse 16 x 16 cells of
#      lambda/4), then T7 at eps 0.05 (theta 0.003, k lambda 0.4 and 0.2, two seeds, 4e6)
#   B: T7 at eps 0.2: theta 0.1 and 1 (k lambda 0.4, 0.2, 0.1; seeds 1, 2; 2e6), and
#      theta 0.003 (k lambda 0.4, 0.2, 0.1; seed 5; 4e6)
set -euo pipefail
R=tracks/C-sidm/heat/scripts/run_mode.py
A=tracks/C-sidm/heat/inputs/card_A.list
B=tracks/C-sidm/heat/inputs/card_B.list
LY=$(python3 -c "import math; print(16*2*math.pi/0.2/128)")
python3 $R prep --theta 0.003 --kl 0.2 --eps 0.2 --seeds 1 --n 4000000 --nsnap 16 --tag T8_ \
  --nt-fixed 16 --ly-fixed "$LY" --list $A \
  --variants '[{}, {"dt_frac": 0.2}, {"dt_frac": 0.05}, {"pmax": 0.2}, {"pmax": 0.05}, {"dx_frac": 0.5}, {"dx_frac": 0.125}]'
python3 $R prep --theta 0.003 --kl 0.4 0.2 --eps 0.05 --seeds 1 2 --n 4000000 --nsnap 16 --tag T7c_ --list $A --append
python3 $R prep --theta 0.1 --kl 0.4 0.2 0.1 --eps 0.2 --seeds 1 2 --n 2000000 --nsnap 16 --tag T7c_ --list $B
python3 $R prep --theta 1.0 --kl 0.4 0.2 0.1 --eps 0.2 --seeds 1 2 --n 2000000 --nsnap 16 --tag T7c_ --list $B --append
python3 $R prep --theta 0.003 --kl 0.4 0.2 0.1 --eps 0.2 --seeds 5 --n 4000000 --nsnap 16 --tag T7c_ --list $B --append
wc -l $A $B
