"""Test particles (tracers) around an evolved black hole: trajectories, L_z, coordinate
energy and areal radius of each tracked particle, from <base>.traj.bin and
<base>.trajmet.bin (metric reconstructed at the particle, mesh-metric runs only).

    python3 tracers.py <rundir> [--base punc] [--tags 0,1,2] [--lim L] [--out NAME]

Left: trajectories in the x-y (top) and x-z (bottom) planes; black disc: apparent
horizon (mean coordinate radius of the last horizon found, if a horizon file exists).
Open circles mark the start, filled circles the last record (excised particles stop).
Right, from top: L_z(t)/L_z(0) - 1 with L_z = x u_y - y u_x (particles with L_z(0) = 0
are left out and their |L_z| printed); E(t)/E(0) - 1 of the coordinate energy
E = alpha W - beta^i u_i with W = (1 + gamma^ij u_i u_j)^(1/2) from the recorded
gamma_ij (both scaled by a common power of ten given on the axis); the areal radius
R = r <(gamma_ij t^i t^j)^(1/2)>, averaged over two unit coordinate vectors t
orthogonal to the radial direction (exact for a conformally flat or spherically
symmetric slice). Black dashed lines in the R panel: the initial values, i.e. the
areal radius on the time-symmetric initial slice.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, inv_sym3, parse_cli, read_horizon, read_traj_tagged, run_path
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], options=("base", "tags", "lim", "out"))
if not runs:
    sys.exit(__doc__)
label, d = runs[0]
base = opts.get("base", "punc")
out = opts.get("out", f"tracers_{label}")

tr = read_traj_tagged(run_path(d, f"{base}.traj.bin"), 8)
tm = read_traj_tagged(run_path(d, f"{base}.trajmet.bin"), 12)
if not tr:
    sys.exit(f"no {base}.traj.bin in {d}")
tags = sorted(tr)
if "tags" in opts:
    tags = [int(v) for v in opts["tags"].split(",")]


def derived(a, m):
    """L_z, E, W, R on the common times of trajectory a and metric m."""
    t, ia, im = np.intersect1d(a[:, 0], m[:, 0], return_indices=True)
    a, m = a[ia], m[im]
    x, u = a[:, 2:5], a[:, 5:8]
    alp, beta = m[:, 2], m[:, 3:6]
    gxx, gxy, gxz, gyy, gyz, gzz = m[:, 6:12].T
    (uxx, uxy, uxz, uyy, uyz, uzz), det = inv_sym3(gxx, gxy, gxz, gyy, gyz, gzz)
    ux, uy, uz = u.T
    uu = (uxx * ux * ux + uyy * uy * uy + uzz * uz * uz
          + 2 * (uxy * ux * uy + uxz * ux * uz + uyz * uy * uz))
    W = np.sqrt(1.0 + uu)
    E = alp * W - (beta * u).sum(1)
    # areal radius from two unit vectors orthogonal to n = x/r
    r = np.sqrt((x ** 2).sum(1))
    n = x / r[:, None]
    ref = np.where(np.abs(n[:, 2:3]) < 0.9, [[0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0]])
    t1 = np.cross(ref, n)
    t1 /= np.sqrt((t1 ** 2).sum(1))[:, None]
    t2 = np.cross(n, t1)
    G = np.stack([np.stack([gxx, gxy, gxz], -1), np.stack([gxy, gyy, gyz], -1),
                  np.stack([gxz, gyz, gzz], -1)], -2)
    q1 = np.sqrt(np.einsum("ni,nij,nj->n", t1, G, t1))
    q2 = np.sqrt(np.einsum("ni,nij,nj->n", t2, G, t2))
    R = r * 0.5 * (q1 + q2)
    Lz = x[:, 0] * u[:, 1] - x[:, 1] * u[:, 0]
    return dict(t=t, x=x, Lz=Lz, E=E, W=W, R=R, r=r, alpha=alp, det=det)


tracks = {}
for k in tags:
    if k not in tr:
        print(f"tag {k}: not in {base}.traj.bin")
        continue
    a = tr[k]
    if k in tm:
        tracks[k] = derived(a, tm[k])
    else:
        x = a[:, 2:5]
        tracks[k] = dict(t=a[:, 0], x=x, Lz=x[:, 0] * a[:, 6] - x[:, 1] * a[:, 5],
                         E=None, R=None, r=np.sqrt((x ** 2).sum(1)))
        print(f"tag {k}: no metric records (not a mesh-metric run?)")
for k, q in tracks.items():
    s = (f"tag {k}: t = {q['t'][0]:.2f} .. {q['t'][-1]:.2f} ({len(q['t'])} records), "
         f"r {q['r'][0]:.3f} -> {q['r'][-1]:.3f}")
    L0 = q["Lz"][0]
    if abs(L0) > 1e-6:
        s += f"; L_z(0) = {L0:.6f}, max|dL_z/L_z| = {np.abs(q['Lz'] / L0 - 1).max():.2e}"
    else:
        s += f"; L_z(0) = {L0:.1e}, max|L_z| = {np.abs(q['Lz']).max():.2e}"
    if q["E"] is not None:
        s += (f"; E {q['E'][0]:.6f} -> {q['E'][-1]:.6f} (max|dE/E| "
              f"{np.abs(q['E'] / q['E'][0] - 1).max():.2e}); R {q['R'][0]:.4f} -> "
              f"{q['R'][-1]:.4f} (min {q['R'].min():.4f}, max {q['R'].max():.4f})")
    print(s)

fs.use_style()
fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.8))
P = 2.58
axy = fs.inch_axes(fig, 0.62, 0.45 + P + 0.12, P, P)
axz = fs.inch_axes(fig, 0.62, 0.45, P, P)
hs, gap, x0, w = 1.72, 0.06, 4.38, 3.47
aL, aE, aR = [fs.inch_axes(fig, x0, 0.45 + i * (hs + gap), w, hs) for i in (2, 1, 0)]
PALETTE = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"], "#7B3FA0",
           "#17A2B8"]
cols = (PALETTE if len(tracks) <= len(PALETTE) else fs.series_colors(len(tracks)))


def pow10(arrays):
    big = max([np.abs(v).max() for v in arrays if len(v)] + [1e-300])
    return int(np.floor(np.log10(big))) if big > 1e-300 else 0


relL = {k: q["Lz"] / q["Lz"][0] - 1 for k, q in tracks.items() if abs(q["Lz"][0]) > 1e-6}
relE = {k: q["E"] / q["E"][0] - 1 for k, q in tracks.items() if q["E"] is not None}
eL, eE = pow10(list(relL.values())), pow10(list(relE.values()))
lim = float(opts["lim"]) if "lim" in opts else 1.08 * max(
    np.abs(q["x"]).max() for q in tracks.values())
ah = read_horizon(run_path(d, f"{base}.horizon_summary_0.txt"))
if len(ah):
    for ax in (axy, axz):
        ax.add_patch(plt.Circle((0, 0), ah[-1, 5], color="k", zorder=5))
    print(f"apparent horizon: first at t = {ah[0, 0]:.2f}, last t = {ah[-1, 0]:.2f}, "
          f"mass {ah[-1, 1]:.5f}, mean coordinate radius {ah[-1, 5]:.4f}")
tmax = max(q["t"][-1] for q in tracks.values())
for (k, q), c in zip(tracks.items(), cols):
    axy.plot(q["x"][:, 0], q["x"][:, 1], color=c, lw=0.8, label=f"{k}")
    axz.plot(q["x"][:, 0], q["x"][:, 2], color=c, lw=0.8)
    for ax, j in ((axy, 1), (axz, 2)):
        ax.plot(q["x"][0, 0], q["x"][0, j], marker="o", ms=3.5, mfc="white", color=c,
                zorder=6)
        ax.plot(q["x"][-1, 0], q["x"][-1, j], marker="o", ms=3, color=c, zorder=6)
    if k in relL:
        aL.plot(q["t"], relL[k] / 10.0 ** eL, color=c, lw=0.8)
    if q["E"] is not None:
        aE.plot(q["t"], relE[k] / 10.0 ** eE, color=c, lw=0.8)
        aR.plot(q["t"], q["R"], color=c)
        aR.axhline(q["R"][0], color="k", lw=0.8, ls="--", zorder=1)
for ax, lab in ((axy, r"$y\,[M]$"), (axz, r"$z\,[M]$")):
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_ylabel(lab)
axy.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
axz.set_xlabel(r"$x\,[M]$", labelpad=-2)
axz.legend(*axy.get_legend_handles_labels(), title="tag", loc="lower center",
           ncol=min(6, len(tracks)), fontsize="small", columnspacing=0.8,
           handlelength=1.0, handletextpad=0.3, title_fontsize="small")
aL.axhline(0.0, **fs.GUIDE)
aL.set_ylabel(r"$L_z/L_z(0)-1$" + ("" if eL == 0 else r" $[10^{%d}]$" % eL))
aE.axhline(0.0, **fs.GUIDE)
aE.set_ylabel(r"$E/E(0)-1$" + ("" if eE == 0 else r" $[10^{%d}]$" % eE))
aR.set_ylabel(r"$R\,[M]$")
for ax in (aL, aE):
    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
for ax in (aL, aE, aR):
    ax.set_xlim(0, tmax)
    ax.yaxis.set_label_coords(-0.13, 0.5)
aR.set_xlabel(r"$t\,[M]$", labelpad=-2)
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
