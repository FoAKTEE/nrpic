# Stage report: A-emd-pbh G1

Date: 2026-11-21 · branch `track/A-emd-pbh` at `72ac63ceae80` · checklist
`tracks/A-emd-pbh/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/A-emd-pbh/G1-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C20 FAIL
- verify reported FAIL: clean, runs

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | present |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
| `stage/G1/VERIFIER.md` (verifier's report) | present |
| `stage/G1/REVIEW.md` | present |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | stage/G1/STATUS.md section 2: expball exact solution and data sets (A-emd-pbh-20261115-121749-90764e1, -121753-90764e1, -130609-947c898), newton references (-113103-9832afd), criteria (-115120-2eb3117), gauge toys (-113614-374a41a, -113755-cac3c4b) | PASS |
| C2 | The analysis pipeline validated on them | stage/G1/STATUS.md section 2 (wave 2): runs_ball/compare.py recovers the exact expanding ball in AthenaK runs (core /R/R_exact - 1/ 7.6e-4 at tau = 16.894, dx = M/4; analysis A-20261115-182657-53da696), re-derived by the lead's own reader (A-20261115-182314-bebd0cf); newton/analyze_newton.py against the cycloid and the ellipsoid on Newtonian-mode runs (A-emd-pbh-20261115-164420-4528861, rerun A-20261115-182402-a46812c identical); periodic analyse_scouting.py reproduced byte for byte (A-20261115-182347-8ee3fcc); wave-1 snapshot analysis on synthetic snapshots (A-emd-pbh-20261115-113822-87cba08) | PASS |
| C3 | Interface proposals submitted | outbox 20261115T1320Z__* (wave 1, 7 messages) and the wave-2 requests of this session (outbox 20261115T18*Z__*) | PASS |
| C4 | Baseline data and figures | expball/figures/, newton/figs/, gauge/figs/, scope/results/ from registered runs; data in scratch/A-emd-pbh/<run_id>/ | PASS |
| C5 | Interface documents | stage/G1/STATUS.md section 3 (scouting-run specification); newton/SCAN.md sections 4-5; gauge/GAUGE.md, gauge/DIAGNOSTICS.md; outbox requests to core | PASS |
| C6 | The constraint residuals of A-pre-1 converge at the expected order | stage/G1/STATUS.md T1: A-emd-pbh-20261115-121654-6bfb707, -122121-aa1c84d, -122117-aa1c84d; rerun A-emd-pbh-20261115-130402-f5566fb identical; cross-checks A-20261115-130257-a7374a4 | PASS |
| C7 | The prediction table of A-pre-2 | stage/G1/STATUS.md T2: criteria/predict.py, runs A-emd-pbh-20261115-120425-80492f8, -115120-2eb3117 (wave 1: 33 of 37, failures on record); lead rerun A-20261115-130252-01e8b64; wave-2 state: A-emd-pbh-20261115-161813-6c820fb (all checks) and -163358-9b2d048 (T2 after the T2.6 fix): 41 of 41 pass, 4 diagnostics without a verdict, confirmed by the G1 verifier (VERIFIER.md 2.2) and recounted in A-20261120-222454-d16dbc6 (g1close) | PASS |
| C8 | The scan design from A-pre-3 | met by decision 0013 (reference-based design, newton/SCAN.md sections 1-6); wave 2 adds the Newtonian-mode runs: top-hat second order (t_ta +7.2e-4 at 128^3), first-collapse time t_1 of the 9 scan points at 128^3 with >= 2.7e5 particles other than the spindle within +2.2e-4 to +6.3e-4 of the isolated ellipsoid (spindle +1.5e-3; 64^3 controls +8.8e-4, +1.5e-3; 3.4e4-particle controls -2.4e-4, -4.6e-4; 14 points in all; sentence corrected 2026-11-20 after VERIFIER.md section 4 item 2, counted in run A-20261120-222454-d16dbc6), range of the full-relativity scan (SCAN.md section 8; runs A-emd-pbh-20261115-153409/-153415/-153437-dc27b98, -164420-4528861, -164757-b8bc9a3; lead's rerun A-20261115-182402-a46812c identical; own estimator A-20261115-182314-bebd0cf agrees) | PASS |
| C9 | Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013) | applied as at G0 (C9 there): T3 judged on the reference-based design, Newtonian-mode runs done as G2 work ahead of time; the ruling's reason corrected (verifier C1c; SCOPE.md 10.9(a); proposal to orch) | PASS |
| C10 | Schematic: Updated architecture | note/figures/schem_architecture.png (script note/scripts/schem_architecture.py), drawn in wave 2 after the release core-v0.3, so it is the current architecture (exists / to be ported / new); the wave-2 runs change no box of it [JUDGEMENT]; PNG looked at by the note helper | PASS |
| C11 | Schematic: Data-flow diagram | note/figures/schem_dataflow.png (script note/scripts/schem_dataflow.py, vendored paperfig.py): four lanes (expanding ball, periodic box, Newtonian mode, criteria and scope) from initial data through AthenaK and raw outputs to the analysis, products, common.py/ledger.py and main.pdf, with the registration of runs and the verifier's path; drawn by the G1 verifier (run A-20261119-143347-37240f3, commit e2999bb2); common.py box updated for the integrity listing (commit 2c115cb1); in the note as Fig. 7 with caption in App. B (commit 2c115cb1); regenerated in runs A-20261120-223316-92c27f5 and A-20261121-030037-3f015fa; PNG looked at (VERIFIER.md C11; g1close/JOURNAL.md entry 5) and on page 9 of note/main.pdf | PASS |
| C12 | Data figure: Baseline results | expball/figures/fig_exact_shells.png, fig_constraint_convergence.png; newton/figs/fig_scan_hoop_time.png; scouting predictions fig_scouting_predictions.png (A-20261115-130948-5a2b58a) | PASS |
| C13 | Data figure: Validation figures for the analysis pipeline | newton/figs/fig_axes_selftest.png; lead fig_crosscheck.png (A-20261115-130257-a7374a4) | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, STATUS.md (criterion by criterion), VERIFY (commands) in stage/G1; lead's re-check ../REVIEW-wave2.md; scoping text scope/SCOPE.md | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | as G0 C13 | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | as G0 C16: note/scripts/schem_architecture.py and schem_timeline.py with the vendored paperfig.py; the timeline brought to the wave-3 state (G0 passed, G1 at its review, what G2 needs) in run A-20261121-030037-3f015fa (commit 8b7304f5), PNG looked at | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | note v1 (12 pages, 2026-11-20): check_manuscript.py --compile on note/main.tex with the guide's --forbid list, 0 undefined references and citations, 0 overfull boxes; 5.5/5.8 candidates only in the ledger appendix and the scripts (WRITING_GUIDE.md exception 1; schem_dataflow.py and Fig. 7 still to be named in it, request to the lead); every page read (g1close/JOURNAL.md entries 6-7) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | stage/G1/VERIFIER.md by a fresh verifier of wave 2b (run A-20261119-142905-c813c01; predictions committed before any run, commit 2256c860; scripts c813c017; sections 1-3 written before reading the track's review, 37240f39; comparison section 4, db950ae8): own code for the note's ledger (42 rows: 39 confirmed, 2 wrong labels/statements, 1 not recomputed: the predicted card-hours of a cost model), the criteria checks (19 of 19), newton/ (17 of 17), runs_ball (12 of 12, SR-2 turnaround estimator-dependent), the note's statements (15 of 17). Its corrections, each checked at the source (run A-20261120-222454-d16dbc6) and applied or partly rebutted (g1close/JOURNAL.md entries 1-4): median label, bang time in the taper, units M_0, six threshold names, checksum sentence (integrity listing run A-20261120-222620-0304d9d), wave-2 state, STATUS T3/C8 band (9 points, not 4), SR-1 breakdown criterion, SR-2 estimator; commits d34bcb87, f26e7f58, 2c115cb1, 3f015fa0, 8b7304f5. Not recomputed by a fresh verifier (named in note App. B and OPEN.md item 1): the predicted card-hours, the four cross-check differences (read from crosscheck.json), and five rows added in note v1 to Table IV from the wave-2 analyses (tracked-particle residuals, constraint norm at t = 20, two central-lapse rows, compactness on the axes). Judged PASS on the scope the gate asked of the verifier (OPEN.md of wave 2, item 2: ledger, newton/, criteria/); a strict reading of "every number" leaves these rows open | PASS |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | as G0 C17 | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | stage/G1/STATUS.md brought to the wave-3 state by g1close (2026-11-20); the owner's STATUS.md, JOURNAL.md and HANDOFF.md were last changed on 2026-11-15 (git log) and still give G0 as not passed and the wave-1/2 statements the verifier corrected (STATUS.md line 13 "14 scan points within 6.3e-4"); the lead rewrites them at the end of wave 3 round 1 (helpers do not write them) | FAIL |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T03:22:02Z, clean export of `72ac63ceae80`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 4 uncommitted paths: commit them first (tracks/A-emd-pbh/periodic_threshold/JOURNAL.md, tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput, tracks/A-emd-pbh/periodic_threshold/scripts/ltb_reference.py, tracks/A-emd-pbh/periodic_threshold/scripts/ltbref.py) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 72ac63ceae80 (HEAD) in /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G1-72ac63c-20261121T032034Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 3 schematics and 4 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 4 of 167 runs have problems |
| run-notes | WARN | 45 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 9 of 9 scripts and commands ran cleanly in the export |
| compare | PASS | 14 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_ball_exact.* | note/scripts/fig_ball_exact.py | data | yes: PNG unchanged since wave 2 (note helper); page 6 of note v1 read (g1close entry 6) |
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | yes: PNG unchanged since wave 2 (note helper); page 5 of note v1 read (g1close entry 6) |
| note/figures/fig_criteria.* | note/scripts/fig_criteria.py | data | yes: PNG unchanged since wave 2 (note helper); page 3 of note v1 read (g1close entry 6) |
| note/figures/fig_landscape.* | note/scripts/fig_landscape.py | data | yes: PNG unchanged since wave 2 (note helper); page 2 of note v1 read (g1close entry 6) |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | yes: PNG unchanged since wave 2 (note helper); page 5 of note v1 read (g1close entry 6) |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | yes: PNG read (VERIFIER.md C11; g1close entry 5); page 9 of note v1 |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | yes: PNG read (g1close entries 6-7); page 8 of note v1 |

## Verifier report

`tracks/A-emd-pbh/stage/G1/VERIFIER.md` present; its first lines:

> # VERIFIER.md: independent verification for gate G1 of A-emd-pbh (checklist item C18)
> 
> Verifier of wave 2b, fresh context, 2026-11-19. Report name per decision 0016 item 1.
> Sections 1-3 were written and committed before I read the track's own review
> (`stage/REVIEW-wave2.md`, `stage/G1/REVIEW.md`, `STATUS.md`, `HANDOFF.md`, the journals);
> section 4 compares afterwards.
> 
> **What I read first.** CLAUDE.md; CHARTER.md to "Owners"; decisions 0010, 0016; the brief at
> S1 (335-365) and the track sheet (708-725); `stage/G1/CHECKLIST.md` (to know what C11 and C18
> ask); the working note `note/main.tex` with `tables/ledger.tex`, `parameters.tex`; the READMEs
> of `note/`, `criteria/`, `newton/`, `runs_ball/` and `newton/SCAN.md` section 7 (for the
> claims); the paper sources at the locators the note and the criteria cite; the formats of

## Null results and failed runs

- `A-20261115-125927-6d2c1e6`: failed (exit 1), lead rerun of the scope package T1-T5 (L1)
- `A-20261115-125932-574c747`: failed (exit 1), lead rerun of the gauge package (L1)
- `A-20261115-125932-5a90432`: failed (exit 0), lead rerun of the newton package (L1)
- `A-20261115-125932-b90223c`: failed (exit 1), lead rerun of the criteria package (L1)
- `A-20261115-125932-f221206`: failed (exit 1), lead rerun of the expball package (L1)
- `A-20261119-151452-46f171e`: failed (exit 1), Szekeres slice (eps=0.1 twisted dipole, and eps=0 LTB) in conformally flat Cartesian coordinates: finite-difference Hamiltonian and momentum residuals at N=32..256, orders 2 and 4 (JOURNAL P7)
- `A-20261119-155945-c09d40e`: failed (exit -15), Data set 3, lattice n_lat = 136 (h = M/16) with tracked particles, for BH-1R (one refined level); same data and exact references as A-20261119-143524-334e553
- `A-emd-pbh-20261115-112500-61acbec`: failed (exit None), G0 scoping: semi-analytic tests T1-T5 of tracks/A-emd-pbh/scope/JOURNAL.md (hoop criterion of 2609.14218, collapse times against top-hat shells, ball geometry, velocity-dispersion axis and particle floor, compute estimate from measured costs)
- `A-emd-pbh-20261115-115339-044312f`: stopped (exit None), G1 of A-pre-1: FD constraint residuals vs resolution (orders (2, 4), N = [32, 64, 128, 256]) and table interpolation error vs spacing
- `A-emd-pbh-20261115-115559-c4a583e`: stopped (exit None), A-pre-1: Hamiltonian-constraint noise of CIC-deposited particles vs N (N = [10000, 30000, 100000, 300000, 1000000], mesh 64^3)
- `A-emd-pbh-20261115-125932-574c747`: failed (recorded as 'failed (exit 1)') (exit None), lead rerun of P1-P7 (L1)
- `A-emd-pbh-20261115-125932-779f753`: failed (recorded as 'failed (exit 1)') (exit None), lead rerun of the snapshot self-test (L1)
- `A-emd-pbh-20261115-153856-9d731b1`: stopped (exit 143), SR-1 (geodesic slicing) of data set 2t on processors, dx = M (128^3 over [-64,64]^3), three segments with restarts (cfl 0.25 to 42.0, 0.03125 to 44.3568, 0.0078125 to 44.4472); release core-v0.3 processor executable
- `A-emd-pbh-20261115-153903-9d731b1`: stopped (exit 143), SR-2 (conformal-time lapse + Gamma-driver) of data set 2t on processors, dx = M (128^3 over [-64,64]^3), t = 0 -> 53; release core-v0.3 processor executable
- `A-emd-pbh-20261115-154356-527a6d1`: stopped (exit None), S1 initial data: peak mu = 0.5, e = 0.2, eps_i = 1, 64^3, one particle per cell (make_peak_ic.py)
- `A-emd-pbh-20261115-161253-b8c1dc9`: failed (exit 2), Analysis of the top-hat campaign A-emd-pbh-20261115-153409-dc27b98 against the cycloid (P9)
- `A-emd-pbh-20261115-161542-36e461d`: failed (exit None), A-pre-2: check the analytic criteria against numbers printed in 1609.01588, 1707.03595, 2211.13950, 2507.18312, 2508.10070
- `A-emd-pbh-20261115-162133-208f933`: failed (exit 1), analysis of SR-1 dx = M/2 segment 1 (run A-emd-pbh-20261115-153843-7172b66): comparison with the exact solution in invariants, field slices
- `A-emd-pbh-20261115-162237-a614467`: failed (exit 1), analysis of SR-1 dx = M/2 segment 1 (run A-emd-pbh-20261115-153843-7172b66): comparison with the exact solution in invariants, field slices (second attempt)
- `A-emd-pbh-20261115-162505-d32d331`: failed (exit 1), Test of analyse_scouting.py on the dry run S0

## Open risks


State 2026-11-15 (lead, end of wave 2). Likelihood and effect: H high, M medium, L low
[JUDGEMENT]. Sources: `scope/SCOPE.md` sections 8 and 10.9, `gauge/GAUGE.md`,
`stage/REVIEW-wave2.md`, the helpers' journals. "Realized" means a wave-2 run showed it.

| # | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| 1 | Lapse fronts: the conformal-time lapse sends a pulse from the edge of the bound core to the centre (central lapse 1.80-1.87 against 1.34 at dx = M, M/2, M/4; runs_ball, A-20261115-182314-bebd0cf) | realized | H: the core runs through its proper time too fast, no horizon | central lapse against a(tau_c) | lapse towards dust proper time, K_ref lapse (outbox gauge-expanding-ball) |
| 2 | Geodesic slicing with frozen shift unstable: SR-1 non-finite at t = 30.8 (dx = M), 33.1 (M/2), grid-scale growth at the core edge | realized | H for SR-1 | largest |H| (0.24 / 0.051 / 0.040 at t = 20) | not the slicing for collapse; keep for the expansion phase only |
| 3 | Time step ignores the coordinate light speed (v = R_i/R reaches 17 at the first trapped sphere in comoving coordinates) | H in SR-1 | M | staged cfl plan | step limit asked of core (outbox) |
| 4 | The ball holds the particle bracket of arXiv:2609.14218 only at q = 2 with the mean-contrast cap, not the hoop or fluid amplitudes (corrected after verifier C1c) | certain | M for the comparison | | threshold line in the periodic box (decision 0013; reason corrected, outbox decision-0013-reason) |
| 5 | Phase-1 capability missing: generator for the source data at its start epoch and mu >= 0.5, a slicing that survives collapse in a box, the finder in a box | H | H: G3 waits | core replies | requests sent; S1/S2 now show where it fails (rows 20-22) |
| 6 | Constraint violation at particle crossings (arXiv:2609.14218 MDPBH.tex:1148-1186) | H | H: spurious black holes below the hoop line (H2) | Hamiltonian norm outside the horizon | Z4c damping; two mesh spacings with damping on and off |
| 7 | Curvature at caustics does not converge (arXiv:1611.07906) | H | M | | outcomes from horizons and constraints |
| 8 | Particle noise halts or seeds collapse near threshold; lattice law N^(-4/9) has no fitted coefficient (verifier C6) | M | H | b_min against N | N convergence of every bracket |
| 9 | Threshold depends on the run length (H1); the comparison bracket at e = 0.2 sits on the cutoff mu_fd(250 t_H) = 0.048 (top-hat form; verifier weak point 2) | H | H | t_AH of every BH run | runs near the bracket to 400 t_H; A_c(t_end) with the cutoff stated |
| 10 | Two amplitude conventions (central 12 mu/5, mean in r_m 0.883 mu); linear measures poor for mu >~ 0.1 (crunch carries e^(3 mu)) | M | M | every table names its measure | criteria/predict.py amplitude_measures |
| 11 | Sharp ball edges: table interpolation deviates by up to 1.37 H at the jump (A-20261115-130257-a7374a4); constraints do not converge | M | M | | C^4 taper for all evolution data |
| 12 | Outflow boundary: a Theta signal enters from 32 M (seen at |x| = 20 at t = 16.9 in the dx = M/4 run) | certain | L-M | Theta near the matter edge | boundary beyond the light-travel distance |
| 13 | Finder spin biased in an expanding region | M | M for spin | test G-R4 | projected rotation vectors (request to core, wave 1) |
| 14 | Budget: first scan ~155 card-hours (band 50-470) against 60 to the next gate | H | M | nrpic-run budget | ask for the raise at G2 |
| 15 | Overlap with the authors of arXiv:2609.14218 | M | M | arXiv | H1 and the converged line first |
| 16 | Newtonian mode lacks the SR push and the deformed-ball generator in make_ic.py (core deferred); energy off by 1e-3 to 3e-2 at sub-cell crossings, cause unknown | M | L-M | newton/JOURNAL.md entry 8 | own generator meanwhile; question to core (newton-mode-followup) |
| 17 | G2 asks convergence of the horizon-formation time and a horizon-mass error ~1e-3; the source's OS test saw no monotonic convergence of the horizon mass (main.tex:1484-1485, verifier C7) | M | M: G2 criterion may be unreachable as written | | report the measured mass error with its N and dx dependence; ask orch if it stalls |
| 18 | First horizon of data set 2t (areal radius 0.161 M) is below one cell in non-comoving gauges (SR-2: largest 2m/R 0.34) | realized | H for the G2 horizon test | | data set with a horizon of several M; central refinement (outbox amr-for-first-horizon) |
| 19 | Non-finite runs keep going with exit 0 (S1 spent a third of its card time on non-finite fields) | realized | M: card time, misread outcomes | first non-finite record | stop option asked of core; every analysis checks finiteness |
| 20 | Periodic constraint control on refined levels: H_r max above 0.1 before collapse (S2 from 36 t_H; S1 0.16 at the first pancake) | realized | H: threshold definition's bound fails | L2 norms (not available on multilevel meshes) | refined-level solve, nested lattice, diagnostics (outbox) |
| 21 | Adaptive refinement crashes with nrpic_cosmo (user_ref_func never set) | certain until fixed | H for the scan cost | | one-line fix asked of core |
| 22 | Periodic generator: make_field has a first-order super-horizon error and fails for mu >= 0.5; the CMC route diverges at mu = 0.5 | certain | H | | Newton step in core's id-solver (outbox phase1-generator-cmc) |

## Decision requested from the group

Lead of A-emd-pbh (text of the wave-3 g1close helper, 2026-11-20, for the lead to revise): the three track criteria of G1 are met (T1 constraint orders 2 and 4; T2 prediction table, criteria checks 41 of 41 with 4 diagnostics; T3 by decision 0013, with the Newtonian-mode runs made as well) and the analysis pipeline is validated on AthenaK runs. The two items missing after wave 2 are closed: C11 (data-flow schematic, Fig. 7 of note v1) and C18 (fresh verifier, VERIFIER.md, run A-20261119-142905-c813c01; its corrections applied or rebutted, g1close/JOURNAL.md). Still open: C20 (the owner's STATUS/JOURNAL/HANDOFF are rewritten by the lead at the end of this round); five rows added to the note's Table IV that no fresh verifier recomputed (OPEN.md item 2); the verify failures clean and runs come from other helpers' work in progress (OPEN.md). Request: an independent gate review (GATE_REVIEW.md) once C20 is done; the lead does not pass the gate.
