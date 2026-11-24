# Stage report: B-emd-gw G2

Date: 2026-11-24 · branch `track/B-emd-gw` at `d3e21f74a302` · checklist
`tracks/B-emd-gw/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/B-emd-gw/G2-fail-20261124` (created and pushed by the orchestrator after review, decision 0003).

- 12 checklist items not PASS or NA: C1 OPEN, C2 OPEN, C3 OPEN, C5 OPEN, C6 OPEN, C9 OPEN, C11 OPEN, C14 OPEN, C15 OPEN, C16 OPEN, C17 OPEN, C18 OPEN
- verify ran on 2116dce; files changed since: coord/DECISIONS/0032-new-account-preemption-allotments.md, harness/workflows/batch-11b.json, harness/workflows/batch-R2b.json, tracks/B-emd-gw/HANDOFF.md, tracks/B-emd-gw/RISKS.md, tracks/B-emd-gw/STATUS.md (run verify again)
- verify reported FAIL: runs
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G2/STAGE_REPORT.md` | present |
| `stage/G2/EVIDENCE.md` | present |
| `stage/G2/OPEN.md` | present |
| `stage/G2/CHECKLIST.md` | present |
| `stage/G2/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G2/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | FLRW dust and linear growth rows pass (flrw_conv entries 7-12; J4 B-20261123-015905-7a30278 with analysis B-20261124-125457-79ce723 confirms the amplitude floor at 128 cells is the start step); GW diagnostics on analytic waves passed at G1 (signed). Shearing dust: S1-S4, M1, L1 judged (B-20261123-015919-dec4392), P10 holds (f = 1 against f = 1/3: -8.7e-5, B-20261124-131336-bc61eee); L2: with narrow fans (series 3, B-20261124-134209-4584052; summary B-20261124-134720-c753aff) Delta = -0.828, -0.830, -0.835 at N_y = 32-128, near CosmoGRaPH (-0.8183) and far from gevolution and GRAMSES, not converging, in a field with relative constraint means of 0.1-0.4 from a = 2.25 on at every N_y (B-20261124-135244-17ebf5c); at 4 particles per cell along y the mesh gives -0.822, -0.831, -0.839 at N_y = 64, 128, 256 (series 5-6, B-20261124-140856-911ded9, summary B-20261124-172643-d1e88c7): L2 not converged in this code. S3 has a floor of 2-3e-5 (N_y = 256). Population in full GR: sigma1 = 0.014 to a = 143 (B-20261123-014847-f295ab4) matches the Newtonian population at equal stage and the design's near field for 6 <= a <= 20 (analysis B-20261124-131918-e71996f, figures B-20261124-133150-e9ef701); sigma1 = 0.028 stops at a = 30.7 in the densest core (B-20261123-035002-bcc82bd; restarts X0-X3 queued, B-20261124-133533-cb0bb7d). Open: a converged L2 number, the 0.028 stop. | OPEN |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | Mesh 16-128 and particle number 1-27 per cell: flrw_conv (fig_b_conv, fig_f_scaling); step at 32 cells (P3/P4, B-20261121-220450-e011c57, -222813-560158b) and at 128 cells (J4, figs/fig_step128.png). Gauge: one slicing point at one mesh (shear S1 at N_y = 64, f = 1 against f = 1/3: -8.7e-5 relative, inside the 1e-4 bar; B-20261124-131336-bc61eee); the f = 1 run stops at t = 0.578, after the rays arrive. Shearing dust L2 at 4 per cell along y: mesh differences 9.4e-3, 7.9e-3 at N_y = 64-128-256 (order about 0.25, B-20261124-172643-d1e88c7, shear/figs/fig_ppc.png): no mesh convergence there. No convergent gauge leg; population has no mesh or particle-number leg yet (initial data at 128^3 x 8 per cell and 256^3 solving on processors, B-20261124-135029-3fe13f6, -135030-b54972f; gauge, particle and mesh chains queued behind them in cards/queue.json). | OPEN |
| C3 | Constraints behave | flrw_conv: largest Hr 3e-9 to 6e-8, mean-density error <= 4e-9 to a = 1000, Hr grows about as N^2 (cause untested). shear: t = 0 momentum constraint fourth order; means below 1e-4 to ray arrival but rising with N_y at HL = 1/16, 1/128. Population (sigma1 = 0.014): Hr_mean 1.6e-4 at a = 29 and 2.85e-2 at a = 141, Mr_mean 0.20 at a = 141, both growing monotonically after the halos form (figs/pop_gr_constraints.png; B-20261124-131918-e71996f). Shearing dust L2: relative means 0.1-0.4 from a = 2.25 on at N_y = 32-128, not falling with N_y (B-20261124-135244-17ebf5c). Not shown to behave at late times, large amplitude or fine meshes. | OPEN |
| C4 | A first minimal full-GR kinetic run | Full-GR kinetic runs with particles coupled to Z4c in the periodic box: flrw_conv J3 B-20261121-202335-3e6a898 (128^3 to a = 1000), shear series B-20261121-202830-417af0c, the population box pop_s014_gr B-20261123-014847-f295ab4 (128^3, L = 8, 2.1e6 particles, to a = 143, 0.19 card-h). | PASS |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | STAGE_REPORT.md generated in batch 10a as a progress record; the verification report itself waits for C1-C3, C9. | OPEN |
| C6 | Reproducibility package | Manifests, decks and scripts exist per package (flrw_conv/README.md "How to rerun"); no package-level reproducibility list yet. | OPEN |
| C7 | The scale-factor error and the linear growth rate of the particle FLRW run reach the sub-percent level and converge in particle number and mesh | Met at 16-128 cells: flrw_conv/README.md "Verdict", JOURNAL entries 7, 9-12; runs above; figures fig_b_conv, fig_b_error, fig_f_lattice, fig_f_noise, fig_f_scaling (looked at). | PASS |
| C8 | Agreement with gevolution in the weak-field regime | Replaced by C9 (decision 0013: gevolution is not run; the multi-code row is the shearing-dust comparison and full GR against the Newtonian mode). | NA |
| C9 | Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013) | Shearing dust (arXiv:2003.08014): S1-S4, M1, L1 judged (S within 1e-5 of linear, M1 and L1 inside the paper's bounds, M2 sign against the prediction); P10 holds; L2, the case that separates the codes: Delta = -0.828, -0.830, -0.835 at N_y = 32, 64, 128 (series 3, B-20261124-134209-4584052, figure shear/figs/fig_series2.png), 0.010-0.017 below CosmoGRaPH's -0.8183 and 0.15-0.2 below gevolution (-0.619) and GRAMSES (-0.68), not converging in N_y (shear journal 2026-11-24 06:50); at N_y = 64 it converges in particles along y to about -0.820 (1-8 per cell, series 4 and 5: B-20261124-135516-34befaf, -135951-237e27b, summary -140808-e6ba5c3), but at 4 per cell the mesh gives -0.822, -0.831, -0.839 at N_y = 64, 128, 256 (series 6, B-20261124-140856-911ded9): no mesh-converged number, each refinement moving away from CosmoGRaPH. Full GR against the Newtonian mode: the GR box at sigma1 = 0.014 has the halo counts and masses of the Newtonian fidL8 box at equal stage (H1: counts inside 2 sqrt(N) + 2 at a = 49-121, largest mass within -7 to +13 per cent, the five largest matched within 0.07) and the design's near-field strain to 9-13 per cent for 6 <= a <= 20 (A1), population/JOURNAL.md 2026-11-24 05:58. The same-particle Newtonian reference at 128^3 is queued (B-20261124-131438-5d7e049, predictions N1-N4). | OPEN |
| C10 | Schematic: Verification ladder | note/figures/schem_ladder.png (note/scripts/schem_ladder.py, run B-20261124-135151-8e1ac95; first drawing B-20261124-135136-563bd0a had overlapping legend labels): eight rungs from analytic waves to the population legs, each with its reference and state as of 2026-11-24; looked at. | PASS |
| C11 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | Mesh and particle number: flrw_conv/figs/fig_b_conv.png, fig_f_scaling.png; step: flrw_conv/figs/fig_step128.png; gauge: a single slicing point (shear rays.png of B-20261124-131336-bc61eee); no gauge convergence figure. | OPEN |
| C12 | Data figure: Constraint norms against time | flrw_conv/figs/fig_b_constraints.png (largest Hr against a, 16-128 cells), fig_f_constraints.png; shear/figs/fig_series.png (means up to arrival). | PASS |
| C13 | Data figure: At least one multi-scale slice mosaic with zoom boxes | population/figs/pop_gr_mosaic.png (run B-20261124-133709-85c4be7): the GR box at a = 132, particle density over the box with zooms L/4 and L/16 around the largest halo (zoom boxes drawn), and the lapse, K and flat TT strain on the same plane; looked at. Defect: the colour range of the K panel saturates in the halo core. | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | CHECKLIST, EVIDENCE, OPEN and STAGE_REPORT exist (batch 10a); REVIEW: stage/REVIEW-wave3.md section "Batch 10a". | OPEN |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | Figures from registered runs and looked at (flrw_conv, shear), but analyze_b.py and analyze_f.py draw several figures each; defects noted (legend over the 128 curve in fig_b_error, cut label in fig_series). | OPEN |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | G2 schematics not drawn. | OPEN |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | No G2 section in the working note yet. | OPEN |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | No G2 verifier yet. | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | Failed predictions and runs on record: flrw_conv entries 7, 9-12 (PB3 floor, J3 quarter rule, P2, P3); shear journal (P4 Hamiltonian order, P7 S3, P8 M2 sign, P12; L2 cause found 2026-11-24); population journal 2026-11-22 (0.028 data above tolerance) and 2026-11-24 (G1 cost below the range; G1 for 0.028: guard stop at a = 30.7, run B-20261123-035002-bcc82bd closed as failed; A1 fails from a = 36; A2 in part; A3 for the strain rms); failed analysis runs B-20261124-130512-d39dae4 and -131918-e71996f (figure step) on record. | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | Rewritten at the end of batch 11 (2026-11-24). | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-24T14:57:17Z, clean export of `2116dce48b65`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 2116dce48b65 (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G2-2116dce-20261124T135054Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 11 figures, each with its script |
| min-figs | PASS | 3 schematics and 8 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 4 of 323 runs have problems; 1 waived |
| runs-waived | WARN | failures of the manifest check waived: 1 runs named in main's coord/WAIVERS.md (decision 0019 item 6): B-20261115-164157-40b9f6d: outputs moved into the run directory after the run finished; data unchanged |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 44 lines |
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
| note/figures/schem_ladder.* | note/scripts/schem_ladder.py | schematic | to be confirmed by the session |
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
- `B-20261123-035002-bcc82bd`: failed (exit 1), population: full-GR run of the box, 128^3, L = 8, nc = 3.2, sigma1 = 0.028, seed 1, one particle per cell, to a = 143 (DESIGN.md section 8, scouting of the amplitude scan; predictions in population/JOURNAL.md 2026-11-21)
- `B-20261124-130512-d39dae4`: failed (exit 1), population: analysis of the full-GR runs sigma1 = 0.014 (to a = 143) and 0.028 (stopped at a = 30.7) against fidL8 and the design; predictions A1-A3, H1-H2, Z (JOURNAL 2026-11-24 05:15)
- `B-20261124-131918-e71996f`: failed (exit 1), population: analysis of the full-GR runs sigma1 = 0.014 (to a = 143) and 0.028 (stopped at a = 30.7) against fidL8 and the design; predictions A1-A3, H1-H2, Z (JOURNAL 2026-11-24 05:15); rerun of B-20261124-130512-d39dae4 with the guard-stop dump skipped
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
| R18 Literal harmonic slicing (f = 1) in the shearing-dust test: S1_n64_lap1 stopped at t = 0.578 (guard: non-finite Khat), run B-20261121-202830-417af0c | measured; P10 judged (batch 11) | the stop itself has no cause; the observable is not touched | batch 11: the rays arrive at t = 0.469 in that slicing, before the stop, and cos(theta) agrees with f = 1/3 to -8.7e-5 (P10 holds against 1e-4; run B-20261124-131336-bc61eee); constraints clean to t = 0.54, then growth by about seven per step | the f = 1 leg counts as a single-mesh gauge point; a convergent gauge leg needs a second slicing or shift at three meshes; the stop stays open (not needed for the observable) |
| R19 Shearing-dust L2 (beta = 0.5, HL = 4): Delta -0.828, -0.830, -0.835 at N_y = 32-128 with one particle per cell (series 3); at N_y = 64 it converges in particles along y to about -0.820 (1, 2, 4, 8 per cell: -0.830, -0.823, -0.822, -0.821; B-20261124-135951-237e27b, -135516-34befaf), beside CosmoGRaPH's -0.8183, but N_y = 128 at 4 per cell gives -0.831; relative constraint means 0.12-0.24 over the interval at every mesh and particle number (B-20261124-135244-17ebf5c, -140808-e6ba5c3) | measured | the multi-code row has a value near the relativistic code but no mesh-converged number | constraint means and Delta against N_y at 4-8 per cell | quote the particle-converged value at N_y = 64 with the mesh trend; next: N_y = 256 at 4 per cell and a cause of the constraint violation (the step is excluded, series 4) |
| R20 Constraint means growing with resolution (new, batch 10a): FLRW leg B largest Hr 3e-9, 1.3e-8, 6.2e-8 at 32, 64, 128 cells; shear S2 and S4 means rise with N_y | medium | 'constraints behave' (G2 C3) not shown at fine meshes | a run that changes the precision of the second differences, or the cell size at fixed time step | round-off amplified by 1/h^2 is a candidate, not tested; quote the values |
| R21 Core runaway in the population box (new, batch 11): the GR run at sigma1 = 0.028 stopped at a = 30.7 (stage 15) in the core of the box's largest halo, K running away (0.003 to 0.26 in one unit of t) and the lapse falling, run B-20261123-035002-bcc82bd; the 0.014 run passes the same stage with K < 0 everywhere. Same mode as R6 (cosmo/TESTLOG.md 1844-1852) | measured | caps the amplitude scan at 0.014 until a remedy; the top amplitude 0.056 of DESIGN.md section 8 is out of reach | restarts X0-X3 (B-20261124-133533-cb0bb7d): same, half step, Gamma-driver shift, f = 1 slicing | name a cause only from X0-X3; if a slicing (X3) passes, ask core for a slicing for halo cores in the periodic box; else 256^3 and refinement (cosmo_amr) |
| R22 High-k TT energy of the GR box after halo formation (new, batch 11): the gauge-corrected metric's Omega_qs reaches 3.2e-4 at a = 132 against 5.7e-7 for the particles' near field, while |k| <= 8 k_f agrees within 1.4; G_tot is as large as the raw strain | measured | a radiated-signal claim from the GR box | the mesh (256^3) and particle (8 per cell) legs queued by the sequencer; spectra in results/analysis_gr.json | quote only |k| <= 8 k_f until the legs show what the excess is |

## Decision requested from the group

None requested: progress record of batch 10a. G2 is not met; stage/G2/OPEN.md lists what it lacks (population GR against Newtonian mode, shear L2, gauge leg, package products).
