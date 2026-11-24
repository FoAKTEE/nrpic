"""Figs. 2 and 4 of arXiv:2512.14649 (P1:444-463, fig:quad_contrast, fig:usr_contrast): 68, 95, 99, 100
per cent bands over the lattice, against the box-mean e-folds, of delta phi/phi_b, delta Pi/Pi_b,
delta K/K_b, R^NR and |H|/[H], |M|/[M], from the npz files of dumppass.py (one per dump).

Usage: fig_contrasts.py --pass DIR/LABEL [--pass DIR2/LABEL2 ...] --case sr|usr --name fig2 --out OUTDIR
       [--hzero]   (constraint panel with |H - <H>|/[H], the box mean of H removed)
Several --pass directories are merged by time (an original run and its continuation, or the field
panels of one run and the constraint panels of another: --cons-from LABEL picks the run whose dumps
carry [H], [M]). Writes <name>.{png,pdf} and <name>.json (band widths, entry span, maxima).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

# central bands: (lo, hi) indices into figlib.QUANT = [0, .5, 2.5, 16, 50, 84, 97.5, 99.5, 100]
BANDS = [(0, 8, "100"), (1, 7, "99"), (2, 6, "95"), (3, 5, "68")]
SHADES = [0.18, 0.38, 0.62, 0.95]


def load(dirs):
    rows = []
    for d in dirs:
        lab = os.path.basename(d.rstrip("/"))
        for p in sorted(glob.glob(os.path.join(d, "d*.npz"))):
            z = np.load(p)
            r = {k: z[k] for k in z.files if not k.startswith(("spec", "shell", "inj", "ms_"))}
            r["label"] = lab
            rows.append(r)
    rows.sort(key=lambda r: float(r["time"]))
    # drop duplicate times (the first dump of a continuation repeats the last of the original)
    out = []
    for r in rows:
        if out and abs(float(r["time"]) - float(out[-1]["time"])) < 1e-9:
            continue
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="passes", action="append", required=True)
    ap.add_argument("--case", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hzero", action="store_true")
    ap.add_argument("--title", default="")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rows = load(args.passes)
    N = np.array([float(r["efolds_chi"]) for r in rows])
    t = np.array([float(r["time"]) for r in rows])
    panels = [("pct_dphi", r"$\delta\phi/\phi_b$", "lin"), ("pct_dPi", r"$\delta\Pi/\Pi_b$", "lin"),
              ("pct_dK", r"$\delta K/K_b$", "lin"), ("pct_R", r"$\mathcal{R}^{\rm NR}$", "lin"),
              ("pct_H0" if args.hzero else "pct_H",
               r"$|\mathcal{H}-\langle\mathcal{H}\rangle|/[\mathcal{H}]$" if args.hzero
               else r"$|\mathcal{H}|/[\mathcal{H}]$", "log"),
              ("pct_M", r"$|\mathcal{M}|/[\mathcal{M}]$", "log")]
    res = dict(case=args.case, n_dumps=len(rows), times=t.tolist(), efolds=N.tolist(),
               labels=[str(r["label"]) for r in rows])
    fs.use_style()
    fig, ax = plt.subplots(len(panels), 1, figsize=(fs.COLUMN_WIDTH + 0.6, 11.0), sharex=True)
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.05, top=0.97, hspace=0.0)
    purple = np.array(matplotlib.colors.to_rgb("#7B1E7A"))
    for i, (key, lab, scale) in enumerate(panels):
        have = [key in r for r in rows]
        if not any(have):
            ax[i].text(0.5, 0.5, "not in these dumps", transform=ax[i].transAxes, ha="center")
            ax[i].set_ylabel(lab)
            continue
        sel = np.array(have)
        P = np.array([r[key] for r in rows if key in r])
        x = N[sel]
        for (lo, hi, name), a in zip(BANDS, SHADES):
            col = 1.0 - a * (1.0 - purple)
            ylo, yhi = P[:, lo], P[:, hi]
            if scale == "log":
                ylo = np.maximum(ylo, 1e-30)
            ax[i].fill_between(x, ylo, yhi, color=col, lw=0, label=f"{name} per cent")
        if scale == "log":
            ax[i].set_yscale("log")
            if key == "pct_M":
                ax[i].set_ylim(1e-9, 3.0)
            else:
                ax[i].set_ylim(max(1e-18, P[:, 1].min() / 3), P[:, 8].max() * 3)
        else:
            m = np.max(np.abs(P[:, [0, 8]]))
            ax[i].set_ylim(-1.25 * m, 1.25 * m)
            ax[i].ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
        ax[i].set_ylabel(lab)
        res[key] = dict(N=x.tolist(), p16=P[:, 3].tolist(), p84=P[:, 5].tolist(),
                        p0=P[:, 0].tolist(), p100=P[:, 8].tolist(), p995=P[:, 7].tolist(),
                        p99_upper=P[:, 7].tolist())
    ax[-1].set_xlabel(r"$\langle\mathcal{N}\rangle$")
    ax[-1].set_xlim(0, N.max())
    ax[0].legend(loc="upper left", fontsize=7, ncol=2)
    if args.title:
        ax[0].set_title(args.title, fontsize=10)
    fs.save(fig, os.path.join(args.out, args.name))
    plt.close(fig)
    # summary numbers
    w = lambda r, k: 0.5 * (float(r[k][5]) - float(r[k][3]))  # noqa: E731
    res["final"] = {k: dict(half68=w(rows[-1], k), max=float(np.max(np.abs(rows[-1][k][[0, 8]]))),
                            ratio100_68=float(np.max(np.abs(rows[-1][k][[0, 8]])) / w(rows[-1], k)))
                    for k in ("pct_dphi", "pct_dPi", "pct_dK", "pct_R") if k in rows[-1]}
    res["rms_R_final"] = float(rows[-1]["rms_R"])
    for k in ("pct_dphi", "pct_dPi", "pct_dK", "pct_R"):
        hw = np.array([w(r, k) for r in rows])
        res[k + "_half68"] = hw.tolist()
        # e-fold at which the 68 per cent width first reaches 95 per cent of its final value
        fin = hw[-1]
        idx = np.flatnonzero(hw >= 0.95 * fin)
        res[k + "_N95"] = float(N[idx[0]]) if idx.size else None
        res[k + "_maxhalf68"] = float(hw.max())
        res[k + "_N_maxhalf68"] = float(N[np.argmax(hw)])
    res["maxabsR_by_dump"] = [float(np.max(np.abs(r["pct_R"][[0, 8]]))) for r in rows]
    for key in ("pct_H", "pct_H0", "pct_M"):
        vals = [r for r in rows if key in r]
        if vals:
            res[key + "_p99_max"] = float(max(r[key][7] for r in vals))
            res[key + "_max_max"] = float(max(r[key][8] for r in vals))
            res[key + "_p84"] = [float(r[key][5]) for r in vals]
            res[key + "_p16"] = [float(r[key][3]) for r in vals]
    for key in ("avg_H", "avg_M", "avg_H0"):
        res[key] = [float(r[key]) for r in rows if key in r]
    res["cycles"] = [int(r["cycle"]) for r in rows]
    with open(os.path.join(args.out, args.name + ".json"), "w") as fp:
        json.dump(res, fp, indent=1)


if __name__ == "__main__":
    main()
