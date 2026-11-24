# Stage report: A-emd-pbh G2

Date: 2026-11-24 · branch `track/A-emd-pbh` at `b92bdbd9df2c` · checklist
`tracks/A-emd-pbh/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/A-emd-pbh/G2-fail-20261124` (created and pushed by the orchestrator after review, decision 0003).

- 11 checklist items not PASS or NA: C1 OPEN, C3 FAIL, C5 OPEN, C6 OPEN, C10 OPEN, C11 OPEN, C13 OPEN, C14 OPEN, C16 OPEN, C17 OPEN, C18 OPEN
- no VERIFY_RESULTS.json (run nrpic-stage verify)
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G2/STAGE_REPORT.md` | written by this command |
| `stage/G2/EVIDENCE.md` | present |
| `stage/G2/OPEN.md` | present |
| `stage/G2/CHECKLIST.md` | present |
| `stage/G2/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G2/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | Rows of brief section 10 that are A's: (i) time-reversed Oppenheimer-Snyder = the expanding ball: horizon formation against the exact solution on three meshes (conv_ball A-20261121-120257-a2eb839) and across eight amplitudes 0.20-1.0 on mesh B (threshold_ball A-20261124-131120-5c974ce: tau_det within 0.03-0.14 M of exact, the code's finite-duration bracket (0.40, 0.42] equals the exact one); (ii) LTB: the periodic spherical peak P0L against its exact LTB reference B (A-20261124-130142-9a2d6a2: shells r0 >= 1.5 within 3 per cent to turnaround; no horizon found, P3 refuted); (iii) Szekeres: round 1 cut (N = 32 non-finite at tau = 26; szekeres/JOURNAL entry 9), the card series has not run. OPEN until Szekeres runs and P0L's horizon is found (peak_leak6 queued). | OPEN |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | conv_ball A-20261121-120257-a2eb839 (README table): mesh M/16, M/32, M/64 (ddet 0.193, 0.068, 0.017 M; orders 1.5, 2.0; horizon-mass error 7.4e-3, 2.1e-3, 2.1e-4), particle number x1, x8, x64 at mesh A and x1, x8 at B (time errors independent of N at B; mass error 2-5e-4 at fixed N on all meshes), boundary 16 M against 32 M (identical to 1e-7 / 1e-11). Gauge leg not run (boundary chosen, charter 9.2 'gauge or boundary'). Ball-radius leg on C added in batch 11 (C-R1.25: ddet +0.040 against +0.017, mass -1.2e-4 against -2.1e-4; T5 partly refuted). | PASS |
| C3 | Constraints behave | Constraint norms are bounded through each run and jump only at the horizon (A-20261124-132342-d5dc06e, fig_constraint_conv.png), but they do not converge before t ~ 6: //H//_2 is flat or grows slightly from M/16 to M/64 at t <= 4 (prediction K refuted) and is flat in particle number x1-x64 at fixed mesh (K2 refuted); //M//_2 at t = 0 grows with the mesh (order -0.8). //H/////16 pi E// on the mesh line outside the horizon is 0.11-0.21 at t = 0 and 0.3-3 later (threshold scan, T6 refuted). Candidate cause (top-hat density jumps) untested. | FAIL |
| C4 | A first minimal full-GR kinetic run | Full-GR kinetic runs (Z4c + particles, nrpic_cf expanding ball) that form horizons: conv_ball's 14 members (A-20261121-075926-d10c2c1, -083336-6a82131, -091934-ac62f5f, -110017-471b0ae) and the eight mesh-B threshold members (queue lines 3-11, closed with nrpic-run finish in batch 11); periodic P0L to t = 140 (A-20261122-235305-4ea0aa5). | PASS |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | STAGE_REPORT.md written by nrpic-stage report in batch 11 as an interim package; the verification report proper waits for C1, C3, C18. | OPEN |
| C6 | Reproducibility package | Every run registered (manifests in tracks/A-emd-pbh/runs/, commands, inputs with sha256); scripts in conv_ball/, threshold_ball/, periodic_threshold/ with 'How to rerun' in conv_ball/README.md. Missing: a single rerun list for G2 (stage/G2/VERIFY) and threshold_ball/README.md. | OPEN |
| C7 | In the spherical case, the errors of the turnaround time and of the horizon-formation time relative to the exact solution converge in particle number, mesh spacing and ball radius | conv_ball (A-20261121-120257-a2eb839): turnaround time error converges B->C at order 2.1 (A->B flat: a flat maximum), horizon-formation time ddet at orders 1.5, 2.0 and trapping time 2.1, 1.5 in mesh spacing; time errors independent of particle number at mesh B; ball radius: dependence 0.09 M at A, 0.04 M at B, 0.024 M at C (C-R1.25, batch 11; T5 refuted at its 0.02 bound). Across amplitude (threshold_ball A-20261124-131120-5c974ce): /ddet/ <= 0.14 M for delta_c 0.35-1.0 on mesh B. | PASS |
| C8 | The horizon-mass error is of the same order as in the Oppenheimer–Snyder test of Wu and Most | Horizon-mass error (median over detections) 7.4e-3, 2.1e-3, 2.1e-4 on M/16, M/32, M/64 (conv_ball A-20261121-120257-a2eb839), against the source's fiducial Oppenheimer-Snyder level 1e-3 (main.tex:945) and best AMR particle RMS 7.3e-4 (main.tex:1484); threshold scan on M/32: /dmmed/ 3.2e-4 to 9.4e-3 for delta_c 0.35-1.0 (A-20261124-131120-5c974ce). First-detection excess (up to 4-7 per cent at threshold) is carried by the slice, not the finder (threshold_ball entry 4). | PASS |
| C9 | Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013) | The expanding ball is the spherical verification case (conv_ball, threshold_ball); the threshold line is built in the periodic box (periodic_threshold): P0L/S1L on the refined periodic mesh run stably at cfl 0.5 (job 2, A-20261124-130507-10510ac); the box's horizon is not yet found (P3 refuted; peak_leak6 queued). Newtonian-mode runs were made at G1 (newton/). | PASS |
| C10 | Schematic: Verification ladder | Verification-ladder schematic not drawn yet (note/ has the G1 architecture and timeline schematics). | OPEN |
| C11 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | fig_convergence.png of conv_ball A-20261121-120257-a2eb839 (mesh, particle number, ball radius, boundary legs) and fig_threshold_outcome.png (A-20261124-131120-5c974ce) exist and were looked at; no gauge-leg figure (boundary leg chosen) and not yet drawn into the note with zoom-figure style. | OPEN |
| C12 | Data figure: Constraint norms against time | fig_constraint_conv.png of A-20261124-132342-d5dc06e (norms of H and M against time on three meshes, the threshold members, the particle-number leg), looked at; fig_job2_q.png (periodic job 2) and fig_compare_ltb_P0L.png panel f. | PASS |
| C13 | Data figure: At least one multi-scale slice mosaic with zoom boxes | No multi-scale slice mosaic yet (the nested runs write line outputs, not field dumps; a mosaic needs 3D outputs of one member). | OPEN |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | CHECKLIST.md, EVIDENCE.md, OPEN.md and STAGE_REPORT.md exist (batch 11); scope text scope/SCOPE.md. Interim package, not for review. | OPEN |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | Every figure of this package is drawn by a registered analysis with the figstyle module (periodic_threshold/scripts/figstyle.py, python/nrpic/figstyle.py): job2_q, compare_ltb, line_trapped, threshold_ball analyse.py, constraint_conv; each PNG looked at by the lead (journals). | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | Schematics of note/ name release core-v0.3 (G1 reservation); not updated to v0.6. | OPEN |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | The working note has no G2 sections yet. | OPEN |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | verify_bh (independent check of BH-1R) exists; no fresh-context verifier has recomputed conv_ball's or threshold_ball's numbers for G2. | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | Failed runs closed as failed: A-20261121-235851-d2200d7 (A-mesh guard stops), A-20261121-131600-02b5d41 (periodic job 1); cut chains continued, not repeated (journals 2026-11-24); refuted predictions on record: T4 reason, T5, T6, P2-P4, Q1b, F1, K, K2 (threshold_ball entries 4-7, periodic_threshold entries 2026-11-24). | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten at the end of batch 11. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

Not run: `harness/bin/nrpic-stage verify A-emd-pbh G2`.

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_ball_exact.* | note/scripts/fig_ball_exact.py | data | to be confirmed by the session |
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_criteria.* | note/scripts/fig_criteria.py | data | to be confirmed by the session |
| note/figures/fig_landscape.* | note/scripts/fig_landscape.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G2/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `A-20261115-125927-6d2c1e6`: failed (exit 1), lead rerun of the scope package T1-T5 (L1)
- `A-20261115-125932-574c747`: failed (exit 1), lead rerun of the gauge package (L1)
- `A-20261115-125932-5a90432`: failed (exit 0), lead rerun of the newton package (L1)
- `A-20261115-125932-b90223c`: failed (exit 1), lead rerun of the criteria package (L1)
- `A-20261115-125932-f221206`: failed (exit 1), lead rerun of the expball package (L1)
- `A-20261119-151452-46f171e`: failed (exit 1), Szekeres slice (eps=0.1 twisted dipole, and eps=0 LTB) in conformally flat Cartesian coordinates: finite-difference Hamiltonian and momentum residuals at N=32..256, orders 2 and 4 (JOURNAL P7)
- `A-20261119-155945-c09d40e`: failed (exit -15), Data set 3, lattice n_lat = 136 (h = M/16) with tracked particles, for BH-1R (one refined level); same data and exact references as A-20261119-143524-334e553
- `A-20261121-064515-aa13c8f`: failed (exit 1), G1 gate review: reviewer's own recomputation of four unverified Table IV rows of note v1 (SR-1 |H| at t=20, SR-2 central lapse, SR-1 tracked particles) and the C8 Newtonian band, from raw outputs with checksums
- `A-20261121-131600-02b5d41`: failed (exit 3), periodic_threshold card job 1: P0L (spherical peak mu = 0.3, relaxed 1+log lapse with Gamma-driver, against the exact LTB reference B of A-20261121-130103-e007f42) and S1L (the S1 data mu = 0.3, e = 0.2, relaxed lapse; S1 went non-finite at 21.9 t_H in the E1 gauge); predictions P and S of periodic_threshold/JOURNAL.md
- `A-20261121-203156-d094c56`: failed (exit 1), threshold_ball smoke test: decks nest16_L32 and nest32_L32 with every queue option on the core-v0.6 processor build, three cycles each, finder from cycle 0
- `A-20261121-222439-65eebaa`: failed (exit 1), periodic_diag Test A: card job 4799 outputs read again (level-4 step, onset, grid-scale part, Test B amplification along the card steps)
- `A-20261121-222557-2d8e53c`: failed (exit 1), periodic_diag analysis of the uniform-mesh runs U0, G0, G1, G2, G5, G6
- `A-20261121-235851-d2200d7`: failed (exit 3), threshold_ball A-d0.42, A-d0.40: the bracket members on mesh A (finest M/16, outer 32 M), v0.6 release (JOURNAL entry 1)
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


State 2026-11-21 (lead, batch 2b of wave 3; first written 2026-11-15). Likelihood and effect:
H high, M medium, L low [JUDGEMENT]. Sources: `scope/SCOPE.md` sections 8 and 10.9,
`gauge/GAUGE.md`, `stage/REVIEW-wave2.md`, `stage/REVIEW-wave3.md`, `stage/G1/GATE_REVIEW.md`,
core's messages of 2026-11-20/21, the helpers' journals. "Realized" means a run showed it;
"eased" means a released capability addresses it but no run of this track has yet shown it.

| # | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| 1 | Lapse fronts: the conformal-time lapse sends a pulse from the edge of the bound core to the centre (central lapse 1.80-1.87 against 1.34 at dx = M, M/2, M/4; runs_ball, A-20261115-182314-bebd0cf); a gauge effect, the same at three resolutions (gate review check B) | realized in SR-2; eased in the ball | H: the core runs through its proper time too fast, no horizon | central lapse against a(tau_c) | relaxed 1+log lapse `<z4c> lapse_leak` (core-v0.4) used in SR-1L, BH-1, BH-1R; BH-1R has a finder detection from t = 10.875 (A-20261120-222355-cc8e0af); not yet tried in the box |
| 2 | Geodesic slicing with frozen shift unstable: SR-1 breaks down at dx = M / M/2 by first non-positive metric determinant at t = 30.25 / 32.875, norm(H) > 1e10 at 30.5 / 33.0, first non-finite line output at 31.0 / 33.25; grid-scale growth at the core edge. Szekeres hole at N = 32 non-finite from tau = 26 (A-20261121-075933-338a6ff) | realized | H for SR-1 | largest abs(H) (0.24 / 0.051 / 0.040 at t = 20; the M/4 run also halves the box) | not the slicing for collapse; keep for the expansion phase and the Szekeres verification at resolved meshes |
| 3 | Time step ignores the coordinate light speed (v = R_i/R reaches 17 at the first trapped sphere in comoving coordinates) | eased | M | staged cfl plan | `<z4c> dt_lightspeed` released in core-v0.5; use it in every comoving-gauge deck |
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
| 16 | Newtonian mode lacks the SR push and the deformed-ball generator in make_ic.py (core deferred); energy off by 1e-3 to 3e-2 at sub-cell crossings, cause unknown | M | L-M | newton/JOURNAL.md entry 8 | core's answer 20261121T081909Z: the drift is a space-discretisation property of W with different deposit and gather kernels (3.7e-6 with pcs + bspline); `problems/newton/make_ic.py ball` now writes our deformed ball; re-test one scan point with pcs + bspline before G2 |
| 17 | G2 asks convergence of the horizon-formation time and a horizon-mass error ~1e-3; the source's OS test saw no monotonic convergence of the horizon mass (main.tex:1484-1485, verifier C7); the source's numbers are final masses after excision against the ADM mass, not the mass of a newly formed horizon against its slice (verify_bh entry 1) | M | M: G2 criterion may be unreachable as written | conv_ball series | report the measured mass error with its N and dx dependence and state which mass is compared; ask orch with the G2 evidence if it stalls (gate review reservation 10) |
| 18 | First horizon of data set 2t (areal radius 0.161 M) is below one cell in non-comoving gauges (SR-2: largest 2m/R 0.34) | realized for 2t | H for the G2 horizon test | | data set 3 with one static level of M/16 (BH-1R): finder horizon at coordinate radius 0.42-0.44 M, about 7 fine cells; conv_ball nests the levels (M/16, M/32, M/64 at the centre) |
| 19 | Non-finite runs keep going with exit 0 (S1 spent a third of its card time on non-finite fields; the Szekeres N = 32 run too) | eased | M: card time, misread outcomes | first non-finite record | `<z4c_guard>` in core-v0.5 stops such runs with exit status 3 (on by default); runs on older executables are still read for finiteness |
| 20 | Periodic constraint control on refined levels: H_r max above 0.1 before collapse (S2 from 36 t_H; S1 0.16 at the first pancake) | realized | H: threshold definition's bound fails | L2 norms (not available on multilevel meshes) | refined-level solve, nested lattice, diagnostics (outbox) |
| 21 | Adaptive refinement crashes with nrpic_cosmo (user_ref_func never set) | resolved in core-v0.5 | H for the scan cost | | `<amr_criterion0> method = user` with `<particles_amr>`; core's S1 run with a lapse ladder ends as the static run does (t = 11.78, core message 20261120T223017Z): the mesh was not what limited S1 |
| 22 | Periodic generator: make_field has a first-order super-horizon error and fails for mu >= 0.5; the CMC route diverges at mu = 0.5 | certain | H | | Newton step in core's id-solver (outbox phase1-generator-cmc) |
| 23 | Finder that never searches: `<fastflow> hmean_tol_<n>` is compared with the surface integral of the expansion (core message 20261120T223017Z item 1); every deck of the track has 100. BH-1 at M/8 (initial radius 3 M): every search ends at iteration 4 with nan | H | H: a horizon is missed, "no detection" misread as "no horizon" | `<fastflow> diagnostics = true` status files | `hmean_tol_0 = 1e30` in every new deck; the BH-1 verdict rests on the line diagnostics until a finder rerun (REVIEW-wave3 section 3) |
| 24 | A horizon in a state that violates the constraints: S1 has relative Hamiltonian constraint of order one near the centre from t = 9 (core, run core-20261120-220816-09f6f79); finder surfaces at t = 11.3-11.7 there are not evidence of a black hole | H in the box | H for the threshold line | constraint norms inside and outside spheres (core-v0.5 region norms) | a finder detection counts only with region norms below a stated bound at that time |
| 25 | Cell-scale modulation of the deposit for stretched or compressed lattices with linear clouds: 7 per cent rms at one particle per cell (core run core-20261121-031145-ffc12b3), 1.7 per cent at four per cell | M | M in the box (noise near threshold) | | four or more particles per cell along each direction, or quadratic clouds, in the periodic set-up |
| 26 | Process: sessions cut by the usage limit leave stranded files and open manifests; two helpers share the worktree with the lead | realized (2026-11-19, 2026-11-20) | L-M: gate checks fail on `clean` and `runs` | git status, `nrpic-run status` | leads close stranded runs whose processes ended (`nrpic-run finish`), list unfinished packages in HANDOFF; commits path-limited |
| 27 | Periodic relaxed-lapse deck blows up early: norm(H) jumps ~1e4 at t = 2.5 in both P0L and S1L, guard stop at 4.8 and 15.1 (A-20261121-131600-02b5d41, read in A-20261121-203120-eaba95f) | realized | H for the periodic threshold line (G3) | jump time common to both members | request to core periodic-relaxed-lapse-blowup; no periodic card run until answered |
| 28 | Finite-duration threshold in the ball depends on the time measure: the coordinate time of first detection lags the shell's proper time by 1-2 M, i.e. ~0.01 in delta_c near 0.41 | certain | M: bracket placement | ddet against tau_AH | threshold_ball judges the bracket in the invariant measure (DESIGN.md section 1); t_end = 45 sits 1.3-1.4 M from both bracket members |
| 29 | Unattended sequencer commits run manifests on track/A-emd-pbh while later sessions work in the worktree (index lock, dirty package refusals) | M | L-M: a queue line skipped after five refusals | scratch/A-emd-pbh/sequencer_threshold/sequencer.log, done.txt | sessions commit threshold_ball changes promptly; skipped lines are resubmitted by hand (HANDOFF) |
| 30 | Disk: a C-mesh chain writes 5.1 GB per restart (rst + prt) every 4 M plus one per segment: about 0.1 TB for C-d0.42 to t = 51 | M | L | du of the run directory | delete superseded restart files after the run is finished and verified (keep the last) |

## Decision requested from the group

One paragraph: accept G2 of A-emd-pbh, or what is missing.

TO WRITE by the track before the package is submitted (`nrpic-stage report ... --decision "..."`).
