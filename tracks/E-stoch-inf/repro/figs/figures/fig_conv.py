"""Figs. 7 and 8 of arXiv:2512.14649 (P1:754-773): convergence with N = 32, 64, 128, 256 at
k_max/dk = 8 (noise_nmax2 = 64).

Fig. 8 (fig:Convergence): <|H|/[H]> (blue) and <|M|/[M]> (red) against the box-mean e-folds from the
records (columns 3 and 6, 0-based; one line per cycle, continuations joined), dotted / dash-dot /
dashed / solid for N = 32 / 64 / 128 / 256, both scenarios. For USR the box mean of H is also shown
removed (column 24, <|H - <H>|/[H]>, thin).
Fig. 7 (fig:specConvergence): |1 - Delta[R^NR]/Delta_lin| per shell (more than 10 modes) at the last
dump of the SR rungs, Delta_lin the realisation's linear spectrum (same alpha_n), from the npz files
of dumppass.py.

Usage: fig_conv.py --out OUT [--rung LABEL=npzdir ...] [--with256]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402
import runs as rr  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

LS = {32: ":", 64: "-.", 128: "--", 256: "-"}
ENTRY = np.log(8.0)          # e-folds of sourcing at k_max/dk = 8 (P1:756)


def entry_orders(recs):
    """Max of <|C|/[C]> over the entry (N <= ln 8) per N, and the order between neighbours."""
    out = {}
    for col, name in ((3, "H"), (6, "M"), (24, "H0")):
        mx = {}
        for n, d in recs.items():
            if d.shape[1] <= col:
                continue
            sel = (d[:, 2] <= ENTRY) & (d[:, 2] > 0.05)
            mx[n] = float(d[sel, col].max())
        ns = sorted(mx)
        out[name] = dict(entry_max=mx, orders={f"{a}-{b}": float(np.log2(mx[a] / mx[b]))
                                               for a, b in zip(ns[:-1], ns[1:])})
        # time-matched: median over N in [0.5, ENTRY] of log2(C_a/C_b) by interpolation
        tm = {}
        for a, b in zip(ns[:-1], ns[1:]):
            grid = np.linspace(0.5, ENTRY, 60)
            ya = np.interp(grid, recs[a][:, 2], recs[a][:, col])
            yb = np.interp(grid, recs[b][:, 2], recs[b][:, col])
            tm[f"{a}-{b}"] = float(np.median(np.log2(ya / yb)))
        out[name]["orders_time_matched"] = tm
        # decay after the entry: value at the end over the maximum after the entry
        out[name]["end_over_entry_end"] = {
            n: float(d[-1, col] / np.interp(ENTRY, d[:, 2], d[:, col])) for n, d in recs.items()
            if d.shape[1] > col}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--rung", action="append", default=[],
                    help="LABEL=npz directory of dumppass (SR rungs for Fig. 7)")
    ap.add_argument("--with256", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    fs.use_style()
    res = {}
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.14, top=0.91, wspace=0.0)
    for ax, case, labs in ((axes[0], "sr", ("C32S", "C64S", "C128S", "CL256S")),
                           (axes[1], "usr", ("C32U", "C64U", "C128U", "CL256U"))):
        recs = {}
        for lab in labs:
            if lab.startswith("CL256") and not args.with256:
                continue
            n = int(lab[1:-1]) if not lab.startswith("CL") else 256
            d = fl.read_con_joined(rr.con_paths(lab))
            recs[n] = d
            ax.semilogy(d[1:, 2], d[1:, 3], color=fs.PAL["blue"], ls=LS[n], lw=1.3)
            ax.semilogy(d[1:, 2], d[1:, 6], color=fs.PAL["red"], ls=LS[n], lw=1.3)
            if case == "usr" and d.shape[1] > 24:
                ax.semilogy(d[1:, 2], d[1:, 24], color=fs.PAL["blue"], ls=LS[n], lw=0.6,
                            alpha=0.6)
        res[case] = entry_orders(recs)
        res[case]["N_end"] = {n: float(d[-1, 2]) for n, d in recs.items()}
        res[case]["t_end"] = {n: float(d[-1, 0]) for n, d in recs.items()}
        ax.axvline(ENTRY, **fs.MASK_LINE)
        ax.set_xlabel(r"$\langle\mathcal{N}\rangle$")
        ax.set_title({"sr": "Quadratic inflation", "usr": "Inflection inflation"}[case],
                     fontsize=10)
        ax.set_xlim(0, max(d[-1, 2] for d in recs.values()))
    for n in (32, 64, 128, 256):
        axes[0].plot([], [], color="k", ls=LS[n],
                     label=f"N = {n}" + ("" if n < 256 or args.with256 else " (pending)"))
    # no shared tick label at the join of the two panels
    from matplotlib.ticker import MaxNLocator
    axes[1].xaxis.set_major_locator(MaxNLocator(nbins=6, prune="lower"))
    axes[0].plot([], [], color=fs.PAL["blue"], label=r"$\langle|\mathcal{H}|/[\mathcal{H}]\rangle$")
    axes[0].plot([], [], color=fs.PAL["red"], label=r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$")
    axes[0].legend(loc="upper right", fontsize=7, ncol=2)
    axes[1].plot([], [], color=fs.PAL["blue"], lw=0.6,
                 label=r"$\langle|\mathcal{H}-\langle\mathcal{H}\rangle|/[\mathcal{H}]\rangle$")
    axes[1].legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(args.out, "fig8_convergence"))
    plt.close(fig)

    # ---- Fig. 7
    if args.rung:
        fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH + 1.0, 3.4))
        fig.subplots_adjust(left=0.16, right=0.97, bottom=0.15, top=0.95)
        res["specconv"] = {}
        for item in args.rung:
            lab, d = item.split("=")
            n = 256 if lab.startswith("CL") else int(lab[1:-1])
            last = sorted(glob.glob(os.path.join(d, "d*.npz")))[-1]
            z = np.load(last)
            cnt = z["inj_count"]
            sel = cnt > 10
            r = np.abs(z["inj_pnr"] / z["inj_plin"] - 1.0)[sel]
            k = fl.k_p1(np.sqrt(z["inj_n2"][sel].astype(float)), "sr")
            ax.loglog(k, r, color=fs.PAL["blue"], ls=LS[n], lw=1.2, label=f"N = {n}")
            res["specconv"][n] = dict(file=last, time=float(z["time"]), N=float(z["efolds_chi"]),
                                      max=float(r.max()), median=float(np.median(r)),
                                      n_shells=int(sel.sum()),
                                      per_mode_rel_rms=float(z["inj_rel_rms"]))
        ns = sorted(res["specconv"])
        res["specconv_monotone"] = bool(all(res["specconv"][a]["max"] > res["specconv"][b]["max"]
                                            for a, b in zip(ns[:-1], ns[1:])))
        ax.set_xlabel(r"comoving wave number $k$ [$M_{\rm Pl}=100$]")
        ax.set_ylabel(r"$|1-\Delta[\mathcal{R}^{\rm NR}]/\Delta[\mathcal{R}]|$")
        ax.legend(loc="lower right", fontsize=8)
        fs.save(fig, os.path.join(args.out, "fig7_specconv"))
        plt.close(fig)
    with open(os.path.join(args.out, "fig7_fig8.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=str)
    print(json.dumps(res, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
