"""Radial tables of the compressed Shapiro-Teukolsky cluster (y_c = 0.756, dpert = 0.1):
the equilibrium table used so far (= the unperturbed model) against the table that
solves the Hamiltonian constraint for the compressed particles (st_cluster.PerturbedST).

    python3 ic_dpert_consistency.py [--new TAB] [--old TAB] [--yc 0.756] [--dpert 0.1]
                                    [--out ic_dpert_consistency]

Top: psi - 1 and alpha against the isotropic radius; dotted, the equilibrium profile
compressed with the matter (psi_0(r/s), alpha_0(r/s)), the start of the iteration.
Bottom left: new - old table. Bottom right: |Lap psi + 2 pi D/psi| on the table rows
(sixth-order differences, step 4 dr) over the central source 2 pi D_c/psi_c, for the
compressed matter (solid) and, for the old table, its own unperturbed matter (dashed);
drawn is the maximum over windows of 25 rows (the floor ~1e-9 is round-off of the
second difference).
Grey band: |r - r_s'| < 0.05 r_s' (the source ~ (r_s - r)^(1/2) is not differentiable
at the surface, so no difference stencil across it is meaningful). Without --new/--old
the tables are recomputed; with them the files are read.
"""
import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, REPO
from nrpic import figstyle as fs
from nrpic import io as nio
from nrpic import st_cluster as stc

p = argparse.ArgumentParser()
p.add_argument("--yc", type=float, default=0.756)
p.add_argument("--dpert", type=float, default=0.1)
p.add_argument("--new", default=os.path.join(
    REPO, "runs/st/ic_yc0756_dp0p1_consistent/st_yc0p756_stratified_N10000_s1_dp0p1_hc.tab"))
p.add_argument("--old", default=os.path.join(
    REPO, "runs/st/reconf_yc0756/st_yc0p756_stratified_N10000_s1_dp0p1.tab"))
p.add_argument("--out", default="ic_dpert_consistency")
a = p.parse_args()

md = stc.STModel(a.yc)
pst = stc.PerturbedST(md, a.dpert)
s, rs_new, rs_old = pst.s, pst.rbar_s, md.rbar_s


def load(path, fallback):
    if path and os.path.exists(path):
        r, u, al, _ = nio.read_tab(path)
        print(f"read {os.path.relpath(path, REPO)}: {len(r)} rows, dr = {r[1]:.6g}")
        return r, u, al
    print(f"{path} not found: recomputed")
    return fallback()


rn, un, an = load(a.new, pst.table_arrays)
ro, uo, ao = load(a.old, lambda: stc.table_arrays(md))
# the files must be the tables of these models
assert np.max(np.abs(un - pst.table_arrays()[1])) < 1e-15
assert np.max(np.abs(uo - stc.table_arrays(md)[1])) < 1e-15

src_c = float(pst.source(np.array([0.0]))[0])
res_new = stc.radial_laplacian_hi(rn, 1 + un) + pst.source(rn, 1 + un)
res_old = stc.radial_laplacian_hi(ro, 1 + uo) + pst.source(ro, 1 + uo)
res_old_eq = stc.radial_laplacian_hi(ro, 1 + uo) + 2 * np.pi * md.rho(ro) * (1 + uo) ** 5
band = 0.05 * rs_new


def far(r, rs):
    return np.isfinite(r) & (np.abs(r - rs) > 0.05 * rs)


ok_n = far(rn, rs_new) & np.isfinite(res_new)
ok_o = far(ro, rs_new) & far(ro, rs_old) & np.isfinite(res_old)
print(f"s = {s:.10f}, r_s = {rs_old:.6f} -> r_s' = {rs_new:.6f}, M' = {pst.M:.12f}")
print(f"psi_c: old {1 + uo[0]:.12f}  new {1 + un[0]:.12f};  alpha_c: old {ao[0]:.12f}  "
      f"new {an[0]:.12f}")
print(f"central source 2 pi D_c/psi_c = {src_c:.6e}")
print(f"residual / central source (|r - r_s| > 5%): new table {np.max(np.abs(res_new[ok_n])) / src_c:.2e} "
      f"(abs {np.max(np.abs(res_new[ok_n])):.2e}); old table, compressed matter "
      f"{np.max(np.abs(res_old[ok_o])) / src_c:.2e}; old table, own matter "
      f"{np.nanmax(np.abs(res_old_eq[ok_o])) / src_c:.2e}")
I_old, rel_old = pst.equilibrium_table_mismatch()
print(f"old table: int D/psi_0 d^3x = {I_old:.12f} vs monopole 1 -> {rel_old:+.4e}")

fs.use_style()
fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.6))
w, h, x0, x1, y0, y1 = 3.15, 2.2, 0.82, 4.72, 0.5, 3.12
ax_p = fs.inch_axes(fig, x0, y1, w, h)
ax_a = fs.inch_axes(fig, x1, y1, w, h)
ax_d = fs.inch_axes(fig, x0, y0, w, h)
ax_r = fs.inch_axes(fig, x1, y0, w, h)
B, R, Y = fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"]
rr = np.linspace(0, ro[-1], 2000)

ax_p.plot(ro, uo, color=B, label="equilibrium = old table")
ax_p.plot(rr, np.where(rr <= rs_new, md.psi(rr / s) - 1, np.nan), color=Y, ls=":",
          label=r"$\psi_0(r/s)$")
ax_p.plot(rn, un, color=R, label=f"consistent, $d = {a.dpert:g}$")
ax_a.plot(ro, ao, color=B, label="equilibrium = old table")
ax_a.plot(rr, np.where(rr <= rs_new, md.alpha(rr / s), np.nan), color=Y, ls=":",
          label=r"$\alpha_0(r/s)$")
ax_a.plot(rn, an, color=R, label=f"consistent, $d = {a.dpert:g}$")

m = rn <= ro[-1]
dpsi = un[m] - np.interp(rn[m], ro, uo)
dal = an[m] - np.interp(rn[m], ro, ao)
ax_d.plot(rn[m], dpsi, color=R, label=r"$\psi_\mathrm{new} - \psi_\mathrm{old}$")
ax_d.plot(rn[m], dal, color=R, ls="--", label=r"$\alpha_\mathrm{new} - \alpha_\mathrm{old}$")
ax_d.axhline(0, **fs.THIN)

def envelope(res, ok, k=25):
    """Maximum of |res| over consecutive windows of k rows (NaN where any row of the
    window is excluded), drawn at the window centres."""
    v = np.where(ok, np.abs(res), np.nan)
    n = len(v) // k
    return np.max(v[: n * k].reshape(n, k), axis=1)


for r_, res, ok, c, ls, lab in ((ro, res_old, ok_o, B, "-", "old table"),
                                (ro, res_old_eq, ok_o, B, "--", "old table, own matter"),
                                (rn, res_new, ok_n, R, "-", "new table")):
    k = 25
    rc = r_[: len(r_) // k * k].reshape(-1, k).mean(axis=1)
    ax_r.semilogy(rc, envelope(res, ok, k) / src_c, color=c, ls=ls, label=lab)
ax_r.axvspan(rs_new - band, rs_old + 0.05 * rs_old, color="grey", alpha=0.15, lw=0)
ax_r.set_ylim(1e-12, 1)

for ax in (ax_p, ax_a, ax_d, ax_r):
    ax.set_xlim(0, ro[-1])
    for rs in (rs_new, rs_old):
        ax.axvline(rs, **fs.MASK_LINE)
for ax in (ax_p, ax_a):
    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
ax_p.set_ylabel(r"$\psi - 1$")
ax_a.set_ylabel(r"$\alpha$")
ax_d.set_ylabel(r"new $-$ old table")
ax_r.set_ylabel(r"$|\nabla^2\psi + 2\pi D/\psi|\;/\;2\pi D_c\psi_c^{-1}$")
for ax in (ax_d, ax_r):
    ax.set_xlabel(r"$r\,[M]$", labelpad=-2)
ax_p.legend(loc="upper right")
ax_a.legend(loc="upper left")
ax_d.legend(loc="upper right")
ax_r.legend(loc="center left", ncol=1, bbox_to_anchor=(0.0, 0.45))
ax_p.text(0.03, 0.06, f"$y_c = {a.yc:g}$, $M' = {pst.M:.6f}$", transform=ax_p.transAxes)
print("\n".join(fs.save(fig, os.path.join(FIGS, a.out))))
