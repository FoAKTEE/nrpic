"""The sign-flip control of arXiv:2512.14649 (P1:541; map S16; scope prediction P3): records of the SR
run with the Pi kick of the noise reversed (RNC256, noise_pi_sign = -1, to t = 4.5) against the proper
run (RSF256, else P256v6), cycle by cycle; and the USR control U256nc (to t = 3.75) against U256ap.

Measures: ratio of <|H|/[H]> (flipped over proper) at every common cycle with N in [0.5, ln 64];
the largest <|M|/[M]> of the flipped run. Writes fig_signflip.{png,pdf} and fig_signflip.json.

Usage: fig_signflip.py OUT
"""
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

RUNS_EXTRA = {"U256nc": ("E-20261122-190341-0419be6", "", "usr")}


def rec(label):
    if label in RUNS_EXTRA:
        rid, sub, base = RUNS_EXTRA[label]
        return fl.read_con_joined([os.path.join(rr.SCR, rid, base + ".sf.con.hst")])
    return fl.read_con_joined(rr.con_paths(label))


def compare(flip, proper):
    a, b = rec(flip), rec(proper)
    common, ia, ib = np.intersect1d(a[:, 1].astype(int), b[:, 1].astype(int),
                                    return_indices=True)
    N = a[ia, 2]
    rH = a[ia, 3] / b[ib, 3]
    win = (N >= 0.5) & (N <= np.log(64.0))
    # scope P2 (record part): the proper run's maxima during the entry, N <= ln 64, from cycle 1
    # on, and without the initial transient (N > 0.05)
    ent = (b[:, 1] >= 1) & (b[:, 2] <= np.log(64.0))
    ent5 = ent & (b[:, 2] > 0.05)
    p2 = dict(proper_H_max_entry=float(b[ent, 3].max()), proper_M_max_entry=float(b[ent, 6].max()),
              proper_H_max_entry_N_gt_005=float(b[ent5, 3].max()),
              proper_M_max_entry_N_gt_005=float(b[ent5, 6].max()),
              proper_N_at_H_max=float(b[ent, 2][np.argmax(b[ent, 3])]),
              proper_N_at_M_max=float(b[ent, 2][np.argmax(b[ent, 6])]),
              proper_last_cycle=int(b[-1, 1]), proper_N_end=float(b[-1, 2]))
    return dict(**p2, n_common=int(common.size), t_end_flip=float(a[-1, 0]), N_end_flip=float(a[-1, 2]),
                H_ratio_min_entry=float(rH[win].min()) if win.any() else None,
                H_ratio_median_entry=float(np.median(rH[win])) if win.any() else None,
                M_flip_max=float(a[1:, 6].max()), H_flip_max=float(a[1:, 3].max()),
                M_proper_max_common=float(b[ib, 6].max())), (a, b)


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    fs.use_style()
    res = {}
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.14, top=0.8, wspace=0.0)
    for j, (flip, proper, title) in enumerate([("RNC256", "RSF256", "Quadratic, 256^3"),
                                               ("U256nc", "U256ap", "Inflection, 256^3")]):
        try:
            r, (a, b) = compare(flip, proper)
        except (OSError, ValueError) as e:
            res[flip] = f"unavailable: {e}"
            continue
        res[flip] = r
        tmax = a[-1, 0]
        sel = b[:, 0] <= tmax + 1e-9
        ax[j].semilogy(b[sel, 2], b[sel, 3], color=fs.PAL["blue"], label=r"$\langle|\mathcal{H}|/[\mathcal{H}]\rangle$, proper")
        ax[j].semilogy(a[1:, 2], a[1:, 3], color=fs.PAL["blue"], ls="--", label="sign of the Pi kick flipped")
        ax[j].semilogy(b[sel, 2], b[sel, 6], color=fs.PAL["red"], label=r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$, proper")
        ax[j].semilogy(a[1:, 2], a[1:, 6], color=fs.PAL["red"], ls="--", label="flipped")
        ax[j].set_title(f"{title}: {flip} against {proper}", fontsize=9)
        ax[j].set_xlabel(r"$\langle\mathcal{N}\rangle$")
    # legend above the panels: inside it would cover the proper run's late rise (SR, N > 3.3)
    ax[0].legend(loc="lower center", bbox_to_anchor=(1.0, 1.1), ncol=4, fontsize=7)
    fs.save(fig, os.path.join(out, "fig_signflip"))
    plt.close(fig)
    with open(os.path.join(out, "fig_signflip.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
