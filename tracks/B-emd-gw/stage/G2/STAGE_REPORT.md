# Stage report: B-emd-gw G2

Date: 2026-11-23 · branch `track/B-emd-gw` at `b9d2a15edbed` · checklist
`tracks/B-emd-gw/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/B-emd-gw/G2-fail-20261123` (created and pushed by the orchestrator after review, decision 0003).

- 14 checklist items not PASS or NA: C1 OPEN, C2 OPEN, C3 OPEN, C5 OPEN, C6 OPEN, C9 OPEN, C10 OPEN, C11 OPEN, C13 OPEN, C14 OPEN, C15 OPEN, C16 OPEN
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
| C1 | The code paths used by the track pass their tests of §10 | FLRW dust and linear growth rows of section 10 pass (flrw_conv, entry 12: runs B-20261120-222955-c8e16e3, -223006-24448ac, B-20261121-202304-dc3020e, -202335-3e6a898, analyses B-20261121-220428-7367d5e, B-20261123-015452-18d2956); GW diagnostics on analytic waves passed at G1 (signed). Open: the shearing-dust row (L2 without result, shear journal 2026-11-22 18:00) and the population box in full GR (queued). | OPEN |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | Mesh 16-128 and particle number 1-27 per cell: flrw_conv (fig_b_conv, fig_f_scaling); step: P3/P4 (B-20261121-220450-e011c57, -222813-560158b). Gauge leg missing: the f = 1 lapse leg of the shear series stopped at the guard (B-20261121-202830-417af0c, S1_n64_lap1). | OPEN |
| C3 | Constraints behave | flrw_conv: largest Hr 3e-9 to 6e-8, mean-density error <= 4e-9 to a = 1000, but Hr grows with N (entry 12). shear: t = 0 momentum constraint fourth order; up to ray arrival below 1e-4 but rising with N_y at HL = 1/16, 1/128 (B-20261123-015919-dec4392). Cause of the rise not tested. | OPEN |
| C4 | A first minimal full-GR kinetic run | Full-GR kinetic runs with particles coupled to Z4c in the periodic box: flrw_conv J3 B-20261121-202335-3e6a898 (128^3 to a = 1000), shear series B-20261121-202830-417af0c; the population box in full GR is queued (B-20261123-014847-f295ab4, Slurm 4921). | PASS |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | STAGE_REPORT.md generated in batch 10a as a progress record; the verification report itself waits for C1-C3, C9. | OPEN |
| C6 | Reproducibility package | Manifests, decks and scripts exist per package (flrw_conv/README.md "How to rerun"); no package-level reproducibility list yet. | OPEN |
| C7 | The scale-factor error and the linear growth rate of the particle FLRW run reach the sub-percent level and converge in particle number and mesh | Met at 16-128 cells: flrw_conv/README.md "Verdict", JOURNAL entries 7, 9-12; runs above; figures fig_b_conv, fig_b_error, fig_f_lattice, fig_f_noise, fig_f_scaling (looked at). | PASS |
| C8 | Agreement with gevolution in the weak-field regime | Replaced by C9 (decision 0013: gevolution is not run; the multi-code row is the shearing-dust comparison and full GR against the Newtonian mode). | NA |
| C9 | Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013) | Shearing dust (arXiv:2003.08014): S1-S4, M1, L1 judged (shear journal 2026-11-22 18:00; S within 1e-5 of linear, M1 and L1 inside the paper bounds, M2 sign against the prediction); L2, the case that separates the codes, has no number. Full GR against the Newtonian mode: GR population runs queued (pop_s014_gr Slurm 4921; pop_s028_gr behind a re-solve of its data B-20261123-014850-7b7d986). | OPEN |
| C10 | Schematic: Verification ladder | No verification-ladder schematic yet. | OPEN |
| C11 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | Mesh and particle number: flrw_conv/figs/fig_b_conv.png, fig_f_scaling.png; gauge: none. | OPEN |
| C12 | Data figure: Constraint norms against time | flrw_conv/figs/fig_b_constraints.png (largest Hr against a, 16-128 cells), fig_f_constraints.png; shear/figs/fig_series.png (means up to arrival). | PASS |
| C13 | Data figure: At least one multi-scale slice mosaic with zoom boxes | No slice mosaic; planned from the population box snapshots. | OPEN |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | CHECKLIST, EVIDENCE, OPEN and STAGE_REPORT exist (batch 10a); REVIEW: stage/REVIEW-wave3.md section "Batch 10a". | OPEN |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | Figures from registered runs and looked at (flrw_conv, shear), but analyze_b.py and analyze_f.py draw several figures each; defects noted (legend over the 128 curve in fig_b_error, cut label in fig_series). | OPEN |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | G2 schematics not drawn. | OPEN |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | No G2 section in the working note yet. | OPEN |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | No G2 verifier yet. | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | Failed predictions and runs on record: flrw_conv entries 7, 9-12 (PB3 floor, J3 quarter rule, P2, P3), shear journal (P4 Hamiltonian order, P7 S3, P8 M2 sign, P9 L2 and P10 without result, P12), population journal 2026-11-22 (0.028 data above tolerance), shear series manifest closed as failed. | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | Rewritten at the end of batch 10a. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

Not run: `harness/bin/nrpic-stage verify B-emd-gw G2`.

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

MISSING: the verifier subagent has not reported (`stage/G2/VERIFIER.md`, decision 0016).

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
- `B-20261121-202503-abdf6f0`: failed (exit 1), shear series 1: S1-S4, M1-M2, L1-L2 at N_y = 32, 64, 128 and legs lapse f = 1, 2 and 4 particles per cell; G2 multi-code row (shearing dust of arXiv:2003.08014)
- `B-20261121-202830-417af0c`: failed (exit 1), shear series 1 (resubmitted after the fan-argument fix): S1-S4, M1-M2, L1-L2 at N_y = 32, 64, 128 and legs lapse f = 1, 2 and 4 particles per cell
- `B-emd-gw-20261115-120531-40a3597`: failed (exit 1), scouting: TT energy spectrum, TT/non-TT ratio and Weyl parts on the restart dumps of the full-GR cosmology runs dav_c256_n128_t and dav_c256_n128_pcs4bt
- `B-emd-gw-20261115-130926-a1c2237`: stopped (exit None), Lead re-check L1 of the five wave-1 packages: clean git-archive export of commit 2fb3dbff41a1dcba59577c9f8410ff4501f06f2c; all analysis scripts and tests rerun, results compared leaf by leaf with the committed/original results (compare_results.py); four periodic_z4c AthenaK cases re-executed with the release processor executable and compared byte by byte with the original runs

## Open risks


State 2026-11-22, batch 10a (lead); rows changed since batch 5 say so (R9, R10, R17, R18, R19, R20). Likelihood and effect are JUDGEMENT; the watch
column names the measurement that decides. Sources: `scope/SCOPE.md` section 8,
`stage/G0/REVIEW.md`, `stage/G0/VERIFIER.md`, `stage/REVIEW-wave2.md`, `stage/REVIEW-wave3.md`,
`stage/G1/verifier3/VERIFIER.md`, the helper journals.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 Spurious TT power from particle noise after shell crossing (brief line 745). In `cosmo/` the relative momentum-constraint violation is 2.9e-2 at a = 40 and 0.17 at a = 100 (`cosmo/TESTLOG.md` 1404-1415, 1674-1676). The crossed-wave scan on an aligned lattice has no noise to show (null at rounding, run B-20261115-190007-e09a0d2); the floor is unmeasured (verifier weakest point 2) | high | the post-crossing science claim | jittered-lattice nulls ran (round 2, first_source P11, P16): in the box modes the noise strain follows its second-order prediction and stays 0.015-0.031 of the eps = 0.1 signal; a quasi-static TT field near the mesh scale, linear in the jitter; batch 4a: the run without a wave (P16', B-20261121-080222-2293fae) shows it is projector leakage of the noise at a <= 2.3 (D = 0.994, 0.856 at 64^3); by a = 12 the wave adds grid-scale TT and non-TT power that the runs cannot separate | read spectra below half the Nyquist wave number (k h >= pi/2 cut, now tested); a run that separates wave-modulated noise from a response at a = 12 is G2 work; eps >= 0.032 (a = 40) to 0.19 (a = 100) [JUDGEMENT bound]; descope to the pancake phase if the floor exceeds the eps = 1 signal at 128 cells |
| R2 Junk TT of conformally flat initial data | certain | biases the pre-crossing comparison | now modelled: the box-mode strain follows s g(tau) with the junk to 0.22-0.44 percent for 2 <= a <= 10 (first_source P2, rechecked) | keep the full second-order solution s g(tau) as the reference; initial data with a TT part deferred by core |
| R3 Near field against radiation in a box | measured: high | the box-mode signal before and after shell crossing is a quasi-static spin-2 field, not radiation: rho_kin/rho_grad <= 0.04 (first_source; K1 mode <= 0.013 for a >= 12, lead) | rho_kin against rho_grad per band; virial frequency against c k_1 | report rho_K (propagating) and the strain (static) separately; the radiated signal needs larger boxes (L = 8) or later times; L = 4 stays the first box |
| R4 Gauge and hypersurface dependence of h^TT (2111.09163 `prd_v1.tex:369-426`; 1704.03500 `GW2nd_ApJ.tex:245`) | medium (was high) | a gauge piece mistaken for a signal | spatial-gauge piece G_tot measured: < 1.1 percent of c_+ for a <= 20, ~10 percent near shell crossing; a second spatial gauge agrees after G_tot (difference reduced twelvefold); the wave-1 late rise is not gauge (runs -164616-a6d9477, -171804-42e975b) | report raw and G_tot-corrected strain; G_tot confirmed by verifier3 (term by term, eps^3 on exact pure-gauge data); its residual after the gauge piece (2.3e-5 to 2.7e-3 of c_+, a = 5-60) is above the third-order estimate and nearly resolution-independent [untested JUDGEMENT: particle or deposit differences]; the direct map leaves 1-6 times less than G_tot at a >= 10; slicing piece only bounded; York projection; lapse as third convergence leg |
| R5 Gauge shocks of the production lapse (conformal time): in vacuum K/k ~ 0.24 makes a shock within two crossings | medium in collapse | non-convergent metric near caustics | Theta and lapse gradients against resolution | harmonic and 1+log as alternatives; joint gauge work with Track A (shared test accepted) |
| R6 Black-hole end: delta = 0.05 fails at a = 17.2 (`cosmo/TESTLOG.md` 1842-1852) | certain at large delta | caps the amplitude range | any slicing that passes collapse (Track A: none yet, its message 18:37Z) | range to 0.02 until then (stop rule) |
| R7 Output volume: restart dumps carry the particles (380 MB per dump at 2.1M particles, 12 GB per run) | medium (was high) | limits cadence and resolution | dump size per run | double-precision bin output is in release core-v0.4 and used by every new deck (verifier3: float32 puts a floor of 3-7e-6 under gauge differences); a 256^3 double dump is 2.7 GB, 100 per run: in-situ low-k Fourier output requested from core (batch 2a) |
| R8 Dependence on core: in-situ Fourier output (accepted by core, no branch), initial data at large amplitude; species history and the spectral Poisson symbol are in core-v0.6 (batch 4a) | medium (was medium) | delays N2 and the G3 population runs | core's answers; READY of core-v0.4 id_solve on the torus | the release executables for new runs; population tests id_solve at L = 8 before any request |
| R9 Literature comparison: 2212.00425, 2312.12499 read at abstract level only; the Omega-today scaling of 2403.15126 is sigma^(5/2) with its own eq. (result_OmZ), not the stated 7/2 (verifier C8); the 144-392 prefactor gap varies as theta^(2/3) | medium | the "when does GR matter" comparison has no quantitative anchor | reading of the papers' spectra; kb claims; 2312.12499 L325 and L582 differ by a factor 3 in delta: kb claim 861 (judgement; which one the results use is not established) | compare emitted energies (7/2 holds at emission), not Omega today, until settled; normalize with Phi = (3/5) R and the matter-era Poisson relation |
| R10 Particle-number and mesh convergence of the background and growth rows (batch 10a: closed) | retired | - | flrw_conv: met at 16-128 cells and 1-27 per cell (entries 7, 9-12; B-20261123-015452-18d2956); amplitude floor about 2e-6 from the start step (P3, P4 at 32 cells; J4 at 128 queued) | none for criterion (a); production step limit 0.01 gives a larger start error, measured by J4 |
| R11 Overlap: 2605.04487 names a fully relativistic treatment as future work (`main_v3.tex:2630`); 2312.12499 says the same (`main.tex:115`) | medium | novelty | arXiv listings | keep the plane-symmetric null, the gauge-controlled box-mode strain and the GR-minus-Newton statement per k as the distinct contribution |
| R12 Short second-order comparison window: at delta = 0.01 the strain departs from s g by 1-2 percent at a = 20 and 6-11 percent at a = 40, growing with eps (beyond second order; 2610.08045 `main.tex:40-49`: secular growth of higher orders in matter domination) | certain | pre-crossing accuracy claims limited to a <= 10 | measured at delta = 0.0025 (round 2, P14): the departure falls as delta^2 (R = 17-19), window |dev| <= 0.5 percent to a = 34-42 | quote the window; the (1 + eps^2) advance test holds to 0.6-3.6 per cent for a = 30-60 at delta = 0.0025 and fails at a = 20 (Q = 1.10-1.16; batch 2b, confirmed by verifier_c18): quote its range |
| R13 Newtonian reference force error (kh)^2/12 of the seven-point Laplacian (3.2e-3 at kh = 2 pi/32) | certain | biases GR-minus-Newton per mode at the 1e-3 level | core-v0.6: newton_poisson = fft with the spectral symbol removes it (core's pancake: 4.6e-5 at n = 64 against 1e-3 with seven points) | new GR-Newton comparisons use the spectral symbol, or quote the error |
| R14 Rounding-level numbers depend on the reading (batch 2a): the X plus amplitude at N >= 48 differs by 1.3e-8 to 1.6e-8 between the modulus of the complex amplitude and its in-phase part | certain at amplitude 1e-6 | a disputed number in a ledger | state the measure next to every number below 1e-7 relative; the x10 runs give the truncation part | quote truncation errors from the cross polarization or from x10 runs |
| R15 Usage-limit cuts strand runs and files (2026-11-19 and 2026-11-20: seven runs ended unattended, one package's outputs uncommitted, a gauge module left uncommitted) | high | lost or unregistered work | `git status`, `nrpic-run status` at every session start | leads close finished runs with `nrpic-run finish`; helpers commit after every step |
| R16 C18 of G1 needed one more verifier session (batch 4a) | retired (batch 5) | - | verifier_c18b ran (56 of 58 numbers confirmed, none wrong); line 59 reworded | none: G1 package complete for review |
| R17 Unattended queue: the sequencer (cards/sequencer.py) submits card chains and starts processor runs between sessions and commits manifests (nrpic-run) in the worktree. Batch 10a: an entry whose condition never held waited without a log line and, because card entries go in file order, blocked every later card run for 19 hours (pop_s028_gr behind unconverged data) | measured | runs not submitted | scratch/B-emd-gw/sequencer/sequencer.log now has a 'waiting:' line per entry and reason; state.json | queue entries whose inputs may fail go last or get an alternative; a lead reads the 'waiting:' lines at every session start; STOP file to halt it |
| R18 Literal harmonic slicing in the shearing-dust test: the S1 leg with lapse_harmonic = 1 stopped at t = 0.578 (guard: non-finite Khat; nine cells with a non-positive metric determinant first), run B-20261121-202830-417af0c | measured | P10 of shear and the gauge leg of the G2 three-way convergence untested | the athena.log of S1_n64_lap1; a run at N_y = 32 or smaller step on processors | cause not yet established; compare in the production lapse (f = 1/3) only until a run shows why f = 1 fails |
| R19 Shearing-dust L2 (beta = 0.5, HL = 4) has no number (new, batch 10a): the ray analysis returns NaN at every N_y (analyze_rays.py:182); M2 has the opposite sign to the prediction | measured | the case that separates the codes (CosmoGRaPH -0.8183, draft.tex:360) is missing from the multi-code row | L2_n64/rays.json miss values, trajectories | diagnose the fan on processors before any new run |
| R20 Constraint means growing with resolution (new, batch 10a): FLRW leg B largest Hr 3e-9, 1.3e-8, 6.2e-8 at 32, 64, 128 cells; shear S2 and S4 means rise with N_y | medium | 'constraints behave' (G2 C3) not shown at fine meshes | a run that changes the precision of the second differences, or the cell size at fixed time step | round-off amplified by 1/h^2 is a candidate, not tested; quote the values |

## Decision requested from the group

None requested: progress record of batch 10a. G2 is not met; stage/G2/OPEN.md lists what it lacks (population GR against Newtonian mode, shear L2, gauge leg, package products).
