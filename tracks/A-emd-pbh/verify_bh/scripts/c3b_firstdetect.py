#!/usr/bin/env python3
"""C3b: why is the first BH-1R horizon 2 per cent heavier than the exact slice mass?
Finder or field? (follow-up of run A-20261121-125512-6df0ee3, verify_bh JOURNAL entry 3)

(1) Field: the Misner-Sharp mass of the code's fields on the x line (adm table outputs every
    0.25 M), m_code(r) = (R/2)(1 + (R KT)^2 - |DR|^2) as in c4_lines.py, against the exact
    m(R_i) of the shells that sit at the same coordinate radius on the same slice (labels of
    the tracked particles, bin medians of R_i against r_p). Evaluated at the finder's mean
    radius r_h: if m_code(r_h) = m_irr the field carries the excess, if
    m_code(r_h) = m_exact the finder does.
(2) Areal radius at r_h from the metric at the tracked particles (R_p = r_p sqrt(B)) against
    the finder's sqrt(A/4 pi), at every finder time of the first 2 M.
(3) Exact areal radius R_exact(tau_p) of the particles' shells against the code R_p near r_h
    at the first detection (t = 10.875): is the code's sphere at r_h bigger than the exact
    one, and by how much?

Writes c3b_firstdetect.json and fig_c3b_firstdetect.{png,pdf} into $NRPIC_RUN_DIR.
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
from c4_lines import line_ms   # noqa: E402
from ltb import TableLTB, shells_from_table   # noqa: E402

RUN = "bh_smr"


def binned(x, y, edges):
    k = np.digitize(x, edges)
    xm, ym = [], []
    for q in np.unique(k):
        s = k == q
        if s.sum() >= 1:
            xm.append(np.median(x[s]))
            ym.append(np.median(y[s]))
    return np.array(xm), np.array(ym)


def main():
    warnings.simplefilter("ignore", RuntimeWarning)
    out = P.outdir()
    T = TableLTB(P.TABLE)
    b1, b2 = np.sort(T.breaks)
    d = P.RUN_DIR[RUN]
    names, hs = V.read_horizon_summary(os.path.join(d, "ball.horizon_summary_0.txt"))
    col = {n: k for k, n in enumerate(names)}
    fin = np.isfinite(hs[:, col["mass"]])
    ht, hm, hr = hs[fin, col["time"]], hs[fin, col["mass"]], hs[fin, col["meanradius"]]
    hmirr = np.sqrt(hs[fin, col["area"]] / (16 * np.pi))
    pd = PD.load(RUN, T)
    times = pd["times"]
    Ri = pd["sh"].R_i
    m_lab = pd["sh"].m                       # exact Misner-Sharp mass of each tracked particle's shell
    res = dict(run=RUN, finder_first=float(ht[0]))

    # ------------------------------------------------ (1) field mass on the line
    files = V.tabout_series(os.path.join(d, "tab"), "adm")
    line_rows, line_plot = [], {}
    for f in files:
        adm = V.read_tabout(f)
        t = adm["time"]
        if t < 10.0 or t > 13.0:
            continue
        L = line_ms(adm, RUN)
        mcode = 0.5 * L["R"] * L["two_m_over_R"]
        k = int(np.argmin(np.abs(times - t)))
        ok = np.isfinite(pd["r"][k])
        xm, ym = binned(pd["r"][k][ok], m_lab[ok], np.arange(0, 3.0, 0.02))
        pos = L["x"] > 0
        neg = L["x"] < 0
        o_p = np.argsort(L["r"][pos])
        o_n = np.argsort(L["r"][neg])
        rp_, mp_ = L["r"][pos][o_p], mcode[pos][o_p]
        rn_, mn_ = L["r"][neg][o_n], mcode[neg][o_n]
        row = dict(t=float(t))
        j = np.nonzero(np.isclose(ht, t))[0]
        if len(j):
            r_h = float(hr[j[0]])
            row.update(r_h=r_h, m_irr=float(hmirr[j[0]]),
                       m_code_at_rh_xpos=float(np.interp(r_h, rp_, mp_)),
                       m_code_at_rh_xneg=float(np.interp(r_h, rn_, mn_)),
                       m_exact_at_rh=float(np.interp(r_h, xm, ym)))
        # largest relative excess of the field mass over the exact shell mass for 0.3 < r < 1.0
        sel = (rp_ > 0.3) & (rp_ < 1.0)
        rel = mp_[sel] / np.interp(rp_[sel], xm, ym) - 1
        row["field_mass_rel_err_0.3_1.0"] = dict(r=rp_[sel].tolist(), rel=rel.tolist())
        line_rows.append(row)
        line_plot[t] = (rp_, mp_, xm, ym)
    res["line"] = line_rows

    # ------------------------------------------------ (2) areal radius at r_h from the particles
    part_rows = []
    for t, rh, mi in zip(ht, hr, hmirr):
        if t > ht[0] + 2.0:
            break
        k = int(np.argmin(np.abs(times - t)))
        ok = np.isfinite(pd["r"][k]) & np.isfinite(pd["R"][k])
        xm, ym = binned(pd["r"][k][ok], pd["R"][k][ok], np.arange(0, 3.0, 0.02))
        # local quadratic fit of R_p(r_p) within 0.1 of r_h (independent of the bins)
        near = ok & (np.abs(pd["r"][k] - rh) < 0.1)
        Rq = np.nan
        if near.sum() >= 6:
            c = np.polyfit(pd["r"][k][near] - rh, pd["R"][k][near], 2)
            Rq = float(c[-1])
        part_rows.append(dict(t=float(t), t_traj=float(times[k]), r_h=float(rh), R_finder=float(2 * mi),
                              R_particles_binned=float(np.interp(rh, xm, ym)), R_particles_quadfit=Rq,
                              n_near=int(near.sum())))
    res["areal_radius_at_rh"] = part_rows

    # ------------------------------------------------ (3) code R against exact R near r_h at first detection
    t1 = float(ht[0])
    k1 = int(np.argmin(np.abs(times - t1)))
    Rex = PD.r_exact_at_own_tau(pd)[k1]
    ok = np.isfinite(pd["r"][k1]) & np.isfinite(Rex) & (Rex > 0)
    near = ok & (np.abs(pd["r"][k1] - hr[0]) < 0.1)
    res["first_detection_particles"] = dict(
        t=float(times[k1]), r_h=float(hr[0]), n=int(near.sum()),
        r=pd["r"][k1][near].tolist(), R_code=pd["R"][k1][near].tolist(), R_exact=Rex[near].tolist(),
        R_i=Ri[near].tolist(), two_m_exact_over_R_code=(2 * m_lab[near] / pd["R"][k1][near]).tolist(),
        two_m_exact_over_R_exact=(2 * m_lab[near] / Rex[near]).tolist(),
        eps_median=float(np.median(pd["R"][k1][near] / Rex[near] - 1)) if near.any() else None)
    with open(os.path.join(out, "c3b_firstdetect.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    # ------------------------------------------------ figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.95, wspace=0.34, hspace=0.42)
    ax = fig.add_subplot(2, 2, 1)
    sel_t = [t for t in sorted(line_plot) if t in (10.5, 10.75, 11.0, 11.25, 11.5, 12.0)]
    cc = fs.series_colors(len(sel_t), "viridis")
    for c_, t in zip(cc, sel_t):
        rp_, mp_, xm, ym = line_plot[t]
        ax.plot(rp_, mp_, color=c_, lw=1.2, label=f"code, $t$ = {t:g}")
        ax.plot(xm, ym, color=c_, lw=0.8, ls=":")
    ax.plot(hr[ht <= 12.0], hmirr[ht <= 12.0], "o", color=fs.PAL["red"], ms=3, label=r"finder $(r_h, m_{\rm irr})$")
    ax.set_xlim(0.25, 0.9)
    ax.set_ylim(0.60, 0.76)
    ax.set_xlabel(r"coordinate radius $r\,/M$ ($x$ line)")
    ax.set_ylabel(r"Misner-Sharp mass $/M$ (dotted: exact shells)")
    ax.legend(fontsize=6, frameon=False, ncol=1, loc="lower right")
    ax.set_title("field mass near the forming horizon", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    lr = [r_ for r_ in line_rows if "r_h" in r_]
    tt = [r_["t"] for r_ in lr]
    ax.plot(tt, [r_["m_irr"] / r_["m_exact_at_rh"] - 1 for r_ in lr], "o-", color=fs.PAL["red"], ms=3,
            label=r"finder $m_{\rm irr}$")
    ax.plot(tt, [r_["m_code_at_rh_xpos"] / r_["m_exact_at_rh"] - 1 for r_ in lr], "s-", color=fs.PAL["blue"],
            ms=3, label=r"field $m(r_h)$, $x>0$")
    ax.plot(tt, [r_["m_code_at_rh_xneg"] / r_["m_exact_at_rh"] - 1 for r_ in lr], "^--", color=fs.PAL["green"],
            ms=3, label=r"field $m(r_h)$, $x<0$")
    ax.axhline(0, **fs.THIN)
    ax.set_xlabel(r"code time $t\,/M$")
    ax.set_ylabel(r"relative to exact $m$ of the shell at $r_h$")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("finder or field?", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    ax.plot([r_["t"] for r_ in part_rows], [r_["R_finder"] for r_ in part_rows], "o", color=fs.PAL["red"], ms=3,
            label=r"finder $\sqrt{A/4\pi}$")
    ax.plot([r_["t"] for r_ in part_rows], [r_["R_particles_binned"] for r_ in part_rows], "-", color=fs.PAL["blue"],
            label=r"$R_p(r_h)$, bin medians")
    ax.plot([r_["t"] for r_ in part_rows], [r_["R_particles_quadfit"] for r_ in part_rows], ":", color="k",
            label=r"$R_p(r_h)$, local quadratic")
    ax.set_xlabel(r"code time $t\,/M$")
    ax.set_ylabel(r"areal radius at $r_h$ $/M$")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("area check from the particles", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    fd = res["first_detection_particles"]
    ax.plot(fd["r"], fd["R_code"], ".", color=fs.PAL["red"], ms=4, label=r"code $R_p$")
    ax.plot(fd["r"], fd["R_exact"], ".", color=fs.PAL["blue"], ms=4, label=r"exact $R(\tau_p)$ of the shell")
    ax.plot(fd["r"], 2 * m_lab[near], "x", color="k", ms=3, label=r"$2m$ of the shell")
    ax.axvline(hr[0], **fs.MASK_LINE)
    ax.axhline(2 * hmirr[0], **fs.GUIDE)
    ax.set_xlabel(r"particle coordinate radius $r_p\,/M$")
    ax.set_ylabel(r"areal radius $/M$")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title(f"particles near $r_h$ at $t$ = {fd['t']:g}", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_c3b_firstdetect"))
    short = dict(res)
    short["line"] = [{k: v for k, v in r_.items() if k != "field_mass_rel_err_0.3_1.0"} for r_ in line_rows]
    print(json.dumps(short, indent=1, default=float)[:12000])


if __name__ == "__main__":
    main()
