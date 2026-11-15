"""C2: dependence of the separation fraction on the release radius r0 (2404 appendix C).

    <venv>/bin/python -I analysis_c2.py <C2 run dir> <outdir>

Reads c2_r{20,50,70}.npz (2404 initial data, both laws) and c2g_r{20,50,70}.npz (HRNA with the
Gamma-corrected initial binary) written by the C2 run; beta = 4.7.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

R0 = (20, 50, 70)


def sf(path):
    d = np.load(path)
    meta = json.loads(str(d["meta"]))
    out = {}
    for i, law in enumerate(meta["laws"]):
        for j, s in enumerate(meta["senses"]):
            out[f"{'pro' if s > 0 else 'retro'}_{law}"] = float((d["separated"][i, j, 0] > 0).mean())
    return out


def main(rundir, outdir):
    os.makedirs(outdir, exist_ok=True)
    res = {"standard": {}, "gamma_ic": {}}
    for r in R0:
        p = os.path.join(rundir, f"c2_r{r}.npz")
        if os.path.exists(p):
            res["standard"][r] = sf(p)
        p = os.path.join(rundir, f"c2g_r{r}.npz")
        if os.path.exists(p):
            res["gamma_ic"][r] = sf(p)
    var = {}
    for kind, dd in res.items():
        if len(dd) < 2:
            continue
        keys = next(iter(dd.values())).keys()
        for k in keys:
            vals = np.array([dd[r][k] for r in dd])
            var[f"{kind}_{k}_rel_spread"] = float((vals.max() - vals.min()) / max(vals.mean(), 1e-12))
            var[f"{kind}_{k}_values"] = vals.tolist()
    res["spread"] = var
    with open(os.path.join(outdir, "c2_summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 2.9))
    ax = fig.add_axes([0.18, 0.16, 0.78, 0.8])
    for kind, mk in (("standard", "o-"), ("gamma_ic", "s--")):
        dd = res[kind]
        if not dd:
            continue
        rs = sorted(dd)
        for k, c in (("retro_hrna", fs.PAL["red"]), ("retro_newton", fs.PAL["blue"])):
            if k in dd[rs[0]]:
                ax.plot(rs, [dd[r][k] for r in rs], mk, color=c, ms=4,
                        label=f"{k.replace('_', ' ')}{' (Gamma IC)' if kind == 'gamma_ic' else ''}")
    ax.set_xlabel(r"$r_0/r_t$")
    ax.set_ylabel(r"s.f. at $\beta=4.7$")
    ax.legend(loc="best", fontsize=7)
    fs.save(fig, os.path.join(outdir, "c2_r0"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
