"""Homogeneous universe over a thousandfold expansion, with and without white noise
(cosmo/PLAN.md, C5; tests A0 and A of Daverio, Dirian & Mitsou, arXiv:1904.07841,
Figs. 4 to 6).

    python3 daverio_a.py [--runs runs/cosmo]

Reads the constraint statistics of runs dav_a0_n{8,16,32} (exact data) and
dav_a_n{8,16,32} (noise). Quantities, with the largest value over the mesh:
    delta_chi = |chi - chi_FLRW| / chi_FLRW,   delta_E = |E - E_FLRW| / E_FLRW,
    H and |M| in the normalization and units of the source paper.
Units: this code has the initial Hubble rate 1 and a = 1 at the start; the source paper
has a = 1 at the end and lengths in Mpc/h. Conformal time: t_paper = t / 0.0105535.
Proper length unit of this code: 0.09466 Mpc/h, so a constraint (1/length^2) is
multiplied by 111.6; the Hamiltonian constraint of the source paper is half the usual
one.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import figstyle as fs  # noqa: E402

HC0 = 0.0105535          # conformal Hubble rate of the source paper at its start, h/Mpc
LUNIT = (1.0/1001.0)/HC0  # proper length unit of this code in Mpc/h
RHO0 = 3.0/(8.0*np.pi)
TREF = (100.0, 1000.0, 3000.0, 5806.0)
# read from the figures of the source paper (cosmo/notes/spec_1904.07841.md)
PAPER = {"a0_dchi_end": (2.55e-9, 1.59e-10, 9.8e-12),
         "a0_dE_end": (3.8e-9, 2.43e-10, 3.3e-11),
         "a_dE_end": (8.9e-7, 1.94e-7, 6.7e-8),
         "a_H": {500.0: (7.4e-7, 3.7e-7, 1.3e-7), 1000.0: (4.7e-8, 1.7e-8, 5.9e-9),
                 5806.0: (4.1e-12, 1.6e-12, 6.8e-13)},
         "a_M": {500.0: (1.9e-7, 1.2e-7, 5.6e-8), 1000.0: (1.4e-8, 6.6e-9, 2.7e-9),
                 5806.0: (2.3e-12, 8.0e-13, 3.6e-13)}}


def load(rundir):
    f = os.path.join(rundir, "flrw.cstat.hst")
    if not os.path.exists(f):
        return None
    c = np.loadtxt(f)
    if c.ndim != 2 or len(c) < 3:
        return None
    t = c[:, 0]
    a = (1.0 + 0.5*t)**2
    chi0, e0 = a**-2, RHO0/a**3
    out = {"t": t/HC0, "a": a,
           "dchi": np.maximum(np.abs(c[:, 1] - chi0), np.abs(c[:, 2] - chi0))/chi0,
           "dE": np.maximum(np.abs(c[:, 5] - e0), np.abs(c[:, 6] - e0))/e0,
           "H": 0.5*c[:, 8]/LUNIT**2, "M": c[:, 12]/LUNIT**2,
           "Hr": c[:, 10], "Mr": c[:, 14], "theta": c[:, 7]}
    out["finite"] = bool(np.isfinite(c).all())
    return out


def at(d, key, t):
    if t > d["t"][-1]*1.001:
        return np.nan
    return float(np.interp(t, d["t"], d[key]))


def main():
    args = sys.argv[1:]
    opt = {args[i][2:]: args[i+1] for i in range(0, len(args) - 1, 2)}
    runs = opt.get("runs", os.path.join(REPO, "runs", "cosmo"))
    ns = (8, 16, 32)
    data = {(k, n): load(os.path.join(runs, f"dav_{k}_n{n}")) for k in ("a0", "a") for n in ns}
    fs.use_style()
    cols = {8: fs.PAL["blue"], 16: fs.PAL["green"], 32: fs.PAL["red"]}
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.10, top=0.95, wspace=0.34,
                        hspace=0.12)
    panels = ((0, 0, "a0", "dchi", r"$\delta_\chi$, exact data"),
              (0, 1, "a0", "dE", r"$\delta_E$, exact data"),
              (0, 2, "a", "dchi", r"$\delta_\chi$, noise"),
              (1, 0, "a", "dE", r"$\delta_E$, noise"),
              (1, 1, "a", "H", r"$H$, noise"),
              (1, 2, "a", "M", r"$|M|$, noise"))
    for r, c, k, key, lab in panels:
        ax = axs[r, c]
        for n in ns:
            d = data[(k, n)]
            if d is None:
                continue
            y = d[key]
            ax.semilogy(d["t"][1:], np.maximum(y[1:], 1e-300), color=cols[n],
                        label=rf"$N_g = {n}$")
        ax.set_ylabel(lab)
        if r == 1:
            ax.set_xlabel(r"conformal time (Mpc/$h$)")
    axs[0, 0].legend(frameon=False, loc="lower right")
    figdir = os.path.join(HERE, "figs")
    os.makedirs(figdir, exist_ok=True)
    fs.save(fig, os.path.join(figdir, "daverio_a"))

    summ = {}
    for k in ("a0", "a"):
        for n in ns:
            d = data[(k, n)]
            if d is None:
                continue
            summ[f"{k}_n{n}"] = {key: {f"{t:g}": at(d, key, t) for t in TREF}
                                 for key in ("dchi", "dE", "H", "M", "Hr", "Mr")}
            summ[f"{k}_n{n}"]["t_end"] = float(d["t"][-1])
            summ[f"{k}_n{n}"]["finite"] = d["finite"]
            summ[f"{k}_n{n}"]["dchi_start"] = float(d["dchi"][0])
            summ[f"{k}_n{n}"]["dchi_max"] = float(np.nanmax(d["dchi"]))
            summ[f"{k}_n{n}"]["dE_over_a_max_after_200"] = float(
                np.nanmax((d["dE"]/d["a"])[d["t"] > 200.0]) if (d["t"] > 200.0).any() else np.nan)
            summ[f"{k}_n{n}"]["dE_over_a_end"] = float(d["dE"][-1]/d["a"][-1])
    with open(os.path.join(HERE, "daverio_a.json"), "w") as fp:
        json.dump(summ, fp, indent=1)

    def row(k, key, t):
        v = [summ.get(f"{k}_n{n}", {}).get(key, {}).get(f"{t:g}", np.nan) for n in ns]
        r = [v[i]/v[i+1] if v[i+1] else np.nan for i in range(2)]
        return v, r
    for k, name in (("a0", "exact data"), ("a", "noise")):
        print(f"== {name}")
        for key in ("dchi", "dE", "H", "M"):
            for t in TREF:
                v, r = row(k, key, t)
                if np.isfinite(v).any():
                    print(f"   {key:5s} t={t:6.0f}: " + " / ".join(f"{x:.2e}" for x in v)
                          + f"   ratios {r[0]:.1f} {r[1]:.1f}")
        for n in ns:
            s = summ.get(f"{k}_n{n}")
            if s:
                print(f"   N_g={n}: end t={s['t_end']:.0f} finite={s['finite']} dchi start "
                      f"{s['dchi_start']:.2e} max {s['dchi_max']:.2e}; dE/a after t=200: max "
                      f"{s['dE_over_a_max_after_200']:.2e} end {s['dE_over_a_end']:.2e}")
    print("source paper: exact data at the end dchi", PAPER["a0_dchi_end"], "dE",
          PAPER["a0_dE_end"], "; noise dE at the end", PAPER["a_dE_end"])
    print("source paper, noise: H", PAPER["a_H"], " M", PAPER["a_M"])
    print(os.path.join(figdir, "daverio_a.png"))


if __name__ == "__main__":
    main()
