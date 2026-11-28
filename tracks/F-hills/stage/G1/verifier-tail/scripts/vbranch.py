"""Branches of the finder in A2 (F-20261124-210400-902c650): the heavy hole 86.6 M to the jump
(finding F1 of the first part) and the member m2 (finder 1) where it alternates, separated by
mass and compared by the summary's hrms (column 9, area mean of the squared expansion) and, where
the status file exists (from 133 M), by found flag, flow iterations and mean expansion.
Also the (2,2) amplitude of rPsi4 against the retarded time u = t - r* (r* with the remnant mass).

Run: python vbranch.py --vtail <vtail.json of the run before> --out <dir>
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "verifier", "scripts")))
import vread  # noqa: E402
sys.path.insert(0, HERE)
import figstyle  # noqa: E402
import vtail  # noqa: E402

RUN_A, RUN_A2 = vtail.RUN_A, vtail.RUN_A2


def branches(t, m, h, t0, t1, split=None):
    w = (t >= t0) & (t < t1)
    tw, mw, hw = t[w], m[w], h[w]
    if split is None:
        split = 0.5 * (np.percentile(mw, 95) + np.percentile(mw, 5))
    up, lo = mw > split, mw <= split
    out = {"t0": t0, "t1": t1, "split": float(split), "n_upper": int(up.sum()), "n_lower": int(lo.sum())}
    for nm, s in (("upper", up), ("lower", lo)):
        if s.any():
            out[nm] = {"t_first": float(tw[s].min()), "t_last": float(tw[s].max()),
                       "mass_median": float(np.median(mw[s])), "mass_min": float(mw[s].min()),
                       "mass_max": float(mw[s].max()),
                       "hrms_min": float(hw[s].min()), "hrms_median": float(np.median(hw[s])),
                       "hrms_max": float(hw[s].max())}
    return out, w, up, lo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--vtail", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    prev = json.load(open(args.vtail))
    t_jump = prev["heavy"]["t_first_mass_above_1.06"]
    mrem = prev["heavy"]["post_median"]
    res = {"from_vtail": args.vtail, "t_jump": t_jump}

    S2 = vread.read_horizon_summary(os.path.join(RUN_A2, "hills.horizon_summary_2.txt"))
    S1 = vread.read_horizon_summary(os.path.join(RUN_A2, "hills.horizon_summary_1.txt"))
    st1 = vtail.read_status(os.path.join(RUN_A2, "hills.horizon_status_1.txt"))

    # heavy hole, F1 window
    hv, w2, up2, lo2 = branches(S2["t"], S2["mass"], S2["hrms"], 86.6, t_jump)
    hv["ranges_overlap"] = bool(hv["upper"]["hrms_max"] >= hv["lower"]["hrms_min"])
    # where the upper branch's hrms is above the lower's minimum (if anywhere)
    tw = S2["t"][w2]
    hv["upper_rows_with_hrms_above_1e-6"] = [float(x) for x in tw[up2 & (S2["hrms"][w2] > 1e-6)][:20]]
    hv["lower_rows_with_hrms_below_1e-5"] = [float(x) for x in tw[lo2 & (S2["hrms"][w2] < 1e-5)][:20]]
    # before 86.6 M (the smooth decline of the first part): hrms
    pre = (S2["t"] >= 62) & (S2["t"] < 86.6)
    hv["pre_86.6"] = {"mass_first_last": [float(S2["mass"][pre][0]), float(S2["mass"][pre][-1])],
                      "hrms_median": float(np.median(S2["hrms"][pre])), "hrms_max": float(S2["hrms"][pre].max())}
    res["heavy_F1"] = hv

    # finder 1, the alternating stretch: find it as the times where consecutive masses jump by > 2e-4
    d = np.abs(np.diff(S1["mass"]))
    alt = np.where(d > 2e-4)[0]
    alt = alt[S1["t"][alt] > 133]
    t0, t1 = float(S1["t"][alt[0]]), float(S1["t"][alt[-1] + 1]) + 1e-6
    m1b, w1, up1, lo1 = branches(S1["t"], S1["mass"], S1["hrms"], t0, t1)
    # status columns on the same searches
    key = {vtail.tkey32(a): i for i, a in enumerate(st1["t"])}
    rows = []
    for tt, mm, isup in zip(S1["t"][w1], S1["mass"][w1], up1):
        k = key.get(vtail.tkey32(tt))
        if k is not None:
            rows.append((isup, st1["found"][k], st1["flow_it"][k], st1["mean_exp"][k], st1["area_mass"][k], mm))
    rows = np.array(rows, dtype=float)
    for nm, s in (("upper", rows[:, 0] > 0.5), ("lower", rows[:, 0] < 0.5)):
        m1b[nm]["status"] = {"n": int(s.sum()), "found": int(rows[s, 1].sum()),
                             "flow_it_median": float(np.median(rows[s, 2])),
                             "flow_it_min_max": [float(rows[s, 2].min()), float(rows[s, 2].max())],
                             "mean_exp_median": float(np.median(rows[s, 3])),
                             "area_mass_minus_summary_mass_median": float(np.median(rows[s, 4] - rows[s, 5]))}
    m1b["ranges_overlap"] = bool(m1b["upper"]["hrms_max"] >= m1b["lower"]["hrms_min"])
    # outside the stretch (133 M to t0 and t1 to 186 M)
    out1 = (S1["t"] >= 133) & ~w1
    m1b["outside"] = {"hrms_median": float(np.median(S1["hrms"][out1])), "hrms_max": float(S1["hrms"][out1].max()),
                      "mass_median": float(np.median(S1["mass"][out1]))}
    res["m2_branches"] = m1b

    # (2,2) amplitude against retarded time
    wf = {}
    for r in (40, 48, 70, 90):
        amp = {}
        for rd in (RUN_A, RUN_A2):
            re_, _ = vread.read_numeric(os.path.join(rd, "waveforms", f"rpsi4_real_{r:04d}.txt"))
            im_, _ = vread.read_numeric(os.path.join(rd, "waveforms", f"rpsi4_imag_{r:04d}.txt"))
            for a_, b_ in zip(re_, im_):
                amp[round(a_[0], 6)] = math.hypot(a_[5], b_[5])
        ts = np.array(sorted(amp))
        av = np.array([amp[k] for k in ts])
        rstar = r + 2 * mrem * math.log(r / (2 * mrem) - 1)
        u = ts - rstar
        base = np.median(av[(ts > 60) & (ts < 130)])
        above = np.where((av > 3 * base) & (ts > 130))[0]
        # first time after 130 M from which the amplitude stays above 3x the baseline to the end
        k_on = None
        if len(above):
            for k in above:
                if (av[k:] > 3 * base).all():
                    k_on = k
                    break
        wf[r] = (u, av, base)
        res.setdefault("waves22_onset", {})[str(r)] = {
            "r_star": rstar, "baseline_60_130": float(base),
            "t_onset_3x_to_end": float(ts[k_on]) if k_on is not None else None,
            "u_onset": float(u[k_on]) if k_on is not None else None,
            "a_end": float(av[-1]), "t_end": float(ts[-1])}

    figstyle.use_style()
    import matplotlib.pyplot as plt
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 6.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.97, wspace=0.34, hspace=0.32)
    a = ax[0, 0]
    tw, hw = S2["t"][w2], S2["hrms"][w2]
    a.semilogy(tw[up2], hw[up2], ".", ms=1.5, color=P["blue"], label="heavy, upper branch")
    a.semilogy(tw[lo2], hw[lo2], ".", ms=1.5, color=P["red"], label="heavy, lower branch(es)")
    a.semilogy(S2["t"][pre], S2["hrms"][pre], ".", ms=1.0, color="grey", label="heavy, 62-86.6 M")
    a.axvline(133.0, color="grey", lw=0.8, ls=":")
    a.set_xlabel("t [M]"); a.set_ylabel("hrms (summary col. 9)"); a.legend(fontsize=7, loc="center left")
    a = ax[0, 1]
    tw1, hw1 = S1["t"][w1], S1["hrms"][w1]
    a.semilogy(tw1[up1], hw1[up1], ".", ms=1.5, color=P["blue"], label="m2, upper branch")
    a.semilogy(tw1[lo1], hw1[lo1], ".", ms=1.5, color=P["red"], label="m2, lower branch")
    o = (S1["t"] >= 120) & ~w1
    a.semilogy(S1["t"][o], S1["hrms"][o], ".", ms=1.0, color="grey", label="m2, outside the stretch")
    a.set_xlabel("t [M]"); a.set_ylabel("hrms (summary col. 9)"); a.legend(fontsize=7, loc="center left")
    a = ax[1, 0]
    flow = rows[:, 2]
    tt_rows = S1["t"][w1][[vtail.tkey32(x) in key for x in S1["t"][w1]]]
    a.plot(tt_rows[rows[:, 0] > 0.5], flow[rows[:, 0] > 0.5], ".", ms=2, color=P["blue"], label="upper")
    a.plot(tt_rows[rows[:, 0] < 0.5], flow[rows[:, 0] < 0.5], ".", ms=2, color=P["red"], label="lower")
    a.set_xlabel("t [M]"); a.set_ylabel("flow iterations (status, finder 1)"); a.legend(fontsize=7)
    a = ax[1, 1]
    for col, r in zip((P["blue"], P["red"], P["green"], P["orange"]), (40, 48, 70, 90)):
        u, av, base = wf[r]
        a.semilogy(u, av, color=col, lw=0.8, label=f"r = {r} M")
    a.axvline(t_jump, **figstyle.MASK_LINE)
    a.set_xlim(20, 160)
    a.set_xlabel("u = t - r* [M]"); a.set_ylabel("|r Psi4 (2,2)|"); a.legend(fontsize=7, loc="upper left")
    figstyle.save(fig, os.path.join(args.out, "fig_t_branches"))

    with open(os.path.join(args.out, "vbranch.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, default=float)[:4000])


if __name__ == "__main__":
    main()
