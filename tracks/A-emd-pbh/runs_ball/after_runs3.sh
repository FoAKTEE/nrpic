#!/usr/bin/env bash
# Registered analysis of the wave-2b card runs of this package (JOURNAL entry 7) once Slurm
# job of run A-20261119-144419-13d5601 has finished: close the card run, then compare.py on
# each of the six runs, fields.py on the finest, and summary3.py (SR-1L against SR-1/SR-2
# of wave 2; BH-1 over three resolutions). Run from anywhere:
#   bash tracks/A-emd-pbh/runs_ball/after_runs3.sh [all|runs3|bh_smr]
# The optional part (default all) runs only the analysis of job A-20261119-144419-13d5601
# (runs3) or only that of BH-1R (bh_smr). The first part copies its figures into figs/, which
# leaves the package dirty, and nrpic-run submit refuses a dirty package: run "runs3", commit
# figs/, then run "bh_smr" (wave 3, JOURNAL entry 11).
set -euo pipefail
PART=${1:-all}
cd /data/haiyangw/nrpic/wt/A-emd-pbh
S=/data/haiyangw/nrpic/scratch/A-emd-pbh
RUN=A-20261119-144419-13d5601
R=$S/$RUN
P2=$S/A-emd-pbh-20261115-153719-91b03d1          # 2t, h = M/2 lattice (dx = M, M/2)
P4=$S/A-emd-pbh-20261115-164353-96e301d          # 2t, h = M/4 lattice (dx = M/4)
P3=$S/A-20261119-143524-334e553                  # data set 3
A12=$S/A-emd-pbh-20261115-163659-4dbacd0         # wave-2 analysis of SR-1/SR-2 at dx = M, M/2
A4=$S/A-20261115-182657-53da696                  # wave-2 analysis of SR-1/SR-2 at dx = M/4
C=tracks/A-emd-pbh/runs_ball
PY=.venv/bin/python
if [ "$PART" = all ] || [ "$PART" = runs3 ]; then
harness/bin/nrpic-run status $RUN | tail -3
harness/bin/nrpic-run finish $RUN || true
harness/bin/nrpic-run submit --kind scouting --gate G2 --package $C --launcher local --cores 4 --wall 01:00:00 \
  --parent $RUN --parent A-20261119-143524-334e553 --parent A-20261119-143309-1cc423f \
  --purpose "analysis of SR-1L (2t, relaxed lapse, dx = M, M/2, M/4) and BH-1 (data set 3, dx = M/4, M/6, M/8) against the exact solution; predictions S and B of runs_ball/JOURNAL.md entry 7" -- \
  bash -c "export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4; O=\$NRPIC_RUN_DIR; \
    $PY $C/compare.py --prep $P2 --seg $R/sr1l_n256 --gauge leak --leak 8 --dx 0.5 --label sr1l_n256 --out \$O --figdir $C/figs > \$O/sr1l_n256.log 2>&1; \
    $PY $C/compare.py --prep $P2 --seg $R/sr1l_n128 --gauge leak --leak 8 --dx 1.0 --label sr1l_n128 --out \$O --figdir $C/figs > \$O/sr1l_n128.log 2>&1; \
    $PY $C/compare.py --prep $P4 --seg $R/sr1l_n256L32 --gauge leak --leak 8 --dx 0.25 --label sr1l_n256L32 --out \$O --figdir $C/figs > \$O/sr1l_n256L32.log 2>&1; \
    $PY $C/compare.py --prep $P3/lat68 --seg $R/bh_n256 --gauge leak --leak 8 --dx 0.125 --label bh_n256 --out \$O --figdir $C/figs > \$O/bh_n256.log 2>&1; \
    $PY $C/compare.py --prep $P3/lat51 --seg $R/bh_n192 --gauge leak --leak 8 --dx 0.16666666666666666 --label bh_n192 --out \$O --figdir $C/figs > \$O/bh_n192.log 2>&1; \
    $PY $C/compare.py --prep $P3/lat34 --seg $R/bh_n128 --gauge leak --leak 8 --dx 0.25 --label bh_n128 --out \$O --figdir $C/figs > \$O/bh_n128.log 2>&1; \
    $PY $C/fields.py --seg $R/sr1l_n256 --label sr1l_n256 --out \$O --figdir $C/figs > \$O/f1.log 2>&1; \
    $PY $C/fields.py --seg $R/bh_n256 --label bh_n256 --out \$O --figdir $C/figs --L 16 --half 8 > \$O/f2.log 2>&1; \
    $PY $C/summary3.py --prep2t $P2 --prep3 $P3 \
      --sr $A12:sr1_n128:1.0:sr1 --sr $A12:sr1_n256:0.5:sr1 --sr $A4:sr1_n256L32:0.25:sr1 \
      --sr $A12:sr2_n128:1.0:sr2 --sr $A12:sr2_n256:0.5:sr2 --sr $A4:sr2_n256L32:0.25:sr2 \
      --sr \$O:sr1l_n128:1.0:leak --sr \$O:sr1l_n256:0.5:leak --sr \$O:sr1l_n256L32:0.25:leak \
      --bh \$O:bh_n128:0.25 --bh \$O:bh_n192:0.16666666666666666 --bh \$O:bh_n256:0.125 \
      --out \$O --figdir $C/figs > \$O/summary3.log 2>&1"
fi

# BH-1R (one refined level, card run A-20261119-164634-f1fe887) once its job has finished
RUN2=A-20261119-164634-f1fe887
P6=$S/A-20261119-164113-74f0f32                  # data set 3, lattice h = M/16
if [ -d $S/$RUN2/bh_smr ] && { [ "$PART" = all ] || [ "$PART" = bh_smr ]; }; then
  harness/bin/nrpic-run finish $RUN2 || true
  harness/bin/nrpic-run submit --kind scouting --gate G2 --package $C --launcher local --cores 4 --wall 00:40:00 \
    --parent $RUN2 --parent A-20261119-164113-74f0f32 \
    --purpose "analysis of BH-1R (data set 3, cells M/16 inside [-4,4]^3) against the exact solution; prediction of runs_ball/JOURNAL.md entry 10" -- \
    bash -c "export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4; O=\$NRPIC_RUN_DIR; \
      $PY $C/compare.py --prep $P6/lat136 --seg $S/$RUN2/bh_smr --gauge leak --leak 8 --dx 0.125 --dx-fine 0.0625 --fine-half 4.0 \
          --label bh_smr --out \$O --figdir $C/figs > \$O/bh_smr.log 2>&1; \
      $PY $C/fields.py --seg $S/$RUN2/bh_smr --label bh_smr --out \$O --figdir $C/figs --L 16 --half 8 > \$O/f.log 2>&1"
fi
