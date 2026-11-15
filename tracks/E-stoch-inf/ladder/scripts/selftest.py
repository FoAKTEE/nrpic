#!/usr/bin/env python3
"""Self-test of ladder_lib on dumps that already exist (core's run
core-20261115-160134-3fde433, 32^3, nmax2 = 64, dump_metric = true), before the ladder
runs are analysed:
  T1 this package's reader equals core's reader (python/nrpic/scalar_field.py of
     core/scalar-2, extracted read-only) field by field, bit for bit;
  T2 at t = 0 the extracted R^NR_n equals s L^-3/2 W R alpha_n of this package's
     reference for the modes with W > 1/2 (the slice is the linear solution, SPEC 5.3);
  T3 the deviation D_n at the later dumps (printed; core reports 2.8e-3 for all modes
     and 7.6e-5 for |n| <= 4 over 3.1 e-folds);
  T4 negative control: amplitudes of another seed give D_n of order 1.

    python3 selftest.py --run DIR --core-python DIR --modefile FILE --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

import ladder_lib as LL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--core-python", required=True)
    ap.add_argument("--modefile", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, os.path.abspath(a.core_python))
    import nrpic.scalar_field as core_sf
    if not os.path.abspath(core_sf.__file__).startswith(os.path.abspath(a.core_python)):
        raise RuntimeError(f"imported {core_sf.__file__}, not core's copy")

    dumps = LL.dump_list(a.run)
    res = dict(run=a.run, dumps=len(dumps))
    # T1
    worst = 0.0
    for f in dumps[:3]:
        h, mine = LL.read_dump(f, LL.read_header(f)["names"])
        ref = core_sf.read_dump(f)["fields"]
        for name, arr in mine.items():
            # core's arrays are [i, j, k] = (x, y, z); mine are [z, y, x]
            worst = max(worst, float(np.abs(arr - ref[name].transpose(2, 1, 0)).max()))
    res["T1_max_abs_difference"] = worst

    modes = LL.Modes(32, 64)
    alpha = modes.alpha()
    alpha_bad = modes.alpha(seed=LL.SEED + 1)
    t_last = LL.read_header(dumps[-1])["time"]
    ref = LL.reference_for(modes, a.modefile, t_last + 0.1)
    rows = []
    for f in dumps:
        h, flds = LL.read_dump(f, LL.CURV_VARS)
        rnr, aniso, means = LL.curvature(modes, flds)
        t = h["time"]
        rk, _ = ref.modes(t)
        w = ref.window(t, modes.shell_n2.astype(float)**0.5)
        lin_shell = LL.L_BOX**-1.5 * w * rk
        lin = lin_shell[modes.shell_of] * alpha
        bad = lin_shell[modes.shell_of] * alpha_bad
        wm = w[modes.shell_of]
        sel = wm > 0.5
        d = np.abs(rnr / lin - 1.0)
        db = np.abs(rnr / bad - 1.0)
        small = sel & (modes.n2 <= 16)
        rows.append(dict(time=t, cycle=h["cycle"], efolds=float(ref.background(t)["lna"]),
                         n_in=int(sel.sum()), D_max_in=float(d[sel].max()),
                         D_max_n2le16_in=float(d[small].max()) if small.any() else None,
                         D_median_in=float(np.median(d[sel])),
                         D_seed_control_median=float(np.median(db[sel])),
                         aniso_over_R_rms=float(np.sqrt(np.mean(np.abs(aniso[sel])**2) /
                                                        np.mean(np.abs(rnr[sel])**2)))))
    res["dumps_table"] = rows
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "selftest.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
