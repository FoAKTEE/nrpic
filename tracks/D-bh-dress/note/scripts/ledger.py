"""Numerical ledger of the note and check of the lead's documents against the run outputs.

Writes, into the output directory (default ../tables):
  ledger.tex      the ledger appendix: every number of the note with its registered run;
  parameters.tex  the parameter table of the note (Einstein-Straus data set, vacuum puncture);
  claims.md, claims.json   numbers stated in stage/G0/REPORT.md, stage/G1/STATUS.md and
                  STATUS.md, each compared with the value in the run output it cites.
Inputs: the run outputs named in common.RUNS (sha256-checked where the run recorded sums)
and the *_numbers.json written by the figure scripts of the same registered run (sibling
directory figures/ of the output directory, or ../figures by default).
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

STEM = "ledger"


def fnum(x, sig=3):
    if x is None:
        return "--"
    if isinstance(x, str):
        return x
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    if -3 <= e <= 4:
        d = max(sig - 1 - e, 0)
        return f"{x:.{d}f}"
    m = x / 10**e
    return f"{m:.{sig - 1}f}e{e}"


def tex_num(s):
    """'1.23e-5' -> '$1.23\\times10^{-5}$' wherever such a number occurs in s."""
    return re.sub(r"(-?\d+(?:\.\d+)?)e([+-]?\d+)",
                  lambda m: f"${m.group(1)}\\times10^{{{int(m.group(2))}}}$", s)


def find_line(rel, needle):
    path = os.path.join(C.TRACK, rel)
    for i, line in enumerate(open(path), 1):
        if needle in line:
            return i
    return None


def main():
    out = C.out_dir("tables")
    figdir = os.path.join(os.path.dirname(os.path.abspath(out)), "figures")
    if not os.path.isdir(figdir):
        figdir = os.path.join(C.NOTE, "figures")
    fn = {k: json.load(open(os.path.join(figdir, f"fig_{k}_numbers.json")))
          for k in ("es", "constraints", "floor", "spike", "infall", "kerr", "newton", "esrun")}
    es = C.load_json("es_data", "es.json")
    s = es["summary"]
    plan = C.load_json("first_run", "first_run_plan.json")
    t0 = C.load_json("es_t0", "code_t0.json")
    t0log = open(C.run_file("es_t0", "log.txt")).read()
    erho = max(float(x.split(":")[1].strip().rstrip(",")) for x in t0log.splitlines()
               if '"E_minus_rho_max"' in x)
    sym = {k: sum(1 for x in open(C.run_file(k, "log.txt")) if x.startswith("[OK]"))
           for k in ("sym", "sym_lead")}
    scop = C.load_json("scoping", "scoping.json")["part_a"]
    drift = C.load_json("drift_ana", "drift_drift.json")
    lc = {k: C.load_json(k, "analysis.json")["losscone"] for k in ("lc05", "lc025")}
    rd = C.load_json("rd", "rd_checks.json")
    lead = C.load_json("infall_lead", "lead_infall_recheck.json")
    sh = C.load_json("shells_ana", "analysis.json")
    man = {k: json.load(open(os.path.join(C.TRACK, "runs", C.RUNS[k], "manifest.json")))
           for k in ("drift8", "drift16")}
    card = {k: m["resources"]["card_hours"] for k, m in man.items()}
    deck = {}                          # the input deck of the M/16 run, as its manifest records it
    dpath = man["drift16"]["inputs"][0]["path"]
    if C._sha256(dpath) != man["drift16"]["inputs"][0]["sha256"]:
        raise SystemExit(f"{dpath} differs from the deck the run recorded")
    block = None
    for line in open(dpath):
        line = line.split("#")[0].strip()
        if line.startswith("<"):
            block = line
        elif "=" in line and (block, line.split("=")[0].strip()) in (("<mesh>", "x1max"), ("<time>", "tlim")):
            deck[line.split("=")[0].strip()] = float(line.split("=")[1])
    cost = {c["name"]: c["card_h"] for c in plan["cost"]}
    c60_8 = cost["outer edge 60 M, M/8, dx_ball 2M, hp 1M"]
    c60_16 = cost["outer edge 60 M, M/16, dx_ball 2M, hp 1M"]
    c106_16 = cost["as generated (dust to 106 M), M/16, dx_ball 2M, hp 1M"]
    code = fn["constraints"]["code"]
    creg = fn["constraints"]["code_regions"]
    off = C.load_json("es_offline", "offline_check.json")["check_3d"]
    orders3d = []
    for bx in off.values():           # finest pair, largest residuals above round-off
        for q in ("H_max", "M_max"):
            e = [x[q] for x in bx["exact"]]
            if min(e) > 1e-15:
                orders3d.append(math.log(e[-2] / e[-1]) / math.log(bx["h"][-2] / bx["h"][-1]))
    f50 = drift["floors"]["50:210"]["M/16"]
    bnd = [drift["floors"][t0_]["M/16"][k]["dM_min"] for t0_ in ("50", "100", "20")
           for k in drift["floors"][t0_]["M/16"]]
    fl = fn["floor"]
    sp = fn["spike"]
    inf = fn["infall"]
    p4 = fn["es"]["P4"]
    rd_deta = max(abs(r["d_eta"]) for r in rd["table1"])
    rd_ratio = [r["y_eq_over_y_ta"] for r in rd["table1"]]

    R = C.RUNS
    E = []  # (section, quantity, value, run keys)
    sec = "Einstein-Straus data set and its checks"
    E += [(sec, r"bare puncture mass $m_p/M$; constant $a=1+u(0)$", f"{s['m_p']:.10f}; {s['a']:.10f}", ["es_data"]),
          (sec, r"plateau Hubble rate $HM$; Hubble radius $1/H$ in $M$", f"{fnum(s['H'], 5)}; {s['hubble_radius']:.1f}", ["es_data"]),
          (sec, r"plateau density $\rho_0M^2$; dust mass; total mass ($M$)", f"{fnum(s['rho0'], 5)}; {s['M_dust']:.4f}; {s['M_total']:.4f}", ["es_data"]),
          (sec, r"$HR$ at the Sch\"ucking radius; at the outer dust edge", f"{s['H_Rb']:.3f}; {s['H_Rout']:.3f}", ["es_data"]),
          (sec, r"table rows; dust particles; tracers", f"{es['table']['rows']}; {es['particles']['n_dust']}; {es['particles']['n_tracers']}", ["es_data"]),
          (sec, "lattice dust mass against the continuum (relative)", fnum(es["particles"]["rel_diff"]), ["es_data"]),
          (sec, "symbolic identities passed (two runs)", f"{sym['sym']} of 48; {sym['sym_lead']} of 48", ["sym", "sym_lead"]),
          (sec, "radial check, orders in the transition ($H$; $M_r$, finest pair)", f"{fn['constraints']['1d']['curvature transition H']['orders'][-1]:.2f}; {fn['constraints']['1d']['curvature transition M']['orders'][-1]:.2f}", ["es_offline"]),
          (sec, "3D check, orders of the largest residuals in seven boxes (range)", f"{min(orders3d):.2f}--{max(orders3d):.2f}", ["es_offline"]),
          (sec, r"AthenaK at $t=0$, box `mid transition', orders of $H$; $M$", f"{code['mid transition']['order_H']:.2f}; {code['mid transition']['order_M']:.2f}", ["es_t0_dx1", "es_t0_dx05", "es_t0"]),
          (sec, r"AthenaK at $t=0$, region $4<r<30M$, orders of $H$; $M$", f"{creg['transition 4 < r < 30']['H_max'][0]:.2f}; {creg['transition 4 < r < 30']['M_max'][0]:.2f}", ["es_t0"]),
          (sec, r"AthenaK at $t=0$, inner dust edge, orders of $H$; $M$", f"{creg['inner dust edge 34 < r < 46']['H_max'][0]:.2f}; {creg['inner dust edge 34 < r < 46']['M_max'][0]:.2f}", ["es_t0"]),
          (sec, "deposited density minus the exact density (largest)", fnum(erho), ["es_t0"]),
          (sec, "wall radius against the closed form; mass inside the wall minus $M$", f"{fnum(fn['es']['P3']['max_rel_wall_vs_closed'])}; {fnum(fn['es']['P3']['max_abs_mass_minus_1'])}", ["es_data"]),
          (sec, r"wall radius at $\tau=50,100,150,200M$ (in $M$)", ", ".join(f"{plan[f'tau={t}']['R_wall']:.2f}" for t in (50, 100, 150, 200)), ["first_run"]),
          (sec, r"scale factor of the plateau at $\tau=200M$; $1+6\ln a$", f"{plan['tau=200']['a_plateau']:.3f}; {plan['tau=200']['alpha_1plog_plateau']:.2f}", ["first_run"]),
          (sec, r"proper time to $R=2M$ from $6,10,20M$: closed form", ", ".join(f"{p4[k]['tau_closed']:.2f}" for k in ("R0=6", "R0=10", "R0=20")), ["es_data"]),
          (sec, r"density from the table: bubble (largest, in $\rho_0$); plateau (relative)", f"{fnum(fn['es']['P5']['inner_max_abs_rho_over_rho0'])}; {fnum(fn['es']['P5']['plateau_max_rel_dev'])}", ["es_data"]),
          (sec, "modelled cost, outer edge $60M$, $200M$: $M/8$; $M/16$ (card-hours)", f"{c60_8:.2f}; {c60_16:.2f}", ["first_run"]),
          (sec, "modelled cost of the data set as generated, $M/16$ (card-hours)", f"{c106_16:.1f}", ["first_run"])]
    sec = "Horizon-mass floor of a vacuum puncture"
    E += [(sec, r"$M_{\rm AH}/M-1$ at $t=100M$: $M/8$; $M/16$", f"{fnum(fl['drift8']['M_minus_1_at_100'])}; {fnum(fl['drift16']['M_minus_1_at_100'])}", ["drift8", "drift16"]),
          (sec, r"drift of the $20M$ mean, $50\to490M$: $M/8$; $M/16$", f"{fnum(fl['drift8']['drift_50_490'])}; {fnum(fl['drift16']['drift_50_490'])}", ["drift8", "drift16", "drift_lead"]),
          (sec, r"largest change of the mean on $[50,210]M$, $M/16$", fnum(fl["drift16"]["maxabsD_50_210"]), ["drift16"]),
          (sec, r"smallest detectable change, $M/16$, windows from $50M$ ending before $210M$", f"{fnum(min(f50[k]['dM_min'] for k in f50))} to {fnum(max(f50[k]['dM_min'] for k in f50))}", ["drift_ana"]),
          (sec, r"the same for windows across $220$--$255M$ (range)", f"{fnum(min(bnd))} to {fnum(max(bnd))}", ["drift_ana"]),
          (sec, r"peak to peak of the $5M$ mean in $220$--$255M$: $M/8$; $M/16$", f"{fnum(fl['drift8']['p2p_rm5_220_255'])}; {fnum(fl['drift16']['p2p_rm5_220_255'])}", ["drift8", "drift16"]),
          (sec, r"largest spin $|S|/M^2$ after $5M$: $M/8$; $M/16$", f"{fnum(fl['drift8']['max_S_over_M2_after5'])}; {fnum(fl['drift16']['max_S_over_M2_after5'])}", ["drift8", "drift16"]),
          (sec, "card-hours of the two runs", f"{card['drift8']:.3f}; {card['drift16']:.3f}", ["drift8", "drift16"])]

    # ---- the first full-relativity run and its vacuum control (wave 2; note v1)
    er = fn["esrun"]
    eb, ec = er["runs"]["bubble"], er["runs"]["control"]
    hb, hc = eb["horizon"], ec["horizon"]
    man_es = {k: json.load(open(os.path.join(C.TRACK, "runs", C.RUNS[k], "manifest.json"))) for k in ("es1", "v1")}

    def grp(run, R0):
        return [x for x in run["groups"] if abs(x["R0"] - R0) < 1e-9][0]
    lb, lc_ = er["lapse_probe_46M"]["bubble"], er["lapse_probe_46M"]["control"]
    pm = er["plateau_model"]
    def jl(needle):                    # locator of a prediction written before the runs
        return f"es_runs/JOURNAL.md:{find_line('es_runs/JOURNAL.md', needle)}"
    sec = "First run of the bubble and its vacuum control"
    E += [(sec, r"$M_{\rm AH}(100M)-M$: bubble run; control (prediction $+1.5\times10^{-3}\pm3\times10^{-4}$)",
           f"{fnum(hb['level'])}; {fnum(hc['level'])}", ["es1", "v1", "es_ana", jl("The level: M_AH(100 M) - M = +1.5e-3")]),
          (sec, r"largest $|M_{\rm AH}(t)/M_{\rm AH}(100M)-1|$ on $[100,200]M$: bubble; control (prediction $3\times10^{-5}$)",
           f"{fnum(hb['max_abs'])}; {fnum(hc['max_abs'])}", ["es1", "v1", "es_ana", jl("<= 3e-5 at M/8")]),
          (sec, r"the same drift on $[100,165]M$, range: bubble; control",
           f"{fnum(hb['window_100_165'][0])} to {fnum(hb['window_100_165'][1])}; {fnum(hc['window_100_165'][0])} to {fnum(hc['window_100_165'][1])}",
           ["es1", "v1", "es_extra"]),
          (sec, r"slope of the drift on $[100,200]M$ (per $M$): bubble; control",
           f"{fnum(hb['slope_per_M'])}; {fnum(hc['slope_per_M'])}", ["es1", "v1", "es_ana"]),
          (sec, r"largest $|$drift of bubble run $-$ drift of control$|$; over the control's largest drift (refutation above 3)",
           f"{fnum(er['difference']['max_abs'])}; {er['difference']['over_control_floor']:.2f}", ["es1", "v1", "es_ana", jl("Refuted by: a horizon-mass change")]),
          (sec, r"$M_{\rm AH}$ bubble $-$ control: largest $|\cdot|$ for $t\le20M$; first above $10^{-9}$ at $t$ ($M$); range on $[25,50]M$",
           f"{fnum(er['difference']['mass_bubble_minus_control_max_abs_t_le_20'])}; {er['difference']['t_first_split_1e-9']:.1f}; "
           f"{fnum(er['difference']['mass_bubble_minus_control_25_50'][0])} to {fnum(er['difference']['mass_bubble_minus_control_25_50'][1])}",
           ["es1", "v1", "es_extra"]),
          (sec, r"wall tracers, largest $|R/R_w-1|$ for $\tau\le200M$: bubble; control (prediction $3\times10^{-3}$)",
           f"{fnum(eb['wall']['max_abs_rel_tau_le_200'])}; {fnum(ec['wall']['max_abs_rel_tau_le_200'])}", ["es1", "v1", "es_ana", jl("to 3e-3 at")]),
          (sec, r"the same, bubble run, axis; diagonal tracers",
           f"{fnum(eb['wall']['by_class_tau_le_200']['axis'])}; {fnum(eb['wall']['by_class_tau_le_200']['diagonal'])}", ["es1"]),
          (sec, r"proper time at $R=2M$, group from $6M$: bubble; control; exact ($M$)",
           f"{grp(eb, 6)['tau_cross_2M_range'][0]:.4f}--{grp(eb, 6)['tau_cross_2M_range'][1]:.4f}; "
           f"{grp(ec, 6)['tau_cross_2M_range'][0]:.4f}--{grp(ec, 6)['tau_cross_2M_range'][1]:.4f}; {grp(eb, 6)['tau_cross_2M_exact']:.4f}",
           ["es1", "v1", "es_ana"]),
          (sec, r"the same, group from $10M$",
           f"{grp(eb, 10)['tau_cross_2M_range'][0]:.4f}--{grp(eb, 10)['tau_cross_2M_range'][1]:.4f}; "
           f"{grp(ec, 10)['tau_cross_2M_range'][0]:.4f}--{grp(ec, 10)['tau_cross_2M_range'][1]:.4f}; {grp(eb, 10)['tau_cross_2M_exact']:.4f}",
           ["es1", "v1", "es_ana"]),
          (sec, r"group from $20M$: crossing in the bubble run; exact; last proper time in the control ($M$)",
           f"{grp(eb, 20)['tau_cross_2M_range'][0]:.2f}--{grp(eb, 20)['tau_cross_2M_range'][1]:.2f}; {grp(eb, 20)['tau_cross_2M_exact']:.2f}; "
           f"{grp(ec, 20)['tau_end_range'][1]:.1f}", ["es1", "v1", "es_ana"]),
          (sec, r"lapse at the plateau probe at $t=10,25,50M$: bubble run; homogeneous $1+\log$ model (prediction)",
           f"{lb['t=10']:.3f}, {lb['t=25']:.3f}, {lb['t=50']:.3f}; {pm['t=10']:.3f}, {pm['t=25']:.3f}, {pm['t=50']:.3f}",
           ["es1", "es_ana", jl("alpha = 2.10, 3.58")]),
          (sec, r"lapse at the plateau probe at $t=100,200M$: bubble; control; model",
           f"{lb['t=100']:.3f}, {lb['t=200']:.3f}; {lc_['t=100']:.3f}, {lc_['t=200']:.3f}; {pm['t=100']:.2f}, {pm['t=200']:.2f}",
           ["es1", "v1", "es_ana"]),
          (sec, r"$K/(-3H)$ at the plateau tracer at $t=10,30,50,80,200M$",
           ", ".join(f"{er['K_over_minus3H_R0_48'][f't={T}']:.2f}" for T in (10, 30, 50, 80, 200)), ["es1", "es_extra"]),
          (sec, r"dust proper time at $t=200M$ (plateau group); homogeneous model",
           f"{er['dust_proper_time_R0_48_at_end'][0]:.1f}--{er['dust_proper_time_R0_48_at_end'][1]:.1f}; {er['plateau_model_tau_at_200']:.0f}",
           ["es1", "es_ana"]),
          (sec, r"smallest lapse on the mesh, range over the run; largest after $10M$: bubble; control",
           f"{fnum(lb['alpha_min_mesh_range'][0])}--{lb['alpha_min_mesh_range'][1]:.3f}, {lb['alpha_max_after_10']:.2f}; "
           f"{fnum(lc_['alpha_min_mesh_range'][0])}--{lc_['alpha_min_mesh_range'][1]:.3f}, {lc_['alpha_max_after_10']:.2f}",
           ["es1", "v1", "es_extra"]),
          (sec, r"tracers removed at the horizon: bubble; control; dust mass at start and end ($M$)",
           f"{lb['n_excised_last']}; {lc_['n_excised_last']}; {lb['sum_m_first_last'][0]:.10f}, {lb['sum_m_first_last'][1]:.10f}",
           ["es1", "v1"]),
          (sec, "card-hours: bubble run; control",
           f"{man_es['es1']['resources']['gpu_hours']:.3f}; {man_es['v1']['resources']['gpu_hours']:.3f}", ["es1", "v1"])]
    sec = "Spike in the probe limit"
    E += [(sec, r"constant $f$: peak density ($10^8$ GeV cm$^{-3}$) at $r/Gm$", f"{sp['peak_rel'][1]:.4f} at {sp['peak_rel'][0]:.2f}", ["spike_ref"]),
          (sec, "the same read off the published figure", f"{sp['peak_rel_sfw_fig1'][1]:.4f} at {sp['peak_rel_sfw_fig1'][0]:.2f}", ["spike_ref"]),
          (sec, r"largest relative deviation from the published curve, $8.5$--$95\,Gm$", fnum(sp["dev_vs_sfw_fig1_rel"]), ["spike_ref"]),
          (sec, r"peak ratio relativistic to Newtonian ($8Gm$ cut); excess of the $4Gm$ cut", f"{sp['ratio_peak_rel_over_gs8']:.3f}; {sp['excess_peak_gs4_over_rel']:.4f}", ["spike_ref"]),
          (sec, r"Hernquist cusp, $4\times10^6M_\odot$: peak (GeV cm$^{-3}$) at $r/Gm$", f"{fnum(sp['hernquist_m4e6']['peak_canonical'][1], 4)} at {sp['hernquist_m4e6']['peak_canonical'][0]:.2f}", ["spike_ref"]),
          (sec, r"largest deviation from the published Kerr-paper curve, $5$--$39\,Gm$", fnum(sp["hernquist_m4e6"]["dev_can_vs_fdrw"]["maxabs"]), ["spike_ref"]),
          (sec, r"AthenaK: particles; duration ($M$); $\chi^2$ per degree of freedom, median", f"{sp['n_particles']}; {sp['t_end']:.0f}; {sp['chi2_median_per_dof']:.2f}", ["spike_run", "spike_ana"]),
          (sec, r"largest $|\Delta E/E|$; $|\Delta L/L|$ over the run", f"{fnum(sp['invariants']['max_over_snapshots_dE/E_median_p99_max'][2])}; {fnum(sp['invariants']['max_over_snapshots_dL/L_median_p99_max'][2])}", ["spike_run", "spike_ana"]),
          (sec, r"count over equilibrium count, second half, $4$--$6\,Gm$", f"{sp['late_half_mean_over_expected']['4-6']:.3f}", ["spike_ana"]),
          (sec, "loss-cone probes: plunging that crossed; bound that crossed", f"{lc['lc025']['species1_predicted_plunge_crossed']} of {lc['lc025']['species1_predicted_plunge']}; {lc['lc025']['species1_predicted_bound_crossed']}", ["lc05", "lc025"]),
          (sec, r"median crossing-time offset at $\Delta t$ and $\Delta t/2$ ($M$)", f"{fnum(lc['lc05']['crossing_time_offset_meas_minus_pred']['median'])}; {fnum(lc['lc025']['crossing_time_offset_meas_minus_pred']['median'])}", ["lc05", "lc025"])]
    kr = fn["kerr"]
    kc, kh, ks = kr["constf"], kr["hern"], kr["stationarity"]
    kpr = kr["peak_ratios"]
    E += [(sec, r"Kerr, constant $f$, equator: peak density ($10^8$ GeV cm$^{-3}$) at $r/Gm$ for $a=0.5$; $0.8$",
           f"{kc['a=0.5']['peak_ours'][1]:.4f} at {kc['a=0.5']['peak_ours'][0]:.2f}; {kc['a=0.8']['peak_ours'][1]:.4f} at {kc['a=0.8']['peak_ours'][0]:.2f}",
           ["kerr_ref"]),
          (sec, "the same read off the published figure",
           f"{kc['a=0.5']['peak_published'][1]:.4f} at {kc['a=0.5']['peak_published'][0]:.2f}; {kc['a=0.8']['peak_published'][1]:.4f} at {kc['a=0.8']['peak_published'][0]:.2f}",
           ["kerr_ref"]),
          (sec, r"constant $f$: largest relative deviation from the published curves, $a=0,0.5,0.8$",
           ", ".join(fnum(kc[f"a={s_}"]["maxabs_rel_dev"]) for s_ in ("0", "0.5", "0.8")), ["kerr_ref"]),
          (sec, r"constant $f$: peak ratio $a=0.8$ over $a=0$; the same from the published figure",
           f"{kpr['constf_peak_a0.8_over_a0 (FdRW line 213: 20%)'][0]:.3f}; {kpr['constf_peak_a0.8_over_a0 (FdRW line 213: 20%)'][1]:.3f}", ["kerr_ref"]),
          (sec, r"Hernquist cusp, $a=0.8$: peak ($10^{18}$ GeV cm$^{-3}$) at $r/Gm$; published; ratio",
           f"{kh['a=0.8']['peak_ours'][1]:.3f} at {kh['a=0.8']['peak_ours'][0]:.2f}; {kh['a=0.8']['peak_published'][1]:.3f} at {kh['a=0.8']['peak_published'][0]:.2f}; "
           f"{kh['a=0.8']['peak_ours'][1] / kh['a=0.8']['peak_published'][1]:.3f}", ["kerr_ref"]),
          (sec, r"Hernquist cusp: median relative deviation from the published curves, $a=0,0.5,0.8$",
           ", ".join(fnum(kh[f"a={s_}"]["median_rel_dev"]) for s_ in ("0", "0.5", "0.8")), ["kerr_ref"]),
          (sec, r"Hernquist cusp: peak ratio $a=0.8$ over $a=0.5$; the same from the published figure",
           f"{kpr['hern_peak_a0.8_over_a0.5 (line 929: ~35%)'][0]:.3f}; {kpr['hern_peak_a0.8_over_a0.5 (line 929: ~35%)'][1]:.3f}", ["kerr_ref"]),
          (sec, r"Kerr code at $a=0$ against the Schwarzschild reference: constant $f$; Hernquist (largest relative)",
           f"{fnum(kr['a0_vs_wave1']['constf_maxrel'])}; {fnum(kr['a0_vs_wave1']['hern_maxrel'])}", ["kerr_ref"]),
          (sec, r"AthenaK, $a=0.8$: particles; duration ($M$); $\chi^2$ at $t=0$, median, range; degrees of freedom",
           f"{ks['N']}; {ks['t_end']:.0f}; {ks['chi2_t0']:.1f}, {ks['chi2_median']:.1f}, {ks['chi2_min']:.1f}--{ks['chi2_max']:.1f}; {ks['dof']}",
           ["kerr_run", "kerr_expected", "kerr_ana"]),
          (sec, r"late over early half of the counts in $0$--$4$, $4$--$6$, $6$--$10$, $10$--$16$, $16$--$40\,Gm$",
           ", ".join(f"{v['late_over_early']:.3f}" for v in ks["ranges"].values()), ["kerr_ana"]),
          (sec, r"mean $L_z/Gm$ in the same ranges, late half; reference",
           ", ".join(f"{v['Lz_mean_late_half']:.3f}" for v in ks["ranges"].values()) + "; " +
           ", ".join(f"{v['Lz_mean_ref']:.3f}" for v in ks["ranges"].values()), ["kerr_expected", "kerr_ana"]),
          (sec, r"largest $|\Delta E/E|$, median and largest; largest $|\Delta L_z|$; smallest radius reached ($Gm$)",
           f"{fnum(ks['invariants']['dE/E_median_p99_max'][0])}, {fnum(ks['invariants']['dE/E_median_p99_max'][2])}; "
           f"{fnum(ks['invariants']['dLz_median_p99_max'][2])}; {ks['inner']['min_r_over_snapshots']:.3f}", ["kerr_ana"]),
          (sec, r"equator over pole, inside $16\,Gm$: late half; reference",
           f"{ks['contrast']['late_half_mean']:.3f}; {ks['contrast']['ref']:.3f}", ["kerr_expected", "kerr_ana"])]
    sec = "Secondary infall and capture"
    E += [(sec, r"turned-around mass $M_{\rm ta}/M$ at $a/a_i=2,4,8$ (closed form)", ", ".join(f"{lead['0.01'][a]['M_ta']:.5f}" for a in ("2", "4", "8")), ["infall_lead"]),
          (sec, r"mass that reached the centre at $a/a_i=2,4,8$ ($M$)", ", ".join(f"{lead['0.01'][a]['M_c']:.4f}" for a in ("2", "4", "8")), ["infall_lead"]),
          (sec, r"$(M_{\rm ta}-M)/(Ma/a_i)$ at $a/a_i=2$; $100$; limit $(4/3\pi)^{2/3}$", f"{lead['0.01']['2']['coef']:.3f}; {lead['0.01']['100']['coef']:.4f}; {lead['coef_limit_(4/(3pi))^(2/3)']:.4f}", ["infall_lead"]),
          (sec, r"turnaround radius at $a/a_i=2$ for $\epsilon=0.003,0.01,0.03,0.1$ ($M$)", ", ".join(f"{scop[e]['r_ta_at_a2']:.1f}" for e in ("0.003", "0.01", "0.03", "0.1")), ["scoping"]),
          (sec, r"black-hole mass, radial dust absorbed, $a/a_i=2,4$; doubling at $a/a_i$", f"{sh['checks']['a2']['mbh']:.3f}, {sh['checks']['a4']['mbh']:.3f}; {sh['mbh_doubling_a']:.2f}", ["shells_ana"]),
          (sec, r"self-similar: slope of $m(\lambda)$ on $[10^{-4},10^{-3}]$; on $[3\times10^{-3},3\times10^{-2}]$", f"{inf['selfsim']['slope_m_1em4_1em3']:.3f}; {inf['selfsim']['slope_m_3em3_3em2']:.3f}", ["selfsim"]),
          (sec, r"outermost caustic $\lambda_1$; mass inside it ($M_{\rm ta}$)", f"{inf['selfsim']['lambda1']:.4f}; {inf['selfsim']['m_at_lambda1']:.3f}", ["selfsim"]),
          (sec, r"$\lambda^{9/4}\rho/\rho_b$ below $\lambda=10^{-4}$", f"{inf['selfsim']['rho_lam94_innermost']:.2f}", ["selfsim"]),
          (sec, "fraction of the turned-around mass that passed the centre", f"{inf['shells']['f_passed']:.4f}", ["shells_ana"]),
          (sec, r"captured fraction at $a/a_i=4$ for $\sigma_i=0.02,0.05,0.1,0.2$", ", ".join(f"{v:.3f}" for v in inf["shells"]["captured_fraction"].values()), ["shells_ana"]),
          (sec, r"radiation era: largest $|\Delta\eta|$ against the printed table; $y_{\rm eq}/y_{\rm ta}$", f"{fnum(rd_deta, 2)}; {min(rd_ratio):.4f}--{max(rd_ratio):.4f}", ["rd"])]
    nw = fn["newton"]["runs"]
    N1, N2, N3 = nw["N128c"], nw["N64c"], nw["N128Lc"]
    NR = ["nm128c", "nm64c", "nm128Lc", "nm_ana"]

    def gat(run, a):
        return [x for x in run["growth"] if abs(x["a"] - a) < 1e-9][0]

    def prof(run, a):
        return min(run["profiles"], key=lambda p: abs(p["a"] - a))
    E += [(sec, r"Newtonian mode: cells ($M$) of the three runs; last $a/a_i$",
           f"{N1['dx']:.4g}, {N2['dx']:.4g}, {N3['dx']:.4g}; {N1['a_end']:.0f}, {N2['a_end']:.0f}, {N3['a_end']:.0f}", NR),
          (sec, r"$M_{\rm ta}/M$ at $a/a_i=4$, three runs (matched shells); at $8$",
           ", ".join(f"{gat(n, 4)['mta']:.4f} ({n['kernel_shells_at']['4']['mta']:.4f})" for n in (N1, N2, N3)) +
           f"; {gat(N3, 8)['mta']:.4f} ({N3['kernel_shells_at']['8']['mta']:.4f})", NR),
          (sec, r"dress ($M$) at $a/a_i=4$, three runs (matched shells); at $8$",
           ", ".join(f"{gat(n, 4)['dress']:.4f} ({n['kernel_shells_at']['4']['dress']:.4f})" for n in (N1, N2, N3)) +
           f"; {gat(N3, 8)['dress']:.4f} ({N3['kernel_shells_at']['8']['dress']:.4f})", NR),
          (sec, r"largest $|M_{\rm ta}/M_{\rm ta}^{\rm shells}-1|$ after $a/a_i=1.5$: mesh kernel; Plummer law",
           ", ".join(fnum(n["vs_kernel"]["mta_max_rel"]) for n in (N1, N2, N3)) + "; " +
           ", ".join(fnum(n["vs_plummer"]["mta_max_rel"]) for n in (N1, N2, N3)), NR),
          (sec, r"dress over $M_{\rm ta}$ at $a/a_i=4$; $8$; self-similar",
           f"{N1['dress_over_mta_end']:.3f}; {N3['dress_over_mta_end']:.3f}; {fn['newton']['selfsim_dress_over_mta']:.3f}", NR),
          (sec, r"$M_{\rm ta}/(Ma/a_i)$ at $a/a_i=4$; $8$; local growth exponent of the dress at $4$; $8$",
           f"{N1['mta_over_a_end']:.3f}; {N3['mta_over_a_end']:.3f}; {N1['dlnMdress_dlna_end']:.2f}; {N3['dlnMdress_dlna_end']:.2f}", NR),
          (sec, r"profile from $4\Delta x$ to $r_{\rm ta}$ outside the caustic bins, largest (rms) deviation from the matched shells: $a/a_i=4$ two runs; $8$",
           f"{fnum(prof(N1, 4)['ratio_kernel']['max_dev_excl_caustic'])} ({fnum(prof(N1, 4)['ratio_kernel']['rms_dev_excl_caustic'])}), "
           f"{fnum(prof(N2, 4)['ratio_kernel']['max_dev_excl_caustic'])}; "
           f"{fnum(prof(N3, 8)['ratio_kernel']['max_dev_excl_caustic'])} ({fnum(prof(N3, 8)['ratio_kernel']['rms_dev_excl_caustic'])})", NR),
          (sec, r"radius enclosing 99 of 100 parts of the dress at $a/a_i=4$, finest run; matched shells ($M$)",
           f"{prof(N1, 4)['r_sp99']:.1f}; {prof(N1, 4)['ref_kernel_r_sp99']:.1f}", NR),
          (sec, r"run over self-similar density on $0.1\le\lambda\le0.35$: $a/a_i=4$; $8$ (range)",
           f"{min(prof(N1, 4)['selfsim_ratio_0p1_0p35']):.2f}--{max(prof(N1, 4)['selfsim_ratio_0p1_0p35']):.2f}; "
           f"{min(prof(N3, 8)['selfsim_ratio_0p1_0p35']):.2f}--{max(prof(N3, 8)['selfsim_ratio_0p1_0p35']):.2f}", NR + ["selfsim"]),
          (sec, r"largest offset of the seed clump from its cell centre, in cells",
           ", ".join(fnum(n["clump_com_max_over_dx"]) for n in (N1, N2, N3)), NR)]

    # ---- claims of the lead's documents against the files ----
    G1, G0, ST = "stage/G1/STATUS.md", "stage/G0/REPORT.md", "STATUS.md"
    K = []

    def claim(doc, needle, stated, value, verdict, runs, note=""):
        K.append(dict(doc=doc, line=find_line(doc, needle), stated=stated, file_value=value,
                      verdict=verdict, runs=[R[r] for r in runs], note=note))
    ok = "agrees"
    claim(G1, "a = 0.9765922286441", "a = 0.9765922286441, m_p = 1.023968828206 M", f"{s['a']:.13f}, {s['m_p']:.12f}", ok, ["es_data"])
    claim(G1, "48 symbolic identities", "48 symbolic identities, lead rerun 48/48", f"{sym['sym']}, {sym['sym_lead']} lines [OK]", ok, ["sym", "sym_lead"])
    claim(G1, "orders 3.85-4.07", "offline 3D orders 3.85-4.07 in seven sub-boxes", f"finest-pair orders of the largest residuals above round-off, seven boxes: {min(orders3d):.2f}-{max(orders3d):.2f}", ok, ["es_offline"])
    claim(G1, "order 5.8-5.9", "order 5.8-5.9 in the curvature transition",
          f"box 'mid transition': H {code['mid transition']['order_H']:.2f}, M {code['mid transition']['order_M']:.2f}; whole region 4 < r < 30 M: H {creg['transition 4 < r < 30']['H_max'][0]:.2f}, M {creg['transition 4 < r < 30']['M_max'][0]:.2f}",
          "agrees for one box only", ["es_t0"], "the region-wide orders are 5.3 and 4.7; say 'in the middle of the transition'")
    claim(G1, "3.2 at the inner dust edge", "3.2 at the inner dust edge", f"M {creg['inner dust edge 34 < r < 46']['M_max'][0]:.2f}, H {creg['inner dust edge 34 < r < 46']['H_max'][0]:.2f}", ok, ["es_t0"], "3.2 is the momentum residual")
    claim(G1, "rho to 1.1e-13", "deposited density equals rho to 1.1e-13", fnum(erho), ok, ["es_t0"])
    claim(G1, "0.8699e8", "peak 0.8699e8 GeV/cm^3 at 7.58 Gm", f"{sp['peak_rel'][1]:.5f}e8 at {sp['peak_rel'][0]:.3f}", ok, ["spike_ref"])
    claim(G1, "0.02 per cent", "against digitized SFW Fig. 1 to 0.02 per cent",
          f"peak height {abs(sp['peak_rel'][1] / sp['peak_rel_sfw_fig1'][1] - 1):.1e}, position {abs(sp['peak_rel'][0] / sp['peak_rel_sfw_fig1'][0] - 1):.1e}; whole curve 8.5-95 Gm {sp['dev_vs_sfw_fig1_rel']:.1e}",
          "agrees for the peak", ["spike_ref"], "the whole curve deviates by up to 0.26 per cent")
    claim(G1, "1.0 per cent", "FdRW Schwarzschild curve to 1.0 per cent", fnum(sp["hernquist_m4e6"]["dev_can_vs_fdrw"]["maxabs"]), ok, ["spike_ref"])
    claim(G1, "chi^2/dof median 0.98", "48000 particles for 20000 M, chi^2/dof median 0.98", f"{sp['n_particles']}, {sp['t_end']:.0f} M, {sp['chi2_median_per_dof']:.3f}", ok, ["spike_ana"])
    claim(G1, "1200/1200", "loss-cone probes 1200/1200 inside cross, 0/1200 outside", f"{lc['lc025']['species1_predicted_plunge_crossed']}/{lc['lc025']['species1_predicted_plunge']}, {lc['lc025']['species1_predicted_bound_crossed']}", ok, ["lc05", "lc025"])
    claim(G0, "|dE/E| at most 1.3e-6", "|dE/E| at most 1.3e-6, |dL/L| at most 1.9e-10 over 20000 M (run -123755)", f"{fnum(sp['invariants']['max_over_snapshots_dE/E_median_p99_max'][2])}, {fnum(sp['invariants']['max_over_snapshots_dL/L_median_p99_max'][2])}", ok, ["spike_ana"], "the numbers are in the analysis run D-bh-dress-20261115-125739-a18d74d, the report cites the simulation run")
    claim(G1, "slope of m 0.741", "slope of m 0.741 on [1e-4, 1e-3] r_ta, outermost caustic 0.355 r_ta", f"{inf['selfsim']['slope_m_1em4_1em3']:.3f}, {inf['selfsim']['lambda1']:.4f}", ok, ["selfsim"])
    claim(G1, "dress 0.625 M_ta", "dress 0.625 M_ta (run -123813-97afeea)",
          f"run -123813-97afeea prints m(lambda_1) = {inf['selfsim']['m_at_lambda1']:.3f}; 0.625 is f_passed = {inf['shells']['f_passed']:.4f} of run -125613-248fdaf",
          "disagrees (locator)", ["selfsim", "shells_ana"], "cite run D-bh-dress-20261115-125613-248fdaf for 0.625, or quote 0.654 as the mass inside the outermost caustic")
    claim(G1, "1.3e-5", "eta_ta of 2106.07480 to 1.3e-5; the 0.964 of 1901.08528 reproduced", f"max |d_eta| {rd_deta:.2e}; y_eq/y_ta {min(rd_ratio):.4f}-{max(rd_ratio):.4f}", ok, ["rd"])
    claim(G1, "M_ta 1.52542, 2.62815", "M_ta 1.52542, 2.62815 at a/a_i = 2, 4", f"{lead['0.01']['2']['M_ta']:.5f}, {lead['0.01']['4']['M_ta']:.5f}", ok, ["infall_lead"])
    claim(G1, "+2.95e-4 (M/8)", "drift 50 -> 490 M +2.95e-4 (M/8), +3.67e-5 (M/16)", f"{fnum(fl['drift8']['drift_50_490'])}, {fnum(fl['drift16']['drift_50_490'])}", ok, ["drift8", "drift16"], "the 20 M mean ends at 489.5 and 489.75 M")
    claim(G1, "2.0-2.5e-5", "smallest detectable change at M/16 2.0-2.5e-5 (windows from 50 M ending before 210 M)", f"{fnum(min(f50[k]['dM_min'] for k in f50))}-{fnum(max(f50[k]['dM_min'] for k in f50))}", ok, ["drift_ana"])
    claim(G1, "5-9e-5", "5-9e-5 across the outer-boundary excursions", f"{fnum(min(bnd))}-{fnum(max(bnd))}", ok, ["drift_ana"])
    claim(G1, "9.3e-5 peak to peak", "9.3e-5 peak to peak in 220-255 M at both resolutions", f"{fnum(fl['drift8']['p2p_rm5_220_255'])}, {fnum(fl['drift16']['p2p_rm5_220_255'])}", ok, ["drift8", "drift16"])
    claim(G1, "spin below 5.7e-9", "spin below 5.7e-9 at M/16", fnum(fl["drift16"]["max_S_over_M2_after5"]), ok, ["drift16"])
    claim(G1, "2.18 card-hours", "2.18 card-hours", f"{card['drift8']:.3f} + {card['drift16']:.3f} = {card['drift8'] + card['drift16']:.3f}", ok, ["drift8", "drift16"])
    claim(G1, "2.8e-5 from t0 = 100 M", "D-pre-4 gives 2.8e-5 from t0 = 100 M before 210 M", f"M/8, T = 40.6 M: {fnum(drift['floors']['100:210']['M/8']['eps0.03_a2']['dM_min'])}; M/16: {fnum(drift['floors']['100:210']['M/16']['eps0.03_a2']['dM_min'])}", ok, ["drift_ana"], "valid for a window of 40.6 M; the run gives no window from 100 M longer than 110 M")
    claim(G1, "+1.5e-3 +- 3e-4", "M_AH(100 M) - M = +1.50e-3 at M/8 (D-pre-4)", fnum(fl["drift8"]["M_minus_1_at_100"], 4), ok, ["drift8"])
    claim(G1, "46.99", "R_w = 46.99, 56.80, 65.84, 74.29 M at tau = 50, 100, 150, 200 M", ", ".join(f"{plan[f'tau={t}']['R_wall']:.2f}" for t in (50, 100, 150, 200)), ok, ["first_run"])
    claim(G1, "reach R = 2M at tau = 15.0 M", "groups at 6 M and 10 M reach R = 2M at tau = 15.0 M and 34.6 M; 20 M group at 245 M",
          f"closed form {p4['R0=6']['tau_closed']:.2f}, {p4['R0=10']['tau_closed']:.2f}, {p4['R0=20']['tau_closed']:.2f} M; 15.0, 34.6, 244.8 are the first samples (spacing 0.2 M) after the crossing",
          "agrees to the sampling", ["es_data", "first_run"], "use 14.83 and 34.44 M as the exact arrival times in the G2 criterion")
    claim(G1, "4.9 by", "alpha = 1 + 6 ln a, about 4.9 by tau = 200 M (a = 1.93)", f"{plan['tau=200']['alpha_1plog_plateau']:.3f}, a = {plan['tau=200']['a_plateau']:.3f}", ok, ["first_run"])
    claim(G1, "Cost 1.4 card-hours", "ES-1 cost 1.4 card-hours (M/8); 2.9 at M/16", f"{c60_8:.3f}, {c60_16:.3f}", ok, ["first_run"])
    claim(G1, "about 1.2 card-hours", "V-1 about 1.2 card-hours [JUDGEMENT]", "no vacuum-control row in the cost table; the 1.24 row is the dust run with particle spacing 2 M", "not computed", ["first_run"], "compute V-1 with the cost model before submission (OPEN item 6)")
    claim(G0, "11.3 card-hours", "data set as generated: 11.3 card-hours at M/16 for 200 M", f"{c106_16:.2f}", ok, ["first_run"])
    claim(G0, "16-33 M", "turnaround radius after one doubling 16-33 M at eps 0.01-0.03", f"{scop['0.03']['r_ta_at_a2']:.1f}-{scop['0.01']['r_ta_at_a2']:.1f}", ok, ["scoping"])
    claim(G0, "74 per", "74 per cent still captured at sigma_i = 0.2", f"{inf['shells']['captured_fraction']['0.2']:.3f}", ok, ["shells_ana"])
    claim(G0, "1.525, 2.628, 4.871", "M_ta/M = 1.525, 2.628, 4.871; centre 1.190, 1.828, 3.215", ", ".join(f"{lead['0.01'][a]['M_ta']:.3f}" for a in ("2", "4", "8")) + "; " + ", ".join(f"{lead['0.01'][a]['M_c']:.3f}" for a in ("2", "4", "8")), ok, ["infall_lead"])
    claim(G0, "0.263 at a/a_i = 2", "coefficient 0.263 at a/a_i = 2, 0.558 at 100, limit 0.5648", f"{lead['0.01']['2']['coef']:.3f}, {lead['0.01']['100']['coef']:.3f}, {lead['coef_limit_(4/(3pi))^(2/3)']:.4f}", ok, ["infall_lead"])
    claim(G0, "33.4 M (eps 0.01)", "r_ta(a/a_i = 2) = 33.4 M (eps 0.01), 16.1 M (eps 0.03)", f"{scop['0.01']['r_ta_at_a2']:.1f}, {scop['0.03']['r_ta_at_a2']:.1f}", ok, ["scoping"])
    claim(ST, "2.0-2.5e-5", "floor 2.0-2.5e-5 at M/16 before 210 M", f"{fnum(min(f50[k]['dM_min'] for k in f50))}-{fnum(max(f50[k]['dM_min'] for k in f50))}", ok, ["drift_ana"])

    # ---- note v1: numbers of the wave-2 documents behind the new sections, each against the
    # value this package recomputed from the registered run output. The verdict is computed:
    # "agrees" when every stated number equals the file value to its printed digits.
    def tol(sv):
        m = re.fullmatch(r"[+-]?(\d+)(?:\.(\d+))?(?:e([+-]?\d+))?", sv.strip())
        if not m:
            raise SystemExit(f"cannot read the stated number {sv!r}")
        return 0.5 * 10.0 ** (int(m.group(3) or 0) - len(m.group(2) or ""))

    def nclaim(doc, needle, stated, values, runs, note="", scale=1.0):
        """stated: list of number strings as printed; values: file values in the same units
        (times scale: 100 for per cent)."""
        vals = [float(v) * scale for v in values]
        good = all(abs(float(sv) - v) <= tol(sv) * (1 + 1e-9) for sv, v in zip(stated, vals))
        K.append(dict(doc=doc, line=find_line(doc, needle), stated=needle + "  [" + ", ".join(stated) + "]",
                      file_value=", ".join(f"{v:.6g}" for v in vals), verdict="agrees" if good else "disagrees",
                      runs=[R[r] for r in runs], note=note))
    SP, NI, ER, EJ = "spike/README.md", "secondary_infall/README.md", "es_runs/README.md", "es_runs/JOURNAL.md"
    nclaim(SP, "7.31 Gm and 1.0604e8 at 6.61 Gm", ["0.9271e8", "7.31", "1.0604e8", "6.61"],
           [kc["a=0.5"]["peak_ours"][1] * 1e8, kc["a=0.5"]["peak_ours"][0], kc["a=0.8"]["peak_ours"][1] * 1e8, kc["a=0.8"]["peak_ours"][0]], ["kerr_ref"])
    nclaim(SP, "within 0.88 % and 0.95 % of fig_rho_a", ["0.88", "0.95"],
           [kc["a=0.5"]["maxabs_rel_dev"], kc["a=0.8"]["maxabs_rel_dev"]], ["kerr_ref"], scale=100)
    nclaim(SP, "Peak ratio a = 0.8 over a = 0: 1.219", ["1.219"],
           [kpr["constf_peak_a0.8_over_a0 (FdRW line 213: 20%)"][0]], ["kerr_ref"])
    nclaim(SP, "4.083e18 at 5.07", ["3.922e18", "5.06", "4.083e18", "5.07"],
           [kh["a=0.8"]["peak_ours"][1] * 1e18, kh["a=0.8"]["peak_ours"][0], kh["a=0.8"]["peak_published"][1] * 1e18, kh["a=0.8"]["peak_published"][0]],
           ["kerr_ref"], "the published value is digitized from the arXiv source by the reference run")
    nclaim(SP, "lies between ours (1.406) and their figure", ["1.406", "1.451"],
           kpr["hern_peak_a0.8_over_a0.5 (line 929: ~35%)"], ["kerr_ref"])
    nclaim(SP, "51.4 at t = 0, median 43.8, range 20-75", ["51.4", "43.8", "20", "75"],
           [ks["chi2_t0"], ks["chi2_median"], ks["chi2_min"], ks["chi2_max"]], ["kerr_ana"])
    nclaim(SP, "late/early-half ratios 0.998, 1.003, 0.999, 1.000, 1.000", ["0.998", "1.003", "0.999", "1.000", "1.000"],
           [v["late_over_early"] for v in ks["ranges"].values()], ["kerr_ana"])
    nclaim(SP, "(reference 2.267, 1.800, 1.069, 0.645, 0.352)", ["2.267", "1.800", "1.069", "0.645", "0.352"],
           [v["Lz_mean_ref"] for v in ks["ranges"].values()], ["kerr_expected", "kerr_ana"])
    nclaim(SP, "2.267, 1.810, 1.054, 0.655, 0.370", ["2.267", "1.810", "1.054", "0.655", "0.370"],
           [v["Lz_mean_late_half"] for v in ks["ranges"].values()], ["kerr_ana"],
           "last digit only: the 10-16 Gm value is 0.6565, printed 0.655")
    nclaim(SP, "|dE/E| median 1.2e-8, max 7.9e-6", ["1.2e-8", "7.9e-6"],
           [ks["invariants"]["dE/E_median_p99_max"][0], ks["invariants"]["dE/E_median_p99_max"][2]], ["kerr_ana"])
    nclaim(SP, "late-half 1.130, reference 1.127", ["1.130", "1.127"],
           [ks["contrast"]["late_half_mean"], ks["contrast"]["ref"]], ["kerr_expected", "kerr_ana"])
    nclaim(NI, "| M_ta at a/a_i = 4 |", ["2.5966", "2.5956", "2.5966", "2.5934", "2.5962", "2.5937"],
           [x for n in (N1, N2, N3) for x in (gat(n, 4)["mta"], n["kernel_shells_at"]["4"]["mta"])], NR)
    nclaim(NI, "| M_ta at a/a_i = 8 |", ["4.8159", "4.8019"], [gat(N3, 8)["mta"], N3["kernel_shells_at"]["8"]["mta"]], NR)
    nclaim(NI, "| dress at a/a_i = 4 |", ["0.7975", "0.7976", "0.7966", "0.7954", "0.7977", "0.7940"],
           [x for n in (N1, N2, N3) for x in (gat(n, 4)["dress"], n["kernel_shells_at"]["4"]["dress"])], NR)
    nclaim(NI, "| dress at a/a_i = 8 |", ["2.1537", "2.1515"], [gat(N3, 8)["dress"], N3["kernel_shells_at"]["8"]["dress"]], NR)
    nclaim(NI, "| largest M_ta deviation after a/a_i = 1.5 |", ["0.10", "0.12", "0.31"],
           [n["vs_kernel"]["mta_max_rel"] for n in (N1, N2, N3)], NR, scale=100)
    nclaim(NI, "| profile, 4 dx to r_ta, outside the caustic bins |", ["12", "6.5", "6.3", "26", "14"],
           [prof(N1, 4)["ratio_kernel"]["max_dev_excl_caustic"], prof(N1, 4)["ratio_kernel"]["rms_dev_excl_caustic"],
            prof(N2, 4)["ratio_kernel"]["max_dev_excl_caustic"], prof(N3, 8)["ratio_kernel"]["max_dev_excl_caustic"],
            prof(N3, 8)["ratio_kernel"]["rms_dev_excl_caustic"]], NR, scale=100)
    nclaim(NI, "dress/M_ta = 0.307 (a/a_i = 4) and 0.447 (8)", ["0.307", "0.447"],
           [N1["dress_over_mta_end"], N3["dress_over_mta_end"]], NR)
    nclaim(NI, "M_ta/(M a/a_i) = 0.649 and 0.602", ["0.649", "0.602"], [N1["mta_over_a_end"], N3["mta_over_a_end"]], NR)
    nclaim(NI, "growth exponent of the dress 1.70 at 4 and 1.25 at 8", ["1.70", "1.25"],
           [N1["dlnMdress_dlna_end"], N3["dlnMdress_dlna_end"]], NR)
    nclaim(NI, "r_sp99 18.4 against 15.9 M", ["18.4", "15.9"], [prof(N1, 4)["r_sp99"], prof(N1, 4)["ref_kernel_r_sp99"]], NR,
           "last digit only: the matched-shell value is 15.85 (kernel law), printed 15.9")
    nclaim(ER, "max over 100-200 M | 3.40e-4 | 1.37e-4", ["3.40e-4", "1.37e-4"], [hb["max_abs"], hc["max_abs"]], ["es1", "v1", "es_ana"])
    nclaim(ER, "| same, over 100-165 M", ["-5.0e-5", "9.3e-5", "-4.2e-5", "2.1e-5"],
           hb["window_100_165"] + hc["window_100_165"], ["es1", "v1", "es_extra"])
    nclaim(ER, "| M_AH(100 M) - M | +9.55e-4 | +9.37e-4", ["9.55e-4", "9.37e-4"], [hb["level"], hc["level"]], ["es1", "v1", "es_ana"])
    nclaim(ER, "| wall tracers, max relative error for tau <= 200 M | 2.20e-3 | 1.59e-3", ["2.20e-3", "1.59e-3"],
           [eb["wall"]["max_abs_rel_tau_le_200"], ec["wall"]["max_abs_rel_tau_le_200"]], ["es1", "v1", "es_ana"])
    nclaim(ER, "| R0 = 6 M group reaches R = 2M (exact 14.827 M) | 14.826 M | 14.826 M", ["14.827", "14.826", "14.826"],
           [grp(eb, 6)["tau_cross_2M_exact"], grp(eb, 6)["tau_cross_2M_mean"], grp(ec, 6)["tau_cross_2M_mean"]], ["es1", "v1", "es_ana"])
    nclaim(ER, "| R0 = 10 M group reaches R = 2M (exact 34.442 M) | 34.437 M | 34.437 M", ["34.442", "34.437", "34.437"],
           [grp(eb, 10)["tau_cross_2M_exact"], grp(eb, 10)["tau_cross_2M_mean"], grp(ec, 10)["tau_cross_2M_mean"]], ["es1", "v1", "es_ana"])
    nclaim(ER, "| R0 = 20 M group (exact 244.74 M) | 244.09-244.51 M at t = 177 M", ["244.74", "244.09", "244.51", "177"],
           [grp(eb, 20)["tau_cross_2M_exact"], grp(eb, 20)["tau_cross_2M_range"][0], grp(eb, 20)["tau_cross_2M_range"][1],
            grp(eb, 20)["t_cross_2M_mean"]], ["es1", "es_ana"])
    nclaim(ER, "| dust proper time at t = 200 M (R0 = 48 M) | 279.7 M (model 1251 M)", ["279.7", "1251"],
           [0.5 * sum(er["dust_proper_time_R0_48_at_end"]), er["plateau_model_tau_at_200"]], ["es1", "es_ana"],
           "279.7 is the middle of the range 279.49-279.88 over the group's tracers")
    nclaim(ER, "| card-hours | 0.769 | 0.672", ["0.769", "0.672"],
           [man_es["es1"]["resources"]["gpu_hours"], man_es["v1"]["resources"]["gpu_hours"]], ["es1", "v1"])
    nclaim(EJ, "max |drift(ES-1) - drift(V-1)| = 2.04e-4 = 1.49", ["2.04e-4", "1.49"],
           [er["difference"]["max_abs"], er["difference"]["over_control_floor"]], ["es1", "v1", "es_ana"])
    nclaim(EJ, "1.292, 1.662, 1.636 at t = 10, 25, 50 M against", ["1.292", "1.662", "1.636"],
           [lb["t=10"], lb["t=25"], lb["t=50"]], ["es1", "es_ana"])
    nclaim(EJ, "the homogeneous model 1.377, 2.096, 3.577", ["1.377", "2.096", "3.577"],
           [pm["t=10"], pm["t=25"], pm["t=50"]], ["es_ana"])
    nclaim(EJ, "-3H(tau): 1.00 (t = 0), 0.50 (10 M), 0.62 (20 M), 0.19 (30 M), 0.10 (40 M), -0.21 (50 M)",
           ["1.00", "0.50", "0.62", "0.19", "0.10", "-0.21"],
           [er["K_over_minus3H_R0_48"][f"t={T}"] for T in (0, 10, 20, 30, 40, 50)], ["es1", "es_extra"],
           "last digit only: 0.4947 at t = 10 M, printed 0.50")
    nclaim(EJ, "Then ES-1 - V-1 swings between +3.2e-4 and -2.3e-4", ["3.2e-4", "-2.3e-4"],
           [er["difference"]["mass_bubble_minus_control_25_50"][1], er["difference"]["mass_bubble_minus_control_25_50"][0]],
           ["es1", "v1", "es_extra"], "window t = 25-50 M here; the journal names 27-48 M")
    nclaim(EJ, "The two horizon masses agree to 9e-16 until t = 23 M", ["9e-16"],
           [er["difference"]["mass_bubble_minus_control_max_abs_t_le_20"]], ["es1", "v1", "es_extra"],
           f"the masses differ by up to 8.6e-9 for t <= 20 M and by more than 1e-9 from t = "
           f"{er['difference']['t_first_split_1e-9']:.1f} M on; entry 8 (es_runs/JOURNAL.md:520) already corrects it")

    # ---- write ----
    rows = ["% generated from registered run outputs; do not edit"]
    cur = None
    parts = []
    for secname, q, v, runs in E:
        if secname != cur:
            if parts:
                parts.append(r"\end{tabular}\end{ruledtabular}\end{table*}")
            n = len([p for p in parts if p.startswith(r"\begin{table*}")]) + 1
            parts.append(r"\begin{table*}")
            parts.append(rf"\caption{{Numerical ledger, part {n}. {secname}: each value with the registered run that produced it.}}")
            parts.append(rf"\label{{tab:ledger{n}}}")
            parts.append(r"\begin{ruledtabular}\begin{tabular}{p{0.44\textwidth}p{0.19\textwidth}p{0.27\textwidth}}")
            parts.append(r"Quantity & Value & Run \\ \hline")
            cur = secname
        rr = r" \newline ".join(r"\texttt{\scriptsize " + (R[k] if k in R else k.replace("_", r"\_")) + "}" for k in runs)
        parts.append(f"{q} & {tex_num(v)} & {rr} \\\\")
    parts.append(r"\end{tabular}\end{ruledtabular}\end{table*}")
    with open(os.path.join(out, "ledger.tex"), "w") as f:
        f.write("\n".join(rows + parts) + "\n")

    par = [r"% generated from registered run outputs; do not edit",
           r"\begin{table}",
           r"\caption{Parameters of the black hole in a vacuum bubble as constructed, of the vacuum black hole that sets the floor, of the first run of the bubble and its control, of the Newtonian-mode infall, and of the Kerr spike on the analytic metric. Lengths and times in units of the black-hole mass $M$.}",
           r"\label{tab:parameters}",
           r"\begin{ruledtabular}\begin{tabular}{lr}",
           r"\multicolumn{2}{l}{\emph{Black hole in a vacuum bubble}} \\",
           rf"vacuum, time-symmetric, below $R$ & {s['R0']:g} \\",
           rf"innermost dust (wall) $R_{{\rm in}}$ & {s['Rin']:g} \\",
           rf"Sch\"ucking radius $R_w$ & {s['Rw']:g} \\",
           rf"plateau, from--to & {s['Rin'] + 2 * s['w_in']:g}--{s['Rb'] - s['w_out']:g} \\",
           rf"outer dust edge $R_{{\rm out}}$ & {s['Rout']:g} \\",
           rf"plateau Hubble rate $HM$ & {tex_num(fnum(s['H'], 4))} \\",
           rf"dust mass, total mass ($M$) & {s['M_dust']:.3f}, {s['M_total']:.3f} \\",
           rf"particle spacing; dust particles & {es['particles']['hp']:g}; {es['particles']['n_dust']} \\",
           rf"tracer groups $\times$ directions & {len(es['tracers'])} $\times$ {es['particles']['n_tracers'] // len(es['tracers'])} \\",
           r"\multicolumn{2}{l}{\emph{Vacuum black hole}} \\",
           r"finest cell $\Delta x$ & $M/8$, $M/16$ \\",
           rf"outer boundary & {deck['x1max']:g} \\",
           rf"duration & {deck['tlim']:g} \\",
           r"slicing; shift & $1+\log$; Gamma driver \\"]
    # the first run and its control (data run es2_data, deck recorded in the run's manifest)
    es2 = C.load_json("es2_data", "es/es.json")
    s2 = es2["summary"]
    din = [i for i in man_es["es1"]["inputs"] if i["path"].endswith(".athinput")][0]
    dpath = din["path"] if os.path.isabs(din["path"]) else os.path.join(os.path.dirname(os.path.dirname(C.TRACK)), din["path"])
    if C._sha256(dpath) != din["sha256"]:
        raise SystemExit(f"{dpath} differs from the deck the first run recorded")
    d1, block, lev = {}, None, []
    for line in open(dpath):
        line = line.split("#")[0].strip()
        if line.startswith("<"):
            block = line
        elif "=" in line:
            k_, v_ = (x.strip() for x in line.split("=", 1))
            d1[(block, k_)] = v_
            if block.startswith("<refined_region") and k_ == "level":
                lev.append(int(v_))
    root = 2 * float(d1[("<mesh>", "x1max")]) / int(d1[("<mesh>", "nx1")])
    fine = root / 2 ** max(lev)
    par += [r"\multicolumn{2}{l}{\emph{First run and its vacuum control}} \\",
            rf"wall; Sch\"ucking radius; outer dust edge & {s2['Rin']:g}; {s2['Rw']:g}; {s2['Rout']:g} \\",
            rf"plateau Hubble rate $HM$; dust mass ($M$) & {tex_num(fnum(s2['H'], 4))}; {s2['M_dust']:.3f} \\",
            rf"dust particles; tracers & {es2['particles']['n_dust']}; {es2['particles']['n_tracers']} \\",
            rf"root cell; finest cell & {root:g}; $M/{round(1 / fine):d}$ \\",
            rf"outer boundary; duration & {float(d1[('<mesh>', 'x1max')]):g}; {float(d1[('<time>', 'tlim')]):g} \\",
            r"slicing; shift & $1+\log$; Gamma driver \\"]
    # the Newtonian-mode runs (setup.json of each run)
    st = {k: C.load_json(k, "setup.json") for k in ("nm128c", "nm64c", "nm128Lc")}
    par += [r"\multicolumn{2}{l}{\emph{Newtonian-mode infall}} \\",
            rf"initial Hubble rate $\epsilon=H_iM$ & {st['nm128c']['eps']:g} \\",
            rf"seed: particles in a clump of radius & {st['nm128c']['n_clump']}; {st['nm128c']['r_clump']:g} \\",
            rf"dust particles & {st['nm128c']['n_dust']}, {st['nm128Lc']['n_dust']} \\",
            rf"cells & {N1['dx']:g}, {N2['dx']:g}, {N3['dx']:g} \\",
            rf"box half-width & {st['nm128c']['L']:g}, {st['nm64c']['L']:g}, {st['nm128Lc']['L']:g} \\",
            rf"last $a/a_i$ & {st['nm128c']['a_end']:g}, {st['nm64c']['a_end']:g}, {st['nm128Lc']['a_end']:g} \\"]
    ic = C.load_json("kerr_ic", "ic_summary.json")["args"]
    par += [r"\multicolumn{2}{l}{\emph{Kerr spike on the analytic metric}} \\",
            rf"spin $a$; particles; energy cut & {ic['a']:g}; {ic['n']}; {ic['ecut']:g} \\",
            rf"duration & {ks['t_end']:g} \\",
            r"\end{tabular}\end{ruledtabular}",
            r"\end{table}"]
    with open(os.path.join(out, "parameters.tex"), "w") as f:
        f.write("\n".join(par) + "\n")

    with open(os.path.join(out, "claims.json"), "w") as f:
        json.dump(K, f, indent=1)
    md = ["# Numbers of the lead's documents checked against the run outputs",
          "", "Generated by `note/scripts/ledger.py`. Paths relative to `tracks/D-bh-dress/`. "
          "Where a document and a file disagree, the file wins.", "",
          "| Document:line | Stated | In the file | Verdict | Runs | Note |", "|---|---|---|---|---|---|"]
    for k in K:
        md.append(f"| `{k['doc']}:{k['line']}` | {k['stated']} | {k['file_value']} | {k['verdict']} | "
                  f"{', '.join(k['runs'])} | {k['note']} |")
    nd = [k for k in K if k["verdict"] != "agrees"]
    md += ["", f"{len(K)} statements checked; {len(K) - len(nd)} agree; {len(nd)} need a remark: "
           + "; ".join(f"`{k['doc']}:{k['line']}` ({k['verdict']})" for k in nd) + "."]
    with open(os.path.join(out, "claims.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[-1:]))
    missing = [k for k in K if k["line"] is None]
    if missing:
        print("ledger: claim text not found in its document:", [k["stated"] for k in missing])
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
