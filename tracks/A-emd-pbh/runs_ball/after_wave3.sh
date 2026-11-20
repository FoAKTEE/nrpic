#!/usr/bin/env bash
# Registered analyses of wave 3 (JOURNAL entries 13 and 14) of the package runs_ball:
#   bash tracks/A-emd-pbh/runs_ball/after_wave3.sh turnaround <analysis run id of after_runs3.sh runs3>
#       turnaround.py (entry 13) on SR-1 and SR-2 of wave 2 (dx = M, M/2, M/4) and SR-1L of job
#       A-20261119-144419-13d5601 (dx = M, M/2, M/4), the synthetic test T0 and the SR-1
#       breakdown criteria of the three SR-1 runs.
#   bash tracks/A-emd-pbh/runs_ball/after_wave3.sh box <analysis run id of after_runs3.sh runs3>
#       closes the fixed-box card run A-20261120-223310-a9ce31a (entry 14), compare.py on its
#       three runs, turnaround.py on every SR-1L run (fixed box and L = 64).
set -euo pipefail
PART=$1
A3=$2
cd /data/haiyangw/nrpic/wt/A-emd-pbh
S=/data/haiyangw/nrpic/scratch/A-emd-pbh
C=tracks/A-emd-pbh/runs_ball
PY=.venv/bin/python
P2=$S/A-emd-pbh-20261115-153719-91b03d1          # 2t, h = M/2 lattice
P4=$S/A-emd-pbh-20261115-164353-96e301d          # 2t, h = M/4 lattice
A12=$S/A-emd-pbh-20261115-163659-4dbacd0         # wave-2 analysis of SR-1/SR-2 at dx = M, M/2
A4=$S/A-20261115-182657-53da696                  # wave-2 analysis of SR-1/SR-2 at dx = M/4
BOX=A-20261120-223310-a9ce31a                    # fixed-box SR-1L card run (entry 14)
if [ "$PART" = turnaround ]; then
  harness/bin/nrpic-run submit --kind scouting --gate G2 --package $C --launcher local --cores 2 --wall 01:00:00 \
    --parent $A3 --parent A-emd-pbh-20261115-163659-4dbacd0 --parent A-20261115-182657-53da696 \
    --parent A-emd-pbh-20261115-153843-7172b66 --parent A-emd-pbh-20261115-155056-ec1b816 --parent A-emd-pbh-20261115-164539-0b18e84 \
    --purpose "window-independent turnaround estimators (runs_ball/JOURNAL.md entry 13, prediction T) on SR-1, SR-2 (wave 2) and SR-1L (dx = M, M/2, M/4); synthetic test T0; SR-1 breakdown criteria" -- \
    bash -c "export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2; O=\$NRPIC_RUN_DIR; \
      $PY $C/turnaround.py --prep $P2 --out \$O --figdir $C/figs --synthetic \
        --run $A12:sr1_n128:1.0:sr1 --run $A12:sr1_n256:0.5:sr1 --run $A4:sr1_n256L32:0.25:sr1 \
        --run $A12:sr2_n128:1.0:sr2 --run $A12:sr2_n256:0.5:sr2 --run $A4:sr2_n256L32:0.25:sr2 \
        --run $S/$A3:sr1l_n128:1.0:leak --run $S/$A3:sr1l_n256:0.5:leak --run $S/$A3:sr1l_n256L32:0.25:leak \
        --breakdown $S/A-emd-pbh-20261115-153843-7172b66/sr1:sr1_n256 \
        --breakdown $S/A-emd-pbh-20261115-155056-ec1b816/sr1_n128:sr1_n128 \
        --breakdown $S/A-emd-pbh-20261115-164539-0b18e84/sr1_n256_L32:sr1_n256L32 > \$O/turnaround.log 2>&1"
fi
if [ "$PART" = box ]; then
  harness/bin/nrpic-run finish $BOX || true
  harness/bin/nrpic-run submit --kind scouting --gate G2 --package $C --launcher local --cores 4 --wall 01:00:00 \
    --parent $BOX --parent $A3 --parent A-emd-pbh-20261115-164353-96e301d --parent A-emd-pbh-20261115-153719-91b03d1 \
    --purpose "analysis of SR-1L on the fixed box [-32,32]^3 (dx = M, M/2; lattices h = M/4, M/2) with sr1l_n256L32, and the turnaround estimators on every SR-1L run (runs_ball/JOURNAL.md entry 14, prediction F)" -- \
    bash -c "export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4; O=\$NRPIC_RUN_DIR; R=$S/$BOX; \
      $PY $C/compare.py --prep $P4 --seg \$R/sr1lb_n64 --gauge leak --leak 8 --dx 1.0 --label sr1lb_n64 --out \$O --figdir $C/figs > \$O/sr1lb_n64.log 2>&1; \
      $PY $C/compare.py --prep $P4 --seg \$R/sr1lb_n128 --gauge leak --leak 8 --dx 0.5 --label sr1lb_n128 --out \$O --figdir $C/figs > \$O/sr1lb_n128.log 2>&1; \
      $PY $C/compare.py --prep $P2 --seg \$R/sr1lb_n128h2 --gauge leak --leak 8 --dx 0.5 --label sr1lb_n128h2 --out \$O --figdir $C/figs > \$O/sr1lb_n128h2.log 2>&1; \
      $PY $C/summary3.py --prep2t $P2 \
        --sr \$O:sr1lb_n64:1.0:leak --sr \$O:sr1lb_n128:0.5:leak --sr $S/$A3:sr1l_n256L32:0.25:leak \
        --out \$O > \$O/summary_box.log 2>&1; \
      mkdir -p \$O/ta; $PY $C/turnaround.py --prep $P2 --out \$O/ta --figdir $C/figs --tag _box \
        --run \$O:sr1lb_n64:1.0:leak --run \$O:sr1lb_n128:0.5:leak --run $S/$A3:sr1l_n256L32:0.25:leak \
        --run \$O:sr1lb_n128h2:0.5:leak --run $S/$A3:sr1l_n256:0.5:leak --run $S/$A3:sr1l_n128:1.0:leak > \$O/ta/turnaround.log 2>&1"
fi
