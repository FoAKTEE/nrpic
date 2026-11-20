#!/usr/bin/env python3
"""Unit tests of growth.growth_fit_v2 and growth.oscillation_period on synthetic signals
(JOURNAL.md entry 9, predictions U1-U5).

    python3 test_growth_v2.py [--out DIR]      # writes DIR/test_growth_v2.json, exit 1 on a failure
    python3 -m pytest test_growth_v2.py        # the same checks as pytest tests

U1 period of 2e-3 sin(2 pi t/25 + phi) on 1e-3 e^{sigma t}, sigma = 0.02, 0.05, up to the
   time the signal reaches 0.1: within 1 percent without noise (4 phases), within 5
   percent (median of 20 realisations) with white noise 1e-3 per 0.25 M record.
U2 pure exponential, exact reference: sigma to 1e-6 relative.
U3 exponential plus oscillation, exact reference and exact supplied period, no noise:
   sigma within 2e-3 relative.
U4 reference as an array (a drifting, oscillating control plus 1e-3 e^{sigma t}): sigma
   within 1e-4 relative.
U5 se_noise against the scatter of sigma over 200 noise realisations (no oscillation):
   ratio between 0.85 and 1.15.
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

DT, A0, AOSC, P, NOISE, HI = 0.25, 1e-3, 2e-3, 25.0, 1e-3, 0.1


def _t(sig, extra=20.0):
    return np.arange(0.0, np.log(300.0) / sig + extra, DT)


def u1():
    out = []
    rng = np.random.default_rng(11)
    for sig in (0.02, 0.05):
        t = _t(sig)
        t_end = np.log(HI / A0) / sig
        for phase in (0.0, 1.0, 2.5, 4.0):
            d = A0 * np.exp(sig * t) + AOSC * np.sin(2 * np.pi * t / P + phase)
            po = gr.oscillation_period(t, d, t_end=t_end)
            out.append(dict(sigma=sig, noise=0.0, phase=phase, period=po["period"], trend=po["trend"],
                            rel=po["period"] / P - 1, ok=bool(abs(po["period"] / P - 1) < 0.01)))
        ps = []
        for _ in range(20):
            d = (A0 * np.exp(sig * t) + AOSC * np.sin(2 * np.pi * t / P + rng.uniform(0, 2 * np.pi))
                 + NOISE * rng.standard_normal(len(t)))
            ps.append(gr.oscillation_period(t, d, t_end=t_end)["period"])
        med = float(np.median(ps))
        out.append(dict(sigma=sig, noise=NOISE, median_period=med, min=float(min(ps)), max=float(max(ps)),
                        rel=med / P - 1, ok=bool(abs(med / P - 1) < 0.05)))
    return dict(rows=out, ok=all(r["ok"] for r in out))


def u2():
    rows = []
    for sig in (0.02, 0.05, 0.1):
        t = _t(sig)
        y = 0.6 + A0 * np.exp(sig * t)
        f = gr.growth_fit_v2(t, y, 0.6, period=P)
        rows.append(dict(sigma=sig, fit=f["sigma"], rel=f["sigma"] / sig - 1,
                         ok=bool(f["ok"] and abs(f["sigma"] / sig - 1) < 1e-6)))
    return dict(rows=rows, ok=all(r["ok"] for r in rows))


def u3():
    rows = []
    for sig in (0.02, 0.05, 0.1):
        t = _t(sig)
        for phase in (0.0, 2.0):
            y = 0.6 + A0 * np.exp(sig * t) + AOSC * np.sin(2 * np.pi * t / P + phase)
            f = gr.growth_fit_v2(t, y, 0.6, period=P)
            rows.append(dict(sigma=sig, phase=phase, fit=f.get("sigma"),
                             rel=(f["sigma"] / sig - 1) if f["ok"] else None,
                             ok=bool(f["ok"] and abs(f["sigma"] / sig - 1) < 2e-3)))
    return dict(rows=rows, ok=all(r["ok"] for r in rows))


def u4():
    rows = []
    for sig in (0.02, 0.05, 0.1):
        t = _t(sig)
        ctrl = 0.6 + 0.01 * np.sin(2 * np.pi * t / 40.0) + 2e-4 * t
        y = ctrl - A0 * np.exp(sig * t)            # contraction relative to the control
        f = gr.growth_fit_v2(t, y, ctrl, period=P)
        rows.append(dict(sigma=sig, fit=f.get("sigma"), sign=f.get("sign"),
                         rel=(f["sigma"] / sig - 1) if f["ok"] else None,
                         ok=bool(f["ok"] and abs(f["sigma"] / sig - 1) < 1e-4 and f["sign"] < 0)))
    return dict(rows=rows, ok=all(r["ok"] for r in rows))


def u5(nreal=200):
    rows = []
    rng = np.random.default_rng(5)
    for sig in (0.02, 0.05, 0.1):
        t = _t(sig)
        s, se = [], []
        for _ in range(nreal):
            y = 0.6 + A0 * np.exp(sig * t) + NOISE * rng.standard_normal(len(t))
            f = gr.growth_fit_v2(t, y, 0.6, period=P)
            if f["ok"]:
                s.append(f["sigma"])
                se.append(f["se_noise"])
        ratio = float(np.median(se) / np.std(s, ddof=1))
        rows.append(dict(sigma=sig, n_ok=len(s), std_sigma=float(np.std(s, ddof=1)),
                         median_se_noise=float(np.median(se)), ratio=ratio,
                         mean_rel_bias=float(np.mean(s) / sig - 1),
                         ok=bool(len(s) == nreal and 0.85 <= ratio <= 1.15)))
    return dict(rows=rows, ok=all(r["ok"] for r in rows))


TESTS = dict(U1=u1, U2=u2, U3=u3, U4=u4, U5=u5)


def test_U1():
    assert u1()["ok"]


def test_U2():
    assert u2()["ok"]


def test_U3():
    assert u3()["ok"]


def test_U4():
    assert u4()["ok"]


def test_U5():
    assert u5()["ok"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args(argv)
    res = {}
    for k, fn in TESTS.items():
        r = fn()
        res[k] = r
        print(f"{k}: {'PASS' if r['ok'] else 'FAIL'}", flush=True)
        for row in r["rows"]:
            print("   ", {kk: (round(v, 6) if isinstance(v, float) else v) for kk, v in row.items()}, flush=True)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "test_growth_v2.json"), "w") as f:
            json.dump(res, f, indent=1)
    return 0 if all(r["ok"] for r in res.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
