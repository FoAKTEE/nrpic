"""Figure: the Einstein-Straus slice and its exact evolution.

Reads the data set of run es_data (format-2 table es.tab, es.json, es_reference.csv) and
the lead's first-run plan (first_run_plan.json). Panel (a): extrinsic curvature K^r_r,
K^theta_theta in units of the plateau Hubble rate and the dust density from the
Hamiltonian constraint on the table columns, against areal radius. Panel (b): exact areal
radius of the tracer groups, the wall and the outer dust edge against their proper time.
Checks P3-P5 of the note journal are computed and written to fig_es_numbers.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_es"


def radial_fall_time(R0, E, M, R_end):
    """Proper time for a radial geodesic starting at areal radius R0 with LTB energy E < 0
    (U^2 = 2E + 2M/R, U >= 0 at the start: outgoing or at rest) to reach R_end < R0.
    Cycloid R = Rmax (1 + cos eta)/2, tau = sqrt(Rmax^3/(8M)) (eta + sin eta)."""
    Rmax = M / (-E)
    c = np.sqrt(Rmax**3 / (8 * M))
    eta = lambda R: np.arccos(np.clip(2 * R / Rmax - 1, -1, 1))  # noqa: E731
    up = c * (eta(R0) + np.sin(eta(R0)))          # time from R0 up to Rmax (eta: eta0 -> 0)
    down = c * (eta(R_end) + np.sin(eta(R_end)))  # time from Rmax down to R_end
    return up + down


def main():
    out = C.out_dir("figures")
    es = C.load_json("es_data", "es.json")
    s = es["summary"]
    M, m_p, H, rho0 = s["M"], s["m_p"], s["H"], s["rho0"]
    tab = np.loadtxt(C.run_file("es_data", "es.tab"), comments="#")
    rbar, u, KL, KT = tab[:, 0], tab[:, 1], tab[:, 2], tab[:, 3]
    ok = rbar > 0
    rbar, u, KL, KT = rbar[ok], u[ok], KL[ok], KT[ok]
    psi = 1.0 + u + m_p / (2.0 * rbar)
    R = psi**2 * rbar
    du = np.gradient(u, rbar, edge_order=2)
    d2u = np.gradient(du, rbar, edge_order=2)
    lap = d2u + 2.0 * du / rbar                       # the puncture term is harmonic
    rho = (-8.0 * psi**-5 * lap + 4.0 * KL * KT + 2.0 * KT**2) / (16.0 * np.pi)

    ref = np.loadtxt(C.run_file("es_data", "es_reference.csv"), delimiter=",")
    with open(C.run_file("es_data", "es_reference.csv")) as f:
        cols = f.readline().lstrip("#").strip().split(",")
    col = {c: i for i, c in enumerate(cols)}
    tau = ref[:, col["tau"]]
    plan = C.load_json("first_run", "first_run_plan.json")

    # P3: wall against the marginally bound closed form, mass inside the wall
    Rw0 = ref[0, col["R_wall"]]
    Rw_cf = (Rw0**1.5 + 1.5 * np.sqrt(2 * M) * tau) ** (2.0 / 3.0)
    p3_wall = float(np.max(np.abs(ref[:, col["R_wall"]] / Rw_cf - 1)))
    p3_mass = float(np.max(np.abs(ref[:, col["m_inside_wall"]] - 1)))
    # P4: arrival of the falling tracer groups at R = 2M
    p4 = {}
    for g in es["tracers"]:
        k = g["index"]
        Rk = ref[:, col[f"R_tracer{k}"]]
        below = np.nonzero(Rk <= 2 * M)[0]
        if g["E"] < 0:
            t_cf = float(radial_fall_time(g["R0"], g["E"], M, 2 * M))
            t_csv = float(tau[below[0]]) if below.size else None
            t_plan = plan["tau_reach_R=2M"].get(f"tracer{k}_R0={g['R0']}")
            p4[f"R0={g['R0']:g}"] = dict(E=g["E"], tau_closed=t_cf, tau_csv_first_below=t_csv,
                                        tau_plan=t_plan,
                                        tau_rest_cycloid=float(radial_fall_time(g["R0"], -M / g["R0"], M, 2 * M)))
    # P5: density from the Hamiltonian constraint on the table
    inner = R < 0.95 * 36.0
    inner &= rbar > 2 * 0.5242560805690288       # away from the puncture (round-off of psi^-5 lap)
    plateau = (R > 50) & (R < 90)
    ext = (R > 110) & (R < R.max() - 2)
    # P5b: the same on every second and fourth row: a second-order differencing error grows 4x
    sub = {}
    for step in (2, 4):
        r2, u2, l2, t2 = rbar[::step], u[::step], KL[::step], KT[::step]
        p2 = 1.0 + u2 + m_p / (2.0 * r2)
        d1 = np.gradient(u2, r2, edge_order=2)
        lap2 = np.gradient(d1, r2, edge_order=2) + 2.0 * d1 / r2
        rho2 = (-8.0 * p2**-5 * lap2 + 4.0 * l2 * t2 + 2.0 * t2**2) / (16.0 * np.pi)
        sub[f"drbar_x{step}"] = float(np.max(np.abs(rho2[inner[::step]])) / rho0)
    p5 = dict(inner_max_abs_rho_over_rho0=float(np.max(np.abs(rho[inner])) / rho0),
              inner_at_R=float(R[inner][np.argmax(np.abs(rho[inner]))]),
              inner_coarser=sub,
              plateau_max_rel_dev=float(np.max(np.abs(rho[plateau] / rho0 - 1))),
              exterior_max_abs_rho_over_rho0=float(np.max(np.abs(rho[ext])) / rho0),
              plateau_minus_KT_over_H=float(np.median(-KT[plateau]) / H),
              plateau_minus_KL_over_H=float(np.median(-KL[plateau]) / H))

    cz.use_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.75))
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.17, top=0.97, wspace=0.27)
    a.plot(R, -KT / H, color=cz.PAL["blue"], label=r"$-K^{\theta}{}_{\theta}/H$")
    a.plot(R, -KL / H, color=cz.PAL["red"], label=r"$-K^{r}{}_{r}/H$")
    a.plot(R, rho / rho0, color="k", ls="--", lw=1.2, label=r"$\rho/\rho_0$")
    for x in (s["R0"], s["Rin"], s["Rout"]):
        a.axvline(x, **cz.MASK_LINE)
    a.set_xscale("log")
    a.set_xlim(2.0, 140)
    a.set_ylim(-0.95, 4.2)
    a.set_xlabel(r"areal radius $R/M$")
    a.set_ylabel("curvature, density")
    a.legend(frameon=False, loc="upper right", handlelength=1.6)
    a.text(0.035, 0.93, "(a)", transform=a.transAxes)
    a.text(2.15, 0.2, "time-\nsymmetric", fontsize=7.5)
    a.text(12.0, -0.75, "vacuum bubble", fontsize=8, ha="center")
    a.text(62, -0.75, "dust", fontsize=8, ha="center")

    fall = [g for g in es["tracers"] if g["E"] < 0]
    expand = [g for g in es["tracers"] if g["E"] >= 0 and g["R0"] < 105]
    for g in fall:
        Rk = ref[:, col[f"R_tracer{g['index']}"]]
        m = Rk > 2 * M
        b.plot(tau[m], Rk[m], color=cz.PAL["red"], lw=1.1)
    for g in expand:
        Rk = ref[:, col[f"R_tracer{g['index']}"]]
        b.plot(tau, Rk, color=cz.PAL["blue"], lw=1.1)
    b.plot(tau, ref[:, col["R_wall"]], color="k", lw=1.6, label="wall")
    b.plot(tau, ref[:, col["R_outer"]], color=cz.PAL["blue"], lw=1.6, ls="--", label="outer dust edge")
    taus = [50, 100, 150, 200]
    b.plot(taus, [plan[f"tau={t}"]["R_wall"] for t in taus], "o", ms=3.5, mfc="white",
           mec="k", label="checkpoints of the first run")
    b.axhline(2 * M, **cz.GUIDE)
    b.text(330, 2.3, r"$R=2M$", fontsize=8)
    b.set_yscale("log")
    b.set_xlim(0, 400)
    b.set_ylim(1.5, 400)
    b.set_xlabel(r"proper time $\tau/M$")
    b.set_ylabel(r"areal radius $R/M$")
    b.legend(frameon=False, loc="lower right", fontsize=8, handlelength=1.8, bbox_to_anchor=(1.0, 0.09))
    b.text(0.025, 0.93, "(b)", transform=b.transAxes)
    cz.save(fig, os.path.join(out, STEM))
    nums = dict(P3=dict(max_rel_wall_vs_closed=p3_wall, max_abs_mass_minus_1=p3_mass,
                        R_wall_0=float(Rw0)),
                P4=p4, P5=p5, M=M, m_p=m_p, H=H, rho0=rho0)
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps(nums, indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
