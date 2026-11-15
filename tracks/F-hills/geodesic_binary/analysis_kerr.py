"""Coordinate dependence of HRNA (S3) and equatorial Kerr (S4) against the Schwarzschild runs (S1).

    <venv>/bin/python -I analysis_kerr.py <s1.npz> <s3.npz> <s4.npz or -> <outdir>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

C_KMS = 299792.458


def load(path):
    d = np.load(path)
    return d, json.loads(str(d["meta"]))


def at(d, meta, law, sense, beta):
    i, j = meta["laws"].index(law), meta["senses"].index(sense)
    b = int(np.argmin(np.abs(d["betas"] - beta)))
    if abs(d["betas"][b] - beta) > 1e-6:
        return None
    sep = d["separated"][i, j, b] > 0
    coll = d["a_min"][i, j, b] < 1e-4                 # point-mass near-collisions: excluded from speeds
    cap = (d["plunged"][i, j, b] > 0) & ~coll
    clean = sep & ~cap & ~coll
    v = d["vinf"][i, j, b] * C_KMS
    return dict(sf=float(sep.mean()), v_mean=float(v[clean].mean()) if clean.any() else None,
                cap=float(cap.mean()), sep=sep)


def main(s1, s3, s4, outdir):
    os.makedirs(outdir, exist_ok=True)
    d1, m1 = load(s1)
    d3, m3 = load(s3)
    res = {"S3": {}, "S4": {}}
    for sense, sn in ((1, "pro"), (-1, "retro")):
        for beta in d3["betas"]:
            A = at(d1, m1, "hrna", sense, beta)
            B = at(d3, m3, "hrna", sense, beta)
            N = at(d1, m1, "newton", sense, beta)
            res["S3"][f"{sn}_beta{beta:g}"] = dict(
                sf_sch=A["sf"], sf_ks=B["sf"], dsf=B["sf"] - A["sf"], sf_newton=N["sf"],
                vmean_sch=A["v_mean"], vmean_ks=B["v_mean"],
                dv_rel=(B["v_mean"] / A["v_mean"] - 1 if A["v_mean"] and B["v_mean"] else None),
                phases_with_different_outcome=int((A["sep"] != B["sep"]).sum()))
    if s4 != "-":
        d4, m4 = load(s4)
        spins = m4.get("spins")
        for sense, sn in ((1, "pro"), (-1, "retro")):
            for beta in d4["betas"]:
                row = {}
                for k, sp in enumerate(spins):
                    i, j = 0, m4["senses"].index(sense)
                    b = int(np.argmin(np.abs(d4["betas"] - beta)))
                    sep = d4["separated"][k, j, b] > 0
                    coll = d4["a_min"][k, j, b] < 1e-4
                    cap = (d4["plunged"][k, j, b] > 0) & ~coll
                    clean = sep & ~cap & ~coll
                    v = d4["vinf"][k, j, b] * C_KMS
                    row[f"sf_a{sp:+g}"] = float(sep.mean())
                    row[f"cap_a{sp:+g}"] = float(cap.mean())
                    row[f"vmean_a{sp:+g}"] = float(v[clean].mean()) if clean.any() else None
                B = at(d3, m3, "hrna", sense, beta)
                if B is not None:
                    row["sf_a+0"] = B["sf"]
                    row["vmean_a+0"] = B["v_mean"]
                N = at(d1, m1, "newton", sense, beta)
                if N is not None:
                    row["sf_newton"] = N["sf"]
                    row["vmean_newton"] = N["v_mean"]
                res["S4"][f"{sn}_beta{beta:g}"] = row
    if s4 != "-":
        res["S4_runs_step_underflow"] = int((d4["status"] == 4).sum())
        res["S4_runs_both_captured"] = int((d4["status"] == 5).sum())
        res["S4_runs_a_min_below_1e-4_a0"] = int((d4["a_min"] < 1e-4).sum())
        res["S4_runs_total"] = int(d4["status"].size)
    res["S3_runs_step_underflow"] = int((d3["status"] == 4).sum())
    with open(os.path.join(outdir, "kerr_summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    axs = [fs.inch_axes(fig, 0.7, 0.5, 3.2, 2.3), fs.inch_axes(fig, 4.6, 0.5, 3.2, 2.3)]
    for ax, sn in zip(axs, ("pro", "retro")):
        sense = 1 if sn == "pro" else -1
        i, j = m1["laws"].index("hrna"), m1["senses"].index(sense)
        ax.plot(d1["betas"], d1["separated"][i, j].mean(-1), color=fs.PAL["red"], label="HRNA, Schwarzschild coords (S1)")
        i, j = m1["laws"].index("newton"), m1["senses"].index(sense)
        ax.plot(d1["betas"], d1["separated"][i, j].mean(-1), color=fs.PAL["blue"], label="Newton (S1)")
        j3 = m3["senses"].index(sense)
        ax.plot(d3["betas"], d3["separated"][0, j3].mean(-1), "s", ms=5, mfc="none", color=fs.PAL["red"],
                label="HRNA, Kerr-Schild $a=0$ (S3)")
        if s4 != "-":
            for k, (sp, c) in enumerate(zip(spins, (fs.PAL["green"], fs.PAL["orange"]))):
                j4 = m4["senses"].index(sense)
                ax.plot(d4["betas"], d4["separated"][k, j4].mean(-1), "o-", ms=4, lw=1.0, color=c,
                        label=f"HRNA, Kerr $a={sp:+g}$ (S4)")
        ax.set_xlabel(r"$\beta$")
        ax.set_ylabel(f"separation fraction ({'prograde' if sn == 'pro' else 'retrograde'})")
        ax.set_xlim(0, max(10, d4["betas"].max() + 0.5 if s4 != "-" else 10))
    axs[1].legend(loc="lower right", fontsize=7)
    fs.save(fig, os.path.join(outdir, "kerr_sepfrac"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
