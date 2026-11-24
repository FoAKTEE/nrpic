#!/usr/bin/env python3
"""Q-a, Q-b, Q-c of g2prod/JOURNAL.md entry 3 (third amplitude s = +-1/4), judged on the g2q analysis
of analyse_g2.py (U256/U256m = s +-1/2, U256h/U256hm = s +-1/4), with the floor and halving code of
judge_g2.py unchanged; the s = 1 over s = 1/2 values of the earlier judge are drawn beside them.

    python3 judge_q.py --q Q_DIR --prev JUDGE_DIR --runs U256qp=<dir> U256qm=<dir> --out OUT

Q_DIR: the g2q analysis (summary.json, coeffs_N256.npz); JUDGE_DIR: judge run E-20261123-024359-5dc3213
(judge_g2.json). Writes OUT/judge_q.json and OUT/fig/fig_g2_quarter.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "usr", "scripts"))
import card_lib as cl  # noqa: E402
import figstyle as fs  # noqa: E402
from judge_g2 import floor_halving, USR  # noqa: E402

CN_MISS = 6.52     # the dump of the U-A4'(a) miss of M (entry 2.3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True)
    ap.add_argument("--prev", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    S = json.load(open(os.path.join(a.q, "summary.json")))
    P = json.load(open(os.path.join(a.prev, "judge_g2.json")))
    c1, ch = S["U256_U256m"]["constraints"], S["U256h_U256hm"]["constraints"]
    cN = np.array(c1["cN"])
    V = dict(cN=cN.tolist())
    hal = {}
    for lab in ("H", "M"):
        r = floor_halving(c1, ch, lab)
        sel = r["sel_a"]
        corr = r["corr"]
        hal[lab] = dict(corr=corr.tolist(), sel_a=sel.tolist(), raw_even=(r["e1"] / r["eh"]).tolist(),
                        f_over_oh=r["f_over_oh"].tolist(), n_judged=int(sel.sum()),
                        judged_min=float(corr[sel].min()) if sel.any() else None,
                        judged_max=float(corr[sel].max()) if sel.any() else None,
                        outside_cN=[float(x) for x in cN[sel][np.abs(corr[sel] - 4.0) > 0.05]])
    i = int(np.argmin(np.abs(cN - CN_MISS)))
    qa_m = hal["M"]["corr"][i]
    prev_m = P["UA4a_b"]["M"]["corr"]
    prev_cN = np.array(P["UA4a_b"]["cN"])
    j = int(np.argmin(np.abs(prev_cN - CN_MISS)))
    V["Q_a"] = dict(cN=float(cN[i]), M_corr_quarter=qa_m, M_corr_prev=prev_m[j], M_judged_here=bool(hal["M"]["sel_a"][i]),
                    pred="3.98 +- 0.015", refuted_if="below 3.9625 (deviation from 4 more than half of 0.075)",
                    holds_M=bool(abs(qa_m - 4.0) <= 0.0375),
                    H_all_within=bool(hal["H"]["n_judged"] > 0 and not hal["H"]["outside_cN"]),
                    H_n_judged=hal["H"]["n_judged"], H_min=hal["H"]["judged_min"], H_max=hal["H"]["judged_max"])
    V["Q_a"]["holds"] = bool(V["Q_a"]["holds_M"] and V["Q_a"]["H_all_within"])
    # Q-b: common mode of the odd-part error at N_f, k <= 16 dk, for both pairs
    z = np.load(os.path.join(a.q, "coeffs_N256.npz"))
    lo = (z["n"]**2).sum(axis=1) <= 256
    cm = {}
    for tag, (p, m, s) in (("half", ("c_U256", "c_U256m", 0.5)), ("quarter", ("c_U256h", "c_U256hm", 0.25))):
        q = 0.5 * (z[p] - z[m]) / (s * z["cref"]) - 1.0
        cm[tag] = dict(end=float(q[-1].real[lo].mean()), t=q.real[:, lo].mean(axis=1).tolist())
    V["Q_b"] = dict(common_mode_end_half=cm["half"]["end"], common_mode_end_quarter=cm["quarter"]["end"],
                    ratio_half_over_quarter=cm["half"]["end"] / cm["quarter"]["end"],
                    pred="-2.5e-6 +- 0.4e-6", holds=bool(-3.3e-6 <= cm["quarter"]["end"] <= -1.7e-6),
                    check_half_vs_entry_2_3="-9.87e-6 expected")
    # Q-c
    pr = {}
    for n in ("U256h", "U256hm"):
        s = S[n]
        dN = max(abs(x["dN"]) for x in s["U_A0_landmarks"])
        a1 = max(s["U_A1_phi_rel_max"], s["U_A1_Pi_rel_max"], s["U_A1_K_rel_max"])
        a3 = s["U_A3_power_ratio_k_le_3"]
        pr[n] = dict(U_A0=dN, U_A0_pass=bool(dN < 1e-5), U_A1=a1, U_A1_pass=bool(a1 < 1e-3), U_A3=a3,
                     U_A3_pass=bool(abs(a3["min"] - 1) <= 0.1 and abs(a3["max"] - 1) <= 0.1))
    runs = dict(x.split("=", 1) for x in a.runs)
    rec = {}
    for lab, d in runs.items():
        con = cl.read_con(os.path.join(d, "usr.sf.con.hst"))
        rec[lab] = dict(Hp_max=float(con[1:, cl.C["Hp_ratio"]].max()), M_max=float(con[1:, cl.C["M_ratio"]].max()))
        rec[lab]["pass"] = bool(rec[lab]["Hp_max"] < 1e-9 and rec[lab]["M_max"] < 1e-1)
    eo = S["U256h_U256hm"]["U_A2s"]["even_over_odd_rms_end_kmask"]
    V["Q_c"] = dict(per_run=pr, records=rec, even_over_odd_kmask_quarter=eo,
                    even_over_odd_kmask_half=S["U256_U256m"]["U_A2s"]["even_over_odd_rms_end_kmask"],
                    UA2p_quarter=S["U256h_U256hm"]["U_A2s"]["max_end"],
                    pred_even_over_odd="6.33e-5 +- 5 percent", eo_holds=bool(abs(eo / 6.33e-5 - 1) <= 0.05))
    V["Q_c"]["holds"] = bool(all(x["U_A0_pass"] and x["U_A1_pass"] and x["U_A3_pass"] for x in pr.values())
                             and all(x["pass"] for x in rec.values()) and V["Q_c"]["eo_holds"])
    V["UA4a_quarter"] = hal
    json.dump(V, open(os.path.join(a.out, "judge_q.json"), "w"), indent=1)
    # figure
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.series_colors(4)
    fig, ax = plt.subplots(1, 3, figsize=(fs.COLUMN_WIDTH * 2.6, 2.6))
    fig.subplots_adjust(left=0.06, right=0.99, top=0.88, bottom=0.18, wspace=0.3)
    for k, lab in enumerate(("H", "M")):
        x = ax[k]
        x.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
        x.axhspan(3.95, 4.05, color="0.85", lw=0)
        pc, ps = np.array(P["UA4a_b"][lab]["corr"]), np.array(P["UA4a_b"][lab]["sel_a"])
        x.plot(prev_cN[ps], pc[ps], "s", mfc="none", ms=4, color=cols[1], label="s = 1 over 1/2 (judged)")
        c, s = np.array(hal[lab]["corr"]), np.array(hal[lab]["sel_a"])
        x.plot(cN[1:], c[1:], "o", ms=2, color="0.6", label="s = 1/2 over 1/4 (all)")
        x.plot(cN[s], c[s], "o", ms=4, color=cols[0], label="s = 1/2 over 1/4 (judged)")
        x.axvline(CN_MISS, **fs.GUIDE)
        x.set_ylim(3.7, 4.3)
        x.set_xlabel(r"$N-N_*$")
        x.set_ylabel(f"even halving of {lab}, floor removed")
        x.legend(loc="lower left", fontsize=5.5)
    y = ax[2]
    y.plot(z["cN"], cm["half"]["t"], "-", color=cols[0], label="s = 1/2")
    y.plot(z["cN"], np.array(cm["quarter"]["t"]) * 4.0, "--", color=cols[2], label=r"s = 1/4, times 4")
    y.axhline(-9.87e-6, **fs.GUIDE)
    y.set_xlabel(r"$N-N_*$")
    y.set_ylabel(r"mean Re$(O/(s\,c_{\rm ref})-1)$, $k\leq16\,dk$")
    y.legend(loc="lower left", fontsize=6)
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_quarter"))
    print(json.dumps({k: V[k] for k in ("Q_a", "Q_b")}, indent=1))
    print(json.dumps({k: v for k, v in V["Q_c"].items() if k != "per_run"}, indent=1))
    print(json.dumps(V["Q_c"]["per_run"], indent=1))


if __name__ == "__main__":
    main()
