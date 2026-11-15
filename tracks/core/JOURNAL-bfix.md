# JOURNAL of core, work package bfix (branch `core/requests-b`)

Append-only. Predictions are written before a test runs, outcomes after, also when the
prediction failed. Runs are registered with `harness/bin/nrpic-run` under
`tracks/core/runs/<run_id>/manifest.json` (outputs under `scratch/core/<run_id>/`).
Labels: [VERIFIED] read or measured in this session (with locator), [BACKGROUND],
[JUDGEMENT], [TO VERIFY].

## 2026-11-15 session bfix-1 (wave 2): requests of Track B

Start: `git merge --no-edit main` (already up to date, 4ebb05f). Read: CLAUDE.md, charter
to "Owners", rulings after wave 1, decisions 0010 to 0015, core HANDOFF/STATUS/G2 OPEN,
the eight `__to-core__` messages of B-emd-gw at 767eb93, its `stage/G0/REVIEW.md`,
`stage/G0/OPEN.md`, `stage/G1/STATUS.md`, `periodic_z4c/README.md`, `gw_diag/README.md`.
A snapshot of the track's packages at 767eb93 is exported to
`scratch/core/tmp/bfix/B/` (read-only use: its readers, reference solutions and
diagnostics are run on core's outputs; nothing of it is copied into this branch).
Triage: `tracks/core/interfaces/REQUESTS_B.md`.

Baseline executable: `.work/athena_cpu_base`, built in this worktree from 4ebb05f with
`scripts/build_cpu.sh .work/build_cpu` before any source change (the source under
`athenak/` at 4ebb05f equals that of tag core-v0.3: `git diff --stat core-v0.3 HEAD --
athenak/` is empty) [VERIFIED].

### Source reading before any change [VERIFIED at 4ebb05f]

1. `athenak/src/pgen/tests/z4c_linear_wave.cpp` lines 91-92 and 107-112. The angles are
   theta = atan2(sqrt(kx1^2 + kx2^2), kx3), phi = atan2(kx1, kx2), so the unit wave vector
   is khat = (sin th sin ph, sin th cos ph, cos th) (phi counted from the x2 axis). With
   theta-hat = (cos th sin ph, cos th cos ph, -sin th) and phi-hat = (-cos ph, sin ph, 0),
   the plus tensor theta theta - phi phi has the components
   xx = cos^2 th sin^2 ph - cos^2 ph, xy = (1 + cos^2 th) sin ph cos ph,
   xz = -cos th sin th sin ph, yy = cos^2 th cos^2 ph - sin^2 ph,
   yz = -cos th sin th cos ph, zz = sin^2 th (my derivation, by hand). The file's
   axx, axz, ayy, azz equal these; its axy = -(1/4)(3 + cos 2th) sin 2ph
   = -(1 + cos^2 th) sin ph cos ph and its ayz = +cos th sin th cos ph have the opposite
   sign. With the file's signs, contracting with khat gives
   (e.khat)_x = -2 (1 + cos^2 th) sin th sin ph cos^2 ph,
   (e.khat)_y = 2 sin th cos ph [cos^2 th - (1 + cos^2 th) sin^2 ph],
   (e.khat)_z = 2 sin^2 th cos th cos^2 ph;
   all three vanish only if cos ph = 0 (k2 = 0: k anywhere in the x1-x3 plane) or k is
   along x2 or x3. So the upstream tensor is transverse for k in the x1-x3 plane and along
   the axes, and for no other direction; "only for k along an axis" (Track B's wording) is
   slightly too narrow. Track B's finding of the two wrong signs is confirmed by an
   independent derivation; the fix is the two sign flips.
2. Weyl timing (`z4c_tasks.cpp` 410-440, 520-534; `driver.cpp` 573-607;
   `z4c_wave_extr.cpp` 201-202). `InitRecvWeyl` (list "before_stagen", last stage) sets
   `last_output_time = float(time)` in the step that starts at `time >= last + waveform_dt`
   (or at time 0); `CalcWeylScalar` and `CalcWaveForm` (list "after_stagen", last stage)
   then run on the state after the update, i.e. of `time + dt`, while `pmesh->time` is
   still `time` (the driver adds dt after the task lists). `WaveExtr` writes
   `pmbp->pmesh->time` as the time of the row. So (a) the extracted waveforms carry a
   label one step too early: the row labelled t holds Psi_4 of t + dt; (b) a `weyl` mesh
   output written at t_n holds the scalar of the last step that started at a waveform
   time, t_(n-1) + dt for equal cadences: Track B's measured t_n - 7 dt with
   waveform_dt = 8 dt. Both statements of the request are confirmed by the source.
3. Mesh binary output (`outputs/binary.cpp` 96, 140-148, 218-232) converts every value
   with `static_cast<float>`; the header line "size of variable" exists, and upstream's
   reader `athenak/vis/python/bin_convert.py` (lines 138-155) accepts 4 or 8.
4. `nrpic_cosmo.cpp` reads n1 x n2 x n3 fields (lines 95-124): nothing cubic in the
   generator. `mesh.cpp` 231-233 asks for at least 4 cells per active direction. The
   initial-data tools `cosmo/ic/cosmo_id.py`, `make_east.py` are cubic only
   (`Torus(n, L)`, `cic_deposit(..., n, L)`), and `cosmo/` is outside core's OWNERSHIP.

### P1 Linear-wave generator: predictions (written before the change is built)

Change: flip the signs of `axy`, `ayz`; add the cross tensor (`<problem> amp_cross`,
`phase_cross`, read only if present); the reference of the error routine is evaluated at
the final time instead of at t = 0.

- P1a (algebra, python): for 400 random directions the corrected tensor has trace 0,
  |e.k|/|k| < 1e-14, e:e = 2, and equals theta theta - phi phi; the cross tensor has
  trace 0, |e.k|/|k| < 1e-14, e:e = 2, e+:ex = 0; the upstream signs give
  |e.k|/|k| = 0.77 for k = (1,1,1) (Track B's number). Refuted by any other value.
- P1b (initial data read back from the code, double precision): the tensor fitted from
  the restart dump at t = 0 of k = (1,1,1), (1,2,0), (2,-1,3), (1,0,0) equals the python
  tensor to 1e-9 relative (amp 1e-6 on top of 1: about 1e-10 of rounding) for the new
  executable, and differs in xy and yz by a sign for the baseline.
- P1c (Track B's case lw3d_check, 16^3, A = 1e-6, production numerics): baseline
  executable, k = (1,1,1): integral of H^2 = 1.385e-9 and of M^2 = 1.558e-9 at the first
  history row with ADM data (Track B's numbers, run B-emd-gw-20261115-113216-0ea0f74).
  New executable: both below 1e-20 (the track's criterion). Estimate of what remains:
  the second-order terms, proportional to |k|^4 A^4 for H^2 and |k|^6 A^4 for M^2, i.e.
  about 9 and 27 times the axis values 4e-22 and 1e-22 that the track measured:
  3.6e-21 and 2.7e-21 within a factor three. Refuted if either is above 1e-20, or if at
  A = 1e-7 they fall by 1e2 (first order left) instead of 1e4. For k = (1,0,0) the new
  executable gives the track's 4e-22 and 1e-22 again (within 10 per cent: the off-diagonal
  components change by rounding only).
- P1d (general oblique direction, k = (1,2,0), where the wave numbers per axis differ):
  the discrete divergence of the tensor does not vanish exactly, because the sixth-order
  first derivative has a different relative error for k_x h and k_y h; the momentum
  constraint of the initial data is of first order in A times the truncation error and
  converges as h^6 (its squared integral as h^12): a factor 4096 from 16^3 to 32^3 within
  a factor two. The same for H with the second derivative. Refuted if the constraints do
  not fall with the resolution.
- P1e (evolution of the oblique wave k = (1,1,1), one period, 16^3 and 32^3, production
  numerics; 64^3 on a card if the queue allows): amplitude and phase errors of the
  Fourier coefficient of each tensor component at the final time against the exact
  solution agree to 10 per cent with the Fourier-symbol prediction of the scheme
  (Track B's `predict_lw.py` extended to three directions: second-derivative symbol
  summed over the axes, Kreiss-Oliger rate summed over the axes, RK4 with
  dt = cfl h); the components keep the ratios of the tensor (the wave stays a plus wave:
  h_x/h_+ below 1e-6 through gwdiag's TT projection), and gwdiag's fixed-direction Psi_4
  equals the analytic second time derivative to the level Track B found along x
  (relative 1e-3 at 32 cells or better, set by the sixth-order stencils). Refuted if the
  errors exceed the prediction by more than a factor two or do not fall with N.
- P1f (cross and circular polarization, k = (1,1,1), 16^3, t = 0 and one period): with
  amp = 0, amp_cross = 1e-6 gwdiag returns h_+ = 0 (below 1e-6 A) and h_x of amplitude A;
  with amp = amp_cross, phase_cross = pi/2 the helicity split of gwdiag puts the energy
  into one helicity (other below 1e-6); constraints as in P1c.
- P1g (Track B's own analytic tests rerun with the new executable): `lw_x_prod` N = 16, 32
  give the amplitude and phase errors of the track's table (-1.72e-4, -2.49e-4;
  -1.49e-6, -6.25e-6) to the printed digits; `validate_athenak.py` of gw_diag on a rerun
  of lw3d_dump_N32 (k = (1,0,0)) gives amplitude within 3e-7, phase within 1.2e-6 rad,
  rho within 6e-7 as in the track's README. Refuted by any change beyond rounding
  (the fix changes the axis-aligned data only in off-diagonal components of size
  1e-16 A).
- P1h (error routine): for integer periods the errors file of the new executable equals
  that of the baseline to the printed digits for k = (1,0,0); for tlim = 0.5 periods the
  baseline reports an L1 error of order A (it compares with the initial data, which is
  the negative of the solution) and the new one an error of the size of the truncation
  error.

Registration: `harness/bin/nrpic-run submit` (and `budget`) stop with
`KeyError: 'outputs'` in `budget_state` -> `is_live` (harness/bin/nrpic-run line 163):
the hand-written manifests of wave 1 under `tracks/core/runs/` have no `outputs` key
[VERIFIED: traceback on 9c92f68]. Runs of this package are therefore registered by hand
with core's helper of wave 1, `tracks/core/tools/run_registered.py` (fields of
CLAUDE.md rule 4); the failure goes into the requests to the orchestrator.

A trial of the test driver on its quick stages (algebra, pol, errs; output
`scratch/core/tmp/bfix/dbg1`, unregistered, to debug the script) ran before the
registered run. It showed two things the predictions above did not say, recorded here
before the registered run: the Euclidean norm of e.khat of the upstream tensor at
k = (1,1,1) is 0.943 and its largest component 0.770 (so P1a's "0.77" is the largest
component, not the norm); and the circular wave has four times the constraint norm of
the linear one. Both are judged in the outcome below.

### P2 Output for the gravitational-wave analysis: predictions (before the runs)

- P2a (double-precision dump): in a linear-wave run with a restart file, a `bin` output
  of `z4c` with `double_precision = true` and one without, at the same times: the 22
  fields of the double dump equal the active cells of the restart file bit for bit; the
  single dump equals the double one rounded to float32 bit for bit; the file size is the
  header plus, per MeshBlock, 40 + 48 + 22 * 8 * cells bytes. Refuted by one differing
  value.
- P2b (nothing else changes): with the new executable and without the new parameters,
  every output file of existing set-ups equals that of the baseline executable byte for
  byte, restart files outside the 36 padding bytes (cases of
  `tracks/core/tools/regress_relativistic.py`: geo, boris, dep, east, os, jeans, binary,
  on processors). Refuted by any differing byte elsewhere.
- P2c (Weyl time): Track B's fit of the time of the `weyl` mesh output
  (`validate_athenak.py`, stage trackb of T1) gives -7 steps with the default, as the
  track measured, and 0 steps (within 0.05) with `waveform_at_new_time = true`, with the
  residual of the fit at the level the track found at -7 (3e-7 to 2e-6). The waveform
  files `waveforms/*.txt` of the two runs hold the same numbers row by row with labels
  that differ: default labels t_n hold Psi_4 of t_n + dt. Refuted if the best offset
  with the option is not 0.
- P2d (restart padding): two runs of one input with the new executable give identical
  restart files; the bytes 36 before the time field are zero; the baseline's file
  differs from the new one only inside those 36 bytes; a baseline restart file read by
  the new executable continues to the same state as read by the baseline executable
  (all 22 fields bit for bit at the end).
- P2e (sources in double precision): in a run with depositing particles, the `tmunu`
  double dump is finite, its energy density is positive where particles are, the float32
  dump of the same output time equals it rounded, and the Hamiltonian constraint
  recomputed in python from the double `z4c` and `tmunu` dumps of one time agrees with
  the code's `con_H` (float32 dump) to the float32 rounding of the latter relative to
  its largest term. This is the check that the dumps of one output time belong to one
  time level. Refuted if the recomputed constraint differs by more than 1e-5 of the
  largest term of H.

### P3 Thin periodic boxes: predictions (before the runs)

Tool: `problems/cosmo/make_waves.py` with `python/nrpic/torus_id.py` (the constraint
solve of `cosmo/ic/cosmo_id.py` for a box of n1 x n2 x n3 cubic cells; `cosmo/ic` itself
is cubic only and outside core's ownership).

- P3a (the tool against the existing one): for the cube, same arguments,
  `particles.nrp` and `fields.bin` of the new tool equal those of
  `cosmo/ic/make_east.py` to 1e-12 relative (the operations are the same; only the order
  of a few sums differs). Refuted by a larger difference.
- P3b (thin data): for waves (1, eps, 0) the thin-box fields equal every z-layer of the
  cube's fields to 1e-12, and the thin-box particles are the cube's particles of the
  first n3 layers (positions, momenta to 1e-12; masses equal).
- P3c (evolution, the answer to the request): crossed waves (1, 0.5, 0) with
  delta = 0.1, 16 cells per wavelength, production configuration (cubic cloud with
  compensation, cubic spline gather, dt_expansion 0.01), from a = 1 through the first
  shell crossing: the runs in the cube 16^3 and in the thin boxes 16 x 16 x 8 and
  16 x 16 x 4 give the same fields on a z-layer and the same particle positions to
  1e-8 relative at the end, and the thin runs show no dependence on z above 1e-10
  relative. The discrete problem is invariant under translations in z, so only rounding
  can differ. Refuted if the differences are of the size of the truncation error (1e-4
  and above), or if a thin run fails. The same with the box thin in x and the waves
  turned to (0, 1, 0.5): equal to the z-thin run after the cyclic exchange of the axes,
  to 1e-8.
- P3d (cost): zone-cycles per second per zone do not depend on the thickness within 20
  per cent; the thin 16 x 16 x 4 run takes about a quarter of the cube's time.

### P4 Lattice jitter: predictions (before the runs)

- P4a: `--jitter 0` writes files identical byte for byte to a call without the option.
- P4b: `--jitter 0.3 --jitter-axes y,z --seed 7` (plane wave 1,0,0): x of every particle
  is unchanged bit for bit; the y and z displacements against the unjittered file lie in
  (-0.3 h, 0.3 h), with mean within 4 standard errors of zero and rms 0.3 h / sqrt(3)
  within 3 per cent; the same seed gives identical files, another seed different ones;
  the constraint residuals of the solved data are at the level of the unjittered data
  (Hamiltonian residual below 1e-9 of the largest term); `id.json` records amplitude,
  axes and seed.
- P4c: the jitter of a lattice site does not depend on the box: the thin-box jitter
  equals that of the same sites of the cube.
- P4d (the code runs it): the jittered plane wave in the thin box 16 x 16 x 4 runs to the
  end of P3c's time with every particle kept; the constraint statistics of the first
  step are within a factor three of the unjittered run's maximum (the deposit of the
  jittered lattice is noisy; the track's null test measures what that does to the
  TT part, not this package).

Amendment to P2c, written before T2 runs: the sentence "the waveform files of the two
runs hold the same numbers row by row" is wrong as a prediction. The two runs compute the
scalar in different steps (default: the step that starts at a waveform time, state of
t_n + dt; with the option: the step that ends at a waveform time, state of t_n), so the
numbers differ. What the source reading predicts instead: both files carry the labels
t_n = n waveform_dt; read against its labels, the default series leads the series of the
option by one step, a phase of omega dt = 2 pi dt/T (= 2 pi/128 = 0.0491 rad for Track
B's deck: period 1, dt = 1/128). Measured on the dominant mode of
`waveforms/rpsi4_real_*.txt` and `rpsi4_imag_*.txt` (extraction sphere of radius 0.3) by a
fit of a sinusoid of the known frequency. Refuted if the phase difference is not
0.0491 rad within 5 per cent.

### P1c supplement (written before run T1s): what is left at A = 1e-7

In T1 the constraint norms of the corrected k = (1,1,1) data fell by 3177 (H^2) and 5449
(M^2) from A = 1e-6 to 1e-7, not by 1e4 (outcome below). Two readings: (i) rounding of
1 + A e sin(P) and of its second differences, independent of A, which matters at 1e-7 and
not above (Track B's item 4 of periodic_z4c); (ii) a first-order remnant of relative size
1e-7, which would scale as A^2. Prediction for amplitudes 1e-7, 1e-6, 1e-5, 1e-4 (stage
`amp` of t1_linear_wave.py): under (i) the ratios per decade from 1e-6 upwards are 1e4
within 1 per cent; under (ii) the ratio from 1e-6 to 1e-5 would be 9.80e3 for H^2 and
9.92e3 for M^2 (the remnant would be 2.0 and 0.8 per cent of the norms at 1e-6). I expect
(i). Refuted if the ratios from 1e-6 to 1e-5 are below 9.9e3.

### Trials before the registered runs T2 and T3 (unregistered, to debug the drivers)

Outputs under `scratch/core/tmp/bfix/dbg2`, `dbg2b`, `dbg3`, `ic1`, `ic2`. No number of
the record is taken from them, but two of them changed the tests, so they are on record:

- The first version of the padding stage of T2 compared the baseline and the new
  executable on the oblique linear wave, where the two differ by design (the generator
  fix); the stage now uses the periodic cosmology case of the regression set with a
  restart output added.
- The trial of T3 showed that prediction P4d is wrong by three orders of magnitude: in
  the code the jittered lattice starts with a Hamiltonian residual of rms 9e-2 against
  3e-5 for the plain lattice, although the constraint solve of the tool had converged
  to 7e-12. Reading [JUDGEMENT at this point]: the tool solves with spectral derivatives
  (as `cosmo/ic/cosmo_id.py`), the code evaluates the constraints with sixth-order
  differences; for sources near the mesh frequency, which only a noisy lattice has, the
  two operators differ by order one. The trial also showed a momentum residual of the
  tool itself of 1.8e-2 for the jittered thin box: the spectral first derivative has no
  Nyquist mode, and in a box four cells thick a quarter of all modes lie on that plane.

Consequence: `python/nrpic/torus_id.py` gets an option `fd_order` (make_waves.py
`--fd-order 6`): the Hamiltonian residual is then the one the code evaluates (Ricci
scalar of psi^4 delta_ij from first and second differences), the vector equation uses the
first difference applied twice. Default unchanged (spectral; files identical to before:
checked by `cmp` on the plane-wave and the jittered data of the trial).

### P4e Constraint solve with the differences of the code: prediction (before T3)

Cases added to T3: `plane4_fd` and `jit4_fd` (the plane wave in the thin box, plain and
jittered, solved with `fd_order = 6`). Prediction for the first row of the Z4c history
(t = 0, constraints of the initial data as the code evaluates them after its first
deposit): the rms of H falls by at least three orders of magnitude for the jittered
lattice (below 1e-4, from about 9e-2) and by at least two for the plain one (below
3e-7, from about 3e-5); what remains is the difference between the code's and the tool's
interpolation of psi to the particles and rounding. The rms of M of the jittered lattice
falls by at least a factor ten (limited by the product-rule error of the differences and
by the eight modes that have no solution). Refuted if H of `jit4_fd` stays above 1e-3:
then the reading above (spectral against finite differences) is wrong.
P4d as written (factor three) is already refuted by the trial; the registered run records
the numbers.

### P5 The new options on a card: predictions (before the job is submitted)

Job `tracks/core/analysis/bfix/gpu_job.sh` (one A100, limit 30 minutes, at most 0.5
card-hours; the allotment of this package is one card-hour), test T4
(`t4_card.py`), new card executable against the release card executable
`/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena`.

- P5a (oblique wave on the card, k = (1,1,1), one period): N = 16 and 32 give the
  amplitude and phase errors of the processor run T1 to three significant digits; N = 64
  agrees with the Fourier-symbol prediction within 10 per cent; N = 128 within a factor
  two, or sits on the rounding floor that Track B found at 128 cells for A = 1e-6
  (periodic_z4c, item 4): then the phase error is of order 1e-8 instead of the predicted
  value. gw_diag's Psi_4 error falls with N at about fifth order to 64 cells.
- P5b (regression on the card): the test particle with the midpoint and the Boris pusher
  and the Z4c puncture benchmark (20 steps) give byte-identical output files with the
  release and the new card executable (no particle deposit: card runs are reproducible).
  Refuted by one differing file.
- P5c (thin boxes on the card): the comparisons of P3c hold on the card with the bound
  1e-8 (card runs with deposit differ from run to run at 1e-13).
- P5d (Track B's box, 256 x 256 x 16, one MeshBlock in z, one particle per cell and
  direction, waves (1, 0.3, 0), delta = 0.01, to conformal time 1): the run ends on the
  time limit with all 1 048 576 particles; the fields depend on z by less than 1e-9
  relative; throughput above 3e6 zone-cycles per second (the cosmology logs give 4.5e6 to
  5.8e6 at 128^3 and 64^3 with particles, Track B's review). Refuted by a failure of the
  run or a z dependence above 1e-6.

### Outcome of T1 (run core-20261115-154120-9c92f68, 1027 s on 8 cores; supplement T1s core-20261115-160040-26eb826, 58 s)

Executables: new `.work/exe/athena_cpu_w1` (source 9c92f68), baseline
`.work/athena_cpu_base` (source 4ebb05f); sha256 in the manifests. Results
`results_t1.json`, figures `t1_constraints.png`, `t1_evolution.png`,
`t1_polarization.png` in the output directories (looked at; copies in
`tracks/core/analysis/bfix/figs/`). All statements below [VERIFIED] by these runs unless
marked.

- P1a PASSED for the corrected tensors: over 400 random directions trace 2.2e-16,
  |e.khat| 1.9e-16, |e:e - 2| 8.9e-16, departure from theta theta - phi phi 3.3e-16;
  cross tensor: 0, 1.1e-16, 8.9e-16, e+:ex 2.8e-16, departure from
  theta phi + phi theta 2.2e-16. FAILED as written for the upstream value: I wrote
  "|e.k|/|k| = 0.77 (Track B's number)"; the Euclidean norm of e.khat at k = (1,1,1) is
  0.9428 and its largest component is 0.7698, so Track B's 0.77 is the largest
  component. The upstream tensor is exactly transverse for (1,0,1) (k2 = 0) and along
  the three axes, and has |e.khat| = 1.000 for (1,1,0) and (0,1,1), 0.800 for (1,2,0),
  0.515 for (2,-1,3); over the 400 directions between 0.014 and 1.000.
- P1b PASSED: the tensor fitted to the restart dump at t = 0 equals the corrected
  tensor to 3.5e-11 (k = (1,1,1)), 2.9e-11 ((1,2,0)), 2.6e-11 ((2,-1,3)) for the new
  executable, and the upstream tensor to the same accuracy for the baseline (distance
  from the corrected one 1.33, 0.80, 1.31). For k = (1,0,0) both executables give the
  same tensor (2.9e-11 from either).
- P1c PASSED on the track's criterion: Track B's case lw3d_check_diag (16^3, A = 1e-6),
  first history row with data (t = 0.0625): baseline 1.3852e-9 and 1.5576e-9 (Track B:
  1.385e-9, 1.558e-9; first-order prediction from the upstream tensor 1.3854e-9,
  1.5585e-9); new executable 4.587e-21 and 1.070e-21, both below 1e-20, within my
  estimate (3.6e-21 and 2.7e-21 within a factor three: ratios 1.27 and 0.40). For
  k = (1,0,0) the two executables give 3.9357e-22 and 1.1942e-22 (H^2 equal to all 17
  printed digits, M^2 to 14). FAILED as written for the amplitude scaling to A = 1e-7:
  the norms fell by 3177 and 5449, neither 1e2 nor 1e4. Supplement T1s (prediction
  written before it): from 1e-6 to 1e-5 and from 1e-5 to 1e-4 the norms rise by 1.0022e4
  and 1.0000e4 (H^2), 1.0008e4 and 1.0000e4 (M^2): reading (i) holds, what remains is of
  second order in A; reading (ii) (a first-order remnant, which would give 9.80e3 and
  9.92e3) is refuted. At A = 1e-7 a floor that does not scale with A adds to the norms
  (1.4e-24 and 2.0e-25 measured against 4.6e-25 and 1.1e-25 expected) [the floor being
  rounding of 1 + A e sin P is JUDGEMENT: it was not varied].
- P1d PASSED: k = (1,2,0), new executable, after the first step: H^2 3.468e-15,
  1.027e-18, 1.020e-20 and M^2 1.664e-15, 4.907e-19, 2.813e-21 at N = 16, 32, 64: factors
  3377 and 3391 from 16 to 32 (h^12 is 4096), then 101 and 174 from 32 to 64, where the
  second-order floor is reached (for |k|^2 = 5 the floor estimated from the axis value is
  25 x 3.9e-22 = 1.0e-20). Baseline at N = 16: 7.965e-9 and 3.112e-9. k = (2,-1,3): new
  5.54e-12 and 1.57e-12 at N = 16, 2.05e-15 and 5.87e-16 at N = 32 (factors 2706, 2672;
  k3 h = 1.18 at N = 16 is not yet asymptotic); baseline 5.38e-9 and 1.00e-8.
- P1e PASSED: oblique wave k = (1,1,1), one period (t = 0.57735), new executable.
  Amplitude error -3.522e-5 (N = 16) and -4.291e-7 (N = 32) against -3.521e-5 and
  -4.285e-7 predicted from the Fourier symbol of the scheme; phase error (numerical
  minus exact advance) -6.321e-5 and -3.037e-6 rad against -6.318e-5 and -3.034e-6:
  agreement 0.02 to 0.14 per cent. (The json of T1 stores the phase with the opposite
  sign, exact minus numerical; the driver was corrected afterwards.) The six components
  keep the ratios of the tensor to 6e-10 A. gw_diag on the final dump: max |h_x| / A
  6.0e-16 and 5.3e-10; h_+ against exact 7.2e-5 A and 3.1e-6 A; energy density over
  the analytic value 0.99993 and 0.9999991; Psi_4 along k against the analytic second
  time derivative 9.17e-5 and 3.21e-6 relative (order 4.8), Psi_4 along -k 5.3e-6 and
  1.1e-7 of the maximum. Constraints at the end 3.9e-21, 1.2e-21 (N = 16) and 3.8e-21,
  1.0e-21 (N = 32). `lwo-errs.dat` (exact solution at the final time): RMS-L1 5.33e-11
  and 5.93e-12.
- P1f PASSED for the polarization content; FAILED as written for the constraints of
  the circular wave. Pure cross wave (amp = 0, amp_cross = 1e-6): gw_diag gives
  max |h_+| = 2.8e-11 A at t = 0 and h_x equal to the exact wave to 2.5e-11 A; helicity
  split 0.5/0.5 (linear polarization). amp = amp_cross, phase_cross = +pi/2: all energy
  in gw_diag's helicity +2 (other 7.7e-21); -pi/2: all in helicity -2. After one period
  the gain and phase equal those of the plus wave (-3.522e-5, -6.321e-5 rad), Psi_4
  against d_t^2 h_+ - i d_t^2 h_x: 9.2e-5. Constraints after the first step: cross wave
  3.92e-21 and 1.25e-21; circular wave 1.399e-20 and 3.51e-21. The circular wave carries
  twice the energy, and its H^2 is 3.57 times that of one linear wave (not exactly four:
  the part of the energy density that oscillates in space cancels for a circular wave):
  second order in A as before, but above the 1e-20 I had predicted for it.
- P1g PASSED: Track B's own tests with the new executable. lw_x_prod (its analysis
  function `ana_lw.analyse_run`): N = 16 amplitude -1.7183e-4, phase -2.4935e-4; N = 32
  -1.4855e-6, -6.2476e-6 (the track's table: -1.72e-4, -2.49e-4; -1.49e-6, -6.25e-6).
  gw_diag's `validate_athenak.py`, unchanged, on a rerun of lw3d_dump_N32: amplitude
  within 3.0e-7, phase within 1.25e-6 rad, energy within 5.9e-7, h_x 7.8e-25 A, non-TT
  part 2.67e-5 A, Psi_4 along x against analytic 2.6e-7 to 1.4e-6; the weyl output lags
  by exactly 7 steps (fit residual 3.0e-7 to 1.8e-6): every number of the track's README
  (3e-7, 1.2e-6, 6e-7, 1e-24, 2.7e-5, 7 steps, 3e-7 to 1.8e-6).
- P1h PASSED with one exception: after a whole period the error files of the two
  executables agree in every printed digit except the column gyz_L1 (4.242392e-31
  against 4.241837e-31: rounding noise of a component that is zero). After half a period
  the baseline reports RMS-L1 1.812e-6 (it compares with the initial data), the new
  executable 1.368e-11.

Figures looked at: `t1_constraints.png` (left: the upstream data sit at 1.4e-9 where
Track B's two points are, the corrected data below the 1e-20 line with the axis-aligned
case a decade lower; right: (1,2,0) follows N^-12 from 16 to 32 and bends to the floor at
64; the legend covered two points at N = 16 in this first version, moved for T1s),
`t1_evolution.png` (code on top of the exact h_xx, h_xy and of Psi_4; errors on the
dashed predictions), `t1_polarization.png` (h_+ = 0 and h_x on the exact curve for the
cross wave; both for the circular wave), and the track's `athenak_psi4.png` for the two
reruns (with the option the grey points "dump at t_n" lie on the diagonal, the red ones
"t_n - 7 dt" do not; without it the reverse).

### Outcome of T2 (run core-20261115-160138-26eb826, 40 s) and of the regression (runs core-20261115-154710-9c92f68 to core-20261115-155839-9c92f68)

- P2a PASSED: five dumps (t = 0 to 0.346) of the oblique wave at 16^3: all 22 fields of
  the double-precision `bin` equal the active cells of the restart file of the same time
  bit for bit (0 differing values of 90112 per dump); the single-precision output equals
  the rounded double one (0 differing); file sizes 729 847 and 369 399 bytes = header
  8863 + 88 + 22 x 4096 x (8 or 4). The `adm` group in double precision equals the
  conversion of the Z4c dump (gamma_xx identical, K_xy to 4e-22) except at t = 0, where
  the ADM arrays of this generator are not yet filled (docs/UPSTREAM_DEFECTS.md, item 4).
- P2b PASSED: geo (2 files), boris (2), dep (1), east (12), jeans (5 and the result
  lines of the log), binary (1) identical byte for byte; os: 11 files identical, the five
  restart files differ in 36 bytes each, all inside the padding window, zero in the new
  files (`results_t2.json`, stage regress; report
  `tracks/core/analysis/bfix/results/regress_cpu_w1.json`).
- P2c PASSED (as amended): Track B's fit of the time of the `weyl` mesh output gives
  -7.0 steps at all six files with the default (residual 3.0e-7 to 1.8e-6) and 0.0 steps
  with `waveform_at_new_time = true` (residual 2.7e-7 to 2.1e-6); gw_diag's radial-triad
  Psi_4 of the dump of the same time agrees with the code's output to 4e-8 to 6e-8 with
  the option, and differs by 0.2 to 0.6 of the maximum without. Waveform files: both
  carry the labels n/16; the default series leads the series of the option by
  0.04908739 rad against omega dt = 0.04908739 (ratio 1.00000003); with the option the
  first row is at 0.0625, not 0.
- P2d PASSED (cosmology regression case with a restart output every 5 cycles, 16^3 in
  eight MeshBlocks, particles with deposit): six restart files of two runs of the new
  executable identical; against the baseline 36 differing bytes per file, all in the
  window, all zero in the new files, all 36 non-zero in the baseline's; the other 24
  output files identical between the three runs. A baseline restart file continued by
  both executables: 14 output files, differences only in the 36 bytes of the three
  restart files.

Figure looked at: `t2_output.png` (left: the float32 output of the diagonal component
scatters by a few per cent of A around the double-precision curve, the off-diagonal one
does not; right: the two waveform series against their labels, shifted by one step).

### Outcome of T3 (run core-20261115-160633-7d80187, 474 s on 8 cores; analysis runs T3b core-20261115-161610-7d39f51 and T3c core-20261115-161720-07ab27e)

Executable `.work/exe/athena_cpu_w1`; eight runs to conformal time 5.5 (a = 13.9, 265
cycles; 9.6 per cent of the lattice neighbours along x have crossed), every particle kept
in every run. Results `tracks/core/analysis/bfix/results/results_t3.json`, figure
`figs/t3_thin_jitter.png` (looked at: the two energy-density panels are alike, with two
dark cells beside the densest one, see P2e; the differences against the cube stay
between 1e-14 and 3e-10 below the 1e-8 line; flat jitter histograms; constraint
histories of the four plane-wave runs).

Registration slip, on record: T3b and T3c received `results_t3.json` of T3 as a linked
input and wrote their result file under the same name, i.e. through the link into the
output directory of T3. That file now carries the added keys `from_dir`, `jcheck` and a
`note`; its `ic`, `run`, `ana` parts are as T3 wrote them (a JSON round trip), and
`meta.commit` was set back by hand to T3's commit. The driver now writes
`results_t3_post.json` when it reads an earlier result.

- P3a PASSED: for the cube the new tool and `cosmo/ic/make_east.py` give the same
  particles (positions identical, momenta to 3.3e-16, masses to 9.1e-15 relative) and
  fields (largest difference 8.9e-16, in psi).
- P3b PASSED: the thin-box fields equal every layer of the cube's to 1.1e-15; the
  thin-box particles are the cube's of the same lattice sites (positions identical,
  momenta to 3.3e-16, masses to 7.8e-15).
- P3c PASSED on the bound 1e-8, FAILED as written on the bound 1e-10 for the dependence
  on z. Thin 16 x 16 x 8 and 16 x 16 x 4 against the cube, largest relative difference
  over 12 dumps and the fields chi, alpha, Khat, Theta, At_xx, At_xy, gt_xx, gt_xy:
  3.0e-10 and 2.7e-10, both in Theta in the first dumps (relative to its own maximum);
  2.3e-12 for At, below 6e-13 for the others; at the end 1.3e-12. Dependence on z inside
  a run: 2.4e-10 (thin8), 2.0e-10 (thin4) and 3.0e-10 in the cube itself, again Theta
  early; at the end 1e-12. The cube shows the same level, so this is the rounding of
  the scheme, not the thickness. Particles at the end against the cube's of the same
  sites: 7.4e-14 cells in x and y, 6.6e-15 in z, momenta 3.4e-14 of the largest. Box
  thin in x with the waves (0, 1, 0.5) against thin4 with the axes exchanged: 9.9e-13
  (Theta), 6e-14 for chi, alpha, Khat.
  Answer to Track B: yes; `nrpic_cosmo`, the cubic cloud with compensation, the cubic
  spline gather and the Z4c exchange work with four cells and one MeshBlock in a
  periodic direction (the minimum that `mesh.cpp` accepts), in z and in x.
- P3d PASSED: 3034, 3233 and 3145 zone-cycles per processor second for 4, 8 and 16
  layers (eight particles per cell); processor time 89 s, 168 s, 345 s: the thin4 run
  costs 0.26 of the cube.
- P2e PASSED except for the sign of E at the end. The `tmunu` dump in double precision
  is finite; the single-precision dump equals it rounded (0 differing values); the
  Hamiltonian constraint recomputed in python (gw_diag's sixth-order Ricci scalar) from
  the double `z4c` and `tmunu` dumps of one output time equals the code's `con_H` to
  6.5e-12, 6.8e-11 and 6.1e-10 of the largest source term 16 pi E at t = 0.51, 3.02, 5.5
  (cube and thin4 alike), where the constraint itself is 2e-4, 2.4e-3, 3.1e-2 of that
  term. With E replaced by E sqrt(gamma) the mismatch is 0.8 to 1.0: the dump holds E
  itself although the run uses `source_density = true`. So the `z4c`, `tmunu` and `con`
  dumps of one output time belong to one time level. E is positive at the first two
  times (minimum 1.9e-2, 1.6e-4) and has a minimum of -5.2e-6 at the end (maximum
  6.9e-4), in the two cells beside the densest one: the compensation of the cubic cloud
  without its limiter undershoots next to the caustic (`deposit_comp_limit` exists for
  this, cosmo/README.md). My prediction "positive where particles are" did not allow for
  that.
- P4a PASSED: `jitter = 0` gives files identical to a call without the option.
- P4b PASSED: 8192 particles; x unchanged in every particle; y displacement in
  (-0.29976, 0.29978) h, mean 0.0029 h (1.5 standard errors), rms 0.17321 h; z in
  (-0.29995, 0.29997) h, mean 0.0020 h (1.0 standard error), rms 0.17372 h (expected
  0.17321); correlation of the two 0.001; same seed: identical files; seed 8: different;
  `id.json` holds jitter 0.3, axes y z, seed 7, sub-stream 16. Hamiltonian residual of
  the tool 6.8e-12 of the largest term (plain lattice 2.4e-12).
- P4c PASSED (T3b, T3c): the particles of the jittered thin box and of the jittered cube
  at the same sites differ by 0 modulo the thin box, and jittered minus plain positions
  equal the deviates of `nrpic.rng` to 4.4e-16. (Stage ic of T3 compared without the
  periodic wrap and reported 3.0, the difference of the box lengths: an error of the
  driver, corrected.)
- P4d FAILED: the jittered plane wave runs to the end with every particle, but its
  Hamiltonian residual at t = 0 is 8.73e-2 rms against 2.91e-5 for the plain lattice
  (largest source term 16 pi E = 7.2): a factor 3000, not three. At the end 2.08e-4
  against 5.43e-5; chi then depends on y and z by 7.3e-3 relative (plain: 7.8e-15).
- P4e PASSED for H, FAILED narrowly for M. With the constraints solved with the code's
  differences (`--fd-order 6`) the residual of the code at t = 0 is 1.89e-6 for the
  jittered lattice (factor 4.6e4 down) and 3.08e-8 for the plain one (factor 944 down):
  the reading "spectral derivatives against the code's differences" is confirmed by a
  run in which it could have failed. The rms of M falls from 5.48e-3 to 7.27e-4, a
  factor 7.5 (predicted: at least ten); the tool's own momentum residual there is 1.0e-3
  from the eight modes without solution (5.2e-4 in amplitude) [that these dominate what
  is left is JUDGEMENT: the product-rule error was not separated].
- Not predicted, and the main thing Track B should know: the gain does not survive ten
  steps. At t = 0.10 the jittered run that started at 1.89e-6 has H rms 6.92e-2 (the
  spectral start: 7.38e-2), from t = 0.5 the two agree to two digits (2.03e-2, 2.06e-2),
  at the end to three (2.075e-4, 2.077e-4). The same for the plain lattice: 3.1e-8 at
  t = 0, 1.65e-4 at t = 0.10 (spectral start 1.73e-4). So the constraint level of these
  runs is set by the evolution within ten steps, not by the initial data; for a noisy
  lattice it is about one per cent of the source term at the start and falls with the
  expansion. Cause not identified [TO VERIFY]; candidates [JUDGEMENT]: the first step has
  no earlier deposit to extrapolate the sources from; the deposit does not obey a
  discrete continuity equation with the code's differences, so the part of the sources
  near the mesh frequency drives Khat and with it the term K^2 of the constraint before
  the metric follows. `--fd-order` therefore cleans the initial slice only.

### Publication (2026-11-15T16:21Z)

`/data/haiyangw/nrpic/scratch/core/exe/core_requests-b/`: `athena_cpu`
(sha256 c32a1389...ceeced, the executable of T1 to T3), `athena_gpu` (sha256
5a35c8f1...11b9aa, built from the same source, not yet run on a card), `COMMIT`
(9c92f68: `athenak/` has not changed since; last source edit 15:32:15 UTC, processor
build 15:33:20, card build 15:37:23), `READY` (options with one example each, what is
tested, and the open card test in its STATUS block). Copies of the two text files:
`tracks/core/notes/READY_core_requests-b.txt`, `COMMIT_core_requests-b.txt`.
[JUDGEMENT] READY is written although the card test has not run: the processor
executable is what Track B needs first (thin N x 4 x 4 waves, 16^3 and 32^3 oblique
checks, initial data), the only device code changed is the generator's kernel, and the
file says in its first block that the card executable is untested. If the orchestrator
prefers, rename READY until T4 has passed.

### State at the end of the session work (card test pending)

Card job 4452 (`tracks/core/analysis/bfix/gpu_job.sh`, test T4, limit 30 minutes, at most
0.5 card-hours) was submitted at 16:07Z and is still pending behind eleven jobs of other
sessions (two cards). Card time used by this package so far: none. When it runs it
registers itself (`tracks/core/tools/run_registered.py`, tag T4; the manifest appears
under `tracks/core/runs/` in this worktree, uncommitted) and writes `results_t4.json`
with the figures into its output directory; predictions P5a to P5d above. To finish:
read `scratch/core/tmp/bfix/slurm-4452.out`, enter the outcome here, append a section
"CARD TEST" to the READY file, commit the manifest.

Not done in this package:
- T4 (above): nothing of this branch has run on a card.
- The oblique convergence at 64^3 and above (Track B's G1 item) is part of T4 only.
- No second agent has checked these results (CLAUDE.md, models and roles): the analysis
  uses Track B's own readers, reference solutions and diagnostics as the independent
  implementation, but the runs and the judgement are this session's.
- The cause of the constraint level that the evolution restores within ten steps
  (outcome of T3) is not identified.
- Requests deferred or declined: REQUESTS_B.md sections 2 (Fourier modes), 6, 7, 8.
- `tracks/core/STATUS.md`, `HANDOFF.md`, `CHANGELOG.md` and `stage/G2/` are the core
  lead's and were not touched (another core branch is open at the same time); this
  journal and `interfaces/REQUESTS_B.md` are the record of the package. OPEN item 15 of
  the G2 package (restart padding) is closed by this branch.

How to rerun (each prints its run id; `W` = this worktree, executables as published):
```
python3 tracks/core/tools/run_registered.py --purpose "..." --cores 8 --tag T1 -- \
  $W/.venv/bin/python $W/tracks/core/analysis/bfix/t1_linear_wave.py \
  --exe-new EXE_NEW --exe-base EXE_BASE --out . [--stages algebra,id,amp,evol,pol,errs,trackb]
... t2_output.py --exe-new EXE_NEW --exe-base EXE_BASE --t1-dir <T1 output> \
  --regress-report tracks/core/analysis/bfix/results/regress_cpu_w1.json --out .
... t3_thin_jitter.py --exe EXE_NEW --out .
python3 tracks/core/tools/regress_relativistic.py --exe-a EXE_BASE --exe-b EXE_NEW \
  --cases geo,boris,dep,east,os,jeans,binary --out report.json
sbatch --export=ALL,T3DIR=<T3 output>,IC256=<dir of make_waves.py --n 256,256,16> \
  tracks/core/analysis/bfix/gpu_job.sh
```
T1 and T2 need the snapshot of Track B's packages (`git archive track/B-emd-gw
tracks/B-emd-gw/periodic_z4c tracks/B-emd-gw/gw_diag python/nrpic | tar -x -C
scratch/core/tmp/bfix/B`; used at 767eb93).

### P6 Generator on several MeshBlocks and across a restart: prediction (before T5)

While the card job waits. Oblique wave k = (1,1,1), 16^3, one period, new processor
executable (`t5_blocks_restart.py`).
- P6a: with eight MeshBlocks of 8^3 the final Z4c dump (double precision) equals that of
  the single-MeshBlock run bit for bit (the Z4c update is the same arithmetic per cell;
  only particle runs depend on the block layout), and the error file is identical.
  Refuted by one differing value.
- P6b: a circular wave (amp = amp_cross = 1e-6, phase_cross = pi/2) restarted from a
  restart file written at about a quarter of the period ends with the fields of the
  uninterrupted run to 1e-11 (a Z4c restart is not bitwise, scripts/README.md) and with
  an error file whose RMS-L1 differs by less than 10 per cent. If the restart lost the
  new parameters or scaled the end time twice, the error would be of order A = 1e-6 or
  the run would end at another time: that would refute it.

### Outcome of T5 (run core-20261115-162321-db3cb0f, 33 s)

- P6a PASSED: eight MeshBlocks of 8^3 against one of 16^3, oblique wave, one period (37
  cycles): 0 of 90112 values differ in the final double-precision dump; the two error
  files are identical (RMS-L1 5.326589e-11).
- P6b PASSED, more closely than predicted: the circular wave restarted from the restart
  file of t = 0.15 ends at the same time and cycle with all 22 fields equal bit for bit
  to the uninterrupted run (I had allowed 1e-11) and with an identical error file
  (RMS-L1 7.561707e-11). The new parameters survive the restart and the end time is not
  scaled twice. No figure: both comparisons are exact zeros.

### P7 Oblique wave at 64 cells on a processor: prediction (before T6)

While the card job waits (one core, about an hour): k = (1,1,1), one period, N = 64,
new processor executable, stage evol of `t1_linear_wave.py`. Fourier-symbol prediction
(148 steps): amplitude error -7.88e-9, phase error -1.750e-7 rad. Prediction: the phase
within 10 per cent of that; the amplitude within 30 per cent (at this size the rounding
of 1 + h, about 1e-10 of A per value, is no longer negligible against 8e-9; Track B saw
the floor at 128 cells); max |h_x| / A below 1e-8; gw_diag's Psi_4 against the analytic
value below 3.2e-6 / 2^4 = 2e-7 times a factor three; constraints at the floor of P1c.
Refuted if the phase error is off by more than 10 per cent or the errors do not fall
from N = 32.

### P8 What restores the constraint level within ten steps: prediction (before T7)

Observation of T3: data that satisfy the Hamiltonian constraint as `ADMConstraints`
evaluates it (rms 3.1e-8 plain, 1.9e-6 jittered) show 1.65e-4 and 6.9e-2 at t = 0.10.
Hypothesis [JUDGEMENT until T7]: the evolution preserves a different discrete constraint
than the one that is evaluated. `ADMConstraints` takes the Ricci scalar from second
differences of the ADM metric; the Theta equation of the Z4c right-hand side takes it
from the conformal variables with the evolved Gamma^i. The two agree up to the truncation
error: of order (k h)^6/140 = 2.6e-5 of the source term for the 16-cell wave (times
16 pi E = 7.2: 1.9e-4, the level seen) and of order one for sources at the mesh
frequency. If so, the level reached at t = 0.1 does not depend on the time step.
Alternative: an error of the time integration (start of the source extrapolation,
splitting of particles and fields), which would fall with the step.
Test T7 (`t7_constraint_drift.py`): the initial data `plane4_fd` and `jit4_fd` of T3,
run to t = 0.3 with `dt_expansion` = 0.01 (as T3) and 0.0025 (a quarter of the step).
Prediction: H rms at t = 0.1 and 0.2 changes by less than 20 per cent between the two
steps, for both lattices. Refuted (and the alternative supported) if it falls by a factor
of about four or sixteen with the smaller step.

### Outcome of T7 (run core-20261115-162609-9dd5b98, 36 s)

P8 PASSED. History every 0.02; rms of H with `dt_expansion` = 0.01 and 0.0025 (steps of
0.01 and 0.0025):

| lattice | t = 0.02 | 0.04 | 0.10 | 0.20 | 0.30 |
|---|---|---|---|---|---|
| jittered, step 0.01 | 1.784e-2 | 3.488e-2 | 6.916e-2 | 6.585e-2 | 4.547e-2 |
| jittered, step 0.0025 | 1.787e-2 | 3.494e-2 | 6.843e-2 | 6.755e-2 | 4.546e-2 |
| plain, step 0.01 | 7.32e-5 | 9.53e-5 | 1.651e-4 | 2.208e-4 | 2.293e-4 |
| plain, step 0.0025 | 4.28e-5 | 8.03e-5 | 1.593e-4 | 2.180e-4 | 2.289e-4 |

(the rows are at the first step after each time, so the two steps sample slightly
different times: 0.1026 and 0.1001). For the jittered lattice the ratio small step over
large step is 1.002, 1.002, 0.989, 1.026, 1.000: the residual grows at 0.87 per unit
time from the first step on, whatever the step. For the plain lattice the ratio is
0.59, 0.84, 0.96, 0.99, 1.00: a part that depends on the step exists in the first few
steps and is gone by t = 0.1. So the level that the evolution restores is not an error
of the time integration [VERIFIED by this run]; it belongs to the spatial discretization
of the coupled system. That it is the difference between the Ricci scalar of
`ADMConstraints` and the one of the Z4c right-hand side (rather than, for instance, the
deposit not obeying a discrete continuity equation) remains [JUDGEMENT, TO VERIFY]: a
test would evaluate the constraint with the right-hand side's own operators.
Figure looked at: `figs/t7_constraint_drift.png` (the two steps lie on top of each other
for the jittered lattice; for the plain one they join at t = 0.05).
Consequence for the answer to Track B (REQUESTS_B.md, section 5): unchanged; a smaller
step does not lower the constraint level of a noisy lattice.
