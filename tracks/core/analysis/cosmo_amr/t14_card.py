#!/usr/bin/env python3
"""T14 of the work package cosmo-amr: the card executable against the processor runs of
the same decks (prediction: tracks/core/JOURNAL-cosmo-amr.md, entry of T14).

    t14_card.py --card RUNDIR --t2 RUNDIR --t9 RUNDIR --out DIR

RUNDIR of --card holds the cases U, S, A, M, G (decks of T2) and ladder (deck of T9) as
run by scripts/gpu_batch.sh; --t2 and --t9 are the processor runs.  Nothing is run here.
Writes DIR/t14_summary.json and DIR/fig_t14_card.{pdf,png}."""
import argparse
import json
import os
import sys

import numpy as np

import amrlib as A


def spread(a, b):
    return np.abs(a/b - 1.0)


def rel(a, b):
    """largest |a/b - 1| over the common records (b non-zero)"""
    n = min(len(a), len(b))
    a, b = np.asarray(a[:n], float), np.asarray(b[:n], float)
    ok = np.isfinite(a) & np.isfinite(b) & (b != 0)
    return float(np.max(np.abs(a[ok]/b[ok] - 1.0))) if ok.any() else float("nan")


def batch_status(rd):
    out = {}
    with open(os.path.join(rd, "batch.list.status")) as f:
        for line in f:
            w = line.split()
            if len(w) >= 3 and w[1].startswith("rc="):
                out[os.path.basename(w[2])] = int(w[1][3:])
    return out


def tracker(path):
    a = np.loadtxt(path, ndmin=2)
    return a[:, 1], a[:, 2:5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--t2", required=True)
    ap.add_argument("--t9", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    a.out = os.path.abspath(a.out)
    os.makedirs(a.out, exist_ok=True)
    rc = batch_status(a.card)
    res = {"exit": rc}
    keep = {}
    # ---- homogeneous cases and the moving tracker
    for n in ("U", "S", "A", "M"):
        hc = A.read_hst(os.path.join(a.card, n, "flrw.nrpic.hst"))
        hp = A.read_hst(os.path.join(a.t2, n, "flrw.nrpic.hst"))
        sc = A.read_hst(os.path.join(a.card, n, "flrw.cstat.hst"))
        r = {"records_card": int(len(hc["time"])), "records_cpu": int(len(hp["time"]))}
        r["chi_spread_max"] = float(np.max(spread(sc["chi_max"], sc["chi_min"])))
        r["E_spread_max"] = float(np.max(spread(hc["E_max"], hc["E_min"])))
        r["time_vs_cpu"] = rel(hc["time"][1:], hp["time"][1:])
        r["alpha_max_vs_cpu"] = rel(hc["alpha_max"], hp["alpha_max"])
        m = min(len(hc["nmb"]), len(hp["nmb"]))
        r["nmb_equal"] = bool(len(hc["nmb"]) == len(hp["nmb"])
                              and np.array_equal(hc["nmb"][:m], hp["nmb"][:m]))
        r["nmb_values_card"] = sorted(set(int(x) for x in hc["nmb"]))
        r["identity_max"] = float(np.max(np.abs(hc["int_E"]/hc["sum_mW"] - 1.0)))
        r["identity_max_cpu"] = float(np.max(np.abs(hp["int_E"]/hp["sum_mW"] - 1.0)))
        res[n] = r
        keep[n] = (hc, hp, sc)
    tc, xc = tracker(os.path.join(a.card, "M", "flrw.co_0.txt"))
    tp, xp = tracker(os.path.join(a.t2, "M", "flrw.co_0.txt"))
    m = min(len(tc), len(tp))
    res["M"]["tracker_records"] = [int(len(tc)), int(len(tp))]
    res["M"]["tracker_vs_cpu_max"] = float(np.max(np.abs(xc[:m] - xp[:m])))
    res["M"]["tracker_time_vs_cpu_max"] = float(np.max(np.abs(tc[:m] - tp[:m])))
    # exact path of the tracker: x = 2.5 + 0.5 t mapped into [-3, 3) (T5)
    xe = (2.5 + 0.5*tc + 3.0) % 6.0 - 3.0
    res["M"]["tracker_vs_exact_max"] = float(np.max(np.abs(xc[:, 0] - xe)))
    # ---- guard
    g = {}
    for lab, rd in (("card", a.card), ("cpu", a.t2)):
        with open(os.path.join(rd, "G", "flrw.guard.txt")) as f:
            txt = f.read()
        line = [x for x in txt.splitlines() if "the run stops" in x][0]
        g[lab + "_stop_cycle"] = int(line.split("cycle")[1].split(",")[0])
        g[lab + "_stop_time"] = float(line.split("time")[1].split(",")[0])
        g[lab + "_reason"] = [x for x in txt.splitlines() if x.startswith("reason")][0]
        h = A.read_hst(os.path.join(rd, "G", "flrw.nrpic.hst"))
        g[lab + "_records"] = int(len(h["time"]))
        keep["G" + lab] = (h, A.read_hst(os.path.join(rd, "G", "flrw.cstat.hst")))
    hc, hp = keep["Gcard"][0], keep["Gcpu"][0]
    # how long the two unstable runs agree: first record where alpha_max departs by 1e-6
    m = min(len(hc["time"]), len(hp["time"]))
    d = np.abs(hc["alpha_max"][:m]/hp["alpha_max"][:m] - 1.0)
    bad = np.where(~(d < 1e-6))[0]
    g["first_record_departing_1e-6"] = int(bad[0]) if len(bad) else None
    g["alpha_max_departure_by_record"] = [float(x) for x in d]
    res["G"] = g
    # ---- peak with the lapse ladder
    hc = A.read_hst(os.path.join(a.card, "ladder", "peak.nrpic.hst"))
    hp = A.read_hst(os.path.join(a.t9, "ladder", "peak.nrpic.hst"))
    sc = A.read_hst(os.path.join(a.card, "ladder", "peak.cstat.hst"))
    sp = A.read_hst(os.path.join(a.t9, "ladder", "peak.cstat.hst"))
    m = min(len(hc["time"]), len(hp["time"]))
    r = {"records_card": int(len(hc["time"])), "records_cpu": int(len(hp["time"])),
         "nmb_card": [int(x) for x in hc["nmb"]], "nmb_cpu": [int(x) for x in hp["nmb"]],
         "np_card": sorted(set(int(x) for x in hc["np"])),
         "sum_m_change": float(np.max(np.abs(hc["sum_m"]/hc["sum_m"][0] - 1.0))),
         "identity_max": float(np.max(np.abs(hc["int_E"]/hc["sum_mW"] - 1.0))),
         "time_vs_cpu": rel(hc["time"][1:], hp["time"][1:]),
         "alpha_min_vs_cpu": rel(hc["alpha_min"], hp["alpha_min"]),
         "alpha_max_vs_cpu": rel(hc["alpha_max"], hp["alpha_max"]),
         "E_max_vs_cpu": rel(hc["E_max"], hp["E_max"])}
    ms = min(len(sc["time"]), len(sp["time"]))
    r["cstat_records"] = [int(len(sc["time"])), int(len(sp["time"]))]
    r["Hr_max_card"] = [float(x) for x in sc["Hr_max"]]
    r["Hr_max_cpu"] = [float(x) for x in sp["Hr_max"]]
    r["Hr_max_vs_cpu"] = rel(sc["Hr_max"], sp["Hr_max"])
    r["H_max_vs_cpu"] = rel(sc["H_max"], sp["H_max"])
    r["chi_min_vs_cpu"] = rel(sc["chi_min"], sp["chi_min"])
    res["ladder"] = r
    # ---- region norms on the card (first use of the reducers there)
    for n in ("U", "S", "A", "M"):
        gc = A.read_hst(os.path.join(a.card, n, "flrw.region.hst"))
        gp = A.read_hst(os.path.join(a.t2, n, "flrw.region.hst"))
        worst = 0.0
        for k in gc:
            if k in ("time", "ncycle") or k not in gp:
                continue
            if k.startswith("H") or k.startswith("M"):
                continue           # residuals at round-off: not comparable relatively
            worst = max(worst, rel(gc[k], gp[k]))
        res[n]["region_nonresidual_vs_cpu"] = worst
    # ---- verdicts against the prediction as written
    v = {}
    v["U,S,A homogeneous to 1e-12"] = all(
        res[n]["chi_spread_max"] <= 1e-12 and res[n]["E_spread_max"] <= 1e-12
        for n in ("U", "S", "A"))
    v["alpha_max equals processors to 1e-12 (U,S,A)"] = all(
        res[n]["alpha_max_vs_cpu"] <= 1e-12 for n in ("U", "S", "A"))
    v["M: MeshBlock count equal at every record"] = res["M"]["nmb_equal"]
    v["M: tracker within 1e-12 of the processor path"] = (
        res["M"]["tracker_vs_cpu_max"] <= 1e-12)
    v["G: stop at cycle 18"] = (g["card_stop_cycle"] == 18)
    v["G: status 3 and guard file"] = (rc.get("G") == 3)
    v["ladder: 64 -> 120 MeshBlocks at cycle 4"] = (
        r["nmb_card"][:4] == [64]*4 and r["nmb_card"][4] == 120)
    v["ladder: particles and rest mass unchanged"] = (
        len(r["np_card"]) == 1 and r["sum_m_change"] == 0.0)
    v["ladder: identity below 1e-12"] = (r["identity_max"] < 1e-12)
    v["ladder: Hr_max within 1e-6 of processors"] = (r["Hr_max_vs_cpu"] <= 1e-6)
    res["verdicts"] = v
    with open(os.path.join(a.out, "t14_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
    for k, ok in v.items():
        print(("PASS  " if ok else "FAIL  ") + k)

    # ---- figure
    sys.path.insert(0, os.path.join(A.ROOT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(9.0, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.90, wspace=0.36)
    cols = fs.SERIES
    for i, n in enumerate(("U", "S", "A", "M")):
        hc, hp, sc = keep[n]
        m = min(len(hc["time"]), len(hp["time"]))
        d = np.abs(hc["alpha_max"][:m]/hp["alpha_max"][:m] - 1.0)
        ax[0].semilogy(hc["time"][:m], np.maximum(d, 1e-17), color=cols[i], label=n)
    ax[0].axhline(1e-12, **fs.GUIDE)
    ax[0].set_ylim(5e-18, 1e-10)
    ax[0].set_xlabel("time")
    ax[0].set_ylabel(r"$|\alpha_{\max}^{\rm card}/\alpha_{\max}^{\rm cpu}-1|$")
    ax[0].legend(frameon=False, fontsize=8, ncol=2)
    ax[0].set_title("homogeneous universe", fontsize=9)
    for lab, c, st in (("card", fs.PAL["red"], "-"), ("cpu", fs.PAL["blue"], "--")):
        h, s = keep["G" + lab]
        ok = np.isfinite(s["chi_max"]) & (s["chi_min"] > 0)
        ax[1].semilogy(s["time"][ok], np.maximum(spread(s["chi_max"][ok], s["chi_min"][ok]),
                                                 1e-17), st, color=c, label=lab)
        ax[1].axvline(g[lab + "_stop_time"], color=c, lw=0.6, ls=":")
    ax[1].set_xlabel("time")
    ax[1].set_ylabel(r"$\chi_{\max}/\chi_{\min}-1$")
    ax[1].legend(frameon=False, fontsize=8)
    ax[1].set_title("unstable step (guard): stop times dotted", fontsize=9)
    hc = A.read_hst(os.path.join(a.card, "ladder", "peak.nrpic.hst"))
    hp = A.read_hst(os.path.join(a.t9, "ladder", "peak.nrpic.hst"))
    ax[2].plot(hp["ncycle"], hp["nmb"], "o-", color=fs.PAL["blue"], label="cpu", ms=5)
    ax[2].plot(hc["ncycle"], hc["nmb"], "x--", color=fs.PAL["red"], label="card", ms=6)
    ax[2].set_xlabel("cycle")
    ax[2].set_ylabel("MeshBlocks")
    ax[2].legend(frameon=False, fontsize=8, loc="lower center")
    ax[2].set_title("peak, lapse ladder", fontsize=9)
    axr = ax[2].twinx()
    sc = A.read_hst(os.path.join(a.card, "ladder", "peak.cstat.hst"))
    sp = A.read_hst(os.path.join(a.t9, "ladder", "peak.cstat.hst"))
    ms = min(len(sc["time"]), len(sp["time"]))
    axr.semilogy(np.arange(ms), np.maximum(np.abs(sc["Hr_max"][:ms]/sp["Hr_max"][:ms] - 1),
                                           1e-17), "s:", color="grey", ms=3)
    axr.set_ylabel(r"$|H_r^{\rm card}/H_r^{\rm cpu}-1|$ (grey)", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_t14_card"))
    plt.close(fig)


if __name__ == "__main__":
    main()
