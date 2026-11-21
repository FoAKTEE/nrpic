#!/usr/bin/env python3
"""V4 test of my second-order gauge piece on exact pure-gauge data (P4.1-P4.3, JOURNAL 12).

Periodic box of side 4, 32^3 cell centres. First-order metric h(x) = sum of plane waves with
random symmetric amplitudes (scalar, vector and tensor parts mixed), displacement
zeta(x) = sum of plane waves with random vector amplitudes (curl and divergence), both
scaled by eps. Exact transform: X = x + zeta(x), gamma'(x) = dX^T gamma(X) dX with gamma(X)
evaluated analytically at the displaced points. Measured:
  Delta = Lambda(h') - Lambda(h) (plain and conformal), the residuals Delta - G for the
  one-sided and symmetric forms, the conformal residual without the density term and with
  the plain formula, zeta recovered from the metric difference, and G with that zeta; all as
  rms over the grid and as the + coefficient at m = (1,1,0) (the scan's mode).
Writes $NRPIC_RUN_DIR/v4_gauge_test.json and v4_gauge_test.png/pdf.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
import exact  # noqa: E402
import figstyle as fs  # noqa: E402
import v4lib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v4t"))
os.makedirs(OUT, exist_ok=True)
L, N = 4.0, 32
grid = diag.Grid((N, N, N), (L, L, L), (0.0, 0.0, 0.0))
X0 = np.array(grid.coords())
rng = np.random.default_rng(20261120)
HM = [(1, 0, 0), (0, 1, 0), (0, 1, 1), (1, -1, 1)]
ZM = [(0, 1, 0), (1, 0, 0), (1, 1, 1), (0, 0, 1)]
HA = []
for m in HM:
    A = rng.normal(size=(3, 3))
    HA.append((np.asarray(m, float) * 2 * np.pi / L, 0.5 * (A + A.T), rng.uniform(0, 2 * np.pi)))
ZA = [(np.asarray(m, float) * 2 * np.pi / L, rng.normal(size=3) * L / (2 * np.pi), rng.uniform(0, 2 * np.pi))
      for m in ZM]


def h_at(X, eps):
    out = np.zeros((3, 3) + X.shape[1:])
    for K, A, ph in HA:
        out += eps * A[:, :, None, None, None] * np.cos(np.einsum("a,a...->...", K, X) + ph)
    return out


def zeta_and_grad(X, eps):
    z = np.zeros((3,) + X.shape[1:])
    dz = np.zeros((3, 3) + X.shape[1:])            # dz[c, k] = d_c zeta^k
    for K, B, ph in ZA:
        arg = np.einsum("a,a...->...", K, X) + ph
        z += eps * B[:, None, None, None] * np.sin(arg)
        dz += eps * K[:, None, None, None, None] * B[None, :, None, None, None] * np.cos(arg)
    return z, dz


EYE = np.eye(3)[:, :, None, None, None]
ep, ex, _, _, _ = exact.pol_tensors((1.0, 1.0, 0.0))


def cplus(T):
    return diag.mode_coeff(0.5 * np.einsum("ab,ab...->...", ep, T), grid, (1, 1, 0))


def rms(T):
    return float(np.sqrt(np.mean(T ** 2)))


rows = []
for eps in (2e-2, 1e-2, 5e-3, 2.5e-3, 1.25e-3):
    zeta, dz = zeta_and_grad(X0, eps)
    Xd = X0 + zeta
    gam_old = EYE + h_at(X0, eps)
    J = EYE + dz                                   # J[i, k] = d_i X^k
    gX = EYE + h_at(Xd, eps)
    gam_new = np.einsum("ik...,kl...,jl...->ij...", J, gX, J)
    rec = {"eps": eps}
    for lab, conf in (("plain", False), ("conformal", True)):
        if conf:
            h_old = v4lib.conformal(gam_old) - EYE
            h_new = v4lib.conformal(gam_new) - EYE
        else:
            h_old, h_new = gam_old - EYE, gam_new - EYE
        Delta = diag.tt_project(h_new, grid) - diag.tt_project(h_old, grid)
        G1 = v4lib.gauge_piece(zeta, grid, h_old=h_old, conformal=conf, form="one")
        G2 = v4lib.gauge_piece(zeta, grid, h_old=h_old, h_new=h_new, conformal=conf, form="sym")
        zB = v4lib.zeta_from_difference(h_new - h_old, grid, conformal=conf)
        GB = v4lib.gauge_piece(zB, grid, h_old=h_old, h_new=h_new, conformal=conf, form="sym")
        r = {"rms Delta": rms(Delta), "rms Delta-G one": rms(Delta - G1), "rms Delta-G sym": rms(Delta - G2),
             "rms Delta-G(zeta_B) sym": rms(Delta - GB),
             "zeta_B rel err": rms(zB - zeta) / rms(zeta),
             "c+ Delta": abs(cplus(Delta)), "c+ Delta-G one": abs(cplus(Delta - G1)),
             "c+ Delta-G sym": abs(cplus(Delta - G2)), "c+ Delta-G(zeta_B)": abs(cplus(Delta - GB))}
        if conf:
            Gp = v4lib.gauge_piece(zeta, grid, h_old=h_old, conformal=False, form="one")
            r["rms Delta-G(plain formula)"] = rms(Delta - Gp)
            r["c+ Delta-G(plain formula)"] = abs(cplus(Delta - Gp))
        rec[lab] = r
    rows.append(rec)
    print(json.dumps(rec), flush=True)

# orders between successive eps
orders = {}
for lab in ("plain", "conformal"):
    for key in rows[0][lab]:
        v = [r[lab][key] for r in rows]
        orders[f"{lab}: {key}"] = [float(np.log(v[i] / v[i + 1]) / np.log(2.0)) if v[i + 1] > 0 else None
                                   for i in range(len(v) - 1)]
res = {"rows": rows, "orders (log2 ratio per halving of eps)": orders,
       "grid": {"N": N, "L": L}, "h modes": HM, "zeta modes": ZM}
with open(os.path.join(OUT, "v4_gauge_test.json"), "w") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps(orders, indent=1))

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

eps = np.array([r["eps"] for r in rows])
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
fig.subplots_adjust(left=0.08, right=0.99, bottom=0.15, top=0.9, wspace=0.25)
for ax, lab in zip(axs, ("plain", "conformal")):
    for key, col, mk in (("rms Delta", fs.PAL["blue"], "o"), ("rms Delta-G one", fs.PAL["red"], "s"),
                         ("rms Delta-G sym", fs.PAL["yellow"], "^"), ("rms Delta-G(zeta_B) sym", fs.PAL["green"], "v"),
                         ("rms Delta-G(plain formula)", "k", "x")):
        if key in rows[0][lab]:
            ax.loglog(eps, [r[lab][key] for r in rows], mk + "-", color=col, ms=4, lw=1.0,
                      label=key.replace("rms ", ""))
    ax.loglog(eps, rows[0][lab]["rms Delta"] * (eps / eps[0]) ** 2, color="grey", ls="--", lw=0.8)
    ax.loglog(eps, rows[0][lab]["rms Delta-G one"] * (eps / eps[0]) ** 3, color="grey", ls=":", lw=0.8)
    ax.set_title(f"{lab} metric: exact pure-gauge data", fontsize=9)
    ax.set_xlabel(r"$\epsilon$", labelpad=-2)
axs[0].set_ylabel("rms over the box")
axs[0].legend(loc="upper left", fontsize=6)
axs[1].legend(loc="upper left", fontsize=6)
fs.save(fig, os.path.join(OUT, "v4_gauge_test"))
