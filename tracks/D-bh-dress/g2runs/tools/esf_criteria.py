#!/usr/bin/env python3
"""Evaluation of the pre-registered ES-F criteria that esf_analyse.py does not compute.

Written before any ES-F card data exist (g2runs JOURNAL entry 3), from the definitions of
flux_tools/JOURNAL.md entry 7 (pre-registration of 2026-11-20 14:33 PST), read as written:

(iii) for removed dust particles (reasons 2, 3) with tau_rem <= 250 M, in bins of 10 M of
      tau_rem with at least 20 removals, the median of
      M_AH(first finder sample >= t_rem) / M_LTB(tau_rem) - 1 lies within +-0.01 in every
      bin; M_LTB(tau) = m(R0) at tau_H(R0) from esf_growth.csv. The tracers (tags 0-139)
      are read the same way, as a second reading.
D1  closure at the end: dM_AH(t_end) - F_rem(t_end), raw and with the control's finder
    history subtracted (dM_AH - [M_ctrl(t) - M_ctrl(0)]).
D2  for t >= 20 M: F_rem(t) - 3e-3 <= M_AH(t) - M_ctrl(t) <= F_sph(t) + 3e-3.
D3  per removed dust particle: M_AH(first sample >= t_rem) - [M_ctrl(t) - 1] >= m_disc(R0) - 3e-4.
D4  tau_rem - tau_H(R0): distribution, minimum, fraction below 0.
Also the predictions P1, P2, P5, P6 of entry 7 where the outputs allow (numbers only; the
judgement is written in the journal).

F_rem uses E_K per tag (energy_by_tag.npy); F_sph = net inward m E through sphere 1 plus
the content at t = 0 (as esf_analyse.py / compare.py). The control is a horizon summary
(V-1 by default, as entry 7 names it).

Usage: esf_criteria.py --run RUN --data DATA --control CTRL_SUMMARY [--base esf] [--out DIR]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FLUX = os.path.join(os.path.dirname(os.path.dirname(HERE)), "flux_tools")
sys.path.insert(0, HERE)
sys.path.insert(0, FLUX)
import fluxio  # noqa: E402  (flux_tools, read-only use)
import compare as cmp  # noqa: E402

TAU_MAX = 250.0
BIN = 10.0
NMIN = 20


def first_sample(th, t_ev):
    k = np.searchsorted(th, t_ev, side="left")
    ok = k < th.size
    return np.clip(k, 0, th.size - 1), ok


def binned_median(tau, y, tau_max=TAU_MAX, width=BIN, nmin=NMIN):
    edges = np.arange(0.0, tau_max + width, width)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = (tau > lo) & (tau <= hi)
        n = int(s.sum())
        rows.append(dict(lo=float(lo), hi=float(hi), n=n,
                         median=float(np.median(y[s])) if n else None,
                         counted=bool(n >= nmin)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--base", default="esf")
    ap.add_argument("--sphere", type=int, default=1)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    b = os.path.join(a.run, a.base)
    hor = fluxio.read_horizon(b + ".horizon_summary_0.txt")
    rem = fluxio.read_removed(b + ".removed.bin")
    acc = fluxio.read_hst(b + ".acc.hst")
    hst = fluxio.read_hst(b + ".nrpic.hst")
    ctrl = fluxio.read_horizon(a.control)
    EK = np.load(os.path.join(a.data, "energy_by_tag.npy"))
    lab = np.load(os.path.join(a.data, "esf_labels.npz"))
    grow = np.loadtxt(os.path.join(a.data, "esf_growth.csv"), delimiter=",", skiprows=1)
    g_tau, g_m = grow[:, 2], grow[:, 1]
    o = np.argsort(g_tau)
    g_tau, g_m = g_tau[o], g_m[o]

    def M_LTB(tau):
        return np.interp(tau, g_tau, g_m, left=1.0)

    th, Mh = hor["time"], hor["mass"]
    tc, Mc = ctrl["time"], ctrl["mass"]
    Mc0 = float(Mc[0])

    def Mctrl(t):
        return np.interp(t, tc, Mc)

    out = dict(run=a.run, control=a.control, t_end_finder=float(th[-1]),
               t_end_hst=float(hst["time"][-1]))

    hz = np.isin(rem["reason"], (2, 3))
    tag, trem, tau = rem["tag"][hz], rem["time"][hz], rem["tau"][hz]
    is_tr = tag < 140
    is_dust = ~is_tr
    k, ok = first_sample(th, trem)
    M_at = Mh[k]

    # (iii)
    ratio = M_at / M_LTB(tau) - 1.0
    res3 = {}
    for name, s in (("dust", is_dust & ok & (tau <= TAU_MAX)), ("tracers", is_tr & ok & (tau <= TAU_MAX))):
        rows = binned_median(tau[s], ratio[s])
        cnt = [r for r in rows if r["counted"]]
        res3[name] = dict(n=int(s.sum()), bins=rows, n_bins_counted=len(cnt),
                          max_abs_median=max((abs(r["median"]) for r in cnt), default=None),
                          overall_median=float(np.median(ratio[s])) if s.any() else None,
                          holds=bool(cnt) and all(abs(r["median"]) <= 0.01 for r in cnt))
    # tracers have few removals per bin: also per R0 group
    if is_tr.any():
        grp = {}
        for R0 in np.unique(np.round(lab["R0"][tag[is_tr]], 3)):
            s = is_tr & ok & (np.abs(lab["R0"][tag] - R0) < 1e-3)
            grp[str(float(R0))] = dict(n=int(s.sum()), median=float(np.median(ratio[s])),
                                       tau_med=float(np.median(tau[s])),
                                       t_first=float(trem[s].min()), t_med=float(np.median(trem[s])))
        res3["tracer_groups"] = grp
    out["iii"] = res3

    # D1, D2 via compare.py with E_K and the t = 0 content inside sphere 1
    nrp = fluxio.read_nrp(os.path.join(a.data, "esf.nrp"))
    rk = float(acc[f"radius{a.sphere}"][0])
    inside = np.linalg.norm(nrp["x"], axis=1) < rk
    content0 = float(np.sum(nrp["m"][inside] * EK[inside]))
    res = cmp.compare(hor, 0.0, rem=rem, acc=acc, ctrl=ctrl, floor=2.8e-5, sphere=a.sphere,
                      E_by_tag=EK, content0=content0)
    t, dM, Frem, Fsph = res["t"], res["dM"], res["F_rem"], res["F_sph"]
    dM_ctrl = dM - (Mctrl(t) - Mc0)
    out["D1"] = dict(t_end=float(t[-1]), dM_end=float(dM[-1]), F_rem_end=float(Frem[-1]),
                     F_sph_end=float(Fsph[-1]), raw=float(dM[-1] - Frem[-1]),
                     ctrl_subtracted=float(dM_ctrl[-1] - Frem[-1]), content0=content0)
    w = t >= 20.0
    diff = Mh[np.searchsorted(th, t)] - Mctrl(t)
    lo_v = Frem - 3e-3 - diff
    hi_v = diff - (Fsph + 3e-3)
    out["D2"] = dict(n=int(w.sum()), n_below=int(np.sum(lo_v[w] > 0)), n_above=int(np.sum(hi_v[w] > 0)),
                     max_below=float(lo_v[w].max()) if w.any() else None,
                     max_above=float(hi_v[w].max()) if w.any() else None,
                     holds=bool(w.any() and np.all(lo_v[w] <= 0) and np.all(hi_v[w] <= 0)))
    out["criterion_i"] = res["summary"]

    # D3 (m_disc as in esf_analyse.py)
    R0all, EKall, mall = lab["R0"], lab["E_K"], lab["rest"]
    order = np.argsort(R0all, kind="stable")
    cum = 1.0 + np.cumsum((mall * EKall)[order])
    Rs = R0all[order]
    last = np.searchsorted(Rs, Rs, side="right") - 1
    m_disc = np.empty_like(cum)
    m_disc[order] = cum[last]
    s = is_dust & ok
    marg = M_at[s] - (Mctrl(th[k[s]]) - 1.0) - m_disc[tag[s]]
    out["D3"] = dict(n=int(s.sum()), min_margin=float(marg.min()) if s.any() else None,
                     n_violations=int(np.sum(marg < -3e-4)), holds=bool(np.all(marg >= -3e-4)))
    # D4
    dtau = tau - lab["tauH"][tag]
    out["D4"] = dict(n=int(dtau.size), min=float(dtau.min()) if dtau.size else None,
                     median=float(np.median(dtau)) if dtau.size else None,
                     frac_below_0=float(np.mean(dtau < 0)) if dtau.size else None,
                     n_below_minus1=int(np.sum(dtau < -1.0)))

    # P1, P2, P5, P6 numbers
    late = trem >= trem.max() - 5.0 if trem.size else np.zeros(0, bool)
    out["P1"] = dict(tau_at_horizon_t_end=float(np.median(tau[late & is_dust])) if (late & is_dust).any() else None,
                     kappa_late=float(np.median(tau[late & is_dust] / trem[late & is_dust])) if (late & is_dust).any() else None)
    out["P2"] = {str(tt): float(np.interp(tt, th, Mh)) for tt in (50.0, 100.0, 150.0, 200.0) if th[-1] >= tt}
    reasons = rem["reason"]
    dust_all = rem["tag"] >= 140
    out["P5"] = dict(t_first_dust_removal=float(rem["time"][dust_all].min()) if dust_all.any() else None,
                     n_excised_dust=int(np.sum(dust_all & np.isin(reasons, (2, 3)))),
                     sum_mEK_removed=float(np.sum(rem["m"][hz & (rem["tag"] >= 140)] * EK[tag[is_dust]])),
                     reasons_dust={str(r): int(np.sum(dust_all & (reasons == r))) for r in (1, 2, 3, 4)},
                     frac_reason3=float(np.mean(reasons[dust_all & np.isin(reasons, (2, 3))] == 3)) if (dust_all & np.isin(reasons, (2, 3))).any() else None)
    th_h = hst["time"]
    m_in = acc.get(f"m_inside{a.sphere}")
    out["P6"] = dict(np_min=float(hst["np"].min()), np_end=float(hst["np"][-1]),
                     n_escaped_end=float(hst["n_escaped"][-1]) if "n_escaped" in hst else None,
                     alpha_min_range=[float(hst["alpha_min"].min()), float(hst["alpha_min"].max())]
                     if "alpha_min" in hst else None,
                     m_inside1_max_after_20=float(m_in[acc["time"] >= 20].max()) if m_in is not None and np.any(acc["time"] >= 20) else None,
                     finder_finite=bool(np.all(np.isfinite(Mh))),
                     finder_gaps_gt_1M=int(np.sum(np.diff(th) > 1.0)))

    with open(os.path.join(a.out, "esf_criteria.json"), "w") as f:
        json.dump(cmp.jsonable(out), f, indent=1)
    figure(a.out, th, Mh, t, diff, Frem, Fsph, tau, ratio, is_dust & ok, is_tr & ok, res3,
           trem[s], marg, dtau)
    print(json.dumps(cmp.jsonable({k: v for k, v in out.items() if k != "iii"}), indent=1))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "bins"} if isinstance(v, dict) else v
                      for k, v in res3.items()}, indent=1))


def figure(outdir, th, Mh, t, diff, Frem, Fsph, tau, ratio, sd, st, res3, trem_d, marg, dtau):
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0), constrained_layout=True)
    x = ax[0, 0]
    x.plot(t, diff, color=fs.PAL["blue"], lw=1.2, label=r"$M_{\rm AH}-M_{\rm ctrl}$")
    x.plot(t, Frem, color=fs.PAL["red"], lw=1.2, label=r"$F_{\rm rem}$ (removed, $mE_K$)")
    x.plot(t, Fsph, color=fs.PAL["green"], lw=1.2, label=r"$F_{\rm sph}$ (sphere 5 M + content)")
    x.fill_between(t, Frem - 3e-3, Fsph + 3e-3, color="grey", alpha=0.15, lw=0)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"mass $/M$")
    x.legend(fontsize=7, frameon=False, loc="upper left")
    x.set_title("(a) growth against the flux (band: D2)", loc="left", fontsize=9)
    x = ax[0, 1]
    if sd.any():
        x.plot(tau[sd], ratio[sd], ".", ms=1, color=fs.PAL["blue"], alpha=0.3, rasterized=True)
    if st.any():
        x.plot(tau[st], ratio[st], "o", ms=3, color=fs.PAL["red"], label="tracers")
    for r in res3["dust"]["bins"]:
        if r["counted"]:
            x.plot([r["lo"], r["hi"]], [r["median"]] * 2, color="k", lw=2)
    x.axhspan(-0.01, 0.01, color="grey", alpha=0.15, lw=0)
    x.set_xlim(0, TAU_MAX)
    x.set_ylim(-0.03, 0.03)
    x.set_xlabel(r"proper time at removal $\tau_{\rm rem}/M$")
    x.set_ylabel(r"$M_{\rm AH}/M_{\rm LTB}(\tau_{\rm rem})-1$")
    x.set_title("(b) criterion (iii): bin medians (black), band +-1 %", loc="left", fontsize=9)
    x = ax[1, 0]
    if marg.size:
        x.plot(trem_d, marg, ".", ms=1, color=fs.PAL["blue"], alpha=0.3, rasterized=True)
    x.axhline(-3e-4, **fs.GUIDE)
    x.set_xlabel(r"removal time $t_{\rm rem}/M$")
    x.set_ylabel(r"$M_{\rm AH}-(M_{\rm ctrl}-1)-m_{\rm disc}(R_0)$")
    x.set_title("(c) D3 margin (dashed: -3e-4)", loc="left", fontsize=9)
    x = ax[1, 1]
    if dtau.size:
        x.hist(dtau, bins=60, color=fs.PAL["blue"], alpha=0.8)
    x.axvline(0.0, **fs.GUIDE)
    x.set_xlabel(r"$\tau_{\rm rem}-\tau_H(R_0)$ $/M$")
    x.set_ylabel("removals")
    x.set_yscale("log")
    x.set_title("(d) D4: removal after the horizon crossing", loc="left", fontsize=9)
    fs.save(fig, os.path.join(outdir, "esf_criteria"))
    plt.close(fig)


if __name__ == "__main__":
    main()
