#!/usr/bin/env bash
# Registered analysis of the dx = M/4 runs (JOURNAL entry 4) once their Slurm jobs have
# finished and their manifests are closed (runreg.py finish), and the three-resolution
# summary together with the dx = M and M/2 analyses (run A-emd-pbh-20261115-163659-4dbacd0).
set -euo pipefail
cd /data/haiyangw/nrpic/wt/A-emd-pbh
S=/data/haiyangw/nrpic/scratch/A-emd-pbh
P2=$S/A-emd-pbh-20261115-153719-91b03d1          # prep, h = M/2 lattice
P4=$S/A-emd-pbh-20261115-164353-96e301d          # prep, h = M/4 lattice
A12=$S/A-emd-pbh-20261115-163659-4dbacd0         # analysis of dx = M, M/2
Q1=$S/A-emd-pbh-20261115-164539-0b18e84/sr1_n256_L32
Q2=$S/A-emd-pbh-20261115-164541-0b18e84/sr2_n256_L32
C=tracks/A-emd-pbh/runs_ball
PY=.venv/bin/python
$PY $C/runreg.py local --cores 4 \
  --parent A-emd-pbh-20261115-164539-0b18e84 --parent A-emd-pbh-20261115-164541-0b18e84 \
  --parent A-emd-pbh-20261115-163659-4dbacd0 --parent A-emd-pbh-20261115-164353-96e301d \
  --input $C/compare.py --input $C/fields.py --input $C/summary.py --input $C/common.py \
  --purpose "analysis of SR-1/SR-2 at dx = M/4 to t = 20 and three-resolution summary (prediction R)" -- \
  bash -c "$PY $C/compare.py --prep $P4 --seg $Q1 --gauge sr1 --dx 0.25 --label sr1_n256L32 --out \$NRPIC_RUN_DIR --figdir $C/figs && \
           $PY $C/compare.py --prep $P4 --seg $Q2 --gauge sr2 --dx 0.25 --label sr2_n256L32 --out \$NRPIC_RUN_DIR --figdir $C/figs && \
           $PY $C/fields.py --seg $Q1 --label sr1_n256L32 --out \$NRPIC_RUN_DIR --figdir $C/figs --L 32 && \
           $PY $C/fields.py --seg $Q2 --label sr2_n256L32 --out \$NRPIC_RUN_DIR --figdir $C/figs --L 32 && \
           $PY $C/summary.py --prep $P2 --run $A12:sr1_n128:1.0 --run $A12:sr1_n256:0.5 --run \$NRPIC_RUN_DIR:sr1_n256L32:0.25 \
               --run $A12:sr2_n128:1.0 --run $A12:sr2_n256:0.5 --run \$NRPIC_RUN_DIR:sr2_n256L32:0.25 \
               --out \$NRPIC_RUN_DIR --figdir $C/figs"
