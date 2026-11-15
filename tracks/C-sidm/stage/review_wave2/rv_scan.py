#!/usr/bin/env python3
"""Lead's recheck L10 of the threshold_scan card runs (wave 2), from the histories only.

Runs C-20261115-171058-c26cfad (cc1_kninf, cc1_kn1), C-20261115-171059-4b70228 (cc1_kn10,
cc2_kninf), C-20261115-171059-35441e3 (cc2_kn10, cc2_kn1). Columns by the header names of
cc.nrpic.hst and cc.coll.hst (rvlib.read_hist). Output: $NRPIC_RUN_DIR/rv_scan.json,
rv_scan.{png,pdf}.
"""
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402

RUNS = {"cc1_kninf": "C-20261115-171058-c26cfad", "cc1_kn1": "C-20261115-171058-c26cfad",
        "cc1_kn10": "C-20261115-171059-4b70228", "cc2_kninf": "C-20261115-171059-4b70228",
        "cc2_kn10": "C-20261115-171059-35441e3", "cc2_kn1": "C-20261115-171059-35441e3"}


def first(t, mask):
    i = np.flatnonzero(mask)
    return float(t[i[0]]) if i.size else None


def one(name):
    rd = os.path.join(rv.SCR, RUNS[name], name)
    h = rv.read_hist(os.path.join(rd, "cc.nrpic.hst"))
    t = h["time"]
    m0 = h["sum_m"][0]
    N0 = h["np"][0]
    fin = np.isfinite(h["alpha_probe"]) & np.isfinite(h["sum_mW"])
    budget = h["sum_m"] + h["m_excised"] + h["m_escaped"]
    r = dict(N0=float(N0), t_end=float(t[-1]),
             t_alpha_min_below_0p3=first(t, h["alpha_min"] < 0.3),
             t_first_excision=first(t, h["n_excised"] > 0),
             t_first_nonfinite=first(t, ~fin),
             np_end=float(h["np"][-1]),
             budget_max_rel=float(np.max(np.abs(budget / m0 - 1))),
             sum_m_bit_identical_before_excision=bool(np.all(
                 h["sum_m"][h["n_excised"] == 0] == m0)),
             m_escaped_max=float(h["m_escaped"].max()),
             alpha_probe_0=float(h["alpha_probe"][0]))
    te = r["t_first_excision"]
    if te is not None:
        for dtau in (20.0, 50.0):
            i = np.searchsorted(t, te + dtau)
            r[f"excised_frac_{int(dtau)}M"] = float(h["m_excised"][min(i, t.size - 1)] / m0)
    pre = fin & (h["n_excised"] == 0)
    ap = h["alpha_probe"][pre]
    gam = h["sum_mW"][pre] / h["sum_m"][pre]
    r["alpha_probe_max_rise"] = float(ap.max() - ap[0])
    r["t_alpha_probe_max"] = float(t[pre][np.argmax(ap)])
    r["mean_W_max_change"] = float(np.max(np.abs(gam - gam[0])))
    cp = os.path.join(rd, "cc.coll.hst")
    if os.path.exists(cp):
        c = rv.read_hist(cp)
        tc = c["time"]
        t03 = r["t_alpha_min_below_0p3"] or 1e99
        r["collisions_total"] = float(c["n_coll"].sum())
        r["coll_per_particle_before_0p3"] = float(2 * c["n_coll"][tc <= t03].sum() / N0)
        r["z_counts"] = float((c["n_coll"].sum() - c["sum_P"].sum()) / math.sqrt(c["sum_P"].sum()))
        r["first_sum_P"] = float(c["sum_P"][0])
        r["max_P"] = float(c["max_P"].max())
        r["n_trunc"] = float(c["n_trunc"].sum())
    log = open(os.path.join(rd, "athena.log")).read()
    mm = re.findall(r"# exit=(\d+)", log)
    r["exit"] = int(mm[-1]) if mm else None
    r["_series"] = dict(t=t[fin].tolist(), alpha_min=h["alpha_min"][fin].tolist(),
                        alpha_probe=h["alpha_probe"][fin].tolist(),
                        excised=(h["m_excised"][fin] / m0).tolist())
    return r


def figure(res, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(rv.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.1, 2.9))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.9, wspace=0.33)
    col = {"kninf": "k", "kn10": fs.PAL["blue"], "kn1": fs.PAL["red"]}
    for n, r in res.items():
        s = r["_series"]
        ls = "-" if n.startswith("cc1") else "--"
        c = col[n.split("_")[1]]
        ax[0].plot(s["t"], s["alpha_min"], ls, color=c, lw=1.2, label=n)
        ax[2].plot(s["t"], s["excised"], ls, color=c, lw=1.2)
        if "kninf" in n:
            ax[1].plot(s["t"], np.array(s["alpha_probe"]) - s["alpha_probe"][0], ls, color=c,
                       lw=1.2, label=n)
    ax[0].axhline(0.3, **fs.GUIDE)
    ax[0].set_ylabel(r"$\alpha_{\min}$")
    ax[0].legend(fontsize=6, frameon=False, ncol=2, loc="lower left")
    ax[1].set_ylabel(r"$\alpha_c(t)-\alpha_c(0)$ (controls)")
    ax[1].legend(fontsize=7, frameon=False)
    ax[2].set_ylabel("excised rest-mass fraction")
    for a in ax:
        a.set_xlabel("$t/M$")
    fs.save(fig, os.path.join(out, "rv_scan"))


def main():
    out = rv.outdir()
    res = {n: one(n) for n in RUNS}
    figure(res, out)
    for r in res.values():
        r.pop("_series")
    json.dump(res, open(os.path.join(out, "rv_scan.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
