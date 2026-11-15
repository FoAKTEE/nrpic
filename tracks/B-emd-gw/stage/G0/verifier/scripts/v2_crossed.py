"""Verifier of B-emd-gw, claim C2: second-order TT strain of crossed sine waves.

    python3 v2_crossed.py OUTDIR [--n 16] [--L 4] [--delta 0.01]

Independent of scope/scripts/crossed_waves_tt.py: the source is built term by term from
the weak-field equation (ij) of arXiv:1604.06065 (compendium_arxiv.tex lines 294-298),
static part,  -(1/2) lap h_ij = TT[ 8 pi a^2 rho v_i v_j - 2 Phi_,i Phi_,j - 4 Phi Phi_,ij ]
(chi, B_i: no TT part at second order), with the dust velocity of cosmo/ic/make_east.py
(v^i = H d_i cos(k x_i)/k at a = 1) and rho = 3 H^2/(8 pi); the TT projection uses the
polarization tensors e_+, e_x of each wave vector (not the Lambda projector). The plus
amplitude at K = (k, k, 0) is read in real space against cos(K.x).

Writes OUTDIR/v2_crossed.json and OUTDIR/v2_crossed.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402


def pol_tensors(kv):
    kh = kv/np.linalg.norm(kv)
    ref = np.array([0.0, 0.0, 1.0]) if abs(kh[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(ref, kh)
    u /= np.linalg.norm(u)
    w = np.cross(kh, u)
    return np.outer(u, u) - np.outer(w, w), np.outer(u, w) + np.outer(w, u), u, w


def build(n, L, ratios, delta, H=1.0, with_kinetic=True, shortcut=False):
    k = 2*np.pi/L
    xs = (np.arange(n) + 0.5)*L/n
    X = np.meshgrid(xs, xs, xs, indexing="ij")
    d = [delta*r for r in ratios]
    phi = [-1.5*(H/k)**2*di for di in d]                 # psi_N of make_east.py
    Phi = sum(phi[i]*np.sin(k*X[i]) for i in range(3))
    dP = [phi[i]*k*np.cos(k*X[i]) for i in range(3)]
    ddP = [[(-phi[i]*k*k*np.sin(k*X[i]) if i == j else 0*Phi) for j in range(3)]
           for i in range(3)]
    v = [H*d[i]*np.cos(k*X[i])/k for i in range(3)]       # make_east.py velocity, a = 1
    rho = 3*H*H/(8*np.pi)
    S = np.zeros((3, 3) + Phi.shape)
    for i in range(3):
        for j in range(3):
            if shortcut:                                  # (10/3) Phi_,i Phi_,j (scope)
                S[i, j] = (10.0/3.0)*dP[i]*dP[j]
                continue
            S[i, j] = -2*dP[i]*dP[j] - 4*Phi*ddP[i][j]
            if with_kinetic:
                S[i, j] += 8*np.pi*rho*v[i]*v[j]
    return k, phi, S, X


def tt_strain(S, n, L):
    """h_ij = 2 TT[S]/K^2 per Fourier mode, by polarization tensors; and the traceless
    untruncated 2 S^T/K^2 for the 'fraction' measure of the scope."""
    Sh = np.fft.fftn(S, axes=(2, 3, 4))/n**3
    m = np.fft.fftfreq(n, d=1.0/n).astype(int)
    hTT = np.zeros_like(Sh)
    norm_tt = np.zeros((n, n, n))
    norm_full = np.zeros((n, n, n))
    big = np.argwhere(np.abs(Sh).max(axis=(0, 1)) > 1e-14*np.abs(Sh).max())
    for (a, b, c) in big:
        mv = np.array([m[a], m[b], m[c]])
        if not mv.any():
            continue
        kv = mv*2*np.pi/L
        K2 = kv @ kv
        ep, ex, _, _ = pol_tensors(kv)
        s = Sh[:, :, a, b, c]
        T = 0.5*(np.sum(ep*s)*ep + np.sum(ex*s)*ex)
        hTT[:, :, a, b, c] = 2*T/K2
        st = s - np.eye(3)*np.trace(s)/3
        norm_tt[a, b, c] = np.sqrt((np.abs(2*T/K2)**2).sum())
        norm_full[a, b, c] = np.sqrt((np.abs(2*st/K2)**2).sum())
    return hTT, norm_tt, norm_full, m


def analyse(n, L, ratios, delta, with_kinetic=True):
    k, phi, S, X = build(n, L, ratios, delta, with_kinetic=with_kinetic)
    hTT, ntt, nfull, m = tt_strain(S, n, L)
    _, _, Ss, _ = build(n, L, ratios, delta, shortcut=True)
    hTTs, ntts, nfulls, _ = tt_strain(Ss, n, L)
    tt_same = float(np.abs(hTTs - hTT).max()/max(np.abs(hTT).max(), 1e-300))
    modes = sorted({(int(m[a]), int(m[b]), int(m[c]))
                    for a, b, c in np.argwhere(ntt > 1e-12*max(nfull.max(), 1e-300))})
    # real-space plus amplitude of the (k, k, 0) and (-k, -k, 0) pair against cos(K.x)
    mask = np.zeros((n, n, n), bool)
    for s in (1, -1):
        mask[s % n, s % n, 0] = True
    hk = np.where(mask[None, None], hTT, 0)
    hreal = np.real(np.fft.ifftn(hk*n**3, axes=(2, 3, 4)))
    u = np.array([1.0, -1.0, 0.0])/np.sqrt(2)
    zz = np.array([0.0, 0.0, 1.0])
    ep = np.outer(u, u) - np.outer(zz, zz)
    hplus = np.einsum("ij,ij...->...", ep, hreal)/2
    cosK = np.cos(k*(X[0] + X[1]))
    sinK = np.sin(k*(X[0] + X[1]))
    A = np.array([cosK.ravel(), sinK.ravel()]).T
    coef, *_ = np.linalg.lstsq(A, hplus.ravel(), rcond=None)
    # residual TT outside (+-k, +-k, 0): everything except the four modes
    allowed = {(1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0)}
    other = max([ntt[a % n, b % n, c % n] for (a, b, c) in modes if (a, b, c) not in allowed]
                or [0.0])
    return {"ratios": list(ratios), "phi": phi, "modes_with_TT": modes,
            "hplus_cos_coefficient": float(coef[0]), "hplus_sin_coefficient": float(coef[1]),
            "predicted_-5/6_phix_phiy": float(-5/6*phi[0]*phi[1]),
            "fourier_abs_kk0": float(abs(np.einsum("ij,ij->", ep, hTT[:, :, 1, 1, 0])/2)),
            "max_TT_outside_kk0": float(other),
            "fraction_max_TT_over_max_traceless": float(ntt.max()/nfull.max()),
            "fraction_with_scope_source_(10/3)dPhidPhi": float(ntts.max()/nfulls.max()),
            "TT_of_shortcut_minus_TT_of_full_rel": tt_same}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--L", type=float, default=4.0)
    ap.add_argument("--delta", type=float, default=0.01)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"n": a.n, "L": a.L, "delta": a.delta, "k_over_aH": 2*np.pi/a.L}
    res["eps1"] = analyse(a.n, a.L, (1, 1, 0), a.delta)
    res["eps1_without_kinetic_stress"] = analyse(a.n, a.L, (1, 1, 0), a.delta,
                                                 with_kinetic=False)
    res["plane_eps0"] = analyse(a.n, a.L, (1, 0, 0), a.delta)
    res["cosmo_three"] = analyse(a.n, a.L, (1, 0.9, 1.1), a.delta)
    res["three_equal"] = analyse(a.n, a.L, (1, 1, 1), a.delta)
    eps = np.concatenate([np.logspace(-3, 0, 25), [1/(2*np.sqrt(3))]])
    eps.sort()
    scan = [analyse(a.n, a.L, (1, float(e), 0), a.delta) for e in eps]
    res["eps"] = eps.tolist()
    res["scan_cos_coefficient"] = [s["hplus_cos_coefficient"] for s in scan]
    res["scan_predicted"] = [s["predicted_-5/6_phix_phiy"] for s in scan]
    res["scan_fraction"] = [s["fraction_max_TT_over_max_traceless"] for s in scan]
    res["scan_fraction_scope_source"] = [s["fraction_with_scope_source_(10/3)dPhidPhi"]
                                         for s in scan]
    res["scan_TT_shortcut_vs_full_max_rel"] = float(max(
        s["TT_of_shortcut_minus_TT_of_full_rel"] for s in scan))
    res["scan_max_rel_dev"] = float(max(abs(c/p - 1) for c, p in
                                        zip(res["scan_cos_coefficient"], res["scan_predicted"])))
    res["fraction_predicted"] = [float(min(np.sqrt(3)*e, 0.5)) for e in eps]
    res["fraction_max_dev_from_min(sqrt3 eps, 1/2)"] = float(max(
        abs(f - p) for f, p in zip(res["scan_fraction_scope_source"],
                                   res["fraction_predicted"])))
    phi_peak = sum(abs(p) for p in analyse(a.n, a.L, (1, 0.9, 1.1), a.delta)["phi"])
    res["peak_linear_potential_over_delta_cosmo_three"] = phi_peak/a.delta
    # id.json of the production run of cosmo/ (read-only, main checkout)
    idp = "/data/haiyangw/nrpic/runs/cosmo/east_d0.01_n64_pcs4b/id.json"
    if os.path.exists(idp):
        with open(idp) as fh:
            idj = json.load(fh)
        res["id_json_max_abs_psiN"] = idj.get("max_abs_psiN")
        res["id_json_keys"] = sorted(idj)[:40]
    with open(os.path.join(a.out, "v2_crossed.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.09, 0.15, 0.37, 0.78])
    c = -np.array(res["scan_cos_coefficient"])
    ax.loglog(eps, -np.array(res["scan_predicted"]), **fs.GUIDE,
              label=r"$\frac{5}{6}\phi_x\phi_y$ (hand derivation)")
    ax.loglog(eps, c, "o", color=fs.PAL["red"], ms=3.5,
              label=r"$-h_+$ coefficient of $\cos\mathbf{K}\cdot\mathbf{x}$")
    nk = -res["eps1_without_kinetic_stress"]["hplus_cos_coefficient"]
    ax.loglog([1.0], [nk], "s", color=fs.PAL["blue"], ms=5,
              label="without dust stress (3/5 of it)")
    ax.set_xlabel(r"ratio $\epsilon$ of the second wave")
    ax.set_ylabel(r"$|h_+|$ at $\mathbf{K}=(k,k,0)$, $\delta=0.01$")
    ax.legend(loc="lower right", fontsize=8)
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    ax2.loglog(eps, res["fraction_predicted"], **fs.GUIDE,
               label=r"$\min(\sqrt{3}\,\epsilon,\ 1/2)$")
    ax2.loglog(eps, res["scan_fraction_scope_source"], "o", color=fs.PAL["blue"], ms=3.5,
               label=r"scope's measure, source $\frac{10}{3}\Phi_{,i}\Phi_{,j}$")
    ax2.loglog(eps, res["scan_fraction"], "^", color=fs.PAL["yellow"], ms=3.5,
               label="same measure, full source")
    ax2.axvline(1/(2*np.sqrt(3)), **fs.MASK_LINE)
    ax2.axvline(0.18, color=fs.PAL["red"], lw=1, ls=":")
    ax2.text(0.19, 2e-3, "0.18 (scope)", color=fs.PAL["red"], fontsize=8, rotation=90)
    ax2.text(0.30, 2e-3, r"$1/(2\sqrt{3})$", color="grey", fontsize=8, rotation=90)
    ax2.set_xlabel(r"ratio $\epsilon$ of the second wave")
    ax2.set_ylabel("TT fraction")
    ax2.legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(a.out, "v2_crossed"))
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("scan")
                      and k not in ("eps", "fraction_predicted")}, indent=1))


if __name__ == "__main__":
    main()
