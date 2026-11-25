"""U-A0, U-A1, U-A4'(c) from the constraint records of every release run.

python3 records.py --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = vlib.read_deck(vlib.DECK)
    tlim = float(d["time/tlim"])
    ref = vlib.Reference(vlib.DECK, vlib.MODEFILE, tlim, rtol=1e-12, nshell=1)
    # landmarks from the fine background (same definitions as reference.py)
    tt = np.linspace(0.0, tlim, 200001)
    b = ref.background(tt)
    from scipy.optimize import brentq
    e2 = b["eps2"] - 3.0
    up = np.nonzero((e2[:-1] < 0) & (e2[1:] >= 0))[0][0]
    dn = np.nonzero((e2[:-1] > 0) & (e2[1:] <= 0))[0][0]
    f = lambda t: float(ref.background(t)["eps2"] - 3.0)
    lm = {"USR onset": brentq(f, tt[up], tt[up + 1], xtol=1e-14),
          "eps2 maximum": float(tt[np.argmax(b["eps2"])]),
          "USR end": brentq(f, tt[dn], tt[dn + 1], xtol=1e-14),
          "eps1 minimum": float(tt[np.argmin(b["eps1"])]), "N_f": tlim}
    res = {"landmark_t": lm, "runs": {}}
    curves = {}
    for lab, (rid, s, seed, N) in vlib.RUNS.items():
        rec, ndup = vlib.read_con(os.path.join(vlib.run_dir(lab), "usr.sf.con.hst"))
        t = rec[:, 0]
        bb = ref.background(t)
        r = {"rows": int(len(rec)), "duplicate_rows_dropped": ndup, "t_last": float(t[-1]),
             "monotonic": bool(np.all(np.diff(t) > 0))}
        sp = CubicSpline(t, rec[:, 2])
        dN = {}
        for k, tl in lm.items():
            if tl <= t[-1] + 1e-12:
                dN[k] = float(sp(min(tl, t[-1])) - ref.background(tl)["N"])
        r["U-A0_dN"] = dN
        r["U-A0_max_abs_dN"] = float(max(abs(v) for v in dN.values()))
        r["U-A0_max_abs_dN_all_rows"] = float(np.abs(rec[:, 2] - bb["N"]).max())
        rel = {"phi": np.abs(rec[:, 16] / bb["phi"] - 1), "Pi": np.abs(rec[:, 17] / bb["Pi"] - 1),
               "K": np.abs(rec[:, 18] / bb["K"] - 1)}
        r["U-A1_max_rel"] = {k: float(v.max()) for k, v in rel.items()}
        r["U-A1_cN_at_max"] = {k: float(bb["N"][np.argmax(v)]) for k, v in rel.items()}
        r["U-A1_max"] = float(max(v.max() for v in rel.values()))
        r["alpha_max_dev"] = float(np.abs(rec[:, 19] - 1).max())
        r["U-A4c_Hp_ratio_max"] = float(rec[:, 24].max())
        r["U-A4c_Hp_ratio_cN_at_max"] = float(bb["N"][np.argmax(rec[:, 24])])
        r["U-A4c_M_ratio_max"] = float(rec[:, 6].max())
        r["U-A4c_M_ratio_cN_at_max"] = float(bb["N"][np.argmax(rec[:, 6])])
        r["H_ratio_max_unsigned"] = float(rec[:, 3].max())
        r["M_ratio_at_end"] = float(rec[-1, 6])
        res["runs"][lab] = r
        curves[lab] = (bb["N"], rel["Pi"], rec[:, 24], rec[:, 6])
    res["thresholds"] = {"U-A0": 1e-5, "U-A1": 1e-3, "U-A4c_H": 1e-9, "U-A4c_M": 1e-1}
    proper = [l for l in vlib.RUNS if l != "U256nc"]
    res["verdict"] = {
        "U-A0": all(res["runs"][l]["U-A0_max_abs_dN"] < 1e-5 for l in vlib.RUNS),
        "U-A1": all(res["runs"][l]["U-A1_max"] < 1e-3 for l in vlib.RUNS),
        "U-A4c_H_proper": all(res["runs"][l]["U-A4c_Hp_ratio_max"] < 1e-9 for l in proper),
        "U-A4c_M_proper": all(res["runs"][l]["U-A4c_M_ratio_max"] < 1e-1 for l in proper),
        "U-A4c_M_runs_over_bar": [l for l in proper if res["runs"][l]["U-A4c_M_ratio_max"] >= 1e-1],
    }
    json.dump(res, open(os.path.join(a.out, "records.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    cols = figstyle.series_colors(len(curves))
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6))
    for c, (lab, (cN, rPi, hp, m)) in zip(cols, curves.items()):
        ax[0].semilogy(cN, rPi + 1e-18, color=c, lw=0.8, label=lab)
        ax[1].semilogy(cN, hp, color=c, lw=0.8)
        ax[2].semilogy(cN, m, color=c, lw=0.8)
    ax[0].axhline(1e-3, color="k", ls="--", lw=0.8)
    ax[1].axhline(1e-9, color="k", ls="--", lw=0.8)
    ax[2].axhline(1e-1, color="k", ls="--", lw=0.8)
    ax[0].set_ylabel("|<Pi>/Pi_ref - 1|")
    ax[1].set_ylabel("<|H'|/[H]> (record col 25)")
    ax[2].set_ylabel("<|M|/[M]> (record col 7)")
    for x in ax:
        x.set_xlabel("cN")
    ax[0].legend(fontsize=5, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_records.png"), dpi=150)


if __name__ == "__main__":
    main()
