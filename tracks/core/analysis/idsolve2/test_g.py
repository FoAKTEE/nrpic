#!/usr/bin/env python3
"""Test G of the initial-data solver, second pass (journal entry 6): Track A's phase-1
generator on the slice of constant mean curvature (request
track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T183719Z__to-core__phase1-generator-cmc.md)
with the code's own solver, as far as it is the same machinery.

The data are those of Track A's feasibility test T4
(track/A-emd-pbh:tracks/A-emd-pbh/periodic_threshold/scripts/t4_cmc_route.py, ge_fields
and run_case; profile of make_peak_ic.zeta_field): a curvature peak
zeta = mu exp(-k^2 r^2/6) [1 + (k^2/6) 3e (Y^2 - Z^2)] at the centre of a torus of side
L = 20/k, k = eps_i = 0.2, e = 0.2, H = 1, a = 1; gradient-expansion fields on the CMC
slice K = -3H: psi_GE = Psi (1 - q/6), Ahat_ij of p_ij, E from the Hamiltonian constraint
of psi_GE (spectral derivatives) and Shat_i from the momentum constraint. One particle per
cell at the cell centre with u_i such that its deposit gives Shat_i and mass such that it
gives Ehat at psi_GE. The code reads psi_GE, K and Ahat_GE from a field file (nrpic_cosmo
id = file), starts the solve from psi = 1 (id_psi_init = one) and solves for psi with K
and Ahat held fixed (and, with id_vector, Ahat = Ahat_GE + L W). Since psi_GE solves the
continuum constraint with this E exactly, the solved psi differs from psi_GE by the
discretisation of the code only: c = max|dpsi - <dpsi>|/max|psi_GE - <psi_GE>| (Track A's
measure c_CMC). Track A's Python solver (cosmo_id.solve, fixed-point preconditioning by
the mean of sigma) diverged at mu = 0.5 (T4, runs A-emd-pbh-20261115-160718-e04c0cc,
-161134-f3949f8).

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/test_g.py --exe <athena>
    test_g.py --analyze <run directory>
"""
import argparse
import glob
import os
import sys

import numpy as np

import lib2
from lib2 import idlib
from nrpic import figstyle as fs  # noqa: E402
from nrpic import io as nio        # noqa: E402

sys.path.insert(0, os.path.join(lib2.WT, "cosmo", "ic"))
import cosmo_id as cid             # noqa: E402
from nrp_io import write_fields    # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TORUS = os.path.join(lib2.WT, "problems/idsolve/torus.athinput")
EPS, ELL, HUB = 0.2, 0.2, 1.0
CASES = [("g_mu0p03_n64", 0.03, 64, False), ("g_mu0p3_n64", 0.3, 64, False),
         ("g_mu0p5_n32", 0.5, 32, False), ("g_mu0p5_n64", 0.5, 64, False),
         ("g_mu0p7_n64", 0.7, 64, False), ("g_mu0p5_n64_vec", 0.5, 64, True)]


def zeta_field(n, L, k, mu, e):
    h = L/n
    xc = (np.arange(n) + 0.5)*h - 0.5*L
    X, Y, Z = np.meshgrid(xc, xc, xc, indexing="ij")
    return mu*np.exp(-k*k*(X*X + Y*Y + Z*Z)/6.0)*(1.0 + (k*k/6.0)*3*e*(Y*Y - Z*Z))


def ge_fields(tor, zeta, aH=1.0, H=1.0):
    """Track A's ge_fields (t4_cmc_route.py): psi_GE, Ahat_ij (six), Ehat = psi^6 E,
    Shat_i = psi^6 S_i on the CMC slice."""
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
    E = (-tor.lap(psi) + K*K*psi**5/12.0 - cid.a_squared(A)/(8.0*psi**7))/(2.0*np.pi*psi**5)
    idx = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 1): 3, (1, 2): 4, (2, 2): 5}
    Ak = [tor.fft(x) for x in A]
    Sh = []
    for i in range(3):
        div = 0.0
        for j in range(3):
            div = div + 1j*kd[j]*Ak[idx[(min(i, j), max(i, j))]]
        Sh.append(tor.ifft(div)/(8.0*np.pi))
    return psi, A, K, E*psi**6, Sh


def make_case(d, mu, n):
    """Field file and particle file of one case; returns psi_GE."""
    L = 20.0/EPS
    tor = cid.Torus(n, L)
    psi, A, K, Eh, Sh = ge_fields(tor, zeta_field(n, L, EPS, mu, ELL), H=HUB)
    write_fields(os.path.join(d, "fields.bin"), psi, K, np.ones_like(psi), A)
    h = L/n
    xc = (np.arange(n) + 0.5)*h
    X, Y, Z = np.meshgrid(xc, xc, xc, indexing="ij")
    x = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    v = np.stack([(Sh[i]/Eh).ravel() for i in range(3)], axis=1)      # u_i/W
    p4 = psi.ravel()**4
    W = 1.0/np.sqrt(1.0 - (v*v).sum(axis=1)/p4)
    u = v*W[:, None]
    m = Eh.ravel()*h**3/W
    nio.write_nrp(os.path.join(d, "peak.nrp"), x, u, m)
    np.save(os.path.join(d, "psi_ge.npy"), psi)
    return psi


def build_cases(root, exe):
    cases = []
    L = 20.0/EPS
    for name, mu, n, vec in CASES:
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        make_case(d, mu, n)
        s = {"mesh/nx1": n, "mesh/nx2": n, "mesh/nx3": n, "meshblock/nx1": n//2,
             "meshblock/nx2": n//2, "meshblock/nx3": n//2}
        for a in "123":
            s["mesh/x%smin" % a] = 0.0
            s["mesh/x%smax" % a] = L
        s.update({"problem/id": "file", "problem/id_file": "fields.bin",
                  "problem/hubble": HUB, "particles/particle_file": "peak.nrp",
                  "particles/id_psi_init": "one", "particles/id_residual": "code",
                  "particles/id_maxit": 80})
        if vec:
            s.update({"particles/id_vector": "true", "particles/id_vector_residual": "code"})
        lib2.make_input(TORUS, os.path.join(d, "in.athinput"), s)
        cases.append(dict(name=name, dir=d, steps=[[exe, "-i", "in.athinput"]],
                          may_fail=True))
    return cases


def analyze(root, status):
    res = dict(run=lib2.run_id(), status=status or {}, cases={})
    lines = {}
    for name, mu, n, vec in CASES:
        d = os.path.join(root, name)
        e = dict(mu=mu, n=n, vector=vec)
        rec = os.path.join(d, "torus.idsolve.txt")
        if os.path.exists(rec):
            rows, tail = lib2.summary(rec)
            e.update(outer=int(rows[-1][0]), summary=tail, lin=int(rows[:, 10].sum()),
                     vcycles=int(rows[:, 11].sum()),
                     converged=any(t.startswith("converged") for t in tail),
                     rel_hist=[float(v) for v in rows[:, 1]])
            if rows.shape[1] > 13:
                e.update(relv_first=float(rows[0][13]), relv_last=float(rows[-1][13]),
                         mmax_first=float(rows[0][16]), mmax_last=float(rows[-1][16]))
        f = os.path.join(d, "torus.idsolve.bin")
        if os.path.exists(f):
            a = idlib.read_idsolve_bin(f)
            pg = np.load(os.path.join(d, "psi_ge.npy"))
            dp = a["psi"] - pg
            pert = float(np.abs(pg - pg.mean()).max())
            e.update(c_cmc=float(np.abs(dp - dp.mean()).max()/pert),
                     mean_offset=float(dp.mean()), psi_ge_max_minus_1=float(pg.max() - 1.0),
                     psi_max_minus_1=float(a["psi"].max() - 1.0),
                     H_after_max=float(np.abs(a["H"]).max()),
                     H_before_max=float(np.abs(a["H0"]).max()),
                     E_max_over_mean=float(a["E"].max()/a["E"].mean()))
            j = n//2
            L = 20.0/EPS
            xc = ((np.arange(n) + 0.5)*L/n - 0.5*L)*EPS
            lines[name] = (xc, a["psi"][:, j, j] - 1.0, pg[:, j, j] - 1.0)
        res["cases"][name] = e
    out = os.path.join(root, "test_g_numbers.json")
    lib2.save_json(out, res)
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.6))
    col = {0.03: fs.PAL["yellow"], 0.3: fs.PAL["red"], 0.5: fs.PAL["blue"],
           0.7: fs.PAL["green"]}
    for name, mu, n, vec in CASES:
        if name not in lines or n != 64 or vec:
            continue
        x, ps, pg = lines[name]
        axs[0].plot(x, ps/max(abs(pg).max(), 1e-30), "o", ms=2, color=col[mu],
                    label=r"$\mu=%g$, code" % mu)
        axs[0].plot(x, pg/max(abs(pg).max(), 1e-30), "-", lw=0.8, color=col[mu])
        axs[1].semilogy(x, np.abs(ps - pg) + 1e-16, "-", color=col[mu],
                        label=r"$\mu=%g$" % mu)
    axs[0].set_xlabel(r"$k x$ (line through the peak)")
    axs[0].set_ylabel(r"$(\psi-1)/\max|\psi_{\rm GE}-1|$")
    axs[0].legend(fontsize=5)
    axs[1].set_xlabel(r"$k x$")
    axs[1].set_ylabel(r"$|\psi-\psi_{\rm GE}|$, $64^3$")
    axs[1].legend(fontsize=5)
    for name, mu, n, vec in CASES:
        e = res["cases"].get(name, {})
        if "rel_hist" in e:
            axs[2].semilogy(e["rel_hist"], "-" if not vec else "--",
                            color=col[mu], label=name.replace("g_", ""))
    axs[2].set_xlabel("outer iteration")
    axs[2].set_ylabel("max|F|/scale")
    axs[2].legend(fontsize=4)
    fig.tight_layout()
    p = os.path.join(root, "test_g_cmc")
    fs.save(fig, p)
    plt.close(fig)
    lib2.publish([out, p + ".png", p + ".pdf"])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=lib2.EXE)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--analyze", default="")
    a = ap.parse_args()
    if a.analyze:
        analyze(a.analyze, None)
        return 0
    root = lib2.run_root()
    cases = build_cases(root, os.path.abspath(a.exe))
    status = lib2.run_cases(cases, a.jobs)
    analyze(root, status)
    print("failed cases:", [k for k, v in status.items() if v["status"] != "completed"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
