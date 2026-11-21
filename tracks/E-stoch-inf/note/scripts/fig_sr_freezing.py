"""Figure: freezing of super-horizon modes in the slow-roll reproduction (criterion A3).

For the 256^3 run in the paper's set-up (P256), every lattice mode with N_f - N_k >= 6 (1051
modes, |n|^2 <= 62) is compared with the full Mukhanov-Sasaki solution of the same wave
vector and amplitude, and with the deformed equation of a lattice on a fixed Friedmann
background (FLRW lattice), which lacks the metric perturbations.
(a) power |R_n|^2 relative to its value at N_k + 4 against N - N_k: 60 modes drawn at
    random (seed 1) in the code and in the full solution; the deformed equation for the
    shells k/dk = 1 ... 6.7 of the reference run.
(b) |Q_n(N_f)/Q_n(N_k + 4) - 1| per mode, Q_n = |R^NR_n|^2/|R^lin_n|^2; for the deformed
    equation the same ratio of deformed over full power.
(c) drift of ln|R_n|^2 per e-fold from N_k + 4 to N_f (least-squares slope over the dumps).

Inputs:
- res/P256.npz and res/P256_judge_a3.npz of the ladder's final analysis
  E-20261115-194633-9e04ed8, read from its run directory by absolute path (the committed
  JSON hold only the extremes), checked against its sha256sums.txt; the A3 numbers are
  recomputed from P256.npz with the ladder's definitions (ladder_analysis.py, judge) and
  compared with P256_judge_a3.npz (prediction N4 of ../JOURNAL.md);
- quadratic.npz of the reference run E-stoch-inf-20261115-122806-ef0d039 (full and deformed
  Mukhanov-Sasaki modes per shell, Bunch-Davies from N_0), checked against its manifest.
The deformed curves end at N_* + 8, the end of the reference grid (the ladder's last dump
is 0.1 e-folds later).
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
REF = "E-stoch-inf-20261115-122806-ef0d039"
NR, MS, DEF = cz.PAL["red"], cz.PAL["blue"], "k"


def a3_from_npz(z):
    """Ratio and drifts of the ladder's judge (A3), recomputed."""
    rnr, lin = z["rnr"], z["lin"]
    nd = z["efolds_ref"]
    nk_mode = z["Nk"][z["shell_of"]]
    nf = float(nd[-1])
    idx = np.nonzero((nf - nk_mode) >= 6.0)[0]
    q = np.abs(rnr[:, idx]) ** 2 / np.abs(lin[:, idx]) ** 2
    ratio = np.empty(idx.size)
    dnr = np.empty(idx.size)
    dlin = np.empty(idx.size)
    for j, m in enumerate(idx):
        n4 = nk_mode[m] + 4.0
        ratio[j] = q[-1, j] / np.interp(n4, nd, q[:, j]) - 1.0
        use = nd >= n4 - 1e-9
        dnr[j] = np.polyfit(nd[use], np.log(np.abs(rnr[use, m]) ** 2), 1)[0]
        dlin[j] = np.polyfit(nd[use], np.log(np.abs(lin[use, m]) ** 2), 1)[0]
    return idx, nk_mode[idx], ratio, dnr, dlin


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    z = np.load(C.path(RUN, "res/P256.npz"))
    ref_a3 = np.load(C.path(RUN, "res/P256_judge_a3.npz"))
    idx, nk, ratio, dnr, dlin = a3_from_npz(z)
    nd = z["efolds_ref"]
    n2 = z["n2"][idx]
    # deformed and full equations of the reference run, shells inside the A3 set
    d = np.load(C.path(REF, "quadratic.npz"))
    kk = d["k"] / float(d["dk"])
    shells = np.nonzero(kk <= np.sqrt(62.0) + 1e-9)[0]
    Nr = d["N"] - float(d["Nstar"])
    def_rows = []
    for s in shells:
        n4 = float(d["Ncross"][s] - d["Nstar"]) + 4.0
        pms, pdf = np.abs(d["R_ms"][s]) ** 2, np.abs(d["R_def"][s]) ** 2
        use = (Nr >= n4) & (Nr <= Nr[-1])
        ratio_def = (pdf[-1] / np.interp(n4, Nr, pdf)) / (pms[-1] / np.interp(n4, Nr, pms)) - 1.0
        slope = np.polyfit(Nr[use], np.log(pdf[use]), 1)[0]
        def_rows.append((kk[s], n4 - 4.0, ratio_def, slope, Nr[use] - (n4 - 4.0),
                         pdf[use] / np.interp(n4, Nr, pdf)))

    fig = plt.figure(figsize=(7.0, 2.75))
    a = cz.inch_axes(fig, 0.72, 0.50, 1.62, 2.10)
    b = cz.inch_axes(fig, 3.08, 0.50, 1.55, 2.10)
    c = cz.inch_axes(fig, 5.30, 0.50, 1.55, 2.10)
    # (a) power relative to N_k + 4
    rng = np.random.default_rng(1)
    pick = np.sort(rng.choice(idx.size, 60, replace=False))
    for j in pick:
        m = idx[j]
        x = nd - nk[j]
        sel = x >= 3.0
        p_nr = np.abs(z["rnr"][:, m]) ** 2
        p_ms = np.abs(z["lin"][:, m]) ** 2
        a.plot(x[sel], p_nr[sel] / np.interp(nk[j] + 4, nd, p_nr), "-", color=NR, lw=0.6,
               alpha=0.5)
        a.plot(x[sel], p_ms[sel] / np.interp(nk[j] + 4, nd, p_ms), ":", color=MS, lw=0.8,
               alpha=0.6)
    for k_, nk_, r_, s_, x_, y_ in def_rows:
        a.plot(x_, y_, "--", color=DEF, lw=0.8)
    a.plot([], [], "-", color=NR, label="code")
    a.plot([], [], ":", color=MS, label="full equation")
    a.plot([], [], "--", color=DEF, label="FLRW lattice")
    a.axvline(4.0, **cz.MASK_LINE)
    a.axhspan(0.99, 1.01, color=NR, alpha=0.12, lw=0)
    a.set_xlim(3.0, 8.2)
    a.set_ylim(0.78, 1.04)
    a.set_xlabel(r"$N-N_k$")
    a.set_ylabel(r"$|\mathcal{R}_n|^2\,/\,|\mathcal{R}_n|^2_{N_k+4}$")
    a.legend(frameon=False, fontsize=7, loc="lower left", handlelength=1.8)
    a.text(0.95, 0.90, "(a)", transform=a.transAxes, ha="right", fontsize=9)
    # (b) ratio per mode
    k = np.sqrt(n2)
    b.plot(k, np.abs(ratio), ".", ms=2.0, color=NR)
    b.plot([r[0] for r in def_rows], [abs(r[2]) for r in def_rows], "s", ms=3.0, color=DEF)
    b.text(1.05, 0.33, "FLRW lattice", fontsize=7)
    b.axhline(0.01, **cz.GUIDE)
    b.text(1.05, 0.013, "threshold", fontsize=7)
    b.set_xscale("log")
    b.set_yscale("log")
    b.set_ylim(1e-10, 1.0)
    b.set_xticks([1, 2, 4, 8])
    b.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    b.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    b.set_xlabel(r"$k/k_{\sigma*}$")
    b.set_ylabel(r"$|Q_n(N_f)/Q_n(N_k+4)-1|$")
    b.text(0.95, 0.5, "(b)", transform=b.transAxes, ha="right", fontsize=9)
    # (c) drift per e-fold
    c.plot(k, np.abs(dnr), ".", ms=2.5, color=NR)
    c.plot(k, np.abs(dlin), ".", ms=1.0, color=MS)
    c.plot([r[0] for r in def_rows], [abs(r[3]) for r in def_rows], "s", ms=3.0, color=DEF)
    c.text(1.05, 0.11, "FLRW lattice", fontsize=7)
    c.axhline(2.5e-3, **cz.GUIDE)
    c.text(1.05, 3.2e-3, "threshold", fontsize=7)
    c.set_xscale("log")
    c.set_yscale("log")
    c.set_ylim(1e-5, 1.0)
    c.set_xticks([1, 2, 4, 8])
    c.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    c.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    c.set_xlabel(r"$k/k_{\sigma*}$")
    c.set_ylabel(r"$|\mathrm{d}\ln|\mathcal{R}_n|^2/\mathrm{d}N|$")
    c.text(0.95, 0.62, "(c)", transform=c.transAxes, ha="right", fontsize=9)
    cz.save(fig, os.path.join(out, "fig_sr_freezing"))
    # prediction N4: the recomputed A3 equals the ladder's judge
    diffs = dict(idx=int(np.abs(idx - ref_a3["idx"]).max()),
                 ratio=float(np.abs(ratio - ref_a3["ratio"]).max()),
                 drift_nr=float(np.abs(dnr - ref_a3["drift_nr"]).max()),
                 drift_lin=float(np.abs(dlin - ref_a3["drift_lin"]).max()))
    print(f"fig_sr_freezing: {idx.size} modes; max |ratio| {np.abs(ratio).max():.3e}, "
          f"max |drift| code {np.abs(dnr).max():.4e}, full {np.abs(dlin).max():.4e}, "
          f"max |code - full| {np.abs(dnr - dlin).max():.3e}; differences to the judge {diffs}")
    print("fig_sr_freezing: FLRW lattice: |ratio| " +
          ", ".join(f"{abs(r[2]):.3g}" for r in def_rows) + "; |drift| " +
          ", ".join(f"{abs(r[3]):.4g}" for r in def_rows))
    if diffs["idx"] or max(diffs["ratio"], diffs["drift_nr"], diffs["drift_lin"]) > 1e-12:
        raise SystemExit("fig_sr_freezing: recomputed A3 differs from P256_judge_a3.npz")


if __name__ == "__main__":
    main()
