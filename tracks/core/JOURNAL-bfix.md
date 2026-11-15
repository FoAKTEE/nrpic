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
