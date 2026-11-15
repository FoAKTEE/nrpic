#!/usr/bin/env python3
"""Verifier check C2 (D-pre-4): drift of the apparent-horizon mass of the vacuum puncture,
recomputed from the raw finder output of the two card runs with my own definitions.

Definitions (mine, fixed before looking at the track's analysis):
  M(t)        finder mass (column 3 of punc.horizon_summary_0.txt; duplicate times from
              the restart: the last record is kept)
  Mbar(t)     centred running mean over a window of 20 M
  drift(T)    Mbar(t0 + T) - Mbar(t0), t0 = 50 M, T <= 450 M (window-limited near the end)
  slope       least-squares dM/dt over [t0, t_end], with the standard error from the
              residuals (inflated by sqrt of the correlation length in samples)
  offset      M - 1 (the exact mass of the unit puncture)
Also the horizon's coordinate mean radius against t and the distance to the edge of the
finest refinement level (|x| < 2 M in both runs: blocks of 16 cells cover the requested
|x| < 1.5 M), the spin magnitude, and the conversion to the coupling floor
k_floor = |drift| / ln(a_f/a_i) for one doubling of a.

Usage: v2_drift.py --out DIR --run NAME=DIR:INV_DX [...]
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def load(path):
    d = np.loadtxt(path, comments="#")
    t = d[:, 1]
    # keep the last record of each time (restart appends)
    _, idx = np.unique(t[::-1], return_index=True)
    keep = len(t) - 1 - idx
    keep.sort()
    d = d[keep]
    return {"t": d[:, 1], "M": d[:, 2], "S": d[:, 6], "area": d[:, 7], "rmean": d[:, 10], "rmin": d[:, 11],
            "n_raw": int(len(t)), "n_unique": int(len(keep))}


def running_mean(t, y, W):
    out = np.full_like(y, np.nan)
    for i, ti in enumerate(t):
        s = (t >= ti - W / 2) & (t <= ti + W / 2)
        if ti - W / 2 >= t[0] and ti + W / 2 <= t[-1]:
            out[i] = y[s].mean()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--t0", type=float, default=50.0)
    ap.add_argument("--W", type=float, default=20.0)
    ap.add_argument("--figdir", default=os.path.join(HERE, "..", "figs"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"t0": a.t0, "W": a.W, "runs": {}}
    data = {}
    for spec in a.run:
        name, rest = spec.split("=", 1)
        rd, inv = rest.rsplit(":", 1)
        D = load(os.path.join(rd, "punc.horizon_summary_0.txt"))
        D["inv_dx"] = float(inv)
        t, M = D["t"], D["M"]
        Mb = running_mean(t, M, a.W)
        D["Mbar"] = Mb
        i0 = np.nanargmin(np.abs(t - a.t0))
        ok = np.isfinite(Mb) & (t >= a.t0)
        drift = Mb[ok] - Mb[i0]
        late = t >= a.t0
        A = np.vstack([np.ones(late.sum()), t[late] - a.t0]).T
        coef, *_ = np.linalg.lstsq(A, M[late], rcond=None)
        r = M[late] - A @ coef
        # correlation length of the residuals (first zero of the autocorrelation)
        rr = r - r.mean()
        ac = np.correlate(rr, rr, "full")[len(rr) - 1:] / (rr @ rr)
        lag = int(np.argmax(ac < 0)) if np.any(ac < 0) else len(rr)
        cov = np.linalg.inv(A.T @ A) * (r @ r) / (len(r) - 2)
        se = math.sqrt(cov[1, 1]) * math.sqrt(max(lag, 1))
        dt = np.median(np.diff(t))
        rec = {"dir": rd, "inv_dx": D["inv_dx"], "n_raw": D["n_raw"], "n_unique": D["n_unique"],
               "t_end": float(t[-1]), "sample_dt": float(dt),
               "M_at_0": float(M[0]), "M_at_t0": float(M[i0]), "Mbar_at_t0": float(Mb[i0]),
               "M_end": float(M[-1]), "Mbar_last": float(Mb[ok][-1]), "t_Mbar_last": float(t[ok][-1]),
               "offset_Mbar_t0_minus_1": float(Mb[i0] - 1),
               "drift_max_abs": float(np.max(np.abs(drift))),
               "drift_at_last": float(drift[-1]),
               "rms_about_Mbar": float(np.sqrt(np.nanmean((M[ok] - Mb[ok]) ** 2))),
               "slope_per_M": float(coef[1]), "slope_se": se, "resid_corr_len_samples": lag,
               "slope_times_450": float(coef[1] * 450),
               "max_spin_S": float(np.max(np.abs(D["S"][late]))),
               "rmean_t0": float(D["rmean"][i0]), "rmean_end": float(D["rmean"][-1]),
               "rmean_slope_last100": float(np.polyfit(t[t > t[-1] - 100], D["rmean"][t > t[-1] - 100], 1)[0]),
               "max_extent_x": None,
               "max_abs_dev_from_linear_fit": float(np.max(np.abs(r))),
               "t_of_max_dev": float(t[late][np.argmax(np.abs(r))]),
               "max_abs_dev_windows": {f"{lo}-{hi}": float(np.max(np.abs(r[(t[late] >= lo) & (t[late] < hi)])))
                                       for lo, hi in ((50, 200), (200, 260), (260, 300), (300, 340), (340, 500))}}
        D["resid"] = (t[late], r)
        # largest coordinate extent of the horizon from the shape file, if present
        shp = os.path.join(rd, "punc.horizon_shape_0.txt")
        rec["shape_file"] = os.path.exists(shp)
        res["runs"][name] = rec
        data[name] = D
    names = sorted(res["runs"], key=lambda n: res["runs"][n]["inv_dx"])
    if len(names) >= 2:
        c, f = res["runs"][names[0]], res["runs"][names[-1]]
        ratio = c["drift_max_abs"] / f["drift_max_abs"] if f["drift_max_abs"] > 0 else float("inf")
        res["convergence"] = {"coarse": names[0], "fine": names[-1],
                              "drift_ratio": ratio,
                              "order_drift": math.log(ratio) / math.log(f["inv_dx"] / c["inv_dx"]),
                              "offset_ratio": abs(c["offset_Mbar_t0_minus_1"] / f["offset_Mbar_t0_minus_1"]),
                              "order_offset": math.log(abs(c["offset_Mbar_t0_minus_1"] / f["offset_Mbar_t0_minus_1"]))
                              / math.log(f["inv_dx"] / c["inv_dx"])}
    for n in names:
        d = res["runs"][n]["drift_max_abs"]
        res["runs"][n]["k_floor_one_doubling"] = d / math.log(2.0)
    with open(os.path.join(a.out, "v2_drift.json"), "w") as fo:
        json.dump(res, fo, indent=1)

    fs.use_style()
    fig, ax = plt.subplots(4, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 9.0), sharex=True)
    for j, n in enumerate(names):
        D = data[n]
        c = fs.SERIES[j]
        lab = f"$dx = M/{int(D['inv_dx'])}$"
        ax[0].plot(D["t"], D["M"] - 1, color=c, lw=0.6, alpha=0.5)
        ax[0].plot(D["t"], D["Mbar"] - 1, color=c, lw=1.5, label=lab)
        i0 = np.nanargmin(np.abs(D["t"] - a.t0))
        ax[1].plot(D["t"], (D["Mbar"] - D["Mbar"][i0]), color=c, lw=1.5, label=lab)
        ax[2].plot(D["resid"][0], D["resid"][1], color=c, lw=0.8, label=lab)
        ax[3].plot(D["t"], D["rmean"], color=c, lw=1.5, label=lab)
    ax[0].set_ylabel(r"$M_{\rm AH}/M - 1$")
    ax[0].set_ylim(-1e-3, 2.5e-3)
    ax[0].legend(frameon=False, fontsize=8)
    ax[1].set_ylabel(r"$\bar M(t) - \bar M(50M)$")
    ax[1].axhline(0, **fs.THIN)
    ax[1].set_yscale("symlog", linthresh=1e-6)
    ax[2].set_ylabel(r"$M_{\rm AH}$ minus linear fit")
    ax[2].axhline(0, **fs.THIN)
    ax[2].legend(frameon=False, fontsize=8)
    ax[3].set_ylabel(r"horizon mean coord. radius $/M$")
    ax[3].axhline(2.0, **fs.MASK_LINE)
    ax[3].text(5, 1.9, "edge of finest level (|x| = 2 M, on the axes)", fontsize=7, va="top")
    ax[3].set_xlabel(r"$t/M$")
    for x in ax:
        x.axvline(a.t0, **fs.MASK_LINE)
    fig.tight_layout()
    files = fs.save(fig, os.path.join(a.out, "v2_drift"))
    shutil.copy(files[1], a.figdir)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
