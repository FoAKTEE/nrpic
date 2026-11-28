#!/usr/bin/env python3
"""Reader of G-8, the first production member of G3 (run D-20261128-062142-c5666c4), written after the
chain ended and before its outputs were read (g3/amend JOURNAL entry 8 holds the predictions).

Claim G at one member (SCOPE_G3.md section 4 with amendments A1-A6):
  * the summary FILTERED by the status file (searches not found dropped; excguard's filtered_view);
  * per dust removal (tags >= 140, reasons 2 and 3) r = M_AH(first found search at or after t_rem) /
    M_LTB(tau_rem) - 1, with M_LTB(tau) = m(R0) at tau_H(R0) (esf_growth.csv of the data run);
  * G3-G1: medians of r in 10 M bins of tau_rem with >= 20 removals, from tau_rem = 50 M to the end,
    within +-0.5 per cent; P-G1 and entry 8's sharper band;
  * the lead of the shells carried as a bias (section 6): the same medians with tau_rem + dtau_lead(R0),
    dtau_lead from VERIFIER section 4.1 (M/8, N) with two brackets beyond R0 = 28 M;
  * excision (reasons by time; reason 2 more than 2 M after a segment start), finder status, G-8 - FK at
    common search times, the slope d ln M / d ln a in windows of 0.1 in ln a from tau = 50 M against the
    exact one, card time from the chain's segment logs.
One figure g8_read.png; numbers in g8_read.json.

Usage: g8_read.py --g8 RUNDIR --fk RUNDIR --data DATADIR [--out DIR]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(TRACK, "flux_tools"))
sys.path.insert(0, os.path.join(TRACK, "excguard", "tools"))
sys.path.insert(0, HERE)
import fluxio  # noqa: E402
import eg8_read  # noqa: E402  (filtered_view, segment_times)
import figstyle  # noqa: E402  (copy of python/nrpic/figstyle.py in this package)

H0 = 5.58116e-3          # Hubble rate of the data, 1/M (flux_tools/esf_data.py; SCOPE_G3 section 1)
LEAD_R0 = np.array([0.0, 10.0, 20.0, 28.0])
LEAD_DT = np.array([0.0, 0.01, 0.17, 0.78])   # VERIFIER section 4.1, M/8 and N (0.01 is the bound "below 0.01")
SLOPE_2028 = (0.78 - 0.17) / 8.0


def lead(R0, bracket):
    d = np.interp(R0, LEAD_R0, LEAD_DT)
    if bracket == "extrapolated":
        d = np.where(R0 > 28.0, 0.78 + SLOPE_2028 * (R0 - 28.0), d)
    return d


def binned(tau, y, lo=0.0, hi=None, width=10.0, nmin=20):
    hi = hi if hi is not None else tau.max()
    edges = np.arange(lo, hi + width, width)
    rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        s = (tau > a) & (tau <= b)
        n = int(s.sum())
        rows.append(dict(lo=float(a), hi=float(b), n=n, median=float(np.median(y[s])) if n else None,
                         counted=bool(n >= nmin)))
    return rows


def lna(tau):
    return (2.0 / 3.0) * np.log1p(1.5 * H0 * tau)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g8", required=True)
    ap.add_argument("--fk", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    J = dict(run=a.g8)

    view = os.path.join(a.out, "view")
    st, n_drop = eg8_read.filtered_view(a.g8, "g3g8", view)
    J["summary_rows_dropped_not_found"] = n_drop
    hor = fluxio.read_horizon(os.path.join(view, "g3g8.horizon_summary_0.txt"))
    th, Mh, rmin = hor["time"], hor["mass"], hor["minradius"]

    rem = fluxio.read_removed(os.path.join(a.g8, "g3g8.removed.bin"))
    rst_t = fluxio.restart_times(os.path.join(a.g8, "rst"))
    info = []
    if np.any(np.diff(rem["time"]) < 0):
        rem, info = fluxio.drop_overlaps(rem, rst_t)
    lab = np.load(os.path.join(a.data, "esf_labels.npz"))
    grow = np.loadtxt(os.path.join(a.data, "esf_growth.csv"), delimiter=",", skiprows=1)
    o = np.argsort(grow[:, 2])
    g_tau, g_m = grow[o, 2], grow[o, 1]

    def M_LTB(tau):
        return np.interp(tau, g_tau, g_m, left=1.0)

    # excision
    dust_all = rem["tag"] >= 140
    seg_starts = np.unique(np.concatenate([[0.0], rst_t]))
    near = np.zeros(rem["time"].size, bool)
    for t0 in seg_starts:
        near |= (rem["time"] >= t0) & (rem["time"] <= t0 + 2.0)
    r2 = dust_all & (rem["reason"] == 2)
    J["excision"] = dict(dust_by_reason={str(r): int(np.sum(dust_all & (rem["reason"] == r))) for r in (1, 2, 3, 4)},
                         reason2_more_than_2M_after_a_segment_start=int(np.sum(r2 & ~near)),
                         reason2_within_2M=int(np.sum(r2 & near)),
                         overlaps_dropped=info, restart_times=[float(x) for x in rst_t],
                         minradius_last=float(rmin[-1]), t_last=float(th[-1]), mass_last=float(Mh[-1]))
    J["excision"]["holds"] = J["excision"]["reason2_more_than_2M_after_a_segment_start"] == 0

    # r per removal
    hz = dust_all & np.isin(rem["reason"], (2, 3))
    tag, trem, tau = rem["tag"][hz], rem["time"][hz], rem["tau"][hz]
    k = np.searchsorted(th, trem, side="left")
    ok = k < th.size
    tag, trem, tau, k = tag[ok], trem[ok], tau[ok], k[ok]
    M_at = Mh[k]
    R0 = lab["R0"][tag]
    r_raw = M_at / M_LTB(tau) - 1.0
    r_held = M_at / M_LTB(tau + lead(R0, "held")) - 1.0
    r_extr = M_at / M_LTB(tau + lead(R0, "extrapolated")) - 1.0
    tau_end = float(tau.max())
    B = {}
    for name, y in (("raw", r_raw), ("lead_held", r_held), ("lead_extrapolated", r_extr)):
        rows = binned(tau, y, hi=tau_end)
        B[name] = rows
    cnt = lambda rows: [b for b in rows if b["counted"] and b["lo"] >= 50.0]  # noqa: E731
    med_raw = np.array([b["median"] for b in cnt(B["raw"])])
    med_held = np.array([b["median"] for b in cnt(B["lead_held"])])
    med_extr = np.array([b["median"] for b in cnt(B["lead_extrapolated"])])
    lo_raw = np.array([b["lo"] for b in cnt(B["raw"])])
    J["bins"] = {k2: [(b["lo"], b["hi"], b["n"], b["median"]) for b in v if b["counted"]] for k2, v in B.items()}
    J["n_removals_read"] = int(tau.size)
    J["R0_range_removed"] = [float(R0.min()), float(R0.max())]
    J["tau_end"] = tau_end
    J["G3_G1"] = dict(n_bins=int(med_raw.size), min=float(med_raw.min()), max=float(med_raw.max()),
                      holds=bool(np.all(np.abs(med_raw) <= 0.005)))
    J["P_G1"] = dict(raw_in_band=bool(np.all((med_raw >= 0.0005) & (med_raw <= 0.0030))),
                     corrected_in_band_held=bool(np.all((med_held >= -0.0010) & (med_held <= 0.0025))),
                     corrected_in_band_extrapolated=bool(np.all((med_extr >= -0.0010) & (med_extr <= 0.0025))),
                     corrected_range_held=[float(med_held.min()), float(med_held.max())],
                     corrected_range_extrapolated=[float(med_extr.min()), float(med_extr.max())])
    J["entry8_band"] = dict(holds=bool(np.all((med_raw >= 0.0012) & (med_raw <= 0.0030))),
                            refuted=bool(np.any(med_raw < 0.0010) or np.any(med_raw > 0.0035)))
    late = lo_raw >= 100.0
    sh_h = med_raw[late] - med_held[late]
    sh_e = med_raw[late] - med_extr[late]
    J["lead_bias"] = dict(shift_held_range=[float(sh_h.min()), float(sh_h.max())], shift_held_mean=float(sh_h.mean()),
                          shift_extrapolated_range=[float(sh_e.min()), float(sh_e.max())],
                          prediction_held_in_band=bool(np.all((sh_h >= 2e-4) & (sh_h <= 1.2e-3))))

    # finder status and G-8 - FK
    s2 = st["time"] > 2.0
    fnd = s2 & (st["found"] == 1)
    J["finder"] = dict(n_after_2M=int(s2.sum()), found=int(fnd.sum()), frac_found=float(fnd.sum() / s2.sum()),
                       not_found_times=[float(x) for x in st["time"][s2 & (st["found"] == 0)]][:50],
                       not_found_reasons=[int(x) for x in st["reason"][s2 & (st["found"] == 0)]][:50],
                       t0=dict(found=int(st["found"][0]), mass=float(st["area_mass"][0])))
    J["finder"]["holds"] = J["finder"]["frac_found"] >= 0.99
    fk = fluxio.read_horizon(os.path.join(a.fk, "esflk.horizon_summary_0.txt"))
    com, i8, ik = np.intersect1d(np.round(th, 6), np.round(fk["time"], 6), return_indices=True)
    w = (com >= 20) & (com <= 399.5)
    dMk = Mh[i8][w] - fk["mass"][ik][w]
    J["G8_minus_FK"] = dict(n=int(w.sum()), median=float(np.median(dMk)), p05=float(np.percentile(dMk, 5)),
                            p95=float(np.percentile(dMk, 95)), holds=bool(2e-5 <= np.median(dMk) <= 1.2e-4))

    # slope windows of 0.1 in ln a from tau = 50 M (A4 S3)
    la = lna(tau)
    la0 = float(lna(np.array(50.0)))
    wins = []
    x0 = la0
    while x0 + 0.1 <= la.max() + 1e-12:
        s = (la >= x0) & (la < x0 + 0.1)
        if s.sum() >= 40:
            p = np.polyfit(la[s], np.log(M_at[s]), 1)[0]
            te = np.linspace(tau[s].min(), tau[s].max(), 200)
            pe = np.polyfit(lna(te), np.log(M_LTB(te)), 1)[0]
            wins.append(dict(lna_lo=float(x0), n=int(s.sum()), s_run=float(p), s_LTB=float(pe), diff=float(p - pe)))
        x0 += 0.1
    J["slope"] = dict(windows=wins, max_abs_diff=float(max(abs(x["diff"]) for x in wins)) if wins else None)
    J["slope"]["within_0.03"] = bool(wins and J["slope"]["max_abs_diff"] <= 0.03)

    # card time
    segs = eg8_read.segment_times(os.path.join(a.g8, "chain"))
    J["card"] = dict(segments=segs, wall_h=sum(x["wall_s"] for x in segs) / 3600.0)
    J["card"]["in_band"] = bool(1.9 <= J["card"]["wall_h"] <= 3.0)

    with open(os.path.join(a.out, "g8_read.json"), "w") as f:
        json.dump(J, f, indent=1, default=float)

    import matplotlib
    matplotlib.use("Agg")
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.2))
    A = ax[0, 0]
    sub = np.arange(0, tau.size, max(1, tau.size // 4000))
    A.plot(tau[sub], M_at[sub], ".", ms=1.5, color="C3", alpha=0.5, label="G-8: M_AH at removal vs tau_rem")
    tt = np.linspace(0, tau_end, 400)
    A.plot(tt, M_LTB(tt), color="k", lw=1.0, label="exact LTB M(tau)")
    A.set_xlabel("proper time of the swallowed dust tau [M]")
    A.set_ylabel("horizon mass [M]")
    A.legend(fontsize=7, loc="upper left")
    A.set_title("(a) growth law: G-8 against the exact solution", fontsize=9)
    Bx = ax[0, 1]
    for name, c, lab_ in (("raw", "C3", "tau_rem"), ("lead_held", "C0", "tau_rem + lead (held beyond 28 M)"),
                          ("lead_extrapolated", "C2", "tau_rem + lead (extrapolated)")):
        rows = [b for b in B[name] if b["counted"]]
        Bx.step([b["lo"] + 5 for b in rows], [100 * b["median"] for b in rows], where="mid", color=c, lw=1, label=lab_)
    Bx.axhspan(0.12, 0.30, color="C3", alpha=0.10, label="entry 8 band (raw)")
    Bx.axhline(0.5, ls="--", color="k", lw=0.8, label="G3-G1 +-0.5 %")
    Bx.axhline(-0.5, ls="--", color="k", lw=0.8)
    Bx.axhline(0, color="k", lw=0.4)
    Bx.axvline(50, ls=":", color="0.5", lw=0.8)
    Bx.set_ylim(-0.6, 0.6)
    Bx.set_xlabel("tau_rem [M]")
    Bx.set_ylabel("median M_AH/M_LTB - 1 [%]")
    Bx.legend(fontsize=6.5, loc="lower right")
    Bx.set_title("(b) G3-G1: 10 M bins (>= 20 removals)", fontsize=9)
    Cx = ax[1, 0]
    if wins:
        xs = [x["lna_lo"] + 0.05 for x in wins]
        Cx.plot(xs, [x["s_run"] for x in wins], "o-", color="C3", ms=3, label="G-8")
        Cx.plot(xs, [x["s_LTB"] for x in wins], "s--", color="k", ms=3, label="exact LTB")
    Cx.set_xlabel("ln a (window centres, width 0.1)")
    Cx.set_ylabel("d ln M_AH / d ln a")
    Cx.legend(fontsize=7)
    Cx.set_title("(c) logarithmic slope of the growth law", fontsize=9)
    D = ax[1, 1]
    D.plot(com[w], 1e5 * dMk, color="C3", lw=0.6, label="M_G-8 - M_FK (polished minus unpolished)")
    D.axhspan(2, 12, color="C2", alpha=0.15, label="band [2e-5, 1.2e-4]")
    D.axhline(1e5 * J["G8_minus_FK"]["median"], color="k", lw=0.8, ls="--",
              label=f"median {J['G8_minus_FK']['median']:.2e}")
    D.set_xlabel("t [M]")
    D.set_ylabel("mass difference [1e-5 M]")
    D.legend(fontsize=7)
    D.set_title("(d) finder: G-8 against FK at common search times", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "g8_read.png"), dpi=130)
    print(json.dumps({k2: v for k2, v in J.items() if k2 in ("G3_G1", "P_G1", "entry8_band", "lead_bias", "excision",
                                                             "G8_minus_FK", "card")}, indent=1, default=float))
    print(json.dumps({"finder": {k2: v for k2, v in J["finder"].items() if k2 != "not_found_times"},
                      "slope_max_abs_diff": J["slope"]["max_abs_diff"], "R0_range": J["R0_range_removed"],
                      "tau_end": tau_end, "n": J["n_removals_read"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
