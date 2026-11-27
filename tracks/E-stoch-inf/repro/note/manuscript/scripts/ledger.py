"""Ledger of the working note: every number of the note with its source.

Usage (inside the registered run_all): ledger.py OUT
Reads
- OUT/lattice/*.json: the figure numbers of the lattice paper, recomputed in this run by
  make_figs.py from the registered dump passes and records named in ORIGIN;
- OUT/langevin/langevin.json: the one-patch numbers, recomputed in this run by analyse.py from
  the registered simulation E-20261123-021043-d00a314;
- the outputs of the registered equation checks E-20261123-022009-a53e7ee and of the reader split
  E-20261124-224228-8e20938 (each checked against its run's sha256sums.txt);
- quotes: committed lines of the track's records (repository path, line, the exact string),
  used for values read off the papers' figures by the figure packages and for numbers of core's
  review; the script stops if the string does not stand on that line;
- the papers' printed statements (source file of the arXiv version 2, line, exact string), read
  as text from the read-only store;
- the report of the independent verifier (repro/verify/VERIFIER.md): for each row its verdict,
  the line of the report and a string that must stand on that line (the script stops otherwise).
Writes OUT/tables/ledger.tex (one table per section, for the appendix) and OUT/tables/ledger.csv.
"""
import csv
import hashlib
import json
import math
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
PASS_CONT = "E-20261124-213029-e937f69"   # 256^3 rung and SR level 2 at N_f (continued runs)
JOIN = "E-20261124-212343-7e9c4b2"        # joined records of the continued runs
R8A = "E-20261124-224228-8e20938"         # four readers of R^NR on the final SR dumps, 128^3 and 256^3
R8ADIR = os.path.join("/data/haiyangw/nrpic/scratch/E-stoch-inf", R8A)
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
    "fig7_fig8.json@256": "the 256^3 runs of the caption",
    "fig7_fig8.json@all": "runs E-20261123-020704-2b99463 (records) and the 256^3 runs of the caption",
    "fig9_ablation.json": ("runs E-20261123-153347-18e7c21, -183822-4abbcae, -164235-49b0945, "
                           f"-192948-348e2e5, -153146-d965002, pass {PASS_SR}"),
    "fig9_ablation.json@al2s": ("runs E-20261123-153347-18e7c21, -152119-38957ba (continued in "
                                f"E-20261124-131359-49afe29), pass {PASS_CONT}"),
    "fig9_ablation_sr_t75.json": ("runs E-20261123-153347-18e7c21, -183822-4abbcae, "
                                  "-152119-38957ba, pass E-20261124-141807-8352509"),
    "fig2_sr_contrast.json": "run E-20261123-035925-8439d79, pass E-20261124-225826-0bf3842",
    "fig_signflip.json": ("records of E-20261123-045030-c20bcb3, -035925-8439d79, "
                          "E-20261122-190341-0419be6, E-20261121-211214-0377aab; the first two joined "
                          f"with their continuations in {JOIN}"),
    "fig_signflip.json@rsf256": "record of E-20261123-035925-8439d79 to N_f",
}
CORE_MSG = "git:core/noise-level2:tracks/core/outbox/20261124T143303Z__to-E-stoch-inf__noise-level2-review-runs-stand.md"

VERIFIER = "tracks/E-stoch-inf/repro/verify/VERIFIER.md"
RES = "tracks/E-stoch-inf/repro/figs/RESULTS.md"
LVR = "tracks/E-stoch-inf/repro/langevin/README.md"

# Definitions behind the rows of each section (verifier, weakest point 2): printed under each table.
SECNOTE = {
    "Lattice background": "Maxima over all record times of the $64^3$ runs; F: the Friedmann (level-0) background of the same run.",
    "Lattice spectra": ("Shells: lattice shells $|n|^2$ with more than ten independent modes ($\\bm n$ and $-\\bm n$ count once). Linear: the power of the realization's own "
                        "random amplitudes with the code's mode functions at the same time. Mukhanov-Sasaki: the ensemble power, "
                        "with the envelope $3/\\sqrt{\\mathrm{modes}}$."),
    "One-point statistics": ("Half-width (68 per cent): half the distance between the 16th and 84th percentiles over the cells "
                             "(0.9945 standard deviations for a Gaussian). N at 95 per cent: the first dump at which the half-width "
                             "reaches 95 per cent of its final value."),
    "Constraints": ("Entry maximum: largest record value of the mean ratio for $0.05 < N \\le \\ln 8$ (the entry at "
                    "$k_\\mathrm{max} = 8\\,\\Delta k$); on the $64^3$ to $256^3$ lattices it falls on the first record of "
                    "that window, the decaying initial transient. Order: $\\log_2$ of the ratio of the entry maxima of "
                    "neighbouring lattices, a convergence order only for the background residual of the USR box mean."
                    " The $256^3$ runs: E-20261123-090727-4b6e5a5 (SR) and E-20261123-065855-265732a (USR) with their "
                    "continuations, joined records of E-20261124-212343-7e9c4b2, pass E-20261124-213029-e937f69."
),
    "Per-cell constraints": ("Percentiles over the $256^3$ cells of one dump of $|\\Ham|/[\\Ham]$ (or $|\\Mom|/[\\Mom]$), "
                             "$[\\Ham]$ and $[\\Mom]$ the sums of the magnitudes of the terms. SR: the 35 dumps of the "
                             "one-point run E-20261123-035925-8439d79 from $N = 0$ to $N_f$, its continuations joined in "
                             "E-20261124-225720-444aecc; entry plateau: its dumps with $0.75 \\le N \\le 3.2$, after "
                             "the initial transient and before the rise of the last crossings. Record mean: "
                             "$\\langle|\\Ham|/[\\Ham]\\rangle$ of the code's record at every cycle. USR: the 41 dumps "
                             "of the one-point run."),
    "Sign flip": ("Runs with the sign of the momentum source flipped, $256^3$. Ratio: flipped over proper run at common "
                  "record times with $0.5 \\le N \\le \\ln 64$, the entry of every mode; SR from the joined records "
                  "of both continued runs."),
    "Extrinsic curvature": "Medians over the shells with more than ten independent modes.",
    "Convergence": ("Final dump of each lattice with $k_\\mathrm{max} = 8\\,\\Delta k$; shells and linear power as in the "
                    "spectra table. Order: $\\log_2$ of the ratio of the largest departures of neighbouring lattices. "
                    "Per-mode rms: root mean square over the modes inside the window ($W_k > 1/2$) of "
                    "$|\\mathcal{R}_k^\\mathrm{NR} - \\mathcal{R}_k^\\mathrm{lin}|/|\\mathcal{R}_k^\\mathrm{lin}|$. "
                    "$\\mathcal{R}^\\mathrm{NR}$ takes the conformal factor as $c[\\chi]/(2\\langle\\chi\\rangle)$; rows marked "
                    "$\\ln\\chi$ take $c[\\ln\\chi]/2$, the independent check's reading, which differs at second order. Plateau "
                    "ratio: median over $0.5 \\le N \\le \\ln 8$ of the ratio of the record means of a constraint at "
                    "matched times, finer lattice over coarser, for 64/32, 128/64 and 256/128."
                    " The $256^3$ runs: E-20261123-090727-4b6e5a5 (SR) and E-20261123-065855-265732a (USR) with their "
                    "continuations, joined records of E-20261124-212343-7e9c4b2, pass E-20261124-213029-e937f69."),
    "Ultra-slow-roll criteria": ("Release runs of the code on $256^3$ (first seed at noise amplitude $\\lambda = \\pm1, \\pm\\frac12, \\pm\\frac14$; second "
                                 "seed at $\\lambda = \\pm1$; a control with the momentum source flipped) and $320^3$ (first seed, $\\lambda = \\pm1$). "
                                 "Departure per mode: $|\\mathcal{R}^\\mathrm{odd}_k/\\mathcal{R}^\\mathrm{lin}_k - 1|$ of the odd part at $N_f$ against "
                                 "the code's linear mode functions. Factor of the even part: $e(\\lambda)/e(\\lambda/2)$ of the rms of the even part of a "
                                 "constraint, with a noise level removed (fixed in advance: from the odd parts of one pair; after the "
                                 "data: from three amplitudes). Common mode: mean of the real part of the relative odd-part error over "
                                 "$k \\le 16\\,\\Delta k$. The Check column of this table cites the fresh verifier of the G2 package "
                                 "(stage/G2/VERIFIER.md); ``verifier's run'' marks a value that only the verifier's own run gives."),
    "Tail statistics": ("Gate G3 of the track: $128^3$ ultra-slow-roll boxes on the release build, mirrored pairs of seeds at "
                        "$\\lambda = \\pm1$ read at $N_f$; $\\zeta$ is $\\delta N$ to the uniform-field surface of the reference "
                        "(tabulated map along the box relation, checked on every box). The pair is the unit: mean over its two "
                        "boxes, then mean and standard error over the pairs. Tails at the box's own standard deviation; reference: "
                        "one-patch $\\delta N$ of the same band, two direct runs pooled (batch means), the importance-sampled tail "
                        "at four standard deviations. Constraint and resolution rows: the three-amplitude and $160^3$ runs of the "
                        "same gate. No independent check yet (Check column: none)."),
    "Backreaction": ("Relative change of the final power per shell with more than ten independent modes, same random amplitudes, "
                     "noise on the mesh unless stated; SR at $N = 7.19$, after the last crossing, and at $N_f$."),
    "One-patch drift and noise amplitude": ("The drift of the lapse measured by Monte Carlo against the two forms of the "
                                     "It\\^o term, and the noise amplitude of the appendix of Paper I over the printed one at the "
                                     "crossing $k = \\sigma a H$."),
    "One patch": ("Widths and skewness over the live paths; a path is lost once $|\\alpha|$ reaches 50 or is not finite. "
                  "Median skewness: over the record times $4.5 \\le N_b \\le 6$."),
}

# Check of the independent verifier: (code, line of VERIFIER.md, string on that line, value shown)
# codes: yes, diff (its value differs beyond the printed digits), reach (its method cannot reach the digits),
#        quote (printed string checked), rerun (rerun of these scripts only), none
def V(code, line=None, needle=None, shown="", path=None):
    return (code, line, needle, shown, path)


# The G2 package of the track (ultra-slow-roll criteria fixed before the runs): registered runs and
# the report of its fresh verifier (stage/G2/VERIFIER.md), which checks those rows.
G2V = "tracks/E-stoch-inf/stage/G2/VERIFIER.md"
G2JUDGE = "E-20261123-024359-5dc3213"   # judge of the release ladder (judge_g2.json)
G2Q = "E-20261125-033450-4c4a31c"       # quarter-amplitude pair (judge_q.json)
G2FL3 = "E-20261125-023427-6fb6400"     # the verifier's three-amplitude reading (floor3.json)
SCR = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
G3PAIRS = "PENDING"                      # pair reading of the G3 baseline (pairs.json)
G3C = "E-20261126-115943-32970f2"        # G3-C reading (g3c.json)
G3R = "E-20261126-120438-9d48377"        # G3-R reading (g3r.json)


G2ORIGIN = {"fig_g2_resolution.json": f"judge {G2JUDGE}",
            "fig_g2_mosaic.json": "the last dump of release run E-20261121-211214-0377aab"}


def G(code, line, needle, shown=""):
    return V(code, line, needle, shown, G2V)

QP = V("quote", 91, "12, 13, 22, 35, 44, 53, 76")
Q0 = V("quote", 92, "84-86, 106 (P0:817-842): CONFIRMED")
NONE = V("none")
# the check joined the SR one-point run to N_f and compared its records with the dump means (VERIFIER 8.6),
# but did not recompute the per-cell percentiles
JOINED = V("joined", 269, "I joined it (8.1: bit-identical over 243 lines", "values not recomputed")

# (section, quantity, kind, args, format, check)
# kinds: j = lattice json of this run; l = langevin.json of this run; e = equation-check run;
#        r = reader split run R8A; jd = a value derived from a lattice json of this run (a function
#        of the json that returns the printed string);
#        q = quote of a committed line (path, line, string[, value shown]); p = printed in a paper (paper, line, string)
ROWS = [
    # --- lattice: background
    ("Lattice background", "SR: largest |V/V_F - 1| of the box means (64^3)", "j", ("fig1.json", "sr.max_rel_V"), "{:.1e}", V("yes", 77, "rows 1 (9.8e-13)")),
    ("Lattice background", "SR: largest |eps1/eps1_F - 1|", "j", ("fig1.json", "sr.max_rel_eps1"), "{:.1e}", V("yes", 77, "2 (6.4e-12)", "6.4e-12")),
    ("Lattice background", "SR: largest |eps2 - eps2_F|", "j", ("fig1.json", "sr.max_abs_eps2"), "{:.1e}", V("reach", 83, "3 and 7 (eps2 differences")),
    ("Lattice background", "SR: e-folds N_f - N_* of the run", "j", ("fig1.json", "sr.N_end"), "{:.3f}", V("yes", 77, "4 (8.0989)")),
    ("Lattice background", "USR: largest |V/V_F - 1|", "j", ("fig1.json", "usr.max_rel_V"), "{:.1e}", V("yes", 77, "5 (1.12e-9)")),
    ("Lattice background", "USR: largest |eps1/eps1_F - 1|", "j", ("fig1.json", "usr.max_rel_eps1"), "{:.1e}", V("yes", 77, "6 (4.63e-5)")),
    ("Lattice background", "USR: largest |eps2 - eps2_F|", "j", ("fig1.json", "usr.max_abs_eps2"), "{:.1e}", V("reach", 83, "3 and 7 (eps2 differences")),
    ("Lattice background", "USR: eps2 = 3 crossed upward at N", "j", ("fig1.json", "usr.eps2_eq3.0"), "{:.3f}", V("yes", 77, "8 (2.523)")),
    ("Lattice background", "USR: eps2 = 3 crossed downward at N", "j", ("fig1.json", "usr.eps2_eq3.1"), "{:.3f}", V("yes", 78, "9 (6.550)")),
    ("Lattice background", "USR: eps1 at N_f", "j", ("fig1.json", "usr.eps1_end"), "{:.2e}", V("yes", 78, "10 (1.008e-12)")),
    ("Lattice background", "USR: eps2 at N_f", "j", ("fig1.json", "usr.eps2_end"), "{:.4f}", V("yes", 78, "11 (-0.02762)")),
    ("Lattice background", "Paper II: USR from N ~ 3.5", "p", ("II", 534, r"From $\mathcal{N} \sim 3.5$ USR starts"), None, QP),
    ("Lattice background", "Paper II: (eps1, eps2) after the plateau", "p", ("II", 534, r"\left(0,-2.8 \times  10^{-2}\right)"), None, QP),
    # --- lattice: spectra
    ("Lattice spectra", "SR: largest |NR/linear - 1| over the shells at N_f (256^3)", "j", ("fig3_sr_spec_P256v6.json", "last.max_abs_r_lin"), "{:.1e}", V("diff", 141, "SR 4.5e-3 (ledger 5.2e-3)", "4.5e-3")),
    ("Lattice spectra", "SR: the same for k <= k_max/2", "j", ("fig3_sr_spec_P256v6.json", "last.max_abs_r_lin_half"), "{:.1e}", V("yes", 143, "Rows 15 and 19 CONFIRMED", "1.1e-4")),
    ("Lattice spectra", "SR: fraction of shells within 3/sqrt(modes) of the Mukhanov-Sasaki power", "j", ("fig3_sr_spec_P256v6.json", "last.frac_within_env"), "{:.4f}", V("yes", 78, "16 and 20 (0.9965)")),
    ("Lattice spectra", "SR: power above k_max over the Mukhanov-Sasaki power at k_max", "j", ("fig3_sr_spec_P256v6.json", "last.max_above_kmax_over_ms_cut"), "{:.1e}", V("diff", 51, "SR 1.1e-14 (8.7e-14)", "1.1e-14")),
    ("Lattice spectra", "USR: largest |NR/linear - 1| over the shells at N_f", "j", ("fig5_usr_spec.json", "last.max_abs_r_lin"), "{:.1e}", V("diff", 142, "USR 4.4e-3 (5.0e-3)", "4.4e-3")),
    ("Lattice spectra", "USR: the same for k <= k_max/2", "j", ("fig5_usr_spec.json", "last.max_abs_r_lin_half"), "{:.1e}", V("yes", 143, "Rows 15 and 19 CONFIRMED", "3.5e-4")),
    ("Lattice spectra", "USR: fraction of shells within 3/sqrt(modes) of the Mukhanov-Sasaki power", "j", ("fig5_usr_spec.json", "last.frac_within_env"), "{:.4f}", V("yes", 78, "16 and 20 (0.9965)")),
    ("Lattice spectra", "USR: power above k_max over the Mukhanov-Sasaki power at k_max", "j", ("fig5_usr_spec.json", "last.max_above_kmax_over_ms_cut"), "{:.1e}", V("yes", 78, "21 (1.2e-7)", "1.2e-7")),
    ("Lattice spectra", "Paper II: USR power reaches", "p", ("II", 536, r"$\Delta[{\cal R}]\sim 0.1-1$"), None, QP),
    # --- lattice: one-point statistics
    ("One-point statistics", "SR: half-width (68 per cent) of R^NR at N_f", "j", ("fig2_sr_contrast_P256v6.json", "final.pct_R.half68"), "{:.3e}", V("yes", 79, "x 0.9945 for a central 68 % band = 2.281e-5")),
    ("One-point statistics", "SR: rms of R^NR at N_f", "j", ("fig2_sr_contrast_P256v6.json", "rms_R_final"), "{:.3e}", V("yes", 79, "24 (2.2780e-5)")),
    ("One-point statistics", "SR: N at which dphi/phi_b reaches 95 per cent of its final half-width", "j", ("fig2_sr_contrast_P256v6.json", "pct_dphi_N95"), "{:.2f}", V("yes", 79, "25 (3.89, dump", "3.89")),
    ("One-point statistics", "SR: the same for R^NR", "j", ("fig2_sr_contrast_P256v6.json", "pct_R_N95"), "{:.2f}", V("diff", 84, "26 (3.28 vs 3.44", "3.28")),
    ("One-point statistics", "USR: half-width (68 per cent) of R^NR at N_f", "j", ("fig4_usr_contrast.json", "final.pct_R.half68"), "{:.3f}", V("yes", 80, "27 (0.8947, 0.8898 as a 68 % band)", "0.8898")),
    ("One-point statistics", "USR: rms of R^NR at N_f", "j", ("fig4_usr_contrast.json", "rms_R_final"), "{:.4f}", V("yes", 80, "28 (0.8945)")),
    ("One-point statistics", "USR: largest |R^NR| over the cells at N_f", "j", ("fig4_usr_contrast.json", "final.pct_R.max"), "{:.2f}", V("yes", 80, "29 (4.568)", "4.568")),
    ("One-point statistics", "USR: half-width of dPi/Pi_b at N_f", "j", ("fig4_usr_contrast.json", "final.pct_dPi.half68"), "{:.2e}", V("rerun", 96, "Rerun only (not from raw outputs): 30")),
    ("One-point statistics", "Paper II, Fig. 2 read off (SR bands of dphi/phi_b)", "q", (RES, 86, "about 1.0e-6"), None, V("yes", 80, "31 and 34", "own read-off")),
    ("One-point statistics", "SR amplitude factor, Paper II over ours", "q", (RES, 86, "3.5: P1's 68 per cent bands", "about 3.5"), None, V("yes", 58, "my value is about 3.5", "about 3.5")),
    ("One-point statistics", "USR amplitude factor, Paper II over ours", "q", (RES, 122, "by a factor 2.3 to 4"), None, V("yes", 58, "CONFIRMED at its upper end", "upper end")),
    ("One-point statistics", "Paper II, Fig. 4 read off: 100 per cent band of R^NR", "q", (RES, 125, "about 18"), None, V("yes", 80, "31 and 34", "own read-off")),
    ("One-point statistics", "Paper II: furthest outliers of R^NR", "p", ("II", 534, r"values of $\sim 10$ for the furthest outliers"), None, V("quote", 93, "from P1's own Fig. 4 (full band about +-18)", "its Fig. 4: about 18")),
    # --- constraints
    ("Constraints", "SR: entry maximum of <|H|/[H]>, 64^3", "j", ("fig7_fig8.json", "sr.H.entry_max.64"), "{:.1e}", V("yes", 137, "SR 64^3 1.78e-12", "1.78e-12")),
    ("Constraints", "SR: entry maximum of <|H|/[H]>, 128^3", "j", ("fig7_fig8.json", "sr.H.entry_max.128"), "{:.1e}", V("yes", 137, "128^3 2.00e-12", "2.00e-12")),
    ("Constraints", "SR: entry maximum of <|M|/[M]>, 128^3", "j", ("fig7_fig8.json", "sr.M.entry_max.128"), "{:.1e}", V("yes", 137, "M 128^3 1.23e-5", "1.23e-5")),
    ("Constraints", "USR: entry maximum of <|H|/[H]>, box mean removed, 128^3", "j", ("fig7_fig8.json", "usr.H0.entry_max.128"), "{:.1e}", V("yes", 138, "USR 128^3 box mean removed 2.25e-12", "2.25e-12")),
    ("Constraints", "USR: entry maximum of <|H|/[H]> with the box mean, 128^3", "j", ("fig7_fig8.json", "usr.H.entry_max.128"), "{:.1e}", V("yes", 138, "with the box mean 3.25e-10", "3.25e-10")),
    ("Constraints", "USR: order of that maximum, 64 to 128", "j", ("fig7_fig8.json", "usr.H.orders.64-128"), "{:.2f}", V("yes", 81, "41 (4.06)", "4.06")),
    ("Constraints", "USR: the same, 128 to 256", "j", ("fig7_fig8.json", "usr.H.orders.128-256", {"origin": "@all"}), "{:.2f}", V("yes", 201, "4.03 (row 42: 4.03, CONFIRMED)")),
    ("Constraints", "USR: largest record mean of |M|/[M] (256^3)", "q", (RES, 326, "2.519e-2"), None, V("yes", 81, "43 (2.519e-2)")),
    ("Constraints", "Paper II: Hamiltonian violation", "p", ("II", 539, r"($\sim 10^{-10}$)"), None, QP),
    ("Constraints", "Paper II, Fig. 8a read off: SR plateau of <|H|/[H]>", "q", (RES, 219, "about 2e-11"), None, V("rerun", 97, "45, 46")),
    ("Constraints", "Momentum constraint second order from (cells per shortest wavelength)", "q", ("tracks/E-stoch-inf/a4res/README.md", 85, "at least 12.8 cells"), None, V("rerun", 97, "45, 46")),
    ("Per-cell constraints", "USR, per cell (256^3): largest 99.5th percentile of |H|/[H] over the dumps", "j", ("fig4_usr_contrast.json", "pct_H_p99_max"), "{:.1e}", V("rerun", 96, "42 (my subset of dumps gives 1.98e-11")),
    ("Per-cell constraints", "SR, per cell (256^3): 99.5th percentile of |H|/[H] on the entry plateau, lowest and highest", "jd", ("fig2_sr_contrast.json", lambda d: ", ".join("{:.2e}".format(f(win(d, "pct_H", "p995", 0.75, 3.2))) for f in (min, max))), None, JOINED),
    ("Per-cell constraints", "SR, per cell: largest 99.5th percentile of |H|/[H] over the dumps, and its N", "jd", ("fig2_sr_contrast.json", lambda d: "{:.2e} at N = {:.2f}".format(*argmax(d, "pct_H", "p995"))), None, JOINED),
    ("Per-cell constraints", "SR, per cell: largest |H|/[H] over the cells and dumps", "j", ("fig2_sr_contrast.json", "pct_H_max_max"), "{:.2e}", JOINED),
    ("Per-cell constraints", "SR, per cell: 99.5th percentile of |H|/[H] at N_f", "jd", ("fig2_sr_contrast.json", lambda d: "{:.2e}".format(d["pct_H"]["p995"][-1])), None, JOINED),
    ("Per-cell constraints", "SR, per cell: fall of that percentile from its largest value to N_f", "jd", ("fig2_sr_contrast.json", lambda d: "{:.1e}".format(max(d["pct_H"]["p995"]) / d["pct_H"]["p995"][-1])), None, JOINED),
    ("Per-cell constraints", "SR, per cell: largest 99.5th percentile of |M|/[M] over the dumps, and its N", "jd", ("fig2_sr_contrast.json", lambda d: "{:.2e} at N = {:.2f}".format(*argmax(d, "pct_M", "p995"))), None, JOINED),
    ("Per-cell constraints", "SR, per cell: largest |M|/[M] over the cells and dumps", "j", ("fig2_sr_contrast.json", "pct_M_max_max"), "{:.2e}", JOINED),
    ("Per-cell constraints", "SR: dump means of |H|/[H] and |M|/[M] against the record, largest relative difference", "jd", ("fig2_sr_contrast.json", lambda d: "{:.1e}, {:.1e}".format(d["reader_check"]["max_rel_H"], d["reader_check"]["max_rel_M"])), None, V("yes", 271, "4.1e-15, my [H] equals Hmag", "4.1e-15 (H)")),
    ("Per-cell constraints", "SR: largest record mean of |H|/[H] over the whole run, and its N", "jd", ("fig_signflip.json", lambda d: "{:.2e} at N = {:.2f}".format(d["RNC256"]["proper_H_max_run"], d["RNC256"]["proper_N_at_H_max_run"]), {"origin": "@rsf256"}), None, V("yes", 272, "largest <abs H/[H]> 5.10e-11 (N = 4.43)", "5.10e-11 at N = 4.43")),
    ("Sign flip", "Sign flipped, SR: ratio of <|H|/[H]> to the proper run, smallest for 0.5 <= N <= ln 64", "j", ("fig_signflip.json", "RNC256.H_ratio_min_entry"), "{:.1e}", V("yes", 181, "| 1.386e3 at N = 4.158", "1.386e3; over the whole flipped run 2.66e2")),
    ("Sign flip", "Sign flipped, SR: median ratio of <|H|/[H]>", "j", ("fig_signflip.json", "RNC256.H_ratio_median_entry"), "{:.1e}", V("yes", 180, "| 1.055e5 over 0.5 <= N <= ln 64", "1.055e5")),
    ("Sign flip", "Sign flipped, SR: largest <|M|/[M]>", "j", ("fig_signflip.json", "RNC256.M_flip_max"), "{:.2f}", V("yes", 179, "| 0.2159 at N = 4.18", "0.2159")),
    ("Sign flip", "Sign flipped, SR: largest <|H|/[H]>", "j", ("fig_signflip.json", "RNC256.H_flip_max"), "{:.1e}", V("yes", 178, "| 9.907e-8 at N = 0.32", "9.907e-8")),
    ("Sign flip", "Sign flipped, SR: N at the end of the flipped run", "j", ("fig_signflip.json", "RNC256.N_end_flip"), "{:.2f}", V("yes", 177, "| 4.3876 (t = 4.5)", "4.3876")),
    ("Sign flip", "Sign flipped, USR: median ratio of <|H|/[H]>", "j", ("fig_signflip.json", "U256nc.H_ratio_median_entry"), "{:.1e}", V("diff", 87, "49 (1.0e4)", "1.0e4")),
    ("Sign flip", "Sign flipped, USR: largest <|M|/[M]>", "j", ("fig_signflip.json", "U256nc.M_flip_max"), "{:.2f}", V("yes", 81, "50 (0.50)")),
    ("Sign flip", "Sign flipped, USR: largest <|H|/[H]>", "j", ("fig_signflip.json", "U256nc.H_flip_max"), "{:.1e}", V("yes", 54, "Absolute flipped H/[H] about 1e-7", "about 1e-7")),
    ("Sign flip", "Paper II: a flipped sign gives", "p", ("II", 541, r"${\cal H}/[{\cal H}]\sim 10^{-5}$ and  ${\cal M}/[{\cal M}]\sim 1$"), None, QP),
    # --- extrinsic curvature
    ("Extrinsic curvature", "SR: Delta[K] at N_f over N = 5.3 (median over shells)", "j", ("fig6a_sr_Kspec_P256v6.json", "K_last_over_N55.median"), "{:.3f}", V("rerun", 97, "54-60")),
    ("Extrinsic curvature", "SR: Delta[Kt] at N_f over N = 4.4 (median)", "j", ("fig6a_sr_Kspec_P256v6.json", "Kt_last_over_N45.median"), "{:.1e}", V("rerun", 97, "54-60")),
    ("Extrinsic curvature", "SR: Q/K at N_f (median)", "j", ("fig6a_sr_Kspec_P256v6.json", "Q_over_K_last.median"), "{:.1e}", V("rerun", 97, "54-60")),
    ("Extrinsic curvature", "USR: Delta[K] at N_f over its maximum (median)", "j", ("fig6b_usr_Kspec.json", "K_last_over_max.median"), "{:.1e}", V("rerun", 97, "54-60")),
    ("Extrinsic curvature", "USR: Q/K at N_f (median)", "j", ("fig6b_usr_Kspec.json", "Q_over_K_last.median"), "{:.1e}", V("rerun", 97, "54-60")),
    ("Extrinsic curvature", "USR: shells with Q below K, N = 0.26-3.05", "q", (RES, 176, "below 0.2 for 0.26 <= N <= 3.05"), None, V("rerun", 97, "54-60")),
    ("Extrinsic curvature", "USR: shells with Q below K from N = 7.27", "q", (RES, 177, "0.98-1.0 from N = 7.27 to N_f"), None, V("rerun", 97, "54-60")),
    # --- convergence
    ("Convergence", "SR spectra: largest |1 - Delta_NR/Delta_lin|, 32^3", "j", ("fig7_fig8.json", "specconv.32.max"), "{:.1e}", V("yes", 212, "| 3.17e-3 | 6.16e-5 | 1.00e-6 | 2.0e-7 |", "3.17e-3 against the code's record")),
    ("Convergence", "the same, 64^3", "j", ("fig7_fig8.json", "specconv.64.max"), "{:.1e}", V("yes", 212, "| 3.17e-3 | 6.16e-5 | 1.00e-6 | 2.0e-7 |", "6.16e-5 against the code's record")),
    ("Convergence", "the same, 128^3", "j", ("fig7_fig8.json", "specconv.128.max"), "{:.1e}", V("yes", 212, "| 3.17e-3 | 6.16e-5 | 1.00e-6 | 2.0e-7 |", "1.00e-6 against the code's record")),
    ("Convergence", "the same, 256^3", "j", ("fig7_fig8.json", "specconv.256.max", {"origin": "@256"}), "{:.1e}", V("diff", 212, "| 3.17e-3 | 6.16e-5 | 1.00e-6 | 2.0e-7 |", "2.0e-7 (ln chi; both hemispheres)")),
    ("Convergence", "order of that departure, 128 to 256", "j", ("fig7_fig8.json", "specconv.128.max", "log2/", "specconv.256.max", {"origin": "@all"}), "{:.2f}", V("diff", 220, "row 69 (order 1.48) NOT CONFIRMED: 2.3 (lockstep)", "2.3 (ln chi; both hemispheres)")),
    ("Convergence", "SR spectra: per-mode rms, 128^3", "j", ("fig7_fig8.json", "specconv.128.per_mode_rel_rms"), "{:.1e}", V("diff", 214, "| 4.0e-7 / 3.73e-7 | 3.3e-7 / 3.73e-7 |", "4.0e-7 (ln chi)")),
    ("Convergence", "the same, 256^3", "j", ("fig7_fig8.json", "specconv.256.per_mode_rel_rms", {"origin": "@256"}), "{:.1e}", V("diff", 214, "| 4.0e-7 / 3.73e-7 | 3.3e-7 / 3.73e-7 |", "3.3e-7 (ln chi)")),
    ("Convergence", "read with ln chi: largest departure, 256^3", "r", ("reader_split.json", "256.D.shell_max_indep_gt10"), "{:.1e}", V("diff", 212, "| 3.17e-3 | 6.16e-5 | 1.00e-6 | 2.0e-7 |", "2.0e-7 (both hemispheres)")),
    ("Convergence", "its order, 128 to 256, read with ln chi", "r", ("reader_split.json", "128.D.shell_max_indep_gt10", "log2/", "256.D.shell_max_indep_gt10"), "{:.2f}", V("diff", 220, "row 69 (order 1.48) NOT CONFIRMED: 2.3 (lockstep)", "2.3 (both hemispheres)")),
    ("Convergence", "per-mode rms read with ln chi, 128^3 and 256^3", "r", ("reader_split.json", ["128.D.permode_rms", "256.D.permode_rms"]), "{:.1e}", V("yes", 214, "| 4.0e-7 / 3.73e-7 | 3.3e-7 / 3.73e-7 |", "4.0e-7, 3.3e-7")),
    ("Convergence", "per-mode rms of the change of reader (ln chi for chi), 128^3 and 256^3", "r", ("reader_split.json", ["128.rms_C_minus_A", "256.rms_C_minus_A"]), "{:.2e}", NONE),
    ("Convergence", "SR <|H|/[H]>: plateau ratios 64/32, 128/64, 256/128", "j", ("fig7_fig8.json", ["sr.H.orders_time_matched.32-64", "sr.H.orders_time_matched.64-128", "sr.H.orders_time_matched.128-256"], "pow2neg", {"origin": "@all"}), "{:.2f}", V("yes", 194, "| 0.186 | 1.167 | 1.109 |", "0.186, 1.167, 1.109")),
    ("Convergence", "SR <|M|/[M]>: the same", "j", ("fig7_fig8.json", ["sr.M.orders_time_matched.32-64", "sr.M.orders_time_matched.64-128", "sr.M.orders_time_matched.128-256"], "pow2neg", {"origin": "@all"}), "{:.2f}", V("yes", 195, "| 0.875 | 1.005 | 1.123 |", "0.875, 1.005, 1.123")),
    ("Convergence", "USR <|M|/[M]>: the same", "j", ("fig7_fig8.json", ["usr.M.orders_time_matched.32-64", "usr.M.orders_time_matched.64-128", "usr.M.orders_time_matched.128-256"], "pow2neg", {"origin": "@all"}), "{:.2f}", V("yes", 196, "| 0.783 | 1.002 | 1.073 |", "0.783, 1.002, 1.073")),
    ("Convergence", "USR <|H|/[H]>, box mean removed: the same", "j", ("fig7_fig8.json", ["usr.H0.orders_time_matched.32-64", "usr.H0.orders_time_matched.64-128", "usr.H0.orders_time_matched.128-256"], "pow2neg", {"origin": "@all"}), "{:.2f}", V("yes", 197, "| 0.342 | 0.995 | 1.031 |", "0.342, 0.995, 1.031")),
    # --- backreaction
    ("Backreaction", "USR level 2 against 0: rms over the shells at N_f", "j", ("fig9_ablation.json", "r20_usr.rms"), "{:.1e}", V("yes", 81, "67 (1.04e-4)", "1.04e-4")),
    ("Backreaction", "USR level 2 against 0: largest shell", "j", ("fig9_ablation.json", "r20_usr.max"), "{:.1e}", V("yes", 248, "(ledger row 77, 7.0e-4: CONFIRMED with it)", "7.03e-4; 9.15e-4 over all shells")),
    ("Backreaction", "USR level 2 against 0: fraction of shells positive", "j", ("fig9_ablation.json", "r20_usr.frac_pos"), "{:.2f}", V("yes", 82, "69 (0.52)")),
    ("Backreaction", "SR level 2 against 0 at N = 7.19: largest shell", "j", ("fig9_ablation_sr_t75.json", "r20_sr.max"), "{:.2e}", V("diff", 87, "70 (1.4e-4)", "1.4e-4 (all shells)")),
    ("Backreaction", "SR level 2 against 0 at N = 7.19: rms for |n| <= 32", "j", ("fig9_ablation_sr_t75.json", "r20_sr.rms_n_le_32"), "{:.3e}", V("diff", 88, "71 (1.75e-5)", "1.75e-5")),
    ("Backreaction", "SR level 2 against 0 at N_f: largest shell (shells of more than ten independent modes)", "j", ("fig9_ablation.json", "r20_sr.max", {"origin": "@al2s"}), "{:.2e}", V("yes", 242, "| 7.932e-5 at abs(n) = 4.47", "7.932e-5; 1.405e-4 over all shells")),
    ("Backreaction", "SR level 2 against 0 at N_f: rms for |n| <= 32 (the same shells)", "j", ("fig9_ablation.json", "r20_sr.rms_n_le_32", {"origin": "@al2s"}), "{:.3e}", V("yes", 243, "| 1.505e-5 (independent modes)", "1.505e-5")),
    ("Backreaction", "SR level 2 against 0 at N_f: fraction of shells positive", "j", ("fig9_ablation.json", "r20_sr.frac_pos", {"origin": "@al2s"}), "{:.2f}", V("yes", 244, "| 49.66 per cent |", "0.4966")),
    ("Backreaction", "SR level 1 against 0: largest shell", "j", ("fig9_ablation.json", "r10_sr.max"), "{:.1e}", V("yes", 82, "73 (6.6e-7)")),
    ("Backreaction", "USR level 1 against 0: largest shell", "j", ("fig9_ablation.json", "r10_usr.max"), "{:.1e}", V("yes", 82, "74 (7.0e-7)")),
    ("Backreaction", "level 0, noise on shells against on the mesh: largest SR shell", "j", ("fig9_ablation.json", "shells_vs_mesh_sr.max"), "{:.1e}", V("yes", 82, "75 (1.33e-2)", "1.33e-2")),
    ("Backreaction", "Paper II: bound on level 2 against 0", "p", ("II", 520, r"$\lesssim  1$\textpertenthousand"), None, QP),
    ("Backreaction", "Review: level 1 against 0 falls per halving of the step by a factor", "q", (CORE_MSG, 41, "falls by 16 per halving of the", "16"), None, V("rerun", 97, "77, 78, 100")),
    ("Backreaction", "Review: level 2 against 0 equals the level-2 curve to", "q", (CORE_MSG, 43, "the level-2 curve to 1 per cent", "1 per cent"), None, V("rerun", 97, "77, 78, 100")),
    # --- one patch
    ("One patch", "Euler 0.01 background crosses the junction at N_b", "l", ("backgrounds.euler01.N_cross_phi_c",), "{:.4f}", V("yes", 41, "Euler 0.01 crosses at 3.04353", "3.04353")),
    ("One patch", "converged background: field at N_b = 12 (the plateau stop)", "l", ("backgrounds.exact.phi_at_12",), "{:.5f}", V("yes", 40, "DOP853 rtol 1e-12: 9.0640187", "9.0640187")),
    ("One patch", "junction phi_c of the potential", "q", (LVR, 50, "phi_c = 9.056"), None, V("yes", 82, "79-82")),
    ("One patch", "Euler 0.005 background: field at N_b = 12", "l", ("backgrounds.euler005.phi_at_12",), "{:.5f}", V("yes", 40, "Euler 0.005: 9.05997")),
    ("One patch", "converged background: half the paths lost by N_b", "l", ("variants.bg_exact.N_half_dead",), "{:.2f}", V("diff", 88, "83 (paths half lost at 5.36-5.38 vs 4.80)", "5.36-5.38")),
    ("One patch", "Paper I: slope reached at", "p", ("I", 842, r"$\simeq 3.04$ efolds"), None, Q0),
    ("One patch", "Paper I: step of the scheme", "p", ("I", 842, r"$0.01$-efolds steps"), None, Q0),
    ("One patch", "Paper I: evolver named", "p", ("I", 836, "Stratonovich evolver"), None, Q0),
    ("One patch", "Ito reading, width of alpha at N_b = 4", "l", ("variants.ito_naive.at.4.std_a",), "{:.4f}", V("yes", 42, "Ito 0.1168, 0.1321, 0.1210", "0.1168")),
    ("One patch", "Ito reading, width of alpha at N_b = 6", "l", ("variants.ito_naive.at.6.std_a",), "{:.4f}", V("yes", 42, "Ito 0.1168, 0.1321, 0.1210", "0.1210")),
    ("One patch", "Ito reading, width of N - N_b at N_b = 6", "l", ("variants.ito_naive.at.6.std_D",), "{:.4f}", V("yes", 42, "Ito 0.0425, 0.1494, 0.1851", "0.1851")),
    ("One patch", "Stratonovich reading, width of alpha at N_b = 6", "l", ("variants.base.at.6.std_a",), "{:.4f}", V("yes", 42, "0.1450 (+19 % at 6)", "0.1450")),
    ("One patch", "Stratonovich reading, width of N - N_b at N_b = 6", "l", ("variants.base.at.6.std_D",), "{:.4f}", V("yes", 42, "0.2169", "0.2169")),
    ("One patch", "Paper I, figures read off: widths of alpha at 4, 5, 6", "q", (LVR, 77, "0.117, 0.133, 0.121"), None, V("yes", 42, "0.117, 0.133, 0.122", "0.117, 0.133, 0.122")),
    ("One patch", "Paper I, figures read off: width of N - N_b at 6", "q", (LVR, 78, "0.190"), None, V("yes", 42, "0.042, 0.150, 0.188", "0.188")),
    ("One patch", "Ito reading, median skewness of alpha, N_b in [4.5, 6]", "l", ("variants.ito_naive.median_4.5_6.skew_a",), "{:.2f}", V("diff", 42, "Ito 1.116 +- 0.012", "1.116 +- 0.012")),
    ("One patch", "Stratonovich reading, the same", "l", ("variants.base.median_4.5_6.skew_a",), "{:.2f}", V("yes", 42, "Stratonovich 1.562 +- 0.026", "1.562 +- 0.026")),
    ("One patch", "Paper I, figures read off: skewness of alpha", "q", (LVR, 78, "kappa3(alpha) ~ 1.1"), None, V("yes", 42, "P0 Fig. 2 about 1.1", "about 1.1")),
    ("One patch", "Stratonovich reading, mean of N - N_b at N_b = 6", "l", ("variants.base.at.6.mean_D",), "{:.3f}", V("yes", 42, "Stratonovich 0.084", "0.084")),
    ("One patch", "Ito reading, mean of N - N_b at N_b = 6", "l", ("variants.ito_naive.at.6.mean_D",), "{:.4f}", V("yes", 42, "Mean N - N_b at 6: Ito 0.003", "0.003")),
    ("One patch", "Ito reading at step 0.001, width of alpha at N_b = 4", "l", ("variants.naive_h001.at.4.std_a",), "{:.4f}", V("yes", 82, "95-99")),
    ("One patch", "linear check at N_b = 3: width of alpha, run over linear theory", "l", ("linear.3.run_std_a", "/", "linear.3.lin_std_a"), "{:.4f}", V("rerun", 97, "77, 78, 100")),
    ("One patch", "alpha^3 set to 1: skewness of alpha at N_b = 6", "l", ("variants.a3one.at.6.skew_a",), "{:.2f}", V("diff", 89, "101 (alpha^3 -> 1 skewness -0.74, one seed, vs -0.96)", "-0.74 (one seed)")),
    ("One-patch drift and noise amplitude", "Ito term: drift measured by Monte Carlo", "e", ("langevin/langevin.json", "mc.measured_drift"), "{:.4f}", V("yes", 43, "drift 0.32039 +- 0.00023 at alpha0 = 2", "0.32039 +- 0.00023")),
    ("One-patch drift and noise amplitude", "Ito term: standard error of that drift", "e", ("langevin/langevin.json", "mc.measured_drift_sem"), "{:.4f}", V("yes", 82, "102-105")),
    ("One-patch drift and noise amplitude", "Ito term: alpha^5 prediction", "e", ("langevin/langevin.json", "mc.pred_alpha5"), "{:.4f}", V("yes", 82, "102-105")),
    ("One-patch drift and noise amplitude", "Ito term: alpha^3 prediction (as printed)", "e", ("langevin/langevin.json", "mc.pred_alpha3_P0"), "{:.4f}", V("yes", 82, "102-105")),
    ("One-patch drift and noise amplitude", "Paper I: Ito term as printed", "p", ("I", 817, r"\frac{\alpha^3}{\dot{\phi_b}^2}"), None, Q0),
    ("One-patch drift and noise amplitude", "USR noise amplitude over printed, sigma = 0.1", "e", ("noise_amp/noise_amp.json", "USR.rows.2.amp_ibp_over_printed"), "{:.2e}", V("yes", 44, "3.3333e-3", "3.3333e-3")),
    ("One-patch drift and noise amplitude", "the same, sigma = 0.5", "e", ("noise_amp/noise_amp.json", "USR.rows.4.amp_ibp_over_printed"), "{:.2e}", V("yes", 44, "8.3332e-2", "8.3332e-2")),
    ("One-patch drift and noise amplitude", "SR noise amplitude over printed, sigma = 0.1", "e", ("noise_amp/noise_amp.json", "SR.rows.2.amp_ibp_over_printed"), "{:.3f}", V("diff", 44, "1.063 at sigma = 0.1 with eps1 = 0.0124, 1.123 with eps1 = 0.0244", "1.063 (eps1 = 0.0124), 1.123 (eps1 = 0.0244)")),
    ("One-patch drift and noise amplitude", "SR: eps1 of our background at that crossing", "e", ("noise_amp/noise_amp.json", "SR.rows.2.eps1"), "{:.1e}", NONE),
    # G2 package: the ultra-slow-roll case against criteria fixed before the runs
    ("Ultra-slow-roll criteria", "Background landmarks: largest |N - N_ref| over the runs, 256^3 and 320^3", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.2e}, {:.2e}".format(max(v["U_A0_max_dN"] for k, v in d["per_run"].items() if not k.startswith("R320")), max(v["U_A0_max_dN"] for k, v in d["per_run"].items() if k.startswith("R320")))), None, G("yes", 55, "1.61e-9 (256^3), 6.6e-10 (320^3)")),
    ("Ultra-slow-roll criteria", "Box means: largest relative departure from the Friedmann solution (lambda = 1)", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.2e}".format(d["per_run"]["A:U256"]["U_A1_max"])), None, G("yes", 56, "max over rows 4.17e-5", "4.17e-5")),
    ("Ultra-slow-roll criteria", "Departure per mode, k <= 32 dk, largest: first seed, second seed", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.4e}, {:.4e}".format(d["pairs"]["A"]["UA2p_max"], d["pairs"]["B"]["UA2p_max"])), None, G("yes", 57, "seed A 1.0894e-4", "1.0894e-4, 1.0871e-4")),
    ("Ultra-slow-roll criteria", "Departure per mode up to k_max, largest (first seed)", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.3e}".format(d["pairs"]["A"]["max_all_modes"])), None, G("yes", 57, "to k_max 4.506e-3 (both)", "4.506e-3")),
    ("Ultra-slow-roll criteria", "Freezing: power after over power at the crossing, k <= 3 dk, range (first seed, lambda = 1)", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.5f} to {:.5f}".format(d["per_run"]["A:U256"]["U_A3"]["min"], d["per_run"]["A:U256"]["U_A3"]["max"])), None, G("yes", 58, "single runs 0.99230-1.00161 (A)", "0.99230-1.00161")),
    ("Ultra-slow-roll criteria", "Factor of the even part of H (lambda = 1 over 1/2, fixed level), judged record times: range", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.4f} to {:.4f} ({} times)".format(d["UA4a_b"]["H"]["a_text"]["min"], d["UA4a_b"]["H"]["a_text"]["max"], d["UA4a_b"]["H"]["a_text"]["n"])), None, G("yes", 59, "H: 9 judged dumps (0, 5-12), 3.9916-4.0424", "3.9916-4.0424")),
    ("Ultra-slow-roll criteria", "Factor of the even part of M (fixed level): the one value outside 3.95-4.05, and its N", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.4f} at N = {:.2f} (of {} times)".format(d["UA4a_b"]["M"]["a_text"]["outside"][0], d["UA4a_b"]["M"]["a_text"]["outside_cN"][0], d["UA4a_b"]["M"]["a_text"]["n"])), None, G("yes", 59, "dump 13 (cN 6.525) = 3.9245", "3.9245")),
    ("Ultra-slow-roll criteria", "The same factor of M at that N from lambda = 1/2 over 1/4 (fixed level; not judged there)", "x", (G2Q, "judge_q.json", lambda d: "{:.4f}".format(d["Q_a"]["M_corr_quarter"])), None, G("yes", 85, "is 4.127 (not judged by 4c's own rule", "4.127")),
    ("Ultra-slow-roll criteria", "Level from three amplitudes (after the data; estimator sigma^2 = [rms(D1)^2 + rms(D2)^2]/34, the verifier's, D1 and D2 pooled): factor of M at that N", "x", (G2FL3, "floor3.json", lambda d: "{:.4f}".format(d["M_dump13"]["ratio_sigma_1h"])), None, G("own", 99, "dump 13 is 3.9988", "3.9988")),
    ("Ultra-slow-roll criteria", "Level from three amplitudes (same pooled estimator; with D1 alone, sigma^2 = rms(D1)^2/17, the gate review finds 3.99924 and 7.6e-4): largest |factor - 4| over the judged times, H and M", "x", (G2FL3, "floor3.json", lambda d: "{:.1e}, {:.1e}".format(d["H_1h"]["max_dev"], d["M_1h"]["max_dev"])), None, G("own", 100, "and +- 0.0012 (M)", "0.0045, 0.0012")),
    ("Ultra-slow-roll criteria", "Records: largest mean |H'|/[H] and |M|/[M] over the proper runs", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.2e}, {:.3f}".format(max(v["Hp_max"] for k, v in d["UA4c_records"].items() if k != "U256nc"), max(v["M_max"] for k, v in d["UA4c_records"].items() if k != "U256nc"))), None, G("yes", 61, "to 3.03e-12", "3.03e-12, 2.52e-2")),
    ("Ultra-slow-roll criteria", "Control (momentum source flipped): odd part of H over the proper one, ratio of the maxima over the entry", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.2e} (cross), {:.2e} (single)".format(d["UA4d_control"]["ratio_max_cross"], d["UA4d_control"]["ratio_max_single"])), None, G("yes", 62, "2.38e5 (control H' against the proper odd part", "2.38e5 (single)")),
    ("Ultra-slow-roll criteria", "Resolution: largest departure per mode (k <= 32 dk), 256^3 over 320^3", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.2f}".format(d["U_R"]["i_factor"])), None, G("yes", 63, "= 2.10", "2.10")),
    ("Ultra-slow-roll criteria", "Resolution: shell power 320^3 over 256^3 minus one, largest for k <= 32 dk and to 64 dk", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.2e}, {:.2e}".format(d["U_R"]["ii_max_k_le_32"], d["U_R"]["ii_max_to_64"])), None, G("yes", 64, "1.18e-4 (k <= 32 dk), 4.6e-3 (to 64 dk)", "1.18e-4, 4.6e-3")),
    ("Ultra-slow-roll criteria", "Resolution: median of the per-shell ratio of Fig. resolution for |n| <= 20 and |n| >= 40", "g", ("fig_g2_resolution.json", lambda d: "{:.3f}, {:.2f}".format(d["ratio_k_le_20_median"], d["ratio_k_ge_40_median"])), None, G("diff", 120, "factor 2.88, order 4.7", "2.88 (axis modes, third-order part removed)")),
    ("Ultra-slow-roll criteria", "Second seed: rms of R^NR at N_f (lattice reference 0.89366)", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.6f}".format(d["U_S"]["rms_bp"])), None, G("yes", 66, "band rms of U256bp 0.894109", "0.894109")),
    ("Ultra-slow-roll criteria", "Window: largest shift of the shell power over the windows, to 16 dk", "q", ("tracks/E-stoch-inf/window/JOURNAL.md", 217, "g2 1.87e-4", "1.87e-4 (to 16 dk)"), None, G("yes", 67, "1.870e-4, 9.13e-3 (g2)", "1.870e-4, 9.13e-3")),
    ("Ultra-slow-roll criteria", "Window: the same to 32 dk", "q", ("tracks/E-stoch-inf/window/JOURNAL.md", 218, "5.09e-4, 2.71e-4, 5.62e-3, 9.13e-3", "9.13e-3"), None, G("yes", 67, "1.870e-4, 9.13e-3 (g2)", "9.13e-3")),
    ("Ultra-slow-roll criteria", "Common mode of the odd-part error at N_f: lambda = 1 (256^3, 320^3)", "x", (G2JUDGE, "judge_g2.json", lambda d: "{:.3e}, {:.3e}".format(d["U_R"]["common_mode_256"]["mean_re"], d["U_R"]["common_mode_320"]["mean_re"])), None, G("yes", 114, "-4.107e-5, -9.87e-6, -2.07e-6", "-4.107e-5 (256^3)")),
    ("Ultra-slow-roll criteria", "Common mode at N_f: lambda = 1/2 and 1/4 (256^3)", "x", (G2Q, "judge_q.json", lambda d: "{:.3e}, {:.3e}".format(d["Q_b"]["common_mode_end_half"], d["Q_b"]["common_mode_end_quarter"])), None, G("yes", 114, "-4.107e-5, -9.87e-6, -2.07e-6", "-9.87e-6, -2.07e-6")),
    ("Ultra-slow-roll criteria", "Slice of Fig. mosaic: rms and largest R^NR over the lattice at N_f (first seed, lambda = 1)", "g", ("fig_g2_mosaic.json", lambda d: "{:.5f}, {:.3f}".format(d["rms_R"], d["max_R"])), None, NONE),
    # G3 package: tail statistics (scope 4d with its amendments); pair reading G3PAIRS, constraint G3C, resolution G3R
    ("Tail statistics", "Pairs read (mirrored, both boxes healthy) and boxes", "x", (G3PAIRS, "pairs.json", lambda d: "{} pairs, {} boxes".format(d["n_pairs"], 2 * d["n_pairs"])), None, NONE),
    ("Tail statistics", "Variance of zeta over the reference variance, minus one, with its standard error", "x", (G3PAIRS, "pairs.json", lambda d: "{:.2e} +- {:.1e} ({:.1f} s.e.)".format(d["V"]["ratio_minus_1"], d["V"]["se"], d["V"]["n_se"])), None, NONE),
    ("Tail statistics", "Variance of zeta over the lattice sum; reference variance over the lattice sum", "x", (G3PAIRS, "pairs.json", lambda d: "{:.5f} +- {:.5f}; {:.5f} +- {:.5f}".format(d["V"]["nr_var_over_lattice"], d["V"]["nr_var_over_lattice_se"], *d["V"]["ref_var_over_lattice"])), None, NONE),
    ("Tail statistics", "Skewness of zeta: lattice, one patch, difference in combined s.e.", "x", (G3PAIRS, "pairs.json", lambda d: "{:.5f} +- {:.5f}; {:.5f} +- {:.5f}; {:.1f}".format(d["T"]["skew"]["nr"], d["T"]["skew"]["nr_se"], d["T"]["skew"]["ref"], d["T"]["skew"]["ref_se"], d["T"]["skew"]["n_se"])), None, NONE),
    ("Tail statistics", "Excess kurtosis of zeta: lattice, one patch, difference in combined s.e.", "x", (G3PAIRS, "pairs.json", lambda d: "{:.4f} +- {:.4f}; {:.4f} +- {:.4f}; {:.1f}".format(d["T"]["exkurt"]["nr"], d["T"]["exkurt"]["nr_se"], d["T"]["exkurt"]["ref"], d["T"]["exkurt"]["ref_se"], d["T"]["exkurt"]["n_se"])), None, NONE),
    ("Tail statistics", "F_+(3) and F_-(3) over the Gaussian Q(3), own width: lattice; one patch", "x", (G3PAIRS, "pairs.json", lambda d: "{:.3f}, {:.3f}; {:.3f}, {:.3f}".format(d["T"]["Fp3"]["nr_Q"], d["T"]["Fm3"]["nr_Q"], d["T"]["Fp3"]["ref_Q"], d["T"]["Fm3"]["ref_Q"])), None, NONE),
    ("Tail statistics", "F_+(3), F_-(3): lattice over one patch minus one, in combined s.e.", "x", (G3PAIRS, "pairs.json", lambda d: "{:.1f}, {:.1f}".format(d["T"]["Fp3"]["n_se"], d["T"]["Fm3"]["n_se"])), None, NONE),
    ("Tail statistics", "F_+(4) and F_-(4) over Q(4), own width: lattice; one patch (importance sampled)", "x", (G3PAIRS, "pairs.json", lambda d: "{:.3f}, {:.3f}; {:.3f}, {:.3f}".format(d["T"]["Fp4"]["nr_Q"], d["T"]["Fm4"]["nr_Q"], d["T"]["Fp4"]["ref_Q"], d["T"]["Fm4"]["ref_Q"])), None, NONE),
    ("Tail statistics", "F_+(4), F_-(4): difference in combined s.e.", "x", (G3PAIRS, "pairs.json", lambda d: "{:.1f}, {:.1f}".format(d["T"]["Fp4"]["n_se"], d["T"]["Fm4"]["n_se"])), None, NONE),
    ("Tail statistics", "Asymmetry A(3): lattice, one patch, difference in combined s.e.", "x", (G3PAIRS, "pairs.json", lambda d: "{:.4f} +- {:.4f}; {:.4f} +- {:.4f}; {:.1f}".format(d["T"]["A3"]["nr"], d["T"]["A3"]["nr_se"], d["T"]["A3"]["ref"], d["T"]["A3"]["ref_se"], d["T"]["A3"]["n_se"])), None, NONE),
    ("Tail statistics", "Asymmetry A(4): lattice, one patch, difference in combined s.e.", "x", (G3PAIRS, "pairs.json", lambda d: "{:.3f} +- {:.3f}; {:.4f} +- {:.4f}; {:.1f}".format(d["T"]["A4"]["nr"], d["T"]["A4"]["nr_se"], d["T"]["A4"]["ref"], d["T"]["A4"]["ref_se"], d["T"]["A4"]["n_se"])), None, NONE),
    ("Tail statistics", "Skewness of R^NR (pair mean) and its s.e.", "x", (G3PAIRS, "pairs.json", lambda d: "{:.5f} +- {:.5f}".format(d["nr"]["R_skew"][0], d["nr"]["R_skew"][1])), None, NONE),
    ("Tail statistics", "Standard error of the skewness of zeta: single boxes over pairs (mirroring gain)", "x", (G3PAIRS, "pairs.json", lambda d: "{:.1f}".format(d["mirror"]["gain"])), None, NONE),
    ("Tail statistics", "Even part per pair: quadratic coefficient a of zeta and of R^NR (mean, pair-to-pair sd)", "x", (G3PAIRS, "pairs.json", lambda d: "{:.3e} (sd {:.1e}); {:.2e} (sd {:.1e})".format(d["A5"]["a_zeta"][0], d["A5"]["a_zeta"][2], d["A5"]["a_R"][0], d["A5"]["a_R"][2])), None, NONE),
    ("Tail statistics", "Even part per pair: F_+(3) of the + box minus F_-(3) of the - box, over Q(3)", "x", (G3PAIRS, "pairs.json", lambda d: "{:.3f} +- {:.3f}".format(*d["A5"]["Fp_plus_minus_Fm_minus_3_Q"][:2])), None, NONE),
    ("Tail statistics", "Constraints, three amplitudes: largest |factor - 4| over the judged records, H and M", "x", (G3C, "g3c.json", lambda d: "{:.1e}, {:.1e}".format(max(d["verdict"]["H"]["f_a"]["max_dev"], d["verdict"]["H"]["f_b"]["max_dev"]), max(d["verdict"]["M"]["f_a"]["max_dev"], d["verdict"]["M"]["f_b"]["max_dev"]))), None, NONE),
    ("Tail statistics", "Resolution 128 to 160: factor of the largest departure of the first-order part; median per-mode ratio", "x", (G3R, "g3r.json", lambda d: "{:.2f}; {:.2f}".format(d["L"]["factor_max"], d["L"]["median_of_ratio"])), None, NONE),
]


def win(d, key, q, lo, hi):
    """Values of percentile q of panel key at the dumps with lo <= N <= hi."""
    return [v for n, v in zip(d[key]["N"], d[key][q]) if lo <= n <= hi]


def argmax(d, key, q):
    """Largest value of percentile q of panel key over the dumps, and the N of that dump."""
    v = d[key][q]
    i = max(range(len(v)), key=v.__getitem__)
    return v[i], d[key]["N"][i]


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


CHECK_WORD = {"yes": "yes", "diff": "differs", "reach": "beyond reach", "quote": "quote",
              "rerun": "rerun only", "joined": "run joined", "own": "verifier's run", "none": "none"}


def read_line(path, line):
    """A committed line of the repository, or of a branch for paths given as git:<ref>:<path>."""
    if path.startswith("git:"):
        ref, gpath = path[4:].split(":", 1)
        body = subprocess.run(["git", "-C", REPO, "show", f"{ref}:{gpath}"], check=True,
                              capture_output=True, text=True).stdout
        path = f"{gpath} (branch {ref})"
    else:
        body = open(os.path.join(REPO, path)).read()
    return path, body.split("\n")[line - 1]


def check_text(ck):
    """The check column: the verifier's verdict, its value where it gives one, and the line of its report."""
    code, line, needle, shown = ck[:4]
    report = ck[4] if len(ck) > 4 and ck[4] else VERIFIER
    if code == "none":
        return "none", ""
    _, text = read_line(report, line)
    if needle not in text:
        sys.exit(f"verifier string not on its line: {report}:{line}: {needle!r}")
    word = CHECK_WORD[code]
    return word, (f"{word}: {shown}" if shown else word) + f" [{line}]"


def main():
    out = sys.argv[1]
    run_id = os.path.basename(os.path.normpath(out))
    os.makedirs(os.path.join(out, "tables"), exist_ok=True)
    cache = {}
    sha_ok(EQDIR, "langevin/langevin.json")
    sha_ok(EQDIR, "noise_amp/noise_amp.json")
    sha_ok(R8ADIR, "reader_split.json")
    rows = []
    for sec, qty, kind, args, fmt, ck in ROWS:
        if kind == "j":
            opts = args[-1] if isinstance(args[-1], dict) else {}
            if opts:
                args = args[:-1]
            fn, path = args[:2]
            p = os.path.join(out, "lattice", fn)
            d = cache.setdefault(p, json.load(open(p)))
            if len(args) == 4 and args[2] == "log2/":      # order between two values
                val = fmt.format(math.log2(get_dotted(d, path) / get_dotted(d, args[3])))
            elif len(args) == 3 and args[2] == "pow2neg":  # log2(coarser/finer) -> finer/coarser
                val = ", ".join(fmt.format(2.0 ** -get_dotted(d, q)) for q in path)
            else:
                val = fmt.format(get_dotted(d, path))
            src = f"this run ({run_id}) from {ORIGIN[fn + opts.get('origin', '')]}"
        elif kind == "jd":
            opts = args[-1] if isinstance(args[-1], dict) else {}
            fn, func = args[:2]
            p = os.path.join(out, "lattice", fn)
            d = cache.setdefault(p, json.load(open(p)))
            val = func(d)
            src = f"this run ({run_id}) from {ORIGIN[fn + opts.get('origin', '')]}"
        elif kind == "x":
            rid, fn, func = args
            rdir = os.path.join(SCR, rid)
            p = os.path.join(rdir, fn)
            if p not in cache:
                sha_ok(rdir, fn)
                cache[p] = json.load(open(p))
            val = func(cache[p])
            src = f"run {rid}"
        elif kind == "g":
            fn, func = args
            p = os.path.join(out, "g2", fn)
            d = cache.setdefault(p, json.load(open(p)))
            val = func(d)
            src = f"this run ({run_id}) from {G2ORIGIN[fn]}"
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
        elif kind == "r":
            p = os.path.join(R8ADIR, args[0])
            d = cache.setdefault(p, json.load(open(p)))
            if len(args) == 4 and args[2] == "log2/":
                val = fmt.format(math.log2(get_dotted(d, args[1]) / get_dotted(d, args[3])))
            elif isinstance(args[1], list):
                val = ", ".join(fmt.format(get_dotted(d, q)) for q in args[1])
            else:
                val = fmt.format(get_dotted(d, args[1]))
            src = f"run {R8A}"
        elif kind == "q":
            path, line, s = args[:3]
            path, text = read_line(path, line)
            if s not in text:
                sys.exit(f"quote not on its line: {path}:{line}: {s!r}")
            val = args[3] if len(args) > 3 else s
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
        code, ctext = check_text(ck)
        rows.append((sec, qty, val, src, code, ctext))
    with open(os.path.join(out, "tables", "ledger.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "quantity", "value", "source", "check", "check_detail"])
        w.writerows(rows)
    # LaTeX: one table per section; values in \texttt where they are printed strings
    secs = []
    for r in rows:
        if r[0] not in secs:
            secs.append(r[0])
    lines = []
    for k, sec in enumerate(secs):
        lab = "ledger" + "".join(c for c in sec.lower() if c.isalpha())
        lines += [r"\begin{table*}", r"\caption{Ledger, " + sec.lower() + ". " + SECNOTE[sec]
                  + r" Each value with its source (a registered run, a committed line of the program's"
                  r" records, or a line of a paper's source) and the independent check (Appendix~\ref{app:ledger}).}",
                  r"\label{tab:" + lab + "}", r"\footnotesize",
                  r"\begin{tabular}{p{0.29\textwidth}p{0.14\textwidth}p{0.17\textwidth}p{0.29\textwidth}}",
                  r"\toprule", r"Quantity & Value & Check & Source \\", r"\midrule"]
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
            c = tex_escape(r[5]) if r[5] else "---"
            s = tex_escape(r[3])
            lines.append(f"{q} & {v} & {c} & {s} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}", ""]
    with open(os.path.join(out, "tables", "ledger.tex"), "w") as f:
        f.write("\n".join(lines))
    counts = {w: sum(1 for r in rows if r[4] == w) for w in CHECK_WORD.values()}
    with open(os.path.join(out, "tables", "ledger_checks.json"), "w") as f:
        json.dump(counts, f, indent=1)
    print(f"ledger: {len(rows)} rows in {len(secs)} tables; checks {counts}")


if __name__ == "__main__":
    main()
