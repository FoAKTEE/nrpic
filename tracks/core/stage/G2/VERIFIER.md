# Verifier report: core, gate G2 (fresh context)

Verifier: helper `verify/verifier_g2` of owner core, batch 6, 2026-11-21 (21:14Z to
22:00Z), model Opus. I did not produce any of the results checked here. Before my
verdicts were committed (commits 2a4336b5, 805da131, 7fff69fc, 5e40e8b9: the outcome
entries of `tracks/core/verify/verifier_g2/JOURNAL.md`) I read only the claims (`EVIDENCE.md`,
`CHECKLIST.md`, the first section of `OPEN.md`, `verify/LADDER.md`, the interface
documents), the paper source for its digits, the source tree for file formats, and raw
outputs; not core's STATUS, HANDOFF, REVIEW files or journal conclusions. Exceptions,
both after a first independent measure disagreed with a claim: I read the measure (not
the result) in `tracks/core/analysis/idsolve2/test_c.py` (mean over r < 1) and the
column names of `athenak/src/outputs/history.cpp`. Package: `tracks/core/verify/verifier_g2/`
(README.md, JOURNAL.md with predictions committed in 41766638 before any check, scripts,
figures). No card time was used.

**Summary.** Fourteen claims checked (rows V1 to V11 of section 2; V5, V7 and V10 in two parts). Every
number core states for the met ladder rows (geodesics, Oppenheimer-Snyder, the fates of
the five clusters, the constraints of the homogeneous universe) and the sampled
capability numbers of core-v0.3 to core-v0.6 recompute from the raw outputs to their
printed digits with my own code. Found: one general statement WRONG on the release
(restarts are exact only for the periodic set-up and the particle state, not for Z4c with
outflow faces and refinement; core's own caveat says so), and five text defects (a
mislabelled column, a number ten times too large, a wrong count, two unstated measures;
section 3). Nothing found changes a verdict of the checklist: C1 stays FAIL for rows 3
and 4, which I did not re-judge; C3 stands with its label corrected; C16 is met by this
report for a sample, not for "every number".

## 1. What was checked and how

A sample of the claims core marks as met, covering every met row of the verification
ladder (brief section 10, rows marked CORE: row 1 geodesics, row 2 Oppenheimer-Snyder,
the met part of row 4 "fates of the five models as the paper"; checklist C3 constraints and
C4 first full-GR kinetic run) and at least one claim of each release core-v0.3 to
core-v0.6: deposition identities, exact restart, the Newtonian mode (multigrid and Fourier
solver), the box tests of the collision operator, the scalar-field ladder, the
initial-data solver (first and second pass), the boundary tests of Z4c, and the MPI
particle module. For each claim I wrote my own reader of the raw output (formats from
`docs/FORMATS.md` and the writers in `athenak/src`), checked the reader on an analytic
case, and recomputed the stated number against a reference I derived or integrated
myself (Kerr-Schild metrics and Carter constant, a DOP853 geodesic, the Kerr radial
potential, Einstein-de Sitter in the conformal-time lapse, -M r/r^3, Maxwell-Juttner,
the Klein-Gordon stencil symbols, the continuum psi of a Gaussian, the Zel'dovich slab
moment, the ghost-extrapolation stencil error). No reader of `python/nrpic` or of core's
analysis code was imported. Every analysis and simulation is a registered run
(`harness/bin/nrpic-run`, run ids below) with one figure each, looked at.

## 2. Verdict per claim

CONFIRMED: the stated number recomputed to its printed digits (or inside a stated
bound). NOT CONFIRMED: recomputed differently, or not reproducible as stated. WRONG: the
statement is contradicted by the data.

| # | Claim (where stated) | Raw output (executable) | My run | Recomputed | Verdict |
|---|---|---|---|---|---|
| V1 | Row 1: Kerr a = 0.9, e = 0.99 passage, dt = 0.01 to 230 M, largest relative errors (E, L_z, Q): midpoint analytic 2.781e-8, 0, 1.254e-7; Boris symmetric 9.046e-8, 1.136e-8, 7.825e-7; midpoint Hermite lattice 2.162e-6, 5.304e-6, 5.060e-5; Boris Cholesky lattice 2.046e-6, 3.788e-6, 5.289e-5; paper main.tex 825-833; second order; pericentre 1.898327 M at 98.948 M (LADDER.md row 1) | core-20261115-065452-3629622 (merged wave-1 processor build) | core-20261121-212008-6986d13 | all twelve numbers to four digits; each rounds to the paper's two digits; E, L_z, Q at t = 0 = 0.99738, 2.4328, 1.974 (main.tex 811); orders 2.0003/2.0001, 1.9991/1.9998, 1.9989/1.9997 against my own reference; pericentre root 1.898327 M, 98.948 M | CONFIRMED |
| V2 | Row 2: regression O first horizon 16.3894 M, M_AH 1.000353, largest abs(M_AH/M - 1) to 25 M 6.3e-4, deposition identity 1.0e-15; nocap_sc: 1.34e-3 over 16-60 M, 1.000093 (20 M), 0.998762 (40 M), 0.998670 (60 M), all 9328 particles removed by 19.74 M; "of the order of the paper's <~ 1e-3" (main.tex 945) | core-20261115-065901-3629622 (card, merged); `runs/os/nocap_sc` (pre-program, unregistered) | core-20261121-212106-131e909 | 16.3894 M, 1.000353, 6.345e-4, 9.6e-16; 1.338e-3, 1.000093, 0.998762, 0.9986707, 19.739 M | CONFIRMED (60 M value is 0.998671 by rounding; the error exceeds 1e-3 from 31 M on, see section 4) |
| V3 | Row 4, met part: 0.900 and 0.819 stay (central lapse 0.886-0.892, 0.787-0.819, all particles kept); 0.605 and 0.500 collapse (first horizon 191.0 M, 104.3 M; M_AH/M 1.0000, 1.0001); 0.283 expands (central lapse 0.976 at 270 M); paper 109 M, 73 M (main.tex 1138); wave-2 y_c = 0.72 mean central lapse 200-300 M 0.7079 | `runs/st/yc*_v4/v5` (pre-program, unregistered); core-20261115-152843-5728b1d (card, release core-v0.3) | core-20261121-212244-3f782d9 | 0.8862-0.8919; 0.7875-0.8190; 191.0 M, 0.99999; 104.31 M, 1.00005; 0.97598 at 270 M; 10000 kept where stated; 0.70789 | CONFIRMED (fates; collapse times 1.75 and 1.43 times the paper's, as LADDER says) |
| V4 | C3: homogeneous universe H-norm2 3.7e-10, abs(Theta) 1.1e-11 (CHECKLIST C3) | core-20261115-065903-3629622 (card, merged) | core-20261121-212248-a7972d1 | H-norm2 3.696e-10; the 1.106e-11 is the column `Theta-norm2` = sum vol Theta^2 (history.cpp 186, 229), pointwise max abs(Theta) 2.27e-7, max abs(H) 1.69e-6; against my Einstein-de Sitter: lapse 1.9e-7, mean K 3.8e-7, proper volume 1.1e-6 relative to a = 4 | numbers CONFIRMED; label "abs(Theta)" WRONG |
| V5a | Deposition identity in the dust collapse 1.0e-15 (LADDER supporting checks) | as V2 | core-20261121-212106-131e909 | 9.6e-16 (regression), 1.04e-15 (nocap_sc) | CONFIRMED |
| V5b | core-v0.5 MPI, periodic cosmology T6 on 1, 2, 4 ranks: positions 1.6e-14, sources at particles 1.3e-14, identity 1e-14 (`interfaces/mpi.md` row 6) | core-20261119-163641-ddb47b0 | core-20261121-213807-4cc035d | identity 9.8e-15, 7.4e-15, 3.1e-15; positions 5.3e-15, 4.0e-15; E, S_i at particles 1.21e-14, 1.26e-14 of column maxima | CONFIRMED |
| V6 | Exact restart (CLAUDE.md "restarts are exact"; LADDER supporting checks: periodic every quantity identical, asymptotically flat positions to 9e-16; `interfaces/mpi.md` row 4: with Z4c and outflow faces not exact on one rank, release too) | fresh runs, release core-v0.6 processor executable: east (periodic, Z4c, 4096 particles, restart at cycle 10 of 20), os (Oppenheimer-Snyder, Z4c, static refinement, outflow faces, restart at cycle 3 of 6) | core-20261121-213713-952a0c4 (runs), core-20261121-215228-d1f36f4 (aligned comparison) | east: restart data, trajectories (470 records), histories and snapshot after the restart identical. os: particle state identical, histories within 5e-13; the mesh state in the restart file at cycle 6 differs in 64 per cent of its float64 words (median relative 2.8e-13, 99th percentile 1.7e-7) | periodic and particle state CONFIRMED; "restarts are exact" as a general statement WRONG for Z4c with outflow faces and refinement (core's own caveat CONFIRMED) |
| V7a | core-v0.3 Newtonian point mass: rms relative force error of tracers at r >= 0.5: 1.609e-2 (N = 32), 4.94e-3 (64), order 1.70; "846 tracers" (`interfaces/newtonian_mode.md` 5.2) | core-20261115-150209-3629622 (merged) | core-20261121-212516-0f0a65b | 1.6092e-2, 4.9399e-3, 1.704; 706 tracers at r >= 0.5 (same particle file as the original run) | CONFIRMED; tracer count NOT CONFIRMED |
| V7b | core-v0.6 Fourier solver, exact pancake T3: slab I_xx error 9.1e-6 (spectral), 3.1e-3 (seven_point) relative to max abs(I_xx - c0), 1.2 <= a <= 7.56 (`newtonian_mode.md` 7.8) | core-20261119-160919-c6a7279 (branch newton-2, merged into v0.6) | core-20261121-213946-cee79fa | 9.107e-6, 3.094e-3 with my own lattice and exact moment; positions at a = 4 within 4.5e-4 (spectral) of the displacement amplitude | CONFIRMED |
| V8 | core-v0.3 collisions, box relaxation: end states Maxwell-Juttner at theta_eq of the conserved energy, KS p 0.26-0.90, pressure within 0.06 sigma, energy sums equal to the last bit (one run of four one unit) (`interfaces/collisions.md` section 8) | core-20261115-134036-5684674 (branch core-coll build) | core-20261121-212611-5973536 | theta_eq to 1e-15; KS p 0.897, 0.744, 0.447, 0.261; abs(z) <= 0.056; energy equal in 3 runs, -2.0e-16 in one; momentum change < 4e-19 of E | CONFIRMED |
| V9 | core-v0.3 scalar field test 1a: spatial orders 1.991, 3.957, 5.918 (EVIDENCE); omega/omega_h - 1 = -1.2e-8 ... -1.34e-8 at dt = 1/512 (`interfaces/scalar_field.md` test 1) | core-20261115-150004-3629622 (merged) | core-20261121-212422-b616c6e | orders 1.9913, 3.9566, 5.9181; my stencil symbols give the code's omega_h to 1e-12; omega/omega_h - 1 = -1.21e-9 ... -1.31e-9 (two-wave fit), equal to the RK4 phase error (omega dt)^4/120 = 1.31e-9 | orders CONFIRMED; frequency number WRONG (ten times too large) |
| V10a | core-v0.4 initial-data solver T1, Gaussian: centre error of psi - 1: -9.10e-3, -2.43e-3, -6.17e-4 (stencil), -1.92e-2, -5.22e-3, -1.33e-3 (code), dx = 1, 0.5, 0.25, second order; monitor after the solve 1.5e-11 to 2.6e-11 (`interfaces/id_solver.md` T1) | core-20261115-155048/-155050/-155053/-160207/-155051/-155054-87e189e (branch idsolve) | core-20261121-214108-0960a46 | as relative errors of psi - 1 against my continuum psi: all six to three digits; orders 1.91/1.98, 1.88/1.97; monitor 1.55e-11, 1.09e-11, 2.59e-11 | CONFIRMED (the numbers are relative errors; the text says "error") |
| V10b | core-v0.6 solver on static refinement (test C): monitor at t = 0 2.4e-12 to 2.0e-11 on every level; central error equal to the uniform run of the finest cell size, -5.01e-3 against -5.03e-3 (`interfaces/id_solver2.md` C) | core-20261119-153510-d1eaa30 (branch idsolve2, merged into v0.6) | core-20261121-214230-ad24f6b | 2.44e-12 and 2.02e-11 (g_smr1); -5.0136e-3 against -5.0331e-3 (mean over r < 1; eight centre cells: -5.20e-3 against -5.22e-3) | CONFIRMED |
| V11 | core-v0.6 faces, H1: stock boundary-cell abs(H) after one step 1.9e-3 = 0.79 of the stencil estimate 8 x 1.117 m/r^3; orders 3, 4: 0.18, 0.048 of it (stencil 0.175, 0.041); fall-off ghosts lower the layer about 12 times (`interfaces/z4c_faces.md` H1, tests a0, a0b, c0) | core-20261119-143938-eded041 (branch faces); fresh runs on release core-v0.6 | core-20261121-214547-7a21ed3 | coefficient 201/180 = 1.1167 derived (sixth-order stencil reading linearly extrapolated ghosts; also 0.117, -0.011 in the next cells); estimate 2.399e-3; measured 1.8953e-3 = 0.790; orders 3, 4: 0.184, 0.048 (my estimates 0.175, 0.041); the release gives the branch value to all digits; `ghost_falloff = true` on the release: 12.4 times lower (order 2), 11.5 (order 4) | CONFIRMED |

## 3. Defects found in the texts (for core to correct)

1. `CHECKLIST.md` C3: "|Theta| 1.1e-11" is the history column `Theta-norm2`, a volume
   integral of Theta^2 (the header of the file truncates it to `Theta-norm`); pointwise
   max |Theta| is 2.27e-7 (run core-20261121-212248-a7972d1).
2. `interfaces/scalar_field.md` test 1: the frequency agrees with omega_h to -1.21e-9 ...
   -1.31e-9, not -1.2e-8 ... -1.34e-8 (run core-20261121-212422-b616c6e; the run's own
   summary.json also gives -1.21e-9).
3. `interfaces/newtonian_mode.md` 5.2: 706 tracers lie at r >= 0.5, not 846
   (run core-20261121-212516-0f0a65b); the rms values are right.
4. `interfaces/id_solver.md` T1: "error of psi - 1" means the relative error of psi - 1
   (run core-20261121-214108-0960a46); the monitor range is 1.1e-11 to 2.6e-11.
5. `LADDER.md` row 2 quotes 0.998670 at 60 M; the value is 0.9986707.

## 4. What could not be checked

- Row 3 (prolate, PARTIAL) and the PARTIAL parts of row 4 (bisection, migration) were not
  sampled: not claimed as met.
- Ladder rows 2 (to 60 M) and 4 rest on pre-program run directories (`runs/os/nocap_sc`,
  `runs/st/*`) that are not registered runs and were made with executables before
  core-v0.1; I recomputed their numbers from their files, but their provenance (command,
  executable, checksums) is outside the manifests.
- Not sampled: the byte regressions of the releases themselves (75/75), the card checks
  of core-v0.5 and core-v0.6 (jobs 4772, 4800, e.g. the Bowen-York puncture max|H|
  6.4e-12), collisions-2 (`coll_energy`, core-v0.4), scalar_field_2/3 (stochastic slice,
  USR), cosmo_amr, the threaded build, rng, multi-puncture and format-2 residual orders
  (sixth order), the far field W1 and puncture tests of the second solver pass, moving
  clumps, the other MPI rows, Track B's pancake-east table T2 (needs Track B's
  unequal-mass construction; T3 checked instead).
- C16's wording "every number of the Supplemental Material recomputed" is not met by a
  sample; core has no working note (C15), so there is no Supplemental Material to recompute.

## 5. The three weakest points of the package

1. Rows 2 and 4 stand on unregistered pre-program runs. The re-verification on merged
   executables covers 25 M of the collapse (horizon mass to 6.3e-4) and none of the five
   cluster fates; to 60 M the horizon-mass error reaches 1.34e-3 and stays above the
   paper's <~ 1e-3 after 31 M, so "of the order of the paper's" holds but "below 1e-3"
   would not; the collapse times differ from the paper's by factors 1.75 and 1.43.
2. Most capability numbers were measured with branch executables before their merge
   (collisions, initial-data solver, Fourier solver, faces). Their bridge to the releases
   is the byte regression of twelve wave-1 set-ups, which does not exercise these
   capabilities, plus quick tests. Only V6 and V11 ran the release executable here (V11:
   the stock face value of the release equals the branch value to all digits). [JUDGEMENT]
3. "Restarts are exact" is the program's standing assumption for chained card runs
   (CLAUDE.md, machine section; `scripts/submit_chain.sh`), but on the release it holds
   for the periodic set-up and for the particle state, not for the Z4c mesh state of an
   asymptotically flat refined run (V6: 64 per cent of the words differ after three
   steps, at 1e-13 to 1e-7). Every chained asymptotically flat run (row 4 on M/8, Track C
   and D chains) is therefore reproducible only up to round-off growth, which core knows
   (mpi.md row 4) but the package does not carry as a limit of C6 or C3. In addition,
   five texts carry numbers whose measure is unstated or mislabelled (section 3), so a
   reader cannot recompute them without the analysis code.
