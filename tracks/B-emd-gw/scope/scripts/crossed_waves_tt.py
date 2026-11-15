"""Quasi-static second-order TT strain of crossed sine waves in the matter era (check 2).

    python3 crossed_waves_tt.py OUTDIR [--n 32] [--L 4] [--delta 0.01]

Weak-field equation of arXiv:1604.06065 (source compendium_arxiv.tex, lines 294-298):
(1/2) h'' + Hc h' - (1/2) lap h = TT[8 pi a^2 Pi - 2 dPhi dPhi - 4 Phi ddPhi]. With the
growing-mode velocity v = -(2/(3 Hc)) grad Phi and 8 pi a^2 rho0 = 3 Hc^2, and
TT[Phi d_i d_j Phi] = -TT[d_i Phi d_j Phi], the quasi-static solution is
h^TT = (20/3) TT[d_i Phi d_j Phi] / |k|^2 (metric (1 - 2 Phi) delta_ij + h_ij).
Potential of the initial data of cosmo/ic/make_east.py: psi_N = -(3/2)(H/k)^2 delta_N,
delta_N = sum_i d_i sin(k x_i).

Writes OUTDIR/crossed_waves_tt.json and the figure OUTDIR/crossed_waves_tt.png.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402


def fields(n, L, d, H=1.0):
    k = 2*np.pi/L
    x = np.arange(n)*L/n
    X = np.meshgrid(x, x, x, indexing="ij")
    phi = [-1.5*(H/k)**2*di for di in d]
    Phi = sum(phi[i]*np.sin(k*X[i]) for i in range(3))
    dPhi = [phi[i]*k*np.cos(k*X[i]) for i in range(3)]
    ddPhi = [[(-phi[i]*k*k*np.sin(k*X[i]) if i == j else np.zeros_like(Phi))
              for j in range(3)] for i in range(3)]
    return k, phi, Phi, dPhi, ddPhi


def tt_project(Shat, kv):
    """Lambda_ijlm S_lm at every wave vector; kv has shape (3, n, n, n)."""
    k2 = (kv**2).sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        khat = np.where(k2 > 0, kv/np.sqrt(np.where(k2 > 0, k2, 1.0)), 0.0)
    P = np.eye(3)[:, :, None, None, None] - khat[:, None]*khat[None, :]
    PSP = np.einsum("ik...,kl...,lj...->ij...", P, Shat, P)
    trPS = np.einsum("kl...,lk...->...", P, Shat)
    TT = PSP - 0.5*P*trPS[None, None]
    TT[..., 0, 0, 0] = 0.0
    return TT, k2


def analyse(n, L, ratios, delta):
    d = [delta*r for r in ratios]
    k, phi, Phi, dPhi, ddPhi = fields(n, L, d)
    S = np.array([[dPhi[i]*dPhi[j] for j in range(3)] for i in range(3)])
    S2 = np.array([[Phi*ddPhi[i][j] for j in range(3)] for i in range(3)])
    Shat = np.fft.fftn(S, axes=(2, 3, 4))/n**3
    S2hat = np.fft.fftn(S2, axes=(2, 3, 4))/n**3
    m = np.fft.fftfreq(n, d=1.0/n)
    kv = np.array(np.meshgrid(m, m, m, indexing="ij"))*k
    TT, k2 = tt_project(Shat, kv)
    TT2, _ = tt_project(S2hat, kv)
    with np.errstate(invalid="ignore", divide="ignore"):
        inv = np.where(k2 > 0, 1.0/np.where(k2 > 0, k2, 1.0), 0.0)
    h = (20.0/3.0)*TT*inv[None, None]
    # size of the untruncated traceless source at the same normalization
    trS = np.einsum("ii...->...", Shat)
    Str = Shat - np.eye(3)[:, :, None, None, None]*trS[None, None]/3.0
    hfull = (20.0/3.0)*np.sqrt((np.abs(Str)**2).sum(axis=(0, 1)))*inv
    hnorm = np.sqrt((np.abs(h)**2).sum(axis=(0, 1)))
    hmax = float(hnorm.max())
    scale = float(hfull.max())
    idx = np.argwhere(hnorm > 1e-10*max(scale, 1e-300))
    modes = sorted({tuple(int(m[i]) for i in v) for v in idx})
    # plus polarization at (k, k, 0) in the basis e1 = (1,-1,0)/sqrt2, e2 = (0,0,1)
    e1 = np.array([1.0, -1.0, 0.0])/np.sqrt(2.0)
    e2 = np.array([0.0, 0.0, 1.0])
    ep = np.outer(e1, e1) - np.outer(e2, e2)
    hk = h[:, :, 1, 1, 0]
    hplus = complex(np.einsum("ij,ij->", hk, ep)/2.0)
    ident = float(np.abs(TT2 + TT).max()/max(np.abs(TT).max(), 1e-300))
    return {"ratios": list(ratios), "delta": delta, "phi": phi,
            "max_TT_strain": hmax, "max_untruncated_strain": scale,
            "TT_over_untruncated": hmax/scale if scale > 0 else None,
            "modes_with_TT": modes, "hplus_kk0_abs": abs(hplus),
            "hplus_kk0_predicted": 5.0/12.0*abs(phi[0]*phi[1]),
            "identity_TT_PhiddPhi_plus_TT_dPhidPhi_rel": ident}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--L", type=float, default=4.0)
    ap.add_argument("--delta", type=float, default=0.01)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cases = {"plane (1,0,0)": (1, 0, 0), "equal two (1,1,0)": (1, 1, 0),
             "equal three (1,1,1)": (1, 1, 1), "cosmo/ runs (1,0.9,1.1)": (1, 0.9, 1.1)}
    res = {"n": a.n, "L": a.L, "delta": a.delta, "cases": {}, "eps_scan": []}
    for name, r in cases.items():
        res["cases"][name] = analyse(a.n, a.L, r, a.delta)
    eps = np.logspace(-3, 0, 13)
    for e in eps:
        res["eps_scan"].append(analyse(a.n, a.L, (1, float(e), 0), a.delta))
    lin = [s["hplus_kk0_abs"]/s["hplus_kk0_predicted"] - 1 for s in res["eps_scan"]]
    res["eps_scan_max_rel_dev_from_5_12"] = float(np.max(np.abs(lin)))
    extra = [s["modes_with_TT"] for s in res["eps_scan"]]
    allowed = {(1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0)}
    res["eps_scan_only_kk0_modes"] = bool(all(set(map(tuple, m)) <= allowed for m in extra))
    with open(os.path.join(a.out, "crossed_waves_tt.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    hp = np.array([s["hplus_kk0_abs"] for s in res["eps_scan"]])
    pr = np.array([s["hplus_kk0_predicted"] for s in res["eps_scan"]])
    ax.loglog(eps, pr, **fs.GUIDE, label=r"$(5/12)\,|\phi_x\phi_y|$")
    ax.loglog(eps, hp, "o", color=fs.PAL["red"], ms=4, label="Fourier projection")
    p0 = res["cases"]["plane (1,0,0)"]["max_TT_strain"]
    ax.axhline(max(p0, 1e-22), **fs.MASK_LINE)
    ax.text(1.2e-3, max(p0, 1e-22)*3, r"plane wave, $\epsilon=0$: largest $|h^{TT}|$",
            fontsize=8, color="grey")
    ax.set_xlabel(r"amplitude ratio $\epsilon$ of the second wave")
    ax.set_ylabel(r"$|h_+|$ at $\mathbf{k}=(k,k,0)$, $\delta=0.01$")
    ax.set_ylim(1e-23, 1e-4)
    ax.legend(loc="center right")
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    names = list(cases)
    vals = [max(res["cases"][nm]["max_TT_strain"], 1e-22) for nm in names]
    full = [res["cases"][nm]["max_untruncated_strain"] for nm in names]
    xs = np.arange(len(names))
    ax2.bar(xs - 0.18, full, 0.36, color=fs.PAL["blue"], label="traceless source")
    ax2.bar(xs + 0.18, vals, 0.36, color=fs.PAL["red"], label="TT part")
    ax2.set_yscale("log")
    ax2.set_ylim(1e-23, 1e-3)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(["(1,0,0)", "(1,1,0)", "(1,1,1)", "(1,0.9,1.1)"])
    ax2.set_xlabel("amplitude ratios of the three waves")
    ax2.set_ylabel(r"largest $(20/3)|S|/k^2$ over the box modes")
    ax2.legend(loc="upper left", ncol=2)
    fs.save(fig, os.path.join(a.out, "crossed_waves_tt"))
    print(json.dumps({k: v for k, v in res.items() if k != "eps_scan"}, indent=1))


if __name__ == "__main__":
    main()
