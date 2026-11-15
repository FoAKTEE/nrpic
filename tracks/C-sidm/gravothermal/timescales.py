"""Time scales and Knudsen numbers at the onset of the dynamical instability.

    python3 -E timescales.py <criteria.json of run_sequence.py> <outdir>

Question (work package C-pre-3): which part of the gravothermal evolution of G26
(arXiv:2601.17117) cannot be followed by a dynamical-time code, and where does the dynamical
instability begin? Inputs, all with locators:

G26 = kb-data/raw/arxiv/2601.17117/v2/src/SIDM_MS.tex
  R_s = 2.6 kpc, rho_s = 0.019 Msun/pc^3, M(<10 R_s) = 6.3e9 Msun, sigma/m = 5 cm^2/g,
  t0 = 0.26 Gyr                                                         SIDM_MS.tex:384
  LMFP/SMFP divider lambda = H, lambda = 1/(rho sigma), H = (v^2/(4 pi rho))^{1/2},
  P = rho v^2 (v one-dimensional)                                       SIDM_MS.tex:229, :233
  SMFP from t = 445.0 t0; max SMFP mass 5e7 Msun at 445.6 t0; at 445.8 t0 a core with
  rho > 1e10 rho_s inside R < 1e-3 R_s                                 SIDM_MS.tex:440
  m/R ~ 1e-6 at the end of the SMFP evolution                          SIDM_MS.tex:455
  t_c ~ 0.1 t0 at 445.8 t0, ~ 40 t0 at 460 t0                          SIDM_MS.tex:474
  horizon at t = 580 t0 with m ~ 3e-8 M ~ 200 Msun                     SIDM_MS.tex:465, :476
F21 = kb-data/raw/arxiv/2108.11967/v2/src/main.tex
  J1205 benchmark: M_seed = 1.9e9 Msun, C = 3.9e-2 (b = 0.1), R = 2.3e-3 pc,
  <rho_seed> = 3.5e25 Msun/kpc^3, rho_s = 8.1e7 Msun/kpc^3, t_halo = 124 Myr,
  t_seed ~ (rho_s/<rho_seed>)^{1/2} t_halo = 1.5e-9 t_halo ~ 69 days  main.tex:349, :355
The dimensionless threshold models come from this package's solver (criteria.json).

Physical constants (cgs) [BACKGROUND]: G, c, Msun, pc, yr below.
"""
import json
import math
import os
import sys

import tmb

G = 6.6743e-8
C = 2.99792458e10
MSUN = 1.98841e33
PC = 3.085677581e18
KPC = 1e3 * PC
YR = 3.15576e7
GYR = 1e9 * YR
DAY = 86400.0
MSUN_PC3 = MSUN / PC ** 3            # g/cm^3

G26 = dict(Rs_kpc=2.6, rhos_Msun_pc3=0.019, M_halo=6.3e9, sigma_m=5.0, t0_Gyr=0.26,
           t_smfp_t0=445.0, t_core_t0=445.8, rho_core_rhos=1e10, R_core_Rs=1e-3,
           tc_fast_t0=0.1, tc_slow_t0=40.0, t_bh_t0=580.0, M_bh=200.0, mR_end_smfp=1e-6)


def physical_core(model, M_msun, sigma_m):
    """Scale a dimensionless F21 model to total mass M (Msun) and cross-section sigma/m."""
    M = M_msun * MSUN
    zeta = (G * M / C ** 2) / model["E"]                 # cm, since M = (c^2 zeta/G) M^
    R = model["R"] * zeta
    dens = C ** 2 / (G * zeta ** 2)                       # g/cm^3 per unit hatted density
    rho_c = model["rho0"] * dens                         # central total energy density / c^2
    p_c = model["p0"] * dens * C ** 2                    # central pressure, erg/cm^3
    # rest-mass density at the centre: n^ = 4 sqrt2 pi I_n; rho_rest = m n = dens * n^
    rho_rest_c = tmb.local(model["b"], model["w0"])[0] * dens
    rho_mean = 3 * M / (4 * math.pi * R ** 3)
    t_dyn_c = 1.0 / math.sqrt(4 * math.pi * G * rho_c)
    t_dyn_mean = 1.0 / math.sqrt(4 * math.pi * G * rho_mean)
    lam_c = 1.0 / (rho_rest_c * sigma_m)                 # mean free path at the centre, cm
    v1_c = math.sqrt(p_c / (rho_c * C ** 2)) * C          # one-dimensional dispersion, cm/s
    H_c = math.sqrt(v1_c ** 2 / (4 * math.pi * G * rho_c))
    return dict(M_msun=M_msun, R_km=R / 1e5, rho_c=rho_c, rho_mean=rho_mean,
                t_dyn_c_s=t_dyn_c, t_dyn_mean_s=t_dyn_mean, t_light_s=R / C,
                lam_c_cm=lam_c, Kn_R=lam_c / R, Kn_H=lam_c / H_c,
                t_coll_c_s=lam_c / (math.sqrt(3) * v1_c),
                sigma_m_code=sigma_m * M / (G * M / C ** 2) ** 2)


def main(crit_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    crit = json.load(open(crit_path))
    out = {}
    L = ["# Time scales at the onset of the dynamical instability", ""]

    # --- check of F21's own J1205 numbers (main.tex:349, :355)
    Ms = 1.9e9 * MSUN
    Cb = 3.9e-2
    R = G * Ms / (Cb * C ** 2)
    rho_seed = 3 * Ms / (4 * math.pi * R ** 3)
    rho_seed_kpc = rho_seed / (MSUN / KPC ** 3)
    t_seed = math.sqrt(8.1e7 / rho_seed_kpc) * 124e6 * YR
    out["F21_J1205_check"] = dict(R_pc=R / PC, rho_seed_Msun_kpc3=rho_seed_kpc,
                                  t_seed_days=t_seed / DAY,
                                  paper=dict(R_pc=2.3e-3, rho_seed=3.5e25, t_seed_days=69))
    L += ["## F21 J1205 benchmark recomputed (main.tex:349, :355)", "",
          f"R = {R / PC:.3e} pc (paper 2.3e-3), <rho_seed> = {rho_seed_kpc:.3e} Msun/kpc^3 "
          f"(paper 3.5e25), t_seed = {t_seed / DAY:.1f} days (paper ~69)", ""]

    # --- G26's own core at the end of the fast SMFP phase (SIDM_MS.tex:440, :474)
    t0 = G26["t0_Gyr"] * GYR
    rho_core = G26["rho_core_rhos"] * G26["rhos_Msun_pc3"] * MSUN_PC3
    R_core = G26["R_core_Rs"] * G26["Rs_kpc"] * KPC
    t_dyn_core = 1.0 / math.sqrt(4 * math.pi * G * rho_core)
    lam_core = 1.0 / (rho_core * G26["sigma_m"])
    g26 = dict(rho_core_g_cm3=rho_core, R_core_pc=R_core / PC, t_dyn_core_yr=t_dyn_core / YR,
               t0_over_tdyn=t0 / t_dyn_core,
               tc_fast_over_tdyn=G26["tc_fast_t0"] * t0 / t_dyn_core,
               tc_slow_over_tdyn=G26["tc_slow_t0"] * t0 / t_dyn_core,
               Kn_core=lam_core / R_core,
               remaining_after_core_t0=G26["t_bh_t0"] - G26["t_core_t0"])
    out["G26_core_445.8t0"] = g26
    L += ["## G26 core at 445.8 t0 (rho > 1e10 rho_s inside 1e-3 R_s; SIDM_MS.tex:440, :474)", "",
          f"rho = {rho_core:.3e} g/cm^3 (lower bound), t_dyn = 1/(4 pi G rho)^1/2 = "
          f"{t_dyn_core / YR:.3e} yr (upper bound)",
          f"t0/t_dyn >= {g26['t0_over_tdyn']:.3e}; fastest gravothermal time t_c ~ 0.1 t0 = "
          f"{g26['tc_fast_over_tdyn']:.3e} t_dyn; t_c ~ 40 t0 = {g26['tc_slow_over_tdyn']:.3e} t_dyn",
          f"Knudsen number lambda/R_core = {g26['Kn_core']:.3e} (SMFP); the remaining "
          f"{g26['remaining_after_core_t0']:.0f} t0 to the horizon cover >= "
          f"{g26['remaining_after_core_t0'] * g26['t0_over_tdyn']:.2e} t_dyn of this core", ""]

    # --- threshold models scaled to G26's seed (200 Msun) and F21's (1.9e9 Msun)
    L += ["## F21 threshold models scaled to a core mass M and sigma/m = 5 cm^2/g", "",
          "| b | criterion | Z(0) | M (Msun) | R (km) | t_dyn,c (s) | R/c (s) | Kn_R | Kn_H "
          "| t_coll,c/t_dyn,c | t0/t_dyn,c | sigma/m in units M^-1 (G=c=1) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for b, c in crit.items():
        for tag in ("max_eps", "gavg_eq_gcr", "omega2_zero_F21gamma"):
            e = c.get(tag)
            if e is None:
                continue
            for Mm in (G26["M_bh"], 1.9e9):
                ph = physical_core(e, Mm, G26["sigma_m"])
                ph.update(b=float(b), criterion=tag, Z0=e["Z0"], C=e["C"],
                          t0_over_tdyn=t0 / ph["t_dyn_c_s"],
                          tcoll_over_tdyn=ph["t_coll_c_s"] / ph["t_dyn_c_s"])
                rows.append(ph)
                L.append(f"| {b} | {tag} | {e['Z0']:.3f} | {Mm:.3g} | {ph['R_km']:.3e} | "
                         f"{ph['t_dyn_c_s']:.3e} | {ph['t_light_s']:.3e} | {ph['Kn_R']:.2e} | "
                         f"{ph['Kn_H']:.2e} | {ph['tcoll_over_tdyn']:.2e} | "
                         f"{ph['t0_over_tdyn']:.2e} | {ph['sigma_m_code']:.2e} |")
    out["threshold_models_scaled"] = rows
    L += ["", "Conversion (G = c = 1, total mass M = 1 of the code): Kn_R = lambda_c/R = "
          "1/(s n^(0) M^ R^), s = (sigma/m) c^4/(G^2 M) = sigma/m in units of M^-1 "
          "(last column); Kn_H uses H = (v_1^2/(4 pi rho_c))^1/2 at the centre (G26's "
          "LMFP/SMFP divider, SIDM_MS.tex:233). t_coll = lambda/(3^1/2 v_1)."]
    json.dump(out, open(os.path.join(outdir, "timescales.json"), "w"), indent=1)
    open(os.path.join(outdir, "timescales.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
