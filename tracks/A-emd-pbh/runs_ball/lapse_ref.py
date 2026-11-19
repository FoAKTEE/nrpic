#!/usr/bin/env python3
"""Reference for the central lapse of the relaxed 1+log condition (core's gauge package,
option lapse_leak) in the homogeneous core of a data set: common.relaxed_lapse_reference
with the exact a(tau) of exact.json (prep.py or prep_bh.py output). Writes
lapse_ref_<rate>.json and fig_lapse_ref.png into --out; prints the numbers that the
predictions of JOURNAL.md quote.

    lapse_ref.py --prep <prep dir> --out <dir> [--rate 8 4]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rate", type=float, nargs="+", default=[8.0])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ex = C.load_json(os.path.join(a.prep, "exact.json"))
    tau_tab = np.array(ex["central"]["tau"])[:-1]
    a_tab = np.array(ex["central"]["a"])[:-1]
    tau_ta = ex["core"]["tau_ta"]
    res = {}
    curves = {}
    for L in a.rate:
        t, tau, al = C.relaxed_lapse_reference(tau_tab, a_tab, L, t_end=80.0)
        d = dict(rate=L, alpha_at={str(x): float(np.interp(x, t, al)) for x in (2, 4, 6, 10, 14, 20, 25, 30, 40, 44)
                                   if x <= t[-1]},
                 tau_at={str(x): float(np.interp(x, t, tau)) for x in (10, 16, 20, 25, 30, 40, 44) if x <= t[-1]},
                 t_at_core_turnaround=float(np.interp(tau_ta, tau, t)),
                 alpha_max=float(al.max()), t_end=float(t[-1]), tau_end=float(tau[-1]),
                 a_end_over_a_max=float(np.interp(tau[-1], tau_tab, a_tab) / a_tab.max()))
        for lev in (0.5, 0.1, 0.01):
            j = np.nonzero(al < lev)[0]
            d[f"t_alpha_lt_{lev:g}"] = float(t[j[0]]) if len(j) else None
            d[f"tau_alpha_lt_{lev:g}"] = float(tau[j[0]]) if len(j) else None
        res[str(L)] = d
        curves[L] = (t, tau, al)
        C.write_json(os.path.join(a.out, f"lapse_ref_{L:g}.json"),
                     dict(rate=L, t=t[::10].tolist(), tau=tau[::10].tolist(), alpha=al[::10].tolist()))
        print(f"rate {L:g}: " + ", ".join(f"{k}={v}" for k, v in d.items()))
    C.write_json(os.path.join(a.out, "lapse_ref_summary.json"), res)
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.3))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.90, wspace=0.30)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    cols = fs.series_colors(len(curves), "viridis")
    for c_, (L, (t, tau, al)) in zip(cols, curves.items()):
        ax1.plot(t, al, color=c_, label=f"rate {L:g} ($T={1 / L:g}\\,M$)")
        ax2.plot(t, tau, color=c_)
    ax2.plot(tau_tab, tau_tab, **fs.GUIDE, label=r"$\tau=t$")
    ax2.axhline(tau_ta, **fs.MASK_LINE)
    ax2.axhline(ex["first_trapped"]["tau"], color="k", lw=1.0, ls=":", label=r"$\tau_{\rm AH}$ first")
    ax1.set_xlabel(r"$t\,/M$")
    ax1.set_ylabel(r"$\alpha_c$ (homogeneous core)")
    ax1.legend(fontsize=8)
    ax1.set_title("relaxed 1+log lapse at the centre", fontsize=10)
    ax2.set_xlabel(r"$t\,/M$")
    ax2.set_ylabel(r"central proper time $\tau_c\,/M$")
    ax2.set_xlim(0, max(c[0][-1] for c in curves.values()))
    ax2.set_ylim(0, 1.05 * max(ex["first_trapped"]["tau"], max(c[1][-1] for c in curves.values())))
    ax2.legend(fontsize=8)
    ax2.set_title("where the centre's proper time stops", fontsize=10)
    fs.save(fig, os.path.join(a.out, "fig_lapse_ref"))


if __name__ == "__main__":
    main()
