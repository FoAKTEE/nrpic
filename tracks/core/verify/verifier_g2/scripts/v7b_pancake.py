#!/usr/bin/env python3
"""V7b: Newtonian mode with the Fourier Poisson solver (core-v0.6), exact Zel'dovich pancake.

Run core-20261119-160919-c6a7279 (test T3 of interfaces/newtonian_mode.md 7.8), cases
sin32_sp (newton_fft_symbol = spectral) and sin32_7pt (seven_point): equal-mass lattice
x = q + a psi(q_x), psi = (d/k) sin(k q_x), d = 0.05, k = 2 pi (L = 1), exact in plane
symmetry before shell crossing (a = 1/d = 20); a = (1 + t/2)^2.
Own steps: the Lagrangian q_x of every particle from the snapshot at a = 1 (Newton
iteration on q + psi(q) = x, then snapped to the lattice (i + 1/2)/32); exact slab moment
I_xx(a) = sum m (q_x - 1/2 + a psi)^2 of group 2 (tags 8192..24575, the header of
newton.newton.g2.hst) about its centroid 1/2; compared with column 13 (I_xx) of the
group history in the window 1.2 <= a <= 7.56, error relative to max |I_xx - c0|;
positions of all particles at the last snapshot against q + a psi.

usage: v7b_pancake.py RUNDIR OUTDIR
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v7a_point import read_snap  # noqa: E402

D, K, N = 0.05, 2 * np.pi, 32


def lagrangian_qx(x0):
    q = x0.copy()
    for _ in range(50):
        f = q + (D / K) * np.sin(K * q) - x0
        q -= f / (1 + D * np.cos(K * q))
    i = np.round(q * N - 0.5)
    return (i + 0.5) / N, float(np.max(np.abs(q - (i + 0.5) / N)))


def main():
    rd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    res, plot = {}, {}
    for case in ("sin32_sp", "sin32_7pt"):
        cd = os.path.join(rd, case)
        t0, _, r0, g0, _, _ = read_snap(os.path.join(cd, "newton.part.00000.bin"))
        t1, _, r1, g1, _, _ = read_snap(os.path.join(cd, "newton.part.00001.bin"))
        o0, o1 = np.argsort(g0), np.argsort(g1)
        r0, r1, tags = r0[o0], r1[o1], g0[o0]
        assert np.array_equal(tags, g1[o1])
        qx, snap_dev = lagrangian_qx(r0[:, 0])
        m = r0[:, 6]
        a1 = (1 + t1 / 2) ** 2
        xex = qx + a1 * (D / K) * np.sin(K * qx)
        dx = r1[:, 0] - xex
        dx -= np.round(dx)
        dyz = np.abs(r1[:, 1:3] - r0[:, 1:3]).max()
        sel = (tags >= 8192) & (tags <= 24575)
        # exact slab moment
        u = qx[sel] - 0.5
        p = (D / K) * np.sin(K * qx[sel])
        ms = m[sel]
        c0, c1, c2 = np.sum(ms * u * u), 2 * np.sum(ms * u * p), np.sum(ms * p * p)
        Xc = np.sum(ms * (u + p)) / ms.sum()
        h = np.loadtxt(os.path.join(cd, "newton.newton.g2.hst"), comments="#", ndmin=2)
        a = h[:, 2]
        Ixx = h[:, 12]
        Iex = c0 + c1 * a + c2 * a * a
        w = (a >= 1.2) & (a <= 7.5625 + 1e-9)   # the window "1.2 <= a <= 7.56" of the claim, last record a = (1 + 3.5/2)^2
        scale = np.max(np.abs(Iex[w] - c0))
        err = float(np.max(np.abs(Ixx[w] - Iex[w])) / scale)
        res[case] = {"t_last": t1, "a_last": a1, "lattice_snap_max_dev": snap_dev,
                     "n_group2": int(sel.sum()), "group2_mass": float(ms.sum()),
                     "c0_c1_c2_own": [c0, c1, c2], "centroid_offset_exact_a1": float(Xc),
                     "Ixx_t0_hst_vs_own": [float(Ixx[0]), float(c0 + c1 + c2)],
                     "Ixx_err_rel_to_max_exact_minus_c0": err, "window_a": [float(a[w][0]), float(a[w][-1])],
                     "n_records_window": int(w.sum()),
                     "pos_err_max_last": float(np.abs(dx).max()),
                     "pos_err_rel_to_a_amp": float(np.abs(dx).max() / (a1 * D / K)),
                     "transverse_max_change": float(dyz)}
        plot[case] = (a[w], (Ixx[w] - Iex[w]) / scale)
        print(case, json.dumps(res[case]))
    with open(os.path.join(outdir, "v7b_pancake.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.4, 3.0))
    for i, (case, (aa, e)) in enumerate(plot.items()):
        ax.semilogy(aa, np.maximum(np.abs(e), 1e-12), color=fs.SERIES[i], lw=1,
                    label=f"{case}: max {res[case]['Ixx_err_rel_to_max_exact_minus_c0']:.2e}")
    ax.set_xlabel("a")
    ax.set_ylabel(r"$|I_{xx}-I_{xx}^{\rm exact}|/\max|I^{\rm exact}_{xx}-c_0|$")
    ax.legend(fontsize=7)
    ax.set_title("V7b: slab moment of the exact pancake, run core-20261119-160919-c6a7279", fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v7b_pancake"))


if __name__ == "__main__":
    main()
