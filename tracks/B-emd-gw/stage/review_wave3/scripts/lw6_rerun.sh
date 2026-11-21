#!/usr/bin/env bash
# Lead review batch 4a, check L6: rerun the registered first_source round-3 analyses
# conv_compare (B-20261121-075302-a9fcc43) and p16_compare 64^3 (B-20261121-085202-b95efda)
# from their registered inputs with the committed scripts, each into its own subdirectory of
# $NRPIC_RUN_DIR, and compare the summary JSON byte for byte and number by number.
set -euo pipefail
S=/data/haiyangw/nrpic/scratch/B-emd-gw
FS=tracks/B-emd-gw/first_source/scripts
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p "$NRPIC_RUN_DIR/conv" "$NRPIC_RUN_DIR/p16"
NRPIC_RUN_DIR="$NRPIC_RUN_DIR/conv" python3 $FS/conv_compare.py \
  e1_p1=$S/B-20261120-223241-f1efd4f/e1_p1_n64.json e1_p8=$S/B-20261115-180834-c77a132/cw_eps1.json \
  e1_p27=$S/B-20261120-223241-f1efd4f/e1_p3_n64.json e1_n128=$S/B-20261120-223236-e213594/e1_p1_n128.json \
  e1_n32=$S/B-20261115-184650-2d155b6/cw_eps1.json e1_rep=$S/B-20261119-155418-80d45af/e1_rep.json > "$NRPIC_RUN_DIR/conv/stdout.txt"
NRPIC_RUN_DIR="$NRPIC_RUN_DIR/p16" python3 $FS/p16_compare.py \
  nw=$S/B-20261121-084959-4c72924/jit0p3_nw.json j3=$S/B-20261119-160530-7bdcb45/jit0p3.json \
  pred_nw=$S/B-20261121-080207-6edafb2/null_prediction.json pred_j3=$S/B-20261119-142733-932e595/null_prediction.json \
  spec_nw=$S/B-20261121-084959-ad6bd72/null_spectrum.json spec_j3=$S/B-20261119-161734-a3a1366/null_spectrum.json \
  kcut=16 shells=16,24,31 > "$NRPIC_RUN_DIR/p16/stdout.txt"
python3 - "$NRPIC_RUN_DIR" <<'PY'
import json, sys, filecmp
out = sys.argv[1]
S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
pairs = {"conv": (f"{out}/conv/conv_summary.json", f"{S}/B-20261121-075302-a9fcc43/conv_summary.json"),
         "p16": (f"{out}/p16/p16_summary.json", f"{S}/B-20261121-085202-b95efda/p16_summary.json")}
def flat(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flat(v, f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flat(v, f"{p}[{i}]")
    else:
        yield p, x
res = {}
for k, (a, b) in pairs.items():
    A, B = dict(flat(json.load(open(a)))), dict(flat(json.load(open(b))))
    num = [p for p in A if isinstance(A[p], (int, float)) and not isinstance(A[p], bool)]
    diff = [p for p in A if A.get(p) != B.get(p)]
    res[k] = {"bytes_equal": filecmp.cmp(a, b, shallow=False), "n_values": len(A), "n_numbers": len(num),
              "keys_equal": sorted(A) == sorted(B), "n_differing": len(diff), "differing": diff[:20]}
json.dump(res, open(f"{out}/lw6_rerun.json", "w"), indent=1)
print(json.dumps(res, indent=1))
PY
