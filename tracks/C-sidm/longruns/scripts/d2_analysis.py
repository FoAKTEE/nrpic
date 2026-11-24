#!/usr/bin/env python3
"""Reader of decisive D2 (predictions D2.1-D2.3 and the control, tracks/C-sidm/JOURNAL.md
entry 2026-11-21T20:25Z): CC2 (y0 = 0.314) on the M/8 mesh at Kn = 10, particle mode,
coll_cell_factor f = 1, 2, 4 (collision cells M/8, M/4, M/2), against the collisionless
control of the same particle file and executable.

    python3 d2_analysis.py --out DIR LABEL=RUN [LABEL=RUN ...]

LABEL is ctrl, f1s1, f2s1, f4s1, f2s2 (f<factor>s<collision seed>); RUN a run id or a run
directory whose cc.nrpic.hst (and cc.coll.hst) sit at its top (chain runs). The per-run
quantities are those of decisive/scripts/analyze_decisive.py (its `analyse`, imported), on
histories read so that a restart that rewrote times already written replaces them (later
segment wins: a chain continued in place after a preemption appends to the same file).
Added here: collisions per particle per M over 0-100 M and over 0-min(t_c, 200) M; the
control's alpha_c - alpha_c(0) mean over 280-300 M; the reference of the M/4 mesh
(f = 1 there: cells M/4): t_c = 206.64 M, 2.89 collisions per particle (decisive README).
Writes DIR/d2.json and DIR/fig_d2.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.normpath(os.path.join(HERE, "..", ".."))
WT = os.path.normpath(os.path.join(TR, "..", ".."))
sys.path.insert(0, os.path.join(TR, "decisive", "scripts"))
sys.path.insert(0, os.path.join(WT, "python"))
import analyze_decisive as AD  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
REF_M4 = dict(t_c=206.64, coll_per_particle=2.89)
N_PART = 100000

_read = AD.C.read_hst


def read_dedup(path):
    """read_hst, then drop rows whose time is not after the last kept one of a later segment."""
    h = _read(path)
    t = np.asarray(h["time"], float)
    keep = np.zeros(len(t), bool)
    last = np.inf
    for i in range(len(t) - 1, -1, -1):          # walk back: the later segment wins
        if t[i] < last - 1e-12:
            keep[i] = True
            last = t[i]
    return {k: np.asarray(v)[keep] for k, v in h.items()}


AD.C.read_hst = read_dedup


def rate(path, t0, t1):
    if not os.path.exists(path):
        return None
    c = read_dedup(path)
    k = (c["time"] > t0) & (c["time"] <= t1)
    if not np.any(k):
        return None
    span = float(c["time"][k][-1] - t0)
    return 2.0 * float(c["n_coll"][k].sum()) / N_PART / span if span > 0 else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dirs = {}
    for s in a.runs:
        lab, r = s.split("=", 1)
        dirs[lab] = r if os.path.isdir(r) else os.path.join(SCR, r)
    ctrl = read_dedup(os.path.join(dirs["ctrl"], "cc.nrpic.hst"))
    res = dict(reference_M4=REF_M4, runs={})
    ser = {}
    for lab, d in dirs.items():
        out = AD.analyse(lab, d, None if lab == "ctrl" else ctrl)
        h = read_dedup(os.path.join(d, "cc.nrpic.hst"))
        out["alpha_min_min"] = float(np.nanmin(h["alpha_min"]))
        out["t_alpha_min_min"] = float(h["time"][int(np.nanargmin(h["alpha_min"]))])
        ac = h["alpha_probe"] - h["alpha_probe"][0]
        k = (h["time"] >= 280.0) & (h["time"] <= 300.0)
        out["alpha_c_change_280_300"] = float(np.mean(ac[k])) if np.any(k) else None
        k = (h["time"] >= 100.0) & (h["time"] <= 110.0)
        out["alpha_c_change_100_110"] = float(np.mean(ac[k])) if np.any(k) else None
        ch = os.path.join(d, "cc.coll.hst")
        tc = out.get("t_c_interp") or out.get("t_c")
        out["coll_rate_0_100"] = rate(ch, 0.0, 100.0)
        out["coll_rate_0_tc_or_200"] = rate(ch, 0.0, min(tc, 200.0) if tc else 200.0)
        res["runs"][lab] = {k: v for k, v in out.items() if not isinstance(v, np.ndarray)}
        ser[lab] = h
    # judgements written before the runs (JOURNAL 2026-11-21T20:25Z); numbers only, the verdict
    # goes into the journal
    R = res["runs"]
    tcs = {lab: (R[lab].get("t_c_interp") if R[lab].get("t_c_interp") is not None else None) for lab in R}
    rates = {lab: R[lab].get("coll_rate_0_100") for lab in R if lab != "ctrl"}
    res["D2"] = dict(t_c=tcs, coll_rate_0_100=rates)
    if all(rates.get(x) for x in ("f1s1", "f4s1", "f2s1")):
        res["D2"]["rate_f1_over_f2"] = rates["f1s1"] / rates["f2s1"]
        res["D2"]["rate_f4_over_f2"] = rates["f4s1"] / rates["f2s1"]
        res["D2"]["rate_f4_over_f1"] = rates["f4s1"] / rates["f1s1"]
    with open(os.path.join(a.out, "d2.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res["D2"], indent=1, default=float))
    for lab, v in R.items():
        print(lab, {k: v.get(k) for k in ("t_end", "t_c_interp", "t_exc", "alpha_min_min", "t_alpha_min_min",
                                         "alpha_c_change_100_110", "alpha_c_change_280_300",
                                         "collisions_per_particle_before_tc", "collisions_per_particle_t100",
                                         "coll_rate_0_100", "coll_rate_0_tc_or_200", "D50", "D100", "D150",
                                         "dH_rel_end", "n_noroot_before_exc", "n_trunc", "max_P", "s_per_M")})

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    cols = dict(zip(("ctrl", "f1s1", "f2s1", "f4s1", "f2s2"), fs.series_colors(5)))
    fig, axs = plt.subplots(1, 3, figsize=(10.0, 3.2))
    for lab, h in ser.items():
        c = cols.get(lab, "k")
        axs[0].plot(h["time"], h["alpha_probe"] - h["alpha_probe"][0], color=c, lw=0.9, label=lab)
        axs[1].plot(h["time"], h["alpha_min"], color=c, lw=0.9, label=lab)
        ch = os.path.join(dirs[lab], "cc.coll.hst")
        if os.path.exists(ch):
            cc = read_dedup(ch)
            axs[2].plot(cc["time"], 2.0 * np.cumsum(cc["n_coll"]) / N_PART, color=c, lw=0.9, label=lab)
    axs[1].axhline(0.3, **fs.GUIDE)
    axs[2].axhline(REF_M4["coll_per_particle"], **fs.GUIDE)
    axs[2].axvline(REF_M4["t_c"], **fs.GUIDE)
    axs[0].set_ylabel(r"$\alpha_c(t)-\alpha_c(0)$")
    axs[1].set_ylabel(r"$\alpha_{\min}$")
    axs[2].set_ylabel("collisions per particle")
    for ax in axs:
        ax.set_xlabel("t / M")
    axs[0].legend(fontsize=7)
    axs[2].set_title("guides: M/4 reference t_c, collisions", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_d2.png"), dpi=150)
    print("wrote", os.path.join(a.out, "fig_d2.png"))


if __name__ == "__main__":
    main()
