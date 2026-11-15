"""D3 of ../JOURNAL.md: first-order momentum constraint of the stochastic kick of
arXiv:2512.14649 (BSSN form) evaluated with the sixth-order centred first derivative of
athenak/src/utils/finite_diff.hpp, for the projector built from the wave vector k and
from the symbol k_eff of the stencil.

Linearised about a homogeneous slice (conformal metric delta_ij, chi constant, phi
homogeneous) the kick changes only K, Atilde_ij and Pi; the momentum constraint of the
kick is M_i = D_j dA_ij - (2/3) D_i dK (the matter term -Pi d_i dphi - dPi d_i phi_b is
zero: phi gets no kick and phi_b is homogeneous).

Usage: python3 -I d3_momentum.py <outdir>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../../python")))
import synth                                     # noqa: E402
from nrpic import figstyle as fs                 # noqa: E402
import matplotlib.pyplot as plt                  # noqa: E402


def kick_fields(n, a, N, L, proj, eps1=1.0, nghost=4):
    """dK and dA_ij on the mesh for unit S_R per mode times alpha_n."""
    h = L/N
    k = 2.0*np.pi*n/L
    if proj == "k":
        q = k
    else:
        q = synth.keff(k*h, nghost)/h
    q2 = (q**2).sum(axis=1)
    dK = synth.synth_fft(n, -eps1*a, N, L).real
    dA = {}
    for i in range(3):
        for j in range(i, 3):
            P = (1.0/3.0 if i == j else 0.0) - q[:, i]*q[:, j]/q2
            dA[(i, j)] = synth.synth_fft(n, eps1*P*a, N, L).real
    return dK, dA


def residual(dK, dA, N, L, nghost=4):
    h = L/N
    M = np.zeros((3,) + dK.shape)
    divA = np.zeros_like(M)
    gK = np.zeros_like(M)
    for i in range(3):
        for j in range(3):
            A = dA[(min(i, j), max(i, j))]
            divA[i] += synth.d1_periodic(A, j, h, nghost)
        gK[i] = (2.0/3.0)*synth.d1_periodic(dK, i, h, nghost)
        M[i] = divA[i] - gK[i]
    rms = lambda v: np.sqrt(np.mean((v**2).sum(axis=0)))
    return rms(M)/(rms(divA) + rms(gK))


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(7)
    N = 64
    L = 2.0*np.pi
    nmax = N//4
    nb = synth.ball_modes(nmax)
    shells = [1, 2, 4, 6, 8, 10, 12, 14, 16]
    rows = []
    for s in shells:
        kk = np.sqrt((nb**2).sum(axis=1))
        sel = (kk >= s - 0.5) & (kk < s + 0.5) if s < nmax else (kk >= s - 1.0)
        n = nb[sel]
        a = synth.hermitian_gaussian(n, rng)
        row = dict(shell=s, kh=float(2*np.pi*s/N), modes=int(len(n)))
        for proj in ("k", "keff"):
            dK, dA = kick_fields(n, a, N, L, proj)
            row[proj] = float(residual(dK, dA, N, L))
        rows.append(row)
        print(row)
    # whole ball, as in a run once every mode has entered
    a = synth.hermitian_gaussian(nb, rng)
    ball = {}
    for proj in ("k", "keff"):
        dK, dA = kick_fields(nb, a, N, L, proj)
        ball[proj] = float(residual(dK, dA, N, L))
    print("ball", ball)
    # symbol error of the stencils at the shells
    sym = [dict(kh=float(2*np.pi*s/N),
                d1=float(abs(synth.keff(2*np.pi*s/N) - 2*np.pi*s/N)/(2*np.pi*s/N)))
           for s in shells]
    res = dict(N=N, nmax=nmax, nghost=4, shells=rows, ball=ball, symbol=sym)
    with open(os.path.join(outdir, "d3.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.2))
    ax = fig.add_axes([0.17, 0.15, 0.78, 0.80])
    kh = np.array([r["kh"] for r in rows])
    ax.plot(kh, [r["k"] for r in rows], "o-", color=fs.PAL["red"],
            label="projector from k (paper)")
    ax.plot(kh, [max(r["keff"], 1e-18) for r in rows], "s-", color=fs.PAL["blue"],
            label="projector from k_eff of the stencil")
    ax.plot(kh, [s["d1"] for s in sym], **fs.GUIDE, label="|k_eff - k| / k")
    ax.axvline(np.pi/2, **fs.MASK_LINE)
    ax.text(np.pi/2*0.62, 3e-15, "k_max = N k_min/4", fontsize=8, rotation=90)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-17, 1)
    ax.set_xlabel("k h of the shell")
    ax.set_ylabel("|M| / (|D dA| + (2/3)|D dK|)")
    ax.legend(fontsize=8, loc="upper left")
    fs.save(fig, os.path.join(outdir, "d3_momentum"))


if __name__ == "__main__":
    main(sys.argv[1])
