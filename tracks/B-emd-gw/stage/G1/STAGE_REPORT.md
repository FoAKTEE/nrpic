# Stage report: B-emd-gw G1

Date: 2026-11-15 · branch `track/B-emd-gw` at `26cbf6b699f5` · checklist
`tracks/B-emd-gw/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/B-emd-gw/G1-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 6 checklist items not PASS or NA: C6 OPEN, C10 OPEN, C11 OPEN, C16 OPEN, C17 OPEN, C18 OPEN
- verify reported FAIL: runs
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | written by this command |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
| `stage/G1/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | vacuum Z4c in periodic boxes (periodic_z4c, wave 1); semi-analytic Zel'dovich and ellipsoid baseline (run B-emd-gw-20261115-115752-840e994); AthenaK Newtonian mode on the same particles, pancake and ellipsoid (newton_tests, runs in EVIDENCE.md); stage/G1/STATUS.md | PASS |
| C2 | The analysis pipeline validated on them | gw_diag validated on analytic fields and AthenaK vacuum output (wave 1; verifier C7, run B-20261115-170546-4507b05); the first-source pipeline reread independently by the lead to 9e-14 of the signal (run B-20261115-190007-e09a0d2); Newtonian analyses rechecked (run B-20261115-190015-4dd3416); stage/REVIEW-wave2.md | PASS |
| C3 | Interface proposals submitted | 14 messages of wave 1 (outbox/20261115T1340Z__*) and the wave-2 messages of this session; core answered the eight requests to core (message 20261115T1620Z, tracks/core/interfaces/REQUESTS_B.md on core/requests-b) | PASS |
| C4 | Baseline data and figures | first_source/figs/scan_*.png, res_compare.png, late_rise.png; newton_tests/figs/*.png; baseline/figs; from the registered runs of EVIDENCE.md, looked at by the helpers and by the lead (stage/review_wave2/figs) | PASS |
| C5 | Interface documents | gw_diag/README.md (TT, energy, spectra, helicity, Weyl, readers), first_source/README.md (gauge piece G_tot), the request documents in outbox/ and core's answers REQUESTS_B.md; coord/INTERFACES/newtonian_mode.md used and tested | PASS |
| C6 | The two diagnostics agree on analytic linear waves | met for waves along an axis in a flat periodic box (TT and Psi_4 agree with the exact wave and with each other to 1.8e-7 A; runs -113218-0ea0f74, -120128-7dfaa38, verifier B-20261115-170546-4507b05); oblique wave: generator fixed on core/requests-b, core's card run with gw_diag (message 20261115T1850Z), the track's own run owed; expanding-box wave with both diagnostics not run (OPEN.md items 1, 2) | OPEN |
| C7 | The Newtonian baseline reproduces the scaling of the literature | lead's judgement: emitted-spectrum scaling sigma^(7/2), omega_peak ~ sigma^(3/2) reproduced by the semi-analytic baseline (run -115752-840e994; verifier run B-20261115-170518-c1b61a3); in AthenaK's Newtonian mode the single patch obeys E ~ (2 alpha)^(7/2) to 3e-14 (N3) and its crossing time and energy converge to the ODE (N1: t_x second order, Richardson within 5e-5; E first order, -9.7 percent at N = 128); rechecked in run B-20261115-190015-4dd3416. Not confirmed: Omega today ~ sigma^(7/2) of 2403.15126:1074 (verifier C8); N2 waits for core | PASS |
| C8 | Background error and constraint convergence with the stand-in matter | struck by decision 0013 (particles do it directly); the particle FLRW background: lapse = a to 1.9e-7 (a = 4) and 7.0e-8 (a = 36), run B-emd-gw-20261115-115414-7ffbde1; Hamiltonian constraint in stage/G1/STATUS.md (corrected values) | NA |
| C9 | Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013) | applied: C8 struck; the N-body baseline runs in AthenaK's Newtonian mode (newton_tests); the multi-code row (shearing dust, GR against the Newtonian mode) is G2 work; item 3 amended (coord/notes/derivations_to_check.md, decision 0013) | PASS |
| C10 | Schematic: Updated architecture | the G0 architecture schematic exists (note/figures/schem_architecture.png); the updated one (Newtonian mode, G_tot, jitter and thin boxes now exist) is not drawn (OPEN.md item 3) | OPEN |
| C11 | Schematic: Data-flow diagram | data-flow diagram not drawn (OPEN.md item 3) | OPEN |
| C12 | Data figure: Baseline results | first_source/figs/scan_kk0.png, scan_secondgauge.png, res_compare.png; newton_tests/figs/pancake_east.png, ell_convergence.png, ell_selfsim.png | PASS |
| C13 | Data figure: Validation figures for the analysis pipeline | gw_diag/figs (wave 1), first_source/figs/t0_gauge.png, scan_null.png; stage/review_wave2/figs/rv_review_first_source.png, rv_review_newton.png | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, STATUS.md in stage/G1/; the lead's recheck is stage/REVIEW-wave2.md (task-given name); scoping text scope/SCOPE.md | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | every data figure of first_source, newton_tests and the review from a registered run with one script each (figstyle), looked at; the note's figures are rerun by nrpic-stage verify | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | G1 schematics not drawn (C10, C11) | OPEN |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | note v0 exists and its checker passed (G0 C17); its G1 sections (first-source scan, Newtonian mode) are not written (OPEN.md item 4) | OPEN |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | the verifier of wave 2 covered the G1 claims of wave 1 (VERIFIER.md C6-C8); the wave-2 G1 runs are rechecked only by the lead (REVIEW-wave2.md), not by an independent agent (OPEN.md item 5) | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed predictions and runs on record: first_source/JOURNAL.md (P1 as worded, P4, P6 with G), newton_tests/JOURNAL.md (P1a, P1b, P2a, H1a, H1c, H1d-3, N1d, N1e), stage/review_wave2/JOURNAL.md (R5, R6); failed runs B-20261115-161656-03d75e1, -164104-886798f, -170149-75036cf kept | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten by the lead at the end of wave 2 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T19:30:17Z, clean export of `26cbf6b699f5`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 26cbf6b699f5 (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G1-26cbf6b-20261115T192519Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 9 of 132 runs have problems |
| run-notes | WARN | 70 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 34 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_baseline.* | note/scripts/fig_baseline.py | data | to be confirmed by the session |
| note/figures/fig_pancake.* | note/scripts/fig_pancake.py | data | to be confirmed by the session |
| note/figures/fig_source.* | note/scripts/fig_source.py | data | to be confirmed by the session |
| note/figures/fig_waves.* | note/scripts/fig_waves.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `B-20261115-161656-03d75e1`: failed (exit -15), first_source: initial data of the crossed-wave scan (1, eps, 0), eps = 0, 0.1, 0.3, 1, delta = 0.01, box 4, 64^3, two particles per cell and direction (make_east.py, production deposit settings)
- `B-20261115-164104-886798f`: failed (exit 2), first_source: initial data of the crossed waves eps = 1 (rebuild; the case was cut off in B-20261115-161656-03d75e1), delta = 0.01, box 4, 64^3, two particles per cell and direction
- `B-20261115-170149-75036cf`: failed (exit 1), newton_tests analysis of P1, P2, H1 (pancakes n=16, 32 against Zel'dovich, pm.py, and the discrete-Laplacian growth law)
- `B-emd-gw-20261115-120531-40a3597`: failed (exit 1), scouting: TT energy spectrum, TT/non-TT ratio and Weyl parts on the restart dumps of the full-GR cosmology runs dav_c256_n128_t and dav_c256_n128_pcs4bt
- `B-emd-gw-20261115-130926-a1c2237`: stopped (exit None), Lead re-check L1 of the five wave-1 packages: clean git-archive export of commit 2fb3dbff41a1dcba59577c9f8410ff4501f06f2c; all analysis scripts and tests rerun, results compared leaf by leaf with the committed/original results (compare_results.py); four periodic_z4c AthenaK cases re-executed with the release processor executable and compared byte by byte with the original runs

## Open risks


State 2026-11-15, end of wave 2 (lead). Likelihood and effect are JUDGEMENT; the watch
column names the measurement that decides. Sources: `scope/SCOPE.md` section 8,
`stage/G0/REVIEW.md`, `stage/G0/VERIFIER.md`, `stage/REVIEW-wave2.md`, the helper journals.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 Spurious TT power from particle noise after shell crossing (brief line 745). In `cosmo/` the relative momentum-constraint violation is 2.9e-2 at a = 40 and 0.17 at a = 100 (`cosmo/TESTLOG.md` 1404-1415, 1674-1676). The crossed-wave scan on an aligned lattice has no noise to show (null at rounding, run B-20261115-190007-e09a0d2); the floor is unmeasured (verifier weakest point 2) | high | the post-crossing science claim | jittered-lattice null (eps = 0, 1 and 8 per cell) against the eps = 0.3 signal; the jitter option exists on core/requests-b | two particles per cell and direction; eps >= 0.032 (a = 40) to 0.19 (a = 100) [JUDGEMENT bound, corrected crossover 0.289]; descope to the pancake phase if the floor exceeds the eps = 1 signal at 128 cells |
| R2 Junk TT of conformally flat initial data | certain | biases the pre-crossing comparison | now modelled: the box-mode strain follows s g(tau) with the junk to 0.22-0.44 percent for 2 <= a <= 10 (first_source P2, rechecked) | keep the full second-order solution s g(tau) as the reference; initial data with a TT part deferred by core |
| R3 Near field against radiation in a box | measured: high | the box-mode signal before and after shell crossing is a quasi-static spin-2 field, not radiation: rho_kin/rho_grad <= 0.04 (first_source; K1 mode <= 0.013 for a >= 12, lead) | rho_kin against rho_grad per band; virial frequency against c k_1 | report rho_K (propagating) and the strain (static) separately; the radiated signal needs larger boxes (L = 8) or later times; L = 4 stays the first box |
| R4 Gauge and hypersurface dependence of h^TT (2111.09163 `prd_v1.tex:369-426`; 1704.03500 `GW2nd_ApJ.tex:245`) | medium (was high) | a gauge piece mistaken for a signal | spatial-gauge piece G_tot measured: < 1.1 percent of c_+ for a <= 20, ~10 percent near shell crossing; a second spatial gauge agrees after G_tot (difference reduced twelvefold); the wave-1 late rise is not gauge (runs -164616-a6d9477, -171804-42e975b) | report raw and G_tot-corrected strain (adopt gauge_piece_total into gw_diag); slicing piece only bounded (P10); York projection; lapse as third convergence leg |
| R5 Gauge shocks of the production lapse (conformal time): in vacuum K/k ~ 0.24 makes a shock within two crossings | medium in collapse | non-convergent metric near caustics | Theta and lapse gradients against resolution | harmonic and 1+log as alternatives; joint gauge work with Track A (shared test accepted) |
| R6 Black-hole end: delta = 0.05 fails at a = 17.2 (`cosmo/TESTLOG.md` 1842-1852) | certain at large delta | caps the amplitude range | any slicing that passes collapse (Track A: none yet, its message 18:37Z) | range to 0.02 until then (stop rule) |
| R7 Output volume: restart dumps carry the particles (380 MB per dump at 2.1M particles, 12 GB per run) | medium (was high) | limits cadence and resolution | dump size per run | double-precision bin output for z4c exists on core/requests-b; single-precision bin is adequate for the box modes (4e-5 relative) but not for the null of tilde A |
| R8 Dependence on core: generator fix and jitter (on core/requests-b, not on main), species history (N2), OpenMP processor build | medium | delays G1 criterion 1 and the noise null | release of core/requests-b to main | scouting with core's published executables (decision 0013) |
| R9 Literature comparison: 2212.00425, 2312.12499 read at abstract level only; the Omega-today scaling of 2403.15126 is sigma^(5/2) with its own eq. (result_OmZ), not the stated 7/2 (verifier C8); the 144-392 prefactor gap varies as theta^(2/3) | medium | the "when does GR matter" comparison has no quantitative anchor | reading of the papers' spectra; kb claims | compare emitted energies (7/2 holds at emission), not Omega today, until settled |
| R10 Particle-number convergence of the background, growth and first-source rows not shown | medium | G2 criterion | FLRW and test B at 1, 8, 27 per cell; first source at 1, 8, 27 per cell and 128^3 | card package of about 1 card-h |
| R11 Overlap: 2605.04487 names a fully relativistic treatment as future work (`main_v3.tex:2630`); 2312.12499 says the same (`main.tex:115`) | medium | novelty | arXiv listings | keep the plane-symmetric null, the gauge-controlled box-mode strain and the GR-minus-Newton statement per k as the distinct contribution |
| R12 Short second-order comparison window: at delta = 0.01 the strain departs from s g by 1-2 percent at a = 20 and 6-11 percent at a = 40, growing with eps (beyond second order; 2610.08045 `main.tex:40-49`: secular growth of higher orders in matter domination) | certain | pre-crossing accuracy claims limited to a <= 10 | the same scan at delta = 0.0025 | quote the window; extend it with smaller delta; the higher-order departure is itself a result to explain |
| R13 Newtonian reference force error (kh)^2/12 of the seven-point Laplacian (3.2e-3 at kh = 2 pi/32) | certain | biases GR-minus-Newton per mode at the 1e-3 level | core's answer on a fourth-order option | quote it with every comparison or use the spectral pm.py as a second Newtonian reference |

## Decision requested from the group

None yet: G1 of Track B is not met (six checklist items open: criterion 1 for oblique and expanding-box waves, G1 schematics, the note's G1 sections, an independent verifier of the wave-2 runs). Recorded for the group: criterion 2 (Newtonian baseline in AthenaK's Newtonian mode) is met in the lead's judgement, criterion 3 is struck by decision 0013, and the full-GR first source already runs through shell crossing (stage/G1/STATUS.md).

## Lead's assessment (wave 2)

G1 is not met. Per criterion of the track sheet as ruled by decision 0013 (details and
corrected numbers in `stage/G1/STATUS.md`, evidence in `EVIDENCE.md`, what is missing in
`OPEN.md`):
1. Two diagnostics on analytic linear waves: met along an axis in a flat periodic box (track
   and verifier); oblique wave only by core's own card test on core/requests-b; expanding box
   not run. OPEN.
2. Newtonian baseline reproduces the literature scaling: met in AthenaK's Newtonian mode
   (N1 converges to the ODE, N3 gives the (2 alpha)^(7/2) law of the single patch to 3e-14;
   rechecked by the lead, run B-20261115-190015-4dd3416), with the emitted-energy scaling of
   the literature; the Omega-today scaling of 2403.15126 is not confirmed (verifier C8).
3. Stand-in matter: struck (0013).
Also open: G1 schematics, the note's G1 sections, an independent verifier of the wave-2 runs.
The verify run's only failure is the runs check shared with G0 (ruling requested).
