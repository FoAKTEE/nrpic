#!/usr/bin/env python3
"""Lead's check L16: when does the core of a collisional cluster run start to contract
relative to its collisionless control, and how much energy had the release operator's
defect injected by then (trigger or consequence)?

Histories only (rvlib.read_hist) of the card runs of threshold_scan (wave 2):
cc.nrpic.hst (time, alpha_probe = lapse at the centre, alpha_min, sum_m) and cc.coll.hst
(n_coll, dE_particles, sum_MW_particles). t_dep = first time alpha_probe(collisional) -
alpha_probe(control, same model, interpolated) < -0.01. Binding margin from the model JSON
(run C-sidm-20261115-120610-b4592be). Prediction L16 in tracks/C-sidm/JOURNAL.md.
Output: $NRPIC_RUN_DIR/rv_cc_onset.json, rv_cc_onset.{png,pdf}.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402
from rv_cc import RUNS, MODEL_OF, model  # noqa: E402

DROP = 0.01


def hist(name, kind):
    return rv.read_hist(os.path.join(rv.SCR, RUNS[name], name, f"cc.{kind}.hst"))


def main():
    out = rv.outdir()
    eb = {k: model(v)["Eb_over_M0"] for k, v in MODEL_OF.items()}
    margin = eb["cc1"] - eb["cc2"]
    res, ser = dict(margin_over_M0=margin, drop=DROP), {}
    for cc in ("cc1", "cc2"):
        hc = hist(f"{cc}_kninf", "nrpic")
        fc = np.isfinite(hc["alpha_probe"])
        for kn in ("kn10", "kn1"):
            n = f"{cc}_{kn}"
            h = hist(n, "nrpic")
            c = hist(n, "coll")
            t = h["time"]
            ok = np.isfinite(h["alpha_probe"]) & (h["n_excised"] == 0)
            ctrl = np.interp(t[ok], hc["time"][fc], hc["alpha_probe"][fc])
            d = h["alpha_probe"][ok] - ctrl
            idep = np.flatnonzero(d < -DROP)
            tdep = float(t[ok][idep[0]]) if idep.size else None
            s0 = float(c["sum_MW_particles"][0])
            acc = np.cumsum(c["dE_particles"]) * 1.0 / float(h["sum_m"][0])   # over M0
            inj = (lambda tt: float(np.interp(tt, c["time"], acc))) if tdep is not None else None
            i03 = np.flatnonzero(h["alpha_min"] < 0.3)
            t03 = float(t[i03[0]]) if i03.size else None
            ic = np.flatnonzero(acc >= margin)
            res[n] = dict(t_dep=tdep, t_alpha_min_0p3=t03,
                          injected_over_M0_at_t_dep=inj(tdep) if inj else None,
                          injected_over_margin_at_t_dep=inj(tdep) / margin if inj else None,
                          t_injected_reaches_margin=float(c["time"][ic[0]]) if ic.size else None,
                          sum_MW_particles0=s0,
                          coll_per_particle_at_t_dep=float(2 * c["n_coll"][c["time"] <= tdep].sum()
                                                           / h["np"][0]) if tdep else None)
            ser[n] = dict(t=t[ok], d=d, tc=c["time"], acc=acc)
            print(n, res[n], flush=True)
    json.dump(res, open(os.path.join(out, "rv_cc_onset.json"), "w"), indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(rv.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH * 0.95, 3.0))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.17, top=0.9, wspace=0.32)
    col = {"kn10": fs.PAL["blue"], "kn1": fs.PAL["red"]}
    for n, s in ser.items():
        ls = "-" if n.startswith("cc1") else "--"
        c = col[n.split("_")[1]]
        ax[0].plot(s["t"], s["d"], ls, color=c, lw=1.2, label=n)
        ax[1].plot(s["tc"], s["acc"] / margin, ls, color=c, lw=1.2, label=n)
        if res[n]["t_dep"] is not None:
            for a in ax:
                a.axvline(res[n]["t_dep"], color=c, lw=0.7, ls=ls, alpha=0.7)
    ax[0].axhline(-DROP, **fs.GUIDE)
    ax[0].set_ylim(-0.3, 0.05)
    ax[0].set_ylabel(r"$\alpha_c - \alpha_c^{\rm control}$")
    ax[0].legend(fontsize=7, frameon=False, loc="lower left")
    ax[1].axhline(1.0, **fs.GUIDE)
    ax[1].set_yscale("log")
    ax[1].set_ylim(1e-3, 30)
    ax[1].set_ylabel("injected energy / binding margin")
    for a in ax:
        a.set_xlabel(r"$t/M$")
        a.set_xlim(0, 230)
    fs.save(fig, os.path.join(out, "rv_cc_onset"))


if __name__ == "__main__":
    main()
