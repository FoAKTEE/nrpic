"""Numerical ledger of the note and the check of the lead's documents against the files.

Reads only registered run outputs (common.RUNS, each file checked against its run's
sha256sums.txt where the run wrote one) and, for the claims, the committed text of the
track's documents (to give each claim a file:line locator). Writes
  ../tables/ledger.tex   the ledger appendix of the note (every number with its run id)
  ../tables/claims.md    each checked claim: document locator, claimed, file value, verdict
  ../tables/claims.json  the same as data
or the same three files into --out DIR.
A claim agrees when the file value, rounded to the digits the document prints, equals the
printed value; "to X" bounds agree when the value rounds to X at one significant digit.
"""
import csv
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

TRACK = os.path.dirname(common.NOTE)


def locate(doc, needle):
    path = os.path.join(TRACK, doc)
    if not os.path.isfile(path):
        return f"{doc}: (file missing)"
    for i, line in enumerate(open(path, errors="replace"), 1):
        if needle in line:
            return f"{doc}:{i}"
    return f"{doc}: (text not found)"


def decimals(s):
    s = s.strip().lstrip("-")
    if "e" in s.lower():
        return None
    return len(s.split(".")[1]) if "." in s else 0


def agrees(value, claimed, mode):
    if mode == "digits":
        n = decimals(claimed)
        return round(value, n) == round(float(claimed), n)
    if mode == "sig1":   # "to X": same order and leading digit
        if value == 0:
            return True
        return float(f"{value:.0e}") == float(claimed)
    if mode == "upper":  # value at most the claimed bound
        return value <= float(claimed)
    if mode == "range":  # claimed "a-b": min and max rounded agree
        lo, hi = claimed.split("-")
        return (round(value[0], decimals(lo)) == float(lo)
                and round(value[1], decimals(hi)) == float(hi))
    if mode == "exact":
        return value == claimed
    raise ValueError(mode)


def main():
    out = common.out_dir("tables")
    S = common.load_json("scope", "scope/scope_numbers.json")
    CS = common.load_json("criteria_scan", "scan_summary.json")
    CC = common.load_json("criteria_check", "results.json")
    CV = common.load_json("convergence", "convergence.json")["models"]
    C5 = common.load_json("convergence512", "convergence.json")["models"]
    X = common.load_json("crosscheck", "crosscheck.json")
    B = common.load_json("ball_exact", "exact.json")
    P = common.load_json("scouting", "scouting_predictions.json")
    CW = common.load_json("criteria_w2", "results.json")["checks"]
    CW2 = common.load_json("criteria_w2_t2", "results.json")["checks"]
    SB = common.load_json("ball_runs", "summary.json")["table"]
    NB = {lab: common.load_json("ball_runs_w2", f"{lab}_numbers.json") for lab in ("sr1_n128", "sr1_n256", "sr2_n256")}
    NW = common.load_json("newton", "newton_results.json")
    with open(common.run_file("newton_range", "gr_scan_range.csv")) as f:
        GR = list(csv.DictReader(f))
    D0 = common.load_json("dataset2t", "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875.json")["model"]
    R = common.RUNS

    def order(models, model, key):
        return models[model]["orders"][key][-1]

    t3 = {q: {round(r["RbH_i"], 3): r for r in S["T3"][q]} for q in ("q2", "q3", "q4")}
    ratios = [r for mu, r in zip(S["T2"]["mu"], S["T2"]["ratio_read_to_tc_rm"]) if mu <= 0.15]
    tcr = dict(zip(S["T2"]["mu"], S["T2"]["t_c_rm"]))
    fails = [c["id"] for c in CC["checks"] if not c["passed"]]
    # wave-2 state of the criteria checks: T1, T3-T5 of the full run, T2 of the rerun after its fix;
    # passed None marks a diagnostic without a verdict (a wave-1 check kept for the record)
    cw1 = [c for c in CW if not c["id"].startswith("T2")]
    tally = {k: (sum(c["passed"] is True for c in cs), sum(c["passed"] is not None for c in cs),
                 sum(c["passed"] is None for c in cs)) for k, cs in (("w2", cw1), ("w2_t2", CW2))}
    # units of the scouting data: nominal mass of the untapered Einstein-de Sitter ball
    M0 = 0.5 * D0["H"] ** 2 * D0["Rb"] ** 3
    MM0 = D0["M_misner_sharp"] / M0
    # wave-2 runs of the expanding ball (SR-1 geodesic, SR-2 conformal-time slicing)
    sb = {r["label"]: r for r in SB}
    sr1 = [sb[k] for k in ("sr1_n128", "sr1_n256", "sr1_n256L32")]
    sr2 = [sb[k] for k in ("sr2_n128", "sr2_n256", "sr2_n256L32")]
    # Newtonian mode: top hat at 32^3, 64^3, 128^3 (2.7e5 particles) and the 14 scan points
    tq = ("t_ta_rel", "R_max_rel", "t_0.25_rel", "t_min_rel")
    tht = {t["name"]: t for t in NW["tophat"]}
    th1 = [tht[f"th_n{n:03d}_h025"] for n in (32, 64, 128)]
    conv = [th1[i][q] / th1[i + 1][q] for q in tq for i in (0, 1)]
    sc = NW["scan"]
    main_pts = [x for x in sc if x["nx"] == 128 and x["n"] >= 2.6e5 and not x["name"].endswith("_pm")]
    t1m = [x["t1_vertex_rel"] for x in main_pts]
    h1m = [abs(x["h1_rel"]) for x in main_pts]
    spindle = [x for x in sc if x["name"] == "e0p2_pm"][0]
    c64 = [x["t1_vertex_rel"] for x in sc if x["nx"] == 64]
    cfew = [x["t1_vertex_rel"] for x in sc if x["n"] < 1e5]
    e09 = max(x["E_err_max_to_0p9t1"] for x in sc if x["nx"] == 128)
    ecross = [x["E_err_max_to_t1"] for x in sc if x["nx"] == 128 and x is not spindle]
    gr0 = {round(float(r["e"]), 2): float(r["deltaL_th_ref"]) for r in GR if abs(float(r["p"])) < 1e-9}

    def sig(v, n=2):     # signed, two significant digits, exponent without a leading zero
        return f"{v:+.{n - 1}e}".replace("e-0", "e-").replace("e+0", "e")

    def sci(v, n=2):     # unsigned, the same
        return f"{v:.{n - 1}e}".replace("e-0", "e-").replace("e+0", "e")
    rows_ch = [r["card_hours"] for r in S["T5"]["rows"]]
    th = CS["thresholds_sigmaH_0.01"]
    L2max = max(X["L2"][k]["max_all"] for k in ("u", "KL", "KT", "betar"))
    L3max = max(X["L3"][k] for k in ("u", "KL", "KT", "alpha", "betar"))
    inv = P["invariant"]

    # ------------------------------------------------------------------ ledger rows
    # (group, quantity (LaTeX), value string, run key)
    L = []
    g = "Threshold landscape"
    L += [(g, r"Zel'dovich-hoop amplitude $\hat h(0.2,0)$", f"{S['T1']['h_hat_0.2_0']:.3f}", "scope"),
          (g, r"largest deviation of $\hat h$ from the values read off Ref.~\cite{Yoo:2026mdpbh}",
           f"{S['T1']['max_abs_dev_readoff']:.4f}", "scope"),
          (g, r"top-hat amplitude $\mu_{\rm fd}$ for $t_{\rm end}=100,250,400,1000\,t_H$",
           ", ".join(f"{S['T2'][k]:.3f}" for k in ("mu_fd_100", "mu_fd_250", "mu_fd_400", "mu_fd_1000")),
           "scope"),
          (g, r"slope of the read-off collapse times against $\mu$", f"{S['T2']['slope']:.2f}", "scope"),
          (g, r"read-off collapse time over top-hat time at $r_m$, $\mu\le0.15$ (range; median); "
              r"median over all six read-offs",
           f"{min(ratios):.2f}--{max(ratios):.2f}; {statistics.median(ratios):.2f}; {S['T2']['median_ratio']:.2f}",
           "scope"),
          (g, r"largest $\mu$ in the ball, $R_bH_i=0.9$, $R_b=2,3,4\,r_m$ (mean contrast $0.3$)",
           ", ".join(f"{t3[q][0.9]['mu_max_mean03']:.3f}" for q in ("q2", "q3", "q4")), "scope"),
          (g, r"the same with the central contrast at most $0.3$",
           ", ".join(f"{t3[q][0.9]['mu_max_centre03']:.4f}" for q in ("q2", "q3", "q4")), "scope"),
          (g, r"critical dispersion $s$: virial halt; crossing time",
           f"{S['T4']['s_c_virial']:.2f}; {S['T4']['s_c_2211']:.1f}", "scope"),
          (g, r"measured cost of the two-overdensity run (card-hours; s per cycle)",
           f"{S['T5']['v19']['card_hours']:.2f}; {S['T5']['v19']['s_per_cycle']:.3f}", "scope"),
          (g, r"modelled cost per run (range; median at $10^6$ particles), card-hours",
           f"{min(rows_ch):.1f}--{max(rows_ch):.1f}; {S['T5']['typical_run_card_hours_1e6']:.1f}", "scope"),
          (g, r"first scan: runs; card-hours", f"{S['T5']['n_runs_first_scan']}; {S['T5']['scan_card_hours']:.0f}",
           "scope")]
    g = "Analytic criteria"
    names = [("R1 hoop ball (1609.01588)", "hoop (ball)"), ("R2 hoop peak (2508.10070)", "hoop (peak)"),
             ("R9 top hat (2507.18312)", "profile"), ("R8 dispersion (2211.13950)", "dispersion"),
             ("R3 Kerr bound (1707.03595)", "spin"), ("R4 duration (1707.03595)", "duration")]
    L += [(g, r"threshold $\delta_c$ at $e=0.2$: " + "; ".join(n for _, n in names),
           "; ".join(f"{th[k][2]:.3g}" for k, _ in names), "criteria_scan"),
          (g, r"particle threshold of Ref.~\cite{Yoo:2026mdpbh} in the same measure",
           f"{CS['particle_2609_delta_at_e0.2']:.3f}", "criteria_scan"),
          (g, "first check run against the five papers: passed of total; failing",
           f"{len(CC['checks']) - len(fails)} of {len(CC['checks'])}; " + ", ".join(fails), "criteria_check"),
          (g, "checks of the hoop, dispersion, profile and peak criteria: passed of total; kept as diagnostics",
           f"{tally['w2'][0]} of {tally['w2'][1]}; {tally['w2'][2]}", "criteria_w2"),
          (g, "checks of the spin and duration criteria: passed of total; kept as diagnostics",
           f"{tally['w2_t2'][0]} of {tally['w2_t2'][1]}; {tally['w2_t2'][2]}", "criteria_w2_t2")]
    g = "Initial data"
    L += [(g, r"order of $\|\mathcal M\|_2$, flat ball, smooth cells, differences of order 2; 4",
           f"{order(CV, 'flat', 'p2/smooth/M_L2'):.2f}; {order(CV, 'flat', 'p4/smooth/M_L2'):.2f}", "convergence"),
          (g, r"order of $\|\mathcal M\|_2$, tapered edge, all cells, order 2; 4",
           f"{order(CV, 'flat_taper', 'p2/all/M_L2'):.2f}; {order(CV, 'flat_taper', 'p4/all/M_L2'):.2f}",
           "convergence"),
          (g, r"order of $\|\mathcal H\|_2$; $\|\mathcal M\|_2$, top hat, smooth cells, order 4",
           f"{order(CV, 'tophat', 'p4/smooth/H_L2'):.2f}; {order(CV, 'tophat', 'p4/smooth/M_L2'):.2f}",
           "convergence"),
          (g, r"order of $\|\mathcal M\|_2$, top hat, all cells, order 4",
           f"{order(CV, 'tophat', 'p4/all/M_L2'):.2f}", "convergence"),
          (g, r"order of $\|\mathcal H\|_2$; $\|\mathcal M\|_2$, smoothed top hat, $N=256\to512$",
           f"{order(C5, 'smooth_tophat', 'p4/smooth/H_L2'):.2f}; {order(C5, 'smooth_tophat', 'p4/smooth/M_L2'):.2f}",
           "convergence512"),
          (g, "largest difference of two independent generators (flat ball)", f"{L2max:.1e}", "crosscheck"),
          (g, "largest difference of two table evaluators", f"{L3max:.1e}", "crosscheck"),
          (g, "largest difference of three exact-solution codes (times)", f"{X['L4']['max_disagreement']:.1e}",
           "crosscheck"),
          (g, r"exterior $K$ against $-\tfrac32\sqrt{2M/R^3}$, largest relative difference",
           f"{X['L6']['max_rel']:.1e}", "crosscheck")]
    g = "Exact solution of the scouting data"
    ft, core, mod = B["first_trapped"], B["core"], B["model"]
    L += [(g, r"total mass $M/M_0$; rest mass$/M_0$", f"{mod['M']:.5f}; {mod['rest_mass']:.5f}", "ball_exact"),
          (g, r"core turnaround $\tau_{\rm ta}/M_0$; $R_{\max}/R_i$", f"{core['tau_ta']:.3f}; {core['R_max_over_R_i']:.4f}",
           "ball_exact"),
          (g, r"first trapped sphere $\tau_{\rm AH}/M_0$; shell $R_i/M_0$; $m_{\rm AH}/M_0$; areal radius$/M_0$",
           f"{ft['tau']:.3f}; {ft['R_i']:.3f}; {ft['m']:.4f}; {ft['R']:.3f}", "ball_exact"),
          (g, r"core edge trapped; crunch of the core ($\tau/M_0$)", f"{core['tau_ah_edge']:.3f}; {core['tau_c']:.3f}",
           "ball_exact"),
          (g, r"$m_{\rm AH}/M_0$ at the crunch", f"{B['m_ah']['m'][-1]:.4f}", "ball_exact"),
          (g, r"in units of the total mass: $\tau_{\rm ta}/M$; $m_{\rm AH}/M$ at first trapping and at the crunch",
           f"{core['tau_ta'] / MM0:.2f}; {ft['m'] / MM0:.4f}; {B['m_ah']['m'][-1] / MM0:.4f}", "ball_exact"),
          (g, r"conformal-time coordinate times: turnaround, core at $\tau_{\rm AH}$, crunch",
           ", ".join(f"{P['SR2_conformal_time']['coordinate_times'][k]:.2f}"
                     for k in ("core_turnaround", "core_at_first_trapped_tau", "core_crunch")), "scouting"),
          (g, r"geodesic slicing reaches the step bound at ${\rm cfl}=0.25$ ($\tau/M_0$; light speed $R_i/R$, "
              r"without the conformal factor)",
           f"{P['SR1_geodesic']['tau_where_cfl_0p25_reaches_limit']:.2f}", "scouting"),
          (g, "predicted card-hours of the two scouting runs",
           f"{P['SR1_geodesic']['card_hours']:.2f}; {P['SR2_conformal_time']['card_hours']:.2f}", "scouting")]
    g = "Newtonian limit"
    tt = tht["th_n128_h025"]
    L += [(g, r"top hat, $128^3$ cells, $2.7\times10^5$ particles: relative error of the turnaround time; "
              r"largest radius; time at a quarter of it; softened collapse",
           "; ".join(sig(tt[q]) for q in tq), "newton"),
          (g, r"the same four errors: reduction per doubling of the mesh, $32^3\to64^3\to128^3$ (range)",
           f"{min(conv):.1f}--{max(conv):.1f}", "newton"),
          (g, r"top hat, $128^3$: largest relative energy error", sci(tt["E_err_max"]), "newton"),
          (g, r"first collapse against the homogeneous ellipsoid, the " + str(len(main_pts)) +
              r" points at $128^3$ with at least $2.7\times10^5$ particles other than the spindle: "
              r"relative error of $t_1$ (range); of the hoop ratio (largest)",
           f"{sig(min(t1m))} to {sig(max(t1m))}; {sci(max(h1m))}", "newton"),
          (g, r"scan points whose first collapse is along the predicted axis",
           f"{sum(bool(x['axis_match']) for x in sc)} of {len(sc)}", "newton"),
          (g, r"the same for the spindle ($p=-e$); the $64^3$ controls; the $3.4\times10^4$-particle controls",
           f"{sig(spindle['t1_vertex_rel'])}; " + ", ".join(sig(v) for v in sorted(c64)) + "; "
           + ", ".join(sig(v) for v in sorted(cfew)), "newton"),
          (g, r"relative energy error to $0.9\,t_1$ (largest); at the first crossing (range); spindle",
           f"{sci(e09)}; {sci(min(ecross))} to {sci(max(ecross))}; {sci(spindle['E_err_max_to_t1'])}", "newton"),
          (g, r"Newtonian hoop amplitude $\delta_{L,\rm th}$ at $e=0.05,0.1,0.2,0.3$ ($p=0$)",
           ", ".join(f"{gr0[e]:.3f}" for e in (0.05, 0.1, 0.2, 0.3)), "newton_range")]
    g = "First evolutions of the scouting data"
    co = NB["sr1_n256"]["sr1_coordinates"]
    L += [(g, r"geodesic slicing, $\Delta x=M_0/2$: largest $|r/r_0-1|$ of the tracked particles; largest "
              r"$|\tau-t|/M_0$", f"{sci(co['max_abs_r_over_r0_minus_1'])}; {sci(co['max_abs_tau_minus_t'])}",
           "ball_runs_w2"),
          (g, r"core shells, largest $|R/R_{\rm exact}-1|$ at $\tau=16.9\,M_0$, geodesic slicing, "
              r"$\Delta x=M_0,\,M_0/2,\,M_0/4$ (the last with half the box)",
           ", ".join(sci(r["eps_core_tau16_9_max"]) for r in sr1), "ball_runs"),
          (g, r"the same, conformal-time slicing", ", ".join(sci(r["eps_core_tau16_9_max"]) for r in sr2),
           "ball_runs"),
          (g, r"core turnaround, mean proper-time error$/M_0$, geodesic slicing, $\Delta x=M_0/2,\,M_0/4$",
           ", ".join(f"{r['tau_ta_err_mean']:+.4f}" for r in sr1[1:]), "ball_runs"),
          (g, r"the same, conformal-time slicing, from the vertex of three records of $R(\tau)$ "
              r"(depends on the estimator)",
           ", ".join(f"{r['tau_ta_err_mean']:+.4f}" for r in sr2[1:]), "ball_runs"),
          (g, r"geodesic slicing: largest $|\mathcal H|$ on the mesh at $t=20\,M_0$, $\Delta x=M_0,\,M_0/2,\,M_0/4$",
           ", ".join(f"{r['H_max_t20']:.2g}" for r in sr1), "ball_runs"),
          (g, r"geodesic slicing: first non-finite line output, $t/M_0$ at $\Delta x=M_0,\,M_0/2$",
           f"{NB['sr1_n128']['lines_nonfinite']['first_t']:g}; {NB['sr1_n256']['lines_nonfinite']['first_t']:g}",
           "ball_runs_w2"),
          (g, r"conformal-time slicing: central lapse off the exact core value by more than a tenth from "
              r"$t/M_0$, $\Delta x=M_0,\,M_0/2,\,M_0/4$",
           ", ".join(f"{r['t_lapse_dev_gt_0p1']:g}" for r in sr2), "ball_runs"),
          (g, r"conformal-time slicing, $\Delta x=M_0/2$: largest relative departure of the central lapse from "
              r"the scale factor of the core up to $t=15\,M_0$",
           f"{NB['sr2_n256']['history']['lapse_dev_maxabs_t_le_15']:.2f}", "ball_runs_w2"),
          (g, r"conformal-time slicing, $\Delta x=M_0/2$: largest $2m/R$ on the axes; apparent horizons found",
           f"{NB['sr2_n256']['line_compactness']['max']:.2f}; {NB['sr2_n256']['finder']['n']}", "ball_runs_w2")]

    # ------------------------------------------------------------------ parameter table
    D = common.load_json("dataset2t", "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875.json")
    dm, da = D["model"], D["args"]
    # the outcome rule of scope/SCOPE.md section 3 (lines 94-116): design constants, no run
    par = [("Scouting data: expanding ball with a bound core", None),
           (r"unit: mass $M_0=\tfrac12H^2R_b^3$ of the untapered ball", f"{0.5 * dm['H'] ** 2 * dm['Rb'] ** 3:g}"),
           (r"total (Misner--Sharp) mass $M/M_0$; rest mass$/M_0$", f"{dm['M_misner_sharp']:.4f}; {dm['rest_mass']:.4f}"),
           (r"envelope: $HR_b$; ball radius $R_b/M_0$; Hubble rate $HM_0$; start $t_i/M_0$",
            f"{dm['HRb']:g}; {dm['Rb']:g}; {dm['H']:g}; {dm['t_i']:.3f}"),
           (r"core: mean contrast $\Delta$ inside $R/M_0$; compensated at $R/M_0$",
            f"{dm['delta_c']:g}; {dm['R1']:g}; {dm['R2']:g}"),
           (r"edge taper: half width$/M_0$; matter edge$/M_0$", f"{dm['edge_width']:g}; {dm['rbar_matter']:g}"),
           (r"conformal factor at the centre; largest $2m/R$ on the slice",
            f"{dm['psi_centre']:.4f}; {dm['max_2m_over_R']:.3f}"),
           (r"particle lattice spacing$/M_0$", f"{2 * dm['rbar_matter'] / da['nlat']:g}"),
           ("Outcome rule and threshold bracket (design)", None),
           ("consecutive horizon searches; their span in units of the horizon mass", "3; 5"),
           (r"constraint bound: $\|\Ham\|_2$ over $\|16\pi E\|_2$ outside the horizon", "0.1"),
           (r"bracket ratio $A_{\rm hi}/A_{\rm lo}$ at the end of the bisection", "1.1"),
           (r"primary end time; continuation of the run below threshold ($t_H$)", "250; 1000")]
    ptex = [r"\begin{table*}", r"\caption{Parameters of the scouting data and of the outcome rule. Lengths, times "
            r"and masses of the scouting data are in units of $M_0$, the mass of the untapered ball.}",
            r"\label{tab:parameters}", r"\begin{ruledtabular}", r"\begin{tabular}{p{0.62\textwidth}l}"]
    for q, v in par:
        ptex.append(rf"\multicolumn{{2}}{{l}}{{\emph{{{q}}}}} \\" if v is None else rf"{q} & {v} \\")
    ptex += [r"\end{tabular}", r"\end{ruledtabular}", r"\end{table*}"]
    with open(os.path.join(out, "parameters.tex"), "w") as f:
        f.write("% generated from registered run outputs; do not edit\n")
        f.write("\n".join(ptex) + "\n")
    L += [("Parameters", r"scouting data of Table~\ref{tab:parameters}", "see table", "dataset2t")]

    # three floats, so that each fits on a page
    parts = [((r"Numerical ledger. Every number of this note with the registered run that produced it: "
               r"scoping and offline tests."), "tab:ledger",
              ("Threshold landscape", "Analytic criteria", "Initial data")),
             (r"Numerical ledger (continued): exact solution and Newtonian limit.", "tab:ledger2",
              ("Exact solution of the scouting data", "Newtonian limit")),
             (r"Numerical ledger (continued): first evolutions in full general relativity.", "tab:ledger3",
              ("First evolutions of the scouting data", "Parameters"))]
    assert {grp for grp, *_ in L} == {g for *_, gs in parts for g in gs}
    tex = []
    for cap, lab, groups in parts:
        tex += [r"\begin{table*}", rf"\caption{{{cap}}}", rf"\label{{{lab}}}", r"\begin{ruledtabular}",
                r"\begin{tabular}{p{0.44\textwidth}p{0.22\textwidth}l}", r"Quantity & Value & Run \\", r"\hline"]
        last = None
        for grp, q, v, key in L:
            if grp not in groups:
                continue
            if grp != last:
                tex.append(rf"\multicolumn{{3}}{{l}}{{\emph{{{grp}}}}} \\")
                last = grp
            tex.append(rf"{q} & {v} & \texttt{{\footnotesize {R[key]}}} \\")
        tex += [r"\end{tabular}", r"\end{ruledtabular}", r"\end{table*}", ""]
    with open(os.path.join(out, "ledger.tex"), "w") as f:
        f.write("% generated from registered run outputs; do not edit\n")
        f.write("\n".join(tex) + "\n")

    # ------------------------------------------------------------------ claims
    C = []

    def claim(doc, needle, what, value, claimed, mode, run_key):
        C.append(dict(doc=locate(doc, needle), what=what, claimed=claimed,
                      file_value=value if not isinstance(value, float) else float(f"{value:.6g}"),
                      run=R[run_key], agrees=bool(agrees(value, claimed, mode)), mode=mode))

    st, g1, sc, jo, rb = "STATUS.md", "stage/G1/STATUS.md", "scope/SCOPE.md", "JOURNAL.md", "runs_ball/JOURNAL.md"
    claim(st, "core turnaround tau = 16.894", "core turnaround tau", inv["core_tau_turnaround"], "16.894", "digits", "scouting")
    claim(st, "first trapped sphere tau = 44.349", "first trapped tau", inv["first_trapped"]["tau"], "44.349", "digits", "scouting")
    claim(st, "(R_i = 2.742, m = 0.0805)", "first trapped R_i", inv["first_trapped"]["R_i"], "2.742", "digits", "scouting")
    claim(st, "(R_i = 2.742, m = 0.0805)", "first trapped m", inv["first_trapped"]["m"], "0.0805", "digits", "scouting")
    claim(st, "crunch 44.454", "crunch", inv["core_crunch_tau"], "44.454", "digits", "scouting")
    claim(st, "SR-1 0.15, SR-2 0.16 card-hours", "SR-1 card-hours", P["SR1_geodesic"]["card_hours"], "0.15", "digits", "scouting")
    claim(st, "SR-1 0.15, SR-2 0.16 card-hours", "SR-2 card-hours", P["SR2_conformal_time"]["card_hours"], "0.16", "digits", "scouting")
    claim(st, "generators agree to 5e-15", "two generators agree to", L2max, "5e-15", "sig1", "crosscheck")
    claim(st, "table rules to 7e-18", "two table rules agree to", L3max, "7e-18", "sig1", "crosscheck")
    claim(st, "three codes to 1e-14", "three exact codes agree to", X["L4"]["max_disagreement"], "1e-14", "sig1", "crosscheck")
    claim(g1, "flat ball momentum orders 2.00, 4.00", "flat ball M order 2", order(CV, "flat", "p2/smooth/M_L2"), "2.00", "digits", "convergence")
    claim(g1, "flat ball momentum orders 2.00, 4.00", "flat ball M order 4", order(CV, "flat", "p4/smooth/M_L2"), "4.00", "digits", "convergence")
    for q in ("H", "M"):
        claim(g1, "compensated top-hat 2.00/4.00", f"top hat {q} order 2 (smooth)", order(CV, "tophat", f"p2/smooth/{q}_L2"), "2.00", "digits", "convergence")
        claim(g1, "compensated top-hat 2.00/4.00", f"top hat {q} order 4 (smooth)", order(CV, "tophat", f"p4/smooth/{q}_L2"), "4.00", "digits", "convergence")
    claim(g1, "C^4 edge taper 1.99/3.90", "taper M order 2 (all cells)", order(CV, "flat_taper", "p2/all/M_L2"), "1.99", "digits", "convergence")
    claim(g1, "C^4 edge taper 1.99/3.90", "taper M order 4 (all cells)", order(CV, "flat_taper", "p4/all/M_L2"), "3.90", "digits", "convergence")
    claim(g1, "3.98 (H) and 3.94 (M)", "smoothed top hat H order 4, N=512", order(C5, "smooth_tophat", "p4/smooth/H_L2"), "3.98", "digits", "convergence512")
    claim(g1, "3.98 (H) and 3.94 (M)", "smoothed top hat M order 4, N=512", order(C5, "smooth_tophat", "p4/smooth/M_L2"), "3.94", "digits", "convergence512")
    claim(g1, "37 checks against printed numbers", "criteria checks passed", len(CC["checks"]) - len(fails), 33, "exact", "criteria_check")
    claim(g1, "four failures are on record", "criteria failing ids", ", ".join(fails), "T1.2b, T2.2d, T2.4a, T2.4c", "exact", "criteria_check")
    claim(g1, "41 of 41 checks pass", "criteria checks passed (wave 2)", tally["w2"][0] + tally["w2_t2"][0], 41,
          "exact", "criteria_w2")
    claim(g1, "41 of 41 checks pass", "criteria checks in all (wave 2)", tally["w2"][1] + tally["w2_t2"][1], 41,
          "exact", "criteria_w2")
    claim(g1, "the 9 scan points at 128^3", "Newtonian scan points in the band", len(main_pts), 9, "exact", "newton")
    claim(g1, "| 16.894 | 16.894 | 13.82 |", "SR-2 coordinate turnaround", P["SR2_conformal_time"]["coordinate_times"]["core_turnaround"], "13.82", "digits", "scouting")
    claim(g1, "| 44.454 | 44.454 | 54.96 |", "SR-2 coordinate crunch", P["SR2_conformal_time"]["coordinate_times"]["core_crunch"], "54.96", "digits", "scouting")
    claim(sc, "h-hat(0.2, 0) = 0.452", "h-hat(0.2, 0)", S["T1"]["h_hat_0.2_0"], "0.452", "digits", "scope")
    claim(sc, "(slope -1.31)", "slope of read-off times", S["T2"]["slope"], "-1.31", "digits", "scope")
    claim(sc, "0.80-1.01 of the top-hat", "read-off/top-hat range, mu <= 0.15", (min(ratios), max(ratios)), "0.80-1.01", "range", "scope")
    claim(sc, "is mu_fd = 0.048 (0.044", "mu_fd(250 t_H)", S["T2"]["mu_fd_250"], "0.048", "digits", "scope")
    claim(sc, "is mu_fd = 0.048 (0.044", "mu_fd scaled by measured ratio", S["T2"]["mu_fd_250_scaled"], "0.044", "digits", "scope")
    claim(sc, "0.86 t_c(r_m) = 239 t_H", "horizon time of mu = 0.045 (t_H)", S["T2"]["median_ratio"] * S["T2"]["t_c_rm_mu0.045"], "239", "digits", "scope")
    tc04 = tcr[0.05] * (0.05 / 0.04) ** 1.5      # top-hat collapse time scales as mu^(-3/2)
    claim(sc, "  285 t_H; if it fails", "horizon time of mu = 0.04 (t_H)", S["T2"]["median_ratio"] * tc04, "285", "digits", "scope")
    claim(sc, "mu <= 0.031 (q = 3)", "ball capacity q = 3, R_b H_i = 0.9", t3["q3"][0.9]["mu_max_mean03"], "0.031", "digits", "scope")
    claim(sc, "mu <= 0.069 (q = 2)", "ball capacity q = 2, R_b H_i = 0.9", t3["q2"][0.9]["mu_max_mean03"], "0.069", "digits", "scope")
    claim(sc, "2.7 times less", "mean over central capacity", t3["q3"][0.9]["mu_max_mean03"] / t3["q3"][0.9]["mu_max_centre03"], "2.7", "digits", "scope")
    claim(sc, "checked to 2e-4", "mean-contrast formula error", S["T2"]["mean_contrast_formula_max_err"], "2e-4", "sig1", "scope")
    claim(sc, "between 0.55 (virial", "critical s, virial", S["T4"]["s_c_virial"], "0.55", "digits", "scope")
    claim(sc, "took 5.41 card-hours", "cost of the v19 run", S["T5"]["v19"]["card_hours"], "5.41", "digits", "scope")
    claim(sc, "took 5.41 card-hours, 0.761 s", "seconds per cycle", S["T5"]["v19"]["s_per_cycle"], "0.761", "digits", "scope")
    claim(sc, "1.1 to 3.5 card-hours per run", "modelled cost range", (min(rows_ch), max(rows_ch)), "1.1-3.5", "range", "scope")
    claim(sc, "2.4 at 10^6 particles", "median cost at 1e6", S["T5"]["typical_run_card_hours_1e6"], "2.4", "digits", "scope")
    claim(sc, "about 155 card-hours", "first scan card-hours", S["T5"]["scan_card_hours"], "155", "digits", "scope")
    claim(sc, "giving 1.0e-7 s per particle", "s per particle and step", S["T5"]["c_p_s_per_particle_step"], "1.0e-7", "sig1", "scope")
    claim(jo, "turnaround 9.542048138750", "L4 turnaround (three codes)", X["L4"]["cycloid"]["tau_ta"], "9.542048138750", "digits", "crosscheck")
    claim(jo, "R = 2M at 25.407847821", "L4 trapping", X["L4"]["cycloid"]["tau_ah"], "25.407847821", "digits", "crosscheck")
    claim(jo, "crunch 26.897059616", "L4 crunch", X["L4"]["cycloid"]["tau_c"], "26.897059616", "digits", "crosscheck")
    claim(jo, "y = 0.746379", "L5 y", X["L5"]["y"], "0.746379", "digits", "crosscheck")
    claim(jo, "R_max/R_i = 1.33980", "L5 R_max/R_i", X["L5"]["R_max_over_R_i"], "1.33980", "digits", "crosscheck")
    claim(jo, "tau_ta = 16.8938", "L5 tau_ta", X["L5"]["tau_ta"], "16.8938", "digits", "crosscheck")
    claim(jo, "tau_c = 44.4542", "L5 tau_c", X["L5"]["tau_c"], "44.4542", "digits", "crosscheck")
    claim(jo, "core edge trapped at 44.3815", "L5 core edge trapped", X["L5"]["tau_ah_core_edge"], "44.3815", "digits", "crosscheck")
    claim(jo, "below 4.3e-15", "L6 exterior K", X["L6"]["max_rel"], "4.3e-15", "upper", "crosscheck")
    claim(jo, "M = 1.00959", "L7 total mass", mod["M"], "1.00959", "digits", "ball_exact")
    claim(jo, "1.01590", "L7 rest mass", mod["rest_mass"], "1.01590", "digits", "ball_exact")
    claim(jo, "L8 holds within 0.17 per cent", "L8 largest relative deviation (per cent)", 100 * max(P["L8_rel_dev"].values()), "0.17", "digits", "scouting")
    claim(jo, "times 13.823 (turnaround)", "L8 conformal turnaround", P["SR2_conformal_time"]["coordinate_times"]["core_turnaround"], "13.823", "digits", "scouting")
    claim(jo, "49.506 (core at tau", "L8 conformal core at tau_AH", P["SR2_conformal_time"]["coordinate_times"]["core_at_first_trapped_tau"], "49.506", "digits", "scouting")
    claim(jo, "54.964 (crunch)", "L8 conformal crunch", P["SR2_conformal_time"]["coordinate_times"]["core_crunch"], "54.964", "digits", "scouting")
    claim(jo, "at cfl 0.25 at tau = 42.30", "L8 cfl 0.25 limit", P["SR1_geodesic"]["tau_where_cfl_0p25_reaches_limit"], "42.30", "digits", "scouting")
    # the recorded edge deviation of the table cubic, in units of H, against "about 0.1 H"
    claim(jo, "of about 0.1 H", "L3 KL deviation at the sharp edge (units of H)",
          X["L3"]["KL_overshoot_near_edge"] / X["L2"]["H_core"], "0.1", "digits", "crosscheck")
    claim(rb, "tau = 16.893769", "runs_ball turnaround", core["tau_ta"], "16.893769", "digits", "ball_exact")
    claim(rb, "R_max/R_i = 1.339803", "runs_ball R_max/R_i", core["R_max_over_R_i"], "1.339803", "digits", "ball_exact")
    claim(rb, "tau = 44.349266", "runs_ball first trapped", ft["tau"], "44.349266", "digits", "ball_exact")
    claim(rb, "R_i = 2.74175", "runs_ball first trapped R_i", ft["R_i"], "2.74175", "digits", "ball_exact")
    claim(rb, "m = 0.080505", "runs_ball first trapped m", ft["m"], "0.080505", "digits", "ball_exact")
    claim(rb, "core edge trapped 44.381466", "runs_ball core edge", core["tau_ah_edge"], "44.381466", "digits", "ball_exact")
    claim(rb, "44.454205", "runs_ball crunch", core["tau_c"], "44.454205", "digits", "ball_exact")
    claim(rb, "0.0805 to 0.0960", "runs_ball m_AH at crunch", B["m_ah"]["m"][-1], "0.0960", "digits", "ball_exact")
    # two exact references of the same data set (lead's run against runs_ball's run)
    C.append(dict(doc=locate(rb, "the lead's numbers (A-20261115-130948-5a2b58a)"), what="first trapped R_i: lead's run vs runs_ball's run",
                  claimed="equal to the printed digits", file_value=f"{inv['first_trapped']['R_i']:.6f} vs {ft['R_i']:.6f}",
                  run=f"{R['scouting']} / {R['ball_exact']}",
                  agrees=round(inv["first_trapped"]["R_i"], 3) == round(ft["R_i"], 3), mode="digits"))

    n_bad = sum(not c["agrees"] for c in C)
    md = ["# Claims of the lead's documents checked against the run outputs", "",
          "Written by `note/scripts/ledger.py`; a claim agrees when the file value rounded to the printed",
          "digits equals the printed value (`sig1`: same leading digit; `upper`: at most the bound).", "",
          f"{len(C)} claims, {len(C) - n_bad} agree, {n_bad} disagree.", "",
          "| Document | Quantity | Claimed | File value | Run | Agrees |", "|---|---|---|---|---|---|"]
    for c in C:
        md.append(f"| {c['doc']} | {c['what']} | {c['claimed']} | {c['file_value']} | {c['run']} | "
                  f"{'yes' if c['agrees'] else '**no**'} |")
    md += ["", "Inputs read:", ""] + [f"- `{r}/{p}`: {s}" for r, p, s in common.CHECKED]
    with open(os.path.join(out, "claims.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(out, "claims.json"), "w") as f:
        json.dump(dict(n=len(C), disagree=n_bad, claims=C, inputs=common.CHECKED), f, indent=1)
    with open(os.path.join(out, "claims_summary.tex"), "w") as f:
        f.write("% generated; do not edit\n")
        words = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
        f.write(f"A check of {len(C)} numbers stated in the track's status documents and journals against "
                f"the run outputs found {len(C) - n_bad} in agreement and {words.get(n_bad, str(n_bad))} "
                f"difference{'s' if n_bad != 1 else ''}%")
    common.report_checks("ledger")
    print(f"ledger: {len(L)} ledger rows; {len(C)} claims, {n_bad} disagree")
    for c in C:
        if not c["agrees"]:
            print(f"ledger: DISAGREES {c['doc']}: {c['what']}: claimed {c['claimed']}, file {c['file_value']}")


if __name__ == "__main__":
    main()
