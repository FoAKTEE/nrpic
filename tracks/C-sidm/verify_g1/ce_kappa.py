"""V1a: Chapman-Enskog thermal conductivity of a hard-sphere gas (isotropic elastic
scattering in the centre-of-momentum frame, constant total cross-section sigma_tot), from
Monte Carlo evaluation of the collision brackets. Own derivation (JOURNAL entry 1):

  first-order Chapman-Enskog equation  L[Phi] = X,  kappa = k_B <X, L^-1 X> / T^2,
  <a, b> = int f0 a b d^3p,   <Phi, L Phi> = (1/4) n^2 sigma_tot E[v_rel (Delta Phi)^2]
  (pairs drawn from f0 x f0, direction uniform in the CM frame, Delta = sum after - before).

Non-relativistic: X = T (x - 5/2) c_z, x = m c^2/(2T); Ritz basis Phi_j = S_j(x) c_z,
S_j = generalised Laguerre L_j^(3/2) (Sonine), j = 1..4. Relativistic (Eckart frame, own
derivation: the vector part of the streaming term is f0 (E - h) v.(grad T + T a)/T^2):
X = (E - h) v_z, h = m K3/K2; Delta X = -h Delta v_z exactly (momentum conservation);
basis {v_z, y^2 v_z, y^3 v_z, y^4 v_z}, y = (E - m)/T (v_z is X modulo the invariant p_z).

Output: kappa in units k_B sqrt(k_B T/m)/sigma_tot for each order; JSON and a figure.
"""
import argparse
import os
import sys

import numpy as np
from scipy import special, integrate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402


def nonrel(npairs, nbatch, seed):
    rng = np.random.default_rng(seed)
    M = 4
    Bs = []
    for _ in range(nbatch):
        n = npairs//nbatch
        c = rng.standard_normal((n, 3))
        c1 = rng.standard_normal((n, 3))
        V = 0.5*(c + c1)
        g = c - c1
        gm = np.sqrt(np.einsum("ij,ij->i", g, g))
        nh = lib.isotropic(n, rng)
        cp = V + 0.5*gm[:, None]*nh
        c1p = V - 0.5*gm[:, None]*nh

        def phis(v):
            x = 0.5*np.einsum("ij,ij->i", v, v)
            return np.stack([special.eval_genlaguerre(j, 1.5, x)*v[:, 2]
                             for j in range(1, M + 1)], axis=1)
        dphi = phis(cp) + phis(c1p) - phis(c) - phis(c1)
        Bs.append(np.einsum("i,ij,ik->jk", gm, dphi, dphi)/n)
    Bs = np.array(Bs)
    # b_1 = <X, S_1 c_z>/n = -E[S_1^2 c_z^2] = -5/2 (analytic, T/m = 1); b_j>1 = 0
    out = []
    for order in range(1, M + 1):
        vals = []
        for Bb in Bs:
            Bi = np.linalg.inv(Bb[:order, :order])
            vals.append(25.0*Bi[0, 0])          # kappa sigma_tot (k_B = T = m = 1)
        Bm = Bs.mean(axis=0)
        k_all = 25.0*np.linalg.inv(Bm[:order, :order])[0, 0]
        out.append(dict(order=order, kappa=k_all,
                        se=np.std(vals, ddof=1)/np.sqrt(len(vals))))
    ratios = []
    for order in range(1, M + 1):
        r = [np.linalg.inv(Bb[:order, :order])[0, 0]*Bb[0, 0] for Bb in Bs]
        ratios.append(dict(order=order, ratio_to_first=float(np.mean(r)),
                           se=float(np.std(r, ddof=1)/np.sqrt(len(r)))))
    # check of the analytic b_1 with the last batch
    x = 0.5*np.einsum("ij,ij->i", c, c)
    b1_mc = -np.mean((special.eval_genlaguerre(1, 1.5, x)*c[:, 2])**2)
    return out, ratios, float(b1_mc)


def mj_moment(theta, fn):
    """E_MJ[fn(u, W)] over the isotropic MJ distribution of |u| (quadrature)."""
    def dens(s):
        u = s*s
        w = np.sqrt(1 + u*u)
        return u*u*np.exp(-(w - 1)/theta)*2*s
    smax = np.sqrt(np.sqrt((1 + 90*theta)**2 - 1))
    pts = np.linspace(0, smax, 9)[1:-1]
    z, _ = integrate.quad(dens, 0, smax, points=pts, limit=500, epsabs=0, epsrel=1e-13)

    def num(s):
        u = s*s
        w = np.sqrt(1 + u*u)
        return fn(u, w)*dens(s)
    v, _ = integrate.quad(num, 0, smax, points=pts, limit=500, epsabs=0, epsrel=1e-13)
    return v/z


def rel(theta, npairs, nbatch, seed):
    rng = np.random.default_rng(seed)
    smp = lib.MJSampler(theta)
    h = lib.enthalpy(theta)
    js = [0, 2, 3, 4]
    Bs = []
    for _ in range(nbatch):
        n = npairs//nbatch
        ua = smp.sample(n, rng)
        ub = smp.sample(n, rng)
        nh = lib.isotropic(n, rng)
        uan, ubn, wa, wb, vmol, _ = lib.scatter_rel(ua, ub, nh)
        wan = np.sqrt(1 + np.einsum("ij,ij->i", uan, uan))
        wbn = np.sqrt(1 + np.einsum("ij,ij->i", ubn, ubn))

        def phis(u, w):
            y = (w - 1)/theta
            vz = u[:, 2]/w
            return np.stack([y**j*vz for j in js], axis=1)
        dphi = phis(uan, wan) + phis(ubn, wbn) - phis(ua, wa) - phis(ub, wb)
        Bs.append(np.einsum("i,ij,ik->jk", vmol, dphi, dphi)/n)
    Bs = np.array(Bs)
    # b vector by quadrature: b_j = E[(W - h) y^j v_z^2] = E[(W - h) y^j v^2]/3
    XX = mj_moment(theta, lambda u, w: (w - h)**2*(u/w)**2/3)
    Xv = mj_moment(theta, lambda u, w: (w - h)*(u/w)**2/3)
    b = [-XX/h]
    for j in js[1:]:
        b.append(mj_moment(theta, lambda u, w, j=j: (w - h)*((w - 1)/theta)**j*(u/w)**2/3))
    b = np.array(b)
    norm = np.sqrt(theta)                      # report kappa sigma_tot / sqrt(theta)
    out = []
    for order in range(1, len(js) + 1):
        vals = []
        for Bb in Bs:
            Bi = np.linalg.inv(Bb[:order, :order])
            vals.append(4*b[:order] @ Bi @ b[:order]/theta**2/norm)
        Bm = Bs.mean(axis=0)
        k_all = 4*b[:order] @ np.linalg.inv(Bm[:order, :order]) @ b[:order]/theta**2/norm
        out.append(dict(order=order, kappa=float(k_all),
                        se=float(np.std(vals, ddof=1)/np.sqrt(len(vals)))))
    return dict(theta=theta, h=h, XX=XX, Xv_direct=Xv, Xv_identity=-XX/h,
                c_p=lib.c_v(theta) + 1, orders=out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npairs", type=int, default=40_000_000)
    ap.add_argument("--nrel", type=int, default=20_000_000)
    ap.add_argument("--thetas", type=float, nargs="+", default=[1e-4, 0.003, 0.1, 1.0])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir("/data/haiyangw/nrpic/scratch/C-sidm/tmp/verify_g1")
    os.makedirs(out, exist_ok=True)
    nr, ratios, b1 = nonrel(a.npairs, 40, 1)
    res = dict(nonrel=nr, nonrel_ratio=ratios, nonrel_b1_mc=b1,
               nonrel_b1_exact=-2.5, first_approx_exact=75*np.sqrt(np.pi)/64)
    print("non-relativistic:", nr, ratios, "b1", b1)
    res["rel"] = []
    for th in a.thetas:
        r = rel(th, a.nrel if th == 0.003 else a.nrel//2, 40, 2)
        print("theta", th, r)
        res["rel"].append(r)
    lib.save_json(os.path.join(out, "ce_kappa.json"), res)
    # figure
    sys.path.insert(0, "/data/haiyangw/nrpic/wt/C-sidm/python")
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.93, wspace=0.3)
    o = [d["order"] for d in nr]
    ax[0].errorbar(o, [d["kappa"] for d in nr], yerr=[d["se"] for d in nr], fmt="o",
                   color=figstyle.PAL["red"], label="Monte Carlo brackets (own)")
    ax[0].axhline(75*np.sqrt(np.pi)/64, color="k", ls="--", lw=1,
                  label=r"$75\sqrt{\pi}/64$ (first approx.)")
    ax[0].axhline(1.025*75*np.sqrt(np.pi)/64, color="k", ls=":", lw=1,
                  label=r"$\times 1.025$ [BACKGROUND]")
    ax[0].set_xlabel("Sonine order")
    ax[0].set_ylabel(r"$\kappa\,\sigma_{\rm tot}/(k_B\sqrt{k_BT/m})$")
    ax[0].legend(loc="lower right")
    ax[0].set_title("non-relativistic hard spheres")
    for r in res["rel"]:
        ax[1].errorbar([d["order"] for d in r["orders"]], [d["kappa"] for d in r["orders"]],
                       yerr=[d["se"] for d in r["orders"]], fmt="o-", ms=4,
                       label=r"$\theta=%g$" % r["theta"])
    ax[1].axhline(75*np.sqrt(np.pi)/64, color="k", ls="--", lw=1)
    ax[1].set_xlabel("order of the trial space")
    ax[1].set_ylabel(r"$\kappa\,\sigma_{\rm tot}/\sqrt{\theta}$ (Eckart)")
    ax[1].legend(loc="best", ncol=2)
    ax[1].set_title("relativistic (Moller flux, isotropic CM)")
    fig.savefig(os.path.join(out, "v1a_ce_kappa.png"))
    print("wrote", out)


if __name__ == "__main__":
    main()
