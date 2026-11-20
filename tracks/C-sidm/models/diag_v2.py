#!/usr/bin/env python3
"""Diagnoses of the failed clauses of G2', G3' and G6' (JOURNAL.md entry 11, predictions
D2 and D3).

    python3 diag_v2.py --validation DIR [--out DIR] [--runs /data/haiyangw/nrpic/runs/st]

D2 (a) curvature of ln|d_s| of alpha_c in the three compensated y_c = 0.5 samples
(growth_fit_v2 smoothing with the measured period, quadratic fit from the first smoothed
time to the first |d_s| >= 0.14); (b) their rates over one common interval (latest first
smoothed time to the earliest time any reaches |d_s| = 0.1).
D3 at sigma = 0.1 of G2': |P/25 - 1| of the realisations outside and inside one SE, read
from DIR/growth_v2_figdata.npz of the validation run.
Writes OUT/diag_v2.json and OUT/diag_v2_figdata.npz.
"""

import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import growth as gr  # noqa: E402

COMP = ["dir_yc0500_comp", "dir_yc0500_comp_s2", "dir_yc0500_comp_s3"]
HI_CURV, HI_COMMON = 0.14, 0.1


def d2(runs):
    out, fig, curves = {}, {}, {}
    for key in COMP:
        d = os.path.join(runs, key)
        run = gr.load_run(d)
        t, a = run["t"], run["alpha"]
        ref = gr.run_probe_reference(d, alpha0=float(a[0]))["alpha_ref"]
        f = gr.growth_fit_v2(t, a, ref, k_lo=3.0, hi=0.1)          # for the measured period
        P = f["period"]
        ts, ds, *_ = gr.boxcar_exact(t, a - ref, P)
        sgn = 1.0
        i1 = int(np.nonzero(sgn * ds >= HI_CURV)[0][0])
        sel = slice(0, i1 + 1)
        tw, dw = ts[sel], sgn * ds[sel]
        if np.any(dw <= 0):
            k0 = int(np.nonzero(dw <= 0)[0][-1]) + 1
            tw, dw = tw[k0:], dw[k0:]
        c2, c1, c0 = np.polyfit(tw, np.log(dw), 2)
        r0, r1 = c1 + 2 * c2 * tw[0], c1 + 2 * c2 * tw[-1]
        t_hi = float(ts[int(np.nonzero(sgn * ds >= HI_COMMON)[0][0])])
        out[key] = dict(period=P, t_first=float(ts[0]), t_hi_0p1=t_hi, curv_t0=float(tw[0]),
                        curv_t1=float(tw[-1]), c=float(c2), rate_start=float(r0), rate_end=float(r1),
                        ratio_end_start=float(r1 / r0), pass_curv=bool(c2 < 0 and r1 / r0 < 0.7))
        curves[key] = (t, a, ref, P)
        fig[f"{key}_ts"], fig[f"{key}_ds"] = ts, ds
        fig[f"{key}_quad"] = np.array([tw[0], tw[-1], c0, c1, c2])
        print(f"D2a {key}: P {P:.2f}, quadratic over [{tw[0]:.1f}, {tw[-1]:.1f}] c = {c2:.3e}, "
              f"rate start {r0:.4f} end {r1:.4f} ratio {r1 / r0:.3f}", flush=True)
    t0 = max(out[k]["t_first"] for k in COMP)
    t1 = min(out[k]["t_hi_0p1"] for k in COMP)
    common = {}
    for key in COMP:
        t, a, ref, P = curves[key]
        s = gr.slope_over(t, a, ref, P, t0, t1)
        common[key] = {k: v for k, v in s.items() if not k.startswith("curve")}
        print(f"D2b {key}: rate over [{t0:.1f}, {t1:.1f}] = {s.get('sigma', float('nan')):.4f} +- "
              f"{s.get('se', float('nan')):.4f}", flush=True)
    ss = np.array([common[k]["sigma"] for k in COMP if common[k]["ok"]])
    m = float(ss.mean()) if len(ss) else None
    res = dict(per_run=out, common_interval=[t0, t1], common=common, common_mean=m,
               common_max_rel_dev=float(np.max(np.abs(ss / m - 1))) if len(ss) else None)
    res["pass_a"] = bool(all(out[k]["pass_curv"] for k in COMP))
    res["pass_b"] = bool(len(ss) == 3 and res["common_max_rel_dev"] < 0.15)
    fig["common"] = np.array([t0, t1] + [common[k].get("sigma", np.nan) for k in COMP]
                             + [common[k].get("amp0", np.nan) for k in COMP])
    return res, fig


def d3(vdir):
    z = np.load(os.path.join(vdir, "growth_v2_figdata.npz"))
    s, se, P = z["syn_0.1_v2_fits"], z["syn_0.1_v2_se"], z["syn_0.1_v2_P"]
    sig = 0.1
    out_ = np.abs(s - sig) > se
    dev = np.abs(P / 25.0 - 1)
    mo, mi = float(np.median(dev[out_])), float(np.median(dev[~out_]))
    rel = np.abs(s / sig - 1)
    corr = float(np.corrcoef(dev, rel)[0, 1])
    res = dict(n_outside=int(out_.sum()), n_inside=int((~out_).sum()), median_dev_outside=mo,
               median_dev_inside=mi, ratio=mo / mi if mi > 0 else None, corr_dev_relerr=corr,
               pass_=bool(mi > 0 and mo > 2 * mi))
    print(f"D3: outside 1 SE {res['n_outside']}, median |P/25-1| {mo:.4f}; inside {res['n_inside']}, "
          f"{mi:.4f}; ratio {res['ratio']}; corr(|P/25-1|, |sigma/0.1-1|) = {corr:.3f}", flush=True)
    return res, dict(d3_dev=dev, d3_rel=rel, d3_out=out_.astype(float))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--validation", required=True)
    ap.add_argument("--runs", default="/data/haiyangw/nrpic/runs/st")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    r2, f2 = d2(a.runs)
    r3, f3 = d3(a.validation)
    res = dict(D2=r2, D3=r3, validation=a.validation)
    print(json.dumps(dict(D2a=r2["pass_a"], D2b=r2["pass_b"], D2b_max_rel_dev=r2["common_max_rel_dev"],
                          D3=r3["pass_"]), indent=1))
    with open(os.path.join(a.out, "diag_v2.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    f2.update(f3)
    np.savez_compressed(os.path.join(a.out, "diag_v2_figdata.npz"), **f2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
