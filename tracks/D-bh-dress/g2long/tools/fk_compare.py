#!/usr/bin/env python3
"""Judgement of run FK ES-FLK against ES-FL (g2long/JOURNAL.md entry 6, predictions P7-P10).

FK is ES-FL with the finder's initial_radius_0 = 1.6 M instead of 0.8 M, so horizon excision
(which stops once the smallest horizon radius exceeds 4 x initial_radius_0, nrpic.cpp:451-455)
stays on to 6.4 M instead of 3.2 M. Both runs are read the same way here (the reading of
g2runs/tools/esf_criteria.py: last finder record per time, removal records of preempted segments
dropped, M_LTB from esf_growth.csv, m_disc as in esf_analyse.py), so the comparison does not
depend on two separate analyses.

P7  |M_FK - M_ESFL| <= 3e-4 at every common finder time t <= t_switch (219 M).
P8  every dust removal (tag >= 140, reasons 2 or 3) has reason 3 up to the end of FK.
P9  (iii) bin medians (10 M bins of tau_rem, >= 20 removals) with lo >= 280 M stay at
    +0.25 +- 0.15 per cent; refuted if a median after tau_rem = 285 M exceeds +0.45 per cent.
    D3 margin of the dust removals after t_rem = 220 M stays below 3e-3.
P10 |M_FK(400) - 1.4920| <= 3e-3; refuted above 5e-3.
(P11, the cost, is read from the manifest.)

Usage: fk_compare.py --fk RUN:BASE --ref RUN:BASE --data DATA --control CTRL_SUMMARY --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TRACK, "flux_tools"))
sys.path.insert(0, os.path.join(TRACK, "g2runs", "tools"))
import fluxio  # noqa: E402
from esf_criteria import binned_median, first_sample  # noqa: E402

TAU_MAX = 650.0


def load_run(spec, data, ctrl):
    run, base = spec.split(":")
    b = os.path.join(run, base)
    hor = fluxio.read_horizon(b + ".horizon_summary_0.txt")
    rem = fluxio.read_removed(b + ".removed.bin")
    info = []
    if np.any(np.diff(rem["time"]) < 0.0):
        rem, info = fluxio.drop_overlaps(rem, fluxio.restart_times(os.path.join(run, "rst")))
    lab = np.load(os.path.join(data, "esf_labels.npz"))
    grow = np.loadtxt(os.path.join(data, "esf_growth.csv"), delimiter=",", skiprows=1)
    g_tau, g_m = grow[:, 2], grow[:, 1]
    o = np.argsort(g_tau)
    g_tau, g_m = g_tau[o], g_m[o]
    th, Mh = hor["time"], hor["mass"]
    tc, Mc = ctrl["time"], ctrl["mass"]
    hz = np.isin(rem["reason"], (2, 3))
    tag, trem, tau, reason = rem["tag"][hz], rem["time"][hz], rem["tau"][hz], rem["reason"][hz]
    dust = tag >= 140
    k, ok = first_sample(th, trem)
    M_at = Mh[k]
    ratio = M_at / np.interp(tau, g_tau, g_m, left=1.0) - 1.0
    s3 = dust & ok & (tau <= TAU_MAX)
    bins = binned_median(tau[s3], ratio[s3], tau_max=TAU_MAX)
    R0all, EKall, mall = lab["R0"], lab["E_K"], lab["rest"]
    order = np.argsort(R0all, kind="stable")
    cum = 1.0 + np.cumsum((mall * EKall)[order])
    Rs = R0all[order]
    last = np.searchsorted(Rs, Rs, side="right") - 1
    m_disc = np.empty_like(cum)
    m_disc[order] = cum[last]
    sd = dust & ok
    marg = M_at[sd] - (np.interp(th[k[sd]], tc, Mc) - 1.0) - m_disc[tag[sd]]
    return dict(run=run, base=base, th=th, Mh=Mh, rmin=hor["minradius"], rmean=hor["meanradius"],
                trem=trem, tau=tau, reason=reason, dust=dust, ratio=ratio, s3=s3, bins=bins,
                trem_d=trem[sd], marg=marg, overlap=info, n_rem=int(rem["n"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fk", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--t_switch", type=float, default=219.0)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ctrl = fluxio.read_horizon(a.control)
    fk = load_run(a.fk, a.data, ctrl)
    rf = load_run(a.ref, a.data, ctrl)
    out = dict(fk=a.fk, ref=a.ref, data=a.data, control=a.control,
               fk_t_end=float(fk["th"][-1]), ref_t_end=float(rf["th"][-1]),
               fk_overlaps_dropped=fk["overlap"], ref_overlaps_dropped=rf["overlap"])

    # P7: common finder times
    tk = np.round(fk["th"] * 2.0) / 2.0
    tr = np.round(rf["th"] * 2.0) / 2.0
    common, ik, ir = np.intersect1d(tk, tr, return_indices=True)
    dM = fk["Mh"][ik] - rf["Mh"][ir]
    w = common <= a.t_switch
    out["P7"] = dict(n=int(w.sum()), max_abs_diff_to_switch=float(np.abs(dM[w]).max()),
                     t_at_max=float(common[w][np.argmax(np.abs(dM[w]))]),
                     max_abs_diff_t0_excluded=float(np.abs(dM[w & (common > 0)]).max()),
                     diff_at={str(t): float(dM[common == t][0]) for t in (0.0, 50.0, 100.0, 150.0, 200.0,
                                                                         219.0, 250.0, 300.0, 350.0, 399.5)
                              if np.any(common == t)},
                     holds=bool(np.abs(dM[w & (common > 0)]).max() <= 3e-4))
    # excision switch: first time the smallest horizon radius exceeds 4 x initial_radius
    for name, r, r0 in (("fk", fk, 1.6), ("ref", rf, 0.8)):
        above = np.nonzero(r["rmin"] > 4.0 * r0)[0]
        out[f"switch_{name}"] = dict(limit=4.0 * r0, t_first_above=float(r["th"][above[0]]) if above.size else None,
                                     rmin_end=float(r["rmin"][-1]), rmin_max=float(r["rmin"].max()))
    # P8
    d = fk["dust"]
    out["P8"] = dict(n_dust_removed=int(d.sum()),
                     reasons={str(x): int(np.sum(d & (fk["reason"] == x))) for x in (2, 3)},
                     frac_reason3=float(np.mean(fk["reason"][d] == 3)),
                     ref_reasons_to_fk_end={str(x): int(np.sum(rf["dust"] & (rf["reason"] == x)
                                                               & (rf["trem"] <= fk["th"][-1]))) for x in (2, 3)},
                     holds=bool(np.all(fk["reason"][d] == 3)))
    # P9
    def late_bins(r, lo=280.0):
        return [b for b in r["bins"] if b["counted"] and b["lo"] >= lo]
    lb_fk, lb_rf = late_bins(fk), late_bins(rf)
    med_fk = [b["median"] for b in lb_fk]
    out["P9"] = dict(
        bins_fk=[dict(lo=b["lo"], n=b["n"], median=b["median"]) for b in lb_fk],
        bins_ref=[dict(lo=b["lo"], n=b["n"], median=b["median"]) for b in lb_rf],
        fk_max_median_late=float(max(med_fk)) if med_fk else None,
        fk_min_median_late=float(min(med_fk)) if med_fk else None,
        ref_max_median_late_same_range=float(max(b["median"] for b in lb_rf if b["lo"] <= (lb_fk[-1]["lo"] if lb_fk else 0)))
        if lb_fk else None,
        fk_tau_max_counted=float(lb_fk[-1]["hi"]) if lb_fk else None,
        fk_all_counted_max_abs=float(max(abs(b["median"]) for b in fk["bins"] if b["counted"])),
        fk_n_counted=int(sum(b["counted"] for b in fk["bins"])),
        within_band=bool(med_fk and all(0.001 <= m <= 0.004 for m in med_fk)),
        refuted=bool(any(b["median"] > 0.0045 for b in lb_fk if b["hi"] > 285.0)),
        D3_fk_max_after_220=float(fk["marg"][fk["trem_d"] >= 220.0].max()) if np.any(fk["trem_d"] >= 220.0) else None,
        D3_ref_max_after_220=float(rf["marg"][(rf["trem_d"] >= 220.0) & (rf["trem_d"] <= fk["th"][-1])].max()),
        D3_fk_min=float(fk["marg"].min()), D3_ref_min=float(rf["marg"].min()),
        D3_fk_n_viol=int(np.sum(fk["marg"] < -3e-4)))
    out["P9"]["D3_holds"] = bool(out["P9"]["D3_fk_max_after_220"] is not None
                                 and out["P9"]["D3_fk_max_after_220"] < 3e-3)
    # P10
    M400 = float(np.interp(400.0, fk["th"], fk["Mh"]))
    out["P10"] = dict(M_fk_400=M400, M_fk_last=float(fk["Mh"][-1]), t_last=float(fk["th"][-1]),
                      M_ref_400=float(np.interp(400.0, rf["th"], rf["Mh"])),
                      diff_vs_14920=M400 - 1.4920, holds=bool(abs(M400 - 1.4920) <= 3e-3),
                      refuted=bool(abs(M400 - 1.4920) > 5e-3))
    with open(os.path.join(a.out, "fk_compare.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "P9"}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out["P9"].items() if not k.startswith("bins")}, indent=1, default=float))
    figure(a.out, fk, rf, common, dM, a.t_switch, out)


def figure(outdir, fk, rf, common, dM, t_switch, out):
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.2))
    fig.subplots_adjust(left=0.11, right=0.91, bottom=0.08, top=0.95, wspace=0.42, hspace=0.38)
    x = ax[0, 0]
    x.plot(common, 1e5 * dM, color=fs.PAL["red"], lw=1.2, label=r"$M_{\rm FK}-M_{\rm ES\text{-}FL}$")
    x.axvline(t_switch, **fs.GUIDE)
    x.set_ylim(-5, 5)
    x.set_xlabel(r"$t/M$", labelpad=-2)
    x.set_ylabel(r"$\Delta M_{\rm AH}$ [$10^{-5} M$]")
    x.set_title("Top left: FK - ES-FL (P7 band +-30, off scale)", loc="left", fontsize=8)
    x.legend(fontsize=7, frameon=False, loc="lower left")
    x = ax[0, 1]
    for r, c, lab in ((rf, fs.PAL["blue"], "ES-FL (excision to 3.2 M)"), (fk, fs.PAL["red"], "FK (excision to 6.4 M)")):
        b = [q for q in r["bins"] if q["counted"]]
        x.step([q["lo"] for q in b] + [b[-1]["hi"]], [100 * q["median"] for q in b] + [100 * b[-1]["median"]],
               where="post", color=c, lw=1.4, label=lab)
    x.axhspan(0.10, 0.40, xmin=0, xmax=1, color="grey", alpha=0.15, lw=0)
    x.axhline(0.45, **fs.GUIDE)
    x.axvline(285.0, color="grey", lw=1.0, ls=":")
    x.set_xlabel(r"$\tau_{\rm rem}/M$", labelpad=-2)
    x.set_ylabel(r"(iii) bin median [per cent]")
    x.set_title("Top right: (iii) medians; band P9, dashed refutation", loc="left", fontsize=8)
    x.legend(fontsize=7, frameon=False, loc="upper left")
    x = ax[1, 0]
    for r, c in ((rf, fs.PAL["blue"]), (fk, fs.PAL["red"])):
        sel = r["trem_d"] <= fk["th"][-1]
        tb = np.arange(0.0, fk["th"][-1] + 10.0, 10.0)
        mx = [r["marg"][sel & (r["trem_d"] > lo) & (r["trem_d"] <= lo + 10)].max()
              if np.any(sel & (r["trem_d"] > lo) & (r["trem_d"] <= lo + 10)) else np.nan for lo in tb]
        mn = [r["marg"][sel & (r["trem_d"] > lo) & (r["trem_d"] <= lo + 10)].min()
              if np.any(sel & (r["trem_d"] > lo) & (r["trem_d"] <= lo + 10)) else np.nan for lo in tb]
        x.step(tb + 10, mx, where="pre", color=c, lw=1.3)
        x.step(tb + 10, mn, where="pre", color=c, lw=1.0, ls="--")
    x.axhline(3e-3, **fs.GUIDE)
    x.axhline(-3e-4, color="grey", lw=1.0, ls=":")
    x.axvline(220.0, color="grey", lw=1.0, ls=":")
    x.set_xlabel(r"$t_{\rm rem}/M$", labelpad=-2)
    x.set_ylabel(r"D3 margin, max / min per 10 M")
    x.set_title("Bottom left: D3 margin (blue ES-FL, red FK)", loc="left", fontsize=8)
    x = ax[1, 1]
    for r, c, r0 in ((rf, fs.PAL["blue"], 0.8), (fk, fs.PAL["red"], 1.6)):
        x.plot(r["th"], r["rmin"], color=c, lw=1.3)
        x.axhline(4 * r0, color=c, lw=1.0, ls="--")
    x2 = x.twinx()
    tb = np.arange(0.0, fk["th"][-1], 10.0)
    for r, c in ((rf, fs.PAL["blue"]), (fk, fs.PAL["red"])):
        f3 = [np.mean(r["reason"][r["dust"] & (r["trem"] > lo) & (r["trem"] <= lo + 10)] == 3)
              if np.any(r["dust"] & (r["trem"] > lo) & (r["trem"] <= lo + 10)) else np.nan for lo in tb]
        x2.plot(tb + 5, f3, "o", ms=2.5, color=c, alpha=0.6)
    x2.set_ylim(-0.05, 1.05)
    x2.set_ylabel("reason-3 fraction")
    x.set_xlabel(r"$t/M$", labelpad=-2)
    x.set_ylabel(r"smallest horizon radius $/M$")
    x.set_title("Bottom right: r_min, 4 x r_init (dashed); dots: reason 3", loc="left", fontsize=8)
    fs.save(fig, os.path.join(outdir, "fk_compare"))
    plt.close(fig)


if __name__ == "__main__":
    main()
