#!/usr/bin/env python3
"""Figures of the ladder package from the outputs of analyse_all.py (style:
figstyle.py, copied from harness/style/).

    make_figures.py --res DIR --out DIR

fig_a2_modes      per-mode deviation D_n of R^NR from the linear solution (A2)
fig_a3_freezing   super-horizon power relative to N_k + 4 and the drift per mode (A3)
fig_spectrum      shell spectrum at N_f against the linear and slow-roll results
fig_constraints   <|H|/[H]>, <|M|/[M]> of the record, L ladder and paper set-up
fig_a5_parts      odd and even parts of H, M on the L ladder and the order of the odd part
fig_a4_paper      odd and even parts at the paper's set-up (P256, Q128, Q64, L32) and
                  the halving factors; negative controls
"""
import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import figstyle as fs  # noqa: E402

LCOL = {32: fs.PAL["yellow"], 64: fs.PAL["green"], 128: fs.PAL["blue"], 256: fs.PAL["red"]}


def load(res, name):
    p = os.path.join(res, name)
    if not os.path.isfile(p):
        return None
    if p.endswith(".npz"):
        return np.load(p)
    with open(p) as fp:
        return json.load(fp)


def fig_a2(res, out):
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.93, wspace=0.25)
    ax = axs[0]
    z = load(res, "P256.npz")
    if z is not None and z["rnr"].shape[0]:
        d = np.abs(z["rnr"][-1] / z["lin"][-1] - 1)
        k = np.sqrt(z["n2"])
        ax.plot(k, d, ".", ms=1.0, color="grey", alpha=0.25, rasterized=True)
        # shell maxima
        sh = z["shell_of"]
        mx = np.zeros(z["kshell"].size)
        np.maximum.at(mx, sh, d)
        ax.plot(z["kshell"], mx, "-", color=fs.PAL["red"], lw=1.0,
                label=r"$256^3$, $k_{\max}=64$: shell max")
        ax.axvline(32, **fs.MASK_LINE)
    for n in (32, 64, 128, 256):
        z = load(res, f"L{n}p.npz")
        if z is None or not z["rnr"].shape[0]:
            continue
        d = np.abs(z["rnr"][-1] / z["lin"][-1] - 1)
        mx = np.zeros(z["kshell"].size)
        np.maximum.at(mx, z["shell_of"], d)
        ax.plot(z["kshell"], mx, "o-", ms=2.5, lw=1.0, color=LCOL[n],
                label=rf"$N={n}$, $k_{{\max}}=8$, $\mathcal{{N}}={z['efolds_ref'][-1]:.1f}$")
    ax.axhline(0.02, **fs.GUIDE)
    ax.text(1.1, 0.012, "A2 threshold", fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([1, 2, 4, 8, 16, 32, 64])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel(r"$k/k_\sigma^*=|n|$")
    ax.set_ylabel(r"$|R^{\rm NR}_n/(W_kR_k\alpha_n)-1|$ at the last dump")
    ax.legend(fontsize=7, loc="lower right", ncol=1)
    ax = axs[1]
    for n in (32, 64, 128, 256):
        z = load(res, f"L{n}p_judge.json")
        if z is None:
            continue
        h = [r for r in z["A2_history"] if r["max_D_in"] is not None]
        ax.plot([r["efolds"] for r in h], [r["max_D_in"] for r in h], "o-", ms=2.5,
                color=LCOL[n], label=rf"L, $N={n}$")
    z = load(res, "P256_judge.json")
    if z is not None:
        h = [r for r in z["A2_history"] if r["max_D_in"] is not None]
        ax.plot([r["efolds"] for r in h], [r["max_D_in"] for r in h], "s--", ms=2.5,
                color=fs.PAL["red"], label=r"P, $256^3$ all modes")
        ax.plot([r["efolds"] for r in h], [r["max_D_in_half"] for r in h], "s:", ms=2.5,
                color=fs.PAL["orange"], label=r"P, $256^3$, $|n|\leq32$")
    ax.axhline(0.02, **fs.GUIDE)
    ax.set_yscale("log")
    ax.set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    ax.set_ylabel(r"max over modes with $W>1/2$")
    ax.legend(fontsize=7, ncol=2, loc="lower right")
    fs.save(fig, os.path.join(out, "fig_a2_modes"))
    plt.close(fig)


def fig_a3(res, out):
    for tag in ("P256", "Q128p", "L128p", "L64p", "L32p"):
        z, a3 = load(res, f"{tag}.npz"), load(res, f"{tag}_judge_a3.npz")
        if z is not None and a3 is not None:
            break
    else:
        return
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.91, wspace=0.36)
    ax = axs[0]
    nd = z["efolds_ref"]
    q_nr = np.abs(z["rnr"])**2
    q_lin = np.abs(z["lin"])**2
    eps1 = 4 * np.pi * z["con"][:, 17]**2 / (z["con"][:, 18] / 3.0)**2
    e1m = float(np.mean(eps1))
    rng = np.random.default_rng(1)
    pick = a3["idx"] if a3["idx"].size <= 60 else np.sort(rng.choice(a3["idx"], 60, False))
    for m in pick:
        nk = z["Nk"][z["shell_of"][m]]
        x = nd - nk
        p4 = np.interp(nk + 4, nd, q_nr[:, m])
        l4 = np.interp(nk + 4, nd, q_lin[:, m])
        sl = x >= 3.0
        ax.plot(x[sl], q_nr[sl, m] / p4, "-", color=fs.PAL["red"], lw=0.6, alpha=0.5)
        ax.plot(x[sl], q_lin[sl, m] / l4, ":", color=fs.PAL["blue"], lw=0.6, alpha=0.5)
    xx = np.linspace(4, 8.1, 50)
    ax.plot(xx, np.exp(-4 * e1m * (xx - 4)), **fs.GUIDE)
    ax.text(5.9, 0.905, r"FLRW lattice" "\n" r"$e^{-4\epsilon_1(\mathcal{N}-\mathcal{N}_k-4)}$",
            fontsize=7)
    fs.band(ax, xx, 0.99 + 0 * xx, 1.01 + 0 * xx, fs.PAL["red"])
    ax.plot([], [], "-", color=fs.PAL["red"], label=r"NR")
    ax.plot([], [], ":", color=fs.PAL["blue"], label="full MS")
    ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_k$")
    ax.set_ylabel(r"$|R_n|^2/|R_n|^2(\mathcal{N}_k+4)$")
    ax.set_ylim(0.78, 1.04)
    ax.legend(fontsize=7, loc="center left")
    ax.set_title(f"{tag}: {a3['idx'].size} modes, "
                 r"$\mathcal{N}_f-\mathcal{N}_k\geq6$", fontsize=8)
    k = np.sqrt(a3["n2"])
    ax = axs[1]
    ax.plot(k, np.abs(a3["ratio"]), ".", ms=2, color=fs.PAL["red"])
    ax.axhline(0.01, **fs.GUIDE)
    ax.axhline(1 - np.exp(-4 * e1m * 2), **fs.REF_LINE)
    ax.text(1.05, 0.0135, "A3 threshold", fontsize=7)
    ax.text(1.05, 0.11, "FLRW lattice", fontsize=7)
    ax.set_yscale("log")
    ax.set_ylim(top=1.0)
    ax.set_xlabel(r"$|n|$")
    ax.set_ylabel(r"$|Q_n(\mathcal{N}_f)/Q_n(\mathcal{N}_k+4)-1|$")
    ax = axs[2]
    ax.plot(k, np.abs(a3["drift_nr"]), ".", ms=2.5, color=fs.PAL["red"], label="NR")
    ax.plot(k, np.abs(a3["drift_lin"]), ".", ms=1.2, color=fs.PAL["blue"], label="full MS")
    ax.axhline(2.5e-3, **fs.GUIDE)
    ax.axhline(4 * e1m, **fs.REF_LINE)
    ax.text(1.05, 3.2e-3, "A3 threshold", fontsize=7)
    ax.text(1.05, 4 * e1m * 1.25, r"$4\epsilon_1$ (FLRW lattice)", fontsize=7)
    ax.set_yscale("log")
    ax.set_ylim(top=0.3)
    ax.set_xlabel(r"$|n|$")
    ax.set_ylabel(r"$|d\ln|R_n|^2/d\mathcal{N}|$ from $\mathcal{N}_k+4$")
    ax.legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(out, "fig_a3_freezing"))
    plt.close(fig)


def fig_spectrum(res, out):
    for tag in ("P256", "Q128p", "L128p", "L64p", "L32p"):
        s = load(res, f"{tag}_judge_spec.npz")
        if s is not None:
            break
    else:
        return
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH + 1.5, 4.6), sharex=True,
                            gridspec_kw=dict(height_ratios=[2, 1]))
    fig.subplots_adjust(left=0.19, right=0.97, bottom=0.10, top=0.97, hspace=0.0)
    ax = axs[0]
    ax.plot(s["k"], s["d_nr"], ".", ms=2.5, color=fs.PAL["red"], label=r"NR, shells")
    ax.plot(s["k"], s["d_ens"], "-", color=fs.PAL["blue"], label="full MS (ensemble)")
    ax.plot(s["k"], s["d_sr"], **fs.GUIDE, label=r"$H_k^2/(8\pi^2\epsilon_{1k}M_{\rm Pl}^2)$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylabel(r"$\Delta_\mathcal{R}(k)$ at $\mathcal{N}_f$")
    ax.legend(fontsize=8, loc="lower left", title=tag, title_fontsize=8)
    ax = axs[1]
    sig = 1 / np.sqrt(s["cnt"])
    fs.band(ax, s["k"], 1 - sig, 1 + sig, fs.PAL["blue"])
    ax.plot(s["k"], s["d_nr"] / s["d_ens"], ".", ms=2.5, color=fs.PAL["red"],
            label="NR / ensemble")
    ax.plot(s["k"], s["d_nr"] / s["d_lin"], "-", color="k", lw=1.0,
            label=r"NR / reference with the same $\alpha_n$")
    ax.axhline(1.0, **fs.MASK_LINE)
    ax.set_xticks([1, 2, 4, 8, 16, 32, 64])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel(r"$k/k_\sigma^*$")
    ax.set_ylabel("ratio")
    ax.set_ylim(0.0, 2.0)
    ax.legend(fontsize=7, loc="upper right")
    fs.save(fig, os.path.join(out, "fig_spectrum"))
    plt.close(fig)


def fig_constraints(res, out):
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.0), sharex="col")
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.95, hspace=0.05,
                        wspace=0.25)
    for col, group in enumerate(("L", "P")):
        names = [f"L{n}p" for n in (32, 64, 128, 256)] if group == "L" else \
            ["L32p", "Q64p", "Q128p", "P256", "NC32p", "NC64p", "NC128p"]
        for name in names:
            z = load(res, f"{name}.npz")
            if z is None:
                continue
            c = z["con"]
            n = int(name.strip("LQNCPpm") or 256)
            ls = "--" if name.startswith("NC") else "-"
            lab = name if not name.startswith("NC") else f"{name} (sign flipped)"
            axs[0, col].plot(c[:, 2], c[:, 3], ls, color=LCOL[n], lw=1.0, label=lab)
            axs[1, col].plot(c[:, 2], c[:, 6], ls, color=LCOL[n], lw=1.0)
        axs[0, col].axhline(1e-10, **fs.MASK_LINE)
        axs[0, col].set_yscale("log")
        axs[1, col].set_yscale("log")
        axs[1, col].set_xlabel(r"e-folds $-\ln\langle\chi\rangle/2$")
        axs[0, col].legend(fontsize=7, ncol=2, loc="lower right")
        axs[0, col].set_title(r"$k_{\max}/dk=8$ (convergence set-up)" if group == "L"
                              else r"$k_{\max}=N/4$ (paper set-up) and controls", fontsize=9)
    axs[0, 0].set_ylabel(r"$\langle|\mathcal{H}|/[\mathcal{H}]\rangle$")
    axs[1, 0].set_ylabel(r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$")
    fs.save(fig, os.path.join(out, "fig_constraints"))
    plt.close(fig)


def pair_rows(res, p, m):
    z = load(res, f"pair_{p}_{m}.json")
    return None if z is None else z["rows"]


def fig_a5(res, out):
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.0), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.95, hspace=0.05,
                        wspace=0.25)
    rows = {n: pair_rows(res, f"L{n}p", f"L{n}m") for n in (32, 64, 128, 256)}
    for n, r in rows.items():
        if r is None:
            continue
        x = [q["efolds"] for q in r]
        for col, c in enumerate(("H", "M")):
            axs[0, col].plot(x, [q[f"{c}_odd"] for q in r], "o-", ms=2.5, color=LCOL[n],
                             label=rf"odd, $N={n}$")
            axs[0, col].plot(x, [q[f"{c}_even"] for q in r], "s--", ms=2.0, color=LCOL[n],
                             lw=1.0, label=rf"even, $N={n}$")
    for col, c in enumerate(("H", "M")):
        for n in (32, 64, 128):
            r1, r2 = rows.get(n), rows.get(2 * n)
            if r1 is None or r2 is None:
                continue
            m = min(len(r1), len(r2))
            x = [r1[i]["efolds"] for i in range(m)]
            o = [np.log2(r1[i][f"{c}_odd"] / r2[i][f"{c}_odd"]) for i in range(m)]
            axs[1, col].plot(x, o, "o-", ms=3, color=LCOL[2 * n], label=rf"${n}\to{2*n}$")
        axs[1, col].axhspan(4, 6, color=fs.PAL["blue"], alpha=0.1)
        axs[1, col].axhline(6, **fs.GUIDE)
        axs[1, col].set_ylim(0, 9)
        axs[0, col].set_yscale("log")
        axs[1, col].set_xlabel(r"e-folds")
        axs[1, col].legend(fontsize=7, loc="lower right")
    axs[0, 0].legend(fontsize=6, ncol=2, loc="lower right")
    axs[0, 0].set_ylabel(r"rms$/\langle[\mathcal{H}]\rangle$")
    axs[0, 1].set_ylabel(r"rms$/\langle[\mathcal{M}]\rangle$")
    axs[1, 0].set_ylabel(r"order of the odd part of $\mathcal{H}$")
    axs[1, 1].set_ylabel(r"order of the odd part of $\mathcal{M}$")
    fs.save(fig, os.path.join(out, "fig_a5_parts"))
    plt.close(fig)


def fig_a4(res, out):
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.91, wspace=0.32)
    sets = [("L32p", "L32m", "L32ph", "L32mh", 32), ("Q64p", "Q64m", "Q64ph", "Q64mh", 64),
            ("Q128p", "Q128m", "Q128ph", "Q128mh", 128), ("P256", "P256m", None, None, 256)]
    for p, m, ph, mh, n in sets:
        r = pair_rows(res, p, m)
        if r is None:
            continue
        x = [q["efolds"] for q in r]
        axs[0].plot(x, [q["H_odd"] for q in r], "o-", ms=2.5, color=LCOL[n],
                    label=rf"odd, $N={n}$")
        axs[0].plot(x, [q["H_even"] for q in r], "s--", ms=2, lw=1.0, color=LCOL[n],
                    label=rf"even, $N={n}$")
        if ph is not None:
            rh = pair_rows(res, ph, mh)
            if rh is not None:
                mm = min(len(r), len(rh))
                axs[1].plot(x[:mm], [r[i]["H_even"] / rh[i]["H_even"] for i in range(mm)],
                            "s--", ms=2.5, color=LCOL[n], label=rf"even, $N={n}$")
                axs[1].plot(x[:mm], [r[i]["H_odd"] / rh[i]["H_odd"] for i in range(mm)],
                            "o-", ms=2.5, color=LCOL[n], label=rf"odd, $N={n}$")
                axs[1].plot(x[:mm], [r[i]["ratio_H_p"] / rh[i]["ratio_H_p"] for i in range(mm)],
                            "-", lw=2.5, alpha=0.4, color=LCOL[n])
    axs[1].axhline(4, **fs.GUIDE)
    axs[1].axhline(2, **fs.REF_LINE)
    axs[0].set_yscale("log")
    axs[0].set_ylabel(r"rms of $\mathcal{H}$ parts$/\langle[\mathcal{H}]\rangle$")
    axs[1].set_ylabel(r"factor between $s=1$ and $s=1/2$")
    axs[1].set_ylim(0, 6)
    axs[0].legend(fontsize=6, ncol=2, loc="lower right")
    axs[1].legend(fontsize=6, ncol=2, loc="upper left")
    axs[0].set_title(r"paper set-up $k_{\max}=N/4$", fontsize=9)
    axs[1].set_title("halving test (thick: record ratio)", fontsize=9)
    for n, (p, m) in {32: ("L32p", "NC32p"), 64: ("Q64p", "NC64p"),
                      128: ("Q128p", "NC128p")}.items():
        zp, zn = load(res, f"{p}.npz"), load(res, f"{m}.npz")
        if zp is None or zn is None:
            continue
        cp, cn = zp["con"], zn["con"]
        mm = min(len(cp), len(cn))
        axs[2].plot(cn[:mm, 2], cn[:mm, 3] / cp[:mm, 3], "-", color=LCOL[n],
                    label=rf"$\mathcal{{H}}$, $N={n}$")
        axs[2].plot(cn[:mm, 2], cn[:mm, 6] / cp[:mm, 6], "--", color=LCOL[n],
                    label=rf"$\mathcal{{M}}$, $N={n}$")
    axs[2].set_yscale("log")
    axs[2].set_ylabel("sign-flipped / proper (record)")
    axs[2].set_title("negative control", fontsize=9)
    axs[2].legend(fontsize=6, ncol=2)
    for ax in axs:
        ax.set_xlabel("e-folds")
    fs.save(fig, os.path.join(out, "fig_a4_paper"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fs.use_style()
    os.makedirs(a.out, exist_ok=True)
    for f in (fig_a2, fig_a3, fig_spectrum, fig_constraints, fig_a5, fig_a4):
        try:
            f(a.res, a.out)
            print("made", f.__name__)
        except Exception as e:          # a missing run must not stop the other figures
            print("skipped", f.__name__, type(e).__name__, e)


if __name__ == "__main__":
    main()
