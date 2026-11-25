"""U-A4'(a), (b), (d) and the three-amplitude reading of the halving (seed A, 256^3).

Per dump of the six runs s = +-1, +-1/2, +-1/4 (and the control up to t = 3.75): odd and
even parts of H and of M_i (taken together) with box means removed, the floor of SCOPE 4c,
the halving ratios with the floor removed, and the fields D1 = E(1) - 4 E(1/2),
D2 = E(1/2) - 4 E(1/4): for E = s^2 A + s^4 B + F (F not scaling with s), D1 = (3/4) B - 3 F
and D2 = (3/64) B - 3 F, so rms(D2)/rms(D1) is 1/16 where the s^4 term dominates and 1
where F does. At most five 256^3 arrays (134 MB each) are held at a time.

python3 constraints.py --out DIR
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

PAIRS = {1.0: ("U256ap", "U256am"), 0.5: ("U256hp", "U256hm"), 0.25: ("U256qp", "U256qm")}
GROUPS = {"H": ["H"], "M": ["Mx", "My", "Mz"]}


def centred(lab, k, name):
    a = vlib.read_var(vlib.dump_path(lab, k), name)
    return a - a.mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = vlib.read_deck(vlib.DECK)
    tlim = float(d["time/tlim"])
    ref = vlib.Reference(vlib.DECK, vlib.MODEFILE, tlim, rtol=1e-12, nshell=1)
    ks = vlib.dumps_of("U256ap")
    nc_ks = set(vlib.dumps_of("U256nc"))
    rows = []
    for k in ks:
        t0 = time.time()
        labs = [l for p in PAIRS.values() for l in p] + (["U256nc"] if k in nc_ks else [])
        times = {l: vlib.dump_header(vlib.dump_path(l, k))["time"] for l in labs}
        tk = times["U256ap"]
        row = {"dump": k, "t": tk, "cN": float(ref.background(tk)["N"]),
               "max_dt": float(max(abs(v - tk) for v in times.values()))}
        for g, comps in GROUPS.items():
            acc = {f"o2_{s}": 0.0 for s in PAIRS} | {f"e2_{s}": 0.0 for s in PAIRS}
            acc |= {f"single2_{l}": 0.0 for l in labs}
            acc |= {"d1": 0.0, "d2": 0.0, "d12": 0.0, "e12": 0.0, "e24": 0.0,
                    "nc2": 0.0, "nce2": 0.0}
            for c in comps:
                E = {}
                for s, (lp, lm) in PAIRS.items():
                    x = centred(lp, k, c)
                    y = centred(lm, k, c)
                    acc[f"single2_{lp}"] += float(np.mean(x * x))
                    acc[f"single2_{lm}"] += float(np.mean(y * y))
                    o = 0.5 * (x - y)
                    acc[f"o2_{s}"] += float(np.mean(o * o))
                    del o
                    x += y
                    x *= 0.5
                    del y
                    acc[f"e2_{s}"] += float(np.mean(x * x))
                    E[s] = x
                if "U256nc" in labs:
                    z = centred("U256nc", k, c)
                    acc["single2_U256nc"] += float(np.mean(z * z))
                    acc["nc2"] += float(np.mean(z * z))
                    z -= E[1.0]
                    acc["nce2"] += float(np.mean(z * z))
                    del z
                acc["e12"] += float(np.mean(E[1.0] * E[0.5]))
                acc["e24"] += float(np.mean(E[0.5] * E[0.25]))
                D1 = E[1.0] - 4.0 * E[0.5]
                D2 = E[0.5] - 4.0 * E[0.25]
                acc["d1"] += float(np.mean(D1 * D1))
                acc["d2"] += float(np.mean(D2 * D2))
                acc["d12"] += float(np.mean(D1 * D2))
                del D1, D2, E
            o = {s: np.sqrt(acc[f"o2_{s}"]) for s in PAIRS}
            e = {s: np.sqrt(acc[f"e2_{s}"]) for s in PAIRS}
            r = {"o": {str(s): o[s] for s in PAIRS}, "e": {str(s): e[s] for s in PAIRS}}
            for (s1, s2), tag in (((1.0, 0.5), "1_h"), ((0.5, 0.25), "h_q")):
                f2 = vlib.floor2(o[s1], o[s2])
                f = np.sqrt(f2)
                r[f"f_{tag}"] = f
                r[f"f_over_o_{tag}"] = f / o[s2]
                r[f"judged_{tag}"] = bool(e[s2] > 3.0 * f)
                r[f"odd_clause_{tag}"] = bool(o[s2] > 3.0 * f)
                num, den = e[s1] ** 2 - f2, e[s2] ** 2 - f2
                r[f"ratio_{tag}"] = float(np.sqrt(num / den)) if num > 0 and den > 0 else None
                r[f"ratio_raw_{tag}"] = e[s1] / e[s2]
                r[f"odd_ratio_{tag}"] = o[s1] / o[s2]
            r["rms_D1"] = np.sqrt(acc["d1"])
            r["rms_D2"] = np.sqrt(acc["d2"])
            r["D2_over_D1"] = r["rms_D2"] / r["rms_D1"]
            r["corr_D1_D2"] = acc["d12"] / np.sqrt(acc["d1"] * acc["d2"])
            r["corr_E1_Eh"] = acc["e12"] / (e[1.0] * e[0.5])
            r["corr_Eh_Eq"] = acc["e24"] / (e[0.5] * e[0.25])
            r["D1_over_E1"] = r["rms_D1"] / e[1.0]
            r["single_rms"] = {l: np.sqrt(acc[f"single2_{l}"]) for l in labs}
            if "U256nc" in labs:
                r["nc_rms"] = np.sqrt(acc["nc2"])
                r["nc_minus_E1_rms"] = np.sqrt(acc["nce2"])
                r["nc_over_odd1"] = r["nc_rms"] / o[1.0]
            row[g] = r
        row["wall_s"] = time.time() - t0
        rows.append(row)
        print(json.dumps({"dump": k, "cN": row["cN"], "H_ratio": row["H"]["ratio_1_h"],
                          "M_ratio": row["M"]["ratio_1_h"], "M_ratio_hq": row["M"]["ratio_h_q"],
                          "wall": row["wall_s"]}), flush=True)
        json.dump(rows, open(os.path.join(a.out, "constraints.json"), "w"), indent=1,
                  default=float)

    # verdicts as written in SCOPE 4c
    out = {"rows": rows}
    for g in GROUPS:
        jd = [r for r in rows if r[g]["judged_1_h"] and r[g]["ratio_1_h"] is not None]
        dev = [abs(r[g]["ratio_1_h"] - 4.0) for r in jd]
        out[f"U-A4a_{g}"] = {
            "judged_dumps": [r["dump"] for r in jd],
            "unjudged_dumps": [r["dump"] for r in rows if r not in jd],
            "max_dev": max(dev) if dev else None,
            "worst_dump": jd[int(np.argmax(dev))]["dump"] if dev else None,
            "outside": [(r["dump"], r["cN"], r[g]["ratio_1_h"]) for r in jd
                        if abs(r[g]["ratio_1_h"] - 4.0) > 0.05],
            "pass": bool(dev) and max(dev) <= 0.05}
        jq = [r for r in rows if r[g]["judged_h_q"] and r[g]["ratio_h_q"] is not None]
        out[f"quarter_{g}"] = {
            "outside": [(r["dump"], r["cN"], r[g]["ratio_h_q"]) for r in jq
                        if abs(r[g]["ratio_h_q"] - 4.0) > 0.05],
            "max_dev": max(abs(r[g]["ratio_h_q"] - 4.0) for r in jq) if jq else None}
    ent = [r for r in rows if r["cN"] <= np.log(32.0) + 1e-12 and "nc_rms" in r["H"]]
    if ent:
        out["U-A4d"] = {
            "dumps": [r["dump"] for r in ent],
            "ratio_of_maxima": max(r["H"]["nc_rms"] for r in ent) / max(r["H"]["o"]["1.0"] for r in ent),
            "ratio_of_maxima_nc_minus_E1": max(r["H"]["nc_minus_E1_rms"] for r in ent) /
            max(r["H"]["o"]["1.0"] for r in ent),
            "pointwise": [(r["dump"], r["cN"], r["H"]["nc_over_odd1"]) for r in ent]}
    json.dump(out, open(os.path.join(a.out, "constraints.json"), "w"), indent=1, default=float)
    summ = {k: v for k, v in out.items() if k != "rows"}
    print(json.dumps(summ, indent=1, default=float))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    cN = np.array([r["cN"] for r in rows])
    fig, ax = plt.subplots(2, 3, figsize=(12, 6.4))
    cols = figstyle.series_colors(3)
    for j, g in enumerate(GROUPS):
        x = ax[j, 0]
        for c, s in zip(cols, PAIRS):
            x.semilogy(cN, [r[g]["o"][str(s)] for r in rows], "-o", ms=2.5, color=c, label=f"odd s={s}")
            x.semilogy(cN, [r[g]["e"][str(s)] for r in rows], "--s", ms=2.5, color=c, label=f"even s={s}")
        x.semilogy(cN, [max(r[g]["f_1_h"], 1e-300) for r in rows], "k:", lw=1.2, label="floor f (1, 1/2)")
        x.semilogy(cN, [max(r[g]["f_h_q"], 1e-300) for r in rows], "k-.", lw=1.0, label="floor f (1/2, 1/4)")
        x.set_title(f"{g}: rms of parts (box means removed)", fontsize=8)
        x.set_xlabel("cN")
        x.legend(fontsize=5, ncol=2)
        x = ax[j, 1]
        for tag, lab_, mk in (("1_h", "1 -> 1/2", "o"), ("h_q", "1/2 -> 1/4", "s")):
            yy = [r[g][f"ratio_{tag}"] if r[g][f"ratio_{tag}"] is not None else np.nan for r in rows]
            jj = [r[g][f"judged_{tag}"] for r in rows]
            x.plot(cN, yy, "-" + mk, ms=3, lw=0.8, label=f"even halving {lab_} (floor removed)")
            x.plot(cN[~np.array(jj)], np.array(yy)[~np.array(jj)], "x", color="r", ms=6)
        x.axhspan(3.95, 4.05, color="0.85")
        x.set_ylim(3.5, 4.5)
        x.set_title(f"{g}: U-A4'(a) ratio; band 4 +- 0.05; x = not judged", fontsize=8)
        x.set_xlabel("cN")
        x.legend(fontsize=6)
        x = ax[j, 2]
        x.semilogy(cN, [r[g]["D2_over_D1"] for r in rows], "-o", ms=3, label="rms(D2)/rms(D1)")
        x.semilogy(cN, [r[g]["D1_over_E1"] for r in rows], "-s", ms=3, label="rms(D1)/rms(E(1))")
        x.semilogy(cN, [abs(r[g]["corr_D1_D2"]) for r in rows], "-^", ms=3, label="|corr(D1, D2)|")
        x.axhline(1.0 / 16.0, color="k", ls=":", lw=0.8)
        x.set_title(f"{g}: three amplitudes (1/16: s^4 term; 1: floor)", fontsize=8)
        x.set_xlabel("cN")
        x.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_constraints.png"), dpi=150)
    if ent:
        fig, x = plt.subplots(figsize=(4.5, 3.4))
        x.semilogy([r["cN"] for r in ent], [r["H"]["nc_rms"] for r in ent], "-o", label="control rms H'")
        x.semilogy([r["cN"] for r in ent], [r["H"]["nc_minus_E1_rms"] for r in ent], "--", label="control H' - E(1)")
        x.semilogy([r["cN"] for r in ent], [r["H"]["o"]["1.0"] for r in ent], "-s", label="proper odd part (s=1)")
        x.set_xlabel("cN")
        x.set_title("U-A4'(d): sign-flip control, H", fontsize=8)
        x.legend(fontsize=6)
        fig.tight_layout()
        fig.savefig(os.path.join(a.out, "fig_control.png"), dpi=150)


if __name__ == "__main__":
    main()
