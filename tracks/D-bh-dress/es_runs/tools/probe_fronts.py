#!/usr/bin/env python3
"""Moving features in the lapse at the probes of the ES runs (es_runs, Track D; entry 7).

    probe_fronts.py --run NAME:DIR:BASE [--run ...] [--out DIR] [--tmin 50] [--tmax 200]

The probes of the ES inputs sit on the x axis at x = 1, 4, 20, 36, 46, 56, 80, 152 M and are
written every 10 cycles (dt = 0.3125 M) to <base>.nrpic.hst. For each run the script forms
d alpha/dt at every probe, removes a smooth trend (running mean over 20 M), and for each
pair of neighbouring probes finds the lag (inner minus outer arrival, coordinate time)
that maximises the cross-correlation of the detrended series over [tmin, tmax]. A positive
lag means a feature that reaches the outer probe first (moving inward). Writes
DIR/probe_fronts.json and DIR/figs/probe_fronts_<NAME>.png (waterfall of the detrended
d alpha/dt, one row per probe, ordered by x).
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.normpath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, PKG)
from nrpic import figstyle as fs  # noqa: E402
from analyse import read_named_hst  # noqa: E402

PROBES = [("alpha_probe1", 1.0), ("alpha_probe2", 4.0), ("alpha_probe3", 20.0), ("alpha_probe4", 36.0),
          ("alpha_probe", 46.0), ("alpha_probe5", 56.0), ("alpha_probe6", 80.0), ("alpha_probe7", 152.0)]


def detrended_rate(t, a, width=20.0):
    tg = np.arange(t[0], t[-1], 0.25)
    ag = np.interp(tg, t, a)
    da = np.gradient(ag, tg)
    n = int(round(width / 0.25))
    ker = np.ones(n) / n
    trend = np.convolve(da, ker, mode="same")
    return tg, da - trend


def best_lag(tg, y_out, y_in, lo, hi, maxlag=80.0):
    s = (tg >= lo) & (tg <= hi)
    dt = tg[1] - tg[0]
    lags = np.arange(-maxlag, maxlag + dt / 2, dt)
    best, cbest = None, -2.0
    for L in lags:
        # y_in(t) compared with y_out(t - L)
        yo = np.interp(tg[s] - L, tg, y_out)
        yi = y_in[s]
        if np.std(yo) == 0 or np.std(yi) == 0:
            continue
        c = float(np.corrcoef(yo, yi)[0, 1])
        if c > cbest:
            best, cbest = float(L), c
    return best, cbest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--tmin", type=float, default=50.0)
    ap.add_argument("--tmax", type=float, default=200.0)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    res = {"tmin": a.tmin, "tmax": a.tmax, "runs": {}}
    for spec in a.run:
        name, d, base = spec.split(":")
        H = read_named_hst(os.path.join(d, f"{base}.nrpic.hst"))
        series = {}
        for key, x in PROBES:
            if key in H:
                tg, y = detrended_rate(H["time"], H[key])
                series[x] = y
        xs = sorted(series)
        pairs = []
        for xi, xo in zip(xs[:-1], xs[1:]):
            L, c = best_lag(tg, series[xo], series[xi], a.tmin, a.tmax)
            pairs.append(dict(x_outer=xo, x_inner=xi, lag=L, corr=c,
                              speed=(float((xo - xi) / L) if L not in (None, 0.0) else None)))
        res["runs"][name] = dict(pairs=pairs,
                                 rms={f"x={x:g}": float(np.std(series[x][(tg >= a.tmin) & (tg <= a.tmax)])) for x in xs})
        fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.0))
        fig.subplots_adjust(left=0.14, right=0.97, bottom=0.09, top=0.97)
        cc = fs.series_colors(len(xs))
        for k, (x, c) in enumerate(zip(xs, cc)):
            y = series[x]
            s = (tg >= a.tmin - 20) & (tg <= a.tmax)
            scale = np.max(np.abs(y[(tg >= a.tmin) & (tg <= a.tmax)])) or 1.0
            ax.plot(tg[s], k + 0.45 * y[s] / scale, color=c, lw=0.8)
            ax.text(a.tmin - 19, k + 0.15, f"x={x:g}M", fontsize=7)
        ax.axvline(a.tmin, **fs.MASK_LINE)
        ax.axvline(165.0, **fs.MASK_LINE)
        ax.set_yticks([])
        ax.set_xlabel(r"coordinate time $t/M$")
        ax.set_ylabel(r"detrended $\partial_t\alpha$ at the probes (each row normalised)")
        ax.text(0.98, 0.01, name, transform=ax.transAxes, ha="right", fontsize=8)
        fs.save(fig, os.path.join(a.out, "figs", f"probe_fronts_{name}"))
        plt.close(fig)
    with open(os.path.join(a.out, "probe_fronts.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
