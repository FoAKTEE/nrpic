"""Light rays in the homogeneous universe: redshift and luminosity distance of the
bundles against the exact matter-dominated relations (cosmo/TESTLOG.md, C3 first test).

    python3 ray_test_flrw.py <rundir> [--dt 0.03125] [--out NAME]

The dashed curves are the expected error of the pusher, which centres the metric in
time: the coordinate speed of light is low by (H_c dt)^2 / 8, H_c the conformal Hubble
rate, so the distance travelled since the emission is low by the mean of that.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, HERE)
from nrpic import figstyle as fs  # noqa: E402
import ray_obs as ar  # noqa: E402

args = sys.argv[1:]
rundir = args[0]
opt = {args[i][2:]: args[i+1] for i in range(1, len(args) - 1, 2)}
dt = float(opt.get("dt", "0.03125"))
out = opt.get("out", "ray_test_flrw")
bundles = ar.gr_bundles(rundir, base="flrw")
fs.use_style()
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.10, right=0.985, bottom=0.17, top=0.95, wspace=0.28)
cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"]]
for b, c in zip(bundles, cols):
    t, te = b["t"], b["t_emit"]
    a, ae = (1.0 + 0.5*t)**2, (1.0 + 0.5*te)**2
    zex = a/ae - 1.0
    dex = 2.0*ae**1.5*(1.0 + zex)**2*(np.sqrt(1.0 + zex) - 1.0)
    lab = f"from point {b['kind'] + 1}, $a_e = {ae:.2f}$"
    ls = "-" if b["kind"] == 0 else ":"
    axs[0].semilogy(zex, np.abs(b["z"]/zex - 1.0), color=c, ls=ls, label=lab)
    axs[1].semilogy(zex, np.abs(b["D_L"]/dex - 1.0), color=c, ls=ls)
    pred = (dt*dt/8.0)*(2.0/(1.0 + 0.5*te) - 2.0/(1.0 + 0.5*t))/(t - te)
    axs[1].semilogy(zex, pred, color="k", ls="--", lw=0.8,
                    label="time-centred metric" if b is bundles[0] else None)
    print(f"bundle {b['bundle']}: solid angle - 1 = {b['solid_angle'] - 1.0:+.1e}; largest "
          f"|z/z_exact - 1| = {np.abs(b['z']/zex - 1.0).max():.2e}; largest "
          f"|D_L/D_exact - 1| = {np.abs(b['D_L']/dex - 1.0).max():.2e}; largest departure "
          f"from the expected error {np.abs(np.abs(b['D_L']/dex - 1.0) - pred).max():.2e}")
axs[0].set_xlabel(r"redshift $z$")
axs[0].set_ylabel("relative error of the redshift")
axs[0].set_ylim(1e-9, 1e-4)
axs[0].legend(frameon=False, loc="upper right", fontsize=7)
axs[1].set_xlabel(r"redshift $z$")
axs[1].set_ylabel("relative error of $D_L$")
axs[1].set_ylim(1e-6, 1e-3)
axs[1].legend(frameon=False, loc="upper right")
figdir = os.path.join(HERE, "figs")
fs.save(fig, os.path.join(figdir, out))
print(os.path.join(figdir, out + ".png"))
