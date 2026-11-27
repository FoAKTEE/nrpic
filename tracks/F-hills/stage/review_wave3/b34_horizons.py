#!/usr/bin/env python3
"""Horizons of the passage A2 from 133 M (lead, batch 34): what the finders' status files say
(found or not, reason, flow iterations, mean expansion), the heavy hole's two branches (verifier
finding F1), m1's merger with M, m2's fate, against the tracker positions and the Newtonian
three-body orbit from the same deck. Predictions D34-1 to D34-4 and C25-1, C25-2 (JOURNAL.md).

Inputs (read only): scratch/F-hills/F-20261124-210400-902c650 (A2; `<fastflow> diagnostics = true`
from the restart at 133.0 M, by `-i`): hills.horizon_status_<n>.txt (columns: cycle, time,
found, reason, flow_iterations, area, area_mass, meanradius, minradius, mean_expansion,
min_abs_mean_expansion, points_outside_mesh, center_x, center_y, center_z; reason 0 found,
1 area not finite, 2 mean expansion not finite, 3 |mean expansion| above its tolerance, 4
negative mean radius, 5 mass below 1e-10, 6 iteration limit: athenak/src/z4c/fastflow.cpp
lines 792-936), hills.horizon_summary_<n>.txt, trackers of A + A2 joined (b11_cards).
Finders: 0 = m1, 1 = m2, 2 = M (P1's order). Masses are area masses sqrt(A / 16 pi).
What is a coordinate reading: tracker positions and the distances between them; what the
horizons show: whether a marginally trapped surface was found, its area mass, its centre.

Output (--out): b34_horizons.json, fig_b34_horizons.png/.pdf.
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/stage/G0/checks"))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import lead_checks as lc  # noqa: E402
import nrread as nr  # noqa: E402
import b11_cards as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

RUN_A2 = bc.RUNS["A2"]
DECK = os.path.join(WT, "tracks/F-hills/binary_conv/inputs/p1b_R16n.athinput")
COLS = ["cycle", "t", "found", "reason", "iters", "area", "mass", "rmean", "rmin", "hmean",
        "hmin_abs", "outside", "cx", "cy", "cz"]


def status(n):
    a = nr.read_table(os.path.join(RUN_A2, f"hills.horizon_status_{n}.txt"))
    a = nr.keep_last_per_time(a, col=1)
    return {c: a[:, i] for i, c in enumerate(COLS[:a.shape[1]])}


def first_below(t, y, thr, t_from=0.0):
    k = np.where((y < thr) & (t >= t_from))[0]
    return float(t[k[0]]) if len(k) else None


def stats(x):
    x = np.asarray(x)
    if len(x) == 0:
        return None
    return {"n": int(len(x)), "min": float(x.min()), "median": float(np.median(x)), "max": float(x.max())}


def branches(t, m, hm):
    """Split found masses into an upper and a lower branch about a running median (width 2 M);
    a branch is real if the split is bimodal: report the gap and |mean expansion| per branch."""
    if len(t) < 10:
        return None
    med = np.array([np.median(m[np.abs(t - ti) <= 1.0]) for ti in t])
    r = m - med
    up, lo = r > 0, r < 0
    sd = float(np.std(r))
    return {"rms_about_running_median": sd, "max_abs_residual": float(np.abs(r).max()),
            "upper": {"n": int(up.sum()), "resid_median": float(np.median(r[up])) if up.any() else None,
                      "abs_hmean_median": float(np.median(np.abs(hm[up]))) if up.any() else None},
            "lower": {"n": int(lo.sum()), "resid_median": float(np.median(r[lo])) if lo.any() else None,
                      "abs_hmean_median": float(np.median(np.abs(hm[lo]))) if lo.any() else None},
            "residual_percentiles_1_50_99": [float(np.percentile(r, q)) for q in (1, 50, 99)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    res = {"run": RUN_A2}

    st = {n: status(n) for n in (0, 1, 2)}
    for n in (0, 1, 2):
        s = st[n]
        reasons = {int(r): int(np.sum(s["reason"] == r)) for r in np.unique(s["reason"])}
        res[f"status{n}"] = {"t_first": float(s["t"][0]), "t_last": float(s["t"][-1]), "n": int(len(s["t"])),
                             "n_found": int(np.sum(s["found"] == 1)), "reasons": reasons,
                             "iters_found": stats(s["iters"][s["found"] == 1]),
                             "mass_found": stats(s["mass"][s["found"] == 1]),
                             "abs_hmean_found": stats(np.abs(s["hmean"][s["found"] == 1]))}

    # trackers (coordinate positions), joined A + A2, fine grid for the merger
    tr = bc.trackers("A")
    tc, X, _ = nr.common_times(tr, keys=[0, 1, 2], dt=0.05)
    d0 = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
    d1 = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)
    s01 = np.linalg.norm(X[:, 0] - X[:, 1], axis=1)
    t15, t10, t05 = (first_below(tc, d0, v, 120.0) for v in (1.5, 1.0, 0.5))
    res["tracker"] = {"t_end": float(tc[-1]), "t_d0_below_1.5": t15, "t_d0_below_1.0": t10, "t_d0_below_0.5": t05,
                      "d0_min_after_120": float(d0[tc >= 120].min()), "d0_end": float(d0[-1]),
                      "d1_end": float(d1[-1]), "s01_end": float(s01[-1])}
    k = tc >= 120
    i1 = int(np.argmin(d1[k]))
    kk = tc >= tc[-1] - 10
    res["tracker"].update({"d1_min_after_120": float(d1[k][i1]), "t_d1_min_after_120": float(tc[k][i1]),
                           "d1_slope_last10M": float(np.polyfit(tc[kk], d1[kk], 1)[0]),
                           "d1_at": {f"{T:g}": float(np.interp(T, tc, d1)) for T in (133, 140, 150, 160, 170, 180)
                                     if T <= tc[-1]}})

    # finder 0 (m1) around the merger: found against the tracker distance
    s0 = st[0]
    d0s = np.interp(s0["t"], tc, d0)
    f0 = s0["found"] == 1
    res["D34-2_finder0"] = {
        "found_while_d0_above_1.5": [int(np.sum(f0 & (d0s > 1.5))), int(np.sum(d0s > 1.5))],
        "found_while_d0_below_0.5": [int(np.sum(f0 & (d0s < 0.5))), int(np.sum(d0s < 0.5))],
        "t_last_found": float(s0["t"][f0].max()) if f0.any() else None,
        "d0_at_last_found": float(np.interp(s0["t"][f0].max(), tc, d0)) if f0.any() else None,
        "reasons_after_last_found": {int(r): int(np.sum(s0["reason"][s0["t"] > s0["t"][f0].max()] == r))
                                     for r in np.unique(s0["reason"][s0["t"] > s0["t"][f0].max()])} if f0.any() else None,
    }
    # finder 2 (M): mass before and after
    s2 = st[2]
    f2 = s2["found"] == 1
    tm = t10 if t10 is not None else s2["t"][-1]
    pre = f2 & (s2["t"] < tm - 1.0)
    post = f2 & (s2["t"] > tm + 5.0)
    win = f2 & (s2["t"] >= tm - 10) & (s2["t"] <= tm + 10)
    res["D34-2_finder2"] = {
        "t_merge_ref (d0 < 1 M)": tm,
        "found_fraction_within_10M_of_merge": [int(win.sum()), int(np.sum((s2["t"] >= tm - 10) & (s2["t"] <= tm + 10)))],
        "mass_pre": stats(s2["mass"][pre]), "mass_post": stats(s2["mass"][post]),
        "mass_jump_median": (float(np.median(s2["mass"][post]) - np.median(s2["mass"][pre]))
                             if pre.any() and post.any() else None),
        "rmean_pre_median": float(np.median(s2["rmean"][pre])) if pre.any() else None,
        "rmean_post_median": float(np.median(s2["rmean"][post])) if post.any() else None,
        "mass_last_found": float(s2["mass"][f2][-1]) if f2.any() else None,
        "t_first_mass_above_1.10": first_below(s2["t"][f2], -s2["mass"][f2], -1.10),
        "not_found_rows": [[float(a), int(b), int(c)] for a, b, c in
                           zip(s2["t"][~f2], s2["reason"][~f2], s2["iters"][~f2])][:40],
    }
    # F1: branches of the found heavy-hole mass before the merger (133 M to tm - 1 M)
    res["D34-1_F1"] = branches(s2["t"][pre], s2["mass"][pre], s2["hmean"][pre])
    # summary rows vs status rows (does the summary carry values the status calls not found?)
    hz = nr.read_horizons(RUN_A2)
    d2, nf2 = hz[2]
    k133 = d2["t"] >= 133.0
    res["summary2_from_133"] = {"n_accepted_by_signature": int(k133.sum()), "n_failed_signature_all": int(nf2)}
    # m2's horizon
    s1 = st[1]
    f1 = s1["found"] == 1
    m1med = float(np.median(s1["mass"][f1])) if f1.any() else None
    res["D34-3_finder1"] = {"n_found": int(f1.sum()), "n": int(len(f1)), "mass_median": m1med,
                            "max_abs_dev_from_median": float(np.abs(s1["mass"][f1] - m1med).max()) if f1.any() else None}
    # finder 2's centre against the tracker of M and of m1 (does the merged surface sit between?)
    cen = np.stack([s2["cx"], s2["cy"], s2["cz"]], 1)
    xM = np.stack([np.interp(s2["t"], tc, X[:, 2, c]) for c in range(3)], 1)
    x0 = np.stack([np.interp(s2["t"], tc, X[:, 0, c]) for c in range(3)], 1)
    res["finder2_centre"] = {"to_M_tracker_pre_median": float(np.median(np.linalg.norm(cen - xM, axis=1)[pre])) if pre.any() else None,
                             "to_M_tracker_post_median": float(np.median(np.linalg.norm(cen - xM, axis=1)[post])) if post.any() else None,
                             "to_m1_tracker_post_median": float(np.median(np.linalg.norm(cen - x0, axis=1)[post])) if post.any() else None}

    # Newton from the same deck (bare masses, deck state)
    m, x, p = lc.read_athinput(DECK)
    tN, Y = lc.newton_full(m, x, p, t_end=200.0, nout=4001)
    XN = Y[:, :9].reshape(-1, 3, 3)
    d0N = np.linalg.norm(XN[:, 0] - XN[:, 2], axis=1)
    d1N = np.linalg.norm(XN[:, 1] - XN[:, 2], axis=1)
    res["newton"] = {"d0_min": float(d0N.min()), "t_d0_min": float(tN[np.argmin(d0N)]),
                     "d1_min": float(d1N.min()), "t_d1_min": float(tN[np.argmin(d1N)]),
                     "d0_at_186": float(np.interp(186, tN, d0N)), "d1_at_186": float(np.interp(186, tN, d1N))}

    with open(os.path.join(o.out, "b34_horizons.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    fig, axs = plt.subplots(4, 1, figsize=(6.6, 10.0), sharex=True)
    ax = axs[0]
    ax.plot(tc, d0, color=fs.PAL["red"], lw=1.2, label="NR m/16: m1 to M (trackers)")
    ax.plot(tc, d1, color=fs.PAL["orange"], lw=1.2, label="NR m/16: m2 to M (trackers)")
    ax.plot(tN, d0N, color=fs.PAL["red"], lw=0.9, ls="--", label="Newton: m1 to M")
    ax.plot(tN, d1N, color=fs.PAL["orange"], lw=0.9, ls="--", label="Newton: m2 to M")
    ax.axvline(133.0, color="0.5", lw=0.6, ls=":")
    ax.set_ylim(0, 30)
    ax.set_ylabel(r"coordinate distance [$M$]")
    ax.legend(fontsize=6, ncol=2)
    ax = axs[1]
    for n, col, lab in ((0, fs.PAL["red"], "finder 0 (m1)"), (1, fs.PAL["orange"], "finder 1 (m2)"),
                        (2, fs.PAL["blue"], "finder 2 (M)")):
        s = st[n]
        f = s["found"] == 1
        ax.plot(s["t"][f], np.full(f.sum(), n) + 0.15, "|", color=col, ms=4, label=f"{lab} found")
        ax.plot(s["t"][~f], np.full((~f).sum(), n) - 0.15, "x", color="k", ms=2.5)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["m1", "m2", "M"])
    ax.set_ylabel("search (| found, x not)")
    ax = axs[2]
    ax.plot(s2["t"][f2], s2["mass"][f2], ".", color=fs.PAL["blue"], ms=1.5, label="finder 2 (M), found")
    ax.plot(s2["t"][~f2], s2["mass"][~f2], "x", color="k", ms=2.5, label="finder 2, not found (last surface)")
    ax.plot(s0["t"][f0], s0["mass"][f0] + 1.0, ".", color=fs.PAL["red"], ms=1.5, label="finder 0 (m1) found, mass + 1")
    ax.set_ylabel(r"area mass [$M$]")
    ax.legend(fontsize=6)
    ax = axs[3]
    ax.semilogy(s2["t"][f2], np.abs(s2["hmean"][f2]), ".", color=fs.PAL["blue"], ms=1.5, label="finder 2 |mean expansion|")
    ax.semilogy(s1["t"][f1], np.abs(s1["hmean"][f1]), ".", color=fs.PAL["orange"], ms=1.5, label="finder 1")
    ax.semilogy(s0["t"][f0], np.abs(s0["hmean"][f0]), ".", color=fs.PAL["red"], ms=1.5, label="finder 0")
    ax.set_ylabel("|mean expansion| (found)")
    ax.set_xlabel(r"$t$ [$M$]")
    ax.legend(fontsize=6)
    for a in axs:
        a.set_xlim(125, float(np.ceil(tc[-1])) + 1)
    axs[0].set_title("A2 from 133 M: trackers (coordinates) and horizon searches (status files)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b34_horizons"))

    # zoom on F1: found heavy-hole masses before the merger
    fig, ax = plt.subplots(1, 1, figsize=(6.4, 3.2))
    ax.plot(s2["t"][pre], s2["mass"][pre], ".", color=fs.PAL["blue"], ms=2)
    ax.plot(s2["t"][~f2 & (s2["t"] < tm)], s2["mass"][~f2 & (s2["t"] < tm)], "x", color="k", ms=3)
    ax.set_xlabel(r"$t$ [$M$]")
    ax.set_ylabel(r"finder 2 area mass [$M$]")
    ax.set_title("F1: heavy hole's found masses from 133 M to the merger (x: not found)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b34_f1"))
    print(json.dumps(res, indent=1)[:7000])


if __name__ == "__main__":
    main()
