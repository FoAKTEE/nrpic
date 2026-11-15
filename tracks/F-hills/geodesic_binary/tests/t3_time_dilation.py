"""T3: relativistic time dilation of a free-falling oscillator under HRNA (2404 appendix B).

Setup of kb-data/raw/arxiv/2404.16270/v1/src/appendix.tex:37-68: two equal masses joined by
Phi = k/2 (|x2 - x1| - l0)^2, k/m = 1/5, l0 = 3/40 r_g, initial elongation 4 l0/3, aligned
perpendicular to the radial direction; the CM falls radially from rest at infinity
(Schwarzschild coordinates).  Frequencies from successive maxima of the separation.

Run: <venv>/bin/python -I tests/t3_time_dilation.py <outdir>
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "..", "..", "..", "python"))
import hrna  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

KM, L0 = 0.2, 3.0 / 40.0          # k/m and l0, appendix.tex:44
R_START, R_END = 220.0, 8.0


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    f = 1 - 2 / R_START
    vx = -f * math.sqrt(2 / R_START)                    # E = 1, L = 0 radial infall
    ell = 4 * L0 / 3
    y0 = np.array([R_START, ell / 2, 0, vx, 0, 0, R_START, -ell / 2, 0, vx, 0, 0])
    t_end = quad(lambda r: 1 / ((1 - 2 / r) * math.sqrt(2 / r)), R_END, R_START, epsabs=1e-12)[0]
    out = hrna.integrate(hrna.LAW_HRNA, hrna.COORDS_SCH, hrna.PAIR_HOOKE, 1.0, 0.0, 1.0, 1.0, KM, L0,
                         y0, 0.01, 1e-12, 1e-15, 1e300, 1e300, 2.5, t_end, 10 ** 7, 1.0, 2 * 10 ** 6,
                         hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._work(), 0.05)
    t, Y = out[4], out[5]
    d = Y[:, 0:3] - Y[:, 6:9]
    w = Y[:, 3:6] - Y[:, 9:12]
    sep = np.linalg.norm(d, axis=1)
    sdot = np.einsum("ij,ij->i", d, w) / sep
    rc = np.linalg.norm(0.5 * (Y[:, 0:3] + Y[:, 6:9]), axis=1)
    idx = np.where((sdot[:-1] > 0) & (sdot[1:] <= 0))[0]
    tm = t[idx] + sdot[idx] / (sdot[idx] - sdot[idx + 1]) * (t[idx + 1] - t[idx])
    tmid = 0.5 * (tm[1:] + tm[:-1])
    rmid = np.interp(tmid, t, rc)
    fmeas = 1 / np.diff(tm)
    # proper time of the CM between maxima: dtau = (1 - 2M/r) dt for E = 1 radial infall
    lapse = 1 - 2 / rc
    cum = np.concatenate([[0], np.cumsum(0.5 * (lapse[1:] + lapse[:-1]) * np.diff(t))])
    tau_m = np.interp(tm, t, cum)
    Ptau = np.diff(tau_m)
    f0 = math.sqrt(2 * KM) / (2 * math.pi)
    P_notide = 1 / f0
    P_tide = 2 * math.pi / np.sqrt(2 * KM + 1 / rmid ** 3)
    f_paper = f0 * (1 - 2 / rmid)                       # appendix.tex:62-66
    f_static = f0 * np.sqrt(1 - 2 / rmid)               # appendix.tex:52-56 (static observer)
    sel = rmid >= 10.0
    res = dict(
        n_periods=int(len(fmeas)), nsteps=int(out[7]), r_range=[float(rmid.min()), float(rmid.max())],
        max_rel_dev_proper_period_vs_tidal=float(np.max(np.abs(Ptau[sel] / P_tide[sel] - 1))),
        max_rel_dev_proper_period_vs_f0=float(np.max(np.abs(Ptau[sel] / P_notide - 1))),
        max_rel_dev_coord_freq_vs_paper_formula=float(np.max(np.abs(fmeas[sel] / f_paper[sel] - 1))),
        rel_dev_coord_freq_vs_paper_at_r200=float(np.interp(200, rmid[::-1], (fmeas / f_paper - 1)[::-1])),
        rel_dev_coord_freq_vs_paper_at_r10=float(np.interp(10, rmid[::-1], (fmeas / f_paper - 1)[::-1])),
    )
    with open(os.path.join(outdir, "t3_time_dilation.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    np.savez(os.path.join(outdir, "t3_time_dilation.npz"), rmid=rmid, fmeas=fmeas, Ptau=Ptau,
             P_tide=P_tide, f_paper=f_paper)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 4.6))
    ax1 = fig.add_axes([0.2, 0.47, 0.75, 0.5])
    ax2 = fig.add_axes([0.2, 0.1, 0.75, 0.32])
    rr = np.geomspace(rmid.min(), rmid.max(), 300)
    ax1.plot(rr, f0 * (1 - 2 / rr), color=fs.PAL["blue"], label=r"$f_0(1-2M/r)$ (free fall)")
    ax1.plot(rr, f0 * np.sqrt(1 - 2 / rr), **fs.GUIDE, label=r"$f_0(1-2M/r)^{1/2}$ (static)")
    ax1.plot(rmid[::6], fmeas[::6], "o", ms=3, color=fs.PAL["red"], label="HRNA, successive maxima")
    ax1.set_xscale("log")
    ax1.set_ylabel(r"$f\ [c^3/GM]$")
    ax1.legend(loc="lower right", fontsize=8)
    ax1.xaxis.set_major_formatter(plt.NullFormatter())
    ax2.semilogx(rmid, Ptau / P_tide - 1, color=fs.PAL["red"], label=r"$\Delta\tau/P_{\rm tide}-1$")
    ax2.semilogx(rmid, Ptau / P_notide - 1, color=fs.PAL["red"], ls="--", label=r"$\Delta\tau f_0-1$")
    ax2.axhline(0, **fs.THIN)
    ax2.set_xlabel(r"$r_{\rm cm}\ [r_g]$")
    ax2.set_ylabel("proper period dev.")
    ax2.legend(loc="lower left", fontsize=8)
    for ax in (ax1, ax2):
        ax.set_xlim(rmid.min() * 0.95, rmid.max() * 1.05)
    fs.save(fig, os.path.join(outdir, "t3_time_dilation"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
