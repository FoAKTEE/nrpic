"""Choice of the dipole amplitude eps for the card series (JOURNAL entry 7).

For eps = 0.1 and 0.2 (twisted dipole, the reference profile of common.py):
1. regularity margins (R'/R)/|b| and (M'/(3M))/|b|, minimum over the shell labels at each
   proper time tau in [0, 40] (both scale exactly as 1/eps: b is linear in eps and R, M do
   not depend on it; computed anyway);
2. the non-spherical signal the code must reproduce, at tau = 0, 10, 20, 30, 40:
   (a) the direction dependence on one shell, max over r of |X(r, +|b|) - X(r, -|b|)|
       (rho relative to the shell mean, K in units of the background H(tau));
   (b) Szekeres minus the LTB solution with the same M, k at the same code coordinates
       (what a spherical code would miss), max over the cells of a 128^3 mesh of [-8, 8]^3;
3. the smallest gradient scales on that mesh: min rho/|grad rho| (3-D, central differences
   at h = 0.125) and max|K|/max|grad K| (K changes sign at turnaround);
4. the finite-difference Hamiltonian and momentum residuals (stencil order 4) of the
   initial slice at N = 64 and 128 on [-8, 8]^3, shell region, in units of 16 pi rho_b.
The truncation error of a run at fixed h scales like (h/L)^p with L the gradient scale;
the ratio signal / truncation error decides (DESIGN.md section 7). Writes eps_choice.json
and fig_eps_choice.

    python3 scripts/run_eps_choice.py [--workers 6] [--n 128]
"""

import argparse
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402
from szekeres import mesh  # noqa: E402

EPS = (0.1, 0.2)
TAUS = (0.0, 10.0, 20.0, 30.0, 40.0)
LH = 8.0
R1, R2 = common.PROFILE[1], common.PROFILE[2]
REGIONS = {"shell": lambda r: (r >= R1) & (r <= R2), "all": lambda r: np.ones_like(r, dtype=bool)}
_MAPS = {}


def _map(eps):
    if eps not in _MAPS:
        ltb, szk = common.models(eps=eps)
        _MAPS[eps] = ConformalMap(szk if eps > 0 else ltb)
    return _MAPS[eps]


def _labels(args):
    eps, pts = args
    f = _map(eps).fields(pts)
    return f["r"], f["bn"]


class _P:
    def __init__(self, cm):
        self.cm = cm

    def fields(self, x):
        return self.cm.fields(x)

    def kmix(self, f):
        return self.cm.kmix(f)


def _resid(args):
    eps, N, i0, i1, norm = args
    return mesh.residuals(_P(_map(eps)), N, LH, orders=(4,), regions=REGIONS, slab=i1 - i0, norm=norm,
                          slab_range=(i0, i1))


def combine(parts):
    out = {}
    for name in REGIONS:
        n = sum(p[4][name]["ncell"] for p in parts)
        nn = max(n, 1)
        out[name] = dict(
            H_L2=math.sqrt(sum(p[4][name]["H_L2"] ** 2 * p[4][name]["ncell"] for p in parts) / nn),
            H_Linf=max(p[4][name]["H_Linf"] for p in parts),
            M_L2=math.sqrt(sum(p[4][name]["M_L2"] ** 2 * p[4][name]["ncell"] for p in parts) / nn),
            M_Linf=max(p[4][name]["M_Linf"] for p in parts), ncell=n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--n", type=int, default=128)
    a = ap.parse_args()
    rdir = common.run_dir("eps_choice")
    ltb, _ = common.models()
    t_i, H, rho_b = ltb.t_i, ltb.H, ltb.rho_b
    out = dict(run_id=common.run_id(), commit=common.git_commit(), eps=list(EPS), taus=list(TAUS), n=a.n, LH=LH)
    ctx = mp.get_context("fork")
    # mesh of the code coordinates
    N = a.n
    c = -LH + (np.arange(N) + 0.5) * (2 * LH / N)
    hgrid = 2 * LH / N
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    chunks = np.array_split(pts, 6 * a.workers)
    with ProcessPoolExecutor(a.workers, mp_context=ctx) as ex:
        res0 = list(ex.map(_labels, [(0.0, ch) for ch in chunks]))
    r_ltb = np.concatenate([q[0] for q in res0]).reshape(X.shape)
    tau_dense = np.linspace(0.0, 40.0, 81)
    rr = np.linspace(R1 + 1e-6, R2 - 1e-6, 1500)
    figdata = {}
    for eps in EPS:
        _, szk = common.models(eps=eps)
        row = dict(eps=eps)
        # 1. margins
        m1 = np.array([np.min(szk.margins(t_i + ta, rr)[0]) for ta in tau_dense])
        m2 = np.array([np.min(szk.margins(t_i + ta, rr)[1]) for ta in tau_dense])
        row["margin_RpR_over_b_min"] = float(m1.min())
        row["margin_Mp3M_over_b_min"] = float(m2.min())
        row["margin_Mp3M_over_b_min_tau"] = float(tau_dense[np.argmin(m2)])
        # 2a. direction dependence on a shell
        bb = np.linalg.norm(szk.dip.b(rr), axis=-1)
        shell = []
        for ta in TAUS:
            fp = szk.fields(t_i + ta, rr, bb)
            fm = szk.fields(t_i + ta, rr, -bb)
            a_ = (1 + ta / t_i) ** (2.0 / 3.0)
            Hb = H / a_ ** 1.5
            shell.append(dict(tau=ta,
                              rho_rel=float(np.max(np.abs(fp["rho"] - fm["rho"]) / (0.5 * (fp["rho"] + fm["rho"])))),
                              K_over_H=float(np.max(np.abs(fp["K"] - fm["K"])) / Hb),
                              KL_over_H=float(np.max(np.abs(fp["KL"] - fm["KL"])) / Hb),
                              rho_ratio_min=float(np.min(np.minimum(fp["rho"], fm["rho"]) / np.maximum(fp["rho"], fm["rho"])))))
        row["shell_direction_dependence"] = shell
        # 2b, 3. mesh
        with ProcessPoolExecutor(a.workers, mp_context=ctx) as ex:
            res = list(ex.map(_labels, [(eps, ch) for ch in chunks]))
        r_sz = np.concatenate([q[0] for q in res]).reshape(X.shape)
        bn_sz = np.concatenate([q[1] for q in res]).reshape(X.shape)
        mesh_rows = []
        for ta in TAUS:
            fs_ = szk.fields(t_i + ta, r_sz, bn_sz)
            fl_ = ltb.fields(t_i + ta, r_ltb, np.zeros_like(r_ltb))
            a_ = (1 + ta / t_i) ** (2.0 / 3.0)
            Hb, rb = H / a_ ** 1.5, rho_b / a_ ** 3
            rho = fs_["rho"]
            g = np.gradient(rho, hgrid)
            gabs = np.sqrt(g[0] ** 2 + g[1] ** 2 + g[2] ** 2)
            K = fs_["K"]
            gK = np.gradient(K, hgrid)
            gKabs = np.sqrt(gK[0] ** 2 + gK[1] ** 2 + gK[2] ** 2)
            mesh_rows.append(dict(
                tau=ta,
                sz_minus_ltb_rho_rel_max=float(np.max(np.abs(rho - fl_["rho"]) / rho)),
                sz_minus_ltb_K_over_H_max=float(np.max(np.abs(K - fl_["K"])) / Hb),
                rho_over_rhob_min=float(rho.min() / rb), rho_over_rhob_max=float(rho.max() / rb),
                rho_scale_min=float(np.min(rho / np.maximum(gabs, 1e-300))),
                K_scale=float(np.max(np.abs(K)) / np.max(gKabs))))
        row["mesh"] = mesh_rows
        # 4. initial-data residuals, order-4 stencil
        resid = {}
        for Nr in (64, 128):
            slabs = [(i, min(Nr, i + max(2, Nr // (2 * a.workers)))) for i in range(0, Nr, max(2, Nr // (2 * a.workers)))]
            with ProcessPoolExecutor(a.workers, mp_context=ctx) as ex:
                parts = list(ex.map(_resid, [(eps, Nr, i0, i1, 16 * math.pi * rho_b) for i0, i1 in slabs]))
            resid[str(Nr)] = combine(parts)
        row["residual_order4"] = resid
        figdata[eps, "m"] = (m1, m2)
        out[f"eps{eps:g}"] = row
        print(eps, {k: v for k, v in row.items() if k not in ("mesh", "shell_direction_dependence")}, flush=True)
        for m in mesh_rows:
            print("  ", m, flush=True)
        for s in shell:
            print("  ", s, flush=True)
    # decision quantities: signal / (h/L)^p at each tau, relative to eps = 0.1, p = 2 and 4
    dec = []
    for i, ta in enumerate(TAUS):
        r1, r2 = out["eps0.1"]["mesh"][i], out["eps0.2"]["mesh"][i]
        s1 = out["eps0.1"]["shell_direction_dependence"][i]
        s2 = out["eps0.2"]["shell_direction_dependence"][i]
        d = dict(tau=ta, signal_ratio_rho=s2["rho_rel"] / s1["rho_rel"], signal_ratio_K=s2["K_over_H"] / s1["K_over_H"],
                 scale_ratio_rho=r2["rho_scale_min"] / r1["rho_scale_min"])
        for p in (2, 4):
            d[f"signal_over_error_gain_p{p}_rho"] = d["signal_ratio_rho"] * d["scale_ratio_rho"] ** p
            d[f"signal_over_error_gain_p{p}_K"] = d["signal_ratio_K"] * d["scale_ratio_rho"] ** p
        dec.append(d)
    out["decision"] = dec
    for d in dec:
        print("decision", d, flush=True)
    common.dump(os.path.join(rdir, "eps_choice.json"), out)

    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.17, top=0.9, wspace=0.38)
    cols = {0.1: fs.PAL["blue"], 0.2: fs.PAL["red"]}
    for eps in EPS:
        m1, m2 = figdata[eps, "m"]
        axs[0].plot(tau_dense, m1, color=cols[eps], label=rf"$(R'/R)/|b|$, $\epsilon={eps:g}$")
        axs[0].plot(tau_dense, m2, color=cols[eps], ls="--", label=rf"$(M'/3M)/|b|$, $\epsilon={eps:g}$")
        row = out[f"eps{eps:g}"]
        axs[1].semilogy(TAUS, [s["rho_rel"] for s in row["shell_direction_dependence"]], "o-", color=cols[eps], ms=3,
                        label=rf"$\rho(+b)$ vs $\rho(-b)$, $\epsilon={eps:g}$")
        axs[1].semilogy(TAUS, [s["K_over_H"] for s in row["shell_direction_dependence"]], "s--", color=cols[eps], ms=3,
                        label=rf"$|\Delta K|/H$, $\epsilon={eps:g}$")
        axs[2].plot(TAUS, [m["rho_scale_min"] for m in row["mesh"]], "o-", color=cols[eps], ms=3,
                    label=rf"$\min\rho/|\nabla\rho|$, $\epsilon={eps:g}$")
    axs[0].axhline(1.0, **fs.GUIDE)
    axs[0].set_ylim(0, 12)
    axs[0].set_xlabel(r"proper time $\tau$")
    axs[0].set_ylabel("regularity margin (min over shells)")
    axs[0].legend(fontsize=6, loc="upper right")
    axs[1].set_xlabel(r"proper time $\tau$")
    axs[1].set_ylabel("direction dependence on a shell")
    axs[1].legend(fontsize=6, loc="upper left")
    axs[2].axhline(0.0625, color="k", lw=1.0, ls=":")
    axs[2].axhline(0.125, color="k", lw=1.0, ls=":")
    axs[2].text(1, 0.07, "h(256)", fontsize=7)
    axs[2].text(1, 0.135, "h(128)", fontsize=7)
    axs[2].set_ylim(0, 0.7)
    axs[2].set_xlabel(r"proper time $\tau$")
    axs[2].set_ylabel("density scale (code coordinates)")
    axs[2].legend(fontsize=6, loc="upper right")
    common.save_fig(fig, "fig_eps_choice", rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
