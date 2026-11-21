"""Figure: the first passage P1 to its end, t = 280 M.

Reads P1's raw tracker, horizon, history and r psi4 files (common.RUNS["p1"]) with the
readers of the code's output (common.nrread()) and checks the closest approach, the remnant's
horizon mass and the radiated energies against p1_280.json of the analysis run ["p1end"]
(checked against its sha256). Left: coordinate distance of each member (after the merger at
t = 48.8 M, of the remnant) from the heavy black hole, and the member separation; middle:
horizon masses of the members and of the remnant, and the remnant's dimensionless spin;
right: energy radiated through the four extraction spheres. Writes fig_p1_end.{pdf,png} and
fig_p1_end_numbers.json.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_p1_end"
T_MERGE = 48.8125
HRMS_GOOD = 1e-3


def main():
    out = C.out_dir("figures")
    ref = C.load_json("p1end", "p1_280.json")
    nr = C.nrread()
    rd = os.path.join(C.SCRATCH, C.RUNS["p1"])
    t, X, _ = nr.common_times(nr.read_trackers(rd), keys=[0, 1, 2])
    d1 = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
    d2 = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)
    r12 = np.linalg.norm(X[:, 1] - X[:, 0], axis=1)
    late = t > 100
    k = np.argmin(np.where(late, d1, np.inf))
    nums = {"runs": [C.RUNS["p1"], C.RUNS["p1end"]], "t_closest": float(t[k]), "d_closest": float(d1[k])}
    if abs(t[k] - ref["remnant_orbit"]["t_closest"]) > 1e-9 or abs(d1[k] - ref["remnant_orbit"]["d_closest"]) > 1e-9:
        raise SystemExit("closest approach differs from p1_280.json")
    cz.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(8.0, 5.0), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.98, wspace=0.22, hspace=0.07)
    axs = axs.ravel()
    ax = axs[0]
    ax.plot(t, d1, color=cz.PAL["blue"], label="member 1 / remnant")
    ax.plot(t, d2, color=cz.PAL["red"], ls="--", label="member 2")
    ax.plot(t, r12, color="k", lw=1.0, label="member separation")
    ax.axvline(T_MERGE, **cz.MASK_LINE)
    ax.plot([t[k]], [d1[k]], "o", color="k", ms=4)
    ax.set_ylabel("distance from $M$ [$M$]")
    ax.set_ylim(0, 40)
    ax.legend(loc="upper right", fontsize=8)
    ax = axs[1]
    hz = nr.read_horizons(rd)
    for n, col in ((0, cz.PAL["blue"]), (1, cz.PAL["red"])):
        h, _ = hz[n]
        g = h["hrms"] < HRMS_GOOD
        ax.plot(h["t"][g], h["mass"][g], ".", ms=1.5, color=col)
    h0, _ = hz[0]
    g = (h0["hrms"] < HRMS_GOOD) & (h0["t"] > T_MERGE)
    chi = h0["S"][g] / h0["mass"][g] ** 2
    m_end = float(np.median(h0["mass"][g & (h0["t"] >= 240)]))
    nums["remnant_mass_240_280"] = m_end
    nums["remnant_chi_60_100"] = float(np.median(chi[(h0["t"][g] >= 60) & (h0["t"][g] <= 100)]))
    if abs(m_end - ref["horizons"]["0"]["mass_240_280"]["median"]) > 1e-12:
        raise SystemExit("remnant mass differs from p1_280.json")
    ax.set_ylabel("horizon mass [$M$]")
    ax.set_ylim(0.12, 0.29)
    bx = axs[2]
    bx.plot(h0["t"][g], chi, ".", ms=1.0, color=cz.PAL["green"])
    bx.axvline(T_MERGE, **cz.MASK_LINE)
    bx.set_ylim(0.6, 0.72)
    bx.set_xlabel("$t$ [$M$]", labelpad=-2)
    bx.set_ylabel("remnant spin $|S|/m^2$")
    ax = axs[3]
    nums["E_end"] = {}
    for R, col in zip((40, 48, 70, 90), (cz.PAL["blue"], cz.PAL["red"], cz.PAL["yellow"], cz.PAL["green"])):
        tw, modes = nr.read_rpsi4(rd, R)
        E, _, _ = nr.radiated_energy(tw, modes)
        nums["E_end"][str(R)] = float(E[-1])
        if abs(E[-1] - ref["radiation"][str(R)]["E_end"]) > 1e-12 * max(1.0, E[-1]):
            raise SystemExit(f"radiated energy at R = {R} differs from p1_280.json")
        pos = E > 0
        ax.semilogy(tw[pos], E[pos], color=col, label=f"$R={R}M$")
    ax.axvline(T_MERGE, **cz.MASK_LINE)
    ax.axvline(float(t[k]), color="grey", lw=1.0, ls=":")
    ax.set_ylim(1e-7, 1e-2)
    ax.set_xlabel("$t$ [$M$]", labelpad=-2)
    ax.set_ylabel("radiated energy [$M$]")
    ax.legend(loc="lower right", fontsize=8, ncol=2)
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
