#!/usr/bin/env python3
"""Predictions of the two baselines for the passage P1 at q = 4 (package nr_first, E6).

From the start state of the P1 input (positions, momenta and bare masses of its <problem>
block, identical to tracks/F-hills/three_punctures/inputs/hills_q4_m8.athinput):
  newton   full Newtonian three-body problem (the hole moves); member energies against the
           barycentre of M and the other member (V5b) and two-body with M
  hrna     geodesic baseline of 2404.16270 (geodesic_binary/hrna.py; hole fixed at the
           origin, Schwarzschild coordinates), from the coordinate state relative to M, as the
           lead's V6a (tracks/F-hills/stage/G0/checks/lead_checks.py lines 322-340)
  newton_fixed  the same with a Newtonian point mass fixed at the origin (isolates the
           relativistic part of the difference)
Uses the lead's functions (read only): lead_checks.read_athinput, newton_full,
hrna_from_state, kepler_elements. Writes <out>/baselines_p1.json and the figure
fig_baselines_p1.{png,pdf}. Needs numba (python of scratch/F-hills/venv-gb).
Usage: baselines_p1.py <p1 input> [outdir]   (outdir default: $NRPIC_RUN_DIR)
"""
import json
import math
import os
import sys

import numpy as np

WT = "/data/haiyangw/nrpic/wt/F-hills"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/stage/G0/checks"))
import lead_checks as lc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

T_RUN = 280.0          # tlim of the P1 input


def turning_points(t, r):
    i = np.arange(1, len(r) - 1)
    lo = i[(r[i] < r[i - 1]) & (r[i] <= r[i + 1])]
    hi = i[(r[i] > r[i - 1]) & (r[i] >= r[i + 1])]
    return ([(float(t[k]), float(r[k])) for k in lo], [(float(t[k]), float(r[k])) for k in hi])


def first_time(t, cond):
    k = np.argmax(cond)
    return float(t[k]) if cond[k] else None


def at(t, y, t0):
    return float(np.interp(t0, t, y))


def main():
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    m, x, p = lc.read_athinput(inp)                # comp0 = m1, comp1 = m2, comp2 = M
    M, m1, m2 = m[2], m[0], m[1]
    mb = m1 + m2
    v = p / m[:, None]
    xcm = (m1 * x[0] + m2 * x[1]) / mb
    vcm = (m1 * v[0] + m2 * v[1]) / mb
    epsb, e_b, _ = lc.kepler_elements(x[0] - x[1], v[0] - v[1], mb)
    a_b = -mb / (2 * epsb)
    a0 = 5.0                                       # nominal binary separation of the design
    rt = a0 * (M / mb) ** (1 / 3)
    Eu = m1 * m2 / a0 * (M / mb) ** (1 / 3)
    eps_cm, e_cm, rp_cm = lc.kepler_elements(xcm - x[2], vcm - v[2], M + mb)
    res = dict(input=inp, masses=dict(M=M, m1=m1, m2=m2), unit_E=Eu, a_b=a_b, e_b=e_b,
               r_t=rt, cm_orbit=dict(e=e_cm, rp=rp_cm), r0=float(np.linalg.norm(xcm - x[2])),
               t_run=T_RUN)
    curves = {}

    # --- full Newton
    ts, Y = lc.newton_full(m, x, p, t_end=1500.0, nout=30001)
    X = Y[:, :9].reshape(-1, 3, 3)
    V = Y[:, 9:].reshape(-1, 3, 3)
    sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
    import nrread as nr
    E = nr.member_energies(X, V, m, iM=2)
    ie = 0 if E["E_0_bc"][-1] > 0 else 1
    ic = 1 - ie
    late = ts >= 300
    peri_c, apo_c = turning_points(ts, E[f"r_{ic}M"])
    res["newton"] = dict(
        ejected=f"m{ie + 1} (comp{ie})", captured=f"m{ic + 1} (comp{ic})",
        E_ejected_bc_u=float(E[f"E_{ie}_bc"][-1] / Eu),
        E_ejected_bc_range_after_300=float(np.ptp(E[f"E_{ie}_bc"][late]) / Eu),
        E_captured_M_u=float(E[f"E_{ic}_M"][-1] / Eu),
        rmin_1M=float(E["r_0M"].min()), rmin_2M=float(E["r_1M"].min()),
        captured_pericentres=peri_c[:4], captured_apocentres=apo_c[:4],
        t_binary_wider_than_2a=first_time(ts, E["r_12"] > 2 * a_b),
        t_cm_pericentre=float(ts[np.argmin(np.linalg.norm(
            (m1 * X[:, 0] + m2 * X[:, 1]) / mb - X[:, 2], axis=1))]),
        at_t_run=dict(r_1M=at(ts, E["r_0M"], T_RUN), r_2M=at(ts, E["r_1M"], T_RUN),
                      r_12=at(ts, E["r_12"], T_RUN),
                      E_ejected_bc_u=at(ts, E[f"E_{ie}_bc"], T_RUN) / Eu,
                      E_ejected_M_u=at(ts, E[f"E_{ie}_M"], T_RUN) / Eu,
                      E_captured_M_u=at(ts, E[f"E_{ic}_M"], T_RUN) / Eu,
                      hole_displacement=float(np.linalg.norm(
                          np.array([np.interp(T_RUN, ts, X[:, 2, k]) for k in range(3)])
                          - x[2]))))
    curves["newton"] = (ts, E["r_0M"], E["r_1M"], E["r_12"])

    # --- hole fixed: HRNA and Newton, from the coordinate state relative to M (V6a)
    hrna = lc.hrna_mod()
    y0 = np.concatenate([x[0] - x[2], v[0] - v[2], x[1] - x[2], v[1] - v[2]])
    for law in ("hrna", "newton"):
        s, rt_, ry = lc.hrna_from_state(hrna, law, y0, m1, m2, a0, rt)
        r1 = np.linalg.norm(ry[:, 0:3], axis=1)
        r2 = np.linalg.norm(ry[:, 6:9], axis=1)
        r12 = np.linalg.norm(ry[:, 0:3] - ry[:, 6:9], axis=1)
        ieh = 0 if s["E1_u"] > s["E2_u"] else 1
        ich = 1 - ieh
        rb = r2 if ich == 1 else r1
        peri, apo = turning_points(rt_, rb)
        key = "hrna" if law == "hrna" else "newton_fixed"
        res[key] = dict(
            outcome=int(s["outcome"]), status=int(s["status"]), t_end=float(s["t_end"]),
            E1_u=float(s["E1_u"]), E2_u=float(s["E2_u"]),
            ejected=f"m{ieh + 1} (comp{ieh})", captured=f"m{ich + 1} (comp{ich})",
            plunged=int(s["plunged"]), rmin_1=float(r1.min()), rmin_2=float(r2.min()),
            captured_pericentres=peri[:4], captured_apocentres=apo[:4],
            t_binary_wider_than_2a=first_time(rt_, r12 > 2 * a_b),
            t_first_within_4M=first_time(rt_, np.minimum(r1, r2) < 4.0),
            at_t_run=dict(r_1M=at(rt_, r1, T_RUN), r_2M=at(rt_, r2, T_RUN),
                          r_12=at(rt_, r12, T_RUN)))
        curves[key] = (rt_, r1, r2, r12)
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(out, "baselines_p1.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3), sharey=True)
    for ax, xmax in zip(axs, (T_RUN + 20, 1000)):
        for key, ls, lab in (("newton", "-", "Newton, full"), ("newton_fixed", ":", "Newton, hole fixed"),
                             ("hrna", "--", "HRNA (geodesic), hole fixed")):
            t_, r1, r2, r12 = curves[key]
            ax.plot(t_, r1, ls=ls, color=fs.PAL["blue"], lw=1.2,
                    label=r"$m_1$ " + lab if ax is axs[0] else None)
            ax.plot(t_, r2, ls=ls, color=fs.PAL["red"], lw=1.2,
                    label=r"$m_2$ " + lab if ax is axs[0] else None)
            if key == "newton":
                ax.plot(t_, r12, ls=ls, color=fs.PAL["yellow"], lw=1.0,
                        label=r"$|x_1-x_2|$ Newton" if ax is axs[0] else None)
        ax.axhline(4.0, **fs.MASK_LINE)
        ax.axvline(T_RUN, **fs.MASK_LINE)
        ax.set_yscale("log")
        ax.set_xlim(0, xmax)
        ax.set_ylim(2, 400)
        ax.set_xlabel(r"$t\,[M]$")
    axs[0].set_ylabel(r"distance from the heavy hole $[M]$")
    axs[0].set_title(f"P1 window (t = 0-{T_RUN:.0f} M)", fontsize=9)
    axs[1].set_title("long term", fontsize=9)
    axs[0].legend(frameon=False, fontsize=6, loc="upper left", ncol=1)
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_baselines_p1")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
