#!/usr/bin/env python3
"""Check of the extraction factor of R^NR (SPEC 9 E6: Phi_k = (a^2 X_k - 1)/2
+ (1/4) k_i k_j (gt_ij - delta_ij)/k^2, the corrected factors of arXiv:2610.32592
appendix.tex:513-522; [JUDGEMENT: hand derivation] in SPEC) on the last dump of a run
with the metric: D_n with the factor 1/4, without the gt term, with 1/2 and with the
sign flipped.  The factor that the evolution satisfies is the one with the smallest D.

    extraction_check.py --run DIR --nmesh N --nmax2 M --modefile F --out DIR
"""
import argparse
import json
import os

import numpy as np

import ladder_lib as LL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--nmesh", type=int, required=True)
    ap.add_argument("--nmax2", type=int, required=True)
    ap.add_argument("--modefile", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    f = LL.dump_list(a.run)[-1]
    h, fl = LL.read_dump(f, LL.CURV_VARS)
    m = LL.Modes(a.nmesh, a.nmax2)
    al = m.alpha()
    ref = LL.reference_for(m, a.modefile, h["time"] + 0.1, t_eval=[h["time"]])
    rk, _ = ref.modes(h["time"])
    w = ref.window(h["time"], np.sqrt(m.shell_n2 * 1.0))
    lin = LL.L_BOX**-1.5 * (w * rk)[m.shell_of] * al
    r, an, _ = LL.curvature(m, fl)
    sel = m.n2 <= a.nmax2 / 4
    res = dict(run=a.run, dump=f, time=h["time"], cases={})
    for lab, x in (("factor 1/4 (SPEC E6)", r), ("without the gt term", r - an),
                   ("factor 1/2", r + an), ("factor -1/4", r - 2 * an)):
        d = np.abs(x / lin - 1)
        res["cases"][lab] = dict(max_D_half=float(d[sel].max()), max_D_all=float(d.max()))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "extraction_check.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
