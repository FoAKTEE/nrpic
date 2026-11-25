#!/usr/bin/env bash
# Check of the published directory scratch/core/exe/core_clump-table: checksums; the
# generator run from its place; examples/clump_table_static.athinput at 32 cells with the
# published processor executable (v = 0.3, curvature, correction, comoving shift); its two
# history files byte by byte against the same case of test M1
# (core-20261121-130253-260f4e3/tb/q0.3_n32_corr). Run through nrpic-run, one core.
set -eu
out=${NRPIC_RUN_DIR:?run through nrpic-run}
P=/data/haiyangw/nrpic/scratch/core/exe/core_clump-table
ref=/data/haiyangw/nrpic/scratch/core/core-20261121-130253-260f4e3/tb/q0.3_n32_corr
( cd "$P" && sha256sum -c SHA256SUMS ) > "$out/sha256.log"
mkdir -p "$out/run"
python3 "$P/generator/problems/ic/make_ic.py" boosted --cluster 0.819,1,0,0,0,0.3,0,0 \
    --sampler quiet --lattice-h 0.25 --prefix cluster --out "$out/run" > "$out/generator.log"
args=$(python3 -c "
import json, sys
p = json.load(open(sys.argv[1]))['athenak']['problem']
print(' '.join('problem/comp0_p%d=%r' % (c, p['comp0_p%d' % c]) for c in (1, 2, 3)))" "$out/run/cluster.json")
cd "$out/run"
# shellcheck disable=SC2086
"$P/athena_cpu" -i "$P/examples/clump_table_static.athinput" -d . mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 \
    particles/particle_file=cluster.nrp $args problem/comp0_corr=table problem/comp0_boost_shift=true \
    > athena.log 2>&1
st=0
for f in clump.z4c.user.hst clump.nrpic.hst; do
  if cmp -s "$f" "$ref/$f"; then echo "$f IDENTICAL"; else echo "$f DIFFERS"; st=1; fi
done | tee "$out/compare.log"
grep -q DIFFERS "$out/compare.log" && st=1
exit $st
