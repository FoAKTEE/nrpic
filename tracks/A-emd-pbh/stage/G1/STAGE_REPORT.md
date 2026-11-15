# Stage report: A-emd-pbh G1

Date: 2026-11-15 · branch `track/A-emd-pbh` at `2b756f503362` · checklist
`tracks/A-emd-pbh/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/A-emd-pbh/G1-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 2 checklist items not PASS or NA: C11 FAIL, C18 FAIL
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | present |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
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
| C7 | The prediction table of A-pre-2 | stage/G1/STATUS.md T2: criteria/predict.py, runs A-emd-pbh-20261115-120425-80492f8, -115120-2eb3117 (33/37, failures on record); lead rerun A-20261115-130252-01e8b64 | PASS |
| C8 | The scan design from A-pre-3 | met by decision 0013 (reference-based design, newton/SCAN.md sections 1-6); wave 2 adds the Newtonian-mode runs: top-hat second order (t_ta +7.2e-4 at 128^3), 14 scan points within 2.2e-4 to 6.3e-4 of the isolated ellipsoid, range of the full-relativity scan (SCAN.md section 8; runs A-emd-pbh-20261115-153409/-153415/-153437-dc27b98, -164420-4528861, -164757-b8bc9a3; lead's rerun A-20261115-182402-a46812c identical; own estimator A-20261115-182314-bebd0cf agrees) | PASS |
| C9 | Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013) | applied as at G0 (C9 there): T3 judged on the reference-based design, Newtonian-mode runs done as G2 work ahead of time; the ruling's reason corrected (verifier C1c; SCOPE.md 10.9(a); proposal to orch) | PASS |
| C10 | Schematic: Updated architecture | note/figures/schem_architecture.png (script note/scripts/schem_architecture.py), drawn in wave 2 after the release core-v0.3, so it is the current architecture (exists / to be ported / new); the wave-2 runs change no box of it [JUDGEMENT]; PNG looked at by the note helper | PASS |
| C11 | Schematic: Data-flow diagram | no data-flow diagram drawn (initial data -> AthenaK -> outputs -> comparison scripts -> ledger); to be drawn with paperfig.py (HANDOFF next actions) | FAIL |
| C12 | Data figure: Baseline results | expball/figures/fig_exact_shells.png, fig_constraint_convergence.png; newton/figs/fig_scan_hoop_time.png; scouting predictions fig_scouting_predictions.png (A-20261115-130948-5a2b58a) | PASS |
| C13 | Data figure: Validation figures for the analysis pipeline | newton/figs/fig_axes_selftest.png; lead fig_crosscheck.png (A-20261115-130257-a7374a4) | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, STATUS.md (criterion by criterion), VERIFY (commands) in stage/G1; lead's re-check ../REVIEW-wave2.md; scoping text scope/SCOPE.md | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | as G0 C13 | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | as G0 C16: note/scripts/schem_architecture.py and schem_timeline.py with the vendored paperfig.py | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | as G0 C17: check_manuscript.py --compile on note/main.tex, 0 undefined references and citations, 0 overfull boxes | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | VERIFIER.md (stage/G0) checks the G1 criteria T1 (its C5: constraint orders 2 and 4 recomputed with its own construction of data set 2t) and T2 in part (C2, C3); it did not examine newton/ (T3) or the criteria package's 37 checks; the lead's independent checks (../REVIEW-wave2.md) are not a fresh verifier's; the note's ledger is not recomputed by a verifier (as G0 C18) | FAIL |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | as G0 C17 | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten in the lead session of wave 2 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T18:52:25Z, clean export of `510fdb96b213`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 510fdb96b213 (HEAD) in /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G1-510fdb9-20261115T184941Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | PASS | 130 run manifests finished (102 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 8 of 8 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_ball_exact.* | note/scripts/fig_ball_exact.py | data | to be confirmed by the session |
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_criteria.* | note/scripts/fig_criteria.py | data | to be confirmed by the session |
| note/figures/fig_landscape.* | note/scripts/fig_landscape.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `A-20261115-125927-6d2c1e6`: failed (exit 1), lead rerun of the scope package T1-T5 (L1)
- `A-20261115-125932-574c747`: failed (exit 1), lead rerun of the gauge package (L1)
- `A-20261115-125932-5a90432`: failed (exit 0), lead rerun of the newton package (L1)
- `A-20261115-125932-b90223c`: failed (exit 1), lead rerun of the criteria package (L1)
- `A-20261115-125932-f221206`: failed (exit 1), lead rerun of the expball package (L1)
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

Lead of A-emd-pbh (wave 2): the three track criteria of G1 are met - T1 constraint residuals converge at orders 2 and 4 (and the time orientation of the data is confirmed by the evolution of SR-1/SR-2), T2 the prediction table with the amplitude conversion, T3 by decision 0013 with the Newtonian-mode runs made as well - and the analysis pipeline is validated on AthenaK runs; the automated re-verification passes. Missing: the data-flow schematic (C11) and a fresh verifier for T3, the criteria checks and the note's ledger (C18). Request: rule whether G1 can be judged together with G0 once these two are delivered; the lead does not pass the gate.
