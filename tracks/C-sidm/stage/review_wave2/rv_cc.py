#!/usr/bin/env python3
"""Lead's recheck L14 of the first collisional cluster runs (threshold_scan, wave 2):
the accumulated energy defect of the core-v0.3 operator before the collapse, and what marks
the collapse time.

Histories only (rvlib.read_hist): cc.nrpic.hst (alpha_min, sum_m) and cc.coll.hst
(n_coll, dE_particles, sum_MW_particles; the release operator's coll_budget columns) of the
card runs C-20261115-171058-c26cfad, C-20261115-171059-4b70228, C-20261115-171059-35441e3.
Binding energies from the model JSON of run C-sidm-20261115-120610-b4592be (the same King
models at N = 1e4; the N = 1e5 files of C-20261115-165832-fccee3a sample them).
Prediction L14 in tracks/C-sidm/JOURNAL.md (2026-11-19T15:15Z).
Output: $NRPIC_RUN_DIR/rv_cc.json, rv_cc.{png,pdf}.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402

RUNS = {"cc1_kninf": "C-20261115-171058-c26cfad", "cc1_kn1": "C-20261115-171058-c26cfad",
        "cc1_kn10": "C-20261115-171059-4b70228", "cc2_kninf": "C-20261115-171059-4b70228",
        "cc2_kn10": "C-20261115-171059-35441e3", "cc2_kn1": "C-20261115-171059-35441e3"}
MODELS = os.path.join(rv.SCR, "C-sidm-20261115-120610-b4592be")
MODEL_OF = {"cc1": "king_y0p33403", "cc2": "king_y0p31400"}


def model(tag):
    return json.load(open(os.path.join(MODELS, f"{tag}_stratified_N10000_s1.json")))


def one(name):
    rd = os.path.join(rv.SCR, RUNS[name], name)
    h = rv.read_hist(os.path.join(rd, "cc.nrpic.hst"))
    t = h["time"]
    i03 = np.flatnonzero(h["alpha_min"] < 0.3)
    t03 = float(t[i03[0]]) if i03.size else None
    r = dict(t_alpha_min_below_0p3=t03, M0=float(h["sum_m"][0]), sum_mW0=float(h["sum_mW"][0]),
             N0=float(h["np"][0]))
    cp = os.path.join(rd, "cc.coll.hst")
    if not os.path.exists(cp):
        return r, None
    c = rv.read_hist(cp)
    tc = c["time"]
    s0 = float(c["sum_MW_particles"][0])
    acc = np.cumsum(c["dE_particles"]) / s0
    ncum = np.cumsum(c["n_coll"])
    pre = tc <= (t03 if t03 is not None else np.inf)
    early = tc <= 25.0
    r.update(acc_defect_rel_at_0p3=float(acc[pre][-1]),
             acc_defect_over_M0_at_0p3=float(acc[pre][-1] * s0 / r["M0"]),
             coll_per_particle_at_0p3=float(2 * ncum[pre][-1] / r["N0"]),
             per_coll_first25M=float(c["dE_particles"][early].sum() / c["n_coll"][early].sum() / s0),
             per_coll_before_0p3=float(c["dE_particles"][pre].sum() / c["n_coll"][pre].sum() / s0),
             collisions_before_0p3=float(ncum[pre][-1]))
    # standard error of the early per-collision mean from 5 M blocks of the record
    blocks = []
    for a in np.arange(0.0, 25.0, 5.0):
        sel = (tc > a) & (tc <= a + 5.0)
        if c["n_coll"][sel].sum() > 0:
            blocks.append(c["dE_particles"][sel].sum() / c["n_coll"][sel].sum() / s0)
    r["per_coll_first25M_block_se"] = float(np.std(blocks, ddof=1) / np.sqrt(len(blocks)))
    series = dict(t=tc[pre].tolist(), acc_over_M0=(acc[pre] * s0 / r["M0"]).tolist(),
                  coll_per_particle=(2 * ncum[pre] / r["N0"]).tolist())
    return r, series


def figure(res, ser, margin, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(rv.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH * 0.95, 3.0))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.17, top=0.9, wspace=0.3)
    col = {"kn10": fs.PAL["blue"], "kn1": fs.PAL["red"]}
    for n, s in ser.items():
        if s is None:
            continue
        ls = "-" if n.startswith("cc1") else "--"
        c = col[n.split("_")[1]]
        ax[0].plot(s["t"], s["acc_over_M0"], ls, color=c, lw=1.3, label=n)
        ax[1].plot(s["t"], s["coll_per_particle"], ls, color=c, lw=1.3, label=n)
        for a in ax:
            a.axvline(res[n]["t_alpha_min_below_0p3"], color=c, lw=0.6, ls=ls, alpha=0.6)
    ax[0].axhline(margin, **fs.GUIDE)
    ax[0].text(5, margin * 1.15, r"$E_b$(threshold) $-$ $E_b$($y_0=0.314$)", fontsize=7)
    ax[0].set_yscale("log")
    ax[0].set_ylim(1e-7, 1e-2)
    ax[0].set_ylabel(r"accumulated $\Delta\Sigma MW_p\,/\,M_0$ (cell mode)")
    ax[1].set_ylabel("collisions per particle")
    ax[1].legend(fontsize=7, frameon=False)
    for a in ax:
        a.set_xlabel(r"$t/M$ (to $\alpha_{\min}<0.3$)")
    fs.save(fig, os.path.join(out, "rv_cc"))


def main():
    out = rv.outdir()
    res, ser = {}, {}
    for n in RUNS:
        res[n], ser[n] = one(n)
    eb = {k: model(v)["Eb_over_M0"] for k, v in MODEL_OF.items()}
    margin = eb["cc1"] - eb["cc2"]
    res["_binding"] = dict(Eb_over_M0=eb, margin_over_M0=margin)
    k1 = res["cc1_kn1"], res["cc2_kn1"]
    k10 = res["cc1_kn10"], res["cc2_kn10"]
    res["_ratios_kn1_over_kn10"] = dict(
        acc_defect=[k1[i]["acc_defect_rel_at_0p3"] / k10[i]["acc_defect_rel_at_0p3"] for i in (0, 1)],
        coll_per_particle=[k1[i]["coll_per_particle_at_0p3"] / k10[i]["coll_per_particle_at_0p3"]
                           for i in (0, 1)],
        time=[k1[i]["t_alpha_min_below_0p3"] / k10[i]["t_alpha_min_below_0p3"] for i in (0, 1)])
    res["_kn10_injected_over_margin"] = [k10[i]["acc_defect_over_M0_at_0p3"] / margin for i in (0, 1)]
    figure(res, ser, margin, out)
    json.dump(res, open(os.path.join(out, "rv_cc.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
