#!/usr/bin/env python3
"""L5 resolution and step test (../JOURNAL.md entry 20): where the first-order parts of H and M
of the single-kick test come from.

    l5_scaling.py --set A=DIR --set B=DIR --set C=DIR --out DIR

Each DIR holds the stencil-projector runs K1p, K1m, K2p, K2m, K0 of one configuration
(A: 32^3, Courant 0.25; B: 32^3, Courant 0.125; C: 64^3, Courant 0.25, so B and C share the
step dt). Per dump, as in l5_analysis.py (cell by cell, rms relative to the box means <[H]>,
<[M]> of the K1p record at that cycle):
    H_even1  rms of [H(100) + H(-100)]/2 - H(0), box mean removed  (second order)
    H_first  rms of [8 H_o(50) - H_o(100)]/3                        (first order)
    M_first  rms|[8 M_o(50) - M_o(100)]/3|                          (first order)
Ratios at equal recorded times: A/B (step halved at fixed mesh: 16 for a fourth-order time
error) and B/C (mesh halved at fixed step: 64 for a sixth-order spatial error, 1 if spatial
error is absent). Writes l5_scaling.json and fig_l5_scaling.png/pdf.
"""
import argparse
import json
import os

import numpy as np

import ladder_lib as LL

RUNS = ("K1p", "K1m", "K2p", "K2m", "K0")
VARS = ["H", "Mx", "My", "Mz"]


def rms(x):
    return float(np.sqrt(np.mean(x * x)))


def config_rows(d):
    dumps = {r: LL.dump_list(os.path.join(d, r)) for r in RUNS}
    con = LL.read_con(os.path.join(d, "K1p"))
    nd = min(len(v) for v in dumps.values())
    rows = []
    for i in range(nd):
        F, T = {}, {}
        for r in RUNS:
            h, f = LL.read_dump(dumps[r][i], VARS)
            F[r] = dict(H=f["H"], M=np.stack([f["Mx"], f["My"], f["Mz"]]))
            T[r] = h["time"]
        if max(T.values()) - min(T.values()) > 1e-12:
            raise SystemExit(f"{d} dump {i}: times differ {T}")
        cyc = int(h["cycle"])
        rec = con[np.nonzero(con[:, 1] == cyc)[0][0]]
        hmag, mmag = rec[9], rec[10]
        he = 0.5 * (F["K1p"]["H"] + F["K1m"]["H"]) - F["K0"]["H"]
        ho1 = 0.5 * (F["K1p"]["H"] - F["K1m"]["H"])
        ho2 = 0.5 * (F["K2p"]["H"] - F["K2m"]["H"])
        mo1 = 0.5 * (F["K1p"]["M"] - F["K1m"]["M"])
        mo2 = 0.5 * (F["K2p"]["M"] - F["K2m"]["M"])
        m1 = (8.0 * mo2 - mo1) / 3.0
        rows.append(dict(cycle=cyc, time=float(T["K1p"]), Hmag=float(hmag), Mmag=float(mmag),
                         H_even1=rms(he - he.mean()) / hmag,
                         H_first=rms((8.0 * ho2 - ho1) / 3.0) / hmag,
                         M_first=float(np.sqrt(np.mean((m1 * m1).sum(axis=0)))) / mmag
                         if mmag > 0 else 0.0))
        del F
    return rows


def ratios(ra, rb, keys=("H_even1", "H_first", "M_first")):
    tb = np.array([r["time"] for r in rb])
    out = []
    for r in ra:
        if r["cycle"] == 0:
            continue
        j = int(np.argmin(np.abs(tb - r["time"])))
        if abs(tb[j] - r["time"]) > 1e-9:
            continue
        out.append(dict(time=r["time"], **{k: r[k] / rb[j][k] if rb[j][k] > 0 else None
                                           for k in keys}))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", required=True, help="NAME=DIR")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    sets = dict(s.split("=", 1) for s in a.set)
    res = dict(sets=sets, rows={k: config_rows(v) for k, v in sets.items()})
    if "A" in sets and "B" in sets:
        res["A_over_B"] = ratios(res["rows"]["A"], res["rows"]["B"])
    if "B" in sets and "C" in sets:
        res["B_over_C"] = ratios(res["rows"]["B"], res["rows"]["C"])
    with open(os.path.join(a.out, "l5_scaling.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    for key in ("A_over_B", "B_over_C"):
        for r in res.get(key, []):
            print(key, f"t={r['time']:.4f} " + " ".join(
                f"{k}={r[k]:.4g}" for k in ("H_even1", "H_first", "M_first") if r[k] is not None))
    for k in ("A_over_B", "B_over_C"):
        if k in res:
            for q in ("H_even1", "H_first", "M_first"):
                v = [r[q] for r in res[k] if r[q] is not None]
                if v:
                    print(f"{k} {q}: min {min(v):.4g} max {max(v):.4g} median {np.median(v):.4g}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    col = dict(A=fs.PAL["yellow"], B=fs.PAL["green"], C=fs.PAL["blue"])
    lab = dict(A=r"$32^3$, $\theta=0.25$", B=r"$32^3$, $\theta=0.125$", C=r"$64^3$, $\theta=0.25$")
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.16, top=0.92, wspace=0.27)
    for k, rows in res["rows"].items():
        rr = [r for r in rows if r["cycle"] >= 1]
        t = [r["time"] for r in rr]
        ax[0].semilogy(t, [r["M_first"] for r in rr], "o-", ms=2.5, color=col.get(k, "k"),
                       label=r"$\mathcal{M}$ first order, " + lab.get(k, k))
        ax[0].semilogy(t, [r["H_first"] for r in rr], "s--", ms=2.5, color=col.get(k, "k"),
                       label=r"$\mathcal{H}$ first order, " + lab.get(k, k))
        ax[0].semilogy(t, [r["H_even1"] for r in rr], ":", color=col.get(k, "k"),
                       label=r"$\mathcal{H}$ second order, " + lab.get(k, k))
    ax[0].set_xlabel(r"$t$")
    ax[0].set_ylabel(r"rms part / $\langle[\mathcal{C}]\rangle$ ($s=100$)")
    ax[0].legend(fontsize=5, ncol=1, loc="center right")
    for key, mk, ttl in (("A_over_B", "o", "step halved (A/B)"), ("B_over_C", "s", "mesh halved (B/C)")):
        rr = res.get(key, [])
        t = [r["time"] for r in rr]
        for q, c in (("M_first", fs.PAL["red"]), ("H_first", fs.PAL["blue"]),
                     ("H_even1", "0.4")):
            ax[1].semilogy(t, [r[q] if r[q] else np.nan for r in rr], mk + ("-" if key == "A_over_B" else "--"),
                           ms=3, color=c, label=f"{q}, {ttl}")
    for y in (1, 16, 64):
        ax[1].axhline(y, **fs.GUIDE)
    ax[1].set_xlabel(r"$t$")
    ax[1].set_ylabel("ratio at equal times")
    ax[1].legend(fontsize=5, loc="center right")
    fs.save(fig, os.path.join(a.out, "fig_l5_scaling"))
    plt.close(fig)


if __name__ == "__main__":
    main()
