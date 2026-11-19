#!/usr/bin/env python3
"""1PN-consistent start states for the passages, and the predictions from them (JOURNAL entry 9).

For each NR input (nr_first/inputs/p1_q4.athinput, three_punctures/inputs/hills_q10_m8.athinput)
the binary is released at 40 r_t with its centre of mass on the 1PN parabola whose angular
momentum is that of the GR parabola with the input's nominal pericentre (areal; 2404.16270
appendix.tex l. 175; the second check's request R1), Newtonian-circular with the input's
nominal a (eih.far_states), and integrated with EIH to the input's start distance r0 (eih.
state_at_r0_1pn). The release phase is chosen so that the binary's orientation (angle of
x2 - x1) at r0 equals that of the input. Output: positions (harmonic = isotropic at 1PN) and
canonical 1PN momenta as an nrpic_cf <problem> block (newton3's multi_puncture_block), and
predictions from that state: EIH (canonical reading, consistent by construction), Newton and
HRNA (v = P/m, as they read the inputs). Needs numba (venv-gb). Usage: p1_state.py [outdir]
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRK = os.path.dirname(PKG)
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
import eih  # noqa: E402
from hills3 import threebody as tb  # noqa: E402
import p1  # noqa: E402

CASES = {"q4": dict(rp=9.82, k_from=40.0), "q10": dict(rp=8.0, k_from=40.0)}


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    allres = {}
    import matplotlib
    matplotlib.use("Agg")
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    for qn, case in CASES.items():
        c = p1.CASES[qn]
        ms, x0, P0 = eih.puncture_masses_positions_momenta(c["path"])
        M, m1, m2 = ms
        mb = m1 + m2
        a0 = c["a"]
        rt = a0 * (M / mb) ** (1 / 3)
        xc0 = (m1 * x0[1] + m2 * x0[2]) / mb
        r0 = float(np.linalg.norm(xc0 - x0[0]))
        d0 = x0[2] - x0[1]
        target = math.atan2(d0[1], d0[0])
        J = math.sqrt(2 * M * case["rp"] ** 2 / (case["rp"] - 2 * M))
        # the input's orbit plane and sense: angular momentum along +z for both inputs
        sense = 1

        def mismatch(ph):
            st = eih.state_at_r0_1pn(M, m1, m2, a0, J, r0, case["k_from"] * rt, ph, sense)
            # rotate: the input's centre-of-mass position angle vs ours
            ang_in = math.atan2((xc0 - x0[0])[1], (xc0 - x0[0])[0])
            xx = st["x"]
            xc = (m1 * xx[1] + m2 * xx[2]) / mb
            ang_us = math.atan2((xc - xx[0])[1], (xc - xx[0])[0])
            return wrap((st["angle12"] - ang_us) - (target - ang_in)), st, ang_in - ang_us
        grid = np.linspace(0, 2 * np.pi, 25)[:-1]
        mm = [mismatch(g)[0] for g in grid]
        k = None
        for i in range(len(grid)):
            a, b = mm[i], mm[(i + 1) % len(grid)]
            if a < 0 <= b and abs(b - a) < 2.0:
                k = i
                break
        lo, hi = grid[k], grid[k] + (grid[1] - grid[0])
        ph = brentq(lambda p_: mismatch(p_)[0], lo, hi, xtol=1e-12)
        mis, st, rot = mismatch(ph)
        # rotate our state about z so that the CM direction matches the input's
        cr, sr = math.cos(rot), math.sin(rot)
        Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
        x = st["x"] @ Rz.T
        v = st["v"] @ Rz.T
        p = st["p"] @ Rz.T
        state = dict(names=["M", "m1", "m2"], masses=ms, positions=x, momenta=p)
        block = tb.multi_puncture_block(state)
        with open(os.path.join(out, f"problem_block_{qn}_1pn.txt"), "w") as fh:
            fh.write(block)
        unit = m1 * m2 / a0 * (M / mb) ** (1 / 3)
        res = dict(input=os.path.relpath(c["path"], os.path.join(TRK, "..", "..")),
                   J_per_mu=J, rp_areal=case["rp"], k_from=case["k_from"], release_phase=ph,
                   orientation_mismatch=mis, r0=r0, t_from_release=st["t"],
                   cm_E_per_mu=st["cm_E_per_mu"], cm_J_per_mu=st["cm_J_per_mu"],
                   r12=st["r12"], binary_a_newton=st["binary_a_newton"],
                   input_r12=float(np.linalg.norm(d0)),
                   positions=x.tolist(), momenta=p.tolist(), velocities=v.tolist(),
                   input_positions=x0.tolist(), input_momenta=P0.tolist(),
                   momentum_change_rel=(np.linalg.norm(p - P0, axis=1)
                                        / np.linalg.norm(P0, axis=1)).tolist(),
                   position_change=np.linalg.norm(x - x0, axis=1).tolist(), models={})
        curves = {}
        for name, msx, vv, c2 in (("newton", ms, p / ms[:, None], 0.0),
                                  ("eih_p", ms, v, 1.0)):
            tt, X, V, _ = p1.integrate(msx, x, vv, c2)
            s, cv = p1.summarize_nbody(name, tt, X, V, msx, unit, a0, c["tlim"], c2)
            res["models"][name] = s
            curves[name] = cv
        s, cv = p1.run_hrna(ms, x, p / ms[:, None], a0, rt, unit, c["tlim"])
        res["models"]["hrna"] = s
        curves["hrna"] = cv
        for k_, s in res["models"].items():
            print(qn, k_, json.dumps({kk: s.get(kk) for kk in ("outcome", "leaves",
                  "E_out_units", "E1_u", "E2_u", "rmin_m1", "rmin_m2", "dE_run_units")},
                  default=float))
        allres[qn] = res
        fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.2, 3.0))
        sty = dict(newton=dict(color="grey", lw=1.5, label="Newton (v = P/m)"),
                   hrna=dict(color=fs.PAL["green"], lw=1.5, label="HRNA (v = P/m)"),
                   eih_p=dict(color=fs.PAL["blue"], lw=1.5, label="EIH (1PN-consistent)"))
        for name, cv in curves.items():
            msk = cv["t"] <= 320
            ax[0].plot(cv["t"][msk], cv["r1"][msk], **sty[name])
            ax[1].plot(cv["t"][msk], cv["r2"][msk], **sty[name])
            ax[2].semilogy(cv["t"][msk], cv["r12"][msk], **sty[name])
        for k_ in (0, 1):
            ax[k_].axhspan(0, p1.R_GRCAP, color="grey", alpha=0.15, lw=0)
            ax[k_].axhline(p1.R_TRUST, **fs.MASK_LINE)
            ax[k_].set_ylim(0, 60)
        for k_ in range(3):
            ax[k_].set_xlabel(r"$t/M$")
        ax[0].set_ylabel(r"$|x_1 - x_M|/M$")
        ax[1].set_ylabel(r"$|x_2 - x_M|/M$")
        ax[2].set_ylabel(r"$|x_1 - x_2|/M$")
        ax[0].legend(frameon=False, fontsize=6.5)
        ax[0].set_title(f"{qn}: 1PN-consistent start state", fontsize=8)
        fig.tight_layout()
        fs.save(fig, os.path.join(out, f"fig_p1_state_{qn}"))
        plt.close(fig)
    with open(os.path.join(out, "p1_state.json"), "w") as fh:
        json.dump(allres, fh, indent=1, default=float)


if __name__ == "__main__":
    main()
