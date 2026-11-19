"""P7: the Szekeres slice in conformally flat Cartesian coordinates satisfies the constraints.

psi, K^i_j and rho of the slice t = t_i, built through szekeres/confmap.py on cell-centred
meshes of [-L, L]^3 (L = 7.5, the hole has label radius 6 and Einstein-de Sitter around it),
finite-difference Hamiltonian and momentum residuals with the stencils of order 2 and 4,
normalised by 16 pi rho_b = 6 H^2. Regions by the shell label r: core (r < R1 = 2.4, closed
FLRW), shell (R1 <= r <= R2 = 6, where the dipole lives), outside (r > R2), all.
Models: eps = 0.1 twisted dipole (no symmetry) and eps = 0 (the LTB limit), N = 32 ... Nmax.

    python3 scripts/run_mesh_constraints.py [--nmax 256] [--workers 12]
"""

import argparse
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402
from szekeres import mesh  # noqa: E402

L = 7.5
ORDERS = (2, 4)
REGIONS = {"all": lambda r: np.ones_like(r, dtype=bool),
           "core": lambda r: r < common.PROFILE[1],
           "shell": lambda r: (r >= common.PROFILE[1]) & (r <= common.PROFILE[2]),
           "outside": lambda r: r > common.PROFILE[2]}
_CM = None


def _work(args):
    N, i0, i1, norm = args
    sub = _Slab(_CM, i0, i1)
    return mesh.residuals(sub, N, L, orders=ORDERS, regions=REGIONS, slab=i1 - i0, norm=norm,
                          plane_axis=1, slab_range=(i0, i1))


class _Slab:
    """Pass-through to the map (the slab range is handled by mesh.residuals)."""

    def __init__(self, cm, i0, i1):
        self.cm, self.i0, self.i1 = cm, i0, i1

    def fields(self, x):
        return self.cm.fields(x)

    def kmix(self, f):
        return self.cm.kmix(f)


def combine(parts):
    out = {}
    for p in ORDERS:
        out[p] = {}
        for name in REGIONS:
            n = sum(pt[0][p][name]["ncell"] for pt in parts)
            if n == 0:
                out[p][name] = None
                continue
            s1H = sum(pt[0][p][name]["H_L1"] * pt[0][p][name]["ncell"] for pt in parts)
            s2H = sum(pt[0][p][name]["H_L2"] ** 2 * pt[0][p][name]["ncell"] for pt in parts)
            s1M = sum(pt[0][p][name]["M_L1"] * pt[0][p][name]["ncell"] for pt in parts)
            s2M = sum(pt[0][p][name]["M_L2"] ** 2 * pt[0][p][name]["ncell"] for pt in parts)
            out[p][name] = dict(H_L1=s1H / n, H_L2=math.sqrt(s2H / n),
                                H_Linf=max(pt[0][p][name]["H_Linf"] for pt in parts),
                                M_L1=s1M / n, M_L2=math.sqrt(s2M / n),
                                M_Linf=max(pt[0][p][name]["M_Linf"] for pt in parts), ncell=n)
    planes = {p: (sum(pt[1][p][0] for pt in parts), sum(pt[1][p][1] for pt in parts)) for p in ORDERS}
    return out, planes, parts[0][2]


def run_model(cm, N, workers, norm):
    global _CM
    _CM = cm
    nchunk = max(1, min(N, 4 * workers))
    edges = np.linspace(0, N, nchunk + 1).astype(int)
    tasks = [(N, int(edges[i]), int(edges[i + 1]), norm) for i in range(nchunk) if edges[i + 1] > edges[i]]
    ctx = mp.get_context("fork")
    with ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as ex:
        parts = list(ex.map(_work, tasks))
    return combine(parts)


def orders_of(res, Ns, p, region, key):
    vals = [res[N][p][region][key] for N in Ns]
    return [math.log(vals[i] / vals[i + 1]) / math.log(Ns[i + 1] / Ns[i]) for i in range(len(Ns) - 1)]


def figures(res, Ns, planes, cvec, rdir):
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.93, wspace=0.28)
    h = np.array([2 * L / N for N in Ns])
    for ax, key, lab in ((axs[0], "H_L2", r"$\|H\|_2/(16\pi\rho_b)$"), (axs[1], "M_L2", r"$\|M\|_2/(16\pi\rho_b)$")):
        for model, col in (("szekeres", fs.PAL["red"]), ("ltb", fs.PAL["blue"])):
            for p, ls in ((2, "--"), (4, "-")):
                for region, mk in (("all", "o"), ("shell", "s")):
                    y = [res[model][N][p][region][key] for N in Ns]
                    ax.loglog(h, y, ls=ls, marker=mk, color=col, ms=4,
                              label=f"{'Szekeres' if model == 'szekeres' else 'LTB'}, order {p}, {region}")
        for p in (2, 4):
            y0 = res["szekeres"][Ns[-1]][p]["all"][key]
            ax.loglog(h, y0 * (h / h[-1]) ** p, color="k", lw=1.0, ls=":")
        ax.set_xlabel(r"cell size $h$")
        ax.set_ylabel(lab)
    axs[0].legend(ncol=1, fontsize=6.5, loc="lower right")
    axs[0].set_title("Hamiltonian")
    axs[1].set_title("momentum")
    common.save_fig(fig, "fig_mesh_constraints", rdir)
    plt.close(fig)
    # residual maps of the Szekeres model, plane y ~ 0, order 4, largest N
    Hm, Mm = planes
    fig, axes, cax = fs.slice_mosaic(1, 2)
    v = max(np.abs(Hm).max(), Mm.max())
    ext = [cvec[0], cvec[-1], cvec[0], cvec[-1]]
    for ax, F, t in ((axes[0][0] if np.ndim(axes) == 2 else axes[0], Hm, r"$H$"),
                     (axes[0][1] if np.ndim(axes) == 2 else axes[1], Mm, r"$|M|$")):
        im = ax.imshow(F.T, origin="lower", extent=ext, cmap="RdBu_r", vmin=-v, vmax=v,
                       interpolation="none", rasterized=True)
        ax.set_title(t + f", order 4, N = {Ns[-1]}")
        ax.set_xlabel("x")
    fig.colorbar(im, cax=cax, label=r"residual $/(16\pi\rho_b)$")
    common.save_fig(fig, "fig_residual_maps", rdir)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=256)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    rdir = common.run_dir("mesh_constraints")
    ltb, szk = common.models()
    norm = 16 * math.pi * szk.rho_b
    Ns = [n for n in (32, 64, 128, 256, 512) if n <= a.nmax]
    res = {"szekeres": {}, "ltb": {}}
    planes = cvec = None
    timing = {}
    for name, model in (("szekeres", szk), ("ltb", ltb)):
        cm = ConformalMap(model)
        for N in Ns:
            t0 = time.time()
            out, pl, cv = run_model(cm, N, a.workers, norm)
            timing[f"{name}_{N}"] = time.time() - t0
            res[name][N] = out
            if name == "szekeres" and N == Ns[-1]:
                planes, cvec = pl[4], cv
            print(name, N, f"{timing[f'{name}_{N}']:.0f} s",
                  {p: (out[p]["all"]["H_L2"], out[p]["all"]["M_L2"]) for p in ORDERS}, flush=True)
    summary = {}
    for name in res:
        summary[name] = {}
        for p in ORDERS:
            for region in REGIONS:
                if res[name][Ns[0]][p][region] is None:
                    continue
                for key in ("H_L2", "M_L2", "H_Linf", "M_Linf", "H_L1", "M_L1"):
                    summary[name][f"order{p}_{region}_{key}"] = dict(
                        values=[res[name][N][p][region][key] for N in Ns],
                        orders=orders_of(res[name], Ns, p, region, key))
    common.dump(os.path.join(rdir, "mesh_constraints.json"),
                dict(run_id=common.run_id(), commit=common.git_commit(), L=L, Ns=Ns, norm="16 pi rho_b",
                     model=szk.summary(), results=summary, timing=timing))
    figures(res, Ns, planes, cvec, rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
