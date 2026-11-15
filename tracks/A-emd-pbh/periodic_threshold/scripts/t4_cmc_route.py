"""T4 (JOURNAL.md): does the existing solver cosmo_id.solve reproduce the
gradient-expansion data of arXiv:2609.14218 on its constant-mean-curvature slice at the
paper's start eps_i = 0.2, where make_field fails? Feasibility evidence for core's
phase-1 generator; not production data (no files for the code are written).

    python3 t4_cmc_route.py --out DIR
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/data/haiyangw/nrpic/wt/A-emd-pbh"
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, HERE)
import cosmo_id as cid          # noqa: E402
import make_peak_ic as mp       # noqa: E402
import figstyle as fs           # noqa: E402


def ge_fields(tor, zeta, aH=1.0, H=1.0):
    """psi_GE, Ahat_ij (six), Ehat = psi^6 E and Shat_i = psi^6 S_i on the CMC slice."""
    Psi = np.exp(0.5*zeta)
    F = tor.fft(Psi)
    kd = tor.kd
    d1 = [tor.ifft(1j*kk*F) for kk in kd]
    d2 = {}
    for a in range(3):
        for b in range(a, 3):
            d2[(a, b)] = tor.ifft(-kd[a]*kd[b]*F)
    lap = d2[(0, 0)] + d2[(1, 1)] + d2[(2, 2)]
    grad2 = d1[0]**2 + d1[1]**2 + d1[2]**2
    q = -(4.0/3.0)*lap/Psi**5
    psi = Psi*(1.0 - q/(6.0*aH**2))
    A = []
    for a in range(3):
        for b in range(a, 3):
            dab = 1.0 if a == b else 0.0
            p = Psi**-4*(-(2.0/Psi)*(d2[(a, b)] - dab*lap/3.0)
                         + (6.0/Psi**2)*(d1[a]*d1[b] - dab*grad2/3.0))
            A.append(psi**6*0.4*p*H/aH**2)
    K = -3.0*H*np.ones_like(psi)
    # Hamiltonian constraint (cosmo_id convention, all terms on the left = 0) solved for E
    E = (-tor.lap(psi) + K*K*psi**5/12.0 - cid.a_squared(A)/(8.0*psi**7))/(2.0*np.pi*psi**5)
    # momentum constraint with constant K: d_j Ahat_ij = 8 pi Shat_i
    idx = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 1): 3, (1, 2): 4, (2, 2): 5}
    Ak = [tor.fft(x) for x in A]
    Sh = []
    for i in range(3):
        div = 0.0
        for j in range(3):
            div = div + 1j*kd[j]*Ak[idx[(min(i, j), max(i, j))]]
        Sh.append(tor.ifft(div)/(8.0*np.pi))
    return psi, A, K, E*psi**6, Sh


def run_case(mu, e, eps, n, nfilter, compensate, start_ge=False):
    k = eps
    L = 20.0/k
    tor = cid.Torus(n, L)
    zeta = mp.zeta_field(n, L, k, mu, e, 0.0)
    psi_ge, A_ge, K, Eh, Sh = ge_fields(tor, zeta)
    h = L/n
    xc = (np.arange(n) + 0.5)*h
    X, Y, Z = np.meshgrid(xc, xc, xc, indexing="ij")
    x = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)    # cell centres
    u = np.stack([(Sh[i]/Eh).ravel() for i in range(3)], axis=1)
    W = np.sqrt(1.0 + (u*u).sum(axis=1)/psi_ge.ravel()**4)
    m = Eh.ravel()*h**3/W
    cid.SHAPE = "cic"
    t0 = time.time()
    r = cid.solve(tor, x, u, m, K, psi0=(psi_ge if start_ge else None), nfilter=nfilter,
                  compensate=compensate,
                  tol=1e-11, maxit=200)
    ham, mom = cid.residuals(tor, r["psi"], K, r["A"], r["E"], r["S"])
    pert = float(np.abs(psi_ge - psi_ge.mean()).max())
    dpsi = r["psi"] - psi_ge
    return {
        "mu": mu, "e": e, "eps_i": eps, "n": n, "nfilter": nfilter,
        "compensate": compensate, "start_ge": start_ge, "iterations": len(r["hist"]),
        "residual_final": r["hist"][-1], "wall_s": time.time() - t0,
        "max_abs_ham": float(np.abs(ham).max()),
        "max_abs_mom": float(max(np.abs(v).max() for v in mom)),
        "psi_ge_max_minus_1": float(psi_ge.max() - 1.0),
        "max_abs_psi_minus_psi_ge": float(np.abs(dpsi).max()),
        "c_cmc": float(np.abs(dpsi - dpsi.mean()).max()/pert),
        "mean_offset": float(dpsi.mean()),
        "Ehat_over_rho_minus_1_max": float(Eh.max()/(3/(8*np.pi)) - 1.0),
        "max_abs_Ahat_solved_minus_ge": float(max(np.abs(a - b).max()
                                                  for a, b in zip(r["A"], A_ge))),
        "max_abs_Ahat_ge": float(max(np.abs(a).max() for a in A_ge)),
        "line": {"x": ((xc - 0.5*L)*k).tolist(), "psi": r["psi"][:, n//2, n//2].tolist(),
                 "psi_ge": psi_ge[:, n//2, n//2].tolist()},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--b", action="store_true", help="T4b: mu = 0.5 from psi_GE, mu = 0.3")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    if a.b:
        for mu, sg in ((0.5, True), (0.3, False)):
            r = run_case(mu, 0.2, 0.2, 64, 0, False, start_ge=sg)
            rows.append(r)
            print({k: v for k, v in r.items() if k != "line"}, flush=True)
        with open(os.path.join(a.out, "t4b_results.json"), "w") as f:
            json.dump(rows, f, indent=1)
        return
    for mu in (0.03, 0.5):
        for nf, cp in ((0, False), (2, True)):
            r = run_case(mu, 0.2, 0.2, 64, nf, cp)
            rows.append(r)
            print({k: v for k, v in r.items() if k != "line"}, flush=True)
    with open(os.path.join(a.out, "t4_results.json"), "w") as f:
        json.dump(rows, f, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.95, wspace=0.3)
    for j, mu in enumerate((0.03, 0.5)):
        ax = fig.add_subplot(1, 2, j + 1)
        for r in [r for r in rows if r["mu"] == mu]:
            ln = r["line"]
            col = fs.PAL["red"] if r["nfilter"] else fs.PAL["yellow"]
            ax.plot(ln["x"], np.array(ln["psi"]) - 1, color=col,
                    label=f"solved, nfilter = {r['nfilter']}")
        ax.plot(ln["x"], np.array(ln["psi_ge"]) - 1, label="gradient expansion",
                **fs.GUIDE)
        ax.set_xlim(-6, 6)
        ax.set_xlabel(r"$k x$ (line through the peak)")
        ax.set_ylabel(r"$\psi - 1$")
        ax.text(0.03, 0.9, rf"$\mu = {mu}$, $\epsilon_i = 0.2$", transform=ax.transAxes)
        if j == 0:
            ax.legend(frameon=False, fontsize=8, loc="upper right")
    fs.save(fig, os.path.join(a.out, "fig_t4_cmc"))


if __name__ == "__main__":
    main()
