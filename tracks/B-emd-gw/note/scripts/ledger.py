"""Numerical ledger, parameter table and claims check of Track B's working note v0.

Writes into ../tables (or --out DIR):
  ledger.tex          the ledger appendix: every number of the note with its registered run
  parameters.tex      the parameter table of the scenarios
  claims.md, .json    numbers stated in the lead's documents checked against the run outputs
  claims_summary.tex  one sentence for the note: how many agree, how many differ
  checked.md          every file read, its run, and how its checksum was checked
Every value is read from a registered run directory through common.load_json.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import g1data  # noqa: E402

R = common.RUNS


class Sig(float):
    """A value printed with its own number of significant digits."""
    def __new__(cls, x, sig):
        o = float.__new__(cls, x)
        o.sig = sig
        return o


def fmt(x, sig=3):
    if isinstance(x, str):
        return x
    sig = getattr(x, "sig", sig)
    if x == 0:
        return "0"
    s = f"{x:.{sig}g}"
    if "e" in s:
        m, e = s.split("e")
        return f"${m}\\times10^{{{int(e)}}}$"
    return s


def load():
    d = {}
    d["lw"] = common.load_json("lead_recheck", "export/tracks/B-emd-gw/periodic_z4c/tables/lw_x.json")
    d["lw3d"] = common.load_json("lead_recheck", "export/tracks/B-emd-gw/periodic_z4c/tables/lw3d_check.json")
    d["awa"] = common.load_json("lead_recheck", "export/tracks/B-emd-gw/periodic_z4c/tables/awa.json")
    d["tt"] = common.load_json("lead_recheck", "gw_tt/results_tt.json")
    d["ak"] = common.load_json("athenak_gw", "results_athenak.json")
    d["cw"] = common.load_json("crossed_tt", "crossed_waves_tt.json")
    d["i3"] = common.load_json("item3", "check_item3.json")
    d["rg"] = common.load_json("regime", "regime_estimates.json")
    d["pc"] = common.load_json("pancake", "pancake.json")
    d["fl"] = common.load_json("flrw", "flrw_recheck.json")
    d["bl"] = common.load_json("baseline", "baseline_results.json")
    d["lc"] = common.load_json("lead_checks", "lead_checks.json")
    d["cd"] = common.load_json("cosmo_dumps", "results_cosmo.json")
    d["lr"] = common.load_json("late_rise", "late_rise.json")
    # wave 2 (G1)
    d["scan"] = g1data.scan_numbers()
    d["gauge"] = g1data.gauge_numbers()
    d["nwp"] = common.load_json("nw_pancake", "pancake.json")
    d["nwe"] = common.load_json("nw_ellipsoid", "ellipsoid.json")
    d["rvn"] = common.load_json("review_nw", "rv_newton.json")
    d["rvf"] = common.load_json("review_fs", "rv_first_source.json")
    d["slc"] = common.load_json("slicing", "slicing_check.json")
    return d


def symbol_dev(lw):
    """Largest relative departure of measured from predicted errors, N <= 64, per set and kind."""
    out = {}
    for s in ("lw_x_prod", "lw_x_ref"):
        for kind in ("amp", "phase"):
            v = [abs(r[kind]/r["pred_" + kind] - 1) for r in lw[s] if r["N"] <= 64]
            out[(s, kind)] = max(v)
    return out


def values(d):
    """name -> (value, run key, description) for every number the note or the claims use."""
    lw, ak, pc, bl, rg = d["lw"], d["ak"], d["pc"], d["bl"], d["rg"]
    v = {}
    prod = {r["N"]: r for r in lw["lw_x_prod"]}
    ref = {r["N"]: r for r in lw["lw_x_ref"]}
    v["lw_prod_amp"] = ([prod[n]["amp"] for n in (16, 32, 64)], "lead_recheck")
    v["lw_prod_phase"] = ([prod[n]["phase"] for n in (16, 32, 64)], "lead_recheck")
    v["lw_prod_orders"] = ([prod[32]["order_amp"], prod[64]["order_amp"],
                            prod[32]["order_phase"], prod[64]["order_phase"]], "lead_recheck")
    v["lw_ref_amp"] = ([ref[n]["amp"] for n in (16, 32, 64)], "lead_recheck")
    v["lw_ref_phase"] = ([ref[n]["phase"] for n in (16, 32, 64)], "lead_recheck")
    v["lw_ref_orders"] = ([ref[32]["order_amp"], ref[64]["order_amp"],
                           ref[32]["order_phase"], ref[64]["order_phase"]], "lead_recheck")
    sd = symbol_dev(lw)
    v["symbol_dev"] = ([sd[("lw_x_prod", "amp")], sd[("lw_x_prod", "phase")],
                        sd[("lw_x_ref", "amp")], sd[("lw_x_ref", "phase")]], "lead_recheck")
    v["floor128"] = ([prod[128]["amp"], prod[128]["phase"]], "lead_recheck")
    v["oblique_H2"] = ([d["lw3d"]["diag"]["H_norm2"], d["lw3d"]["axis"]["H_norm2"]], "lead_recheck")
    v["oblique_ek"] = ([d["lc"]["a"]["code"]["max_ek"], d["lc"]["a"]["flipped"]["max_ek"]], "lead_checks")
    a01 = d["awa"]["0.01"]
    v["awa_orders"] = ([a01[1]["order_g_max"], a01[1]["order_H"]], "lead_recheck")
    sp = d["tt"]["spectrum"]
    v["tt_analytic"] = ([sp["nmodes"], sp["shell_max_rel_err"]], "lead_recheck")
    last = ak["per_dump"][-1]
    psi4 = max(w["psi4x_err_vs_analytic"] for w in ak["weyl"] if w["t"] > 0)
    v["ak_t2"] = ([1 - last["amp_ratio"], last["phase_err"], 1 - last["rho_tot/ref"], psi4], "athenak_gw")
    fits = ak["weyl_output_timing"]["fits"]
    v["weyl_lag"] = ([fits[0]["best_offset_steps"], ak["weyl_output_timing"]["dt_step"]], "athenak_gw")
    cw = d["cw"]
    v["cw_dev"] = ([cw["eps_scan_max_rel_dev_from_5_12"], cw["cases"]["plane (1,0,0)"]["max_TT_strain"]], "crossed_tt")
    v["cw_three"] = ([cw["cases"]["cosmo/ runs (1,0.9,1.1)"]["hplus_kk0_abs"]], "crossed_tt")
    v["cw_lead"] = ([d["lc"]["d"]["hplus_cos_amplitude"], d["lc"]["d"]["rel_dev"]], "lead_checks")
    v["junk"] = ([rg["3A"]["log_slope_10_100"], rg["3A"]["envelope_at_a_60_over_hs"]], "regime")
    v["vir_range"] = (rg["3B"]["L4_ratio_range_0.0025_0.05"], "regime")
    rows = rg["3C"]
    v["cost_d01"] = ([r["card_hours"] for r in rows if r["delta"] == 0.01], "regime")
    v["cost_d0025"] = ([r["card_hours"] for r in rows if r["delta"] == 0.0025], "regime")
    v["cross_exact"] = ([pc["L1_n64"]["a_cross_zeldovich_sheets"]], "pancake")
    v["cross_l1"] = ([pc["L1_n32"]["a_cross"], pc["L1_n64"]["a_cross"], pc["L1_n96"]["a_cross"]], "pancake")
    v["cross_nw"] = ([pc["N_n32"]["a_cross"], pc["N_n64"]["a_cross"]], "pancake")
    v["cross_l4"] = ([pc["L4_n64"]["a_cross"], pc["L4_n64"]["a_p_cross_sheets"][0],
                      pc["L1_n64"]["a_p_cross_sheets"][0]], "pancake")
    dl1 = pc["diff_L1_n64_N_n64"]["dx_a10"]
    dl4 = pc["diff_L4_n64_N4_n64"]["dx_a10"]
    v["grdiff10"] = ([pc["diff_L1_n32_N_n32"]["dx_a10"], dl1, pc["L1_n96"]["ex_a10"], dl4, dl4/dl1], "pancake")
    c1, c2 = pc["constraints_L1_n64"], pc["constraints_L1_n64_p2"]
    v["Hr"] = ([c1["Hr_mean"]["10"], c1["Hr_mean"]["15"], c2["Hr_mean"]["10"], c2["Hr_mean"]["15"]], "pancake")
    v["Hr_ratio"] = ([c1["Hr_mean"]["15"]/c2["Hr_mean"]["15"], c1["Mr_mean"]["15"]/c2["Mr_mean"]["15"]], "pancake")
    v["Mr"] = ([c1["Mr_mean"]["15"], c2["Mr_mean"]["15"]], "pancake")
    v["Hr_after"] = ([max(c1["Hr_mean"][k] for k in ("22", "25", "30", "35", "41.9")),
                      max(c2["Hr_mean"][k] for k in ("22", "25", "30", "35", "41.9"))], "pancake")
    sym = [s for k in ("symmetry_L1_n32", "symmetry_L1_n64", "symmetry_L1_n96",
                       "symmetry_L4_n64", "symmetry_L1_n64_p2") for s in pc[k]]
    v["symmetry"] = ([max(s["spread_x_over_L"] for s in sym), max(s["max_u_perp"] for s in sym)], "pancake")
    v["newton"] = ([pc["N_n64"]["ex_a10"], pc["N_n32"]["ex_a10"], pc["N_n32_p2"]["ex_a10"]], "pancake")
    v["za_l1"] = ([pc["L1_n64"]["ex_a10"], pc["L1_n64_p2"]["ex_a10"]], "pancake")
    gr1, gr2 = common.manifest("pancake_gr"), common.manifest("pancake_gr_p2")
    v["card_h"] = ([gr1["card_hours"], gr2["card_hours"], gr1["card_hours"] + gr2["card_hours"]], "pancake_gr")
    cdv = []
    for run in ("dav_c256_n128_t", "dav_c256_n128_pcs4bt"):
        rows = d["cd"][run]["rows"]
        frozen = min(rows[1:], key=lambda r: abs(r["a"] - 36.0))
        last = rows[-1]
        cdv += [frozen["rms_hTT"], last["a"], last["rms_hTT"], last["rms_h_nonTT"]**2]
    v["cosmo_tt"] = (cdv, "cosmo_dumps")
    lrv = []
    for run in ("dav_c256_n128_t", "dav_c256_n128_pcs4bt"):
        r = d["lr"]["runs"][run][-1]
        lrv += [r["rms_TT"], r["rms_G"], r["rms_TT_minus_G"], r["rho_kin"]/r["rho_grad"]]
    v["late_rise"] = (lrv, "late_rise")
    fl = d["fl"]
    v["flrw"] = ([fl["flrw_n32_cpu_sd"]["max_rel_err_lapse"], fl["dtexp_test/lim"]["max_rel_err_lapse"],
                  fl["dtexp_test/lim"]["Hr_max_end"]], "flrw")
    T2 = bl["T2"]
    v["za_slopes"] = ([T2["max_dev_small_delta"]["E"], T2["max_dev_small_delta"]["wpeak"],
                       T2["max_dev_small_delta"]["peak"]], "baseline")
    v["self_sim"] = ([max(bl["T6"][m]["rel_spread_F"] for m in ("A", "B", "C"))], "baseline")
    cr = bl["T45"]["T5_crossings_2605_benchmark"]["B"]
    v["crossings_B"] = ([cr["first_x"], cr["first_y"], cr["rel_x_vs_paper"], cr["rel_y_vs_paper"]], "baseline")
    v["redshift"] = ([bl["T7"]["tk_over_trh_coefficient"]], "baseline")
    om = bl["T7"]["T7b"]["Omega_over_3.16e-10"]
    v["omega_factor"] = ([min(om), max(om)], "baseline")
    v["lead_e"] = ([d["lc"]["e"]["rel_dev"]], "lead_checks")
    v["lead_f"] = ([d["lc"]["f"]["conformal_t10_A1e-6"], d["lc"]["f"]["onelog_t10_A1e-6"]], "lead_checks")
    req = d["i3"]["1E_flat_transverse_zeldovich"]["dD_dt_required"][0].replace(" ", "")
    law = "$\\dot D=-\\tfrac32 D\\,\\dot a/a$" if req == "-3*D(t)*Derivative(a(t),t)/(2*a(t))" else req
    v["item3"] = (["yes" if d["i3"]["1A_tt_projector_along_x"]["vanishes_for_E2_symmetric"] else "no", law], "item3")
    values_g1(d, v)
    return v


def values_g1(d, v):
    """The numbers of the G1 sections (wave 2): first source, spatial gauge, Newtonian mode."""
    S, G, P, E = d["scan"], d["gauge"], d["nwp"], d["nwe"]
    names = ("cw_eps0p1", "cw_eps0p3", "cw_eps1")
    v["fs_ic"] = ([S["ic_ham_max"], S["ic_mom_max"], Sig(S["ic_particles"], 7)], "scan_ic64")
    v["fs_s"] = ([S["s_eps1"], S["a_cross_zeldovich"]], "scan64_a")
    v["fs_dev64"] = ([S[f"dev_64_{n}_K1_2_10"] for n in names], "scan64_a")
    v["fs_dev64K2"] = ([S[f"dev_64_{n}_K2_2_10"] for n in names], "scan64_a")
    v["fs_dev32"] = ([S[f"dev_32_{n}_K1_2_10"] for n in names], "scan32")
    for a0 in (20, 40, 60):
        v[f"fs_dev_a{a0}"] = ([S[f"dev_64_{n}_a{a0}"] for n in names], "scan64_a")
    v["fs_slope"] = ([S[f"dev_slope_64_{n}"] for n in names], "scan64_a")
    v["fs_scaled"] = ([S[f"dev_scaled_{n}_a{a0}"] for a0 in (20, 40, 60) for n in ("cw_eps0p3", "cw_eps1")],
                      "scan64_a")
    v["fs_lin"] = ([S["lin_cw_eps0p3_2_10"], S["lin_cw_eps1_2_10"]], "scan64_a")
    v["fs_lin_late"] = ([S["lin_cw_eps0p3_a20"], S["lin_cw_eps1_a20"], S["lin_cw_eps0p3_a60"],
                         S["lin_cw_eps1_a60"]], "scan64_a")
    v["fs_max"] = ([S["max_c_over_s_eps1"], S["a_of_max_eps1"], S["max_c_over_s_cw_eps0p1"],
                    S["max_c_over_s_cw_eps0p3"]], "scan64_b")
    v["fs_null"] = ([S["null_h_bin"], S["null_h_rst"], S["null_A_rst"], S["null_zdep_rst"]], "scan64_a")
    v["fs_res"] = ([S[f"res_{n}_5_40"] for n in names + ("cw_eps1_gd",)], "scan32")
    v["fs_res_late"] = ([max(S[f"res_{n}_40_80"] for n in names + ("cw_eps1_gd",)),
                         max(abs(S[f"res_{n}_a100"]) for n in names + ("cw_eps1_gd",))], "scan32")
    v["fs_box"] = ([S["box_share_cw_eps0p1_a10"], S["box_share_cw_eps1_a10"],
                    S["box_share_cw_eps0p1_a20"], S["box_share_cw_eps1_a20"]], "scan64_a")
    v["fs_kin"] = ([S["kin_over_grad_cw_eps0p1_a12"], S["kin_over_grad_cw_eps1_a12"]], "scan64_b")
    ma, mb = common.manifest("scan_cards_a"), common.manifest("scan_cards_b")
    ga, gb = ma["resources"]["gpu_hours"], mb["resources"]["gpu_hours"]
    v["fs_card"] = ([ga, gb, ga + gb], "scan_cards_a")
    t0 = G["t0_slopes"]
    nos = [k for k in t0 if k.startswith("slicing=False")]
    yes = [k for k in t0 if k.startswith("slicing=True")]
    v["g_t0"] = ([min(t0[k]["Lh"] for k in nos), min(t0[k]["Lh_minus_G"] for k in nos),
                  max(t0[k]["Lh_minus_G"] for k in yes)], "t0_gauge")
    v["g_size"] = ([G[f"Gtot_over_c_{n}_le20"] for n in names], "scan64_a")
    v["g_size40"] = ([G[f"Gtot_over_c_{n}_a40"] for n in names], "scan64_a")
    v["g_raw"] = ([G[f"raw_a{a0}"] for a0 in (5, 10, 20, 40, 60)], "scan64_b")
    v["g_cor"] = ([G[f"cor_a{a0}"] for a0 in (5, 10, 20, 40, 60)], "scan64_b")
    v["g_median"] = ([G["median_cor_over_raw_64"], G["median_cor_over_raw_32"], G["share_big_64"]], "scan64_b")
    v["g_quad"] = ([G["median_quad_over_raw_64"], G["median_quad_over_raw_32"]], "scan64_b")
    v["g_dev"] = ([G["dev_raw_a10"], G["dev_cor_a10"], G["dev_raw_a20"], G["dev_cor_a20"]], "scan64_b")
    v["g_nonTT"] = ([G["nonTT_ratio_min"], G["nonTT_ratio_max"]], "scan64_b")
    v["g_weyl"] = ([G["weyl_dB_median_le64"], G["weyl_dh_median_le64"]], "scan64_b")
    rows = [r for run in d["slc"].values() for r in run if 1.0 < r["a"] <= 125.0]
    v["g_slicing"] = ([max(r["corr"] for r in rows),
                       min(r["rms_dln_alpha_gamma16"] / r["rms_dln_alpha"] for r in rows),
                       max(r["rms_dln_alpha_gamma16"] / r["rms_dln_alpha"] for r in rows)], "slicing")
    F = d["rvn"]["R7"]
    v["n_force"] = ([F[str(n)]["F_minus_1"] for n in (16, 32, 64)], "review_nw")
    rat = []
    for n in (16, 32, 64):
        r = P[f"P1_athenak_n{n}"]
        rat += [Sig(r["ex_cont_a2"] / r["ex_h1_pred_a2"], 4), Sig(r["ex_cont_a5"] / r["ex_h1_pred_a5"], 4)]
    v["n_h1"] = (rat, "nw_pancake")
    p32, p64 = P["P1_athenak_n32"], P["P1_athenak_n64"]
    v["n_err"] = ([p32["ex_cont_a2"], p64["ex_cont_a2"], p32["ex_cont_a5"], p64["ex_cont_a5"],
                   p32["ex_cont_a2"] / p64["ex_cont_a2"], p32["ex_cont_a5"] / p64["ex_cont_a5"]], "nw_pancake")
    q32, q64 = P["P1_athenak_minus_pm_n32"], P["P1_athenak_minus_pm_n64"]
    v["n_pm"] = ([q32["pm_ex_cont_a2"], q32["pm_ex_cont_a5"], q64["pm_ex_cont_a2"], q64["pm_ex_cont_a5"]],
                 "nw_pancake")
    v["n_late"] = ([p32["ex_cont_a10"] / p32["ex_h1_pred_a10"], p32["ex_cont_a15"] / p32["ex_h1_pred_a15"]],
                   "nw_pancake")
    v["n_cross"] = ([Sig(P[f"P1_athenak_n{n}"]["a_cross"], 4) for n in (16, 32, 64)] +
                    [Sig(q32["a_cross_pm"], 4), Sig(q64["a_cross_pm"], 4)], "nw_pancake")
    v["n_sym"] = ([max(s_["spread_x"] for n in (16, 32, 64) for s_ in P[f"P1_athenak_n{n}"]["plane_symmetry"])],
                  "nw_pancake")
    v["n_d3I"] = ([P[f"P2_athenak_n{n}"]["d3I_rms_rel_1.2_15"] for n in (16, 32, 64)], "nw_pancake")
    v["n_LI"] = ([P[f"P2_athenak_n{n}"]["layzer_irvine_dC_over_max_aW"] for n in (16, 32, 64)], "nw_pancake")
    C = E["N1_convergence"]
    v["e_tx"] = ([Sig(x, 6) for x in C["t_x"]["values"]] +
                 [Sig(C["t_x_ode_nominal"], 6), Sig(C["t_x"]["richardson"], 6), C["t_x"]["order"]],
                 "nw_ellipsoid")
    v["e_E"] = ([x / C["E_ode_nominal"] - 1 for x in C["E_raw"]["values"]] +
                [C["E_raw"]["richardson"] / C["E_ode_nominal"] - 1, C["E_raw"]["order"]], "nw_ellipsoid")
    v["e_EM"] = ([E["N1_N128"]["ode"]["nominal"]["E_over_M"]], "nw_ellipsoid")
    v["e_early"] = ([E[f"N1_N{n}"]["ode"]["nominal"]["dE_early_rel"] for n in (32, 64, 128)], "nw_ellipsoid")
    v["e_step"] = ([E["N1f_N64_dt"]["vs_step_0.02"]["t_x_rel"]], "nw_ellipsoid")
    n3 = [E["N3_N32"], E["N3_N64"]]
    v["e_self"] = ([n3[0]["rows"]["0.1"]["F_avg"], n3[1]["rows"]["0.1"]["F_avg"],
                    max(n3[0]["spread_F_avg"], n3[1]["spread_F_avg"]), E["F_C_baseline"]], "nw_ellipsoid")
    v["n_card"] = ([common.manifest("nw_card")["resources"]["gpu_hours"]], "nw_card")
    rf = d["rvf"]["summary"]["cases"]
    v["rv_dev"] = ([rf[f"64/{n[3:]}"]["P2_K1_maxdev_a2_10"] for n in names], "review_fs")
    rn = d["rvn"]["R8"]
    v["rv_tx"] = ([Sig(rn[str(n)]["t_x"], 6) for n in (32, 64, 128)] +
                  [Sig(rn["richardson_t_x"][1], 6)], "review_nw")
    v["rv_self"] = ([max(d["rvn"]["R9"][k]["E_spread_rel"] for k in ("32", "64"))], "review_nw")


LEDGER = [
    ("Linear wave in the periodic vacuum box (ten crossings)", [
        ("lw_prod_amp", "amplitude error, cosmology numerics, $N=16,32,64$"),
        ("lw_prod_phase", "phase error (rad), cosmology numerics, $N=16,32,64$"),
        ("lw_prod_orders", "measured orders, amplitude 16--32, 32--64; phase 16--32, 32--64"),
        ("lw_ref_amp", "amplitude error, upstream test numerics, $N=16,32,64$"),
        ("lw_ref_phase", "phase error (rad), upstream test numerics, $N=16,32,64$"),
        ("lw_ref_orders", "measured orders, upstream numerics, as above"),
        ("symbol_dev", "largest relative departure from the Fourier-symbol prediction, $N\\le64$: amplitude, phase (cosmology); amplitude, phase (upstream)"),
        ("floor128", "amplitude and phase error at $N=128$ (rounding floor of $1+h$)"),
        ("oblique_H2", "$\\int\\mathcal H^2$ of the generator's oblique data, $k=(1,1,1)$; axis-aligned"),
        ("oblique_ek", "largest $|e_{ij}k^j|$ of the generator's tensor over random directions; with two signs flipped"),
        ("awa_orders", "gauge wave, $A=0.01$: orders of the metric error and of $\\mathcal H$, $N=50\\to100$"),
    ]),
    ("Diagnostics", [
        ("tt_analytic", "analytic random waves: number of modes; largest relative error of the shell energies"),
        ("ak_t2", "AthenaK wave at $t=2$, 32 cells: amplitude, phase (rad), energy density; largest $\\Psi_4$ error over the dumps"),
        ("weyl_lag", "lag of the code's own Weyl output (steps); step size"),
        ("cosmo_tt", "earlier three-wave relativistic dumps (two deposits): rms $h^{\\rm TT}$ at $a\\approx36$; $a$ of the last dump; rms $h^{\\rm TT}$ there; square of the rms non-TT part there"),
        ("late_rise", "the same dumps at $a\\approx1000$, two deposits: rms $h^{\\rm TT}$; rms of the spatial-gauge piece; rms after its removal; kinetic over gradient energy of the TT part"),
    ]),
    ("First source and regime", [
        ("cw_dev", "largest relative departure of the $(k,k,0)$ amplitude from $\\frac{5}{12}|\\phi_x\\phi_y|$; largest TT strain of the plane wave"),
        ("cw_three", "Fourier amplitude at $(k,k,0)$, three-wave data, $\\delta=0.01$, $L=4$"),
        ("cw_lead", "independent rederivation: real cosine amplitude of $h_+$; relative difference"),
        ("item3", "symbolic: TT projection vanishes for $E(2)$-symmetric data; growth law forced on a flat transverse slice"),
        ("junk", "junk TT of conformally flat data: logarithmic slope of the envelope, $10<a<100$; envelope at $a=60$ over the static value"),
        ("vir_range", "$\\omega_{\\rm vir}/(ck_1)$ for $\\delta=0.0025$--$0.05$, box of four Hubble radii"),
        ("cost_d01", "card-hours per run, $\\delta=0.01$ to $a=140$: $64^3$, $128^3$, $256^3$, $256^2\\times16$"),
        ("cost_d0025", "the same, $\\delta=0.0025$ to $a=560$"),
    ]),
    ("Plane-wave pancake through shell crossing", [
        ("cross_exact", "first crossing of the exact Zel'dovich sheets, 64 sheets (scale factor)"),
        ("cross_l1", "first crossing, relativistic, one Hubble radius, 32, 64, 96 cells (coordinate label)"),
        ("cross_nw", "first crossing, Newtonian particle mesh, 32, 64 cells"),
        ("cross_l4", "four Hubble radii, 64 cells: coordinate label; proper time of the crossing sheets; the same for one Hubble radius"),
        ("grdiff10", "relativistic minus Newtonian position at $a=10$: one Hubble radius, 32 and 64 cells; relativistic minus Zel'dovich, 96 cells; four Hubble radii; ratio of the two box sizes"),
        ("za_l1", "relativistic minus Zel'dovich at $a=10$, 64 cells, one and two particles per cell and direction"),
        ("newton", "Newtonian minus Zel'dovich at $a=10$: 64 cells; 32 cells; 32 cells with two per cell and direction"),
        ("Hr", "mean $|\\mathcal H|$ relative, $a=10,15$: one per cell; two per cell and direction (64 cells)"),
        ("Mr", "mean $|\\mathcal M|$ relative, $a=15$: one; two per cell and direction"),
        ("Hr_ratio", "ratio one to two per cell and direction at $a=15$: $\\mathcal H$, $\\mathcal M$"),
        ("Hr_after", "largest mean $|\\mathcal H|$ after crossing, $a=22$--$42$: one; two per cell and direction"),
        ("symmetry", "plane symmetry: largest spread of $x$ over a lattice plane ($L$); largest transverse velocity"),
        ("card_h", "card-hours of the relativistic runs: one per cell; two per cell; total"),
    ]),
    ("Homogeneous background", [
        ("flrw", "largest relative lapse error, $a=4$ and $a=36$ (step limited); $\\mathcal H$ at $a=36$"),
    ]),
    ("Semi-analytic Newtonian baseline", [
        ("za_slopes", "largest departure of the local slopes from $7/2$, $3/2$, $7/2$ for $\\delta_L\\le10^{-2}$: energy, peak frequency, peak"),
        ("self_sim", "self-similarity: relative spread of the energy coefficient over the amplitude"),
        ("crossings_B", "literal model B: first crossings along $x$, $y$ ($t/t_k$); relative difference from Ref.~\\cite{Escriva:2026gw}"),
        ("redshift", "coefficient of the turnaround-to-reheating time ratio (21.03 in Ref.~\\cite{Escriva:2026gw})"),
        ("omega_factor", "ratio of our $\\Omega_{\\rm GW}$ to the prefactor of Ref.~\\cite{Dalianis:2024gw} (range over four parameters)"),
        ("lead_e", "independent quadrature of the ellipsoid energy against the closed form"),
        ("lead_f", "second-order lapse of a closed box with a TT wave, $t=10$, $A=10^{-6}$: conformal time; 1+log"),
    ]),
]

LEDGER_G1 = [
    ("Crossed waves in full relativity ($\\delta=0.01$, box of four initial Hubble radii, $64^3$ unless stated)", [
        ("fs_ic", "initial data: largest Hamiltonian and momentum residuals of the four cases; particles per run"),
        ("fs_s", "static amplitude $s$ at $\\epsilon=1$; Zel'dovich first crossing $1+1/\\delta$"),
        ("fs_dev64", "largest $|c_+/(s\\epsilon g)-1|$, $2\\le a\\le10$: $\\epsilon=0.1,0.3,1$"),
        ("fs_dev64K2", "the same at $(k,-k,0)$ with the opposite sign"),
        ("fs_dev32", "the same at $(k,k,0)$, $32^3$"),
        ("fs_dev_a20", "departure from second order at $a=20$: $\\epsilon=0.1,0.3,1$"),
        ("fs_dev_a40", "the same at $a=40$"),
        ("fs_dev_a60", "the same at $a=60$"),
        ("fs_slope", "logarithmic slope of the departure between $a=10$ and $a=60$"),
        ("fs_scaled", "departure over $1+\\epsilon^2$, relative to that of $\\epsilon=0.1$: $\\epsilon=0.3,1$ at $a=20$; at $40$; at $60$"),
        ("fs_lin", "linearity, $2\\le a\\le10$: largest relative difference of $c_+/\\epsilon$, $0.3$ and $1$ against $0.1$"),
        ("fs_lin_late", "the same at $a=20$ ($0.3$; $1$) and $a=60$ ($0.3$; $1$)"),
        ("fs_max", "largest $c_+/s$ at $\\epsilon=1$ and its $a$; $c_+/(s\\epsilon)$ at the end, $\\epsilon=0.1,0.3$"),
        ("fs_null", "null $\\epsilon=0$, all dumps to $a=140$: largest TT amplitude of $h$ (single, double precision), of $\\tilde A$ (double); largest $z$ dependence"),
        ("fs_res", "$32^3$ against $64^3$: largest $|c_+$ ratio$-1|$, $5\\le a\\le40$: $\\epsilon=0.1,0.3,1$, driven shift"),
        ("fs_res_late", "the same, largest over the four cases for $40<a\\le80$; at $a=100$"),
        ("fs_box", "share of the four box modes in the mean square TT strain: $a=10$ ($\\epsilon=0.1,1$), $a=20$ ($0.1,1$)"),
        ("fs_kin", "largest kinetic over gradient energy of the TT part for $a\\ge12$: $\\epsilon=0.1,1$"),
        ("fs_card", "card-hours of the scan: three cases; two gauges; total"),
    ]),
    ("Spatial gauge of the projection ($\\epsilon=1$, two gauges, $64^3$ unless stated)", [
        ("g_t0", "exact pure-gauge data: slope of $\\Lambda h$ and of $\\Lambda h-G$ in the gauge amplitude; with a slicing change, $\\Lambda h-G$"),
        ("g_size", "largest $|G_{\\rm tot}/c_+|$ for $a\\le20$, zero shift: $\\epsilon=0.1,0.3,1$"),
        ("g_size40", "the same at $a=40$"),
        ("g_raw", "gauge difference of $c_+$ over $|s|$, as projected, $a=5,10,20,40,60$"),
        ("g_cor", "the same after $G_{\\rm tot}$ in each gauge"),
        ("g_median", "median of corrected over projected difference where the latter exceeds $10^{-3}|s|$: $64^3$, $32^3$; share of such dumps"),
        ("g_quad", "the same median with the quadratic piece alone: $64^3$, $32^3$"),
        ("g_dev", "departure from $sg$ at $a=10$: as projected, corrected; at $a=20$: as projected, corrected"),
        ("g_nonTT", "rms non-TT part, zero shift over driven shift, $a\\ge10$: smallest, largest ratio"),
        ("g_weyl", "median relative gauge difference for $a\\le64$: magnetic Weyl part; flat TT strain"),
        ("g_slicing", "first-order slicing of the earlier three-wave runs, $1<a\\le121$: largest correlation of $\\delta\\ln\\alpha$ with $\\delta\\ln\\gamma^{1/6}$; rms of $\\delta\\ln(\\alpha\\gamma^{1/6})$ over that of $\\delta\\ln\\alpha$, smallest and largest"),
    ]),
    ("Newtonian mode of the code", [
        ("n_force", "force excess $[(k\\Delta x/2)/\\sin(k\\Delta x/2)]^2-1$ on the box mode, $N=16,32,64$"),
        ("n_h1", "measured over predicted sheet error at $a=2,5$: $N=16$; $32$; $64$"),
        ("n_err", "sheet error over displacement at $a=2$ ($N=32,64$), $a=5$ ($32,64$); ratios $32/64$ at $a=2,5$"),
        ("n_pm", "spectral particle mesh, the same: $a=2,5$ at $N=32$; at $N=64$"),
        ("n_late", "measured over predicted at $a=10,15$, $N=32$"),
        ("n_cross", "first sheet crossing (scale factor): $N=16,32,64$; particle mesh $N=32,64$"),
        ("n_sym", "largest spread of $x$ over a lattice plane ($L$)"),
        ("n_d3I", "rms relative error of the third derivative of $I_{xx}$, $1.2\\le a\\le15$: $N=16,32,64$"),
        ("n_LI", "Layzer--Irvine constant over largest $a|W|$: $N=16,32,64$"),
        ("e_tx", "ellipsoid: first crossing time ($t_k$), $N=32,64,128$; ODE; extrapolation and its order"),
        ("e_E", "energy to the first crossing against the ODE, $N=32,64,128$; extrapolation; order"),
        ("e_EM", "ODE energy to the first crossing over $Mc^2$"),
        ("e_early", "energy until one time unit before the crossing against the ODE (both averaged), $N=32,64,128$"),
        ("e_step", "relative change of the crossing time when the step is halved, $N=64$"),
        ("e_self", "energy over $Mc^2(2\\alpha_{\\rm e})^{7/2}$, $N=32,64$; largest spread over four $\\alpha_{\\rm e}$; ODE value"),
        ("n_card", "card-hours of the $N=64$ pancakes"),
    ]),
    ("Second readings of the wave-2 runs (own reader and reference)", [
        ("rv_dev", "largest departure from second order, $2\\le a\\le10$, $\\epsilon=0.1,0.3,1$"),
        ("rv_tx", "ellipsoid first crossing time from the history files, $N=32,64,128$; extrapolation"),
        ("rv_self", "largest relative spread of the self-similar energy over $\\alpha_{\\rm e}$"),
    ]),
]


def ledger_tex(v):
    lines = ["% generated by scripts/ledger.py from registered run outputs; do not edit"]
    parts = [(LEDGER[:3], "Numerical ledger. Every number behind this note with the registered run that produced it.", "tab:ledger"),
             (LEDGER[3:], "Numerical ledger (continued).", "tab:ledger2"),
             (LEDGER_G1[:1], "Numerical ledger: the crossed waves in full relativity.", "tab:ledger3"),
             (LEDGER_G1[1:], "Numerical ledger: the spatial gauge and the Newtonian mode.", "tab:ledger4")]
    for groups, caption, label in parts:
        lines += ["\\begin{table*}", "\\footnotesize", f"\\caption{{{caption}}}", f"\\label{{{label}}}",
                  "\\begin{ruledtabular}",
                  "\\begin{tabular}{p{0.47\\textwidth}p{0.24\\textwidth}l}",
                  "Quantity & Value & Run \\\\", "\\hline"]
        for head, rows in groups:
            lines.append(f"\\multicolumn{{3}}{{l}}{{\\emph{{{head}}}}} \\\\")
            for key, desc in rows:
                vals, rk = v[key]
                if not isinstance(vals, list):
                    vals = [vals]
                sv = ", ".join(fmt(x) if not isinstance(x, str) else f"\\texttt{{\\scriptsize {x}}}"
                               for x in vals)
                lines.append(f"{desc} & {sv} & \\texttt{{\\scriptsize {R[rk]}}} \\\\")
        lines += ["\\end{tabular}", "\\end{ruledtabular}", "\\end{table*}"]
    return "\n".join(lines) + "\n"


# scenario parameters: values from the run analysis files where they are recorded there,
# the rest from the inputs named in the comment (verify_cosmo/scripts/build_ic.sh line 10,
# verify_cosmo/inputs/pancake.athinput lines 41-51, periodic_z4c/README.md lines 49-51,
# first_source/JOURNAL.md set-up, scope/SCOPE.md section 3)
def parameters_tex(d):
    pc = d["pc"]
    e = d["nwe"]
    a_end = max(pc[k]["a_end"] for k in ("L1_n32", "L1_n64", "L1_n96", "L4_n64"))
    amp = d["ak"]["deck"]["amp"]
    rows = [
        ("Linear wave, vacuum box", "box side $L$", "one wavelength"),
        ("", "amplitude $A$", fmt(amp)),
        ("", "cells per wavelength $N$", "16, 32, 64, 128"),
        ("", "duration", "ten crossings (two for the dumps)"),
        ("", "slicing; shift", "conformal time; zero"),
        ("Plane-wave pancake", "amplitude $\\delta$ at $a=1$", "0.05"),
        ("", "box side (initial Hubble radii)", "1 and 4"),
        ("", "cells per side", "32, 64, 96 (box 1); 64 (box 4)"),
        ("", "particles per cell", "1; 8 (two per direction, 64 cells)"),
        ("", "end", f"$a={a_end:.0f}$, twice the first crossing"),
        ("", "slicing; shift", "conformal time; zero"),
        ("First source (crossed waves)", "amplitude $\\delta$; ratios", "0.01; $(1,\\epsilon,0)$"),
        ("", "$\\epsilon$", "0, 0.1, 0.3, 1"),
        ("", "box side (initial Hubble radii)", "4"),
        ("", "cells per side; particles per cell", "64 and 32; 8"),
        ("", "end; dump interval in conformal time", "$a=140$; 0.1"),
        ("", "slicing; shift", "conformal time; zero (also driven, $\\epsilon=1$)"),
        ("Newtonian pancake", "amplitude $\\delta$ at $a=1$; box side", "0.05; one length unit"),
        ("", "cells per side; particles per cell", "16, 32, 64; 1"),
        ("Newtonian ellipsoid", "model", "C of Ref.~\\cite{Escriva:2026gw}, from turnaround"),
        ("", "turnaround time; deformation $\\alpha_{\\rm e}$", f"{e['N1_N64']['t_turn']:.2f}\\,$t_k$; {e['N1_N64']['alpha']:.3f}"),
        ("", "cells per side; particles per cell", "32, 64, 128; 8"),
        ("", "rescaled copies $\\alpha_{\\rm e}$", "0.05, 0.1, 0.2"),
    ]
    lines = ["% generated by scripts/ledger.py; do not edit",
             "\\begin{table*}",
             "\\caption{Parameters of the scenarios.}",
             "\\label{tab:parameters}",
             "\\begin{ruledtabular}",
             "\\begin{tabular}{lll}",
             "Scenario & Parameter & Value \\\\", "\\hline"]
    for a, b, c in rows:
        lines.append(f"{a} & {b} & {c} \\\\")
    lines += ["\\end{tabular}", "\\end{ruledtabular}", "\\end{table*}"]
    return "\n".join(lines) + "\n"


# claims of the lead's documents: (document, phrase found on one line, stated values,
# actual values, relative tolerance implied by the stated digits, note)
def claims(v):
    def c(doc, phrase, stated, actual, rtol, note=""):
        return dict(doc=doc, phrase=phrase, stated=stated, actual=actual, rtol=rtol, note=note)
    rep, g1, st = "stage/G0/REPORT.md", "stage/G1/STATUS.md", "STATUS.md"
    sd = v["symbol_dev"][0]
    return [
        c(rep, "virial frequency 0.81-3.57", [0.81, 3.57], v["vir_range"][0], 0.01),
        c(rep, "pancake void H_r 1.3e-3 and M_r 0.21 at a = 15",
          [1.3e-3, 0.21], [v["Hr"][0][1], v["Mr"][0][0]], 0.05,
          "the values are box means (`Hr_mean`, `Mr_mean`); the dumps place most of the violation in the void"),
        c(rep, "two per direction about 30 times", [30, 30], v["Hr_ratio"][0], 0.15),
        c(rep, "0.018 card-h at 64^3", [0.018, 0.36, 5.8, 0.36], v["cost_d01"][0], 0.05),
        c(rep, "(a = 560): 0.037, 0.76, 12.1, 0.76", [0.037, 0.76, 12.1, 0.76], v["cost_d0025"][0], 0.05),
        c(rep, "Used this wave: 0.48 card-h", [0.48], [v["card_h"][0][2]], 0.01),
        c(rep, "lapse = scale factor to 1e-7 at a = 4 and 36", [1e-7, 1e-7], v["flrw"][0][:2], 0.5,
          "order of magnitude only: the value at a = 4 is 1.9e-7"),
        c(rep, "amplitude 3e-7, phase 1.2e-6 rad at 32^3", [3e-7, 1.2e-6], v["ak_t2"][0][:2], 0.05),
        c(rep, "plane symmetry to 1e-12", [1e-12], [v["symmetry"][0][1]], 0.5,
          "largest transverse velocity 1.3e-12 (96 cells, a = 26.3); positions to 4.5e-14 L"),
        c(rep, "1.8 % of the static value at a = 60", [0.018], [v["junk"][0][1]], 0.03),
        c(g1, "48 random waves to 2.6e-12", [48, 2.6e-12], v["tt_analytic"][0], 0.02),
        c(g1, "amplitude within 3e-7, phase within 1.2e-6 rad, rho", [3e-7, 1.2e-6, 6e-7],
          v["ak_t2"][0][:3], 0.05),
        c(g1, "matching the Fourier symbol of the scheme to 1 % up to 64 cells", [0.01],
          [max(sd)], 0.0,
          "the production phase error at 64 cells departs by 9.5 % (periodic_z4c/README.md says "
          "\"10 percent for the production phase at 64\"); the other errors to 1 %"),
        c(g1, "within 0.034", [0.034], [v["za_slopes"][0][0]], 0.02),
        c(g1, "to\n  3e-13", [3e-13], v["self_sim"][0], 0.2),
        c(g1, "(22.536, 29.097)", [0.010, 0.0009], v["crossings_B"][0][2:], 0.1),
        c(g1, "21.027 against 21.03", [21.027], v["redshift"][0], 1e-4),
        c(g1, "1e-3 in position to a = 15 at 64 cells", [1e-3], [v["newton"][0][0]], 0.05),
        c(g1, "4.1e-4 at 32 cells", [4.1e-4], [v["newton"][0][2]], 0.02),
        c(g1, "lapse = scale factor to 1.9e-7", [1.9e-7, 7.0e-8], v["flrw"][0][:2], 0.02),
        c(g1, "0.48 card-hours", [0.48], [v["card_h"][0][2]], 0.01),
        c(g1, "missed by a factor 144-392", [144, 392], v["omega_factor"][0], 0.01),
        c(st, "budget:      0.48 GPU-hours", [0.48], [v["card_h"][0][2]], 0.01),
        c("stage/G0/REVIEW.md", "-1.64e-10 (conformal time) and -9.87e-10", [-1.64e-10, -9.87e-10],
          v["lead_f"][0], 0.005),
        c("stage/G0/REVIEW.md", "Fourier coefficient\n  (5/12)|phi_x phi_y| = 1.3858e-5", [1.3858e-5],
          v["cw_three"][0], 1e-4),
        c("tracks/B-emd-gw/verify_cosmo/JOURNAL.md", "16.1 times the L = 1 value", [16.1],
          [v["grdiff10"][0][4]], 0.005),
    ]


# committed copies of the run outputs in the helper packages (paths under tracks/B-emd-gw/)
COMMITTED = {
    "crossed_waves_tt.json": "scope/results/crossed_waves_tt.json",
    "regime_estimates.json": "scope/results/regime_estimates.json",
    "check_item3.json": "scope/results/check_item3.json",
    "flrw_recheck.json": "verify_cosmo/results/flrw_recheck.json",
    "pancake.json": "verify_cosmo/results/pancake.json",
    "baseline_results.json": "baseline/results/baseline_results.json",
    "lw_x.json": "periodic_z4c/tables/lw_x.json",
    "lw3d_check.json": "periodic_z4c/tables/lw3d_check.json",
    "awa.json": "periodic_z4c/tables/awa.json",
}


# committed copies of the wave-2 run outputs, by run (the same file name occurs in several runs)
COMMITTED_BY_RUN = {
    common.RUNS["nw_pancake"]: {"pancake.json": "newton_tests/results/pancake.json"},
    common.RUNS["nw_ellipsoid"]: {"ellipsoid.json": "newton_tests/results/ellipsoid.json"},
    common.RUNS["t0_gauge"]: {"t0_gauge.json": "first_source/results/t0_gauge.json"},
    common.RUNS["slicing"]: {"slicing_check.json": "first_source/results/slicing_check.json"},
    common.RUNS["review_nw"]: {"rv_newton.json": "stage/review_wave2/results/rv_newton.json"},
}


def committed_copy(run_id, rel):
    base = os.path.basename(rel)
    if run_id in COMMITTED_BY_RUN:
        return COMMITTED_BY_RUN[run_id].get(base)
    if run_id.startswith("B-emd-gw-"):          # wave-1 runs: names are unique among them
        return COMMITTED.get(base)
    return None


def locate(doc, phrase):
    """Line of `phrase` in `doc` as the document stood at common.CLAIMS_REV (the revision
    the note v0 checked; the lead's stage documents were rewritten after that check)."""
    rel = doc if doc.startswith("tracks/") else "tracks/B-emd-gw/" + doc
    text = subprocess.run(["git", "-C", common.WT, "show", f"{common.CLAIMS_REV}:{rel}"],
                          capture_output=True, text=True, check=True).stdout
    flat = re.sub(r"\s+", " ", text)
    ph = re.sub(r"\s+", " ", phrase)
    i = flat.find(ph)
    if i < 0:
        return None
    # map the flat index back to a line by counting words
    words_before = len(flat[:i].split(" "))
    count = 0
    for n, line in enumerate(text.splitlines(), 1):
        count += len(line.split())
        if count >= words_before:
            return n
    return None


def check_claims(v):
    res = []
    for cl in claims(v):
        line = locate(cl["doc"], cl["phrase"])
        st, ac = cl["stated"], [float(x) for x in cl["actual"]]
        ok = line is not None and all(
            (abs(a - s) <= cl["rtol"]*abs(s)) if cl["rtol"] > 0 else (abs(a) <= abs(s))
            for s, a in zip(st, ac))
        res.append(dict(cl, line=line, agree=bool(ok),
                        actual=[float(f"{a:.4g}") for a in ac]))
    # a number of the cosmology extension's own record (a committed file, not a run of this track)
    dav = json.load(open(os.path.join(common.WT, "cosmo", "analysis", "daverio_a.json")))
    hr100 = [dav[f"a0_n{n}"]["Hr"]["100"] for n in (8, 16, 32)]
    hr3000 = [dav[f"a0_n{n}"]["Hr"]["3000"] for n in (8, 16, 32)]
    ok = all(abs(a - b) <= 0.05*abs(b) for a, b in zip(hr100, [1.6e-9, 1.1e-10, 3.2e-11]))
    res.append(dict(doc="stage/G1/STATUS.md", phrase="constraint 1.6e-9, 1.1e-10, 3.2e-11 at 8, 16, 32 cells over a thousandfold expansion",
                    stated=[1.6e-9, 1.1e-10, 3.2e-11], actual=[float(f"{x:.3g}") for x in hr100 + hr3000], rtol=0.05,
                    line=locate("stage/G1/STATUS.md", "constraint 1.6e-9, 1.1e-10, 3.2e-11"), agree=False,
                    note=("values at t = 100 Mpc/h, early in the run (agree there: %s); at the end of the thousandfold "
                          "expansion (t = 3000 Mpc/h) the relative Hamiltonian constraint is 3.1e-8, 2.5e-9, 3.0e-9 and "
                          "does not fall from 16 to 32 cells; the fourth-order convergence holds for the error of chi "
                          "(cosmo/analysis/daverio_a.json, committed file of the cosmology extension)" % ("yes" if ok else "no"))))
    # a statement of state, not a number: the Newtonian mode and its quadrupole history
    on_main = subprocess.run(["git", "-C", common.WT, "cat-file", "-e",
                              "main:coord/INTERFACES/newtonian_mode.md"]).returncode == 0
    line = locate("stage/G1/STATUS.md", "exist on `core/newton` (tip")
    res.append(dict(doc="stage/G1/STATUS.md", phrase="exist on `core/newton` (tip ce329f5, not on main)",
                    stated="not on main", actual="on main (release core-v0.3)" if on_main else "not on main",
                    rtol=None, line=line, agree=not on_main,
                    note="written before wave 1 was merged; the mode, its interface document "
                         "coord/INTERFACES/newtonian_mode.md and the quadrupole history are on main now"))
    return res


def main():
    out = common.out_dir("tables")
    d = load()
    v = values(d)
    with open(os.path.join(out, "ledger.tex"), "w") as f:
        f.write(ledger_tex(v))
    with open(os.path.join(out, "parameters.tex"), "w") as f:
        f.write(parameters_tex(d))
    res = check_claims(v)
    with open(os.path.join(out, "claims.json"), "w") as f:
        json.dump(res, f, indent=1)
    n_ok = sum(r["agree"] for r in res)
    md = ["# Numbers of the lead's documents checked against the run outputs",
          "", "Written by `note/scripts/ledger.py`. Paths relative to `tracks/B-emd-gw/`. "
          "Where the document and the file disagree, the file wins.", "",
          f"{n_ok} of {len(res)} agree at the precision stated.", "",
          "| Document:line | Stated | From the files | Agree | Note |", "|---|---|---|---|---|"]
    for r in res:
        md.append(f"| {r['doc']}:{r['line']} | {r['stated']} | {r['actual']} | "
                  f"{'yes' if r['agree'] else 'NO'} | {r.get('note', '')} |")
    with open(os.path.join(out, "claims.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    n_bad = len(res) - n_ok
    with open(os.path.join(out, "claims_summary.tex"), "w") as f:
        f.write(f"Of the {len(res)} numbers and statements of the track's stage documents of the first "
                f"stage check that were checked against these files, {n_ok} agree at the precision "
                f"stated and {n_bad} differ%\n")
    chk = ["# Files read by the note scripts", "",
           "Committed copy: the file of the helper package that the run output should equal byte for byte.", "",
           "| Run | File | Checksum | Committed copy | Identical |", "|---|---|---|---|---|"]
    n_same = n_cmp = 0
    for run_id, rel, how in sorted(set(common.CHECKED)):
        copy = committed_copy(run_id, rel)
        same = "-"
        if copy:
            a = open(os.path.join(common.SCRATCH, run_id, rel), "rb").read()
            b = open(os.path.join(common.TRACK, copy), "rb").read()
            same = "yes" if a == b else "NO"
            n_cmp += 1
            n_same += a == b
        chk.append(f"| {run_id} | {rel} | {how} | {copy or '-'} | {same} |")
    print(f"committed copies identical: {n_same} of {n_cmp}")
    with open(os.path.join(out, "checked.md"), "w") as f:
        f.write("\n".join(chk) + "\n")
    print(f"claims: {n_ok} of {len(res)} agree")
    for r in res:
        if not r["agree"]:
            print("  differs:", r["doc"], r["line"], r["stated"], r["actual"], r.get("note", ""))


if __name__ == "__main__":
    main()
