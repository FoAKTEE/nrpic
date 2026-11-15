"""Figures of the gravothermal package (style: python/nrpic/figstyle.py).

    python3 -E make_figures.py <sequence run outdir> <f21_tables.json> <figdir>
                               [<timescales outdir> [<polytrope check outdir>]]

Colour convention of figstyle: blue = published reference (F21 tables), red = this solver;
yellow, green, orange for further series; black dashed = analytic or printed guide lines.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

BCOL = {"0.1": fs.PAL["red"], "0.2": fs.PAL["yellow"], "0.3": fs.PAL["green"],
        "0.5": fs.PAL["blue"]}


def load(run):
    j = lambda n: json.load(open(os.path.join(run, n)))
    t1 = list(csv.DictReader(open(os.path.join(run, "table1_compare.csv"))))
    t2 = list(csv.DictReader(open(os.path.join(run, "table2_compare.csv"))))
    return j("criteria.json"), j("sequences.json"), j("eos.json"), j("profiles.json"), t1, t2


def fig_eos(eos, out):
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.95, wspace=0.25)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], "C1"]
    for (b, d), c in zip(eos.items(), cols):
        ax[0].plot(d["bw"], d["v"], color=c, label=f"b = {b}")
        ax[1].plot(d["bw"], d["gamma"], color=c, label=f"b = {b}")
    ax[0].axhline(0.57, **fs.GUIDE)
    ax[1].axhline(1.59, **fs.GUIDE)
    ax[0].set_xlabel(r"$bw = \epsilon_c/(mc^2+\epsilon_c)$")
    ax[1].set_xlabel(r"$bw = \epsilon_c/(mc^2+\epsilon_c)$")
    ax[0].set_ylabel(r"$v/c = (3p/\rho c^2)^{1/2}$")
    ax[1].set_ylabel(r"$\gamma = 1 + p/u$")
    ax[0].legend(loc="upper left", ncol=1)
    for a in ax:
        a.set_xlim(0, 1)
    fs.save(fig, os.path.join(out, "fig_eos"))
    plt.close(fig)


def fig_sequence(seqs, crit, t1, out, b="0.1"):
    seq = seqs[b]
    v = np.array([e["v0"] for e in seq])
    rows = [r for r in t1 if r["b"] == b]
    vp = np.array([float(r["v0_paper"]) for r in rows])
    c = crit[b]
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.09, top=0.97, wspace=0.32, hspace=0.06)
    panels = [("gavg", r"$\langle\gamma\rangle$, $\gamma_{\rm cr}$"), ("eps", r"$\varepsilon$"),
              ("B", r"$\hat B$"), ("E", r"$\hat E = \hat M$")]
    vis = (v >= 0.05) & (v <= 0.62)
    for a, (k, lab) in zip(ax.ravel(), panels):
        a.plot(v, [e[k] for e in seq], color=fs.PAL["red"], label="this solver")
        yv = np.array([e[k] for e in seq])[vis]
        pad = 0.06 * (yv.max() - yv.min())
        a.set_ylim(yv.min() - pad, yv.max() + pad)
        a.plot(vp, [float(r[f"{k}_paper"]) for r in rows], "o", ms=4, mfc="none",
               color=fs.PAL["blue"], label="F21 Table 1")
        if k == "gavg":
            a.plot(v, [e["gcr"] for e in seq], color=fs.PAL["yellow"],
                   label=r"$\gamma_{\rm cr}$, this solver")
            a.plot(vp, [float(r["gcr_paper"]) for r in rows], "s", ms=4, mfc="none",
                   color=fs.PAL["blue"])
            a.set_ylim(1.33, 1.68)
            a.axhline(5 / 3, **fs.GUIDE)
            a.axhline(4 / 3, **fs.GUIDE)
        a.set_ylabel(lab)
        for tag, ls in (("max_E", ":"), ("max_B", ":"), ("max_eps", "--"),
                        ("gavg_eq_gcr", "-."), ("omega2_zero_F21gamma", "-")):
            if c.get(tag):
                a.axvline(c[tag]["v0"], color="grey", lw=1.0, ls=ls, alpha=0.7)
        a.set_xlim(0.05, 0.62)
    ax[0, 0].legend(loc="center left", ncol=1)
    ax[1, 0].set_xlabel(r"$v(0)/c$")
    ax[1, 1].set_xlabel(r"$v(0)/c$")
    fs.save(fig, os.path.join(out, f"fig_sequence_b{b}"))
    plt.close(fig)


def fig_residuals(t1, t2, out):
    cols = ["E", "Erest", "B", "eps", "R", "C", "Z0", "ec0", "rho0", "p0", "v0", "gavg", "gcr"]
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.95)
    for i, k in enumerate(cols):
        for r in t1:
            d = abs(float(r[f"{k}_rel"]))
            ax.plot(i + 0.6 * (float(r["w0"]) * float(r["b"]) - 0.25), max(d, 1e-9), "o", ms=3,
                    color=BCOL[r["b"]], alpha=0.8)
    for i, k in enumerate(["w0"]):
        for r in t2:
            ax.plot(len(cols) + 0.1, max(abs(float(r["w0_rel"])), 1e-9), "s", ms=3,
                    color=fs.PAL["blue"], mfc="none")
    ax.set_yscale("log")
    ax.set_xticks(list(range(len(cols))) + [len(cols)])
    ax.set_xticklabels(cols + [r"$w_0$ T2"], rotation=0, fontsize=8)
    ax.set_ylabel(r"$|X_{\rm here}/X_{\rm F21} - 1|$")
    ax.minorticks_off()
    ax.set_ylim(1e-9, 1e4)
    for b, col in BCOL.items():
        ax.plot([], [], "o", color=col, label=f"b = {b}")
    ax.legend(loc="upper left", ncol=4)
    for i, k in enumerate(cols):
        for r in t1:
            d = abs(float(r[f"{k}_rel"]))
            if d > 1e-2:
                ax.annotate(f"main.tex:{r['line']}", (i, d), xytext=(6, 4),
                            textcoords="offset points", fontsize=7)
    fs.save(fig, os.path.join(out, "fig_table_residuals"))
    plt.close(fig)


def fig_omega(seqs, crit, out):
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
    for b, seq in seqs.items():
        Z = np.array([e["Z0"] for e in seq])
        rc = np.array([e["rho0"] for e in seq])
        o1 = np.array([e["omega2_F21"] for e in seq]) / (4 * np.pi * rc)
        o2 = np.array([e["omega2_53"] for e in seq]) / (4 * np.pi * rc)
        tr = np.array([e["gavg"] - e["gcr"] for e in seq])
        ax[0].plot(Z, o1, color=BCOL[b], label=f"b = {b}")
        ax[0].plot(Z, o2, color=BCOL[b], ls="--")
        ax[1].plot(Z, tr, color=BCOL[b], label=f"b = {b}")
        ax[1].plot(Z, [5 / 3 - e["gcr"] for e in seq], color=BCOL[b], ls="--")
    for a in ax:
        a.axhline(0, **fs.GUIDE)
        a.set_xlabel(r"$Z(0)$")
        a.set_xlim(0, 1.6)
    ax[0].set_ylim(-0.05, 0.05)
    ax[1].set_ylim(-0.15, 0.35)
    ax[0].set_ylabel(r"$\omega_0^2/(4\pi G\rho_c)$ (exact, FEM)")
    ax[1].set_ylabel(r"$\langle\gamma\rangle-\gamma_{\rm cr}$ (trial $\xi = r e^\Phi$)")
    ax[0].plot([], [], color="grey", label=r"$\gamma = 1 + p/u$")
    ax[0].plot([], [], color="grey", ls="--", label=r"$\gamma = 5/3$")
    ax[0].legend(loc="upper right", ncol=2, fontsize=8)
    fs.save(fig, os.path.join(out, "fig_onset"))
    plt.close(fig)


def fig_criteria(crit, t2, out):
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH / 2 + 0.6, 3.4))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.95)
    tags = [("max_E", r"max $\hat E$", fs.PAL["green"]), ("max_B", r"max $\hat B$", "C1"),
            ("max_eps", r"max $\varepsilon$", fs.PAL["yellow"]),
            ("omega2_zero_F21gamma", r"$\omega_0^2=0$, $\gamma=1+p/u$", fs.PAL["red"]),
            ("gavg_eq_gcr", r"$\langle\gamma\rangle=\gamma_{\rm cr}$", "k"),
            ("omega2_zero_gamma53", r"$\omega_0^2=0$, $\gamma=5/3$", "purple"),
            ("gcr_eq_5_3", r"$\gamma_{\rm cr}=5/3$", "grey")]
    bs = sorted(crit, key=float)
    for tag, lab, col in tags:
        x = [float(b) for b in bs if crit[b].get(tag)]
        y = [crit[b][tag]["Z0"] for b in bs if crit[b].get(tag)]
        if x:
            ax.plot(x, y, "o-", color=col, label=lab, ms=4)
    ax.plot([float(r["b"]) for r in t2], [float(r["Z0_paper"]) for r in t2], "s", ms=6,
            mfc="none", color=fs.PAL["blue"], label=r"F21 Table 2")
    ax.plot([float(r["b"]) for r in t2], [float(r["Z0_here"]) for r in t2], "x", ms=4,
            color="k", label=r"Table 2 roots, this solver")
    ax.set_xscale("log")
    ax.set_xlabel(r"$b = kT(R)/mc^2$")
    ax.set_ylabel(r"$Z(0)$ at the criterion")
    ax.legend(loc="lower right", ncol=1, fontsize=7)
    ax.set_xlim(0.08, 6)
    fs.save(fig, os.path.join(out, "fig_criteria_vs_b"))
    plt.close(fig)


def fig_profiles(prof, out):
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.97, wspace=0.28, hspace=0.06)
    lab = {"max_E": r"max $\hat E$", "max_B": r"max $\hat B$", "max_eps": r"max $\varepsilon$",
           "omega2_zero_F21gamma": r"$\omega_0^2 = 0$", "gavg_eq_gcr": r"$\langle\gamma\rangle=\gamma_{\rm cr}$"}
    col = {"max_E": fs.PAL["green"], "max_B": "C1", "max_eps": fs.PAL["yellow"],
           "omega2_zero_F21gamma": fs.PAL["red"], "gavg_eq_gcr": "k"}
    for tag, p in prof.items():
        r = np.array(p["r"]) / p["R"]
        b = 0.1
        ax[0, 0].plot(r, b * np.array(p["w"]), color=col[tag], label=lab[tag])
        ax[0, 1].semilogy(r, np.clip(p["rho"], 1e-12, None), color=col[tag])
        ax[1, 0].plot(r, p["v"], color=col[tag])
        ax[1, 1].plot(r, p["gamma"], color=col[tag])
    ax[0, 0].set_ylabel(r"$bw$")
    ax[0, 1].set_ylabel(r"$\hat\rho$")
    ax[0, 1].set_ylim(1e-6, 1e3)
    ax[1, 0].set_ylabel(r"$v/c$")
    ax[1, 1].set_ylabel(r"$\gamma$")
    for a in ax[1]:
        a.set_xlabel(r"$r/R$")
    ax[0, 0].legend(loc="upper right")
    fs.save(fig, os.path.join(out, "fig_profiles_b0.1"))
    plt.close(fig)


def fig_timescales(ts, out):
    rows = [r for r in ts["threshold_models_scaled"] if r["M_msun"] < 1e3]
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.04, right=0.98, bottom=0.15, top=0.97)
    g = ts["G26_core_445.8t0"]
    t0 = 0.26 * 3.15576e16
    lines = [
        (r"$t_{\rm coll}$ at the centre ($\sigma/m = 5$ cm$^2$/g)",
         np.median([r["t_coll_c_s"] for r in rows]), "C1"),
        (r"$R/c$", np.median([r["t_light_s"] for r in rows]), fs.PAL["green"]),
        (r"$t_{\rm dyn}$ (centre)", np.median([r["t_dyn_c_s"] for r in rows]), fs.PAL["red"]),
        (r"G26 core $t_{\rm dyn}$ at 445.8 $t_0$", g["t_dyn_core_yr"] * 3.15576e7, fs.PAL["yellow"]),
        (r"$t_c \sim 0.1\,t_0$ (fastest)", 0.1 * t0, fs.PAL["blue"]),
        (r"$t_0$", t0, fs.PAL["blue"]),
        (r"$t_c\sim 40\,t_0$", 40 * t0, fs.PAL["blue"]),
        (r"$580\,t_0$ (horizon)", 580 * t0, "k"),
    ]
    for i, (lab, t, c) in enumerate(lines):
        ax.plot([t], [i], "o", color=c)
        ax.text(t * 30, i, lab, va="center", fontsize=8)
    ax.set_xscale("log")
    ax.set_yticks([])
    ax.set_ylim(-0.7, len(lines) - 0.3)
    ax.set_xlim(1e-25, 1e30)
    ax.set_xlabel(r"time (s); onset models scaled to $M = 200\,M_\odot$; G26 values from SIDM_MS.tex:384, 440, 474, 476")
    fs.save(fig, os.path.join(out, "fig_timescales"))
    plt.close(fig)


def fig_polytrope(pc, out):
    x = np.array(pc["grid"])
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.3)
    ax[0].semilogx(x, pc["M"], color=fs.PAL["blue"], label=r"TOV, $\Gamma=2$, $K=100$")
    ax[0].axvline(pc["rhoc_Mmax"], **fs.GUIDE)
    ax[0].set_xlabel(r"$\rho_{0,c}$")
    ax[0].set_ylabel(r"$M$")
    ax[0].legend(loc="lower right")
    ax[1].semilogx(x, pc["omega2_N600"], color=fs.PAL["red"], label="FEM, N = 600")
    ax[1].semilogx(x, pc["trial"], color=fs.PAL["yellow"], label=r"trial $\xi = r e^\Phi$")
    ax[1].axhline(0, color="grey", lw=1.0)
    ax[1].axvline(pc["rhoc_Mmax"], **fs.GUIDE)
    ax[1].set_xlabel(r"$\rho_{0,c}$")
    ax[1].set_ylabel(r"$\omega_0^2$")
    ax[1].set_ylim(-0.05, 0.05)
    ax[1].legend(loc="lower left")
    fs.save(fig, os.path.join(out, "fig_polytrope_check"))
    plt.close(fig)


def main(run, tables, figdir, tsdir=None, polydir=None):
    fs.use_style()
    os.makedirs(figdir, exist_ok=True)
    crit, seqs, eos, prof, t1, t2 = load(run)
    fig_eos(eos, figdir)
    for b in seqs:
        fig_sequence(seqs, crit, t1, figdir, b)
    fig_residuals(t1, t2, figdir)
    fig_omega(seqs, crit, figdir)
    fig_criteria(crit, t2, figdir)
    fig_profiles(prof, figdir)
    if tsdir:
        fig_timescales(json.load(open(os.path.join(tsdir, "timescales.json"))), figdir)
    if polydir:
        fig_polytrope(json.load(open(os.path.join(polydir, "polytrope_check.json"))), figdir)
    print("figures in", figdir)


if __name__ == "__main__":
    main(*sys.argv[1:])
