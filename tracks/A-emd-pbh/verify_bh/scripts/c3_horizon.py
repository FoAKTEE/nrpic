#!/usr/bin/env python3
"""C3: the first apparent horizon of BH-1R against the exact LTB solution of the table.

For every finder time t with a finite result: irreducible mass sqrt(A/16 pi) and the
Christodoulou mass of the summary, against m_exact(slice t), the Misner-Sharp mass of the
outermost shell that is trapped on that code slice by the particles' own proper times
(tau_p >= tau_AH(R_i)), located from the tracked particles (trajmet proper times) and,
at the snapshot times, from all particles. At the first detection: tau_p - tau_AH(R_i) of
the particles at the horizon's coordinate radius.

Writes c3_horizon.json, fig_c3_horizon.{png,pdf} into $NRPIC_RUN_DIR.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs          # noqa: E402
import vbpaths as P            # noqa: E402
import vbio as V               # noqa: E402
import partdata as PD          # noqa: E402
from ltb import TableLTB, shells_from_table   # noqa: E402

RUN = sys.argv[1] if len(sys.argv) > 1 else "bh_smr"


def tauah_curve(T):
    b1, b2 = np.sort(T.breaks)
    rb = np.concatenate([[b1], b1 + np.geomspace(1e-8, b2 - b1 - 1e-8, 4000)])
    sh = shells_from_table(T, rb, side="out")
    return rb, sh


def outermost_trapped(Ri, taup, curve, Ri_lo, Ri_hi, binw=0.01):
    """Outermost label R_i in (Ri_lo, Ri_hi) with tau_slice(R_i) >= tau_AH(R_i).
    tau_slice: medians of the particles' proper times in bins of R_i, linearly interpolated.
    Returns (R_i*, method spread estimate, number of bins) or NaN when no shell is trapped."""
    sel = np.isfinite(taup) & (Ri > Ri_lo - 0.06) & (Ri < Ri_hi)
    if sel.sum() < 5:
        return np.nan, np.nan, 0, None
    Rs, ts = Ri[sel], taup[sel]
    edges = np.arange(Ri_lo - 0.06, Ri_hi + binw, binw)
    k = np.digitize(Rs, edges)
    xb, yb, sb = [], [], []
    for q in np.unique(k):
        s = k == q
        if s.sum() >= 1:
            xb.append(np.median(Rs[s]))
            yb.append(np.median(ts[s]))
            sb.append(np.std(ts[s]) if s.sum() > 2 else np.nan)
    xb, yb, sb = np.array(xb), np.array(yb), np.array(sb)
    cR, ctau = curve                              # tau_AH against R_i outside the edge (increasing)
    # evaluate on the exact curve's R_i grid inside the data range (outside the edge only)
    g = cR[(cR >= max(Ri_lo, xb.min())) & (cR <= xb.max())]
    if len(g) < 2:
        return np.nan, np.nan, len(xb), (xb, yb, sb)
    out_side = xb >= Ri_lo - 1e-12
    if out_side.sum() >= 2:
        ts_g = np.interp(g, xb[out_side], yb[out_side])
    else:
        return np.nan, np.nan, len(xb), (xb, yb, sb)
    ta_g = np.interp(g, cR, ctau)
    D = ts_g - ta_g
    if not np.any(D >= 0):
        return np.nan, np.nan, len(xb), (xb, yb, sb)
    j = np.nonzero(D >= 0)[0].max()
    if j + 1 < len(g):
        f = D[j] / (D[j] - D[j + 1])
        Rstar = g[j] + f * (g[j + 1] - g[j])
    else:
        Rstar = g[j]
    # second estimate: quadratic fit of tau_slice(R_i) outside the edge
    xs, ys = xb[out_side], yb[out_side]
    use = xs < min(Rstar + 0.4, xs.max())
    if use.sum() >= 4:
        c = np.polyfit(xs[use], ys[use], 2)
        D2 = np.polyval(c, g) - ta_g
        if np.any(D2 >= 0):
            j2 = np.nonzero(D2 >= 0)[0].max()
            R2 = g[j2] if j2 + 1 >= len(g) else g[j2] + D2[j2] / (D2[j2] - D2[j2 + 1]) * (g[j2 + 1] - g[j2])
        else:
            R2 = np.nan
    else:
        R2 = np.nan
    return Rstar, R2, len(xb), (xb, yb, sb)


def main():
    warnings.simplefilter("ignore", RuntimeWarning)
    out = P.outdir()
    T = TableLTB(P.TABLE)
    b1, b2 = np.sort(T.breaks)
    s_edge = T.slice(np.array([b1]), side="in")
    R1 = float(s_edge["R"][0])
    rb_c, sh_c = tauah_curve(T)
    curve = (sh_c.R_i, sh_c.tau_ah)
    m_of_R = lambda R: np.interp(R, sh_c.R_i, sh_c.m)          # noqa: E731
    edge_sh = shells_from_table(T, np.array([b1]), side="in")
    tau_ah_edge = float(edge_sh.tau_ah[0])

    d = P.RUN_DIR[RUN]
    names, hs = V.read_horizon_summary(os.path.join(d, "ball.horizon_summary_0.txt"))
    col = {n: k for k, n in enumerate(names)}
    fin = np.isfinite(hs[:, col["mass"]]) if len(hs) else np.zeros(0, bool)
    res = dict(run=RUN, summary_columns=names, n_searches=int(len(hs)), n_finite=int(fin.sum()),
               search_times=[float(hs[0, col["time"]]), float(hs[-1, col["time"]])] if len(hs) else None)
    pd = PD.load(RUN, T)
    times = pd["times"]
    Ri = pd["sh"].R_i
    tauah_p = pd["sh"].tau_ah
    res["traj"] = dict(met_reclen=pd["met_reclen"], ntag=pd["ntag"], n_out=int(len(times)),
                       t_first=float(times[0]), t_last=float(times[-1]), tags_match_file=pd["tags_match_file"])
    # ------------------------------------------------ exact slice mass at every trajectory time
    slice_rows = []
    for k, t in enumerate(times):
        taup = pd["tau"][k]
        Dp = taup - tauah_p
        any_trapped = bool(np.any(Dp[np.isfinite(Dp)] >= 0))
        Rstar, R2, nb, _ = outermost_trapped(Ri, taup, curve, R1, R1 + 1.2)
        slice_rows.append(dict(t=float(t), any_tracked_trapped=any_trapped,
                               R_i_star=float(Rstar), R_i_star_quad=float(R2),
                               m_exact=float(m_of_R(Rstar)) if np.isfinite(Rstar) else np.nan,
                               m_exact_quad=float(m_of_R(R2)) if np.isfinite(R2) else np.nan))
    first_tr = next((r_ for r_ in slice_rows if r_["any_tracked_trapped"]), None)
    first_ex = next((r_ for r_ in slice_rows if np.isfinite(r_["m_exact"])), None)
    res["first_slice_with_trapped_tracked_particle"] = first_tr["t"] if first_tr else None
    res["first_slice_with_exact_horizon"] = first_ex["t"] if first_ex else None

    # ------------------------------------------------ horizon rows
    rows = []
    if fin.any():
        for i in np.nonzero(fin)[0]:
            t = hs[i, col["time"]]
            k = int(np.argmin(np.abs(times - t)))
            area = hs[i, col["area"]]
            mirr = np.sqrt(area / (16 * np.pi))
            sr = slice_rows[k]
            # areal radius of the coordinate sphere r = meanradius from the metric at the particles
            # (bin medians of R_p against r_p, linear interpolation): a check of the finder's area
            rpk, Rpk = pd["r"][k], pd["R"][k]
            okk = np.isfinite(rpk) & np.isfinite(Rpk)
            ob = np.argsort(rpk[okk])
            rr_, RR_ = rpk[okk][ob], Rpk[okk][ob]
            bins_ = np.arange(0, 1.5, 0.025)
            kb_ = np.digitize(rr_, bins_)
            xm_ = np.array([np.median(rr_[kb_ == q]) for q in np.unique(kb_)])
            ym_ = np.array([np.median(RR_[kb_ == q]) for q in np.unique(kb_)])
            R_part = float(np.interp(hs[i, col["meanradius"]], xm_, ym_))
            rows.append(dict(R_particles_at_rh=R_part, t=float(t), t_traj=float(times[k]), mass=float(hs[i, col["mass"]]), m_irr=float(mirr),
                             S=float(hs[i, col["S"]]), meanradius=float(hs[i, col["meanradius"]]),
                             minradius=float(hs[i, col["minradius"]]), hrms=float(hs[i, col["hrms"]]),
                             R_areal=float(2 * mirr), m_exact=sr["m_exact"], m_exact_quad=sr["m_exact_quad"],
                             R_i_star=sr["R_i_star"],
                             rel_err=float(mirr / sr["m_exact"] - 1) if np.isfinite(sr["m_exact"]) else np.nan,
                             rel_err_quad=float(mirr / sr["m_exact_quad"] - 1) if np.isfinite(sr["m_exact_quad"]) else np.nan))
        res["rows"] = rows
        t1 = rows[0]["t"]
        res["first_detection"] = rows[0]
        # gaps: are detections continuous after the first?
        tf = np.array([r_["t"] for r_ in rows])
        res["detections_after_first"] = dict(n=int(len(tf)), t_last=float(tf[-1]),
                                             largest_gap=float(np.max(np.diff(tf))) if len(tf) > 1 else None)
        w = np.array([r_["t"] <= t1 + 4.0 for r_ in rows])
        errs = np.array([r_["rel_err"] for r_ in rows])
        errq = np.array([r_["rel_err_quad"] for r_ in rows])
        res["median_rel_err_first_4M"] = float(np.nanmedian(errs[w]))
        res["median_abs_rel_err_first_4M"] = float(np.nanmedian(np.abs(errs[w])))
        res["max_abs_rel_err_first_4M"] = float(np.nanmax(np.abs(errs[w])))
        res["median_rel_err_first_4M_quad"] = float(np.nanmedian(errq[w]))
        res["n_rows_first_4M"] = int(w.sum())
        res["christodoulou_minus_irr_max"] = float(np.max(np.abs([r_["mass"] - r_["m_irr"] for r_ in rows])))
        # particles at the horizon at first detection
        k1 = int(np.argmin(np.abs(times - t1)))
        rh = rows[0]["meanradius"]
        rp = pd["r"][k1]
        Dp = pd["tau"][k1] - tauah_p
        ok = np.isfinite(rp) & np.isfinite(Dp)
        near = ok & (np.abs(rp - rh) < 0.0625)
        res["at_first_detection"] = dict(
            t=float(times[k1]), r_h=float(rh), n_near=int(near.sum()),
            D_near_mean=float(np.mean(Dp[near])) if near.any() else None,
            D_near_min=float(np.min(Dp[near])) if near.any() else None,
            D_near_max=float(np.max(Dp[near])) if near.any() else None,
            R_i_near=sorted(set(np.round(Ri[near], 3).tolist())) if near.any() else None,
            alpha_near_mean=float(np.nanmean(pd["alpha"][k1][near])) if near.any() else None,
            R_areal_near_mean=float(np.nanmean(pd["R"][k1][near])) if near.any() else None)
        # D interpolated at r_h from bin medians in r
        o = np.argsort(rp[ok])
        rr_, DD_ = rp[ok][o], Dp[ok][o]
        bins = np.arange(0, rr_.max() + 0.05, 0.05)
        kb = np.digitize(rr_, bins)
        xm = np.array([np.median(rr_[kb == q]) for q in np.unique(kb)])
        ym = np.array([np.median(DD_[kb == q]) for q in np.unique(kb)])
        res["at_first_detection"]["D_interp_at_r_h"] = float(np.interp(rh, xm, ym))
        # same over the first 4 M: D at the horizon radius
        Dh = []
        for r_ in rows:
            if r_["t"] > t1 + 4.0:
                break
            kk = int(np.argmin(np.abs(times - r_["t"])))
            rpk = pd["r"][kk]
            Dk = pd["tau"][kk] - tauah_p
            okk = np.isfinite(rpk) & np.isfinite(Dk) & (np.abs(rpk - r_["meanradius"]) < 0.0625)
            Dh.append([r_["t"], float(np.mean(Dk[okk])) if okk.any() else np.nan, int(okk.sum())])
        res["D_at_horizon_first_4M"] = Dh
        res["proper_time_of_edge_particles_at_first_detection"] = None
        edge = np.abs(Ri - R1) < 0.06
        res["edge_band"] = dict(n=int(edge.sum()), tau_ah_edge=tau_ah_edge,
                                tau_p_at_first_detection_mean=float(np.nanmean(pd["tau"][k1][edge])) if edge.any() else None)
    # ------------------------------------------------ snapshot cross-check (all particles)
    snaps = sorted(f for f in os.listdir(d) if f.startswith("ball.part.") and f.endswith(".bin"))
    s0 = V.read_snap(os.path.join(d, snaps[0]))
    order0 = np.argsort(s0["tag"])
    tag0 = s0["tag"][order0]
    r0 = np.sqrt(np.sum(s0["x"][order0] ** 2, axis=1))
    sel_lab = (r0 > b1 - 0.3) & (r0 < b1 + 1.0)
    shs = shells_from_table(T, r0[sel_lab])
    Ri_all = np.full(len(r0), np.nan)
    tah_all = np.full(len(r0), np.nan)
    Ri_all[sel_lab] = shs.R_i
    tah_all[sel_lab] = shs.tau_ah
    snaprows = []
    for f in snaps[1:]:
        s = V.read_snap(os.path.join(d, f))
        if s["t"] < 9.0:
            continue
        pos = np.searchsorted(tag0, s["tag"])
        Rk, tk = Ri_all[pos], s["tau"]
        ok = np.isfinite(Rk)
        Rstar, R2, nb, _ = outermost_trapped(Rk[ok], tk[ok], curve, R1, R1 + 0.9, binw=0.004)
        kt = int(np.argmin(np.abs(times - s["t"])))
        snaprows.append(dict(t=s["t"], n=int(s["n"]), R_i_star_all=float(Rstar), m_exact_all=float(m_of_R(Rstar)) if np.isfinite(Rstar) else np.nan,
                             R_i_star_tracked=slice_rows[kt]["R_i_star"], m_exact_tracked=slice_rows[kt]["m_exact"],
                             any_trapped_all=bool(np.any(tk[ok] - tah_all[pos][ok] >= 0))))
    res["snapshot_check"] = snaprows
    res["slice_rows"] = slice_rows
    with open(os.path.join(out, f"c3_horizon_{RUN}.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    # ------------------------------------------------ figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.95, wspace=0.33, hspace=0.42)
    ax = fig.add_subplot(2, 2, 1)
    ts_ = np.array([r_["t"] for r_ in slice_rows])
    me = np.array([r_["m_exact"] for r_ in slice_rows])
    mq = np.array([r_["m_exact_quad"] for r_ in slice_rows])
    ax.plot(ts_, me, color=fs.PAL["blue"], label=r"$m_{\rm exact}$(slice), tracked")
    ax.plot(ts_, mq, color=fs.PAL["blue"], ls=":", lw=1.0, label="same, quadratic fit")
    if snaprows:
        ax.plot([r_["t"] for r_ in snaprows], [r_["m_exact_all"] for r_ in snaprows], "s", color=fs.PAL["green"],
                ms=4, label="same, all particles (snapshots)")
    if rows:
        ax.plot([r_["t"] for r_ in rows], [r_["m_irr"] for r_ in rows], ".", color=fs.PAL["red"], ms=3,
                label=r"finder $\sqrt{A/16\pi}$")
        ax.axvline(rows[0]["t"], **fs.MASK_LINE)
    ax.set_xlabel(r"code time $t\,/M$")
    ax.set_ylabel(r"mass $/M$")
    ax.set_xlim(9, 16)
    ax.set_ylim(0.66, 0.74)
    ax.legend(fontsize=6.5, frameon=False, loc="lower right")
    ax.set_title(f"{RUN}: horizon mass", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    if rows:
        tr_ = np.array([r_["t"] for r_ in rows])
        ax.plot(tr_, [r_["rel_err"] for r_ in rows], ".", color=fs.PAL["red"], ms=3, label="tracked, linear")
        ax.plot(tr_, [r_["rel_err_quad"] for r_ in rows], ".", color=fs.PAL["orange"], ms=2, label="tracked, quadratic")
        ax.axhspan(-3e-3, 3e-3, color=fs.PAL["blue"], alpha=0.1)
        ax.axhline(0, **fs.THIN)
        ax.axvspan(rows[0]["t"], rows[0]["t"] + 4, color="grey", alpha=0.08)
        ax.legend(fontsize=7, frameon=False)
    ax.set_xlabel(r"code time $t\,/M$")
    ax.set_ylabel(r"$m_{\rm irr}/m_{\rm exact}-1$ (band: $\pm3\times10^{-3}$)")
    ax.set_title("relative horizon-mass error", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    if rows:
        k1 = int(np.argmin(np.abs(times - rows[0]["t"])))
        okp = np.isfinite(pd["tau"][k1])
        ax.plot(Ri[okp], pd["tau"][k1][okp], ".", ms=2, color=fs.PAL["red"], label=f"particles, $t$ = {times[k1]:.3f}")
        ax.plot(sh_c.R_i, sh_c.tau_ah, **fs.GUIDE, label=r"exact $\tau_{\rm AH}(R_i)$")
        core_r = np.linspace(0.05, b1, 200)
        shc = shells_from_table(T, core_r, side="in")
        ax.plot(shc.R_i, shc.tau_ah, color="k", lw=1.0, ls="--")
        if np.isfinite(rows[0]["R_i_star"]):
            ax.axvline(rows[0]["R_i_star"], **fs.MASK_LINE)
        ax.set_xlim(0, R1 + 1.0)
        ax.set_ylim(6, 14)
        ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_xlabel(r"shell label $R_i\,/M$")
    ax.set_ylabel(r"proper time $\tau\,/M$")
    ax.set_title("slice of the first detection", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    if rows:
        ax.plot([r_["t"] for r_ in rows], [r_["meanradius"] for r_ in rows], color=fs.PAL["red"], label="horizon mean $r$")
        ax.plot([r_["t"] for r_ in rows], [r_["minradius"] for r_ in rows], color=fs.PAL["red"], ls=":", lw=1.0,
                label="horizon min $r$")
    groups = [(R1 - 0.05, "R1-0.05"), (R1 + 0.05, "R1+0.05"), (R1 + 0.15, "R1+0.15"), (R1 + 0.3, "R1+0.3")]
    cc = fs.series_colors(len(groups), "viridis")
    for c_, (Rg, lab) in zip(cc, groups):
        sel = np.abs(Ri - Rg) < 0.01
        if sel.any():
            ax.plot(times, np.nanmedian(pd["r"][:, sel], axis=1), color=c_, lw=1.0, label=f"particles $R_i\\approx${Rg:.2f}")
    ax.set_xlim(8, 16)
    ax.set_ylim(0, 3)
    ax.set_xlabel(r"code time $t\,/M$")
    ax.set_ylabel(r"coordinate radius $/M$")
    ax.legend(fontsize=6.5, frameon=False)
    ax.set_title("coordinate radii", fontsize=10)
    fs.save(fig, os.path.join(out, f"fig_c3_horizon_{RUN}"))
    short = {k: v for k, v in res.items() if k not in ("rows", "slice_rows")}
    print(json.dumps(short, indent=1, default=float))


if __name__ == "__main__":
    main()
