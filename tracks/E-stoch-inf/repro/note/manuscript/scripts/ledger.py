"""Ledger of the working note: every number of the note with its source.

Usage (inside the registered run_all): ledger.py OUT
Reads
- OUT/lattice/*.json: the figure numbers of the lattice paper, recomputed in this run by
  make_figs.py from the registered dump passes and records named in ORIGIN;
- OUT/langevin/langevin.json: the one-patch numbers, recomputed in this run by analyse.py from
  the registered simulation E-20261123-021043-d00a314;
- the outputs of the registered equation checks E-20261123-022009-a53e7ee (checked against that
  run's sha256sums.txt);
- quotes: committed lines of the track's records (repository path, line, the exact string),
  used for values read off the papers' figures by the figure packages and for numbers of core's
  review; the script stops if the string does not stand on that line;
- the papers' printed statements (source file of the arXiv version 2, line, exact string), read
  as text from the read-only store.
Writes OUT/tables/ledger.tex (one table per section, for the appendix) and OUT/tables/ledger.csv.
"""
import csv
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
KB = "/data/haiyangw/nrpic/kb-data/raw/arxiv"
PAPER = {"I": os.path.join(KB, "2401.08530/v2/src/Stochastic_Inflation.tex"),
         "II": os.path.join(KB, "2512.14649/v2/src/PRD_v2.tex")}
EQRUN = "E-20261123-022009-a53e7ee"
EQDIR = os.path.join("/data/haiyangw/nrpic/scratch/E-stoch-inf", EQRUN)
SIMRUN = "E-20261123-021043-d00a314"

PASS_SR = "E-20261124-133251-42e8aab"
PASS_USR = "E-20261124-130628-6790851"
ORIGIN = {
    "fig1.json": "records of E-20261123-020704-2b99463",
    "fig2_sr_contrast_P256v6.json": f"run E-20261121-202935-31520bc, pass {PASS_SR}",
    "fig3_sr_spec_P256v6.json": f"run E-20261121-202935-31520bc, pass {PASS_SR}",
    "fig4_usr_contrast.json": f"run E-20261123-021204-2f573ec, pass {PASS_USR}",
    "fig5_usr_spec.json": f"run E-20261123-021204-2f573ec, pass {PASS_USR}",
    "fig6a_sr_Kspec_P256v6.json": f"run E-20261121-202935-31520bc, pass {PASS_SR}",
    "fig6b_usr_Kspec.json": (f"run E-20261123-021204-2f573ec, passes {PASS_USR}, "
                             "E-20261124-141807-8352509, E-20261124-172949-8b2255b"),
    "fig7_fig8.json": f"runs E-20261123-020704-2b99463 (records), pass {PASS_SR}",
    "fig9_ablation.json": ("runs E-20261123-153347-18e7c21, -183822-4abbcae, -164235-49b0945, "
                           f"-192948-348e2e5, -153146-d965002, pass {PASS_SR}"),
    "fig9_ablation_sr_t75.json": ("runs E-20261123-153347-18e7c21, -183822-4abbcae, "
                                  "-152119-38957ba, pass E-20261124-141807-8352509"),
    "fig_signflip.json": ("records of E-20261123-045030-c20bcb3, -035925-8439d79, "
                          "E-20261122-190341-0419be6, E-20261121-211214-0377aab"),
}
CORE_MSG = "git:core/noise-level2:tracks/core/outbox/20261124T143303Z__to-E-stoch-inf__noise-level2-review-runs-stand.md"

# (section, quantity, kind, args, format)
# kinds: j = lattice json of this run; l = langevin.json of this run; e = equation-check run;
#        q = quote of a committed line (path, line, string); p = printed in a paper (paper, line, string)
ROWS = [
    # --- lattice: background
    ("Lattice background", "SR: largest |V/V_F - 1| of the box means (64^3)", "j", ("fig1.json", "sr.max_rel_V"), "{:.1e}"),
    ("Lattice background", "SR: largest |eps1/eps1_F - 1|", "j", ("fig1.json", "sr.max_rel_eps1"), "{:.1e}"),
    ("Lattice background", "SR: largest |eps2 - eps2_F|", "j", ("fig1.json", "sr.max_abs_eps2"), "{:.1e}"),
    ("Lattice background", "SR: e-folds N_f - N_* of the run", "j", ("fig1.json", "sr.N_end"), "{:.3f}"),
    ("Lattice background", "USR: largest |V/V_F - 1|", "j", ("fig1.json", "usr.max_rel_V"), "{:.1e}"),
    ("Lattice background", "USR: largest |eps1/eps1_F - 1|", "j", ("fig1.json", "usr.max_rel_eps1"), "{:.1e}"),
    ("Lattice background", "USR: largest |eps2 - eps2_F|", "j", ("fig1.json", "usr.max_abs_eps2"), "{:.1e}"),
    ("Lattice background", "USR: eps2 = 3 crossed upward at N", "j", ("fig1.json", "usr.eps2_eq3.0"), "{:.3f}"),
    ("Lattice background", "USR: eps2 = 3 crossed downward at N", "j", ("fig1.json", "usr.eps2_eq3.1"), "{:.3f}"),
    ("Lattice background", "USR: eps1 at N_f", "j", ("fig1.json", "usr.eps1_end"), "{:.2e}"),
    ("Lattice background", "USR: eps2 at N_f", "j", ("fig1.json", "usr.eps2_end"), "{:.4f}"),
    ("Lattice background", "Paper II: USR from N ~ 3.5", "p", ("II", 534, r"From $\mathcal{N} \sim 3.5$ USR starts"), None),
    ("Lattice background", "Paper II: (eps1, eps2) after the plateau", "p", ("II", 534, r"\left(0,-2.8 \times  10^{-2}\right)"), None),
    # --- lattice: spectra
    ("Lattice spectra", "SR: largest |NR/linear - 1| over all shells at N_f (256^3)", "j", ("fig3_sr_spec_P256v6.json", "last.max_abs_r_lin"), "{:.1e}"),
    ("Lattice spectra", "SR: the same for k <= k_max/2", "j", ("fig3_sr_spec_P256v6.json", "last.max_abs_r_lin_half"), "{:.1e}"),
    ("Lattice spectra", "SR: fraction of shells with NR/MS within 3/sqrt(modes)", "j", ("fig3_sr_spec_P256v6.json", "last.frac_within_env"), "{:.4f}"),
    ("Lattice spectra", "SR: power above k_max over Delta_MS(k_max)", "j", ("fig3_sr_spec_P256v6.json", "last.max_above_kmax_over_ms_cut"), "{:.1e}"),
    ("Lattice spectra", "USR: largest |NR/linear - 1| over all shells at N_f", "j", ("fig5_usr_spec.json", "last.max_abs_r_lin"), "{:.1e}"),
    ("Lattice spectra", "USR: the same for k <= k_max/2", "j", ("fig5_usr_spec.json", "last.max_abs_r_lin_half"), "{:.1e}"),
    ("Lattice spectra", "USR: fraction of shells with NR/MS within 3/sqrt(modes)", "j", ("fig5_usr_spec.json", "last.frac_within_env"), "{:.4f}"),
    ("Lattice spectra", "USR: power above k_max over Delta_MS(k_max)", "j", ("fig5_usr_spec.json", "last.max_above_kmax_over_ms_cut"), "{:.1e}"),
    ("Lattice spectra", "Paper II: USR power reaches", "p", ("II", 536, r"$\Delta[{\cal R}]\sim 0.1-1$"), None),
    # --- lattice: one-point statistics and constraints
    ("One-point statistics", "SR: half-width (68 per cent) of R^NR at N_f", "j", ("fig2_sr_contrast_P256v6.json", "final.pct_R.half68"), "{:.3e}"),
    ("One-point statistics", "SR: rms of R^NR at N_f", "j", ("fig2_sr_contrast_P256v6.json", "rms_R_final"), "{:.3e}"),
    ("One-point statistics", "SR: N at which dphi/phi_b reaches 95 per cent of its final width", "j", ("fig2_sr_contrast_P256v6.json", "pct_dphi_N95"), "{:.2f}"),
    ("One-point statistics", "SR: the same for R^NR", "j", ("fig2_sr_contrast_P256v6.json", "pct_R_N95"), "{:.2f}"),
    ("One-point statistics", "USR: half-width (68 per cent) of R^NR at N_f", "j", ("fig4_usr_contrast.json", "final.pct_R.half68"), "{:.3f}"),
    ("One-point statistics", "USR: rms of R^NR at N_f", "j", ("fig4_usr_contrast.json", "rms_R_final"), "{:.4f}"),
    ("One-point statistics", "USR: largest |R^NR| over the cells at N_f", "j", ("fig4_usr_contrast.json", "final.pct_R.max"), "{:.2f}"),
    ("One-point statistics", "USR: half-width of dPi/Pi_b at N_f", "j", ("fig4_usr_contrast.json", "final.pct_dPi.half68"), "{:.2e}"),
    ("One-point statistics", "Paper II, Fig. 2 read off (SR bands)", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 69, "about 1.0e-6"), None),
    ("One-point statistics", "SR amplitude factor, Paper II over ours", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 68, "factor of about"), None),
    ("One-point statistics", "USR amplitude factor, Paper II over ours", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 102, "by a factor 2.3 to 4"), None),
    ("One-point statistics", "Paper II, Fig. 4 read off: 100 per cent band of R^NR", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 105, "about 18"), None),
    ("One-point statistics", "Paper II: furthest outliers of R^NR", "p", ("II", 534, r"values of $\sim 10$ for the furthest outliers"), None),
    # --- constraints
    ("Constraints", "SR: entry maximum of <|H|/[H]>, 64^3", "j", ("fig7_fig8.json", "sr.H.entry_max.64"), "{:.1e}"),
    ("Constraints", "SR: entry maximum of <|H|/[H]>, 128^3", "j", ("fig7_fig8.json", "sr.H.entry_max.128"), "{:.1e}"),
    ("Constraints", "SR: entry maximum of <|M|/[M]>, 128^3", "j", ("fig7_fig8.json", "sr.M.entry_max.128"), "{:.1e}"),
    ("Constraints", "USR: entry maximum of <|H|/[H]>, box mean removed, 128^3", "j", ("fig7_fig8.json", "usr.H0.entry_max.128"), "{:.1e}"),
    ("Constraints", "USR: entry maximum of <|H|/[H]> with the box mean, 128^3", "j", ("fig7_fig8.json", "usr.H.entry_max.128"), "{:.1e}"),
    ("Constraints", "USR: order of that maximum, 64 to 128", "j", ("fig7_fig8.json", "usr.H.orders.64-128"), "{:.2f}"),
    ("Constraints", "USR: largest 99th percentile of |H|/[H] over the cells (256^3)", "j", ("fig4_usr_contrast.json", "pct_H_p99_max"), "{:.1e}"),
    ("Constraints", "USR: largest record mean of |M|/[M] (256^3)", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 265, "2.519e-2"), None),
    ("Constraints", "Paper II: Hamiltonian violation", "p", ("II", 539, r"($\sim 10^{-10}$)"), None),
    ("Constraints", "Paper II, Fig. 8a read off: SR plateau of <|H|/[H]>", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 180, "about 2e-11"), None),
    ("Constraints", "Momentum constraint second order from (cells per shortest wavelength)", "q", ("tracks/E-stoch-inf/a4res/README.md", 85, "at least 12.8 cells"), None),
    ("Constraints", "Sign flipped, SR: ratio of <|H|/[H]> to the proper run", "j", ("fig_signflip.json", "RNC256.H_ratio_min_entry"), "{:.1e}"),
    ("Constraints", "Sign flipped, SR: largest <|M|/[M]>", "j", ("fig_signflip.json", "RNC256.M_flip_max"), "{:.2f}"),
    ("Constraints", "Sign flipped, USR: median ratio of <|H|/[H]>", "j", ("fig_signflip.json", "U256nc.H_ratio_median_entry"), "{:.1e}"),
    ("Constraints", "Sign flipped, USR: largest <|M|/[M]>", "j", ("fig_signflip.json", "U256nc.M_flip_max"), "{:.2f}"),
    ("Constraints", "Paper II: a flipped sign gives", "p", ("II", 541, r"${\cal H}/[{\cal H}]\sim 10^{-5}$ and  ${\cal M}/[{\cal M}]\sim 1$"), None),
    # --- extrinsic curvature
    ("Extrinsic curvature", "SR: Delta[K] at N_f over N = 5.3 (median over shells)", "j", ("fig6a_sr_Kspec_P256v6.json", "K_last_over_N55.median"), "{:.3f}"),
    ("Extrinsic curvature", "SR: Delta[Kt] at N_f over N = 4.4 (median)", "j", ("fig6a_sr_Kspec_P256v6.json", "Kt_last_over_N45.median"), "{:.1e}"),
    ("Extrinsic curvature", "SR: Q/K at N_f (median)", "j", ("fig6a_sr_Kspec_P256v6.json", "Q_over_K_last.median"), "{:.1e}"),
    ("Extrinsic curvature", "USR: Delta[K] at N_f over its maximum (median)", "j", ("fig6b_usr_Kspec.json", "K_last_over_max.median"), "{:.1e}"),
    ("Extrinsic curvature", "USR: Q/K at N_f (median)", "j", ("fig6b_usr_Kspec.json", "Q_over_K_last.median"), "{:.1e}"),
    ("Extrinsic curvature", "USR: shells with Q below K, N = 0.26-3.05", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 152, "below 0.2 for 0.26 <= N <= 3.05"), None),
    ("Extrinsic curvature", "USR: shells with Q below K from N = 7.27", "q", ("tracks/E-stoch-inf/repro/figs/RESULTS.md", 153, "0.98-1.0 from N = 7.27 to N_f"), None),
    # --- convergence
    ("Convergence", "SR spectra: largest |1 - Delta_NR/Delta_lin|, 32^3", "j", ("fig7_fig8.json", "specconv.32.max"), "{:.1e}"),
    ("Convergence", "the same, 64^3", "j", ("fig7_fig8.json", "specconv.64.max"), "{:.1e}"),
    ("Convergence", "the same, 128^3", "j", ("fig7_fig8.json", "specconv.128.max"), "{:.1e}"),
    ("Convergence", "SR: order of the entry maximum of H, 32 to 64", "j", ("fig7_fig8.json", "sr.H.orders.32-64"), "{:.2f}"),
    ("Convergence", "SR: order of the entry maximum of M, 32 to 64", "j", ("fig7_fig8.json", "sr.M.orders.32-64"), "{:.2f}"),
    ("Convergence", "256^3 rungs", "pending", ("E-20261124-130952-4be980b, E-20261124-130711-a5dec67",), None),
    # --- backreaction
    ("Backreaction", "USR level 2 against 0: rms over the shells at N_f", "j", ("fig9_ablation.json", "r20_usr.rms"), "{:.1e}"),
    ("Backreaction", "USR level 2 against 0: largest shell", "j", ("fig9_ablation.json", "r20_usr.max"), "{:.1e}"),
    ("Backreaction", "USR level 2 against 0: fraction of shells positive", "j", ("fig9_ablation.json", "r20_usr.frac_pos"), "{:.2f}"),
    ("Backreaction", "SR level 2 against 0 at N = 7.19: largest shell", "j", ("fig9_ablation_sr_t75.json", "r20_sr.max"), "{:.1e}"),
    ("Backreaction", "SR level 2 against 0 at N = 7.19: rms for |n| <= 32", "j", ("fig9_ablation_sr_t75.json", "r20_sr.rms_n_le_32"), "{:.1e}"),
    ("Backreaction", "SR level 2 against 0 at N_f", "pending", ("E-20261124-131359-49afe29",), None),
    ("Backreaction", "SR level 1 against 0: largest shell", "j", ("fig9_ablation.json", "r10_sr.max"), "{:.1e}"),
    ("Backreaction", "USR level 1 against 0: largest shell", "j", ("fig9_ablation.json", "r10_usr.max"), "{:.1e}"),
    ("Backreaction", "level 0, noise on shells against on the mesh: largest SR shell", "j", ("fig9_ablation.json", "shells_vs_mesh_sr.max"), "{:.1e}"),
    ("Backreaction", "Paper II: bound on level 2 against 0", "p", ("II", 520, r"$\lesssim  1$\textpertenthousand"), None),
    ("Backreaction", "Review: level 1 against 0 falls per halving of the step by", "q", (CORE_MSG, 41, "falls by 16 per halving of the"), None),
    ("Backreaction", "Review: level 2 against 0 equals the level-2 curve to", "q", (CORE_MSG, 43, "the level-2 curve to 1 per cent"), None),
    # --- one patch
    ("One patch", "Euler 0.01 background crosses the junction at N_b", "l", ("backgrounds.euler01.N_cross_phi_c",), "{:.4f}"),
    ("One patch", "converged background: field at N_b = 12 (the plateau stop)", "l", ("backgrounds.exact.phi_at_12",), "{:.5f}"),
    ("One patch", "junction phi_c of the potential", "q", ("tracks/E-stoch-inf/repro/langevin/README.md", 50, "phi_c = 9.056"), None),
    ("One patch", "Euler 0.005 background: field at N_b = 12", "l", ("backgrounds.euler005.phi_at_12",), "{:.5f}"),
    ("One patch", "converged background: half the paths lost by N_b", "l", ("variants.bg_exact.N_half_dead",), "{:.2f}"),
    ("One patch", "Paper I: slope reached at", "p", ("I", 842, r"$\simeq 3.04$ efolds"), None),
    ("One patch", "Paper I: step of the scheme", "p", ("I", 842, r"$0.01$-efolds steps"), None),
    ("One patch", "Paper I: evolver named", "p", ("I", 836, "Stratonovich evolver"), None),
    ("One patch", "Ito reading, width of alpha at N_b = 4", "l", ("variants.ito_naive.at.4.std_a",), "{:.4f}"),
    ("One patch", "Ito reading, width of alpha at N_b = 6", "l", ("variants.ito_naive.at.6.std_a",), "{:.4f}"),
    ("One patch", "Ito reading, width of N - N_b at N_b = 6", "l", ("variants.ito_naive.at.6.std_D",), "{:.4f}"),
    ("One patch", "Stratonovich reading, width of alpha at N_b = 6", "l", ("variants.base.at.6.std_a",), "{:.4f}"),
    ("One patch", "Stratonovich reading, width of N - N_b at N_b = 6", "l", ("variants.base.at.6.std_D",), "{:.4f}"),
    ("One patch", "Paper I, figures read off: widths of alpha at 4, 5, 6", "q", ("tracks/E-stoch-inf/repro/langevin/README.md", 77, "0.117, 0.133, 0.121"), None),
    ("One patch", "Paper I, figures read off: widths of N - N_b at 4, 5, 6", "q", ("tracks/E-stoch-inf/repro/langevin/README.md", 78, "0.190"), None),
    ("One patch", "Ito reading, median skewness of alpha, N_b in [4.5, 6]", "l", ("variants.ito_naive.median_4.5_6.skew_a",), "{:.2f}"),
    ("One patch", "Stratonovich reading, the same", "l", ("variants.base.median_4.5_6.skew_a",), "{:.2f}"),
    ("One patch", "Paper I, figures read off: skewness of alpha", "q", ("tracks/E-stoch-inf/repro/langevin/README.md", 78, "kappa3(alpha) ~ 1.1"), None),
    ("One patch", "Stratonovich reading, mean of N - N_b at N_b = 6", "l", ("variants.base.at.6.mean_D",), "{:.3f}"),
    ("One patch", "Ito reading, mean of N - N_b at N_b = 6", "l", ("variants.ito_naive.at.6.mean_D",), "{:.4f}"),
    ("One patch", "Ito reading at step 0.001, width of alpha at N_b = 4", "l", ("variants.naive_h001.at.4.std_a",), "{:.4f}"),
    ("One patch", "linear check at N_b = 3: width of alpha, run over linear theory", "l", ("linear.3.run_std_a", "/", "linear.3.lin_std_a"), "{:.4f}"),
    ("One patch", "alpha^3 set to 1: skewness of alpha at N_b = 6", "l", ("variants.a3one.at.6.skew_a",), "{:.2f}"),
    ("One patch", "Ito term: drift measured by Monte Carlo", "e", ("langevin/langevin.json", "mc.measured_drift"), "{:.4f}"),
    ("One patch", "Ito term: standard error of that drift", "e", ("langevin/langevin.json", "mc.measured_drift_sem"), "{:.4f}"),
    ("One patch", "Ito term: alpha^5 prediction", "e", ("langevin/langevin.json", "mc.pred_alpha5"), "{:.4f}"),
    ("One patch", "Ito term: alpha^3 prediction (as printed)", "e", ("langevin/langevin.json", "mc.pred_alpha3_P0"), "{:.4f}"),
    ("One patch", "Paper I: Ito term as printed", "p", ("I", 817, r"\frac{\alpha^3}{\dot{\phi_b}^2}"), None),
    ("One patch", "USR noise amplitude over printed, sigma = 0.1", "e", ("noise_amp/noise_amp.json", "USR.rows.2.amp_ibp_over_printed"), "{:.2e}"),
    ("One patch", "the same, sigma = 0.5", "e", ("noise_amp/noise_amp.json", "USR.rows.4.amp_ibp_over_printed"), "{:.2e}"),
    ("One patch", "SR noise amplitude over printed, sigma = 0.1", "e", ("noise_amp/noise_amp.json", "SR.rows.2.amp_ibp_over_printed"), "{:.3f}"),
]


def get(d, path):
    for k in path.split("."):
        if isinstance(d, list):
            d = d[int(k)]
        elif k in d:
            d = d[k]
        else:  # keys with dots, such as "4.5_6"
            raise KeyError(path)
    return d


def get_dotted(d, path):
    """Like get, but joins key parts so that keys such as 'median_4.5_6' and '4.5' resolve."""
    parts = path.split(".")
    i = 0
    while i < len(parts):
        for j in range(len(parts), i, -1):
            key = ".".join(parts[i:j])
            if isinstance(d, list) and j == i + 1 and key.isdigit():
                d = d[int(key)]
                i = j
                break
            if isinstance(d, dict) and key in d:
                d = d[key]
                i = j
                break
        else:
            raise KeyError(path)
    return d


def sha_ok(run_dir, rel):
    sums = os.path.join(run_dir, "sha256sums.txt")
    want = None
    for line in open(sums):
        h, f = line.split(maxsplit=1)
        if f.strip().lstrip("*").lstrip("./") == rel:
            want = h
    got = hashlib.sha256(open(os.path.join(run_dir, rel), "rb").read()).hexdigest()
    if want != got:
        sys.exit(f"checksum of {run_dir}/{rel} does not match its sha256sums.txt")


def tex_escape(s):
    """Plain text of the quantity and source columns, safe for LaTeX."""
    s = s.replace("<=", "\u0001").replace(">=", "\u0002")
    rep = {"_": r"\_", "%": r"\%", "&": r"\&", "#": r"\#", "^": r"\^{}", "~": r"$\sim$",
           "<": r"$<$", ">": r"$>$", "|": r"$|$", "\u0001": r"$\le$", "\u0002": r"$\ge$",
           "/": r"/\allowbreak{}"}
    return "".join(rep.get(c, c) for c in s)


def printed(s):
    """A string printed in a paper's LaTeX source, typeset as the paper typesets it."""
    if "$" not in s and "\\" in s:
        s = "$" + s + "$"
    return "``" + s + "''"


def main():
    out = sys.argv[1]
    run_id = os.path.basename(os.path.normpath(out))
    os.makedirs(os.path.join(out, "tables"), exist_ok=True)
    cache = {}
    sha_ok(EQDIR, "langevin/langevin.json")
    sha_ok(EQDIR, "noise_amp/noise_amp.json")
    rows = []
    for sec, qty, kind, args, fmt in ROWS:
        if kind == "j":
            fn, path = args
            p = os.path.join(out, "lattice", fn)
            d = cache.setdefault(p, json.load(open(p)))
            val = fmt.format(get_dotted(d, path))
            src = f"this run ({run_id}) from {ORIGIN[fn]}"
        elif kind == "l":
            p = os.path.join(out, "langevin", "langevin.json")
            d = cache.setdefault(p, json.load(open(p)))
            if len(args) == 3:
                v = get_dotted(d, args[0]) / get_dotted(d, args[2])
            else:
                v = get_dotted(d, args[0])
            val = fmt.format(v)
            src = f"this run ({run_id}) from simulation {SIMRUN}"
        elif kind == "e":
            p = os.path.join(EQDIR, args[0])
            d = cache.setdefault(p, json.load(open(p)))
            val = fmt.format(get_dotted(d, args[1]))
            src = f"run {EQRUN}"
        elif kind == "q":
            path, line, s = args
            if path.startswith("git:"):
                ref, gpath = path[4:].split(":", 1)
                body = subprocess.run(["git", "-C", REPO, "show", f"{ref}:{gpath}"], check=True,
                                      capture_output=True, text=True).stdout
                path = f"{gpath} (branch {ref})"
            else:
                body = open(os.path.join(REPO, path)).read()
            text = body.split("\n")[line - 1]
            if s not in text:
                sys.exit(f"quote not on its line: {path}:{line}: {s!r}")
            val = s
            src = f"{path}:{line}"
        elif kind == "p":
            pap, line, s = args
            text = open(PAPER[pap]).read().split("\n")[line - 1]
            if s not in text:
                sys.exit(f"paper string not on its line: Paper {pap}:{line}: {s!r}")
            val = "printed: " + s
            src = f"Paper {pap}, source line {line}"
        elif kind == "pending":
            val = "PENDING"
            src = "continued run " + args[0]
        rows.append((sec, qty, val, src))
    with open(os.path.join(out, "tables", "ledger.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "quantity", "value", "source"])
        w.writerows(rows)
    # LaTeX: one table per section; values in \texttt where they are printed strings
    secs = []
    for r in rows:
        if r[0] not in secs:
            secs.append(r[0])
    lines = []
    for k, sec in enumerate(secs):
        lab = "ledger" + "".join(c for c in sec.lower() if c.isalpha())
        lines += [r"\begin{table*}", r"\caption{Ledger, " + sec.lower() + r". Each value with its source: "
                  r"a registered run, a committed line of the program's records, or a line of a paper's source.}",
                  r"\label{tab:" + lab + "}", r"\footnotesize", r"\begin{tabular}{p{0.36\textwidth}p{0.2\textwidth}p{0.38\textwidth}}",
                  r"\toprule", r"Quantity & Value & Source \\", r"\midrule"]
        for r in rows:
            if r[0] != sec:
                continue
            q = tex_escape(r[1])
            v = r[2]
            if v.startswith("printed: "):
                v = printed(v[len("printed: "):])
            elif v == "PENDING":
                v = r"\pending{continued run}"
            else:
                v = tex_escape(v)
            s = tex_escape(r[3])
            lines.append(f"{q} & {v} & {s} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    with open(os.path.join(out, "tables", "ledger.tex"), "w") as f:
        f.write("\n".join(lines))
    print(f"ledger: {len(rows)} rows in {len(secs)} tables")


if __name__ == "__main__":
    main()
