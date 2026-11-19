#!/usr/bin/env python3
"""Where the Hamiltonian residual left by the correction of psi sits (test TB3, the
ratio |D_H(corr)|/|D_H(curv)| of 0.08 to 0.10 that does not fall with the cell size;
tracks/core/JOURNAL-clump2.md). Reads the dumps of the TB runs, writes
tb_residual_diag.json and fig_tb_residual_profiles.{pdf,png} into --out:

- for each v and cell count: D_H = H(case) - H(rest), its projection on H(rest) and the
  norm of the rest, and the norms inside and outside a shell of half-width 1 M about the
  surface rbar_s of the cluster;
- shell averages of D_H(curv), D_H(corr) and H(rest) (monopole, and the P_2 part about
  the direction of motion), against the continuum second-order residual of the Python
  reference (predict_boost.py) for D_H(curv).

    tb_residual_diag.py --run RUN_ID/tb [--out DIR]
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
sys.path.insert(0, HERE)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import boosted_cluster as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402
from boost_static_check import Case, RCUT, NS, VS  # noqa: E402


def shells(r, mu, f, w, edges):
    """weighted shell averages of f and of f P_2(mu) (times 5: the l = 2 coefficient)"""
    k = np.digitize(r, edges) - 1
    n = len(edges) - 1
    p2 = 0.5 * (3.0 * mu * mu - 1.0)
    a0, a2 = np.zeros(n), np.zeros(n)
    for i in range(n):
        s = (k == i)
        if np.any(s):
            ws = w[s]
            a0[i] = np.sum(ws * f[s]) / np.sum(ws)
            a2[i] = 5.0 * np.sum(ws * f[s] * p2[s]) / np.sum(ws)
    return a0, a2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--n", default=",".join(str(n) for n in NS))
    ap.add_argument("--v", default=",".join(VS))
    a = ap.parse_args()
    ns = [int(x) for x in a.n.split(",")]
    vs = a.v.split(",")
    top = os.path.join(SCRATCH, a.run)
    os.makedirs(a.out, exist_ok=True)
    md = stc.STModel(0.819)
    B = bc.BoostedST(md)
    rs = float(B.rs)
    out = dict(run=a.run, rbar_s=rs, cases={})
    prof = {}
    for n in ns:
        st = Case(top, f"q0_n{n}")
        w = st.psi ** 6 * st.dV
        ins = st.inside
        surf = np.abs(st.r - rs) < 1.0
        mu = np.where(st.r > 0, st.x[:, 0] / np.maximum(st.r, 1e-30), 0.0)
        for v in vs:
            key = f"v={v},n={n}"
            o = {}
            for c in ("curv", "corr"):
                cs = Case(top, f"q{v}_n{n}_{c}")
                d = cs.H - st.H
                hh = float(np.sum((w * st.H * st.H)[ins]))
                coef = float(np.sum((w * d * st.H)[ins]) / hh)
                rest = d - coef * st.H
                o[c] = dict(
                    norm=math.sqrt(float(np.sum((w * d * d)[ins]))),
                    proj_on_rest_H=coef,
                    norm_after_removing_rest_H=math.sqrt(float(np.sum((w * rest * rest)[ins]))),
                    norm_surface_shell=math.sqrt(float(np.sum((w * d * d)[ins & surf]))),
                    norm_off_surface=math.sqrt(float(np.sum((w * d * d)[ins & ~surf]))))
                if n == 128 or (n == 64 and v == "0.3"):
                    edges = np.arange(0.0, RCUT + 1e-9, 0.25 if n == 128 else 0.5)
                    a0, a2 = shells(st.r[ins], mu[ins], d[ins], w[ins], edges)
                    prof[(v, n, c)] = (0.5 * (edges[1:] + edges[:-1]), a0, a2)
            o["rest_H_norm"] = math.sqrt(float(np.sum((w * st.H * st.H)[ins])))
            out["cases"][key] = o
            if n == 128 and v == "0.3":
                edges = np.arange(0.0, RCUT + 1e-9, 0.25)
                a0, a2 = shells(st.r[ins], mu[ins], st.H[ins], w[ins], edges)
                prof[("rest", n)] = (0.5 * (edges[1:] + edges[:-1]), a0, a2)

    if ("0.3", 128, "corr") not in prof or ("0.3", 64, "corr") not in prof:
        with open(os.path.join(a.out, "tb_residual_diag.json"), "w") as f:
            json.dump(out, f, indent=1)
        print(json.dumps(out, indent=1))
        return 0
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.15, top=0.95, wspace=0.3)
    rr, c0, c2 = prof[("0.3", 128, "curv")]
    _, k0, k2 = prof[("0.3", 128, "corr")]
    _, h0, h2 = prof[("rest", 128)]
    _, k64, _ = prof[("0.3", 64, "corr")]
    rr64 = prof[("0.3", 64, "corr")][0]
    ax[0].plot(rr, c0, color=fs.PAL["blue"], label="no correction")
    ax[0].plot(rr, k0, color=fs.PAL["red"], label=r"corrected, $\Delta x = M/4$")
    ax[0].plot(rr64, k64, color=fs.PAL["red"], ls="--", label=r"corrected, $\Delta x = M/2$")
    ax[0].plot(rr, 0.1 * h0, color=fs.PAL["green"], ls=":", label=r"$0.1\,H_{\rm rest}$")
    ax[1].plot(rr, c2, color=fs.PAL["blue"], label="no correction")
    ax[1].plot(rr, k2, color=fs.PAL["red"], label="corrected")
    ax[1].plot(rr, 0.1 * h2, color=fs.PAL["green"], ls=":", label=r"$0.1\,H_{\rm rest}$")
    for a_, t in zip(ax, ("monopole of $H - H_{\\rm rest}$", "$P_2$ part of $H - H_{\\rm rest}$")):
        a_.axvline(rs, **fs.THIN, ls=":")
        a_.axhline(0.0, **fs.THIN)
        a_.set_xlabel(r"$r/M$")
        a_.set_ylabel(t)
    ax[0].legend(loc="best", fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig_tb_residual_profiles"))
    with open(os.path.join(a.out, "tb_residual_diag.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
