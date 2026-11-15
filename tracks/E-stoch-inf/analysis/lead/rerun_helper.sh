#!/bin/bash
# Lead check: rerun the tests of one helper package from the committed scripts into a new
# directory and compare the numbers with the helper's original run outputs.
#   rerun_helper.sh spec|codebase|langevin|noise OUTDIR
# Run from the worktree root (nrpic-run local does this). Original outputs are read from
# /data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/ (read only).
set -u
PKG=$1
D=$2
T=tracks/E-stoch-inf
S=/data/haiyangw/nrpic/scratch/E-stoch-inf
CMP="python3 $T/analysis/lead/compare_json.py"
mkdir -p "$D"
st=0
case "$PKG" in
spec)
  python3 $T/spec/ref/ms_reference.py --out "$D/ms" > "$D/ms.log" 2>&1 || st=1
  python3 $T/spec/ref/norm_test.py --out "$D/norm" --n 64 --seeds 8 > "$D/norm.log" 2>&1 || st=1
  python3 $T/spec/ref/ic_constraint_check.py --out "$D/ic" > "$D/ic.log" 2>&1 || st=1
  python3 $T/spec/ref/make_figures.py --ms "$D/ms" --norm "$D/norm" --out "$D/fig" > "$D/fig.log" 2>&1 || st=1
  O=$S/E-stoch-inf-20261115-122806-ef0d039
  for f in summary.json quadratic.json inflection.json; do $CMP "$O/$f" "$D/ms/$f" >> "$D/compare.txt" 2>&1 || st=1; done
  $CMP $S/E-stoch-inf-20261115-122934-9ac98d8/norm_test.json "$D/norm/norm_test.json" >> "$D/compare.txt" 2>&1 || st=1
  $CMP $S/E-stoch-inf-20261115-123146-82d2fd4/ic_check.json "$D/ic/ic_check.json" >> "$D/compare.txt" 2>&1 || st=1
  ;;
codebase)
  R=$T/codebase/ref
  O=$S/E-stoch-inf-20261115-123936-b2ec5c7
  (cd $R && python3 d1_memory.py $S/E-stoch-inf-20261115-122727-a1c2237 "$D" > "$D/d1.log" 2>&1) || st=1
  (cd $R && python3 d4_stages_window.py "$D" > "$D/d4.log" 2>&1) || st=1
  (cd $R && python3 d3_momentum.py "$D" > "$D/d3.log" 2>&1) || st=1
  (cd $R && python3 d2_synthesis.py "$D" > "$D/d2.log" 2>&1) || st=1
  (cd $R && python3 cost.py "$D" "$D/d1.json" "$D/d2.json" > "$D/cost.log" 2>&1) || st=1
  for f in d1.json d2.json d3.json d4.json cost.json; do $CMP "$O/$f" "$D/$f" --ignore wall >> "$D/compare.txt" 2>&1 || st=1; done
  ;;
langevin)
  # V2 in full (117 s on 8 cores originally); the quadratic reference with 1e5 instead of
  # 1e6 realisations (different seeds; statistical comparison in compare.txt)
  mkdir -p "$D/v2" "$D/refq"
  RUN_DIR="$D/v2" RUN_ID=lead-rerun NRPIC_CORES=8 python3 $T/langevin/scripts/v2_quadratic.py > "$D/v2.log" 2>&1 || st=1
  RUN_DIR="$D/refq" RUN_ID=lead-rerun NRPIC_CORES=8 python3 $T/langevin/scripts/ref_spec.py quadratic 100000 > "$D/refq.log" 2>&1 || st=1
  $CMP $S/E-stoch-inf-20261115-125658-e3eaef3/v2_quadratic.json "$D/v2/v2_quadratic.json" >> "$D/compare.txt" 2>&1 || st=1
  $CMP $S/E-stoch-inf-20261115-130139-176cdd6/ref_quadratic.json "$D/refq/ref_quadratic.json" --stat >> "$D/compare.txt" 2>&1 || st=1
  ;;
noise)
  N=$T/noise
  mkdir -p "$D/twin" "$D/check_twin" "$D/count" "$D/selftest" "$D/dump" "$D/reader"
  git show core/rng:python/nrpic/rng.py > "$D/twin/rng.py"
  python3 $N/ref/check_twin.py --twin "$D/twin/rng.py" --out "$D/check_twin" > "$D/check_twin.log" 2>&1 || st=1
  python3 $N/ref/count_draws.py --out "$D/count" > "$D/count.log" 2>&1 || st=1
  python3 $N/validate/selftest.py --out "$D/selftest" > "$D/selftest.log" 2>&1 || st=1
  python3 $N/validate/dump_selftest.py --out "$D/dump" > "$D/dump.log" 2>&1 || st=1
  python3 $N/validate/reader_test.py --athena /data/haiyangw/nrpic/.work/build_cpu_c1/src/athena \
      --input $N/validate/inputs/reader_test.athinput --out "$D/reader" > "$D/reader.log" 2>&1 || st=1
  $CMP $S/E-stoch-inf-20261115-125255-fcdcbdc/check_twin.json "$D/check_twin/check_twin.json" >> "$D/compare.txt" 2>&1 || st=1
  $CMP $S/E-stoch-inf-20261115-132950-16a0168/selftest.json "$D/selftest/selftest.json" --ignore wall >> "$D/compare.txt" 2>&1 || st=1
  $CMP $S/E-stoch-inf-20261115-133731-2031735/dump_selftest.json "$D/dump/dump_selftest.json" >> "$D/compare.txt" 2>&1 || st=1
  ;;
*)
  echo "unknown package $PKG"; exit 2;;
esac
echo "exit $st" >> "$D/compare.txt"
cat "$D/compare.txt"
exit $st
