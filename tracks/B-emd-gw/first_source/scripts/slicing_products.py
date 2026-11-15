#!/usr/bin/env python3
"""Size of the second-order slicing products of the flat TT projection (P10 of JOURNAL.md).

    python3 slicing_products.py <run dir> [...]       (output: $NRPIC_RUN_DIR)

With the first-order gauge Newtonian (P9), the code gauge differs from the Poisson gauge by
second-order generators: a time shift T and a spatial shift d_i L with zero shift kept,
L' = T, and the scalar part of the conformal metric h^S_ij = 2 (d_i d_j - delta_ij lap/3) E,
E = -L, so |T| = |E'| (conformal time eta). Products quadratic in the generators enter
Lambda h: the spatial ones are G (fslib.gauge); those with T are of the forms
d_i T d_j T (from the g_00 part) and T d_eta h^S_ij [JUDGEMENT on the list, order-one
coefficients not derived]. With E growing as a ~ eta^2, E' = 2E/eta and d_eta h^S = 2h^S/eta.
Per restart dump: rms of Lambda[d T d T] and of Lambda[T d_eta h^S], with eta = 2/(a H),
H = -<trK>/3, against rms G and rms Lambda h. Writes slicing_products.json.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from gwdiag import tt, readers  # noqa: E402
from fslib import gauge  # noqa: E402

AX = (-3, -2, -1)


def rms_tt(Q, g):
    T = tt.tt_project_fourier(Q, g)
    P = tt.power_tensor(T, g)
    return float(np.sqrt(P.sum()))


def main():
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    res = {}
    for rd in sys.argv[1:]:
        rows = []
        for f in sorted(glob.glob(os.path.join(rd, "rst", "*.rst")))[1:]:
            d = readers.read_rst(f)
            g = d["grid"]
            chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
            a = float(np.mean(chi)) ** -0.5
            H = -float(np.mean(trK)) / 3.0
            eta = 2.0 / (a * H)
            h = gauge.traceless(gt - np.eye(3)[:, :, None, None, None])
            F = tt.tensor_rfft(h)
            k = g.kvec(real=True)
            k2 = (k ** 2).sum(axis=0)
            kkh = np.einsum("a...,b...,ab...->...", k, k, F)
            with np.errstate(divide="ignore", invalid="ignore"):
                Eh = np.where(k2 > 0, -0.75 * kkh / np.where(k2 > 0, k2, 1.0) ** 2, 0.0)
            Eh[g.nyquist_mask(real=True)] = 0.0
            Th = 2.0 * Eh / eta
            T = np.fft.irfftn(Th, s=g.shape, axes=AX)
            dT = np.array([np.fft.irfftn(1j * k[c] * Th, s=g.shape, axes=AX) for c in range(3)])
            # scalar part h^S and its eta derivative
            hS_h = -2.0 * (k[:, None] * k[None, :] - np.eye(3)[:, :, None, None, None] * k2 / 3.0) * Eh
            hS = np.empty((3, 3) + g.shape)
            for i in range(3):
                for j in range(3):
                    hS[i, j] = np.fft.irfftn(hS_h[i, j], s=g.shape, axes=AX)
            Q1 = dT[:, None] * dT[None, :]
            Q2 = T * 2.0 * hS / eta
            G = gauge.gauge_piece(h, g)
            row = {"file": os.path.basename(f), "a": a, "eta": eta,
                   "rms_E": float(np.sqrt(np.mean(np.fft.irfftn(Eh, s=g.shape, axes=AX) ** 2))),
                   "rms_hS": float(np.sqrt(np.mean(np.einsum("ab...,ab...->...", hS, hS)))),
                   "rms_LdTdT": rms_tt(Q1, g), "rms_LThS": rms_tt(Q2, g),
                   "rms_G": float(np.sqrt(np.mean(np.einsum("ab...,ab...->...", G, G)))),
                   "rms_TT": rms_tt(h, g)}
            print(rd, {k_: (f"{v:.3e}" if isinstance(v, float) else v) for k_, v in row.items()}, flush=True)
            rows.append(row)
        res[os.path.basename(rd.rstrip("/"))] = rows
    with open(os.path.join(out, "slicing_products.json"), "w") as f:
        json.dump(res, f, indent=1)
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.4, 3.0))
    for c, (name, rows) in zip(fs.SERIES, res.items()):
        a = [r["a"] for r in rows]
        ax.loglog(a, [r["rms_TT"] for r in rows], "o-", color=c, ms=3, label=r"$\Lambda h$ (%s)" % name)
        ax.loglog(a, [r["rms_G"] for r in rows], "s--", color=c, ms=3, label=r"$G$ (spatial)")
        ax.loglog(a, [r["rms_LdTdT"] for r in rows], "^:", color=c, ms=4, label=r"$\Lambda[\partial T\partial T]$")
        ax.loglog(a, [r["rms_LThS"] for r in rows], "v-.", color=c, ms=4, label=r"$\Lambda[T\,\partial_\eta h^S]$")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel("rms over the box")
    ax.legend(fontsize=6, ncol=2)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "slicing_products"))


if __name__ == "__main__":
    main()
