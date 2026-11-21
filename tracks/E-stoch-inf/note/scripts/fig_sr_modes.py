"""Figure: per-mode amplitudes of the slow-roll reproduction (criterion A2).

Panel (a): deviation D_n = |R^NR_n / (W_k R_k alpha_n) - 1| of every lattice mode at the last
dump, against |n| = k / k_sigma*, for the 256^3 run in the paper's set-up (k_max = 64 dk,
P256) and the convergence ladder (k_max = 8 dk, 32^3 to 256^3; the 256^3 rung ran to 4.4
e-folds only). Panel (b): the largest D_n over the modes inside the window (W > 1/2)
against the e-folds since the start.

Inputs (registered analysis E-20261115-194633-9e04ed8 of the ladder):
- the per-mode arrays res/{P256,L32p,L64p,L128p,L256p}.npz, read from the run directory by
  absolute path (the committed JSON of ladder/results/final/ hold only the maxima), each
  checked against the run's sha256sums.txt;
- the committed ladder/results/final/{P256,L32p,L64p,L128p,L256p}_judge.json (A2 history),
  checked against the same file.
The script recomputes the maximum over |n| <= k_max/2 and stops if it differs from the
committed summary.json (prediction N4 of ../JOURNAL.md).
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402

RUN = "E-20261115-194633-9e04ed8"
FINAL = "ladder/results/final"
LCOL = {32: cz.PAL["yellow"], 64: cz.PAL["green"], 128: cz.PAL["blue"], 256: cz.PAL["red"]}


def last_dev(z):
    d = np.abs(z["rnr"][-1] / z["lin"][-1] - 1.0)
    n2 = z["n2"]
    half = n2 <= n2.max() / 4.0
    mx = np.zeros(z["kshell"].size)
    np.maximum.at(mx, z["shell_of"], d)
    return d, n2, half, mx


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    summ = C.committed_json(f"{FINAL}/summary.json")
    fig = plt.figure(figsize=(7.0, 2.85))
    a = cz.inch_axes(fig, 0.62, 0.50, 2.85, 2.20)
    b = cz.inch_axes(fig, 4.12, 0.50, 2.75, 2.20)
    checks = []
    # (a) per mode at the last dump
    z = np.load(C.path(RUN, "res/P256.npz"))
    d, n2, half, mx = last_dev(z)
    a.plot(np.sqrt(n2), d, ".", ms=0.8, color="0.65", alpha=0.35, rasterized=True, zorder=1)
    a.plot(z["kshell"], mx, "-", color="k", lw=1.0, zorder=3)
    a.text(66, 6e-3, r"$256^3$, $k_{\max}=64\,\Delta k$", fontsize=7.5, ha="right")
    checks.append(("P256", float(d[half].max()), summ["A2"]["P256"]["max_D_half"]))
    for n in (32, 64, 128, 256):
        tag = f"L{n}p"
        z = np.load(C.path(RUN, f"res/{tag}.npz"))
        d, n2, half, mx = last_dev(z)
        a.plot(z["kshell"], mx, "o-", ms=2.2, lw=1.0, color=LCOL[n], zorder=4)
        checks.append((tag, float(d[half].max()), summ["A2"][tag]["max_D_half"]))
    a.axhline(0.02, **cz.GUIDE)
    a.text(1.05, 0.03, "threshold", fontsize=8)
    a.text(1.05, 1.5e-5, r"ladder, $k_{\max}=8\,\Delta k$", fontsize=7.5)
    for x, lab in ((4, r"$k_{\max}/2$" "\n" "(ladder)"), (32, r"$k_{\max}/2$" "\n" r"($256^3$)")):
        a.axvline(x, **cz.MASK_LINE)
        a.text(x * 0.92, 4e-8, lab, fontsize=7, ha="right", va="bottom", color="0.35")
    a.set_xscale("log")
    a.set_yscale("log")
    a.set_xlim(0.9, 72)
    a.set_ylim(1e-8, 0.2)
    a.set_xticks([1, 2, 4, 8, 16, 32, 64])
    a.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    a.set_xlabel(r"$k/k_{\sigma*}$")
    a.set_ylabel(r"$D_n$ at the last dump")
    a.text(0.97, 0.05, "(a)", transform=a.transAxes, ha="right", fontsize=9)
    # (b) history inside the window
    for n in (32, 64, 128, 256):
        h = [r for r in C.committed_json(f"{FINAL}/L{n}p_judge.json")["A2_history"]
             if r["max_D_in"] is not None]
        b.plot([r["efolds"] for r in h], [r["max_D_in"] for r in h], "o-", ms=2.2, lw=1.0,
               color=LCOL[n], label=rf"${n}^3$, $k_{{\max}}=8\,\Delta k$")
    h = [r for r in C.committed_json(f"{FINAL}/P256_judge.json")["A2_history"]
         if r["max_D_in"] is not None]
    b.plot([r["efolds"] for r in h], [r["max_D_in"] for r in h], "s-", ms=2.2, lw=1.0,
           color="k", label=r"$256^3$, $k_{\max}=64\,\Delta k$")
    b.plot([r["efolds"] for r in h], [r["max_D_in_half"] for r in h], "s--", ms=2.2, lw=1.0,
           color="0.45", label=r"same, $k\leq k_{\max}/2$")
    b.axhline(0.02, **cz.GUIDE)
    b.set_yscale("log")
    b.set_ylim(1e-12, 0.2)
    b.set_xlim(-0.2, 8.4)
    b.set_xlabel(r"$N-N_*$")
    b.set_ylabel(r"largest $D_n$ inside the window")
    b.legend(frameon=False, fontsize=6.5, loc="lower right", ncol=1, handlelength=1.6)
    b.text(0.04, 0.05, "(b)", transform=b.transAxes, fontsize=9)
    cz.save(fig, os.path.join(out, "fig_sr_modes"))
    bad = []
    for tag, got, want in checks:
        rel = abs(got / want - 1.0)
        print(f"fig_sr_modes: {tag} max D_n over |n| <= k_max/2 = {got:.6e} "
              f"(summary.json {want:.6e}, relative difference {rel:.1e})")
        if rel > 1e-12:
            bad.append(tag)
    if bad:
        raise SystemExit(f"fig_sr_modes: recomputed A2 differs from summary.json for {bad}")


if __name__ == "__main__":
    main()
