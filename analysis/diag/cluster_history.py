"""Relativistic star clusters (basename ``st``): central lapse, Lagrangian radii,
particle bookkeeping, constraint norms, centre of mass and momentum drift.

    python3 cluster_history.py <label>=<rundir> [...] [--base st] [--yc Y] [--every K]
                               [--out NAME]

Top left: central lapse (probe at the origin) against t; black dashed: alpha_c of the
equilibrium model y_c (taken from --yc, else from the "yc" entry of a *.json file in
the first run directory).
Top right: coordinate radii enclosing 10, 20, ..., 90 percent of the surviving rest
mass about the instantaneous (rest-mass weighted, coordinate) centre of mass, from
the snapshots; the median (50 percent) is drawn thicker; black dashed: the same
radii of the equilibrium model (isotropic radius).
Middle left: losses, as fractions on a log axis: (N_0 - N)/N_0 (solid), excised rest
mass / initial rest mass (dashed), escaped rest mass / initial (dotted); the legend
gives N at the start and end. Panels without any loss say so.
Middle right: constraint norms (int H^2 dV)^(1/2) (solid) and (int M_i M^i dV)^(1/2)
(dashed) from <base>.z4c.user.hst.
Bottom left: centre of mass from the snapshots, components x, y, z as solid, dashed,
dotted.
Bottom right: drift of the particle momentum sum, sum m u_i (t) - sum m u_i (0) from
<base>.nrpic.hst, over the initial rest mass; components as solid, dashed, dotted.
--every K uses every K-th snapshot only (default 1).
"""
import glob
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, H, parse_cli, read_athena_hst, read_nrpic_hst, read_snapshot, \
    run_path, snapshot_files
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], options=("base", "yc", "every", "out"))
base = opts.get("base", "st")
out = opts.get("out", "cluster_history")
every = int(opts.get("every", 1))
QS = np.arange(1, 10) / 10.0
colors = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
LS = ["-", "--", ":"]


def model_yc(d):
    if "yc" in opts:
        return float(opts["yc"])
    for p in sorted(glob.glob(run_path(d, "*.json"))):
        try:
            j = json.load(open(p))
        except (OSError, ValueError):
            continue
        if "yc" in j:
            return float(j["yc"])
    return None


def lagrangian(files):
    """Times, centre of mass [n,3], Lagrangian radii [n,9], particle number."""
    T, C, R, N = [], [], [], []
    for p in files:
        t, d, tag, _ = read_snapshot(p)
        T.append(t)
        N.append(len(tag))
        if len(tag) == 0:
            C.append([np.nan] * 3)
            R.append([np.nan] * len(QS))
            continue
        m, x = d[:, 6], d[:, :3]
        c = (m[:, None] * x).sum(0) / m.sum()
        r = np.sqrt(((x - c) ** 2).sum(1))
        o = np.argsort(r)
        F = np.cumsum(m[o]) / m.sum()
        C.append(c)
        R.append(np.interp(QS, F, r[o]))
    return np.array(T), np.array(C), np.array(R), np.array(N)


fs.use_style()
fig, axes = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 7.6), sharex=True)
fig.subplots_adjust(left=0.1, right=0.985, bottom=0.06, top=0.985, wspace=0.3,
                    hspace=0.07)
(a_lap, a_rad), (a_num, a_con), (a_com, a_mom) = axes
tmax = 0.0
anyloss = False
mom, com = [], []
yc = model_yc(runs[0][1]) if runs else None
for (label, d), c in zip(runs, colors):
    hp = run_path(d, f"{base}.nrpic.hst")
    if not os.path.exists(hp):
        print(f"{label}: no {base}.nrpic.hst in {d} yet, skipped")
        continue
    h = read_nrpic_hst(hp)
    t = h[:, H["time"]]
    tmax = max(tmax, t[-1])
    m0 = h[0, H["sum_m"]]
    a_lap.plot(t, h[:, H["alpha_probe"]], color=c, label=label)
    n0 = h[0, H["np"]]
    for q, ls in ((1.0 - h[:, H["np"]] / n0, "-"), (h[:, H["m_excised"]] / m0, "--"),
                  (h[:, H["m_escaped"]] / m0, ":")):
        pos = q > 0
        anyloss |= bool(pos.any())
        a_num.plot(t[pos], q[pos], color=c, ls=ls)
    a_num.plot([], [], color=c, label=f"N: {n0:.0f} to {h[-1, H['np']]:.0f}")
    mom.append((t, [(h[:, H[q]] - h[0, H[q]]) / m0 for q in ("sum_mux", "sum_muy",
                                                              "sum_muz")], c))
    print(f"{label}: t = {t[0]:.2f} .. {t[-1]:.2f}; alpha_c {h[0, H['alpha_probe']]:.5f} "
          f"-> {h[-1, H['alpha_probe']]:.5f} (min {h[:, H['alpha_probe']].min():.5f}); "
          f"N {h[0, H['np']]:.0f} -> {h[-1, H['np']]:.0f}; excised {h[-1, H['m_excised']]:.3e},"
          f" escaped {h[-1, H['m_escaped']]:.3e}; momentum drift "
          + ", ".join(f"{(h[-1, H[q]] - h[0, H[q]]) / m0:+.2e}"
                      for q in ("sum_mux", "sum_muy", "sum_muz")))
    z = read_athena_hst(run_path(d, f"{base}.z4c.user.hst"))
    if z:
        Hn, Mn = np.sqrt(z["H-norm2"]), np.sqrt(z["M-norm2"])
        a_con.plot(z["time"][Hn > 0], Hn[Hn > 0], color=c)
        a_con.plot(z["time"][Mn > 0], Mn[Mn > 0], color=c, ls="--")
        print(f"   ||H|| {Hn[0]:.3e} -> {Hn[-1]:.3e} (max {Hn.max():.3e}); ||M|| -> "
              f"{Mn[-1]:.3e} (max {Mn.max():.3e})")
    files = snapshot_files(d, base)[::every]
    if files:
        T, C, R, N = lagrangian(files)
        for k in range(len(QS)):
            a_rad.plot(T, R[:, k], color=c, lw=2.2 if QS[k] == 0.5 else 0.9,
                       zorder=3 if QS[k] == 0.5 else 2)
        com.append((T, C, c))
        print(f"   {len(files)} snapshots t = {T[0]:.1f} .. {T[-1]:.1f}; r50 {R[0, 4]:.4f} -> "
              f"{R[-1, 4]:.4f}; r10 {R[0, 0]:.4f} -> {R[-1, 0]:.4f}; r90 {R[0, 8]:.4f} -> "
              f"{R[-1, 8]:.4f}; |com| max {np.nanmax(np.sqrt((C ** 2).sum(1))):.3e}")
    else:
        print("   no snapshots")

if yc is not None:
    from nrpic.st_cluster import STModel
    mod = STModel(yc)
    a_lap.axhline(mod.alpha_c, **fs.GUIDE, label=rf"equilibrium $y_c={yc:g}$")
    for r in mod.Finv(QS):
        a_rad.axhline(r, color="k", lw=0.8, ls="--", zorder=1)
    print(f"model y_c = {yc}: alpha_c = {mod.alpha_c:.5f}, radii "
          + " ".join(f"{r:.3f}" for r in mod.Finv(QS)))

a_lap.set_ylabel(r"$\alpha_c$")
a_lap.legend(loc="best", fontsize="small")
a_rad.set_ylabel(r"$r_{10\ldots90\%}\,[M]$")
a_rad.plot([], [], color="k", lw=2.2, label="50 %")
a_rad.plot([], [], color="k", lw=0.9, label="10, 20, ..., 90 %")
if yc is not None:
    a_rad.plot([], [], color="k", lw=0.8, ls="--", label="equilibrium")
a_rad.legend(loc="upper left", fontsize="small", ncol=3, columnspacing=0.8,
             handlelength=1.5)
a_rad.set_ylim(bottom=0)
ylo, yhi = a_rad.get_ylim()
a_rad.set_ylim(0, yhi * 1.18)
a_num.set_yscale("log")
a_num.set_ylabel("lost fraction")
for ls, lab in (("-", r"$1-N/N_0$"), ("--", r"$m_{\rm exc}/m_0$"),
                ("::", r"$m_{\rm esc}/m_0$")):
    a_num.plot([], [], color="k", ls=ls[:2] if ls != "::" else ":", label=lab)
a_num.legend(loc="upper left", fontsize="small", ncol=2)
if not anyloss:
    a_num.set_ylim(1e-5, 1)
    a_num.text(0.5, 0.45, "no particle excised or escaped", transform=a_num.transAxes,
               ha="center", color="grey")
a_con.set_yscale("log")
a_con.set_ylabel(r"$\|H\|$ (solid), $\|M\|$ (dashed)")
fs.no_minor_labels(a_con)
big = max([np.nanmax(np.abs(C)) for _, C, _ in com if np.isfinite(C).any()] + [1e-300])
exc = int(np.floor(np.log10(big))) if big > 1e-300 else 0
exc = 0 if exc >= -1 else exc
for T, C, c in com:
    for k in range(3):
        a_com.plot(T, C[:, k] / 10.0 ** exc, color=c, ls=LS[k])
a_com.axhline(0.0, **fs.MASK_LINE)
a_com.set_ylabel(r"$x_{\rm cm}^i\,[M]$" if exc == 0 else
                 r"$x_{\rm cm}^i\,[10^{%d}M]$" % exc)
a_com.plot([], [], color="k", ls="-", label="x")
a_com.plot([], [], color="k", ls="--", label="y")
a_com.plot([], [], color="k", ls=":", label="z")
a_com.legend(loc="upper left", ncol=3, fontsize="small")
# momentum drift, scaled by a common power of ten
big = max([np.abs(np.concatenate(v)).max() for _, v, _ in mom] + [1e-300])
ex = int(np.floor(np.log10(big))) if big > 1e-300 else 0
for t, v, c in mom:
    for k in range(3):
        a_mom.plot(t, v[k] / 10.0 ** ex, color=c, ls=LS[k])
a_mom.axhline(0.0, **fs.MASK_LINE)
a_mom.set_ylabel(r"$\Delta\sum m u_i\,/\,m_0\;[10^{%d}]$" % ex)
for ax in axes[-1]:
    ax.set_xlabel(r"$t\,[M]$", labelpad=-2)
for ax in axes.ravel():
    ax.set_xlim(0, max(tmax, 1e-6))
for ax in axes.ravel():
    ax.yaxis.set_label_coords(-0.15, 0.5)
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
