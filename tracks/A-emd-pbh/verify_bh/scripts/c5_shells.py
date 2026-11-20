#!/usr/bin/env python3
"""C5: core-shell errors |R/R_exact - 1| of the tracked particles at proper times 3.37 and 9.0
in BH-1R and BH-1 (M/8; also M/6, M/4), plus per-particle turnaround and trapping times.

R of a particle: areal radius of the coordinate sphere through it, r sqrt(B), B the tangential
eigenvalue of gamma_ij at the particle (trajmet). R_exact: cycloid of the particle's shell
(label from its t = 0 position and the table) at the particle's own proper time.

Writes c5_shells.json and fig_c5_shells.{png,pdf} into $NRPIC_RUN_DIR.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs          # noqa: E402
import vbpaths as P            # noqa: E402
import partdata as PD          # noqa: E402
from ltb import TableLTB       # noqa: E402

RUNS = ["bh_smr", "bh_n256", "bh_n192", "bh_n128"]
TAU_TA = 3.3716      # checked by c1_exact.py (core turnaround of my LTB)


def interp_at_tau(tau_row, val_row, tq):
    ok = np.isfinite(tau_row) & np.isfinite(val_row)
    if ok.sum() < 2 or tau_row[ok].max() < tq:
        return np.nan
    return float(np.interp(tq, tau_row[ok], val_row[ok]))


def main():
    warnings.simplefilter("ignore", RuntimeWarning)
    out = P.outdir()
    T = TableLTB(P.TABLE)
    b1, b2 = np.sort(T.breaks)
    R1 = float(T.slice(np.array([b1]), side="in")["R"][0])
    res = dict(tau_ta_exact=TAU_TA)
    plots = {}
    for run in RUNS:
        pd = PD.load(run, T)
        Rex = PD.r_exact_at_own_tau(pd)
        eps = pd["R"] / Rex - 1.0
        core = pd["rbar_i"] < b1
        rr = dict(n_core=int(core.sum()), n_track=int(pd["ntag"]))
        rr["eps_t0_core_max"] = float(np.nanmax(np.abs(eps[0][core])))
        rr["eps_t0_all_max"] = float(np.nanmax(np.abs(eps[0])))
        for tq in (TAU_TA, 6.0, 9.0):
            e = np.array([interp_at_tau(pd["tau"][:, j], eps[:, j], tq) for j in np.nonzero(core)[0]])
            fin = np.isfinite(e)
            rr[f"tau{tq:g}"] = dict(n=int(fin.sum()), max_abs=float(np.nanmax(np.abs(e))) if fin.any() else None,
                                    p99_abs=float(np.nanpercentile(np.abs(e), 99)) if fin.any() else None,
                                    median=float(np.nanmedian(e)) if fin.any() else None,
                                    R_i_of_max=float(pd["sh"].R_i[np.nonzero(core)[0]][np.nanargmax(np.abs(e))]) if fin.any() else None)
            if tq == TAU_TA:
                plots.setdefault(run, {})["ta"] = (pd["sh"].R_i[core], e)
            if tq == 9.0:
                plots.setdefault(run, {})["t9"] = (pd["sh"].R_i[core], e)
        # per-particle turnaround: maximum of R_p along the track, parabola through the top three points
        dta, drm = [], []
        for j in np.nonzero(core)[0]:
            tt, RR = pd["tau"][:, j], pd["R"][:, j]
            ok = np.isfinite(tt) & np.isfinite(RR)
            tt, RR = tt[ok], RR[ok]
            if len(tt) < 5:
                continue
            k = int(np.argmax(RR))
            if k == 0 or k == len(tt) - 1:
                continue
            c = np.polyfit(tt[k - 1:k + 2] - tt[k], RR[k - 1:k + 2], 2)
            tmax = tt[k] - c[1] / (2 * c[0])
            Rm = np.polyval(c, tmax - tt[k])
            dta.append(tmax - pd["sh"].tau_ta[j])
            drm.append(Rm / pd["sh"].R_max[j] - 1)
        dta, drm = np.array(dta), np.array(drm)
        rr["turnaround"] = dict(n=int(len(dta)), dtau_mean=float(np.mean(dta)), dtau_std=float(np.std(dta)),
                                dtau_maxabs=float(np.max(np.abs(dta))), dRmax_mean=float(np.mean(drm)),
                                dRmax_maxabs=float(np.max(np.abs(drm))))
        # per-particle trapping: proper time at which R_p falls through 2 m(R_i) (exact m)
        dah = []
        for j in np.nonzero((pd["sh"].R_i > R1 - 0.1) & (pd["sh"].R_i < R1 + 0.35))[0]:
            tt, RR = pd["tau"][:, j], pd["R"][:, j]
            ok = np.isfinite(tt) & np.isfinite(RR)
            tt, RR = tt[ok], RR[ok]
            f = RR - 2 * pd["sh"].m[j]
            cr = np.nonzero((f[:-1] > 0) & (f[1:] <= 0))[0]
            if len(cr) == 0:
                continue
            q = cr[0]
            tc = tt[q] + f[q] / (f[q] - f[q + 1]) * (tt[q + 1] - tt[q])
            dah.append((pd["sh"].R_i[j], tc - pd["sh"].tau_ah[j]))
        dah = np.array(dah) if dah else np.zeros((0, 2))
        rr["trapping"] = dict(n=int(len(dah)),
                              edge_band_mean=float(np.mean(dah[np.abs(dah[:, 0] - (R1 - 0.05)) < 0.02, 1])) if len(dah) and np.any(np.abs(dah[:, 0] - (R1 - 0.05)) < 0.02) else None,
                              outer_band_mean=float(np.mean(dah[np.abs(dah[:, 0] - (R1 + 0.05)) < 0.02, 1])) if len(dah) and np.any(np.abs(dah[:, 0] - (R1 + 0.05)) < 0.02) else None,
                              all_mean=float(np.mean(dah[:, 1])) if len(dah) else None,
                              all_std=float(np.std(dah[:, 1])) if len(dah) else None)
        plots[run]["trap"] = dah
        # median and largest |eps| of core particles against proper time (for the figure)
        taugrid = np.linspace(0, 10.5, 106)
        E = np.array([[interp_at_tau(pd["tau"][:, j], eps[:, j], tq) for tq in taugrid] for j in np.nonzero(core)[0]])
        plots[run]["curve"] = (taugrid, np.nanmax(np.abs(E), axis=0), np.nanmedian(np.abs(E), axis=0))
        if run == "bh_smr":
            k1 = int(np.argmin(np.abs(pd["times"] - 10.875)))
            edge = np.abs(pd["sh"].R_i - R1) < 0.06
            rr["edge_band_at_t10.875"] = dict(eps_median=float(np.nanmedian(eps[k1][edge])),
                                             eps_min=float(np.nanmin(eps[k1][edge])),
                                             eps_max=float(np.nanmax(eps[k1][edge])),
                                             n=int(np.isfinite(eps[k1][edge]).sum()))
        res[run] = rr
    with open(os.path.join(out, "c5_shells.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    fs.use_style()
    import matplotlib.pyplot as plt
    lab = {"bh_smr": "BH-1R (M/16)", "bh_n256": "BH-1 M/8", "bh_n192": "BH-1 M/6", "bh_n128": "BH-1 M/4"}
    cols = {"bh_smr": fs.PAL["red"], "bh_n256": fs.PAL["blue"], "bh_n192": fs.PAL["green"], "bh_n128": fs.PAL["orange"]}
    fig = plt.figure(figsize=(8.0, 6.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.95, wspace=0.32, hspace=0.42)
    ax = fig.add_subplot(2, 2, 1)
    for run in RUNS:
        tg, mx, md = plots[run]["curve"]
        ax.semilogy(tg, mx, color=cols[run], label=lab[run])
        ax.semilogy(tg, md, color=cols[run], ls=":", lw=1.0)
    ax.axvline(TAU_TA, **fs.MASK_LINE)
    ax.axvline(9.0, **fs.MASK_LINE)
    ax.plot([TAU_TA], [1.5e-3], "v", color=fs.PAL["red"], ms=5)
    ax.plot([TAU_TA, 9.0], [2e-3, 2e-2], "v", color=fs.PAL["blue"], ms=5)
    ax.set_xlabel(r"proper time $\tau\,/M$")
    ax.set_ylabel(r"core $|R/R_{\rm exact}-1|$ (solid max, dotted median)")
    ax.set_ylim(1e-6, 1)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title(r"core shells (triangles: claimed bounds)", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    for run in RUNS:
        Ri, e = plots[run]["ta"]
        ax.plot(Ri, e, ".", ms=2, color=cols[run], label=lab[run])
    ax.axhline(0, **fs.THIN)
    ax.set_xlabel(r"shell label $R_i\,/M$ (core)")
    ax.set_ylabel(r"$R/R_{\rm exact}-1$ at $\tau=3.3716$")
    ax.set_ylim(-0.01, 0.01)
    ax.legend(fontsize=7, frameon=False, markerscale=4)
    ax.set_title("at the turnaround", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    for run in RUNS:
        Ri, e = plots[run]["t9"]
        ax.plot(Ri, e, ".", ms=2, color=cols[run], label=lab[run])
    ax.axhline(0, **fs.THIN)
    ax.set_xlabel(r"shell label $R_i\,/M$ (core)")
    ax.set_ylabel(r"$R/R_{\rm exact}-1$ at $\tau=9.0$")
    ax.set_ylim(-0.1, 0.1)
    ax.set_title(r"at $\tau=9.0$", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    for run in RUNS:
        d = plots[run]["trap"]
        if len(d):
            ax.plot(d[:, 0], d[:, 1], ".", ms=3, color=cols[run], label=lab[run])
    ax.axhline(0, **fs.THIN)
    ax.axvline(R1, **fs.MASK_LINE)
    ax.set_xlabel(r"shell label $R_i\,/M$")
    ax.set_ylabel(r"$\tau(R=2m)-\tau_{\rm AH}^{\rm exact}\,/M$")
    ax.legend(fontsize=7, frameon=False, markerscale=2)
    ax.set_title("per-particle trapping time", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_c5_shells"))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
