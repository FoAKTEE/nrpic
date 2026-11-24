#!/usr/bin/env python3
"""Reader of the conductivity series against cell size and step (heat_C1, heat_C2 of the
longruns queue; predictions H.1-H.4 in tracks/C-sidm/JOURNAL.md entry 2026-11-21T20:25Z).

    python3 heat_series.py --out DIR --noise RUN_OR_T7JSON --group T7_th0.003_e0.2 BATCH [BATCH ...]

BATCH: a card run whose case directories TC_th<theta>_kl<kl>_e<eps>_s<seed>_dt<dt>_p<p>_dx<dx>
were reduced (`heat/scripts/run_mode.py reduce`). Each case is fitted with the heat package's
entropy-mode fit (`an_mode.fit_case`, f = kappa/kappa_1). The noise of one case is
sd_f = sqrt(s2/N), s2 the N-weighted unit variance of the theta = 0.003, eps = 0.2 seeds at the
same k lambda (`an_compare.seeds_of` and `weighted` on the T7.json given by --noise).
Quantities (seed means where two seeds exist):
  H.1  f(dx = lambda/2) / f(lambda/8) - 1 at k lambda 0.2
  H.2  f0 of f = f0 + c (dx/lambda)^2 through dx = lambda/8, /4, /2 (least squares, equal sd)
  H.3  f(dt 0.05) / f(dt 0.1) - 1 at dx = lambda/8, and z = change / (sd of a change)
  H.4  c at k lambda 0.1 against c at 0.2: z = (c01 - c02) / sqrt(se01^2 + se02^2)
Writes DIR/heat_series.json and DIR/fig_heat_series.png.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TR, "heat", "scripts"))
import an_mode as AM  # noqa: E402
import an_compare as AC  # noqa: E402

PAT = re.compile(r"TC_th(?P<th>[0-9.]+)_kl(?P<kl>[0-9.]+)_e(?P<e>[0-9.]+)_s(?P<s>\d+)_dt(?P<dt>[0-9.]+)"
                 r"_p(?P<p>[0-9.]+)_dx(?P<dx>[0-9.]+)$")
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"


def fitline(dx, f, sd):
    x = np.asarray(dx, float) ** 2
    A = np.vstack([np.ones_like(x), x]).T
    p, *_ = np.linalg.lstsq(A, np.asarray(f, float), rcond=None)
    C = np.linalg.inv(A.T @ A) * sd ** 2
    res = np.asarray(f) - A @ p
    return dict(f0=float(p[0]), f0_se=float(np.sqrt(C[0, 0])), c=float(p[1]), c_se=float(np.sqrt(C[1, 1])),
                chi2=float(np.sum(res ** 2) / sd ** 2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--noise", required=True)
    ap.add_argument("--group", default="T7_th0.003_e0.2")
    ap.add_argument("batches", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    TN = json.load(open(AC.resolve(a.noise, "T7.json")))
    _, rowsN = AC.seeds_of(TN, a.group)
    s2 = {}
    for kl, ss in rowsN:
        s2[round(kl, 6)] = AC.weighted([s["f"] for s in ss], [s["N"] for s in ss])[2]
    rows = []
    for b in a.batches:
        d = b if os.path.isdir(b) else os.path.join(SCR, b)
        for p in sorted(glob.glob(os.path.join(d, "TC_*", "reduced.npz"))):
            cd = os.path.dirname(p)
            m = PAT.match(os.path.basename(cd))
            c = AM.load_case(cd)
            f = AM.fit_case(c)
            kl = float(m["kl"])
            rows.append(dict(name=os.path.basename(cd), batch=os.path.basename(d), kl=kl, seed=int(m["s"]),
                             dt=float(m["dt"]), dx=float(m["dx"]), n=int(c["n"]), f_S=float(f["f_S"]),
                             f_N=float(f["f_N"]), sd=float(np.sqrt(s2[round(kl, 6)] / c["n"]))))
    res = dict(noise=dict(source=a.noise, group=a.group, s2={str(k): v for k, v in s2.items()}), rows=rows)

    def sel(kl, dt, dx, seed=None):
        return [r for r in rows if abs(r["kl"] - kl) < 1e-9 and abs(r["dt"] - dt) < 1e-9
                and abs(r["dx"] - dx) < 1e-9 and (seed is None or r["seed"] == seed)]

    def mean_f(kl, dt, dx):
        rs = sel(kl, dt, dx)
        return (float(np.mean([r["f_S"] for r in rs])), float(np.sqrt(np.sum([r["sd"] ** 2 for r in rs])) / len(rs)),
                len(rs)) if rs else (None, None, 0)

    out = {}
    for kl in sorted({r["kl"] for r in rows}):
        dxs = sorted({r["dx"] for r in rows if abs(r["kl"] - kl) < 1e-9 and abs(r["dt"] - 0.1) < 1e-9})
        pts = [(dx,) + mean_f(kl, 0.1, dx) for dx in dxs]
        sd = float(np.mean([p[2] for p in pts]))
        fit = fitline([p[0] for p in pts], [p[1] for p in pts], sd) if len(pts) >= 3 else None
        per_seed = {}
        for s in sorted({r["seed"] for r in rows if abs(r["kl"] - kl) < 1e-9}):
            q = [(dx, sel(kl, 0.1, dx, s)) for dx in dxs]
            if all(v for _, v in q) and len(q) >= 3:
                per_seed[s] = fitline([dx for dx, _ in q], [v[0]["f_S"] for _, v in q], v[0]["sd"])
        o = dict(points=[dict(dx=p[0], f=p[1], sd=p[2], n_seeds=p[3]) for p in pts], fit=fit, fit_per_seed=per_seed)
        f2, f8 = mean_f(kl, 0.1, 0.5), mean_f(kl, 0.1, 0.125)
        if f2[0] and f8[0]:
            o["H1_ratio_minus_1"] = f2[0] / f8[0] - 1.0
            o["H1_sd"] = float(np.hypot(f2[1], f8[1]) / f8[0])
        a05, a10 = mean_f(kl, 0.05, 0.125), mean_f(kl, 0.1, 0.125)
        if a05[0] and a10[0]:
            ch = a05[0] / a10[0] - 1.0
            # the two dt cases of one seed share the particle file: the sd of a change is the
            # sd of the difference of two independent fits (an upper bound if correlated)
            sdc = float(np.hypot(a05[1], a10[1]) / a10[0])
            pair = [sel(kl, 0.05, 0.125, s)[0]["f_S"] / sel(kl, 0.1, 0.125, s)[0]["f_S"] - 1.0
                    for s in sorted({r["seed"] for r in sel(kl, 0.05, 0.125)})]
            o["H3_change"] = ch
            o["H3_sd_change"] = sdc
            o["H3_z"] = ch / sdc
            o["H3_per_seed"] = pair
        out[str(kl)] = o
    if "0.1" in out and "0.2" in out and out["0.1"]["fit"] and out["0.2"]["fit"]:
        f1, f2 = out["0.1"]["fit"], out["0.2"]["fit"]
        out["H4_z"] = (f1["c"] - f2["c"]) / float(np.hypot(f1["c_se"], f2["c_se"]))
    res["series"] = out
    with open(os.path.join(a.out, "heat_series.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    for r in rows:
        print("%-46s f_S %.4f sd %.4f" % (r["name"], r["f_S"], r["sd"]))
    print(json.dumps(out, indent=1, default=float))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
    cols = fs.series_colors(4)
    for j, kl in enumerate(sorted({r["kl"] for r in rows})):
        for i, s in enumerate(sorted({r["seed"] for r in rows if abs(r["kl"] - kl) < 1e-9})):
            q = sorted([r for r in rows if abs(r["kl"] - kl) < 1e-9 and r["seed"] == s and abs(r["dt"] - 0.1) < 1e-9],
                       key=lambda r: r["dx"])
            axs[0].errorbar([r["dx"] ** 2 for r in q], [r["f_S"] for r in q], yerr=[r["sd"] for r in q],
                            fmt="o", ms=3.5, capsize=2, color=cols[2 * j + i],
                            label=f"k lambda {kl:g}, seed {s}")
            dtq = [r for r in rows if abs(r["kl"] - kl) < 1e-9 and r["seed"] == s and abs(r["dt"] - 0.05) < 1e-9]
            if dtq:
                axs[1].errorbar([0.05], [dtq[0]["f_S"]], yerr=[dtq[0]["sd"]], fmt="s", color=cols[2 * j + i])
                b = [r for r in q if abs(r["dx"] - dtq[0]["dx"]) < 1e-9]
                if b:
                    axs[1].errorbar([0.1], [b[0]["f_S"]], yerr=[b[0]["sd"]], fmt="o", color=cols[2 * j + i],
                                    label=f"k lambda {kl:g}, seed {s}, dx lambda/8")
        fit = out[str(kl)]["fit"]
        if fit:
            x = np.linspace(0, 0.26, 50)
            axs[0].plot(x, fit["f0"] + fit["c"] * x, color=cols[2 * j], lw=0.8, ls="--")
    axs[0].set_xlabel(r"$(\Delta x/\lambda)^2$")
    axs[0].set_ylabel(r"$f=\kappa/\kappa_1$")
    axs[0].legend(fontsize=6)
    axs[1].set_xlabel(r"$\Delta t/t_{\rm coll}$")
    axs[1].set_xlim(0.03, 0.12)
    axs[1].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_heat_series.png"), dpi=150)
    print("wrote", os.path.join(a.out, "fig_heat_series.png"))


if __name__ == "__main__":
    main()
