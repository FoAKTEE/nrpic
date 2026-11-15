#!/usr/bin/env python3
"""Diagnosis of the failed synthetic test G2 (JOURNAL.md entry 4): which ingredient of the
synthetic signal biases the log-linear growth fit of growth.py.

    python3 diag_g2.py [--out DIR]

Signal as in validate_growth.synthetic: d = s (1e-3 e^{sigma t} + a_osc sin(2 pi t/25 + phi)
+ noise), s = +-1, dt = 0.25 M, a_osc = 2e-3, noise 1e-3 per record, window (0.01, 0.1).
Variants: G exactly as G2 (the departure is measured from the first record, which holds
the initial amplitude 1e-3 itself plus oscillation and noise); A as G with the exact
reference 0; B as A without oscillation; C as A without noise; D as A with the oracle
window (the noise-free crossing times of lo and hi, fit of ln|d_s| over that fixed
interval); E as A with boxcar width = oscillation period (25 M); F as G with the curve_fit
estimator (A e^{sigma t} + C); H as A with the curve_fit estimator.
Writes DIR/diag_g2.json.
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

LO, HI, A0, AOSC, P, NOISE = 0.01, 0.1, 1e-3, 2e-3, 25.0, 1e-3


def oracle_fit(t, y, sig, width):
    ts, ds = gr.boxcar(t, y, width)
    t0, t1 = np.log(LO / A0) / sig, np.log(HI / A0) / sig
    w = (ts >= t0) & (ts <= t1)
    dd = np.abs(ds[w])
    ok = dd > 0
    p = np.polyfit(ts[w][ok], np.log(dd[ok]), 1)
    return float(p[0])


def run(variant, sig, nreal=50, seed=7):
    rng = np.random.default_rng(seed)
    dt = 0.25
    t = np.arange(0.0, np.log(300.0) / sig + 20.0, dt)
    out = []
    for k in range(nreal):
        sgn = 1.0 if k % 2 == 0 else -1.0
        phase = rng.uniform(0, 2 * np.pi)
        noise = rng.standard_normal(len(t))
        aosc = 0.0 if variant == "B" else AOSC
        nz = 0.0 if variant == "C" else NOISE
        y = sgn * (A0 * np.exp(sig * t) + aosc * np.sin(2 * np.pi * t / P + phase) + nz * noise)
        width = P if variant == "E" else 10.0
        if variant == "D":
            out.append((oracle_fit(t, y, sig, width), np.nan))
            continue
        ref = None if variant in ("G", "F") else 0.0
        f = gr.growth_fit(t, y, width=width, lo=LO, hi=HI, y_ref=ref)
        if variant in ("F", "H"):
            out.append((f["sigma_nl"], f["se_nl"]))
        else:
            out.append((f["sigma"], f["se"]))
    s = np.array([o[0] for o in out])
    se = np.array([o[1] for o in out])
    rel = s / sig - 1
    return dict(variant=variant, sigma=sig, mean_rel_bias=float(rel.mean()),
                sem_rel_bias=float(rel.std(ddof=1) / np.sqrt(len(rel))),
                rms_rel_err=float(np.sqrt(np.mean(rel ** 2))),
                coverage_3se=(float(np.mean(np.abs(s - sig) < 3 * se)) if np.all(np.isfinite(se)) else None))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    res = []
    for sig in (0.02, 0.05, 0.1):
        for v in "GABCDEFH":
            r = run(v, sig)
            res.append(r)
            cov = "n/a" if r["coverage_3se"] is None else f"{r['coverage_3se']:.2f}"
            print(f"sigma {sig:<5g} {v}: bias {r['mean_rel_bias']:+.4f} +- {r['sem_rel_bias']:.4f}, "
                  f"rms {r['rms_rel_err']:.4f}, 3SE coverage {cov}", flush=True)
    with open(os.path.join(a.out, "diag_g2.json"), "w") as f:
        json.dump(res, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
