"""T5: rotation covariance of the inclined set-up, and regression of hrna_incl against hrna.

(a) Schwarzschild ('sch' and 'cks' with a = 0): the encounter built with an inclined CM orbit
    (L_z < L, Q > 0) equals the coplanar encounter (Q = 0) rotated about the x axis by the
    orbit's inclination: same outcome, trajectories equal step by step.
(b) hrna_incl.initial_state_incl(ic='coord', iota=0 / pi) reproduces hrna.initial_state
    (sense +1 / -1) in 'sch' and in 'cks' with a = 0.9.
(c) Kerr: hrna_incl with spin +0.9 and L_z < 0 rotated by pi about x equals hrna's equatorial
    set-up with spin -0.9 (the convention of geodesic_binary S4): trajectories step by step.

Run: <venv>/bin/python -I tests/t5_rotation.py <outdir>
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "scripts"))
import hrna_incl as H  # noqa: E402
import hrna  # noqa: E402

# 2402.02178 fiducial binary (main.tex:486, 504-515) and a strongly perturbed encounter
P = dict(mb=6.25e-6, q12=2 / 3, a0=0.125, r0=100.0)


def run_y0(y0, coords, spin, info, rec=200000):
    m1, m2 = info["m1"], info["m2"]
    t_max = 6.0 * (math.sqrt(2.0) / 3.0) * 2 * P["r0"] ** 1.5 + 200.0
    out = H.integrate_y0(y0, "hrna", coords, spin, m1, m2, P["a0"], P["r0"], 1e300, t_max,
                         record=rec)
    status, t, y, diag, rt, ry, nrec, nsteps, nrej = out
    return dict(status=int(status), t=float(t), y=np.array(y), rt=np.array(rt), ry=np.array(ry),
                nsteps=int(nsteps), el=H.binary_elements(np.array(y), m1, m2))


def matched_dpos(tA, YA, tB, YB):
    """Member-position differences of two step records at matched times: the step-size
    controller turns rounding into step-time offsets (its error estimate is a small difference),
    so record B is moved to A's times to first order, x_B + v_B (t_A - t_B)."""
    n = min(len(tA), len(tB))
    dt = (tA[:n] - tB[:n])[:, None]
    XB = np.concatenate([YB[:n, 0:3] + YB[:n, 3:6] * dt, YB[:n, 6:9] + YB[:n, 9:12] * dt], axis=1)
    XA = np.concatenate([YA[:n, 0:3], YA[:n, 6:9]], axis=1)
    return np.max(np.abs(XA - XB), axis=1), np.abs(dt[:, 0])


def case_a(coords, rp, iota_orb, iota, Omega, phase):
    """Inclined CM orbit vs rotated coplanar one (a = 0)."""
    Lmax = H.lz_range(rp, 0.0)[1]
    Lz = Lmax * math.cos(iota_orb)
    y_inc, inf_inc = H.initial_state_incl("hrna", coords, 0.0, P["mb"], P["q12"], P["a0"], rp, Lz,
                                          iota, Omega, phase, P["r0"])
    y_eq, inf_eq = H.initial_state_incl("hrna", coords, 0.0, P["mb"], P["q12"], P["a0"], rp, Lmax,
                                        iota, Omega, phase, P["r0"])
    # the inclined orbit's tangential direction is (0, cos i, -sin i): rotation about x by -i
    R = H.rot_x(-math.acos(max(-1.0, min(1.0, Lz / Lmax))))
    d0 = float(np.abs(H.rotate_y(y_eq, R) - y_inc).max())
    A = run_y0(y_inc, coords, 0.0, inf_inc)
    B = run_y0(y_eq, coords, 0.0, inf_eq)
    # sensitivity control: the coplanar run with its initial state changed at the rounding level
    rng = np.random.default_rng(12345)
    y_pert = y_eq * (1 + 2.2e-16 * rng.standard_normal(y_eq.shape))
    C = run_y0(y_pert, coords, 0.0, inf_eq)
    nC = min(len(C["rt"]), len(B["rt"]))
    dctl_raw = np.max(np.abs(C["ry"][:nC, [0, 1, 2, 6, 7, 8]] - B["ry"][:nC, [0, 1, 2, 6, 7, 8]]), axis=1)
    dctl, _ = matched_dpos(C["rt"], C["ry"], B["rt"], B["ry"])
    n = min(len(A["rt"]), len(B["rt"]))
    RB = np.array([H.rotate_y(B["ry"][i], R) for i in range(n)])
    dpos_raw = np.max(np.abs(A["ry"][:n, [0, 1, 2, 6, 7, 8]] - RB[:, [0, 1, 2, 6, 7, 8]]), axis=1)
    dpos, dtm = matched_dpos(A["rt"], A["ry"], B["rt"], RB)
    rel = np.max(np.abs(A["ry"][:n, [0, 1, 2, 6, 7, 8]] - RB[:, [0, 1, 2, 6, 7, 8]])
                 / np.abs(RB[:, [0, 1, 2, 6, 7, 8]]).max(axis=1, keepdims=True), axis=1)
    sep = np.linalg.norm(A["ry"][:n, 0:3] - A["ry"][:n, 6:9], axis=1)
    dsep = np.abs(sep - np.linalg.norm(RB[:, 0:3] - RB[:, 6:9], axis=1)) / P["a0"]
    return dict(coords=coords, rp=rp, iota_orb=iota_orb, Lz=Lz, Q=inf_inc["Q"], iota=iota,
                Omega=Omega, phase=phase, init_maxdiff=d0, nsteps=(A["nsteps"], B["nsteps"]),
                t_end=(A["t"], B["t"]), max_dpos=float(dpos.max()), max_rel=float(rel.max()),
                max_dsep_over_a0=float(dsep.max()), control_max_dpos=float(dctl.max()),
                max_dpos_step_index=float(dpos_raw.max()), control_max_dpos_step_index=float(dctl_raw.max()),
                max_step_time_offset=float(dtm.max()),
                control_nsteps=C["nsteps"],
                Eb=(A["el"]["Eb"], B["el"]["Eb"]), e=(A["el"]["e"], B["el"]["e"]),
                outcome_equal=bool((A["el"]["Eb"] < 0) == (B["el"]["Eb"] < 0))), (A["rt"][:n], dpos, dsep, C["rt"][:nC], dctl)


def case_b():
    """Regression against hrna.initial_state (2404 conventions, ic='coord')."""
    out = []
    for coords, spin in (("sch", 0.0), ("cks", 0.9)):
        for sense in (1, -1):
            for phase in (0.0, 0.7, 2.5):
                rp = 8.0
                y_h, info = hrna.initial_state("hrna", coords, spin, P["mb"], P["q12"], P["a0"],
                                               None, rp, phase, sense, P["r0"] / ((1 / P["mb"]) ** (1 / 3) * P["a0"]))
                Lz = H.lz_range(rp, spin)[1]
                xc, _, _ = H.parabolic_state(coords, spin, rp, Lz, P["r0"])
                psi = math.atan2(xc[1], xc[0])     # hrna measures the phase from e_x, hrna_incl from x_cm
                ph_m = phase - psi if sense == 1 else -(phase - psi)
                y_m, _ = H.initial_state_incl("hrna", coords, spin, P["mb"], P["q12"], P["a0"], rp,
                                              Lz, 0.0 if sense == 1 else math.pi, 0.0, ph_m,
                                              P["r0"], ic="coord")
                d = np.abs(y_h - y_m)
                vb = P["a0"] * math.sqrt(P["mb"] / P["a0"] ** 3)
                out.append(dict(coords=coords, spin=spin, sense=sense, phase=phase, psi=psi,
                                max_dpos_over_a0=float(max(d[0:3].max(), d[6:9].max()) / P["a0"]),
                                max_dvel_over_vb=float(max(d[3:6].max(), d[9:12].max()) / vb)))
    return out


def case_c(rp=8.0, iota=0.9, Omega=0.4, phase=1.3):
    """Kerr: spin +0.9, L_z < 0 rotated by pi about x == spin -0.9, L_z > 0."""
    Lneg = H.lz_range(rp, 0.9)[0]
    y_a, inf_a = H.initial_state_incl("hrna", "cks", 0.9, P["mb"], P["q12"], P["a0"], rp, Lneg,
                                      iota, Omega, phase, P["r0"])
    Lpos = H.lz_range(rp, -0.9)[1]                  # equatorial, L along +z, spin along -z
    y_b, inf_b = H.initial_state_incl("hrna", "cks", -0.9, P["mb"], P["q12"], P["a0"], rp, Lpos,
                                      iota, Omega, phase, P["r0"])
    R = H.rot_x(math.pi)
    d0 = float(np.abs(H.rotate_y(y_a, R) - y_b).max())
    A = run_y0(y_a, "cks", 0.9, inf_a)
    B = run_y0(y_b, "cks", -0.9, inf_b)
    n = min(len(A["rt"]), len(B["rt"]))
    RA = np.array([H.rotate_y(A["ry"][i], R) for i in range(n)])
    dpos, dtm = matched_dpos(A["rt"], RA, B["rt"], B["ry"])
    rng = np.random.default_rng(54321)
    C = run_y0(y_b * (1 + 2.2e-16 * rng.standard_normal(y_b.shape)), "cks", -0.9, inf_b)
    dctl, _ = matched_dpos(C["rt"], C["ry"], B["rt"], B["ry"])
    return dict(rp=rp, Lz_neg=Lneg, Lz_pos_mirror=Lpos, init_maxdiff=d0,
                nsteps=(A["nsteps"], B["nsteps"]), max_dpos=float(dpos.max()),
                control_max_dpos=float(dctl.max()), max_step_time_offset=float(dtm.max()),
                Eb=(A["el"]["Eb"], B["el"]["Eb"])), (A["rt"][:n], dpos)


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    res = {"a": [], "b": case_b()}
    curves = []
    for coords in ("sch", "cks"):
        for (rp, io, i, Om, ph) in ((10.0, 0.6, 0.8, 1.1, 0.4), (7.0, 1.3, 2.2, 0.3, 2.0),
                                    (6.0, 2.4, 1.6, 2.7, 5.0)):
            r, c = case_a(coords, rp, io, i, Om, ph)
            res["a"].append(r)
            curves.append((f"{coords}, $r_p={rp:g}$, $i_{{orb}}={io}$", c))
    rc, cc = case_c()
    res["c"] = rc
    res["pass"] = dict(
        a=all(r["outcome_equal"] and r["nsteps"][0] == r["nsteps"][1]
              and r["max_dpos"] <= 10 * max(r["control_max_dpos"], 1e-12) for r in res["a"]),
        b=all(r["max_dpos_over_a0"] < 1e-10 and r["max_dvel_over_vb"] < 1e-10 for r in res["b"]),
        c=bool(rc["nsteps"][0] == rc["nsteps"][1] and (rc["Eb"][0] < 0) == (rc["Eb"][1] < 0)
               and rc["max_dpos"] <= 10 * max(rc["control_max_dpos"], 1e-12)))
    with open(os.path.join(outdir, "t5_rotation.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax1 = fs.inch_axes(fig, 0.75, 0.5, 3.2, 2.3)
    ax2 = fs.inch_axes(fig, 4.6, 0.5, 3.2, 2.3)
    cols = fs.series_colors(len(curves) + 1)
    for (lab, (t, dpos, dsep, tc, dctl)), col in zip(curves, cols):
        ax1.semilogy(t, dpos + 1e-18, color=col, label=lab)
        ax2.semilogy(tc, dctl + 1e-18, color=col)
    t, dpos = cc
    ax1.semilogy(t, dpos + 1e-18, color="k", ls="--", label="Kerr $a=\\pm0.9$ mirror (c)")
    ax1.set_xlabel(r"$t\ [GM/c^3]$")
    ax2.set_xlabel(r"$t\ [GM/c^3]$")
    ax1.set_ylabel(r"max $|x_{\rm incl} - R\,x_{\rm copl}|$ at equal $t$ $[r_g]$")
    ax2.set_ylabel(r"control: max $|x - x_{\rm copl}|$, $\delta y_0 \sim 10^{-16}$")
    ax1.legend(fontsize=6, loc="upper left")
    ax1.set_ylim(1e-16, 1e-4)
    ax2.set_ylim(1e-16, 1e-4)
    fs.save(fig, os.path.join(outdir, "t5_rotation"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"])
