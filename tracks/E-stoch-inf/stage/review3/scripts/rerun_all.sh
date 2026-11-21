#!/bin/bash
# Lead review of wave 3 (E-stoch-inf, batch 2a): rerun the final analysis steps of the
# packages g1verify and ladder from their registered outputs, unchanged, into OUT; then
# compare every JSON leaf with the registered run's output and with the copy committed in
# the package (compare_json.py).  Inputs are the registered run directories named below.
#
#   bash rerun_all.sh OUT
set -e
OUT="$1"
S=/data/haiyangw/nrpic/scratch/E-stoch-inf
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
T=$WT/tracks/E-stoch-inf
mkdir -p "$OUT"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MPLBACKEND=Agg
cd "$WT"
date -u
# --- g1verify (commands as in the manifests of the runs named in each comment)
mkdir -p "$OUT/g1"
# E-20261121-030207-fb6f090
python3 $T/g1verify/scripts/v123.py "$OUT/g1/v123" $S/E-20261120-223154-d42de1a $S/E-20261121-025750-d1b6139
# E-20261121-031951-82984f8
python3 $T/g1verify/scripts/v45.py "$OUT/g1/v45" $S/E-20261121-030657-c1afe38
# E-20261121-032413-0672bf9 (the addendum part of make_figs.sh)
python3 $T/g1verify/scripts/v45_addendum.py "$OUT/g1/v45add" $S/E-20261121-031951-82984f8
# E-20261121-030522-c6907b6, E-20261121-030520-5a23d64
python3 $T/g1verify/scripts/v6.py "$OUT/g1/v6"
python3 $T/g1verify/scripts/v7.py "$OUT/g1/v7"
# E-20261121-031251-c48670d
python3 $T/g1verify/scripts/v7_g1exe.py "$OUT/g1/v7g" $S/E-20261121-031049-27cdc06
date -u
# --- ladder
cd $T/ladder/scripts
# E-20261121-025932-7a21f34 (item a)
R="$OUT/ladder/final2"; mkdir -p "$R"
cp $S/E-20261120-223038-684821a/res/pair_*.json "$R"/
python3 verdicts.py --res "$R" ../results/final --rundirs $S/E-20261115-172636-ce98836 $S/E-20261115-173719-e810503 $S/E-20261115-172618-f948386 $S/E-20261115-172629-312a82c $S/E-20261115-172625-416fec0 --out "$R/summary.json"
python3 make_figures.py --res "$R" ../results/final $S/E-20261115-194633-9e04ed8/res --out "$OUT/ladder/final2_fig" --only fig_a4
# E-20261121-034414-bfd0285 (item b)
python3 a6_analysis.py --run $S/E-20261121-025643-02526ff --nmesh 64 --nmax2 256 --modefile $T/ladder/inputs/modes_n256.txt --out "$OUT/ladder/a6_64"
# E-20261121-034645-02a463e (item c, card)
python3 l5_analysis.py --run $S/E-20261121-025643-02526ff --out "$OUT/ladder/l5card"
# E-20261121-040015-436a615 (item c, step/mesh)
python3 l5_scaling.py --set A=$S/E-20261121-034950-06f01f9/A --set B=$S/E-20261121-034950-06f01f9/B --set C=$S/E-20261121-025643-02526ff --out "$OUT/ladder/l5scaling"
date -u
# E-20261121-045105-f797ebb (item d): extract reads the 18 dumps of P256s2 (50 GB)
export OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3
R="$OUT/ladder/seed2"; mkdir -p "$R"
python3 ladder_analysis.py extract $S/E-20261121-032828-fe18c5f/P256s2 --nmesh 256 --nmax2 4096 --modefile $T/ladder/inputs/modes_n4096.txt --seed 20261120 --out "$R/P256s2.npz"
python3 ladder_analysis.py judge "$R/P256s2.npz" --out "$R/P256s2_judge.json"
python3 seed2_compare.py --old-res $S/E-20261115-194633-9e04ed8/res --new-res "$R" --old P256 --new P256s2 --out "$OUT/ladder/seed2cmp"
date -u
# --- comparison
cd "$WT"
python3 $T/stage/review3/scripts/compare_json.py --out "$OUT/compare" \
  g1.v123="$OUT/g1/v123/v123.json|$S/E-20261121-030207-fb6f090/v123.json|$T/g1verify/results/v123.json" \
  g1.v45="$OUT/g1/v45/v45.json|$S/E-20261121-031951-82984f8/v45.json|$T/g1verify/results/v45.json" \
  g1.v45add="$OUT/g1/v45add/v45_addendum.json|$S/E-20261121-032413-0672bf9/v45_addendum.json|$T/g1verify/results/v45_addendum.json" \
  g1.v6="$OUT/g1/v6/v6.json|$S/E-20261121-030522-c6907b6/v6.json|$T/g1verify/results/v6.json" \
  g1.v7="$OUT/g1/v7/v7.json|$S/E-20261121-030520-5a23d64/v7.json|$T/g1verify/results/v7.json" \
  g1.v7g="$OUT/g1/v7g/v7_g1exe.json|$S/E-20261121-031251-c48670d/v7_g1exe.json|$T/g1verify/results/v7_g1exe.json" \
  ladder.final2="$OUT/ladder/final2/summary.json|$S/E-20261121-025932-7a21f34/res/summary.json|$T/ladder/results/final2/summary.json" \
  ladder.a6_64="$OUT/ladder/a6_64/a6.json|$S/E-20261121-034414-bfd0285/a6.json|$T/ladder/results/a6_64/a6.json" \
  ladder.l5card="$OUT/ladder/l5card/l5.json|$S/E-20261121-034645-02a463e/card/l5.json|$T/ladder/results/l5/card/l5.json" \
  ladder.l5scaling="$OUT/ladder/l5scaling/l5_scaling.json|$S/E-20261121-040015-436a615/l5_scaling.json|$T/ladder/results/l5/l5_scaling.json" \
  ladder.seed2judge="$OUT/ladder/seed2/P256s2_judge.json|$S/E-20261121-045105-f797ebb/res/P256s2_judge.json|$T/ladder/results/seed2/P256s2_judge.json" \
  ladder.seed2cmp="$OUT/ladder/seed2cmp/seed2.json|$S/E-20261121-045105-f797ebb/compare/seed2.json|$T/ladder/results/seed2/seed2.json"
date -u
