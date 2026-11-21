#!/usr/bin/env bash
# Initial data of work package omp, written to scratch/core/omp/ic/ (made once; the runs
# record the checksum of every file they read):
#   wave32.nrp            plane wave of the Newtonian mode, 32^3 particles
#   box.nrp               two-temperature gas for the collision box, 2e4 particles
#   st/                   monoenergetic cluster y_c = 0.819, 1e5 particles (stratified, seed 1)
#   dav64/                64^3 periodic box of the cosmology extension, two particles per
#                         cell (cosmo/README.md, "A run from start to finish")
#   dnewt/                Newtonian-mode box of Track D's size: 128^3 mesh, 80^3 particles
set -euo pipefail
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
OUT=/data/haiyangw/nrpic/scratch/core/omp/ic
mkdir -p "$OUT"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
cd "$WT"
[[ -f $OUT/wave32.nrp ]] || python3 problems/newton/make_ic.py wave --out "$OUT/wave32.nrp" --n 32
[[ -f $OUT/box.nrp ]] || python3 tracks/core/analysis/collisions/make_box.py "$OUT/box.nrp" twotemp 20000 --theta 0.1 --theta2 0.3
if [[ ! -d $OUT/st ]]; then
  python3 problems/ic/make_ic.py st --yc 0.819 --N 100000 --sampler stratified --seed 1 --out "$OUT/st"
fi
if [[ ! -f $OUT/dav64/particles.nrp ]]; then
  (cd cosmo/ic && python3 make_daverio_c.py --box 704 --cut 220 --n 64 --ppc 2 --seed 1 \
      --shape pcs --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 \
      --out "$OUT/dav64")
fi
[[ -f $OUT/dnewt/wave80.nrp ]] || { mkdir -p "$OUT/dnewt"; \
  python3 problems/newton/make_ic.py wave --out "$OUT/dnewt/wave80.nrp" --n 80; }
ls -la "$OUT" "$OUT"/st "$OUT"/dav64 "$OUT"/dnewt
sha256sum "$OUT"/*.nrp "$OUT"/st/* "$OUT"/dav64/* "$OUT"/dnewt/* > "$OUT/SHA256SUMS"
