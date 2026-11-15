"""Figure: the restricted Newtonian Hills problem, disruption probability and energy.

Reads coplanar.npz of the newton3 scan P1 (F-hills-20261115-130237-cbfaf6b, used for
D >= 1e-3) and of its deep supplement (F-hills-20261115-132156-efddfc0, D < 1e-3), as the
newton3 analysis does (newton3/scripts/analyze.py, coplanar()), and checks the recomputed
edge, deep-limit probability and maximum energy against that analysis run's
summary_coplanar.json (F-hills-20261115-133222-9cb10db). Parabolic restricted problem,
3000 binary phases per D, prograde and retrograde coplanar orbits. Marks the values printed
in the text of arXiv:0911.1136 (prp.tex:735-738, 846-849). Writes fig_newton.{pdf,png}.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_newton"
BLUE, RED, YEL = cz.PAL["blue"], cz.PAL["red"], cz.PAL["yellow"]
D_TRUST = 1e-3          # newton3/scripts/analyze.py: main scan used for D >= 1e-3
SKR = {"Dmax_pro": 2.1, "Dmax_ret": 0.44, "P_deep": 0.8, "D_best": 0.15,
       "Emax_pro": 27.3, "Emax_ret": 1.8}   # prp.tex:735-738, 846-849


def stats(D, Z, tag):
    ok, dis, E = Z[f"ok_{tag}"], Z[f"disrupted_{tag}"], Z[f"E2_{tag}"]
    P = np.array([dis[i][ok[i]].mean() for i in range(D.size)])
    Em = np.array([np.abs(E[i][dis[i] & ok[i]]).mean() if (dis[i] & ok[i]).any() else np.nan
                   for i in range(D.size)])
    Ex = np.array([np.abs(E[i][dis[i] & ok[i]]).max() if (dis[i] & ok[i]).any() else np.nan
                   for i in range(D.size)])
    return P, Em, Ex


def main():
    out = C.out_dir("figures")
    Z0 = np.load(C.run_file("coplanar", "coplanar.npz"))
    Y = np.load(C.run_file("deep", "coplanar.npz"))
    ref = C.load_json("coplanar_an", "summary_coplanar.json")
    keep = Z0["D"] >= D_TRUST * (1 - 1e-9)
    keys = [k for k in Z0.files if k.rsplit("_", 1)[-1] in ("pro", "ret")]
    D = np.concatenate([Y["D"], Z0["D"][keep]])
    Z = {k: np.concatenate([Y[k], np.asarray(Z0[k])[keep]]) for k in keys}
    o = np.argsort(D)
    D = D[o]
    Z = {k: v[o] for k, v in Z.items()}
    nums = {"runs": [C.RUNS["coplanar"], C.RUNS["deep"]], "check_run": C.RUNS["coplanar_an"],
            "phases_per_D": int(Z0["phase_skr"].size), "skr_text": SKR}
    res = {}
    for tag in ("pro", "ret"):
        P, Em, Ex = stats(D, Z, tag)
        imax = np.where(P > 0)[0].max()
        r = {"Dmax_last_disrupting": float(D[imax]), "P_at_Dmin": float(P[0]),
             "D_min": float(D[0]), "P_max": float(P.max()), "D_at_P_max": float(D[np.argmax(P)]),
             "Emax": float(np.nanmax(Ex)), "D_at_Emax": float(D[np.nanargmax(Ex)]),
             "Emean_deep": float(Em[0])}
        for k, v in r.items():
            C.close(v, ref[tag][k], 1e-12, f"{tag} {k}")
        sel = (D > 0.06) & (D < 0.3)
        r["P_range_0.06_0.3"] = [float(P[sel].min()), float(P[sel].max())]
        r["n_fail"], r["n_total"] = ref[tag]["n_fail"], ref[tag]["n_total"]
        res[tag] = (P, Em)
        nums[tag] = r
    cz.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(3.4, 4.1), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.96, bottom=0.11, top=0.98, hspace=0.07)
    Dp = np.where(D > 0, D, np.nan)
    for tag, col, lab in (("pro", RED, "prograde"), ("ret", BLUE, "retrograde")):
        P, Em = res[tag]
        axs[0].plot(Dp, P, color=col, lw=1.3, label=lab)
        axs[1].plot(Dp, Em, color=col, lw=1.3)
    a = axs[0]
    a.plot([SKR["Dmax_pro"]] * 2, [0.0, 0.18], color=RED, lw=1.0, ls="--")
    a.plot([SKR["Dmax_ret"]] * 2, [0.0, 0.18], color=BLUE, lw=1.0, ls="--")
    a.plot([1e-5, 3e-4], [SKR["P_deep"]] * 2, color="k", lw=1.0, ls="--")
    a.plot([SKR["D_best"]], [1.0], "v", color="k", ms=4)
    a.set_ylabel(r"disruption probability")
    a.set_ylim(0, 1.05)
    a.legend(frameon=False, loc="center left", fontsize=8)
    b = axs[1]
    b.set_ylabel(r"mean $|E|$ [unit]")
    b.set_xscale("log")
    b.set_xlim(8e-6, 3)
    b.set_xlabel(r"penetration $D=r_p/r_t$")
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
