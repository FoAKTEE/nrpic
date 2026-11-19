#!/usr/bin/env python3
"""Analysis of a scan.py run: fractions per (q, sense, r_p, model), phase-by-phase agreement,
figures. Usage: scan_figs.py <scan run dir> [outdir]   (outdir default $NRPIC_RUN_DIR)
Writes scan_summary.json, fig_scan_lines.{png,pdf}, fig_scan_phase.{png,pdf}.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402

CLASS = ["survived", "m2 ejected", "m1 ejected", "both bound", "both free", "unsettled",
         "captured", "merged"]
MODELS = ["newton", "hrna", "eih", "eihp"]
LABEL = dict(newton="Newton (full)", hrna="HRNA (hole fixed)", eih="EIH, v read as velocity",
             eihp="EIH, m v read as canonical momentum")
COL = dict(newton="grey", hrna=fs.PAL["green"], eih=fs.PAL["red"], eihp=fs.PAL["blue"])


def load(rundir):
    z = np.load(os.path.join(rundir, "scan.npz"))
    meta = json.load(open(os.path.join(rundir, "scan_meta.json")))
    data = {}
    for k in z.files:
        model, q, rp, sense, field = k.split("|")
        data.setdefault((model, q, float(rp), int(sense)), {})[field] = z[k]
    return data, meta


def summarize(d, model, meta):
    o = d["outcome"].astype(int)
    n = o.size
    fr = {c: float(np.mean(o == i)) for i, c in enumerate(CLASS)}
    s = dict(n=n, fractions=fr,
             separated=float(np.mean((o != 0) & (o != 5))),
             single_ejection=fr["m2 ejected"] + fr["m1 ejected"])
    single = (o == 1) | (o == 2)
    if model == "hrna":
        e = np.where(o == 1, d["E2_u"], np.where(o == 2, d["E1_u"], np.nan))
        s["captured"] = fr["captured"]
    else:
        e = np.where(single, d["E_out"], np.nan)
    if model in ("newton", "eih", "eihp"):
        # E_out of newton3.scatter / eih.scatter is already in newton3's unit
        s["inside_5.35M"] = float(np.mean(d["rMmin"] < meta.get("r_grcap", 5.35)))
        s["inside_12M"] = float(np.mean(d["rMmin"] < meta.get("r_trust", 12.0)))
        s["rMmin_median"] = float(np.median(d["rMmin"]))
    if model in ("eih", "eihp"):
        s["dE1PN_units_median_abs"] = float(np.median(np.abs(d["dE1PN_u"])))
        s["dE1PN_units_p90_abs"] = float(np.percentile(np.abs(d["dE1PN_u"]), 90))
        s["not_ok"] = int(np.sum(~d["ok"].astype(bool)))
    s["E_ej_units_mean"] = float(np.nanmean(e)) if np.any(single) else None
    s["E_ej_units_median"] = float(np.nanmedian(e)) if np.any(single) else None
    return s


def main():
    rundir = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    data, meta = load(rundir)
    for (model, q, rp, sense), d in data.items():
        d["_q"] = q
    summ = {}
    for (model, q, rp, sense), d in sorted(data.items()):
        summ.setdefault(q, {}).setdefault(str(sense), {}).setdefault(str(rp), {})[model] = \
            summarize(d, model, meta)
    # phase-by-phase agreement of the outcome classes
    agree = {}
    for q in ("q10", "q4"):
        for sense in (1, -1):
            for rp in meta["configs"][q]["rps"]:
                rp = float(rp)
                oc = {m: data[(m, q, rp, sense)]["outcome"].astype(int) for m in MODELS
                      if (m, q, rp, sense) in data}
                a = {}
                for i, m1 in enumerate(MODELS):
                    for m2 in MODELS[i + 1:]:
                        if m1 in oc and m2 in oc:
                            a[f"{m1}-{m2}"] = float(np.mean(oc[m1] == oc[m2]))
                summ[q][str(sense)][str(rp)]["agreement"] = a
    with open(os.path.join(out, "scan_summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)
    # ---------------------------------------------------------------- figure 1: scan lines
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharey=True)
    for r, q in enumerate(("q10", "q4")):
        for c, sense in enumerate((1, -1)):
            ax = axs[r, c]
            rps = [float(x) for x in meta["configs"][q]["rps"]]
            for m in MODELS:
                if (m, q, rps[0], sense) not in data:
                    continue
                sep = [summ[q][str(sense)][str(rp)][m]["separated"] for rp in rps]
                ax.plot(rps, sep, "o-", color=COL[m], label=LABEL[m], ms=4)
                if m == "hrna":
                    cap = [summ[q][str(sense)][str(rp)][m]["captured"] for rp in rps]
                    ax.plot(rps, cap, "x--", color=COL[m], lw=1, ms=5)
                elif m in ("eih", "eihp"):
                    cap = [summ[q][str(sense)][str(rp)][m]["inside_5.35M"] for rp in rps]
                    ax.plot(rps, cap, "x--", color=COL[m], lw=1, ms=5)
            ax.set_title(f"{q}, {'prograde' if sense > 0 else 'retrograde'}", fontsize=9)
            ax.set_ylim(-0.03, 1.03)
            ax.set_xlabel(r"Newtonian pericentre $r_p/M$")
            if c == 0:
                ax.set_ylabel("fraction of phases")
    axs[0, 0].legend(frameon=False, fontsize=6.5, loc="lower left")
    axs[0, 1].text(0.02, 0.02, "solid: binary separated\ndashed: HRNA capture (2.5 M);\n"
                   "EIH member inside 5.35 M", transform=axs[0, 1].transAxes, fontsize=6.5)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_scan_lines"))
    plt.close(fig)
    # ---------------------------------------------------------------- figure 2: phase scans
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["#DDDDDD", fs.PAL["yellow"], fs.PAL["orange"], "#7F3C8D",
                           "#11A579", "#AAAAAA", "k", "#E73F74"])
    fig, axs = plt.subplots(4, 2, figsize=(fs.FULL_WIDTH, 6.4),
                            gridspec_kw=dict(height_ratios=[1, 1.6, 1, 1.6]))
    for r, (q, rp) in enumerate((("q10", 8.0), ("q4", 9.82))):
        for c, sense in enumerate((1, -1)):
            ax = axs[2 * r, c]
            rows = []
            for m in MODELS:
                o = data[(m, q, rp, sense)]["outcome"].astype(int)
                rows.append(o)
            nph = rows[0].size
            ax.imshow(np.array(rows), aspect="auto", cmap=cmap, vmin=-0.5, vmax=7.5,
                      interpolation="nearest", extent=(0, 360, len(MODELS) - 0.5, -0.5))
            ax.set_yticks(range(len(MODELS)))
            ax.set_yticklabels(["Newton", "HRNA", "EIH v", "EIH p"], fontsize=7)
            ax.set_xticks([])
            ax.set_title(f"{q}, r_p = {rp:g} M, {'prograde' if sense > 0 else 'retrograde'}",
                         fontsize=8)
            ax2 = axs[2 * r + 1, c]
            ph = 360.0 * np.arange(nph) / nph
            for m in MODELS:
                d = data[(m, q, rp, sense)]
                if m == "hrna":
                    continue
                o = d["outcome"].astype(int)
                e = np.where((o == 1) | (o == 2), d["E_out"], np.nan)
                ax2.plot(ph, e, ".", ms=2, color=COL[m], label=LABEL[m])
                if m in ("eih", "eihp"):
                    ax2.plot(ph, d["rMmin"] / 10.0, "-", lw=0.6, color=COL[m], alpha=0.6)
            ax2.axhline(0.535, color="k", lw=0.6, ls=":")
            ax2.set_xlim(0, 360)
            ax2.set_ylim(0, 2.6)
            ax2.set_xlabel("effective phase [deg]")
            if c == 0:
                ax2.set_ylabel(r"$E_{\rm ej}$ [units]; $r_{\rm min}/10M$ (lines)", fontsize=7)
    axs[1, 0].legend(frameon=False, fontsize=6, loc="upper right", markerscale=3)
    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(color=cmap(i), label=CLASS[i]) for i in range(8)]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=6, frameon=False)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fs.save(fig, os.path.join(out, "fig_scan_phase"))
    plt.close(fig)
    print(json.dumps({q: {s: {rp: {m: dict(sep=v[m]["separated"],
                                            cap=v[m].get("captured", v[m].get("inside_5.35M")))
                                    for m in MODELS if m in v} for rp, v in d2.items()}
                          for s, d2 in d1.items()} for q, d1 in summ.items()}))


if __name__ == "__main__":
    main()
