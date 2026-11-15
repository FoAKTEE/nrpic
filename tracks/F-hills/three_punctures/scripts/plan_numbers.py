#!/usr/bin/env python3
"""Numbers of PLAN.md and the proposed inputs, from the registered Newtonian start states.

Closed forms (labels as in PLAN.md):
  r_t = a_b q^(1/3) (0911.1136 prp.tex:88), D = r_p / r_t (prp.tex:349);
  tidal-to-binding ratio at distance r: 2 (r_t / r)^3 [BACKGROUND];
  binary period 2 pi sqrt(a^3 / m_b); Peters merger time (5/256) a^4 / (m1 m2 m_b)
  [BACKGROUND; the equal-mass form was checked in run F-hills-20261115-045435-f62d553];
  parabolic pericentre speed sqrt(2 M_t / r_p), angular velocity v_p / r_p, l = 2 burst
  wavelength pi / Omega_p [BACKGROUND];
  quadrupole energy of a parabolic flyby (85 pi / (12 sqrt 2)) mu^2 M_t^(5/2) / r_p^(7/2)
  [BACKGROUND, TO VERIFY: locator to be found by kb];
  l = 2 fundamental quasinormal frequency of Schwarzschild 0.3737 / m [BACKGROUND];
  ADM mass of a corrected Bowen-York puncture m + (5/8) P^2 / m (0711.1165 second.tex
  lines 285-287, quoted from core's interface note);
  background factor Lambda_c = 1 + sum_{j != c} m_j / (2 d_cj) (core interface note, s. 3).
Writes plan_numbers.json into the output directory and the proposed inputs into
tracks/F-hills/three_punctures/inputs/ (written, not run: they need core/multi-puncture).
Usage: python3 plan_numbers.py <q10 newton_start.json> <q4 newton_start.json> <outdir>
"""
import json
import math
import os
import sys

import numpy as np

WT = "/data/haiyangw/nrpic/wt/F-hills"
INP = os.path.join(WT, "tracks/F-hills/three_punctures/inputs")
QNM = 0.3737


def numbers(js, name):
    c = json.load(open(js))["choice"]
    M, m1, m2 = c["masses"]
    mb = m1 + m2
    q = M / mb
    p = json.load(open(js))["configs"][c["config"]]["params"]
    a, rp = p["a"], p["rp"]
    Mt = M + mb
    rt = a * q ** (1 / 3)
    r0 = c["r0"]
    x = np.array(c["from10"]["positions"])
    P = np.array(c["from10"]["momenta"])
    mm = np.array([M, m1, m2])
    d = {(i, j): float(np.linalg.norm(x[i] - x[j])) for i in range(3) for j in range(3) if i != j}
    lam = [1 + sum(mm[j] / (2 * d[(i, j)]) for j in range(3) if j != i) for i in range(3)]
    vp = math.sqrt(2 * Mt / rp)
    Om = vp / rp
    mu = M * mb / Mt
    unit = m1 * m2 / a * q ** (1 / 3)
    E1, E2 = c["E1_r10"] * unit, c["E2_r10"] * unit
    mu1, mu2 = M * m1 / (M + m1), M * m2 / (M + m2)
    out = dict(
        name=name, M=M, m1=m1, m2=m2, q=q, a_b=a, a_b_over_m_b=a / mb, r_t=rt, D=rp / rt,
        r_p=rp, r0=r0, r0_over_rt=r0 / rt, plunge_bound_a_over_mb=4 * q ** (2 / 3),
        tidal_ratio_r0=2 * (rt / r0) ** 3, tidal_ratio_10rt=2 / 1000.0,
        binary_period=2 * math.pi * math.sqrt(a ** 3 / mb),
        peters_time=5 / 256 * a ** 4 / (m1 * m2 * mb),
        t_to_pericentre_newton=c["t_to_pericentre"], v_pericentre=vp, Omega_pericentre=Om,
        burst_wavelength=math.pi / Om,
        E_flyby_quadrupole=85 * math.pi / (12 * math.sqrt(2)) * mu ** 2 * Mt ** 2.5 / rp ** 3.5,
        qnm_wavelength_member=2 * math.pi * m1 / QNM, qnm_wavelength_heavy=2 * math.pi * M / QNM,
        P=[float(np.linalg.norm(v)) for v in P], P_over_m=[float(np.linalg.norm(P[i]) / mm[i]) for i in range(3)],
        dM_ADM_uncorrected=[float(5 / 8 * np.linalg.norm(P[i]) ** 2 / mm[i]) for i in range(3)],
        Lambda=lam, eta_times_mass_for_eta2=[2.0 * v for v in mm],
        energy_unit=unit, E1=E1, E2=E2, E1_units=c["E1_r10"], E2_units=c["E2_r10"],
        v_inf_ejected=math.sqrt(2 * E1 / mu1) if E1 > 0 else None,
        a_captured_newton=M * m2 / (2 * abs(E2)) if E2 < 0 else None,
        rmin_captured=c["rmin_r10"][1], phase_deg=c["phase_deg"],
        positions=x.tolist(), momenta=P.tolist(), binary_sep_at_r0=c["from10"]["a12"],
        binary_ecc_at_r0=c["from10"]["e12"],
    )
    return out, c


def write_input(path, nm, c, half, nroot, nlev, rwz, lwz, tlim, comment):
    M, m1, m2 = c["masses"]
    x = c["from10"]["positions"]
    P = c["from10"]["momenta"]
    comps = [(m1, x[1], P[1]), (m2, x[2], P[2]), (M, x[0], P[0])]
    L = [f"# {line}" for line in comment] + ["", "<comment>",
         f"problem   = Hills passage, {nm['name']} (proposal of tracks/F-hills/three_punctures; not run)",
         "", "<job>", "basename  = hills", "", "<mesh>", "nghost    = 4"]
    for a in (1, 2, 3):
        L += [f"nx{a}       = {nroot}", f"x{a}min     = {-half}", f"x{a}max     = {half}",
              f"ix{a}_bc    = outflow", f"ox{a}_bc    = outflow"]
    L += ["", "<meshblock>", "nx1       = 16", "nx2       = 16", "nx3       = 16", "",
          "<mesh_refinement>", "refinement          = adaptive", f"num_levels          = {nlev}",
          "max_nmb_per_rank    = 2700      # T3b: at most 2332 (q = 10) / 2080 (q = 4) at m/8; check the card memory",
          "ncycle_check        = 4", "refinement_interval = 8", "",
          "<z4c_amr>", "method            = tracker",
          f"radius_0_rad      = {rwz[0]}", f"radius_0_reflevel = {lwz}",
          f"radius_1_rad      = {rwz[1]}", f"radius_1_reflevel = {lwz - 1}", "",
          "<time>", "evolution  = dynamic", "integrator = rk4", "cfl_number = 0.25", "nlim       = -1",
          f"tlim       = {tlim}", "ndiag      = 100", "",
          "<z4c>", "lapse_oplog     = 2.0", "lapse_harmonicf = 1.0", "lapse_harmonic  = 0.0",
          "lapse_advect    = 1.0", "shift_Gamma     = 0.75",
          f"shift_eta       = 2.0       # eta M = 2 for the heavy hole, eta m = {2 * m1:g} for a member",
          "shift_advect    = 1.0", "diss            = 0.5", "chi_div_floor   = 1.0e-5",
          "damp_kappa1     = 0.02", "damp_kappa2     = 0.0", "tracker_mode    = ode",
          "nrad_wave_extraction = 4", "extraction_radius_0  = 40.0", "extraction_radius_1  = 48.0",
          "extraction_radius_2  = 70.0", "extraction_radius_3  = 90.0", "extraction_nlev      = 10",
          "waveform_dt          = 0.25", "", "<problem>", "pgen_name       = nrpic_cf", "ncomp           = 3"]
    for k, (m, xx, pp) in enumerate(comps):
        L += [f"comp{k}_type      = puncture", f"comp{k}_mass      = {m:.10g}",
              f"comp{k}_x1        = {xx[0]:.10f}", f"comp{k}_x2        = {xx[1]:.10f}",
              f"comp{k}_x3        = 0.0",
              f"comp{k}_p1        = {pp[0]:.10f}", f"comp{k}_p2        = {pp[1]:.10f}",
              f"comp{k}_p3        = 0.0", f"comp{k}_corr      = approx"]
    L += ["corr_background = true", "lapse           = precollapsed", "puncture_setup  = true",
          "puncture_radius = 1.8", "", "<output1>", "file_type = hst", "dt        = 0.5", "",
          "<output2>", "file_type = bin", "variable  = z4c_alpha", "slice_x3  = 0.001", "dt        = 10.0", "",
          "<output3>", "file_type = bin", "variable  = con_H", "slice_x3  = 0.001", "dt        = 10.0", "",
          "<output4>", "file_type = rst", "dt        = 5.0", "",
          "# full fields once at the start, for the constraint check of the data (run R0)",
          "<output5>", "file_type = bin", "variable  = con", "dt        = 1.0e6", "",
          "<output6>", "file_type = bin", "variable  = adm_psi4", "dt        = 1.0e6", ""]
    with open(path, "w") as f:
        f.write("\n".join(L))


def write_single(path):
    """Run R2: one Bowen-York puncture with the members' P/m, spheres far out."""
    L = ["# Run R2 of tracks/F-hills/three_punctures/PLAN.md (proposal; not run): junk radiation",
         "# of one Bowen-York puncture with P/m = 0.28 (the members of the first configuration),",
         "# closed-form correction, measured on spheres at 40, 60, 80 m (core's test 1b had",
         "# 10 and 14). m = 1 at x = -10 moving along +x; cells m/16 at the puncture, 1 within 88.",
         "# Variant with no correction: problem/comp0_corr=none. Variant for the gauge",
         "# calibration of the members (eta m = 0.1): z4c/shift_eta=0.1.",
         "", "<comment>", "problem   = junk of one Bowen-York puncture, P/m = 0.28", "",
         "<job>", "basename  = junk1", "", "<mesh>", "nghost    = 4"]
    for a in (1, 2, 3):
        L += [f"nx{a}       = 64", f"x{a}min     = -256.0", f"x{a}max     = 256.0",
              f"ix{a}_bc    = outflow", f"ox{a}_bc    = outflow"]
    L += ["", "<meshblock>", "nx1       = 16", "nx2       = 16", "nx3       = 16", "",
          "<mesh_refinement>", "refinement          = adaptive", "num_levels          = 8",
          "max_nmb_per_rank    = 2400", "ncycle_check        = 4", "refinement_interval = 8", "",
          "<z4c_amr>", "method            = tracker", "radius_0_rad      = 88.0",
          "radius_0_reflevel = 3", "", "<time>", "evolution  = dynamic", "integrator = rk4",
          "cfl_number = 0.25", "nlim       = -1", "tlim       = 110.0", "ndiag      = 100", "",
          "<z4c>", "lapse_oplog     = 2.0", "lapse_harmonicf = 1.0", "lapse_harmonic  = 0.0",
          "lapse_advect    = 1.0", "shift_Gamma     = 0.75", "shift_eta       = 2.0",
          "shift_advect    = 1.0", "diss            = 0.5", "chi_div_floor   = 1.0e-5",
          "damp_kappa1     = 0.02", "damp_kappa2     = 0.0", "tracker_mode    = ode",
          "nrad_wave_extraction = 3", "extraction_radius_0  = 40.0", "extraction_radius_1  = 60.0",
          "extraction_radius_2  = 80.0", "extraction_nlev      = 10", "waveform_dt          = 0.25", "",
          "<problem>", "pgen_name       = nrpic_cf", "ncomp           = 1",
          "comp0_type      = puncture", "comp0_mass      = 1.0", "comp0_x1        = -10.0",
          "comp0_x2        = 0.0", "comp0_x3        = 0.0", "comp0_p1        = 0.28",
          "comp0_p2        = 0.0", "comp0_p3        = 0.0", "comp0_corr      = approx",
          "lapse           = precollapsed", "puncture_setup  = true", "puncture_radius = 1.8", "",
          "<output1>", "file_type = hst", "dt        = 0.5", "",
          "<output2>", "file_type = rst", "dt        = 10.0", ""]
    with open(path, "w") as f:
        f.write("\n".join(L))


def main():
    q10js, q4js, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    os.makedirs(INP, exist_ok=True)
    n10, c10 = numbers(q10js, "q10_ab3_rp8")
    n4, c4 = numbers(q4js, "q4_ab5_rp9.8")
    res = {"q10": n10, "q4": n4}
    with open(os.path.join(out, "plan_numbers.json"), "w") as f:
        json.dump(res, f, indent=1)
    for k, v in res.items():
        print(k)
        for kk, vv in v.items():
            if kk not in ("positions", "momenta"):
                print(f"   {kk} = {vv}")
    write_input(os.path.join(INP, "hills_q10_m8.athinput"), n10, c10, 204.8, 64, 11, (48.0, 100.0), 2,
                250.0, ["First Hills passage, q = M/m_b = 10: M = 1, m1 = m2 = 0.05, a_b = 3, r_p = 8",
                        "(D = 1.24), coplanar prograde, binary phase 130 deg, start at 4 r_t = 25.85.",
                        "Positions and momenta: newton3 driver integrated from 10 r_t and read at 4 r_t",
                        "(run F-hills-20261115-130755-982aba0). Members at m/8 (cells 0.00625, level 10),",
                        "heavy hole at M/10 (level 6, set by puncture_setup). Wave zone: cells 1.6 within",
                        "48 and 3.2 within 100 (free at t = 0, run F-hills-20261115-131348-634fb86).",
                        "Cost: 39 card-hours for 240 M (same run). Needs core/multi-puncture."])
    write_input(os.path.join(INP, "hills_q4_m8.athinput"), n4, c4, 256.0, 64, 10, (48.0, 100.0), 2,
                280.0, ["Cheaper Hills passage, q = 4: M = 1, m1 = m2 = 0.125, a_b = 5, r_p = 9.82",
                        "(D = 1.24), coplanar prograde, binary phase 127 deg, start at 4 r_t = 31.75.",
                        "Positions and momenta: newton3 driver from 10 r_t read at 4 r_t",
                        "(run F-hills-20261115-131832-907e5fe). Members at m/8 (cells 0.015625, level 9),",
                        "heavy hole at M/8 (level 6). Wave zone: cells 2 within 48, 4 within 100.",
                        "Cost: 15 card-hours for 270 M (run F-hills-20261115-131933-907e5fe).",
                        "Needs core/multi-puncture."])
    write_single(os.path.join(INP, "junk_single_P028.athinput"))
    print("inputs written to", INP)


if __name__ == "__main__":
    main()
