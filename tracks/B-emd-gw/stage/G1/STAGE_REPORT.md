# Stage report: B-emd-gw G1

Date: 2026-11-21 · branch `track/B-emd-gw` at `790c492be6cf` · checklist
`tracks/B-emd-gw/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/B-emd-gw/G1-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C18 OPEN
- verify ran on 1197792; files changed since: coord/DECISIONS/0020-size-batches-to-the-five-hour-window.md, harness/workflows/batch-2a.json, harness/workflows/batch-2b.json, harness/workflows/make_batch.py, tracks/B-emd-gw/HANDOFF.md, tracks/B-emd-gw/JOURNAL.md (run verify again)
- verify reported FAIL: clean, sync

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
| C1 | Baseline results obtainable without the NRPIC coupling | vacuum Z4c in periodic boxes (periodic_z4c, wave 1); linear waves of test F (flat, oblique) and X (expanding box) with both diagnostics (waves, runs in EVIDENCE.md); semi-analytic Zel'dovich and ellipsoid baseline (run B-emd-gw-20261115-115752-840e994); AthenaK Newtonian mode, pancake and ellipsoid (newton_tests) and the EMD random-field box at 32^3 and 64^3 (population, runs B-20261119-143828-0ef9b5b, -143832-85cbe25, -145324-525e4fd) | PASS |
| C2 | The analysis pipeline validated on them | gw_diag validated on analytic fields and AthenaK output (wave 1; verifier run B-20261115-170546-4507b05); criterion-1 pipeline read three times: waves (B-20261119-164402-7438a99, B-20261120-221708-d8eae03), verifier3 with its own code (B-20261121-025826-80973e3, -030121-58fe5dc), the lead's third reading of X at N = 64 (B-20261121-063617-6183015, -063835-826c461); first-source pipeline reread by the lead (B-20261115-190007-e09a0d2) and by verifier2 (B-20261119-142332-dd28d1d); stage/REVIEW-wave2.md, stage/REVIEW-wave3.md | PASS |
| C3 | Interface proposals submitted | 14 messages of wave 1 and the wave-2 messages (outbox/); core answered in tracks/core/interfaces/REQUESTS_B.md and released the oblique generator, double-precision output and jitter in core-v0.4 (tag on f9323185); wave-3 requests in outbox/20261121T* | PASS |
| C4 | Baseline data and figures | first_source/figs (scan, res_compare, late_rise, conv_null, conv_delta, null_spectrum); waves/figs (final_*, x10_check); newton_tests/figs; population/figs; all from registered runs, looked at by the helpers and the lead (stage/review_wave2/figs, stage/review_wave3/figs) | PASS |
| C5 | Interface documents | gw_diag/README.md (TT, energy, spectra, helicity, Weyl, readers; gwdiag/binio.py reads single and double precision, commit 5499ec6c); first_source/README.md (gauge piece G_tot); requests and core's REQUESTS_B.md; coord/INTERFACES/newtonian_mode.md and the core-v0.4 interfaces used | PASS |
| C6 | The two diagnostics agree on analytic linear waves | met for both set-ups [lead's judgement, verified]: test F (k = 2 pi (1,1,1), N = 16-64) and test X (tensor mode in the matter-era box, N = 16-64, x10): TT projection and Weyl/Psi_4 recover amplitude, phase and both polarizations against the exact solutions with the errors of the code's stencils and integrator (F within 2.1 percent of the symbol-plus-RK4 prediction; X cross within 0.5 percent of the RK4()4[2S] prediction); the diagnostics agree to <= 6.4e-11 (F, forward combination; theta^6/1120 with h alone) and 2.4e-8 (X); X plus at N >= 48 is rounding-limited (1/A, x10 run B-20261119-155758-458cf17). Runs: waves B-20261119-142016-ee73a03, -142233-70d5043, -142021-8f4c441, -142234-85da208, -142124-feb2daf; analyses -164402-7438a99, B-20261120-221708-d8eae03; independent verifier stage/G1/verifier3/VERIFIER.md section 4; lead's recheck stage/REVIEW-wave3.md | PASS |
| C7 | The Newtonian baseline reproduces the scaling of the literature | lead's judgement: emitted-spectrum scaling sigma^(7/2), omega_peak ~ sigma^(3/2) reproduced by the semi-analytic baseline (run -115752-840e994; verifier run B-20261115-170518-c1b61a3); AthenaK's Newtonian mode: single patch E ~ (2 alpha)^(7/2) to 3e-14 (N3), crossing time and energy converge to the ODE (N1), pancake errors equal the seven-point-Laplacian prediction; confirmed independently by verifier2 (ellipsoid crossing 23.852370 t_k, order 2.28; sheet errors within 3 percent; run B-20261119-142135-e582e09). Reservation carried from G0 and still [TO VERIFY]: Omega today ~ sigma^(7/2) of 2403.15126:1074 against sigma^(5/2) from its eq. (result_OmZ); the criterion is judged on the emitted energy | PASS |
| C8 | Background error and constraint convergence with the stand-in matter | struck by decision 0013 (particles do it directly); the particle FLRW background: lapse = a to 1.9e-7 (a = 4) and 7.0e-8 (a = 36), run B-emd-gw-20261115-115414-7ffbde1; Hamiltonian constraint in stage/G1/STATUS.md (corrected values) | NA |
| C9 | Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013) | applied: C8 struck; the N-body baseline runs in AthenaK's Newtonian mode (newton_tests); the multi-code row (shearing dust, GR against the Newtonian mode) is G2 work; item 3 amended (coord/notes/derivations_to_check.md, decision 0013) | PASS |
| C10 | Schematic: Updated architecture | note/figures/schem_architecture.png (G1 version, boxes classified by evidence: verified in a run, on a tested branch, to be written; run B-20261120-223319-cc5320d), looked at by the lead | PASS |
| C11 | Schematic: Data-flow diagram | note/figures/schem_dataflow.png (initial data, AthenaK, outputs, analysis, comparison, ledger; run B-20261120-223319-cc5320d), looked at by the lead | PASS |
| C12 | Data figure: Baseline results | note/figures/fig_scan.png, fig_waves.png, fig_r2.png, fig_newton.png; first_source/figs/scan_kk0.png, res_compare.png; newton_tests/figs/pancake_east.png, ell_convergence.png | PASS |
| C13 | Data figure: Validation figures for the analysis pipeline | note/figures/fig_waves.png (both diagnostics against exact waves), fig_gauge.png; first_source/figs/t0_gauge.png, scan_null.png; stage/G1/verifier3/figs (v3_F_conv, v3_X_conv, v3_F_diag_diff, v3_X_diag_diff, v4_gauge_test); stage/review_wave3/figs/lw3_crit1.png | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, STATUS.md, VERIFIER.md (verifier2) and verifier3/VERIFIER.md in stage/G1/; the lead's rechecks are stage/REVIEW-wave2.md and stage/REVIEW-wave3.md (task-given names); scoping text scope/SCOPE.md | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | every data figure from a registered run with one script each (figstyle), looked at; the note's figures and tables are byte copies of run B-20261120-223319-cc5320d (28 of 28, cmp by the lead) | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | schem_architecture (exists / on a tested branch / to be written) and schem_timeline (G0 passed, G1 needs) with paperfig, note/scripts/schem_*.py, run B-20261120-223319-cc5320d; looked at | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | note/main.pdf v2, 21 pages (REVTeX), built from run B-20261120-223319-cc5320d; latexmk: 0 undefined references or citations, 0 overfull boxes; the paper-writing checker is clean in the main text except the allowed delta = 0.0025 hits (note/JOURNAL.md, outcome N16); all pages read by the note helper. Rewordings owed for v3: ledger rows 101, 118-119, 168 (stage/REVIEW-wave3.md) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | in part: independent verifiers recomputed the G1 claims of wave 1 (stage/G0/VERIFIER.md), the wave-2 first-source and Newtonian runs (stage/G1/VERIFIER.md, verifier2: 12 confirmed, 3 in part, none wrong) and the criterion-1 table and gauge rows 101, 115-119 (verifier3); not recomputed by an independent agent: the second-round table of the ledger (jittered nulls, delta = 0.0025, rerun floor, parity; checked only by the note helper's own second reading, N13-N15), gauge rows 120-125, eps = 0.1 and 0.3 of rows 116-117, and the wave-1 rows outside the G0 claims. Owed: one verifier package that recomputes every remaining ledger row (no card time) (OPEN.md item 1) | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed predictions and runs on record: first_source/JOURNAL.md (P1 as worded, P4, P6 with G), newton_tests/JOURNAL.md (P1a, P1b, P2a, H1a, H1c, H1d-3, N1d, N1e), waves/JOURNAL.md (F4, F6, X6, X3 at N = 32, A3, plus phase at N >= 48, cost), note/JOURNAL.md (N8 in part, N12 plus phase at N = 32, N16 page count), verifier2 and verifier3 journals (P3.5, P4.5, P4.7), population/JOURNAL.md (P2, P5, P8, P10b, I1), stage/review_wave2 (R5, R6) and stage/review_wave3 (L1 marginal, L2, L2b, L3); failed runs kept: B-20261115-161656-03d75e1, -164104-886798f, -170149-75036cf, B-20261119-142234-85da208, -145125-51e9f8f, -141813-91cfe8e, -143836-644f0a9, B-20261120-222232-3d7d57e, -223445-3686145, B-20261121-025612-ed4a875, -030110-52ae004 | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten by the lead at the end of batch 2a (2026-11-20) | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T07:20:08Z, clean export of `1197792fa0da`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 3 uncommitted paths: commit them first (tracks/B-emd-gw/gw_diag/gwdiag/gauge.py, tracks/B-emd-gw/gw_diag/tests/test_gauge.py, tracks/B-emd-gw/waves/scripts/check_gauge.py) |
| sync | FAIL | main has commits not merged: run nrpic-ctx sync |
| export | PASS | clean export of 1197792fa0da (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G1-1197792-20261121T064418Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 11 figures, each with its script |
| min-figs | PASS | 3 schematics and 8 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | PASS | 234 run manifests finished (78 hand-written, read as decision 0012 allows); failures of 1 runs waived by coord/WAIVERS.md (decision 0019), output checksums verified where recorded |
| runs-waived | WARN | failures of the manifest check waived: 1 runs named in main's coord/WAIVERS.md (decision 0019 item 6): B-20261115-164157-40b9f6d: outputs moved into the run directory after the run finished; data unchanged |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 34 lines |
| rerun | PASS | 11 of 11 scripts and commands ran cleanly in the export |
| compare | PASS | 22 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 22 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_baseline.* | note/scripts/fig_baseline.py | data | to be confirmed by the session |
| note/figures/fig_gauge.* | note/scripts/fig_gauge.py | data | to be confirmed by the session |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | to be confirmed by the session |
| note/figures/fig_pancake.* | note/scripts/fig_pancake.py | data | to be confirmed by the session |
| note/figures/fig_r2.* | note/scripts/fig_r2.py | data | to be confirmed by the session |
| note/figures/fig_scan.* | note/scripts/fig_scan.py | data | to be confirmed by the session |
| note/figures/fig_source.* | note/scripts/fig_source.py | data | to be confirmed by the session |
| note/figures/fig_waves.* | note/scripts/fig_waves.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

`tracks/B-emd-gw/stage/G1/VERIFIER.md` present; its first lines:

> # Verifier report: the wave-2 runs of B-emd-gw for gate G1 (verifier2, 2026-11-19)
> 
> Independent verification (item C18 of `CHECKLIST.md`) of the first-source scan in full GR
> (crossed waves (1, eps, 0), runs B-20261115-164059-d802e82, -165353-b592d43 on cards at 64^3,
> -165525-f7c2004 on processors at 32^3) and of the Newtonian-mode tests (pancakes
> B-20261115-165349-81a17bc, -163556-ad5637f, -165351-b38db6f, -163558-20244f2,
> -163653-f6324ea; ellipsoid -163613-790095f, -163615-7bc8b30, -163617-085c093).
> 
> How it was done. I was a fresh reader: I did not read `stage/REVIEW-wave2.md`, the owner's
> STATUS, HANDOFF or journals, or the package journals until my own numbers were written into
> `JOURNAL.md` (commit 8519d1d1). I read the package READMEs for the set-up and the claims, the
> manifests, the inputs, `cosmo/ic/make_east.py` and the AthenaK writers

## Null results and failed runs

- `B-20261115-161656-03d75e1`: failed (exit -15), first_source: initial data of the crossed-wave scan (1, eps, 0), eps = 0, 0.1, 0.3, 1, delta = 0.01, box 4, 64^3, two particles per cell and direction (make_east.py, production deposit settings)
- `B-20261115-164104-886798f`: failed (exit 2), first_source: initial data of the crossed waves eps = 1 (rebuild; the case was cut off in B-20261115-161656-03d75e1), delta = 0.01, box 4, 64^3, two particles per cell and direction
- `B-20261115-170149-75036cf`: failed (exit 1), newton_tests analysis of P1, P2, H1 (pancakes n=16, 32 against Zel'dovich, pm.py, and the discrete-Laplacian growth law)
- `B-20261119-141201-1433762`: stopped (exit -15), verifier2 V2-V4: own flat-TT diagnostics (K1, K2 amplitudes of h and tilde A, full TT spectrum, plane-symmetry quantities, first-order potentials) on every bin and rst dump of the crossed-wave scan at 64^3 (cards) and 32^3 (processors)
- `B-20261119-141813-91cfe8e`: failed (exit 1), verifier2 V2-V4: comparison of the own TT diagnostics (run B-20261119-141219-b391580) with the derived second-order reference s g(eta), linearity in eps, plane-symmetric null, 32^3 against 64^3, raw difference of the two spatial gauges; figures
- `B-20261119-142234-85da208`: failed (exit 127), waves test X at N=48 (processor insurance for the queued card run)
- `B-20261119-143348-728c0e5`: stopped (exit -15), population N-fid: Newtonian mode (release core-v0.3, processors) of the EMD random-field box, L=4, 64^3, nc=3.2, sigma1=0.0562, seed 1, 1 ppc, to a=100; halos, masses, TT-stress GW signal
- `B-20261119-143836-644f0a9`: failed (exit 1), population design: semi-analytic scales vs box size, BBKS and Press-Schechter halo counts, baseline (model A) GW energy per maximum of the seed-1 field, quasi-static second-order TT floor, relativistic card cost at 64/128/256
- `B-20261119-145125-51e9f8f`: failed (exit 1), waves: provisional analysis of tests F and X at N=16,32 (TT and Weyl diagnostics vs exact; predictions F1-F6, X1-X6)
- `B-20261119-145328-4b3663f`: stopped (exit -15), population N-amp2: as N-fid with sigma1 doubled (0.1124), seed 1, to a=100; collapse-time and signal scaling P4, P9; snapshots every 0.0625
- `B-20261119-153724-a6f1ab5`: stopped (exit -15), population analysis A-fid: halos, TT-stress GW energy (ng=64, radiated, switch-off and near-field measures), quadrupole formula of the 5 largest halos, of the fiducial 64^3 Newtonian run B-20261119-143828-0ef9b5b
- `B-20261119-154528-9306cb1`: stopped (exit -15), population I-gr: relativistic initial data (dictionary + constraint solve, production deposit) of the seed-1 field at 64^3 for L=4, 8, 16 (nc=3.2, sigma1=0.0562); prediction I1
- `B-20261120-222232-3d7d57e`: failed (exit 1), verifier3 V1: exact solutions of tests F and X, sympy and ODE checks (P1.1-P1.7)
- `B-20261120-223445-3686145`: failed (exit 1), shear smoke: S1 (beta 0.005, HL 1) N_y=32, release processor exe, initial data, rays, observer; pipeline check
- `B-20261121-025612-ed4a875`: failed (exit -15), verifier3 V3: own TT and Weyl/Psi4 measurement of tests F (N16-64) and X (N16-64, x10) from the raw dumps (P3.1-P3.7)
- `B-20261121-030110-52ae004`: failed (exit 1), verifier3 V3 summary: amplitude/phase errors, TT-Weyl differences, orders, plus/cross, x1 vs x10, figures, from run B-20261121-025826-80973e3
- `B-emd-gw-20261115-120531-40a3597`: failed (exit 1), scouting: TT energy spectrum, TT/non-TT ratio and Weyl parts on the restart dumps of the full-GR cosmology runs dav_c256_n128_t and dav_c256_n128_pcs4bt
- `B-emd-gw-20261115-130926-a1c2237`: stopped (exit None), Lead re-check L1 of the five wave-1 packages: clean git-archive export of commit 2fb3dbff41a1dcba59577c9f8410ff4501f06f2c; all analysis scripts and tests rerun, results compared leaf by leaf with the committed/original results (compare_results.py); four periodic_z4c AthenaK cases re-executed with the release processor executable and compared byte by byte with the original runs

## Open risks


State 2026-11-20, batch 2a (lead); rows changed since wave 2 say so. Likelihood and effect are JUDGEMENT; the watch
column names the measurement that decides. Sources: `scope/SCOPE.md` section 8,
`stage/G0/REVIEW.md`, `stage/G0/VERIFIER.md`, `stage/REVIEW-wave2.md`, `stage/REVIEW-wave3.md`,
`stage/G1/verifier3/VERIFIER.md`, the helper journals.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 Spurious TT power from particle noise after shell crossing (brief line 745). In `cosmo/` the relative momentum-constraint violation is 2.9e-2 at a = 40 and 0.17 at a = 100 (`cosmo/TESTLOG.md` 1404-1415, 1674-1676). The crossed-wave scan on an aligned lattice has no noise to show (null at rounding, run B-20261115-190007-e09a0d2); the floor is unmeasured (verifier weakest point 2) | high | the post-crossing science claim | jittered-lattice nulls ran (round 2, first_source P11, P16): in the box modes the noise strain follows its second-order prediction and stays 0.015-0.031 of the eps = 0.1 signal; a quasi-static TT field near the mesh scale, linear in the jitter, of unresolved origin (batch 2a: unchanged) | read spectra below half the Nyquist wave number; the jitter-without-wave run decides between projector leakage and a response to the wave; eps >= 0.032 (a = 40) to 0.19 (a = 100) [JUDGEMENT bound]; descope to the pancake phase if the floor exceeds the eps = 1 signal at 128 cells |
| R2 Junk TT of conformally flat initial data | certain | biases the pre-crossing comparison | now modelled: the box-mode strain follows s g(tau) with the junk to 0.22-0.44 percent for 2 <= a <= 10 (first_source P2, rechecked) | keep the full second-order solution s g(tau) as the reference; initial data with a TT part deferred by core |
| R3 Near field against radiation in a box | measured: high | the box-mode signal before and after shell crossing is a quasi-static spin-2 field, not radiation: rho_kin/rho_grad <= 0.04 (first_source; K1 mode <= 0.013 for a >= 12, lead) | rho_kin against rho_grad per band; virial frequency against c k_1 | report rho_K (propagating) and the strain (static) separately; the radiated signal needs larger boxes (L = 8) or later times; L = 4 stays the first box |
| R4 Gauge and hypersurface dependence of h^TT (2111.09163 `prd_v1.tex:369-426`; 1704.03500 `GW2nd_ApJ.tex:245`) | medium (was high) | a gauge piece mistaken for a signal | spatial-gauge piece G_tot measured: < 1.1 percent of c_+ for a <= 20, ~10 percent near shell crossing; a second spatial gauge agrees after G_tot (difference reduced twelvefold); the wave-1 late rise is not gauge (runs -164616-a6d9477, -171804-42e975b) | report raw and G_tot-corrected strain; G_tot confirmed by verifier3 (term by term, eps^3 on exact pure-gauge data); its residual after the gauge piece (2.3e-5 to 2.7e-3 of c_+, a = 5-60) is above the third-order estimate and nearly resolution-independent [untested JUDGEMENT: particle or deposit differences]; the direct map leaves 1-6 times less than G_tot at a >= 10; slicing piece only bounded; York projection; lapse as third convergence leg |
| R5 Gauge shocks of the production lapse (conformal time): in vacuum K/k ~ 0.24 makes a shock within two crossings | medium in collapse | non-convergent metric near caustics | Theta and lapse gradients against resolution | harmonic and 1+log as alternatives; joint gauge work with Track A (shared test accepted) |
| R6 Black-hole end: delta = 0.05 fails at a = 17.2 (`cosmo/TESTLOG.md` 1842-1852) | certain at large delta | caps the amplitude range | any slicing that passes collapse (Track A: none yet, its message 18:37Z) | range to 0.02 until then (stop rule) |
| R7 Output volume: restart dumps carry the particles (380 MB per dump at 2.1M particles, 12 GB per run) | medium (was high) | limits cadence and resolution | dump size per run | double-precision bin output is in release core-v0.4 and used by every new deck (verifier3: float32 puts a floor of 3-7e-6 under gauge differences); a 256^3 double dump is 2.7 GB, 100 per run: in-situ low-k Fourier output requested from core (batch 2a) |
| R8 Dependence on core: species history (N2), in-situ Fourier output, initial data at large amplitude (generator fix, jitter and double precision are in core-v0.4 since 2026-11-21) | medium (was medium) | delays N2 and the G3 population runs | core's answers; READY of core-v0.4 id_solve on the torus | the release executables for new runs; population tests id_solve at L = 8 before any request |
| R9 Literature comparison: 2212.00425, 2312.12499 read at abstract level only; the Omega-today scaling of 2403.15126 is sigma^(5/2) with its own eq. (result_OmZ), not the stated 7/2 (verifier C8); the 144-392 prefactor gap varies as theta^(2/3) | medium | the "when does GR matter" comparison has no quantitative anchor | reading of the papers' spectra; kb claims; batch 2a: 2312.12499 lines 324 and 581 differ by a factor 3 in delta (kb request) | compare emitted energies (7/2 holds at emission), not Omega today, until settled; normalize with Phi = (3/5) R and the matter-era Poisson relation |
| R10 Particle-number convergence of the background, growth and first-source rows not shown | medium | G2 criterion | the runs exist (first source: B-20261119-153655-2deca0a, scan analyses -223236-e213594, -223241-f1efd4f; flrw_conv: J1 B-20261120-222955-c8e16e3, P1 -223006-24448ac), none analysed | analyse first; J2, J3 of flrw_conv (1.25 card-h) after that |
| R11 Overlap: 2605.04487 names a fully relativistic treatment as future work (`main_v3.tex:2630`); 2312.12499 says the same (`main.tex:115`) | medium | novelty | arXiv listings | keep the plane-symmetric null, the gauge-controlled box-mode strain and the GR-minus-Newton statement per k as the distinct contribution |
| R12 Short second-order comparison window: at delta = 0.01 the strain departs from s g by 1-2 percent at a = 20 and 6-11 percent at a = 40, growing with eps (beyond second order; 2610.08045 `main.tex:40-49`: secular growth of higher orders in matter domination) | certain | pre-crossing accuracy claims limited to a <= 10 | measured at delta = 0.0025 (round 2, P14): the departure falls as delta^2 (R = 17-19), window |dev| <= 0.5 percent to a = 34-42 | quote the window; the (1 + eps^2) reading has its advance test written, not run |
| R13 Newtonian reference force error (kh)^2/12 of the seven-point Laplacian (3.2e-3 at kh = 2 pi/32) | certain | biases GR-minus-Newton per mode at the 1e-3 level | core's answer on a fourth-order option | quote it with every comparison or use the spectral pm.py as a second Newtonian reference |
| R14 Rounding-level numbers depend on the reading (batch 2a): the X plus amplitude at N >= 48 differs by 1.3e-8 to 1.6e-8 between the modulus of the complex amplitude and its in-phase part | certain at amplitude 1e-6 | a disputed number in a ledger | state the measure next to every number below 1e-7 relative; the x10 runs give the truncation part | quote truncation errors from the cross polarization or from x10 runs |
| R15 Usage-limit cuts strand runs and files (2026-11-19 and 2026-11-20: seven runs ended unattended, one package's outputs uncommitted, a gauge module left uncommitted) | high | lost or unregistered work | `git status`, `nrpic-run status` at every session start | leads close finished runs with `nrpic-run finish`; helpers commit after every step |

## Decision requested from the group

Not requested yet. The lead judges G1 not met: criteria 1 and 2 are met (criterion 1 read three times: waves, verifier3, the lead's third reading), criterion 3 is struck (decision 0013), schematics and note v2 pass; item C18 is open in part (ledger rows not yet recomputed by an independent verifier; stage/G1/OPEN.md item 1). The gate will be requested after the verifier4 package. verify FAIL is on clean (three untracked files of the waves package still in progress, left as found) and sync (main moved during the 25-minute run; merged afterwards); every other check passes, runs included.

## Lead's assessment (batch 2a, 2026-11-20)

G1 is not met; one item is owed. Per criterion of the track sheet as ruled by decision 0013
(details in `STATUS.md`, evidence in `EVIDENCE.md`, the recheck in `../REVIEW-wave3.md`):
1. Two diagnostics on analytic linear waves: MET for an oblique flat wave (k = 2 pi (1,1,1))
   and a tensor mode of the expanding matter-era box, N = 16-64, both polarizations, against
   exact solutions; independent verifier (verifier3) and a third reading by the lead (runs
   B-20261121-063617-6183015, -063835-826c461); the one disputed number (X plus amplitude at
   N >= 48) is a difference of definition at the rounding level.
2. Newtonian baseline reproduces the literature scaling: MET (wave 2), now confirmed by
   verifier2 (run B-20261119-142135-e582e09); the Omega-today scaling of 2403.15126 stays
   [TO VERIFY] and is not used.
3. Stand-in matter: struck (0013).
Products: schematics (architecture, data flow, timeline) and the note v2 (21 pages) PASS.
Owed: C18, an independent recomputation of the ledger rows no verifier has recomputed
(`OPEN.md` item 1; requested from orch, outbox 20261121T065439Z). The verify FAILs are
`clean` (three untracked files of the waves package in progress, left as found) and `sync`
(main moved during the run and was merged afterwards); `runs`, `rerun`, `compare` and
`regenerate` pass.

## Lead's assessment (wave 2, superseded)

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
