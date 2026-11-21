#!/usr/bin/env python3
"""Specific energy of dust shells outside every shell crossing, against its initial value
(wave 3; analysis of AthenaK output only, decision 0010).

In spherical symmetry a shell that no other shell has crossed keeps its energy
E = v^2/2 - G M(<r)/r exactly (Newtonian, the mass inside it fixed). Outside the outermost
caustic (lambda_1 = 0.355 of r_ta) the flow is single-stream, so every dust particle with
r > 0.5 r_ta(t) that has not been on the other side of the centre is such a shell. For those
particles, M(<r) is the mass of all particles (seed and dust) inside r at that snapshot, and
dE = E(t) - E(0) is a direct measure of the force error the shell has felt up to t: a
shell that lost energy turns around early, one that gained energy late (t_ta ~ |E|^(-3/2)).

For groups of initial radius r0: median and 16/84 percentiles of dE/|E(0)| against a/a_i,
until the group's particles fall inside 0.5 r_ta(t). r_ta(t) from the zero of the median
radial velocity (nm_analyze.r_ta_from_velocity). Writes nm_energy.json and the figure
nm_energy.

Usage: python3 nm_energy.py --run RUNDIR [--stride 3] [--groups 20 24 27 29 31 33 35 36.3] --out DIR
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import load_figstyle   # noqa: E402
from nrpic import newton as nw     # noqa: E402
import nm_analyze as NA            # noqa: E402


def energy(X, U, M, alive):
    r = np.sqrt((X ** 2).sum(1))
    E = np.full(r.size, np.nan)
    idx = np.where(alive)[0]
    o = idx[np.argsort(r[idx])]
    menc = np.cumsum(M[o]) - 0.5 * M[o]
    E[o] = 0.5 * (U[o] ** 2).sum(1) - menc / r[o]
    return E, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--run", required=True)
    ap.add_argument("--stride", type=int, default=3)
    ap.add_argument("--groups", type=float, nargs="+", default=[20, 24, 27, 29, 31, 33, 35, 36.3])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    p = json.load(open(os.path.join(a.run, "setup.json")))
    n_tot, (d0, d1) = p["n_total"], p["tag_dust"]
    sh = np.asarray(p.get("shift", [0, 0, 0]))
    files = sorted(glob.glob(os.path.join(a.run, "infall.part.*.bin")))
    sel = list(range(0, len(files), a.stride))
    if sel[-1] != len(files) - 1:
        sel.append(len(files) - 1)

    def load(k):
        t, _, x, u, m, tag = nw.read_snapshot(files[k])
        X = np.full((n_tot, 3), np.nan)
        U = np.full((n_tot, 3), np.nan)
        Mm = np.zeros(n_tot)
        X[tag], U[tag], Mm[tag] = x - sh, u, m
        return t, X, U, Mm

    t0, X0, U0, M = load(0)
    al0 = np.isfinite(X0[:, 0])
    E0, r0 = energy(X0, U0, M, al0)
    dust = np.zeros(n_tot, bool)
    dust[d0:d1] = True
    g = np.asarray(a.groups)
    gid = np.digitize(r0, g) - 1
    gid[~dust | (r0 < g[0]) | (r0 >= g[-1])] = -1
    crossed = np.zeros(n_tot, bool)
    out = dict(run=a.run, groups=g.tolist(), E0_median=[float(np.median(E0[gid == i])) for i in range(len(g) - 1)],
               series=[])
    for k in range(len(files)):
        # the crossing flag needs every snapshot; energies only at the selected ones
        t, X, U, Mm = load(k)
        al = np.isfinite(X[:, 0])
        crossed |= al & ((X * X0).sum(1) < 0)
        if k not in sel:
            continue
        E, r = energy(X, U, M, al)
        with np.errstate(invalid="ignore", divide="ignore"):
            vr = (X * U).sum(1) / r
        rta = NA.r_ta_from_velocity(r[al & dust], vr[al & dust])
        ok = al & dust & ~crossed & (r > 0.5 * rta if rta else True)
        row = dict(k=k, t=float(t), a=float(((p["t_i"] + t) / p["t_i"]) ** (2.0 / 3.0)), r_ta=rta, groups=[])
        for i in range(len(g) - 1):
            m_ = ok & (gid == i)
            if m_.sum() >= 50:
                d = (E[m_] - E0[m_]) / np.abs(E0[m_])
                row["groups"].append(dict(i=i, n=int(m_.sum()), med=float(np.median(d)),
                                          p16=float(np.percentile(d, 16)), p84=float(np.percentile(d, 84)),
                                          frac_vr_neg=float(np.mean(vr[m_] < 0))))
            else:
                row["groups"].append(dict(i=i, n=int(m_.sum())))
        out["series"].append(row)
    with open(os.path.join(a.out, "nm_energy.json"), "w") as f:
        json.dump(out, f, indent=1)
    # summary table: the last value of each group before it leaves the single-stream region
    lines = ["# group r0 range, E0 median, then dE/|E0| (median) at a/a_i = 2, 4, 8, 16, 24, last available"]
    for i in range(len(g) - 1):
        vals = []
        for aa in (2, 4, 8, 16, 24):
            rows = [s for s in out["series"] if abs(s["a"] / aa - 1) < 0.06 and "med" in s["groups"][i]]
            vals.append(f"{rows[0]['groups'][i]['med']:+.4f}" if rows else "   -   ")
        last = [s for s in out["series"] if "med" in s["groups"][i]]
        vals.append(f"{last[-1]['groups'][i]['med']:+.4f} (a {last[-1]['a']:.2f})" if last else "-")
        lines.append(f"[{g[i]:.1f}, {g[i + 1]:.1f}) E0 {out['E0_median'][i]:+.4f}  " + "  ".join(vals))
    txt = "\n".join(lines) + "\n"
    open(os.path.join(a.out, "nm_energy.txt"), "w").write(txt)
    print(txt)

    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.5, 4.2))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.13, top=0.97)
    cols = fs.series_colors(len(g) - 1) if hasattr(fs, "series_colors") else None
    for i in range(len(g) - 1):
        av = [s["a"] for s in out["series"] if "med" in s["groups"][i]]
        md = [s["groups"][i]["med"] for s in out["series"] if "med" in s["groups"][i]]
        lo = [s["groups"][i]["p16"] for s in out["series"] if "med" in s["groups"][i]]
        hi = [s["groups"][i]["p84"] for s in out["series"] if "med" in s["groups"][i]]
        c = cols[i] if cols is not None else None
        ax.plot(av, md, color=c, lw=1.2, label=f"$r_0$ in [{g[i]:g}, {g[i + 1]:g}) $M$")
        ax.fill_between(av, lo, hi, color=c, alpha=0.15, lw=0)
    ax.axhline(0, **fs.GUIDE)
    ax.set_xscale("log")
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel(r"$[E(t) - E(0)]/|E(0)|$, single-stream shells")
    ax.legend(fontsize=6.5, loc="upper left", ncol=2)
    fs.save(fig, os.path.join(a.out, "nm_energy"))


if __name__ == "__main__":
    main()
