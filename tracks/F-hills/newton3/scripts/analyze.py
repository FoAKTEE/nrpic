"""Analysis and figures of the newton3 runs; each call is a registered analysis run.

    python3 scripts/analyze.py coplanar <run_id>   P1 (scan_coplanar.py output)
    python3 scripts/analyze.py general  <run_id>   P2 (scan_general.py output)
    python3 scripts/analyze.py p3       <run_id>   P3 (compare_full.py p3)
    python3 scripts/analyze.py p4       <run_id>   P4 (compare_full.py p4)
    python3 scripts/analyze.py finiteq  <run_id>   finite mass ratio (compare_full.py finiteq)
    python3 scripts/analyze.py example            driver demonstration at M/m = 10

Figures go to the run directory and are copied to ../figures/; the numbers to
<run dir>/summary_<name>.json and ../results/<name>.json.
"""
import json
import os
import shutil
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "..", "..", "..", "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from hills3 import reference as ref  # noqa: E402
from hills3 import threebody as T  # noqa: E402
import runlib  # noqa: E402

fs.use_style()
FIG = os.path.join(PKG, "figures")
D_TRUST = 1e-3   # rtol 1e-10 results below this D are not converged (JOURNAL P5)
RES = os.path.join(PKG, "results")
RED, BLUE, YEL, GRN, ORA = fs.PAL["red"], fs.PAL["blue"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]


def _src(run_id, name):
    return os.path.join(runlib.SCRATCH, run_id, name)


def _save(fig, run, name):
    files = fs.save(fig, os.path.join(run["dir"], name))
    os.makedirs(FIG, exist_ok=True)
    for f in files:
        shutil.copy(f, FIG)
    plt.close(fig)


def _summary(run, name, d):
    with open(os.path.join(run["dir"], f"summary_{name}.json"), "w") as fh:
        json.dump(d, fh, indent=2)
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, f"{name}.json"), "w") as fh:
        json.dump(d, fh, indent=2)


def _windows(phase, mask):
    """Contiguous runs of True in mask over the sampled phases -> list of (lo, hi)."""
    out, i, n = [], 0, mask.size
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            out.append((float(phase[i]), float(phase[j])))
            i = j + 1
        else:
            i += 1
    return out


# ============================================================================ P1
def coplanar(run_id, supplement_run=None):
    src = _src(run_id, "coplanar.npz")
    extra = [src] + ([_src(supplement_run, "coplanar.npz")] if supplement_run else [])
    run = runlib.start_run(f"analysis of {run_id} (P1 coplanar)"
                           + (f" with deep supplement {supplement_run}" if supplement_run else ""),
                           extra_inputs=extra, preregistered="tracks/F-hills/newton3/JOURNAL.md#P1")
    Z0 = np.load(src)
    keep = Z0["D"] >= D_TRUST * (1 - 1e-9)
    perD = [k for k in Z0.files if k.rsplit("_", 1)[-1] in ("pro", "ret")]
    Z = {k: np.asarray(Z0[k])[keep] for k in perD}
    D, ph = Z0["D"][keep], Z0["phase_skr"]
    if supplement_run:
        Y = np.load(_src(supplement_run, "coplanar.npz"))
        D = np.concatenate([Y["D"], D])
        Z = {k: np.concatenate([Y[k], Z[k]]) for k in perD}
        o = np.argsort(D)
        D = D[o]
        Z = {k: v[o] for k, v in Z.items()}
    S = {"source_run": run_id, "supplement_run": supplement_run, "phases_per_D": int(ph.size),
         "phase_range": "[0, pi)", "main_run_used_for_D_at_least": D_TRUST,
         "reason": "rtol 1e-10 not converged below 1e-3 (JOURNAL P5); deep points from the "
                   "rtol 1e-13 supplement", "D_grid": [float(x) for x in D]}
    stat = {}
    for tag in ("pro", "ret"):
        ok, dis, E = Z[f"ok_{tag}"], Z[f"disrupted_{tag}"], Z[f"E2_{tag}"]
        sv, amb, af = Z[f"survived_{tag}"], Z[f"ambiguous_{tag}"], Z[f"af_{tag}"]
        P = np.array([dis[i][ok[i]].mean() for i in range(D.size)])
        Em = np.array([np.abs(E[i][dis[i] & ok[i]]).mean() if (dis[i] & ok[i]).any() else np.nan
                       for i in range(D.size)])
        Ex = np.array([np.abs(E[i][dis[i] & ok[i]]).max() if (dis[i] & ok[i]).any() else np.nan
                       for i in range(D.size)])
        Vm = np.array([np.sqrt(np.abs(E[i][dis[i] & ok[i]])).mean() if (dis[i] & ok[i]).any()
                       else np.nan for i in range(D.size)])
        stat[tag] = dict(P=P, Em=Em, Ex=Ex, Vm=Vm)
        has = np.where(P > 0)[0]
        imax = has.max()
        S[tag] = {
            "Dmax_last_disrupting": float(D[imax]),
            "Dmax_first_nondisrupting": float(D[imax + 1]) if imax + 1 < D.size else None,
            "P_at_Dmin": float(P[0]), "D_min": float(D[0]),
            "survival_deep": float(1 - P[0]),
            "P_max": float(P.max()), "D_at_P_max": float(D[np.argmax(P)]),
            "Emax": float(np.nanmax(Ex)), "D_at_Emax": float(D[np.nanargmax(Ex)]),
            "Emean_deep": float(Em[0]), "vmean_deep": float(Vm[0]),
            "n_fail": int((~ok).sum()), "n_ambiguous": int((amb & ok).sum()),
            "n_total": int(ok.size),
            "survivors_harder_deep": float((af[0][sv[0] & ok[0]] < 1).mean()),
        }
        i4 = int(np.argmin(np.abs(np.log(D / 1e-4))))
        S[tag]["at_D=1e-4"] = {"D": float(D[i4]), "P": float(P[i4]), "Emean": float(Em[i4]),
                               "vmean": float(Vm[i4]), "survival": float(1 - P[i4]),
                               "survivors_harder": float((af[i4][sv[i4] & ok[i4]] < 1).mean()),
                               "survival_windows_pi": None}
        w4 = _windows(ph / np.pi, sv[i4] & ok[i4])
        S[tag]["at_D=1e-4"]["survival_windows_pi"] = w4 + [(lo - 1, hi - 1) for lo, hi in w4]
        sel = (D > 0.06) & (D < 0.3)
        S[tag]["P_range_0.06_0.3"] = [float(P[sel].min()), float(P[sel].max())]
        # survival windows at the deepest D, in SKR's phase, mapped to [-pi, pi)
        w = _windows(ph / np.pi, sv[0] & ok[0])
        S[tag]["survival_windows_deep_pi"] = w + [(lo - 1, hi - 1) for lo, hi in w]
        # averages with D uniformly distributed (SKR prp.tex:850-853, definition not stated)
        lin = D >= 0.0399
        Dl = np.concatenate([[0.0], D[lin]])
        Pl = np.concatenate([[P[0]], P[lin]])
        El = np.concatenate([[Em[0]], np.nan_to_num(Em[lin])])
        for top, lab in ((2.1, "0_2.1"), (float(D[imax + 1]) if imax + 1 < D.size else 2.3, "0_Dmax")):
            m = Dl <= top + 1e-9
            num = np.trapezoid(Pl[m] * El[m], Dl[m])
            den = np.trapezoid(Pl[m], Dl[m])
            S[tag][f"Emean_Duniform_disrupted_weighted_{lab}"] = float(num / den)
            S[tag][f"_num_{lab}"], S[tag][f"_den_{lab}"] = float(num), float(den)
            mm = m & (Pl > 0)
            S[tag][f"Emean_Duniform_unweighted_{lab}"] = float(
                np.trapezoid(El[mm], Dl[mm]) / (Dl[mm].max() - Dl[mm].min()))
    for lab in ("0_2.1", "0_Dmax"):
        S[f"Emean_Duniform_both_weighted_{lab}"] = float(
            (S["pro"][f"_num_{lab}"] + S["ret"][f"_num_{lab}"])
            / (S["pro"][f"_den_{lab}"] + S["ret"][f"_den_{lab}"]))
    S["P_both_mean_deep"] = float(0.5 * (stat["pro"]["P"][0] + stat["ret"]["P"][0]))
    S["reference"] = {k: [str(v[0]), v[1]] for k, v in ref.SKR.items()}
    _summary(run, "coplanar", S)

    # ---- figure: probability and energies vs D
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.25, 7.2), sharex=True)
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.07, top=0.98, hspace=0.06)
    Dp = np.where(D > 0, D, np.nan)
    for tag, ls, lab in (("pro", "-", "prograde"), ("ret", "--", "retrograde")):
        axs[0].plot(Dp, stat[tag]["P"], color=RED, ls=ls, label=f"this work, {lab}")
        axs[1].plot(Dp, stat[tag]["Em"], color=RED, ls=ls)
        axs[2].plot(Dp, stat[tag]["Ex"], color=RED, ls=ls)
    axs[0].plot(Dp, 0.5 * (stat["pro"]["P"] + stat["ret"]["P"]), color=YEL, ls="-", lw=1.0,
                label="this work, mean")
    a = axs[0]
    a.axvline(2.1, color=BLUE, lw=1.0, ls="-")
    a.axvline(0.44, color=BLUE, lw=1.0, ls="--")
    a.axhspan(0.79, 0.81, xmin=0, xmax=0.45, color=BLUE, alpha=0.2)
    a.fill_between([0.06, 0.3], 0.980, 0.988, color=BLUE, alpha=0.4, lw=0)
    a.plot([0.15], [0.984], "o", color=BLUE, ms=4, label="SKR printed values")
    a.set_ylabel(r"$P_{\rm dis}$")
    a.set_ylim(0, 1.05)
    a.legend(loc="lower left", fontsize=8)
    axs[1].set_ylabel(r"$\langle |E| \rangle$")
    axs[1].axhline(0.99 ** 2, color="grey", lw=0.8, alpha=0.4)
    axs[2].set_yscale("log")
    axs[2].plot([0.1], [27.3], "o", color=BLUE, ms=4)
    axs[2].axhline(1.8, color=BLUE, lw=1.0, ls="--")
    axs[2].set_ylabel(r"$\max |E|$")
    axs[2].set_xscale("log")
    axs[2].set_xlabel(r"$D = r_p / r_t$", labelpad=-1)
    axs[2].set_xlim(8e-5, 3)
    _save(fig, run, "fig_coplanar_pdis_energy")

    # ---- figure: energy vs phase in the deep limit (SKR fig. 6 analogue)
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.25, 3.2))
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.15, top=0.97)
    phf = np.concatenate([ph - np.pi, ph]) / np.pi
    picks = [(1e-4, RED, "-"), (1e-2, GRN, "-."), (0.03, "k", "--")]
    Dl = list(D)
    for Dv, col, ls in picks:
        i = int(np.argmin(np.abs(np.log(D) - np.log(Dv))))
        E = Z["E2_pro"][i].astype(float)
        m = Z["disrupted_pro"][i] & Z["ok_pro"][i]
        Ef = np.concatenate([-E, E])
        mf = np.concatenate([m, m])
        ax.plot(phf, np.where(mf, Ef, np.nan), color=col, ls=ls, lw=1.0, label=f"D = {D[i]:.3g}")
    for lo, hi in ref.SKR["survival_windows_radial_pi"][0]:
        ax.axvspan(lo, hi, color=BLUE, alpha=0.15)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-4, 4)
    ax.set_xlabel(r"effective phase $\phi/\pi$ (SKR convention, prograde)")
    ax.set_ylabel(r"$E_2$")
    ax.legend(loc="upper left", fontsize=8, ncol=3)
    ax.text(0.985, 0.04, "shaded: SKR survival windows (radial limit)", transform=ax.transAxes,
            ha="right", fontsize=8, color=BLUE)
    _save(fig, run, "fig_coplanar_phase_deep")

    # ---- figure: energy map in (phase, D) (SKR fig. 5 analogue)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.9, bottom=0.14, top=0.92, wspace=0.05)
    sel = D >= 0.01
    Ds = D[sel]
    edges = np.sqrt(Ds[1:] * Ds[:-1])
    edges = np.concatenate([[Ds[0] ** 2 / edges[0]], edges, [Ds[-1] ** 2 / edges[-1]]])
    phe = np.linspace(-1, 1, 2 * ph.size + 1)
    for ax, tag, title in ((axs[0], "pro", "prograde"), (axs[1], "ret", "retrograde")):
        E = Z[f"E2_{tag}"][sel].astype(float)
        m = Z[f"disrupted_{tag}"][sel] & Z[f"ok_{tag}"][sel]
        Ef = np.concatenate([-E, E], axis=1)
        mf = np.concatenate([m, m], axis=1)
        img = np.ma.masked_where(~mf, Ef)
        cm = plt.get_cmap("RdBu_r").copy()
        cm.set_bad("0.75")
        pc = ax.pcolormesh(phe, edges, img, cmap=cm, vmin=-3, vmax=3, rasterized=True)
        ax.set_yscale("log")
        ax.set_title(title)
        ax.set_xlabel(r"$\phi/\pi$ (SKR convention)")
    axs[0].set_ylabel(r"$D$")
    cax = fs.inch_axes(fig, 7.3, 0.48, 0.1, 2.65)
    fig.colorbar(pc, cax=cax, label=r"$E_2$ (grey: survives)", extend="both")
    _save(fig, run, "fig_coplanar_energy_map")
    runlib.finish_run(run, results={k: S[k] for k in ("pro", "ret")})
    return S


# ============================================================================ P2
def general(run_id, coplanar_run=None, supplement_run=None):
    src = _src(run_id, "general.npz")
    extra = [src]
    if coplanar_run:
        extra.append(_src(coplanar_run, "coplanar.npz"))
    if supplement_run:
        extra.append(_src(supplement_run, "general.npz"))
    run = runlib.start_run(f"analysis of {run_id} (P2 general orientation)", extra_inputs=extra,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P2")
    Z = np.load(src)
    kA = Z["D_A"] >= D_TRUST * (1 - 1e-9)
    D = Z["D_A"][kA]
    ok, dis, E, rmin = Z["ok_A"][kA], Z["disrupted_A"][kA], Z["E2_A"][kA], Z["rmin_A"][kA]
    P = np.array([dis[i][ok[i]].mean() for i in range(D.size)])
    Em = np.array([np.abs(E[i][dis[i] & ok[i]]).mean() if (dis[i] & ok[i]).any() else np.nan
                   for i in range(D.size)])
    E99 = np.array([np.percentile(np.abs(E[i][dis[i] & ok[i]]), 99) if (dis[i] & ok[i]).any()
                    else np.nan for i in range(D.size)])
    Pc = np.array([(rmin[i][ok[i]] < 0.2).mean() for i in range(D.size)])
    Pfit, Efit = ref.bkrs_pdis(D), ref.bkrs_emean(D)
    S = {"source_run": run_id, "N_ori": int(Z["theta_A"].size), "N_pha": int(Z["phase_A"].size),
         "sampling": "Fibonacci lattice on the whole sphere x equally spaced phases in [0, pi)",
         "D": D.tolist(), "P_dis": P.tolist(), "P_fit_BKRS": Pfit.tolist(),
         "P_minus_fit": (P - Pfit).tolist(), "Emean": Em.tolist(), "Emean_fit_BKRS": Efit.tolist(),
         "Emean_rel_dev": (Em / Efit - 1).tolist(), "E_top1pc": E99.tolist(),
         "P_collision_rmin_lt_0.2a": Pc.tolist(), "n_fail": int((~ok).sum()),
         "n_ambiguous": int((Z["ambiguous_A"][kA] & ok).sum()), "n_total": int(ok.size)}
    m1 = D <= 1.0 + 1e-9
    m18 = D <= 1.8 + 1e-9
    m15 = D <= 1.5 + 1e-9
    S["max_abs_P_minus_fit_D<=1"] = float(np.nanmax(np.abs(P - Pfit)[m1]))
    S["max_abs_P_minus_fit_D<=1.8"] = float(np.nanmax(np.abs(P - Pfit)[m18]))
    S["max_abs_Emean_rel_dev_D<=1"] = float(np.nanmax(np.abs(Em / Efit - 1)[m1]))
    S["max_abs_Emean_rel_dev_D<=1.5"] = float(np.nanmax(np.abs(Em / Efit - 1)[m15]))
    S["Dmax_last_disrupting"] = float(D[np.where(P > 0)[0].max()])
    # part B: inclination (D below D_TRUST discarded; supplement run merged in)
    th = Z["theta_B"]
    kB = Z["D_B"] >= D_TRUST * (1 - 1e-9)
    DB, okB, disB, EB = Z["D_B"][kB], Z["ok_B"][kB], Z["disrupted_B"][kB], Z["E2_B"][kB]
    if supplement_run:
        Y = np.load(_src(supplement_run, "general.npz"))
        dup = np.isin(DB, Y["D_B"])
        DB, okB, disB, EB = DB[~dup], okB[~dup], disB[~dup], EB[~dup]
        DB = np.concatenate([Y["D_B"], DB])
        okB = np.concatenate([Y["ok_B"], okB])
        disB = np.concatenate([Y["disrupted_B"], disB])
        EB = np.concatenate([Y["E2_B"], EB])
        o = np.argsort(DB)
        DB, okB, disB, EB = DB[o], okB[o], disB[o], EB[o]
        S["supplement_run"] = supplement_run
    PB = np.zeros((DB.size, th.size))
    EBm = np.zeros((DB.size, th.size))
    for i in range(DB.size):
        for j in range(th.size):
            o, d = okB[i, j], disB[i, j]
            PB[i, j] = d[o].mean()
            EBm[i, j] = np.abs(EB[i, j][d & o]).mean() if (d & o).any() else np.nan
    S["B_D"] = DB.tolist()
    S["B_theta_over_pi"] = (th / np.pi).tolist()
    S["B_P"] = PB.tolist()
    S["B_Emean"] = EBm.tolist()
    S["B_Emean_ratio_pi2_over_0"] = (EBm[:, -1] / EBm[:, 0]).tolist()
    S["B_P_min_and_theta"] = [[float(PB[i].min()), float(th[np.argmin(PB[i])] / np.pi)] for i in range(DB.size)]
    deep = 0
    surv = np.where(PB[deep] < 0.999)[0]
    S["B_deep_first_theta_with_survivors_over_pi"] = float(th[surv.min()] / np.pi) if surv.size else None
    S["reference"] = {k: [str(v[0]), v[1]] for k, v in ref.BKRS.items()}
    _summary(run, "general", S)

    # ---- figure: isotropic P and <E> against the BKRS fits
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.0), sharex=True,
                            gridspec_kw={"height_ratios": [2.2, 1]})
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, hspace=0.05, wspace=0.25)
    Dc = np.linspace(0, 2.1, 300)
    a = axs[0, 0]
    a.plot(Dc, ref.bkrs_pdis(Dc), color=BLUE, label="BKRS fit (isotropic)")
    a.plot(D, P, "o-", color=RED, ms=3, lw=1.0, label="this work (isotropic)")
    if coplanar_run:
        C = np.load(_src(coplanar_run, "coplanar.npz"))
        kc = C["D"] >= D_TRUST * (1 - 1e-9)
        Dcp = C["D"][kc]
        for tag, ls, col, lab in (("pro", "-", YEL, "this work, coplanar prograde"),
                                  ("ret", "--", GRN, "this work, coplanar retrograde")):
            dc, oc = C[f"disrupted_{tag}"][kc], C[f"ok_{tag}"][kc]
            Pcp = np.array([dc[i][oc[i]].mean() for i in range(Dcp.size)])
            a.plot(Dcp, Pcp, color=col, ls=ls, lw=1.0, label=lab)
    a.set_ylabel(r"$P_{\rm dis}$")
    a.set_ylim(0, 1.05)
    a.legend(loc="lower left", fontsize=8)
    a = axs[1, 0]
    a.axhline(0, **fs.THIN)
    a.plot(D, 100 * (P - Pfit), "o-", color=RED, ms=3, lw=1.0)
    acc = np.where(Dc <= 1, 0.01, np.interp(Dc, [1, 1.8, 2.0, 2.1], [0.01, 0.05, 0.2, 0.2]))
    fs.band(a, Dc, -100 * acc * ref.bkrs_pdis(Dc), 100 * acc * ref.bkrs_pdis(Dc), BLUE)
    a.set_ylim(-4, 4)
    a.set_ylabel(r"$\Delta P_{\rm dis}$ [points]")
    a.set_xlabel(r"$D$", labelpad=-2)
    a = axs[0, 1]
    a.plot(Dc, ref.bkrs_emean(Dc), color=BLUE, label="BKRS fit")
    a.plot(D, Em, "o-", color=RED, ms=3, lw=1.0, label=r"this work, $\langle|E|\rangle$")
    a.plot(D, E99, "s--", color=RED, ms=2.5, lw=1.0, label="this work, top 1% threshold")
    a.set_ylabel(r"$|E|$")
    a.legend(loc="upper right", fontsize=8)
    a = axs[1, 1]
    a.axhline(0, **fs.THIN)
    a.plot(D, 100 * (Em / Efit - 1), "o-", color=RED, ms=3, lw=1.0)
    acc = np.where(Dc <= 1, 0.01, np.interp(Dc, [1, 1.8, 2.0, 2.1], [0.01, 0.03, 0.1, 0.1]))
    fs.band(a, Dc, -100 * acc, 100 * acc, BLUE)
    a.set_ylim(-12, 12)
    a.set_ylabel(r"$\langle|E|\rangle$/fit $-1$ [%]")
    a.set_xlabel(r"$D$", labelpad=-2)
    _save(fig, run, "fig_general_pdis_energy")

    # ---- figure: inclination dependence
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.25, 5.4), sharex=True)
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.09, top=0.98, hspace=0.05)
    cols = fs.series_colors(DB.size)
    for i in range(DB.size):
        axs[0].plot(th / np.pi, PB[i], color=cols[i], lw=1.2, label=f"D = {DB[i]:g}")
        axs[1].plot(th / np.pi, EBm[i], color=cols[i], lw=1.2)
    axs[0].axvline(0.15, **fs.MASK_LINE)
    axs[0].axhline(0.8, **fs.MASK_LINE)
    axs[0].set_ylabel(r"$P_{\rm dis}(\theta)$")
    axs[0].set_ylim(-0.32, 1.05)
    axs[0].legend(loc="lower center", fontsize=7, ncol=3)
    axs[1].set_ylabel(r"$\langle |E| \rangle(\theta)$")
    axs[1].set_xlabel(r"inclination $\theta/\pi$", labelpad=-2)
    axs[1].set_xlim(0, 0.5)
    _save(fig, run, "fig_general_theta")

    # ---- figure: collision probability (r_min < a/5)
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.25, 2.8))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.17, top=0.97)
    ax.plot(D, Pc, "o-", color=RED, ms=3, lw=1.0, label=r"this work, $r_{\min} < a/5$")
    ax.fill_between([1e-4, 0.1], 0.05, 0.07, color=BLUE, alpha=0.3, lw=0, label="BKRS text")
    ax.plot([1.6], [0.14], "o", color=BLUE, ms=4)
    ax.set_xscale("log")
    ax.set_xlabel(r"$D$")
    ax.set_ylabel("collision probability")
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, run, "fig_general_collision")
    runlib.finish_run(run, results={k: S[k] for k in S if k.startswith("max_") or k.startswith("Dmax")})
    return S


# ============================================================================ P3
def p3(run_id):
    src = _src(run_id, "p3.npz")
    run = runlib.start_run(f"analysis of {run_id} (P3 full vs restricted)", extra_inputs=[src],
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P3")
    Z = np.load(src)
    qs = [q for q in Z["q"] if q > 0]
    ph = Z["phase"]
    S = {"source_run": run_id, "q": [float(q) for q in qs], "phases": int(ph.size)}
    rows = {}
    for D in (1.0, 0.1):
        Er = Z[f"E2_q0_D{D:g}"]
        dr = Z[f"disrupted_q0_D{D:g}"] & Z[f"ok_q0_D{D:g}"]
        scale = np.abs(Er[dr]).mean()
        med, p90, mis = [], [], []
        for q in qs:
            Ef = Z[f"dE_q{q:g}_D{D:g}"]
            outc = Z[f"outcome_q{q:g}_D{D:g}"]
            df = (outc >= 1) & (outc <= 4) & Z[f"ok_q{q:g}_D{D:g}"]
            both = df & dr
            rel = np.abs(Ef[both] - Er[both]) / scale
            med.append(float(np.median(rel)))
            p90.append(float(np.percentile(rel, 90)))
            mis.append(float(np.mean(df != dr)))
        rows[D] = (med, p90, mis)
        S[f"D{D:g}"] = {"median_rel_diff": med, "p90_rel_diff": p90, "fate_mismatch_fraction": mis,
                        "scale_mean_absE_restricted": float(scale)}
    S["SKR_example"] = {"restricted_E2": float(Z["example_restricted_E2"][0]),
                        "full_dE_q1e6": float(Z["example_full_dE"][0]),
                        "rel_diff": float(abs(Z["example_full_dE"][0] / Z["example_restricted_E2"][0] - 1)),
                        "full_outcome": OUT[int(Z["example_full_outcome"][0])]}
    _summary(run, "p3", S)
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.91, wspace=0.32)
    cols = fs.series_colors(len(qs), cmap="viridis")
    for ax, D in ((axs[0], 1.0), (axs[1], 0.1)):
        Er = Z[f"E2_q0_D{D:g}"]
        dr = Z[f"disrupted_q0_D{D:g}"] & Z[f"ok_q0_D{D:g}"]
        for q, c in zip(qs, cols):
            if q in (1e6, 1e3, 1e2, 10):
                outc = Z[f"outcome_q{q:g}_D{D:g}"]
                df = (outc >= 1) & (outc <= 4)
                ax.plot(ph / np.pi, np.where(df, Z[f"dE_q{q:g}_D{D:g}"], np.nan), color=c, lw=1.0,
                        label=f"full, M/m = {q:.0e}".replace("e+0", "e"))
        ax.plot(ph / np.pi, np.where(dr, Er, np.nan), color=RED, ls="--", lw=1.2, label="restricted")
        ax.set_xlabel(r"$\phi/\pi$")
        ax.set_title(f"D = {D:g}, prograde", fontsize=10)
        ax.set_xlim(0, 2)
    axs[0].set_ylabel(r"$\Delta E$")
    axs[1].set_ylim(-6, 6)
    axs[0].legend(fontsize=7, loc="upper left")
    ax = axs[2]
    qa = np.array(qs)
    for D, mk in ((1.0, "o"), (0.1, "s")):
        ax.loglog(qa, rows[D][0], mk + "-", color=RED, ms=3, lw=1.0, label=f"median, D = {D:g}")
        ax.loglog(qa, rows[D][1], mk + ":", color=YEL, ms=3, lw=1.0, label=f"90th pct, D = {D:g}")
    ax.loglog(qa, 0.5 * qa ** (-1 / 3), **fs.GUIDE, label=r"$\propto (M/m)^{-1/3}$")
    ax.axhline(1e-3, **fs.MASK_LINE)
    ax.set_xlabel(r"$M/m$")
    ax.set_ylabel(r"$|\Delta E_{\rm full} - E_{\rm restr}| / \langle|E|\rangle$")
    ax.legend(fontsize=6.5, loc="lower left")
    _save(fig, run, "fig_full_vs_restricted")
    runlib.finish_run(run, results=S)
    return S


OUT = T.OUTCOME_NAMES


# ============================================================================ P4
def p4(run_id):
    src = _src(run_id, "p4.npz")
    run = runlib.start_run(f"analysis of {run_id} (P4 start distance)", extra_inputs=[src],
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P4")
    Z = np.load(src)
    ph = Z["phase"]
    S = {"source_run": run_id}
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.92, wspace=0.05)
    for ax, q in ((axs[0], 1e6), (axs[1], 10)):
        refk = 40
        oref = Z[f"outcome_q{q:g}_k{refk}"]
        Eref = Z[f"dE_q{q:g}_k{refk}"]
        dref = (oref >= 1) & (oref <= 4)
        scale = np.abs(Eref[dref]).mean()
        S[f"q{q:g}"] = {}
        for k0, c in zip((5, 10, 20, 40), fs.series_colors(4)):
            o = Z[f"outcome_q{q:g}_k{k0}"]
            E = Z[f"dE_q{q:g}_k{k0}"]
            d = (o >= 1) & (o <= 4)
            both = d & dref
            S[f"q{q:g}"][f"k0={k0}"] = {
                "same_outcome_fraction": float(np.mean(o == oref)),
                "same_disruption_flag_fraction": float(np.mean(d == dref)),
                "median_rel_dE_diff": float(np.median(np.abs(E[both] - Eref[both])) / scale),
                "P_dis": float(d.mean())}
            ax.plot(ph / np.pi, np.where(d, E, np.nan), color=c, lw=1.0, label=f"start {k0} $r_t$")
        ax.set_title(f"M/m = {q:g}, D = 0.5, prograde, m1 = m2", fontsize=10)
        ax.set_xlabel(r"effective phase $\phi/\pi$")
        ax.set_xlim(0, 2)
        ax.set_xticks([0, 0.5, 1, 1.5])
    axs[0].set_ylabel(r"$\Delta E$")
    axs[0].legend(fontsize=8, ncol=2)
    _save(fig, run, "fig_start_distance")
    _summary(run, "p4", S)
    runlib.finish_run(run, results=S)
    return S


# ============================================================================ finite q
def finiteq(run_id):
    src = _src(run_id, "finiteq.npz")
    run = runlib.start_run(f"analysis of {run_id} (finite mass ratio)", extra_inputs=[src],
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P3")
    Z = np.load(src)
    qs, D = list(Z["q"]), Z["D"]
    S = {"source_run": run_id, "q": [float(q) for q in qs], "D": D.tolist()}
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 4.8), sharex=True, sharey="row")
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.1, top=0.95, hspace=0.06, wspace=0.05)
    cols = {0: RED, 10: BLUE, 30: GRN, 100: YEL, 1000: ORA}
    for j, kind in enumerate(("iso", "pro", "ret")):
        S[kind] = {}
        for q in qs:
            P, Em, frac = [], [], []
            for Dv in D:
                if q == 0:
                    ok = Z[f"ok_{kind}_q0_D{Dv:g}"]
                    d = Z[f"disrupted_{kind}_q0_D{Dv:g}"][ok]
                    E = Z[f"E2_{kind}_q0_D{Dv:g}"][ok]
                else:
                    o = Z[f"outcome_{kind}_q{q:g}_D{Dv:g}"]
                    ok = Z[f"ok_{kind}_q{q:g}_D{Dv:g}"] & (o != T.UNSETTLED)
                    o = o[ok]
                    d = o != T.SURVIVED
                    E = Z[f"dE_{kind}_q{q:g}_D{Dv:g}"][ok]
                    frac.append([float(np.mean(o == c)) for c in range(5)])
                P.append(float(d.mean()))
                Em.append(float(np.abs(E[d]).mean()) if d.any() else float("nan"))
            lab = "restricted" if q == 0 else f"M/m = {q:g}"
            S[kind][lab] = {"P_dis": P, "Emean": Em}
            if frac:
                S[kind][lab]["outcome_fractions(survived,m2ej,m1ej,bothbound,bothfree)"] = frac
            ls = "--" if q == 0 else "-"
            axs[0, j].plot(D, P, color=cols[int(q)], ls=ls, lw=1.2, label=lab)
            axs[1, j].plot(D, Em, color=cols[int(q)], ls=ls, lw=1.2)
        axs[0, j].set_title({"iso": "isotropic", "pro": "coplanar prograde",
                             "ret": "coplanar retrograde"}[kind], fontsize=10)
        axs[1, j].set_xlabel(r"$D = r_p/r_t$", labelpad=-2)
    axs[0, 0].set_ylabel(r"$P_{\rm dis}$")
    axs[1, 0].set_ylabel(r"$\langle|\Delta E|\rangle$")
    axs[0, 0].legend(fontsize=8)
    _save(fig, run, "fig_finite_q")
    _summary(run, "finiteq", S)
    runlib.finish_run(run)
    return S


# ============================================================================ example
def example():
    """Driver demonstration: initial data and one passage at M/m = 10 (units G = c = 1,
    lengths in units of the binary mass m = m1 + m2)."""
    run = runlib.start_run("driver demonstration: initial data and trajectory of one encounter at "
                           "M/m = 10, D = 0.7, coplanar prograde; cross-check scatter vs solve_ivp")
    s = T.HillsSetup(M=10.0, m1=0.5, m2=0.5, a=30.0, D=0.7, phase=0.3 * np.pi)
    ic = T.initial_state(s, k0=10.0)
    out = T.scatter([s], k0=10.0, k_end=30.0)
    tt, X, V, sol = T.trajectory(s, k0=10.0, k_end=30.0, n_out=4000)
    S = {"setup": ic["params"], "r_t": ic["r_t"], "r_p": ic["r_p"], "r0": ic["r0"],
         "t_to_pericentre": ic["t_to_pericentre"],
         "positions": ic["positions"].tolist(), "momenta": ic["momenta"].tolist(),
         "outcome": OUT[int(out["outcome"][0])], "dE": float(out["dE"][0]),
         "E1": float(out["E1"][0]), "E2": float(out["E2"][0]),
         "energy_error": float(out["energy_error"][0]),
         "scatter_vs_solve_ivp_max_abs_diff_final_positions": float(np.abs(X[-1] - out["x_end"][0]).max())}
    _summary(run, "example", S)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.8))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.13, top=0.95, wspace=0.25)
    ax = axs[0]
    for b, c, lab in ((0, "k", "M"), (1, RED, "m1"), (2, BLUE, "m2")):
        ax.plot(X[:, b, 0], X[:, b, 1], color=c, lw=1.0, label=lab)
        ax.plot(X[0, b, 0], X[0, b, 1], "o", color=c, ms=3)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x\ [m]$")
    ax.set_ylabel(r"$y\ [m]$")
    ax.legend(fontsize=8, loc="lower left")
    ax.set_title(f"M/m = 10, D = 0.7, a = 30 m: {OUT[int(out['outcome'][0])]}", fontsize=10)
    ax = axs[1]
    r12 = np.linalg.norm(X[:, 2] - X[:, 1], axis=1)
    r1 = np.linalg.norm(X[:, 1] - X[:, 0], axis=1)
    r2 = np.linalg.norm(X[:, 2] - X[:, 0], axis=1)
    ax.semilogy(tt, r12, color="k", label=r"$|x_2 - x_1|$")
    ax.semilogy(tt, r1, color=RED, label=r"$|x_1 - x_M|$")
    ax.semilogy(tt, r2, color=BLUE, label=r"$|x_2 - x_M|$")
    ax.axhline(ic["r_t"], **fs.MASK_LINE)
    ax.axvline(0, **fs.MASK_LINE)
    ax.set_xlabel(r"$t$ (0 = pericentre of the unperturbed orbit)")
    ax.set_ylabel(r"separation $[m]$")
    ax.legend(fontsize=8)
    _save(fig, run, "fig_driver_example")
    runlib.finish_run(run, results={k: S[k] for k in ("outcome", "dE", "energy_error")})
    return S


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "example":
        example()
    elif which == "general":
        general(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None,
                sys.argv[4] if len(sys.argv) > 4 else None)
    elif which == "coplanar":
        coplanar(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        {"p3": p3, "p4": p4, "finiteq": finiteq}[which](sys.argv[2])
