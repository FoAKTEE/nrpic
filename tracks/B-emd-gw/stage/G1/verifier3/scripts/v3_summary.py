#!/usr/bin/env python3
"""V3 summary of verifier3: error measures, convergence orders and figures from the
per-dump numbers of v3_measure.py (JOURNAL entry 5 defines the measures).

    V3_DUMPS=<run dir of v3_measure>/v3_dumps.json python3 v3_summary.py
Writes $NRPIC_RUN_DIR/v3_summary.json and v3_*.png/pdf.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact  # noqa: E402
import figstyle as fs  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v3s"))
os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.environ["V3_DUMPS"]))
dumps = D["dumps"]
POL = ["+", "x"]
DIAGS = ["TT", "Wsp", "Wfd6"]


def cx(p):
    return complex(p[0], p[1])


def series(case, N):
    return [d for d in dumps if d["case"] == case and d["N"] == N]


def order(e1, e2, n1, n2):
    if e1 == 0 or e2 == 0:
        return None
    return float(np.log(abs(e1) / abs(e2)) / np.log(n2 / n1))


summary = {"F": {}, "X": {}, "X10": {}}
TS = {}

# ------------------------------------------------------------------ F
fw = exact.FlatWave()
for N in sorted({d["N"] for d in dumps if d["case"] == "F"}):
    S = series("F", N)
    t = np.array([d["t"] for d in S])
    rec = {"t_final": float(t[-1]), "n_dumps": len(S)}
    ts = {"t": t}
    for p in (0, 1):
        Zex = np.array([fw.complex_amp(tt)[p] for tt in t])
        Z = {dg: np.array([cx(d[dg][p]) for d in S]) for dg in DIAGS}
        for dg in DIAGS:
            amp = np.abs(Z[dg]) / np.abs(Zex) - 1
            ph = np.angle(Z[dg] / Zex)
            crel = np.abs(Z[dg] - Zex) / np.abs(Zex)
            ts[(dg, p, "amp")], ts[(dg, p, "ph")], ts[(dg, p, "crel")] = amp, ph, crel
            rec[f"{dg} {POL[p]}"] = {
                "amp_err_final": float(amp[-1]), "phase_err_final": float(ph[-1]),
                "crel_final": float(crel[-1]),
                "max|amp_err|": float(np.max(np.abs(amp[1:]))), "max|phase_err|": float(np.max(np.abs(ph[1:]))),
                "max crel": float(np.max(crel[1:]))}
        for dg in ("Wsp", "Wfd6"):
            dd = np.abs(Z["TT"] - Z[dg]) / np.abs(Zex)
            ts[("diff", dg, p)] = dd
            rec[f"TT-{dg} {POL[p]}"] = {"final": float(dd[-1]), "max": float(np.max(dd))}
        rec[f"backward_frac {POL[p]} max"] = float(max(d["backward_frac"][p] for d in S))
    rec["nonTT_frac max"] = float(max(d["nonTT_frac"] for d in S[1:]))
    rec["nonTT_frac t0"] = float(S[0]["nonTT_frac"])
    rec["offmode_frac max"] = float(max(d["offmode_frac"] for d in S[1:]))
    rec["Wsp_rev_over_fwd max"] = float(max(d["Wsp_rev_over_fwd"] for d in S))
    summary["F"][N] = rec
    TS[("F", N)] = ts

# ------------------------------------------------------------------ X and X10
for case in ("X", "X10"):
    eps = D["eps"][case]
    xw = exact.ExpandingWave(eps_p=eps[0], eps_x=eps[1])
    kn = xw.kn
    for N in sorted({d["N"] for d in dumps if d["case"] == case}):
        S = series(case, N)
        t = np.array([d["t"] for d in S])
        T, dT = xw.mode.T(t), xw.mode.dT(t)
        rec = {"t_final": float(t[-1]), "n_dumps": len(S)}
        ts = {"t": t}
        a_ex = exact.eds_a(t)
        a_num = np.array([d["bg"]["chi_mean"] for d in S]) ** -0.5
        al = np.array([d["bg"]["alpha_mean"] for d in S])
        trK = np.array([d["bg"]["trK_mean"] for d in S])
        ts["bg_a"], ts["bg_alpha"] = a_num / a_ex - 1, al / a_ex - 1
        ts["bg_K"] = trK / (-3 * a_ex ** -1.5) - 1
        rec["background"] = {"max|a/a_ex-1|": float(np.max(np.abs(ts["bg_a"]))),
                             "max|alpha/a_ex-1|": float(np.max(np.abs(ts["bg_alpha"]))),
                             "max|K/K_ex-1|": float(np.max(np.abs(ts["bg_K"]))),
                             "a/a_ex-1 final": float(ts["bg_a"][-1]),
                             "max chi rms dev": float(max(d["bg"]["chi_rms_dev"] for d in S)),
                             "max Theta": float(max(d["bg"]["Theta_max"] for d in S))}
        for p in (0, 1):
            e = eps[p]
            Zex = e * (T + 1j * dT / kn)
            Z = {}
            for dg in DIAGS:
                kh = "TT_h" if dg == "TT" else dg + "_h"
                kd = "TT_hd" if dg == "TT" else dg + "_hd"
                H = np.array([cx(d[kh][p]) for d in S])
                Hd = np.array([cx(d[kd][p]) for d in S])
                Z[dg] = H.real + 1j * Hd.real / kn
                quad = np.abs(H.imag + 1j * Hd.imag / kn) / np.abs(Zex)
                amp = np.abs(Z[dg]) / np.abs(Zex) - 1
                ph = np.angle(Z[dg] / Zex)
                crel = np.abs(Z[dg] - Zex) / np.abs(Zex)
                ts[(dg, p, "amp")], ts[(dg, p, "ph")], ts[(dg, p, "crel")] = amp, ph, crel
                ts[(dg, p, "H")] = H.real / e
                rec[f"{dg} {POL[p]}"] = {
                    "amp_err_final": float(amp[-1]), "phase_err_final": float(ph[-1]),
                    "crel_final": float(crel[-1]),
                    "max|amp_err|": float(np.max(np.abs(amp[1:]))),
                    "max|phase_err|": float(np.max(np.abs(ph[1:]))),
                    "max crel": float(np.max(crel[1:])),
                    "max spatial quadrature": float(np.max(quad[1:]))}
            for dg in ("Wsp", "Wfd6"):
                dd = np.abs(Z["TT"] - Z[dg]) / np.abs(Zex)
                ts[("diff", dg, p)] = dd
                rec[f"TT-{dg} {POL[p]}"] = {"final": float(dd[-1]), "max": float(np.max(dd))}
        rec["nonTT_frac max"] = float(max(d["nonTT_frac"] for d in S[1:]))
        rec["offmode_frac max"] = float(max(d["offmode_frac"] for d in S[1:]))
        # plus/cross asymmetry of the TT route
        rec["asym TT"] = {
            "amp_err x - +, final": float(ts[("TT", 1, "amp")][-1] - ts[("TT", 0, "amp")][-1]),
            "phase_err x - +, final": float(ts[("TT", 1, "ph")][-1] - ts[("TT", 0, "ph")][-1]),
            "crel x / crel +, final": float(ts[("TT", 1, "crel")][-1] / ts[("TT", 0, "crel")][-1]),
            "max_t |amp_err x - amp_err +|": float(np.max(np.abs(ts[("TT", 1, "amp")] - ts[("TT", 0, "amp")])[1:])),
            "max_t |phase_err x - phase_err +|": float(np.max(np.abs(ts[("TT", 1, "ph")] - ts[("TT", 0, "ph")])[1:]))}
        summary[case][N] = rec
        TS[(case, N)] = ts

# ------------------------------------------------------------------ convergence orders
for case in ("F", "X"):
    Ns = sorted(summary[case])
    conv = {}
    for dg in DIAGS:
        for p in (0, 1):
            for q in ("amp_err_final", "phase_err_final", "crel_final", "max crel"):
                vals = [summary[case][N][f"{dg} {POL[p]}"][q] for N in Ns]
                conv[f"{dg} {POL[p]} {q}"] = {
                    f"{Ns[i]}->{Ns[i + 1]}": order(vals[i], vals[i + 1], Ns[i], Ns[i + 1]) for i in range(len(Ns) - 1)}
    for dg in ("Wsp", "Wfd6"):
        for p in (0, 1):
            vals = [summary[case][N][f"TT-{dg} {POL[p]}"]["max"] for N in Ns]
            conv[f"TT-{dg} {POL[p]} max"] = {
                f"{Ns[i]}->{Ns[i + 1]}": order(vals[i], vals[i + 1], Ns[i], Ns[i + 1]) for i in range(len(Ns) - 1)}
    summary[case]["orders"] = conv

# x1 vs x10 at N = 64
if 64 in summary["X"] and 64 in summary["X10"]:
    cmp = {}
    for p in (0, 1):
        for q in ("amp_err_final", "phase_err_final", "crel_final", "max|amp_err|", "max|phase_err|"):
            a1 = summary["X"][64][f"TT {POL[p]}"][q]
            a10 = summary["X10"][64][f"TT {POL[p]}"][q]
            cmp[f"TT {POL[p]} {q}"] = {"x1": a1, "x10": a10, "ratio x1/x10": (a1 / a10 if a10 else None)}
    summary["x1_vs_x10_N64"] = cmp

with open(os.path.join(OUT, "v3_summary.json"), "w") as f:
    json.dump(summary, f, indent=1, default=str)

# ------------------------------------------------------------------ figures
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

NCOL = {16: fs.PAL["blue"], 32: fs.PAL["red"], 48: fs.PAL["yellow"], 64: fs.PAL["green"]}
LS = {"TT": "-", "Wsp": "--", "Wfd6": ":"}
LAB = {"TT": "TT", "Wsp": r"$\Psi_4$/Weyl spectral", "Wfd6": r"$\Psi_4$/Weyl FD6"}


def time_fig(case, fname, tlabel, period=None):
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.95, hspace=0.08, wspace=0.28)
    for p in (0, 1):
        for N in sorted(summary[case]):
            if not isinstance(N, int):
                continue
            ts = TS[(case, N)]
            tt = ts["t"] / (period or 1.0)
            for dg in DIAGS:
                kw = dict(color=NCOL[N], ls=LS[dg], lw=1.2)
                axs[0, p].plot(tt[1:], ts[(dg, p, "amp")][1:], **kw, label=(f"N={N}" if dg == "TT" else None))
                axs[1, p].plot(tt[1:], ts[(dg, p, "ph")][1:], **kw,
                               label=(LAB[dg] if N == 16 else None))
        axs[0, p].set_yscale("symlog", linthresh=1e-9)
        axs[1, p].set_yscale("symlog", linthresh=1e-9)
        axs[0, p].set_title(f"{case}: polarization {POL[p]}")
        axs[1, p].set_xlabel(tlabel, labelpad=-2)
    axs[0, 0].set_ylabel(r"amplitude error $|Z|/|Z_{\rm ex}|-1$")
    axs[1, 0].set_ylabel(r"phase error arg$(Z/Z_{\rm ex})$ [rad]")
    axs[0, 0].legend(loc="lower left", ncol=2, fontsize=8)
    axs[1, 0].legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(OUT, fname))


time_fig("F", "v3_F_time", "t [periods]", period=1.0 / np.sqrt(3.0))
time_fig("X", "v3_X_time", "conformal time t")


def conv_fig(case, fname, refs):
    Ns = np.array(sorted(N for N in summary[case] if isinstance(N, int)))
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.9, wspace=0.32)
    titles = ["|amplitude error| (final)", "|phase error| (final) [rad]", "TT vs Weyl (max over t)"]
    for p, mk in ((0, "o"), (1, "s")):
        for dg in DIAGS:
            col = {"TT": fs.PAL["blue"], "Wsp": fs.PAL["red"], "Wfd6": fs.PAL["yellow"]}[dg]
            a = [abs(summary[case][N][f"{dg} {POL[p]}"]["amp_err_final"]) for N in Ns]
            ph = [abs(summary[case][N][f"{dg} {POL[p]}"]["phase_err_final"]) for N in Ns]
            axs[0].loglog(Ns, a, mk + LS[dg], color=col, ms=4, lw=1.0, label=(f"{LAB[dg]} {POL[p]}"))
            axs[1].loglog(Ns, ph, mk + LS[dg], color=col, ms=4, lw=1.0)
        for dg, col in (("Wsp", fs.PAL["red"]), ("Wfd6", fs.PAL["yellow"])):
            dd = [summary[case][N][f"TT-{dg} {POL[p]}"]["max"] for N in Ns]
            axs[2].loglog(Ns, dd, mk + "-", color=col, ms=4, lw=1.0, label=f"TT$-${LAB[dg]} {POL[p]}")
        if case == "X" and 64 in summary.get("X10", {}):
            r = summary["X10"][64]
            axs[0].loglog([64], [abs(r[f"TT {POL[p]}"]["amp_err_final"])], mk, mfc="none", color="k", ms=7,
                          label=(r"TT, $\epsilon\times10$" if p == 0 else None))
            axs[1].loglog([64], [abs(r[f"TT {POL[p]}"]["phase_err_final"])], mk, mfc="none", color="k", ms=7)
    for ax, (slopes, y0) in zip(axs, refs):
        for s in slopes:
            ax.loglog(Ns, y0 * (Ns / 16.0) ** (-s), color="grey", lw=0.8, ls="--")
            ax.text(Ns[-1] * 1.03, y0 * (Ns[-1] / 16.0) ** (-s), f"$N^{{-{s}}}$", fontsize=7, color="grey")
    for ax, tl in zip(axs, titles):
        ax.set_title(tl, fontsize=9)
        ax.set_xlabel("N", labelpad=-2)
        ax.set_xticks([16, 32, 48, 64])
        ax.set_xticklabels(["16", "32", "48", "64"])
        ax.minorticks_off()
    axs[0].legend(loc="lower left", fontsize=6)
    axs[2].legend(loc="lower left", fontsize=6)
    fs.save(fig, os.path.join(OUT, fname))


def y0(case, key, dg="TT"):
    return abs(summary[case][16][f"{dg} +"][key]) or 1e-6


conv_fig("F", "v3_F_conv", [((5, 7), y0("F", "amp_err_final")), ((4, 6), y0("F", "phase_err_final")),
                            ((6,), summary["F"][16]["TT-Wfd6 +"]["max"])])
conv_fig("X", "v3_X_conv", [((5, 7), y0("X", "amp_err_final")), ((4, 6), y0("X", "phase_err_final")),
                            ((6,), summary["X"][16]["TT-Wfd6 +"]["max"])])

# X: signal, background, x1 vs x10
fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 7.0), sharex=True)
fig.subplots_adjust(left=0.15, right=0.97, bottom=0.07, top=0.98, hspace=0.07)
tt = np.linspace(0, 10, 1000)
xw = exact.ExpandingWave()
axs[0].plot(tt, xw.mode.T(tt), **fs.GUIDE, label="exact $T(t)$")
for N in (16, 64):
    ts = TS[("X", N)]
    axs[0].plot(ts["t"], ts[("TT", 0, "H")], "o", ms=3, color=NCOL[N], label=f"TT $h_+/\\epsilon_+$, N={N}")
    axs[0].plot(ts["t"], ts[("TT", 1, "H")], "x", ms=4, color=NCOL[N], label=f"TT $h_\\times/\\epsilon_\\times$, N={N}")
axs[0].set_ylabel(r"$h/\epsilon$")
axs[0].legend(loc="upper right", fontsize=7, ncol=2)
for N in sorted(N for N in summary["X"] if isinstance(N, int)):
    ts = TS[("X", N)]
    axs[1].plot(ts["t"], ts["bg_a"], color=NCOL[N], label=f"$a$ from $\\chi$, N={N}")
    axs[1].plot(ts["t"], ts["bg_alpha"], color=NCOL[N], ls=":")
axs[1].set_ylabel(r"$a_{\rm num}/a_{\rm ex}-1$")
axs[1].set_yscale("symlog", linthresh=1e-12)
axs[1].legend(loc="lower left", fontsize=7, ncol=2)
for case, ls in (("X", "-"), ("X10", "--")):
    ts = TS[(case, 64)]
    for p, col in ((0, fs.PAL["blue"]), (1, fs.PAL["red"])):
        axs[2].plot(ts["t"][1:], np.abs(ts[("TT", p, "crel")][1:]), color=col, ls=ls,
                    label=f"{POL[p]}, " + (r"$\epsilon\times1$" if case == "X" else r"$\epsilon\times10$"))
axs[2].set_yscale("log")
axs[2].set_ylabel(r"$|Z-Z_{\rm ex}|/|Z_{\rm ex}|$, TT, N=64")
axs[2].set_xlabel("conformal time t", labelpad=-2)
axs[2].legend(loc="upper left", fontsize=7, ncol=2)
fs.save(fig, os.path.join(OUT, "v3_X_signal_bg_x10"))
print(json.dumps(summary, indent=1, default=str)[:20000])
