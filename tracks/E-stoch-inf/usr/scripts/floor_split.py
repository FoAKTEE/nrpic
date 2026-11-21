#!/usr/bin/env python3
"""Post-hoc floor reading of the constraint parts of group 1 (JOURNAL entry 12.1; not an
acceptance quantity). Reads the summary of analyse_cards.py --group g1 and, per dump, fits
part(s) = sqrt((s^p a)^2 + f^2) (p = 1 odd, p = 2 even) with one floor f per constraint,
independent of s and equal in the odd and even parts, from the odd parts at s = 1 and 1/2:

    a_odd^2 = 4 (o1^2 - oh^2) / 3,   f^2 = (4 oh^2 - o1^2) / 3,

then the floor-corrected even factor sqrt(E1^2 - f^2) / sqrt(Eh^2 - f^2).

    python3 floor_split.py --summary SUMMARY.json --out OUT
"""
import argparse
import json
import os

import numpy as np


def split(c1, ch, lab):
    o1 = np.array(c1[lab + "_odd_abs"])
    oh = np.array(ch[lab + "_odd_abs"])
    e1 = np.array(c1[lab + "_even_abs"])
    eh = np.array(ch[lab + "_even_abs"])
    f2 = (4.0 * oh**2 - o1**2) / 3.0
    resolved = f2 > 0
    f = np.sqrt(np.where(resolved, f2, 0.0))
    a_odd = np.sqrt(np.maximum(4.0 * (o1**2 - oh**2) / 3.0, 0.0))
    ok = resolved & (eh**2 > 2.0 * f**2)
    corr = np.sqrt(np.maximum(e1**2 - f**2, 0.0)) / np.sqrt(np.maximum(eh**2 - f**2, 1e-300))
    raw_even = e1 / eh
    raw_odd = o1 / oh
    at_floor = np.abs(raw_odd - 1.0) <= 0.05
    return dict(f=f, a_odd=a_odd, resolved=resolved, ok=ok, corr=corr, raw_even=raw_even,
                raw_odd=raw_odd, at_floor=at_floor, even_over_odd_1=e1 / o1, even_over_odd_h=eh / oh,
                o1=o1, oh=oh, e1=e1, eh=eh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    d = json.load(open(a.summary))
    c1 = d["U128p_U128m"]["constraints"]
    ch = d["U128hp_U128hm"]["constraints"]
    cN = np.array(c1["cN"])
    res = dict(source=a.summary, cN=cN.tolist())
    parts = {}
    for lab in ("H", "M"):
        r = split(c1, ch, lab)
        parts[lab] = r
        sel = r["ok"] & (cN > 0)
        fl = r["at_floor"] & (cN > 0)
        res[lab] = dict(
            f=r["f"].tolist(), resolved=r["resolved"].tolist(), judged=sel.tolist(),
            corrected_even_factor=r["corr"].tolist(), raw_even_factor=r["raw_even"].tolist(),
            raw_odd_factor=r["raw_odd"].tolist(),
            F1=dict(n=int(sel.sum()), min=float(r["corr"][sel].min()) if sel.any() else None,
                    max=float(r["corr"][sel].max()) if sel.any() else None,
                    within_010=int(np.sum(np.abs(r["corr"][sel] - 4.0) <= 0.10))),
            F2=dict(n=int(fl.sum()),
                    even_over_odd_s1=[float(x) for x in r["even_over_odd_1"][fl]],
                    even_over_odd_sh=[float(x) for x in r["even_over_odd_h"][fl]],
                    within_15pct=int(np.sum(np.abs(r["even_over_odd_1"][fl] - 1) <= 0.15)
                                     + np.sum(np.abs(r["even_over_odd_h"][fl] - 1) <= 0.15))))
        print(lab, "F1", res[lab]["F1"], "F2 n", res[lab]["F2"]["n"], "within", res[lab]["F2"]["within_15pct"],
              "of", 2 * res[lab]["F2"]["n"], flush=True)
        for i in range(cN.size):
            print(f"  cN {cN[i]:5.2f} f {r['f'][i]:.2e} a_odd {r['a_odd'][i]:.2e} odd x{r['raw_odd'][i]:.3f} "
                  f"even raw x{r['raw_even'][i]:.3f} corr x{r['corr'][i]:.3f} judged {bool(r['ok'][i] and cN[i] > 0)} "
                  f"e/o(1) {r['even_over_odd_1'][i]:.2f} e/o(1/2) {r['even_over_odd_h'][i]:.2f}")
    with open(os.path.join(a.out, "floor_split.json"), "w") as fp:
        json.dump(res, fp, indent=1)

    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.series_colors(4)
    fig, ax = plt.subplots(2, 2, figsize=(fs.COLUMN_WIDTH * 2.0, 5.6), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.95, bottom=0.1, hspace=0.1, wspace=0.28)
    usr = (2.5235, 6.5503)
    for j, lab in enumerate(("H", "M")):
        r = parts[lab]
        x = cN[1:]
        a0 = ax[0, j]
        a0.axvspan(*usr, color=fs.PAL["yellow"], alpha=0.15, lw=0)
        for y in (2.0, 4.0):
            a0.axhspan(y - 0.1, y + 0.1, color="0.88", lw=0)
        a0.plot(x, r["raw_even"][1:], color=cols[0], marker="s", ms=3, lw=0.8, label="even, raw")
        jd = (r["ok"] & (cN > 0))[1:]
        a0.plot(x[jd], r["corr"][1:][jd], color=cols[2], marker="o", ms=4, ls="none", label="even, floor removed (judged)")
        a0.plot(x, r["raw_odd"][1:], color=cols[1], marker="^", ms=3, lw=0.8, label="odd, raw")
        a0.set_ylim(0.0, 5.0)
        a0.set_title(("Hamiltonian" if lab == "H" else "momentum") + ", 128$^3$, s = 1 over 1/2", fontsize=8)
        a0.set_ylabel("factor under halving")
        a0.legend(loc="lower left", fontsize=6)
        a1 = ax[1, j]
        a1.axvspan(*usr, color=fs.PAL["yellow"], alpha=0.15, lw=0)
        a1.semilogy(x, r["o1"][1:], color=cols[1], marker="^", ms=3, lw=0.8, label="odd, s = 1")
        a1.semilogy(x, r["e1"][1:], color=cols[0], marker="s", ms=3, lw=0.8, label="even, s = 1")
        a1.semilogy(x, r["oh"][1:], color=cols[1], ls="--", lw=0.8, label="odd, s = 1/2")
        a1.semilogy(x, r["eh"][1:], color=cols[0], ls="--", lw=0.8, label="even, s = 1/2")
        fr = r["resolved"][1:]
        a1.semilogy(x[fr], r["f"][1:][fr], color="k", marker="x", ms=4, ls="none", label="floor f (fit)")
        a1.set_xlabel(r"$N-N_*$")
        a1.set_ylabel("rms part (absolute)")
        a1.legend(loc="best", fontsize=6, ncol=2)
    fs.save(fig, os.path.join(a.out, "fig", "fig_card_g1_floor"))
    plt.close(fig)
    print("done", flush=True)


if __name__ == "__main__":
    main()
