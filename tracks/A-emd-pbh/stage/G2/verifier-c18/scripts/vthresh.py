"""Recompute the threshold_ball claims (README results table) from the raw outputs with the
verifier's readers. Usage: python -I vthresh.py --out DIR [--member NAME ...]"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import figstyle as fs
import matplotlib.pyplot as plt
from vmembers import THRESH, table_of, member_args
from vmeasure import Member, bh_rule, line_ratio, line_mots
from vref import LTB

DC = {"B-d1.00": 1.0, "B-d0.70": 0.7, "B-d0.50": 0.5, "B-d0.45": 0.45, "B-d0.42": 0.42,
      "B-d0.40": 0.40, "B-d0.35": 0.35, "B-d0.20": 0.20, "A-d0.42": 0.42, "A-d0.40": 0.40,
      "C-R1.25": 1.5, "C-d0.42": 0.42}
# threshold_ball/README.md results table: exact tau_AH, persistent from, tau_det, ddet, dmmed
CLAIM = {
    "B-d1.00": (15.386, 17.000, 15.513, 0.126, -3.8e-4),
    "B-d0.70": (23.405, 25.250, 23.472, 0.059, -1.9e-3),
    "B-d0.50": (35.160, 37.188, 35.131, -0.040, -9.4e-3),
    "B-d0.45": (40.054, 42.250, 40.117, 0.043, 1.9e-3),
    "B-d0.42": (43.656, 45.875, 43.686, 0.015, 2.8e-3),
    "B-d0.40": (46.415, 48.625, 46.402, -0.045, 3.2e-4),
    "B-d0.35": (54.980, 58.312, 54.929, -0.142, 2.4e-3),
    "B-d0.20": (114.574, None, None, None, None),
    "A-d0.42": (43.656, None, 43.442, -0.232, -3.8e-2),
    "A-d0.40": (46.415, None, 46.103, -0.331, -4.6e-2),
    "C-R1.25": (9.551, "every", 9.603, 0.040, -1.2e-4),
    "C-d0.42": (43.656, 45.906, 43.705, -0.014, 2.4e-2),
}
T_END = 45.0


def tab_files(d, kind):
    fs_ = sorted(glob.glob(os.path.join(d, "tab", "ball.%s.*.tab" % kind)))
    return fs_


def tab_times(files):
    out = []
    for f in files:
        with open(f) as fh:
            m = re.search(r"time\s*=\s*([-+0-9.eE]+)", fh.readline())
            out.append(float(m.group(1)))
    return np.array(out)


def analyse(name, d):
    m = Member(d, table_of(d))
    args = member_args(d)
    tlim = float(args.get("time/tlim", "nan"))
    rule = bh_rule(m.summ)
    found = m.summ["found"]
    res = {"dir": d, "table": table_of(d), "tlim": tlim, "rule": rule,
           "exact_tau_ah_edge": m.ltb.at_break(0)["tau_ah"], "exact_m_edge": m.ltb.at_break(0)["m"],
           "last_summary_time": float(m.summ["time"][-1]), "last_traj_time": float(m.tr.t[-1])}
    if not found.any():
        # still contracting? Lagrangian radius of the core edge band at the end
        R = m.tr.areal_radius()
        b = int(np.nanargmin(np.abs(m.bRi - 2.603)))
        sel = m.band == b
        Rb = np.nanmean(R[:, sel], axis=1)
        k = np.where(np.isfinite(Rb))[0]
        res["core_band_R_last"] = float(Rb[k[-1]])
        res["core_band_dRdt_last"] = float((Rb[k[-1]] - Rb[k[-5]]) / (m.tr.t[k[-1]] - m.tr.t[k[-5]]))
        res["core_band_tau_last"] = float(np.nanmean(m.tr.tau[k[-1], sel]))
        return res, None
    i1 = np.where(found)[0][0]
    res["first"] = m.ddet(i1)
    if rule["persistent_from"] is not None:
        ip = int(np.where(np.isclose(m.summ["time"], rule["persistent_from"]))[0][0])
        res["persistent"] = m.ddet(ip)
    # envelope proper time at the first detection (SCOPE section 3 time measure)
    br, bt, cnt = m.bands_at(res["first"]["t"])
    env = m.brb0 > m.ltb.breaks[1] + 0.02
    res["envelope_tau_at_first"] = float(np.nanmean(bt[env])) if env.any() else None
    ms = m.masses()
    dm = ms[:, 1] / ms[:, 2] - 1
    ok = np.isfinite(dm)
    res["dm_first"] = float(dm[0]) if ok[0] else None
    res["dm_median"] = float(np.median(dm[ok])) if ok.any() else None
    res["dm_median_bounds"] = ([float(np.nanmedian(ms[ok, 1] / ms[ok, 4] - 1)),
                                float(np.nanmedian(ms[ok, 1] / ms[ok, 3] - 1))] if ok.any() else None)
    res["n_det"], res["n_det_exact"] = int(ms.shape[0]), int(ok.sum())
    res["exact_window"] = [float(ms[ok, 0].min()), float(ms[ok, 0].max())] if ok.any() else None
    # line diagnostics at the tab output nearest the first detection and the persistent start
    con, tmu, adm = tab_files(d, "con"), tab_files(d, "tmunu"), tab_files(d, "adm")
    if con and len(con) == len(tmu) == len(adm):
        tt = tab_times(con)
        res["line"] = {}
        for key, tq in (("t0", 0.0), ("first", res["first"]["t"]),
                        ("persistent", res.get("persistent", {}).get("t")),
                        ("plus2", res["first"]["t"] + 2.0)):
            if tq is None:
                continue
            k = int(np.argmin(np.abs(tt - tq)))
            # horizon coordinate radius at that time from the nearest successful search
            js = np.where(found)[0]
            j = js[np.argmin(np.abs(m.summ["time"][js] - tt[k]))]
            rin = float(m.summ["meanradius"][j]) if key != "t0" else 0.0
            lr_all = line_ratio(con[k], tmu[k], adm[k], r_in=rin)
            lr_mat = line_ratio(con[k], tmu[k], adm[k], r_in=rin, matter_only=True)
            mo = line_mots(adm[k])
            mots = [mo[s]["m"] for s in ("pos", "neg") if mo[s] is not None]
            res["line"][key] = {"t_tab": float(tt[k]), "r_in": rin, "ratio_all": lr_all,
                                "ratio_matter": lr_mat,
                                "mots_m": mots, "finder_t": float(m.summ["time"][j]),
                                "finder_mirr": float(m.summ["mirr"][j])}
    series = {"t": m.summ["time"], "found": m.summ["found"].astype(float), "mirr": m.summ["mirr"],
              "mt": ms[:, 0], "mmirr": ms[:, 1], "mex": ms[:, 2], "mlo": ms[:, 3], "mhi": ms[:, 4]}
    # line MOTS mass at every tab output from 1 M before the first detection to the end
    if con:
        lt, lm = [], []
        for k in np.where(tt >= res["first"]["t"] - 1.0)[0]:
            mo = line_mots(adm[k])
            ms_ = [mo[s_]["m"] for s_ in ("pos", "neg") if mo[s_] is not None]
            lt.append(tt[k])
            lm.append(np.mean(ms_) if ms_ else np.nan)
        series["line_t"], series["line_mots"] = np.array(lt), np.array(lm)
    return res, series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--member", action="append")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = a.member or list(THRESH)
    res, ser = {}, {}
    for n in names:
        res[n], ser[n] = analyse(n, THRESH[n])
        r = res[n]
        if "first" in r:
            f = r["first"]
            ln = r.get("line", {}).get("first", {})
            print("%-8s bh %s pers %s t1 %.4f tau_det %.4f ddet v1 %+.4f v2 %+.4f v3 %+.4f dm1 %s dmmed %s "
                  "env_tau %.3f ratio(r2) %s mots %s finder %s" % (
                      n, r["rule"]["bh"], r["rule"]["persistent_from"], f["t"], f["tau_det"], f["ddet_v1"],
                      f["ddet_v2"], f["ddet_v3"], r["dm_first"], r["dm_median"], r["envelope_tau_at_first"],
                      ln.get("ratio_all", {}).get("r2"), ln.get("mots_m"), ln.get("finder_mirr")), flush=True)
        else:
            print("%-8s never found; last search %.3f, core band R %.4f dR/dt %.4f" % (
                n, r["last_summary_time"], r["core_band_R_last"], r["core_band_dRdt_last"]), flush=True)
    # bracket at t_end = 45 on mesh B (tau_det of the first detection, v2)
    br = {}
    for mesh, lo, hi in (("B", "B-d0.40", "B-d0.42"), ("A", "A-d0.40", "A-d0.42")):
        if lo in res and hi in res and "first" in res[lo] and "first" in res[hi]:
            tl, th = res[lo]["first"]["tau_det"], res[hi]["first"]["tau_det"]
            br[mesh] = {"tau_det_lo": tl, "tau_det_hi": th,
                        "bracket_holds": bool(th <= T_END < tl),
                        "dc_interp": 0.40 + 0.02 * (tl - T_END) / (tl - th)}
    el, eh = res.get("B-d0.40", {}).get("exact_tau_ah_edge"), res.get("B-d0.42", {}).get("exact_tau_ah_edge")
    if el and eh:
        br["exact"] = {"tau_lo": el, "tau_hi": eh, "dc_interp": 0.40 + 0.02 * (el - T_END) / (el - eh)}
    np.savez(os.path.join(a.out, "vthresh_series.npz"),
             **{"%s__%s" % (n, k): v for n, sr in ser.items() if sr is not None for k, v in sr.items()})
    out = {"members": res, "bracket": br, "claims": CLAIM}
    with open(os.path.join(a.out, "vthresh.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(json.dumps(br, indent=1))

    # figure 1: search outcomes and the persistence rule
    fs.use_style()
    order = [n for n in ("B-d1.00", "B-d0.70", "B-d0.50", "B-d0.45", "B-d0.42", "B-d0.40", "B-d0.35",
                         "B-d0.20", "A-d0.42", "A-d0.40", "C-d0.42", "C-R1.25") if n in res]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.14, top=0.97)
    for y, n in enumerate(order):
        s = ser[n]
        r = res[n]
        if s is None:
            ax.plot([r["last_summary_time"]], [y], "x", color="k", ms=4)
            continue
        f = s["found"] > 0
        ax.plot(s["t"][~f], np.full((~f).sum(), y), "|", color="grey", alpha=0.4, ms=6)
        ax.plot(s["t"][f], np.full(f.sum(), y), "|", color=fs.PAL["red"], ms=8)
        tau = r["exact_tau_ah_edge"]
        ax.plot([r["first"]["tau_det"]], [y + 0.3], "v", color=fs.PAL["red"], ms=4)
        ax.plot([tau], [y + 0.3], "v", color=fs.PAL["blue"], ms=4, mfc="none")
        if r["rule"]["persistent_from"] is not None and r["rule"]["bh"]:
            ax.plot([r["rule"]["persistent_from"]], [y], "o", color="k", ms=3)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=8)
    ax.axvline(T_END, color="k", ls="--", lw=1.0)
    ax.set_xlabel("coordinate time of the search (red: found, grey: not); triangles: proper time "
                  "of first detection (red), exact $\\tau_{\\rm AH}$ (blue)", fontsize=8)
    ax.set_xlim(5, 72)
    fs.save(fig, os.path.join(a.out, "fig_vthresh_searches"))
    plt.close(fig)

    # figure 2: tau_det against delta_c with the exact curve and t_end, ddet, constraint ratios
    fig, ax = plt.subplots(1, 3, figsize=(8, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.9, wspace=0.42)
    exact = sorted((DC[n], res[n]["exact_tau_ah_edge"]) for n in res if n.startswith("B-"))
    ax[0].plot([e[0] for e in exact], [e[1] for e in exact], "-", color=fs.PAL["blue"], label="exact (verifier)")
    for n, mk, c in (("B-", "o", fs.PAL["red"]), ("A-", "s", fs.PAL["yellow"]), ("C-d", "^", fs.PAL["green"])):
        pts = [(DC[k], res[k]["first"]["tau_det"]) for k in res if k.startswith(n) and "first" in res[k]]
        if pts:
            ax[0].plot(*zip(*pts), mk, color=c, ms=4, mfc="none", label="mesh %s" % n[0])
    ax[0].axhline(T_END, color="k", ls="--", lw=1.0)
    ax[0].set_xlim(0.37, 0.47)
    ax[0].set_ylim(38, 50)
    ax[0].set_xlabel(r"$\delta_c$", labelpad=-1)
    ax[0].set_title(r"$\tau_{\rm det}$ near $t_{\rm end}$", fontsize=10)
    ax[0].legend(fontsize=7)
    for n, mk, c in (("B-", "o", fs.PAL["red"]), ("A-", "s", fs.PAL["yellow"]), ("C-", "^", fs.PAL["green"])):
        pts = [(DC[k], res[k]["first"]["ddet_v2"]) for k in res if k.startswith(n) and "first" in res[k]]
        cl = [(DC[k], CLAIM[k][3]) for k in res if k.startswith(n) and CLAIM[k][3] is not None]
        if pts:
            ax[1].plot(*zip(*pts), mk, color=c, ms=4, label="verifier %s" % n[0])
        if cl:
            ax[1].plot(*zip(*cl), "x", color=c, ms=5)
    ax[1].axhline(0, color="grey", lw=0.8)
    ax[1].set_xlabel(r"$\delta_c$", labelpad=-1)
    ax[1].set_title(r"$\Delta\tau_{\rm det}$ (M); x: README", fontsize=10)
    ax[1].legend(fontsize=7)
    for k in res:
        ln = res[k].get("line", {})
        for key, mk in (("first", "o"), ("persistent", "s")):
            if key in ln:
                ax[2].semilogy([DC[k]], [ln[key]["ratio_all"]["r2"]], mk, ms=4, mfc="none",
                               color=fs.PAL["red"] if k.startswith("B") else (fs.PAL["yellow"] if k.startswith("A") else fs.PAL["green"]))
        if "t0" in ln:
            ax[2].semilogy([DC[k]], [max(ln["t0"]["ratio_all"]["r2"], 1e-6)], "+", color="k", ms=5)
    ax[2].axhline(0.1, color="k", ls="--", lw=1.0)
    ax[2].set_xlabel(r"$\delta_c$", labelpad=-1)
    ax[2].set_title(r"$\|H\|/\|16\pi E\|$ outside AH", fontsize=10)
    fs.save(fig, os.path.join(a.out, "fig_vthresh_summary"))
    plt.close(fig)
    fig_masses(res, ser, a.out)


def fig_masses(res, ser, out):
    show = [n for n in ("B-d1.00", "B-d0.45", "B-d0.42", "B-d0.40", "C-d0.42", "C-R1.25") if n in ser and ser[n] is not None]
    fig, axs = plt.subplots(2, 3, figsize=(8, 5.0), sharey=False)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.1, top=0.95, wspace=0.32, hspace=0.38)
    for ax, n in zip(axs.flat, show):
        s = ser[n]
        f = s["found"] > 0
        ax.plot(s["t"][f], s["mirr"][f], ".", ms=2, color=fs.PAL["red"], label="finder (found)")
        ok = np.isfinite(s["mex"])
        ax.plot(s["mt"][ok], s["mex"][ok], "-", color=fs.PAL["blue"], lw=1.0, label="exact on slice")
        fs.band(ax, s["mt"][ok], np.minimum(s["mlo"][ok], s["mhi"][ok]), np.maximum(s["mlo"][ok], s["mhi"][ok]), fs.PAL["blue"])
        if "line_t" in s:
            ax.plot(s["line_t"], s["line_mots"], "s", ms=3, mfc="none", color="k", label="line MOTS (verifier)")
        ax.axhline(res[n]["exact_m_edge"], color="grey", lw=0.8, ls=":")
        ax.set_title(n, fontsize=9)
        ax.set_xlabel("$t$ (M)", labelpad=-1)
        if ax is axs.flat[0]:
            ax.legend(fontsize=6)
    fs.save(fig, os.path.join(out, "fig_vthresh_masses"))
    plt.close(fig)


if __name__ == "__main__":
    main()
