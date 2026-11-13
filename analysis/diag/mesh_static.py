"""Circular orbit (r = 8 M) of a test particle in Schwarzschild with the Kerr-Schild
metric sampled on the mesh: orbit, radius drift, conservation of the energy and of
L_z against the exact metric, and the deposition identity.

    python3 mesh_static.py [<rundir>] [--out NAME]

<rundir> defaults to runs/dev/mesh_static (basename ``mesh``).
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, H, floor_log, ks_schwarzschild, parse_cli, read_nrpic_hst, \
    read_traj_tagged, run_path
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], defaults=["runs/dev/mesh_static"], options=("out",))
label, d = runs[0]
out = opts.get("out", "mesh_static")
M, R_ORB = 1.0, 8.0
DX, MB = 0.25, 8.0           # cell size and MeshBlock width of the test mesh
FLOOR = 1e-17

tr = read_traj_tagged(run_path(d, "mesh.traj.bin"))[0]
t, x, u = tr[:, 0], tr[:, 2:5], tr[:, 5:8]
q = ks_schwarzschild(x, u, M)
E_ex = (1 - 2 * M / R_ORB) / np.sqrt(1 - 3 * M / R_ORB)
L_ex = np.sqrt(M * R_ORB) / np.sqrt(1 - 3 * M / R_ORB)
Lz = x[:, 0] * u[:, 1] - x[:, 1] * u[:, 0]
dE = q["E"] / E_ex - 1
dL = Lz / L_ex - 1
h = read_nrpic_hst(run_path(d, "mesh.nrpic.hst"))
res, low = floor_log(h[:, H["int_e"]] / h[:, H["sum_mw"]] - 1, FLOOR)

# phase drift relative to the exact angular frequency, for the record
Om = np.sqrt(M / R_ORB ** 3)
phi = np.unwrap(np.arctan2(x[:, 1], x[:, 0]))
print(f"{label}: t_end = {t[-1]:.3f} M, {phi[-1] / (2 * np.pi):.3f} orbits")
print(f"  r - 8 in [{(q['r'] - R_ORB).min():.3e}, {(q['r'] - R_ORB).max():.3e}],"
      f" final {(q['r'][-1] - R_ORB):.3e}")
print(f"  |E/E_exact - 1| max {np.abs(dE).max():.3e}, final {dE[-1]:.3e}")
print(f"  |Lz/Lz_exact - 1| max {np.abs(dL).max():.3e}, final {dL[-1]:.3e}")
print(f"  phase error at end: {phi[-1] - Om * t[-1]:.3e} rad")
print(f"  deposition residual max {np.abs(h[:, H['int_e']] / h[:, H['sum_mw']] - 1).max():.3e}"
      f", exact zeros {low.sum()} of {len(low)}")
print(f"  pusher iterations max {h[:, H['push_maxit']].max():.0f},"
      f" unconverged {h[:, H['push_unconverged']].max():.0f}")

fs.use_style()
fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.55))
ax0 = fs.inch_axes(fig, 0.66, 0.535, 3.8, 3.8)
x0r, w0, hs, gap = 5.47, 2.36, 0.95, 0.05
ax1, ax2, ax2b, ax3 = [fs.inch_axes(fig, x0r, 0.46 + i * (hs + gap), w0, hs)
                       for i in (3, 2, 1, 0)]

# orbit with the MeshBlock faces (grey) and the horizon
for xb in (-MB / 2 - MB, -MB / 2, MB / 2, MB / 2 + MB):
    ax0.axvline(xb, **{**fs.MASK_LINE, "lw": 1.0})
    ax0.axhline(xb, **{**fs.MASK_LINE, "lw": 1.0})
ph = np.linspace(0, 2 * np.pi, 400)
ax0.plot(R_ORB * np.cos(ph), R_ORB * np.sin(ph), **fs.GUIDE, label="exact orbit")
ax0.plot(x[:, 0], x[:, 1], color=fs.PAL["red"], lw=1.0, label="mesh metric")
ax0.add_patch(plt.Circle((0, 0), 2 * M, color="k", zorder=4))
ax0.text(0, -2.6, "black hole", ha="center", va="top")
ax0.text(-4.0 + 0.2, -10.2, "MeshBlock faces", color="grey", va="bottom",
         fontsize="small")
ax0.set_xlim(-10.5, 10.5)
ax0.set_ylim(-10.5, 10.5)
ax0.set_aspect("equal")
ax0.set_xticks([-10, -5, 0, 5, 10])
ax0.set_yticks([-10, -5, 0, 5, 10])
ax0.set_xlabel(r"$x\,[M]$")
ax0.set_ylabel(r"$y\,[M]$")
ax0.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.0))

ax1.axhline(0.0, **fs.GUIDE)
ax1.plot(t, (q["r"] - R_ORB) * 1e3, color=fs.PAL["red"])
ax1.set_ylabel(r"$r-8M$" "\n" r"$[10^{-3}M]$")
ax1.set_ylim(-0.25, 1.45)
ax1.text(0.5, 0.3, f"dx = {DX:g} M", transform=ax1.transAxes, ha="center")

ax2.axhline(0.0, **fs.GUIDE)
ax2.plot(t, dE * 1e6, color=fs.PAL["red"], lw=0.5)
ax2.set_ylabel(r"$E/E_{\rm exact}-1$" "\n" r"$[10^{-6}]$")
ax2.set_ylim(-1.2, 1.2)
ax2b.axhline(0.0, **fs.GUIDE)
ax2b.plot(t, dL * 1e6, color=fs.PAL["red"], lw=0.5)
ax2b.set_ylabel(r"$L_z/L_{z,\rm exact}-1$" "\n" r"$[10^{-6}]$")
ax2b.set_ylim(-6.5, 6.5)

th = h[:, H["time"]]
ax3.plot(th[~low], res[~low], color=fs.PAL["red"], marker="o", ms=2.0, ls="none")
ax3.plot(th[low], res[low], color=fs.PAL["red"], marker="o", ms=2.0, ls="none",
         mfc="white", mew=0.6)
ax3.set_yscale("log")
ax3.set_ylim(4e-18, 6e-15)
ax3.axhline(2.22e-16, **fs.MASK_LINE)
ax3.text(0.99, 0.57, r"$\epsilon_{\rm mach}$", transform=ax3.transAxes, ha="right",
         color="grey", va="bottom")
ax3.set_ylabel(r"$|\int\! E\,/$" "\n" r"$\sum mW-1|$")
ax3.text(0.02, 0.2, r"open: exact 0, drawn at $10^{-17}$", transform=ax3.transAxes,
         fontsize="small")
for a in (ax1, ax2, ax2b, ax3):
    a.set_xlim(0, t[-1])
    a.yaxis.set_label_coords(-0.25, 0.5)
for a in (ax1, ax2, ax2b):
    a.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
ax3.set_yticks([1e-17, 1e-16, 1e-15])
fs.no_minor_labels(ax3)
ax3.set_xlabel(r"$t\,[M]$", labelpad=-2)
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
