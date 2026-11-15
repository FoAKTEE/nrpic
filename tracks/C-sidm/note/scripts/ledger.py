"""Numerical ledger, parameter table and claims check of the note (C-sidm, note v0).

Writes, into ../tables (or --out DIR):
  ledger.tex          every number of the note with the registered run that produced it
  parameters.tex      the parameters of the equilibrium models the note uses
  claims.md, .json    numbers stated in the lead's documents (stage/G0/REPORT.md,
                      stage/G1/STATUS.md, STATUS.md) checked against the run outputs;
                      where they differ, the files win and the difference is listed
  claims_summary.tex  one sentence for the note: how many claims, how many differ
Every input is read through common.run_file (sha256 checked where the run recorded one).
"""
import csv
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402

R = cm.RUNS
ROWS = []      # (section, quantity, value, run key)
CLAIMS = []    # dict(doc, claim, file_value, agrees, note, run)


def add(section, quantity, value, key):
    ROWS.append((section, quantity, value, key))


def claim(doc, text, file_value, agrees, key, note=""):
    CLAIMS.append(dict(doc=doc, claim=text, file_value=file_value, agrees=bool(agrees),
                       run=R[key] if key in R else key, note=note))


def g(x, n=4):
    return f"{x:.{n}g}"


def e(x, n=2):
    m, ex = f"{x:.{n}e}".split("e")
    return f"${m}\\times10^{{{int(ex)}}}$"


def main():
    out = cm.out_dir("tables")
    # ---------------- spherical baseline ----------------
    crit = cm.load_json("thermal", "criteria.json")
    rows1 = list(csv.DictReader(open(cm.run_file("thermal", "table1_compare.csv"))))
    rows2 = list(csv.DictReader(open(cm.run_file("thermal", "table2_compare.csv"))))
    cols = ["E", "Erest", "B", "eps", "Z0", "ec0", "rho0", "p0", "v0", "gavg", "gcr"]
    typos, worst = [], {}
    for r in rows1:
        for c in cols + ["C"]:
            v = abs(float(r[f"{c}_rel"]))
            if v > 0.1:
                typos.append((r["line"], c))
                continue
            if c != "C" and v > worst.get(c, (0, ""))[0]:
                worst[c] = (v, r["line"])
    wmax = max(worst.values())
    cmax = max(worst, key=lambda c: worst[c][0])
    rmax = max(abs(float(r["R_rel"])) for r in rows1)
    w2 = max(abs(float(r["w0_rel"])) for r in rows2)
    add("baseline", "rows of the two printed tables of Ref.~\\cite{Feng:2021instab} compared",
        f"{len(rows1)}; {len(rows2)}", "thermal")
    add("baseline", "largest relative difference, columns other than the radius (column, line)",
        f"{e(wmax[0])} ({cmax}, {wmax[1]})", "thermal")
    add("baseline", "largest relative difference of the radius (printed to three digits)",
        e(rmax), "thermal")
    add("baseline", "printed values off by more than ten percent (line, column)",
        ", ".join(f"{l} {c}" for l, c in typos), "thermal")
    add("baseline", "largest relative difference of the root $w_0$ of the second table", e(w2), "thermal")
    c1 = crit["0.1"]
    add("baseline", "$b=0.1$: binding-energy maximum, $w_0$; $Z(0)$; $\\epsilon$; $v(0)$",
        f"{g(c1['max_eps']['w0'], 6)}; {g(c1['max_eps']['Z0'], 5)}; "
        f"{g(c1['max_eps']['eps'], 5)}; {g(c1['max_eps']['v0'], 4)}", "thermal")
    on = c1["omega2_zero_F21gamma"]
    add("baseline", "$b=0.1$: pulsation onset, $\\Gamma=1+p/u$, $w_0$; $Z(0)$; $\\epsilon$; $v(0)$",
        f"{g(on['w0'], 6)}; {g(on['Z0'], 5)}; {g(on['eps'], 5)}; {g(on['v0'], 4)}", "thermal")
    add("baseline", "$b=0.1$: pulsation onset with $\\Gamma=5/3$, $Z(0)$; trial criterion $w_0$, $Z(0)$",
        f"{g(c1['omega2_zero_gamma53']['Z0'], 5)}; {g(c1['gavg_eq_gcr']['w0'], 6)}, "
        f"{g(c1['gavg_eq_gcr']['Z0'], 5)}", "thermal")
    add("baseline", "$b=0.2, 0.3, 0.5$: $Z(0)$ of the binding-energy maximum; of the onset ($1+p/u$)",
        ", ".join(g(crit[b]["max_eps"]["Z0"], 4) for b in ("0.2", "0.3", "0.5")) + "; " +
        ", ".join(g(crit[b]["omega2_zero_F21gamma"]["Z0"], 4) for b in ("0.2", "0.3", "0.5")), "thermal")
    poly = cm.load_json("poly", "polytrope_check.json")
    add("baseline", "pulsation zero against the mass maximum, $\\Gamma=2$ polytropes, three resolutions",
        ", ".join(e(abs(v), 1) for v in poly["rel_diff"].values()), "poly")
    x = cm.load_json("xchk", "crosscheck.json")
    gr = x["X2"]["grid"]["0.1"]
    d_eps, d_z = gr["max_rel_eps"], gr["max_abs_Z0"]
    add("baseline", "two independent thermal-core solvers, $b=0.1$ grid: largest relative "
        "difference in $\\epsilon$; absolute in $Z(0)$", f"{e(d_eps, 1)}; {e(d_z, 1)}", "xchk")
    x5 = [r for r in x["X5"]["rows"] if abs(r["w0"] - 3.5871) < 1e-6]
    add("baseline", "lowest $\\omega_0^2$ at the onset, two resolutions",
        ", ".join(e(r["omega2"], 1) for r in x5), "xchk")
    king = cm.load_json("king", "king_sequence.json")
    km = king["maxima"]["1.0"]
    add("baseline", "King: binding-energy maximum $y_0$; $z_c$; fraction; first zero $y_0$ "
        "(printed 0.334, 0.784, Ref.~\\cite{Gunther:2020ev})",
        f"{g(km['y0'], 6)}; {g(km['Z0'], 5)}; {g(km['eps_b'], 5)}; {g(king['zero_b1']['y0'], 5)}",
        "king")
    x3 = x["X3"]["rows"]
    d3 = max(abs(r["eps_scope"] - r["eps_ev"]) / r["eps_ev"] for r in x3)
    d3z = max(abs(r["Z_scope"] - r["Z_ev"]) for r in x3)
    add("baseline", "King: two solvers, largest relative difference of the fraction; of $z_c$",
        f"{e(d3, 1)}; {e(d3z, 1)}", "xchk")
    mono = cm.load_json("mono", "seq_monoenergetic.json")
    mm = mono["binding_energy_maximum"]
    add("baseline", "monoenergetic: maximum $y_c$; $z_c$; fraction; $R/M$",
        f"{g(mm['yc'], 6)}; {g(mm['zc'], 5)}; {g(mm['Eb_over_M0'], 5)}; {g(mm['R_over_M'], 4)}",
        "mono")
    wm = [m for m in mono["models"] if m.get("zc_WM") is not None]
    dz = max(abs(m["zc"] - m["zc_WM"]) for m in wm)
    dr = max(abs(m["R_over_M"] - m["R_over_M_WM"]) / m["R_over_M_WM"] for m in wm)
    add("baseline", f"monoenergetic: {len(wm)} models of Ref.~\\cite{{Wu:2026nrpic}}, largest "
        "difference of $z_c$; relative of $R/M$", f"{e(dz, 1)}; {e(dr, 1)}", "mono")
    init = cm.load_json("init", "initial_models.json")["0.1"]
    sel = [m for m in init if 0.395 <= m["Z0"] <= 0.805]
    RR = [m["R_over_M"] for m in sel]
    rc = [m["rcore_over_M"] for m in sel]
    ac = [m["alpha_c"] for m in sel]
    add("baseline", "thermal-core models $Z(0)=0.40$--$0.80$: $R/M$; $r_{\\rm core}/M$; central lapse",
        f"{min(RR):.1f}--{max(RR):.1f}; {min(rc):.2f}--{max(rc):.2f}; {min(ac):.3f}--{max(ac):.3f}",
        "init")
    # ---------------- particle models, Knudsen number ----------------
    idx = cm.load_json("models", "index.json")
    chk = cm.load_json("eqchk", "checks.json")

    def count(o):
        n = p = 0
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "pass" and isinstance(v, bool):
                    n += 1
                    p += v
                else:
                    a, b = count(v)
                    n, p = n + a, p + b
        elif isinstance(o, list):
            for v in o:
                a, b = count(v)
                n, p = n + a, p + b
        return n, p
    nflag, npass = count(chk)
    add("models", "particle models; particles each; offline checks passed of total",
        f"{len(idx['models'])}; {idx['N']}; {npass} of {nflag}", "eqchk")
    x4 = x["X4"]
    Ks = [m["Kn_sigma_lead"] for m in x4["models"]]
    add("models", "$K=\\tilde\\sigma\\,{\\rm Kn}_c$: King threshold model; range over the 13 models",
        f"{g(x4['Kn_sigma_lead_scope_solver'], 6)}; {min(Ks):.1f}--{max(Ks):.1f}", "xchk")
    add("models", "$K$ with the energy density in $H$; ratio of the transport mean free path to $\\lambda$",
        f"{g(x4['Kn_sigma_scope_def'], 5)}; "
        f"{min(m['l_over_lambda'] for m in x4['models']):.3f}--"
        f"{max(m['l_over_lambda'] for m in x4['models']):.3f}", "xchk")
    cM = x4["cgs_per_code_at_1Msun"]
    add("models", "$\\sigma/m$ in cm$^2$/g for $\\tilde\\sigma=1$ and $M=M_\\odot$", e(cM, 4), "xchk")
    kn200 = (min(Ks) * cM * 200 / 5, max(Ks) * cM * 200 / 5)
    kn19 = (min(Ks) * cM * 1.9e9 / 5, max(Ks) * cM * 1.9e9 / 5)
    add("models", "${\\rm Kn}_c$ at $\\sigma/m=5\\,$cm$^2$/g, $M=200\\,M_\\odot$; $1.9\\times10^9\\,M_\\odot$ "
        "(13 models)", f"{e(kn200[0], 1)}--{e(kn200[1], 1)}; {e(kn19[0], 1)}--{e(kn19[1], 1)}", "xchk")
    kc = cm.load_json("kncost", "knudsen_costs.json")

    def phys(Ms):
        v = [p["Kn_c"] for p in kc["physical"] if p.get("M_msun") == Ms
             and p.get("sigma_over_m_cgs") == 5.0]
        return min(v), max(v)
    p200, p19 = phys(200.0), phys(1.9e9)
    add("models", "the same with the energy density in $H$, six candidate models",
        f"{e(p200[0], 1)}--{e(p200[1], 1)}; {e(p19[0], 1)}--{e(p19[1], 1)}", "kncost")
    kq = cm.load_json("kneq", "knudsen.json")
    kt = [m for m in kq["models"] if m["tag"] == "king_y0p33403"][0]
    add("models", "King threshold model: $H_c/M$; central particle spacing at $10^4$ particles",
        f"{g(kt['H_c'], 5)}; {g(kt['rows'][0]['d_c'], 3)}", "kneq")
    sm = cm.load_json("smoke", "smoke.json")["checks"]
    add("models", "code reads the King threshold files: particles; rest mass against the model; "
        "Hamiltonian; momentum constraint norm over the reference",
        f"{int(sm['new_np'])}; {e(abs(sm['new_sum_m_rel']), 1)}; "
        f"{sm['H_norm2_ratio_new_over_ref']:.3f}; {sm['M_norm2_new'] / sm['M_norm2_ref']:.3f}",
        "smoke")
    # ---------------- collisions ----------------
    x1 = x["X1"]["rows"]
    rq = [abs(r["rel_quad"]) for r in x1]
    add("collisions", "closed-form mean M\\o ller speed against quadrature: largest relative "
        "difference ($\\theta$); at $\\theta=100$",
        f"{e(max(rq))} ({x1[int(np.argmax(rq))]['theta']:g}); {e(rq[-1], 1)}", "xchk")
    ref = cm.load_json("collref", "ref_numbers.json")
    rd = list(ref["rate_mc_dev_sigma"].values())
    add("collisions", f"Monte Carlo pair average of the rate, {len(rd)} temperatures, "
        "deviation in standard errors", f"{min(rd):+.2f} to {max(rd):+.2f}", "collref")
    rel = ref["relax_mc_over_quad"]
    add("collisions", "two-temperature relaxation rate, Monte Carlo over quadrature at "
        "$\\theta=10^{-3}, 0.1, 1, 10$",
        ", ".join(f"{r[1]:.4f}$\\pm${r[2]:.4f}" for r in rel), "collref")
    rr = ref["relax_rate_ratio_rel_over_nr"]
    add("collisions", "relaxation rate over its non-relativistic form at $\\theta="
        + ", ".join(g(t, 3) for t in rr["theta"]) + "$",
        ", ".join(g(v, 4) for v in rr["ratio"]), "collref")
    add("collisions", "pair kinematics: largest error against the 60-digit oracle; momentum; "
        "energy residual (units of $\\varepsilon$)",
        f"{e(ref['kin_err_max'], 1)}; {ref['kin_resP_max_over_eps']:.2f}; "
        f"{ref['kin_resE_max_over_eps']:.2f}", "collref")
    add("collisions", "conductivity coefficient $\\kappa_1\\sigma/\\sqrt\\theta$; ratio to the "
        "constant of Ref.~\\cite{Balberg:2002gt}", f"{ref['kappa1_coefficient']:.4f}; "
        f"{ref['kappa_ratio_KS_over_BSI']:.3f}", "collref")
    add("collisions", "entropy gap per particle at $\\theta_2=10^{-3}$; $\\theta_2=1$",
        f"{ref['entropy_gap_theta2_1e-3']:.4f}; {ref['entropy_gap_theta2_1']:.4f}", "collref")
    t0 = cm.load_json("t0", "t0.json")
    fe = max(f["max_err_u"] for f in t0["flags"].values())
    fc = max(f["max_cons_eps"] for f in t0["flags"].values())
    add("collisions", "kernel test on the code: cases (skipped); largest velocity error; "
        "four-momentum residual ($\\varepsilon$); failures",
        f"{t0['n_cases']} ({t0['n_skipped']}); {e(fe)}; {fc:.2f}; "
        f"{sum(f['n_fail'] for f in t0['flags'].values())}", "t0")
    # ---------------- AthenaK box ----------------
    st = cm.load_json("t60", "step_step.json")
    meta = cm.load_json("t60", "step.json")
    add("box", "free streaming in the box: particles; $\\theta_1$; $\\theta_2$ (measured); snapshots",
        f"{meta['n']}; {st['theta1']:.5f}; {st['theta2']:.5f}; {len(st['times'])}", "t60")
    add("box", "largest position error over the box length; code against free streaming of "
        "the sample (relative)",
        f"{e(st['max_position_error_over_L'])}; {st['max_rel_dev_code_vs_free_sample']:g}", "t60")
    add("box", "deviation from the ensemble in noise units, largest; rms (rest mass, energy, "
        "kinetic energy)",
        ", ".join(f"{v:.2f}" for v in st["max_abs_dev_vs_ensemble_in_noise"]) + "; " +
        ", ".join(f"{v:.2f}" for v in st["rms_dev_vs_ensemble_in_noise"]), "t60")
    des = cm.load_json("boxdesign", "design.json")["T2"]
    eps_ = [v["expected_per_step"] for v in des.values()]
    add("box", "planned rate test: expected collisions per step at $\\theta="
        + ", ".join(des.keys()) + "$", ", ".join(f"{v:.0f}" for v in eps_), "boxdesign")
    # ---------------- time scales, costs ----------------
    ts = cm.load_json("times", "timescales.json")["G26_core_445.8t0"]
    add("scales", "fluid model, collapsing core: $t_0/t_{\\rm dyn}$; fastest phase over "
        "$t_{\\rm dyn}$; ${\\rm Kn}$ of the core (lower bounds)",
        f"{e(ts['t0_over_tdyn'])}; {e(ts['tc_fast_over_tdyn'])}; {e(ts['Kn_core'])}", "times")
    costs = kc["costs"]
    add("scales", "cost of existing cluster runs at $10^4$ particles, s per $M$: static $M/2$; "
        "static $M/4$; adaptive",
        f"{costs[0]['s_per_M']:.2f}; {min(c['s_per_M'] for c in costs[1:3]):.2f}--"
        f"{max(c['s_per_M'] for c in costs[1:3]):.2f}; "
        f"{min(c['s_per_M'] for c in costs[3:]):.1f}--{max(c['s_per_M'] for c in costs[3:]):.1f}",
        "kncost")

    # ---------------- claims of the lead's documents ----------------
    claim("stage/G1/STATUS.md item 2", "Table 1: 56 rows, all columns within 1.1e-4 relative "
          "except R (printed on a 1e-3 grid) and three printed typos",
          f"56 rows; largest outside R and the typos: {cmax} {wmax[0]:.2e} (line {wmax[1]}); "
          f"typos {typos}", wmax[0] <= 1.15e-4, "thermal",
          "B, eps and ec0 exceed 1.1e-4 at line 503 (w0 = 4.5): the bound holds for E and E_rest only")
    claim("stage/G1/STATUS.md item 2", "Table 2: 14 roots, w0 within 1.1e-4",
          f"{len(rows2)} rows, w0 {w2:.2e}", len(rows2) == 14 and w2 <= 1.15e-4, "thermal")
    claim("stage/G0/REPORT.md 2.3", "fluid onset Z(0) = 0.6348 (b = 0.1, gamma = 1 + p/u)",
          f"{on['Z0']:.6f}", abs(on["Z0"] - 0.6348) < 5e-5, "thermal")
    claim("STATUS.md", "eps max at Z(0) = 0.5404 (b = 0.1)", f"{c1['max_eps']['Z0']:.6f}",
          abs(c1["max_eps"]["Z0"] - 0.5404) < 5e-5, "thermal")
    claim("stage/G1/STATUS.md item 2", "adiabatic-index root w0 = 4.05115",
          f"{c1['gavg_eq_gcr']['w0']:.6f}", abs(c1["gavg_eq_gcr"]["w0"] - 4.05115) < 5e-6, "thermal")
    claim("stage/G1/STATUS.md item 2", "onset Z(0) = 0.6348 (b = 0.1) to 0.5790 (b = 0.5)",
          f"{on['Z0']:.4f} to {crit['0.5']['omega2_zero_F21gamma']['Z0']:.4f}",
          abs(crit["0.5"]["omega2_zero_F21gamma"]["Z0"] - 0.5790) < 5e-5, "thermal")
    claim("stage/G1/STATUS.md item 2", "polytrope check: zero at the mass maximum to 3e-8",
          ", ".join(f"{abs(v):.1e}" for v in poly["rel_diff"].values()),
          max(abs(v) for v in poly["rel_diff"].values()) < 3.05e-8, "poly")
    claim("STATUS.md", "three independent equilibrium solvers agree to 3e-8",
          f"thermal core eps {d_eps:.1e}; King fraction {d3:.1e}", max(d_eps, d3) < 3.5e-8, "xchk",
          "King: 3.5e-8 (rounded to 3e-8)" if d3 >= 3.05e-8 else "")
    claim("stage/G1/STATUS.md item 3", "King y_max 0.33403", f"{km['y0']:.6f}",
          abs(km["y0"] - 0.33403) < 5e-6, "king")
    claim("stage/G0/REPORT.md 3", "monoenergetic threshold y_c = 0.67961", f"{mm['yc']:.6f}",
          abs(mm["yc"] - 0.67961) < 5e-6, "mono")
    claim("stage/G1/STATUS.md item 3", "243 pass flags of the 13 models", f"{npass} of {nflag}",
          npass == nflag == 243, "eqchk")
    claim("stage/G0/REPORT.md 2.2", "K = 168.9 for the King threshold model; 154-206 over the "
          "13 models; scope convention 198.6",
          f"{x4['Kn_sigma_lead_scope_solver']:.2f}; {min(Ks):.1f}-{max(Ks):.1f}; "
          f"{x4['Kn_sigma_scope_def']:.2f}",
          abs(x4["Kn_sigma_lead_scope_solver"] - 168.9) < 0.05 and abs(min(Ks) - 154) < 0.5
          and abs(max(Ks) - 206) < 0.5, "xchk")
    claim("stage/G0/REPORT.md 2.2", "sigma/m = sigma~ x 1.097e-23 cm^2/g x (M/M_sun)",
          f"{cM:.4e}", abs(cM - 1.097e-23) < 5e-27, "xchk")
    claim("stage/G0/REPORT.md 1", "200 M_sun core, sigma/m = 5: Kn_c = 4.5e-20 to 1.8e-19 "
          "(scope's H convention)", f"{p200[0]:.2e} to {p200[1]:.2e}",
          abs(p200[0] - 4.5e-20) / 4.5e-20 < 0.06 and abs(p200[1] - 1.8e-19) / 1.8e-19 < 0.06,
          "kncost", f"track definition over the 13 models: {kn200[0]:.1e} to {kn200[1]:.1e}")
    claim("stage/G0/REPORT.md 1", "1.9e9 M_sun core: Kn_c = 4e-13 to 2e-12",
          f"{p19[0]:.2e} to {p19[1]:.2e}",
          abs(p19[0] - 4e-13) / 4e-13 < 0.15 and abs(p19[1] - 2e-12) / 2e-12 < 0.15, "kncost")
    claim("stage/G0/REPORT.md 1", "every phase before the dynamical instability lasts at "
          "least 1e5 dynamical times of the then-current core",
          f"t0/t_dyn >= {ts['t0_over_tdyn']:.3e}; fastest phase >= {ts['tc_fast_over_tdyn']:.3e}",
          ts["tc_fast_over_tdyn"] >= 1e5, "times",
          "the fastest phase (t_c ~ 0.1 t_0) gives a lower bound of 8.5e4, not 1e5")
    claim("stage/G0/REPORT.md 3", "thermal core b = 0.1, Z(0) = 0.40-0.80: R/M = 20-26, "
          "r_core/M = 1.5-2.1, central lapse 0.56-0.71",
          f"R/M {min(RR):.2f}-{max(RR):.2f}; r_core/M {min(rc):.3f}-{max(rc):.3f}; "
          f"alpha_c {min(ac):.3f}-{max(ac):.3f}",
          min(RR) > 19.5 and max(RR) < 26.5 and min(rc) > 1.45 and max(rc) < 2.15, "init",
          "R/M and r_core/M quoted for a narrower range of Z(0); lapse agrees")
    claim("STATUS.md", "closed-form Moller rate confirmed to 5e-7 by a 3D quadrature",
          f"{max(rq):.2e}", max(rq) < 5.5e-7, "xchk", "5.2e-7, rounded")
    claim("STATUS.md", "core's kernels pass T0 on 208 vectors (3.2e-16, 1.32 eps)",
          f"{t0['n_cases']} cases, {fe:.2e}, {fc:.3f} eps, pass {t0['pass']}",
          t0["n_cases"] == 208 and abs(fe - 3.2e-16) < 0.05e-16 and abs(fc - 1.32) < 0.005
          and t0["pass"], "t0")
    claim("stage/G1/STATUS.md item 4", "T6-0 positions exact to 1.8e-12 L",
          f"{st['max_position_error_over_L']:.3e}", abs(st["max_position_error_over_L"] - 1.8e-12)
          < 0.05e-12, "t60")
    claim("stage/G1/STATUS.md 4", "King threshold model: central spacing 0.293 M at N = 1e4; "
          "H_c = 1.436 M", f"{kt['rows'][0]['d_c']:.4f}; {kt['H_c']:.4f}",
          abs(kt["rows"][0]["d_c"] - 0.293) < 5e-4 and abs(kt["H_c"] - 1.436) < 5e-4, "kneq")
    claim("stage/G0/OPEN.md 12", "momentum-constraint integral 1.42 times the reference",
          f"{sm['M_norm2_new'] / sm['M_norm2_ref']:.4f}",
          abs(sm["M_norm2_new"] / sm["M_norm2_ref"] - 1.42) < 0.005, "smoke")
    claim("stage/G0/CHECKLIST.md C4", "unit costs 1.67, 3.28-3.71, 14.2-17.5 s per M",
          f"{costs[0]['s_per_M']:.3f}; {costs[1]['s_per_M']:.3f}-{costs[2]['s_per_M']:.3f}; "
          f"{costs[3]['s_per_M']:.2f}-{costs[4]['s_per_M']:.2f}",
          abs(costs[0]["s_per_M"] - 1.67) < 0.005 and abs(costs[3]["s_per_M"] - 14.2) < 0.05
          and abs(costs[4]["s_per_M"] - 17.5) < 0.05, "kncost")

    # ---------------- write ----------------
    sect = {"baseline": "Spherical baseline", "models": "Particle models and Knudsen number",
            "collisions": "Collision operator: references and kernel test",
            "box": "Minkowski box in the code", "scales": "Time scales and costs"}
    parts = [(("baseline", "models"), "tab:ledger",
              "Numerical ledger. Every number of this note with the registered run that "
              "produced it."),
             (("collisions", "box", "scales"), "tab:ledger2",
              "Numerical ledger, continued.")]
    with open(os.path.join(out, "ledger.tex"), "w") as f:
        f.write("% generated by scripts/ledger.py from registered run outputs; do not edit\n")
        for secs, label, cap in parts:
            f.write(f"\\begin{{table*}}\n\\caption{{{cap}}}\n\\label{{{label}}}\n"
                    "\\begin{ruledtabular}\n\\footnotesize\n"
                    "\\begin{tabular}{p{0.44\\textwidth}p{0.30\\textwidth}l}\n"
                    "Quantity & Value & Run \\\\\n\\hline\n")
            last = None
            for s_, q, v, k in ROWS:
                if s_ not in secs:
                    continue
                if s_ != last:
                    f.write(f"\\multicolumn{{3}}{{l}}{{\\emph{{{sect[s_]}}}}} \\\\\n")
                    last = s_
                f.write(f"{q} & {v} & \\texttt{{\\scriptsize {R[k]}}} \\\\\n")
            f.write("\\end{tabular}\n\\end{ruledtabular}\n\\end{table*}\n")
    km_ = [m for m in idx["models"] if m["family"] == "king" and "threshold" in m["role"]][0]
    with open(os.path.join(out, "parameters.tex"), "w") as f:
        f.write("% generated by scripts/ledger.py from registered run outputs; do not edit\n")
        f.write("\\begin{table}\n\\caption{The equilibrium models at the instability criteria. "
                "Thermal core: $b=0.1$. $Z(0)$, $z_c$: central redshift; $\\epsilon$: "
                "binding-energy fraction; $R$: areal radius; $M$: ADM mass.}\n"
                "\\label{tab:parameters}\n"
                "\\begin{ruledtabular}\n\\begin{tabular}{llccc}\n"
                "Model & label & $Z(0)$, $z_c$ & $\\epsilon$ & $R/M$ \\\\\n\\hline\n")
        for lab, r in (("thermal, $\\epsilon$ max.", c1["max_eps"]),
                       ("thermal, onset $1+p/u$", on),
                       ("thermal, onset $5/3$", c1["omega2_zero_gamma53"]),
                       ("thermal, trial", c1["gavg_eq_gcr"])):
            f.write(f"{lab} & $w_0={r['w0']:.4f}$ & {r['Z0']:.4f} & {r['eps']:.5f} & "
                    f"{r['R'] / r['E']:.2f} \\\\\n")
        f.write(f"King, $\\epsilon$ max. & $y_0={km['y0']:.5f}$ & {km['Z0']:.4f} & "
                f"{km['eps_b']:.5f} & {km['R'] / km['M']:.2f} \\\\\n")
        f.write(f"monoen., $\\epsilon$ max. & $y_c={mm['yc']:.5f}$ & {mm['zc']:.4f} & "
                f"{mm['Eb_over_M0']:.5f} & {mm['R_over_M']:.2f} \\\\\n")
        f.write("\\end{tabular}\n\\end{ruledtabular}\n\\end{table}\n")
    with open(os.path.join(out, "claims.json"), "w") as f:
        json.dump(CLAIMS, f, indent=1)
    nd = sum(not c["agrees"] for c in CLAIMS)
    with open(os.path.join(out, "claims.md"), "w") as f:
        f.write("# Numbers of the lead's documents checked against the run outputs\n\n"
                "Generated by `note/scripts/ledger.py`; the files win where they differ.\n\n"
                f"{len(CLAIMS)} claims, {nd} differ.\n\n"
                "| Document | Claim | Files | Agrees | Note | Run |\n|---|---|---|---|---|---|\n")
        for c in CLAIMS:
            f.write(f"| {c['doc']} | {c['claim']} | {c['file_value']} | "
                    f"{'yes' if c['agrees'] else 'NO'} | {c['note']} | {c['run']} |\n")
    with open(os.path.join(out, "claims_summary.tex"), "w") as f:
        f.write(f"Of {len(CLAIMS)} numbers quoted in the stage documents of the track, "
                f"{len(CLAIMS) - nd} agree with the run outputs and {nd} differ")
    cm.report_checks("ledger")
    print(f"ledger: {len(ROWS)} rows; claims {len(CLAIMS)}, differ {nd}")
    for c in CLAIMS:
        if not c["agrees"]:
            print(f"ledger: DIFFERS: {c['doc']}: {c['claim']} | files: {c['file_value']}")


if __name__ == "__main__":
    main()
