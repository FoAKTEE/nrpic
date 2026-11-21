#!/usr/bin/env python3
"""Figure and checks of the KHSR comparison (khsr_ecc.py output): ejection probability,
ejection preference (primary / secondary) and mean ejection energy against D for the
parabolic orbit and r_a/r_t = 500, 200, 130, 100, prograde and retrograde; lines: KHSR's
parabolic approximation from the restricted problem; filled markers: direct three-body
integration of the elliptic orbit; open markers: parabolic approximation from the direct
parabolic runs at the same phases. Also writes khsr_checks.json with the K1-K3 judgements'
numbers.

Usage: fig_khsr.py <dir with khsr_ecc.json> [--out=<dir>]   (default out: the same dir)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

RA_ORDER = ["inf", "500.0", "200.0", "130.0", "100.0"]
LABEL = {"inf": "parabolic", "500.0": r"$r_a/r_t=500$", "200.0": "200", "130.0": "130",
         "100.0": "100"}


def main():
    src = sys.argv[1]
    out = src
    for a in sys.argv[2:]:
        if a.startswith("--out="):
            out = a.split("=", 1)[1]
    os.makedirs(out, exist_ok=True)
    S = json.load(open(os.path.join(src, "khsr_ecc.json")))
    cols = dict(zip(RA_ORDER, fs.SERIES))
    # ---------------------------------------------------------------- checks
    chk = {"K1": S["K1"], "K2": S["K2"], "points": []}
    k1 = S["K1"]["E_bar_coefficient_at_ra100"]
    chk["K1"]["rounds_to_printed"] = bool(round(k1, 1) == S["K1"]["KHSR_printed"])
    chk["K2"]["within_0.05"] = bool(abs(S["K2"]["r0_e0.9"] - 12.2) <= 0.05 and abs(S["K2"]["r0_e1.1"] - 17.4) <= 0.05)
    worst = dict(dPej_vs_lines=0.0, dPej_vs_pardirect=0.0, dEej_rel=0.0, dratio_rel=0.0, dmeanabs_rel=0.0,
                 E_orb0_rel=0.0)
    for s in ("pro", "ret"):
        lines = S["lines"][s]
        for r in S["direct"][s]:
            ra = r["r_a"]
            L = [x for x in lines[ra] if abs(x["D"] - r["D"]) < 1e-9][0]
            pa = r["parabolic_from_direct"]
            row = dict(sense=s, D=r["D"], r_a=ra, Pdis=r["Pdis"], Pej=r["Pej"], Pej_lines=L["Pej"],
                       Pej_pardirect=pa["Pej"], P1=r["P1"], P2=r["P2"], n1=r["n1"], n2=r["n2"],
                       ratio=r["P1"] / r["P2"] if r["P2"] > 0 else None,
                       ratio_lines=L["P1"] / L["P2"] if L["P2"] > 0 else None,
                       ratio_pardirect=pa["P1"] / pa["P2"] if pa["P2"] > 0 else None,
                       Eej=r["Eej"], Eej_lines=L["Eej"], Eej_pardirect=pa["Eej"],
                       mean_abs_dE=r["mean_abs_dE"], mean_abs_dE_par=pa["mean_abs_dE"],
                       Pboth_bound=r["Pboth_bound"], Psurv=r["Psurv"], n_fail=r["n_fail"],
                       E_orb0=r["E_orb0"], E_bar=r["E_bar"])
            row["dPej_vs_lines"] = row["Pej"] - row["Pej_lines"]
            row["dPej_vs_pardirect"] = row["Pej"] - row["Pej_pardirect"]
            if r["E_bar"] != 0:
                row["E_orb0_rel"] = r["E_orb0"] / r["E_bar"] - 1
                worst["E_orb0_rel"] = max(worst["E_orb0_rel"], abs(row["E_orb0_rel"]))
            judged = r["Pdis"] > 0.1
            row["judged_K3c"] = judged
            if judged:
                worst["dPej_vs_lines"] = max(worst["dPej_vs_lines"], abs(row["dPej_vs_lines"]))
                worst["dPej_vs_pardirect"] = max(worst["dPej_vs_pardirect"], abs(row["dPej_vs_pardirect"]))
                if np.isfinite(row["Eej"]) and np.isfinite(row["Eej_pardirect"]):
                    worst["dEej_rel"] = max(worst["dEej_rel"], abs(row["Eej"] / row["Eej_pardirect"] - 1))
                if row["n1"] > 20 and row["n2"] > 20 and row["ratio_pardirect"]:
                    worst["dratio_rel"] = max(worst["dratio_rel"], abs(row["ratio"] / row["ratio_pardirect"] - 1))
                if ra != "inf":
                    worst["dmeanabs_rel"] = max(worst["dmeanabs_rel"], abs(row["mean_abs_dE"] / row["mean_abs_dE_par"] - 1))
            chk["points"].append(row)
    chk["worst_K3c_K3d"] = worst
    with open(os.path.join(out, "khsr_checks.json"), "w") as fh:
        json.dump(chk, fh, indent=1)
    # ---------------------------------------------------------------- figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 8.0), sharex="col")
    plt.subplots_adjust(left=0.09, right=0.98, bottom=0.07, top=0.96, wspace=0.22, hspace=0.08)
    for j, s in enumerate(("pro", "ret")):
        lines = S["lines"][s]
        pts = S["direct"][s]
        for ra in RA_ORDER:
            c = cols[ra]
            L = lines[ra]
            D = np.array([x["D"] for x in L])
            P = np.array([x["Pej"] for x in L])
            P1 = np.array([x["P1"] for x in L])
            P2 = np.array([x["P2"] for x in L])
            E = np.array([x["Eej"] for x in L])
            with np.errstate(divide="ignore", invalid="ignore"):
                R = np.where(P2 > 0, P1 / P2, np.nan)
            axs[0, j].plot(D, P, color=c, label=LABEL[ra])
            axs[1, j].plot(D, R, color=c)
            axs[2, j].plot(D, E, color=c)
            pp = [r for r in pts if r["r_a"] == ra]
            Dd = np.array([r["D"] for r in pp])
            axs[0, j].plot(Dd, [r["Pej"] for r in pp], "o", color=c, ms=4)
            axs[0, j].plot(Dd, [r["parabolic_from_direct"]["Pej"] for r in pp], "s", color=c, ms=6, mfc="none", mew=0.8)
            rr = [r["P1"] / r["P2"] if r["P2"] > 0 else np.nan for r in pp]
            axs[1, j].plot(Dd, rr, "o", color=c, ms=4)
            axs[2, j].plot(Dd, [r["Eej"] for r in pp], "o", color=c, ms=4)
        axs[0, j].set_ylim(0, 1.05)
        axs[1, j].set_yscale("log")
        axs[1, j].set_ylim(1e-3, 3)
        axs[1, j].axhline(1, **fs.GUIDE)
        axs[2, j].set_ylim(0, 3.2 if s == "pro" else 1.6)
        axs[2, j].set_xlabel("penetration factor $D$", labelpad=-2)
        axs[0, j].set_title("prograde" if s == "pro" else "retrograde")
        if s == "ret":
            axs[2, j].set_xlim(0, 0.45)
        else:
            axs[2, j].set_xlim(0, 2.2)
    axs[0, 0].set_ylabel("ejection probability")
    axs[1, 0].set_ylabel("preference primary/secondary")
    axs[2, 0].set_ylabel(r"mean ejection energy")
    axs[0, 0].legend(loc="upper right", ncol=2, fontsize=8)
    axs[0, 1].plot([], [], "o", color="grey", ms=4, label="three-body, elliptic orbit")
    axs[0, 1].plot([], [], "s", color="grey", ms=6, mfc="none", label="parabolic approx., same phases")
    axs[0, 1].plot([], [], "-", color="grey", label="parabolic approx., restricted")
    axs[0, 1].legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_khsr_ecc"))
    print(json.dumps(dict(K1=chk["K1"], K2=chk["K2"], worst=worst), indent=1))


if __name__ == "__main__":
    main()
