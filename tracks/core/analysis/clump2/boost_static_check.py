#!/usr/bin/env python3
"""Outcome of the tests TB of tracks/core/JOURNAL-clump2.md: reads the runs of
run_boost_static.py, compares with predict_boost.py and the Python reference, writes
boost_static_check.json and the figures fig_boost_static_*.{pdf,png} into --out.

    boost_static_check.py --run RUN_ID [--out DIR]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
sys.path.insert(0, HERE)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mp_common import read_bin  # noqa: E402
from nrpic import boosted_cluster as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402
import predict_boost as pb  # noqa: E402

RCUT = 14.0
NS = (32, 64, 128)
VS = ("0.1", "0.3")


class Case:
    """constraint dump of one case: fields over all cells and the cell geometry"""

    def __init__(self, top, label):
        d = os.path.join(top, label, "bin")
        _, _, x, y, z, dx, con = read_bin(os.path.join(d, "clump.con.00000.bin"))
        _, _, _, _, _, _, adm = read_bin(os.path.join(d, "clump.adm_psi4.00000.bin"))
        self.x = np.stack([x, y, z], axis=-1)
        self.r = np.sqrt(np.sum(self.x ** 2, axis=1))
        self.dV = dx ** 3
        self.dx = float(dx[0])
        self.psi = adm["adm_psi4"] ** 0.25
        self.H = con["con_H"]
        self.M = np.stack([con["con_Mx"], con["con_My"], con["con_Mz"]], axis=-1)
        self.inside = self.r < RCUT

    def norm_H(self, H=None):
        H = self.H if H is None else H
        w = self.inside
        return math.sqrt(np.sum((self.psi ** 6 * H * H * self.dV)[w]))

    def norm_M(self, M=None):
        M = self.M if M is None else M
        w = self.inside
        return math.sqrt(np.sum((self.psi ** 2 * np.sum(M * M, axis=1) * self.dV)[w]))

    def norm_Mx(self, Mx=None):
        Mx = self.M[:, 0] if Mx is None else Mx
        w = self.inside
        return math.sqrt(np.sum((self.psi ** 6 * Mx * Mx * self.dV)[w]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    top = os.path.join(SCRATCH, a.run)
    with open(os.path.join(top, "cases.json")) as f:
        cj = json.load(f)
    os.makedirs(a.out, exist_ok=True)
    md = stc.STModel(0.819)
    B = bc.BoostedST(md)
    cont = {v: pb.continuum(B, float(v) / math.sqrt(1.0 - float(v) ** 2), RCUT) for v in VS}
    out = dict(run=a.run, rcut=RCUT, continuum=cont, TB1={}, TB2={}, TB3={}, TB4={})
    keep = {}

    for n in NS:
        st = Case(top, f"q0_n{n}")
        out.setdefault("static", {})[str(n)] = dict(
            H_norm=st.norm_H(), M_norm=st.norm_M(),
            H_norm_history=math.sqrt(cj["cases"][f"q0_n{n}"]["hst0"][3]))
        for v in VS:
            none = Case(top, f"q{v}_n{n}_none")
            curv = Case(top, f"q{v}_n{n}_curv")
            corr = Case(top, f"q{v}_n{n}_corr")
            key = f"v={v},n={n}"
            m0, m1 = none.norm_M(), curv.norm_M()
            out["TB1"][key] = dict(M_norm=m0, continuum=cont[v]["M_norm"],
                                   ratio=m0 / cont[v]["M_norm"])
            cterm = curv.M[:, 0] - none.M[:, 0]
            out["TB2"][key] = dict(
                M_norm_curv=m1, ratio=m1 / m0, M_norm_corr=corr.norm_M(),
                curvature_term_Mx_norm=none.norm_Mx(cterm),
                continuum_Mx_norm=cont[v]["Mx_norm"],
                curvature_term_over_continuum=none.norm_Mx(cterm) / cont[v]["Mx_norm"],
                boundary_layer_M_norm=math.sqrt(np.sum(
                    (curv.psi ** 2 * np.sum(curv.M ** 2, axis=1) * curv.dV)[~curv.inside])))
            d_curv = curv.H - st.H
            d_corr = corr.H - st.H
            d_none = none.H - st.H
            w = st.inside
            wt = st.psi ** 6 * st.dV
            proj = float(np.sum((wt * d_corr * d_curv)[w]) / np.sum((wt * d_curv ** 2)[w]))
            out["TB3"][key] = dict(
                DH_none=st.norm_H(d_none), DH_curv=st.norm_H(d_curv),
                DH_corr=st.norm_H(d_corr), continuum=cont[v]["H2_norm"],
                DH_curv_over_continuum=st.norm_H(d_curv) / cont[v]["H2_norm"],
                ratio_corr_over_curv=st.norm_H(d_corr) / st.norm_H(d_curv),
                projection=proj, H_norm_static=st.norm_H(), H_norm_curv=curv.norm_H(),
                H_norm_corr=corr.norm_H())
            h = cj["cases"]
            out["TB4"][key] = {c: dict(H_norm=math.sqrt(h[f"q{v}_n{n}_{c}"]["hst0"][3]),
                                       M_norm=math.sqrt(h[f"q{v}_n{n}_{c}"]["hst0"][4]))
                               for c in ("none", "curv", "corr")}
            if n == 128 and v == "0.3":
                keep = dict(none=none, curv=curv, st=st, d_curv=d_curv, d_corr=d_corr)

    # ---- TB5: fields of the code against the reference (64 cells, v = 0.3, all on)
    d = os.path.join(top, "q0.3_n64_corr", "bin")
    _, _, x, y, z, _, adm = read_bin(os.path.join(d, "clump.adm.00000.bin"))
    _, _, _, _, _, _, z4 = read_bin(os.path.join(d, "clump.z4c.00000.bin"))
    X = np.stack([x, y, z], axis=-1)
    BC = bc.BoostedClusters([dict(yc=0.819, mass=1.0, centre=(0, 0, 0), v=(0.3, 0, 0))])
    prob = cj["ic"]["q0.3"]["athenak"]["problem"]
    P = np.array([prob[f"comp0_p{c}"] for c in (1, 2, 3)])
    psi = BC.psi(X)
    kref = BC.abar(X, [P]) / psi[:, None, None] ** 2
    names = ["adm_Kxx", "adm_Kxy", "adm_Kxz", "adm_Kyy", "adm_Kyz", "adm_Kzz"]
    idx = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    ksc = float(np.max(np.abs(kref)))
    b = BC.boost[0]
    bref = b.shift(X, (0, 0, 0), P / b.pmass)
    bsc = float(np.max(np.abs(bref)))
    r = np.sqrt(np.sum(X * X, axis=1))
    out["TB5"] = dict(
        psi4=float(np.max(np.abs(adm["adm_psi4"] / psi ** 4 - 1.0))),
        K=max(float(np.max(np.abs(adm[nm] - kref[:, i, j]))) / ksc
              for nm, (i, j) in zip(names, idx)),
        K_largest=ksc,
        beta=max(float(np.max(np.abs(z4[nm] - bref[:, c]))) / bsc
                 for c, nm in enumerate(("z4c_betax", "z4c_betay", "z4c_betaz"))),
        beta_largest=bsc,
        alpha=float(np.max(np.abs(z4["z4c_alpha"] - md.alpha(r)))),
        trace_K=float(np.max(np.abs(z4["z4c_Khat"]))))

    # ---- TB6: the stratified sample of the evolution
    s0 = Case(top, "s0_n64")
    sn = Case(top, "s0.3_n64_none")
    sc = Case(top, "s0.3_n64_curv")
    so = Case(top, "s0.3_n64_corr")
    probs = cj["ic"]["s0.3"]["athenak"]["problem"]
    Ps = np.array([probs[f"comp0_p{c}"] for c in (1, 2, 3)])
    T = -8.0 * math.pi * sn.psi ** -6 * B.momentum_density(sn.x, (0, 0, 0), Ps)[:, 0]
    wt = (sn.psi ** 6 * sn.dV) * sn.inside

    def proj(c):
        return float(np.sum(wt * c.M[:, 0] * T) / np.sum(wt * T * T))
    out["TB6"] = dict(
        M_norm2={k: c.norm_M() ** 2 for k, c in (("static", s0), ("none", sn),
                                                  ("curv", sc), ("corr", so))},
        H_norm={k: c.norm_H() for k, c in (("static", s0), ("none", sn), ("curv", sc),
                                           ("corr", so))},
        M_norm2_drop=sn.norm_M() ** 2 - sc.norm_M() ** 2,
        smooth_M_norm2=cont["0.3"]["M_norm"] ** 2,
        projection_none=proj(sn), projection_curv=proj(sc), projection_static=proj(s0))

    # ---- figures
    fs.use_style()
    dxs = np.array([32.0 / n for n in NS])
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.96, wspace=0.26)
    for v, ls in zip(VS, ("--", "-")):
        ax[0].plot(dxs, [out["TB1"][f"v={v},n={n}"]["M_norm"] for n in NS], "o" + ls,
                   color=fs.PAL["blue"], label=rf"$K_{{ij}} = 0$, $v = {v}$")
        ax[0].plot(dxs, [out["TB2"][f"v={v},n={n}"]["M_norm_curv"] for n in NS], "s" + ls,
                   color=fs.PAL["red"], label=rf"boost table, $v = {v}$")
        ax[0].axhline(cont[v]["M_norm"], **fs.THIN, ls=":")
        ax[1].plot(dxs, [out["TB3"][f"v={v},n={n}"]["DH_curv"] for n in NS], "o" + ls,
                   color=fs.PAL["blue"], label=rf"no correction, $v = {v}$")
        ax[1].plot(dxs, [out["TB3"][f"v={v},n={n}"]["DH_corr"] for n in NS], "s" + ls,
                   color=fs.PAL["red"], label=rf"corrected $\psi$, $v = {v}$")
        ax[1].axhline(cont[v]["H2_norm"], **fs.THIN, ls=":")
    ax[1].plot(dxs, [out["static"][str(n)]["H_norm"] for n in NS], "^-",
               color=fs.PAL["green"], label="cluster at rest (deposit)")
    xx = np.array([0.25, 1.0])
    ax[0].plot(xx, 2e-3 * xx, **fs.GUIDE)
    ax[0].plot(xx, 2e-3 * xx ** 2, **fs.GUIDE)
    for a_, yl in zip(ax, (r"interior norm of $M_i$", r"interior norm of $H - H_{\rm rest}$")):
        a_.set_xscale("log")
        a_.set_yscale("log")
        a_.set_xlabel(r"cell size $\Delta x/M$")
        a_.set_ylabel(yl)
        a_.set_xticks(dxs)
        a_.set_xticklabels([f"{d_:g}" for d_ in dxs])
    ax[0].legend(loc="lower right", fontsize=8)
    ax[1].legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_boost_static_convergence"))

    # slices through the plane nearest z = 0 at 128 cells, v = 0.3
    st = keep["st"]
    zs = np.unique(st.x[:, 2])
    z0 = zs[np.argmin(np.abs(zs))]
    sel = st.x[:, 2] == z0
    xs = np.unique(st.x[sel, 0])
    ys = np.unique(st.x[sel, 1])

    def img(f):
        order = np.lexsort((st.x[sel, 0], st.x[sel, 1]))
        return f[sel][order].reshape(len(ys), len(xs))
    fig, ax, cax = fs.slice_mosaic(1, 4, top_pad=0.42)
    panels = [(keep["none"].M[:, 0], r"$M_x$, $K_{ij} = 0$"),
              (keep["curv"].M[:, 0], r"$M_x$, boost table"),
              (keep["d_curv"], r"$H - H_{\rm rest}$, no correction"),
              (keep["d_corr"], r"$H - H_{\rm rest}$, corrected")]
    lims = [np.max(np.abs(img(panels[0][0]))), np.max(np.abs(img(panels[0][0]))),
            np.max(np.abs(img(panels[2][0]))), np.max(np.abs(img(panels[2][0])))]
    cax.remove()        # two colour scales: the range is written into each title
    for k, ((f, title), lim) in enumerate(zip(panels, lims)):
        a_ = ax[0, k]
        a_.imshow(img(f), origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]],
                  cmap="RdBu_r", vmin=-lim, vmax=lim, interpolation="none",
                  rasterized=True)
        a_.set_title(title + "\n" + rf"$\pm${lim:.1e}", fontsize=8)
        a_.add_patch(plt.Circle((0, 0), B.rs, fill=False, color="k", lw=0.6, ls=":"))
        fs.slice_ticks(a_, 16, show_y=(k == 0))
    fs.save(fig, os.path.join(a.out, "fig_boost_static_slices"))

    with open(os.path.join(a.out, "boost_static_check.json"), "w") as f:
        json.dump(out, f, indent=1)
    for k in ("static", "TB1", "TB2", "TB3", "TB5", "TB6"):
        print(k, json.dumps(out[k], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
