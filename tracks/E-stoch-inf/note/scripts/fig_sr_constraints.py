"""Figure: the Hamiltonian constraint of the slow-roll reproduction split into the parts odd
and even in the noise amplitude (criterion A4 and the reworded A4' adopted by decision 0021).

The amplitude scale of the noise (the code's noise_mode_scale, the ladder's s) is called lambda
in the note, because s is the steepness of the window there (NOTATION.md).
A mirrored pair of runs (lambda = +1 and -1, same Gaussian numbers) gives
H_odd = (H(+) - H(-))/2, first order in lambda, and H_even = (H(+) + H(-))/2, second order;
their rms over the box divided by the box mean of the term magnitude [H].
(a) odd (solid) and even (dashed) parts in the paper's set-up k_max = N/4 for N = 32, 64,
    128, 256 cells per side; ticks at ln(N/8) e-folds after the start, where the first
    shell with fewer than eight cells per wavelength enters the window; dotted: the floor
    model of the odd part, F(N, t) = odd_256(t) (N/256)^q, fitted on the convergence
    ladder (k_max = 8 dk) between 128^3 and 256^3.
(b) factor by which each part falls when lambda is halved (pairs +-1 and +-1/2): 2 for a
    first-order part, 4 for a second-order part, 1 for the amplitude-independent floor.

Inputs: the committed ladder/results/final/pair_{L32p_L32m, Q64p_Q64m, Q128p_Q128m,
P256_P256m}.json of the ladder's final analysis E-20261115-194633-9e04ed8 and
ladder/results/floor/floor.json of the floor analysis E-20261119-142713-32c883a, each checked
against the sha256 its run recorded. The last dump of the pairs whose partners ran to
different end times (64, 128, 256: t = 4.500 against 4.504-4.516) compares two different
times and is left out, as the floor analysis does (ladder JOURNAL entry 9).
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

FINAL = "ladder/results/final"
FLOOR = "ladder/results/floor/floor.json"
LCOL = {32: cz.PAL["yellow"], 64: cz.PAL["green"], 128: cz.PAL["blue"], 256: cz.PAL["red"]}
PAIRS = {32: "pair_L32p_L32m", 64: "pair_Q64p_Q64m", 128: "pair_Q128p_Q128m",
         256: "pair_P256_P256m"}
TMAX = 4.5 + 1e-9          # common end time of the s = -1 partners


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    fl = C.committed_json(FLOOR)
    fig = plt.figure(figsize=(7.0, 2.85))
    a = cz.inch_axes(fig, 0.74, 0.50, 3.24, 2.20)
    b = cz.inch_axes(fig, 4.72, 0.50, 2.15, 2.20)
    first = {}
    for n, name in PAIRS.items():
        rows = [r for r in C.committed_json(f"{FINAL}/{name}.json")["rows"] if r["time"] <= TMAX]
        x = np.array([r["efolds"] for r in rows])
        ho = np.array([r["H_odd"] for r in rows])
        he = np.array([r["H_even"] for r in rows])
        a.plot(x, ho, "o-", ms=2.4, lw=1.1, color=LCOL[n], label=rf"${n}^3$")
        a.plot(x, he, "s--", ms=1.8, lw=0.9, color=LCOL[n])
        xm = np.log(n / 8.0)
        a.plot([xm, xm], [2e-16, 6e-16], "-", color=LCOL[n], lw=2.0)
        a.plot(fl["efolds"], fl["floor"]["H_odd"]["model"][str(n)], ":", color=LCOL[n], lw=1.0)
        above = (ho > he) & (np.array([r["time"] for r in rows]) > 0.2)
        first[n] = float(x[np.argmax(above)]) if above.any() else None
    a.text(1.25, 2.4e-16, r"$\ln(N/8)$", fontsize=7.5, ha="right", va="bottom")
    a.plot([], [], "k-", lw=1.1, label="odd")
    a.plot([], [], "k--", lw=0.9, label="even")
    a.plot([], [], "k:", lw=1.0, label="floor model")
    a.set_yscale("log")
    a.set_ylim(1e-16, 3e-10)
    a.set_xlim(-0.15, 4.5)
    a.set_xlabel(r"$N-N_*$")
    a.set_ylabel(r"rms of the part of $\mathcal{H}$ / $\langle[\mathcal{H}]\rangle$")
    a.legend(frameon=False, fontsize=7, loc="upper left", ncol=2, handlelength=1.8, columnspacing=1.0)
    a.text(0.97, 0.05, "(a)", transform=a.transAxes, ha="right", fontsize=9)
    hv = fl["halving"]
    for n in (32, 64, 128):
        h = hv[f"N{n}"]
        b.plot(h["efolds"], h["H_odd"], "o-", ms=2.4, lw=1.1, color=LCOL[n])
        b.plot(h["efolds"], h["H_even"], "s--", ms=1.8, lw=0.9, color=LCOL[n])
    b.axhline(4.0, **cz.GUIDE)
    b.axhline(2.0, **cz.GUIDE)
    b.axhline(1.0, **cz.MASK_LINE)
    b.text(4.4, 4.15, "second order", fontsize=7, ha="right")
    b.text(4.4, 2.15, "first order", fontsize=7, ha="right")
    b.text(4.4, 1.15, "floor", fontsize=7, ha="right", color="0.4")
    b.set_ylim(0.0, 5.0)
    b.set_xlim(-0.15, 4.5)
    b.set_xlabel(r"$N-N_*$")
    b.set_ylabel(r"factor between $\lambda=1$ and $\lambda=1/2$")
    b.text(0.04, 0.05, "(b)", transform=b.transAxes, fontsize=9)
    cz.save(fig, os.path.join(out, "fig_sr_constraints"))
    # prediction N4: first dump with odd > even near ln(N/8); same as the floor analysis
    for n in PAIRS:
        ref = fl["crossing"][f"N{n}"]["first_dump_odd_gt_even"]
        print(f"fig_sr_constraints: N = {n}: first dump with odd > even at {first[n]:.3f} "
              f"e-folds (floor.json {ref:.3f}), ln(N/8) = {np.log(n / 8):.3f}")
        if first[n] is None or abs(first[n] - ref) > 1e-9:
            raise SystemExit("fig_sr_constraints: crossing differs from floor.json")


if __name__ == "__main__":
    main()
