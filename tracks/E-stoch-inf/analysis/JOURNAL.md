# Journal of the analysis package of E-stoch-inf (wave 2 helper)

Predictions are written before a run starts; outcomes are appended below them, failed
predictions included. Times are UTC on 2026-11-15. Run ids are those of
`harness/bin/nrpic-run` (`tracks/E-stoch-inf/runs/<run_id>/manifest.json`).

## 17:05 Predictions: noise unit test at the base size (N = 64, 300 steps), U9 on a card

Set-up. Inputs `inputs/u64/U*.athinput`, made by `scripts/make_u_inputs.py` from the lead's
base `lead/inputs/u_base.athinput` (NOISE_SPEC section 9 with dt = 0.25 x 2.5/64, dumps at
cycles 0, 100, 200, 300, restart file every 150 cycles). Executables: the release builds
of core-v0.3, `.work/build_gpu_v03/src/athena` (card) and `.work/build_cpu_v03/src/athena`
(processors). The card job runs U1, U2, U3, U5a, U5b, U6, U7, U8; its U2 is U9. The
processors run U2 and then U4 (U2 restarted at cycle 150). Validator:
`noise/validate/validate_noise.py` (the track's contract, A0-A15).

Source facts the predictions rest on (read, not run): the release forms the window
increment of the tanh window as sinh(x1 - x0)/(2 cosh x1 cosh x0)
(`athenak/src/scalar_field/scalar_field_noise.cpp:570-577`, commit 5a6953e "window
increment without cancellation"), while the reference `noise/ref/noise_ref.py:155,159`
still forms W(t) - W(t - dt). The lead's earlier validation used core's executable of
836ac86, which predates 5a6953e.

- **P1 (frozen scheme, card: U1 with U2, U3, U5a/U5b, U8).** A0-A11, A13, A15 pass; A11
  bit-identical for 1, 8 and 64 MeshBlocks on the card. Refuted by any failed
  deterministic test, or by a statistical test that also fails on the second seed.
- **P2 (Markov-Heaviside, card U7).** Every applicable test passes.
- **P3 (Markov-tanh, card U6).** With the reference as it is, A1 fails at a level between
  1e-11 and 1e-8 of the rms, from the cancellation in the *reference's* increment (one
  unit in the last place of W near 1 gives sqrt(dW) an error of about u/(2 sqrt(dW)),
  saturating near sqrt(u) base when dW < u). With the reference increment replaced by the
  cancellation-free form of the code (a wrapper in this package, `scripts/val_cf.py`;
  the reference file itself is not changed), A1 passes below 1e-11. Refuted, as an
  explanation, if A1 still fails with the cancellation-free reference (then the code has
  another error), or if A1 passes with the standard reference.
- **P4 (A14, U9 on the card against U2 on processors).** Not bitwise; the largest
  difference is between 1e-16 and 1e-13 of the rms (device libm for cos, sin, tanh, exp
  and fused multiply-adds), below the 1e-12 criterion. Refuted if above 1e-12.
- **P5 (A12 on processors, U4 against U2).** Bit-identical at cycles 200 and 300.
- **P6 (cost).** Each card run below one minute; the job below 0.15 card-hours. The
  processor U2 takes 80-120 min (1.35e4 zone-cycles/s of the lead's timing run
  E-20261115-135218-bdf4710 gives 97 min for 64^3 x 300), U4 about half.

## 17:08 Run E-20261115-170651-885fc6e stopped (my error, no result)

The local launcher passes its arguments without a shell, so the literal argument
`$NRPIC_RUN_DIR` reached the script unexpanded and the runs started writing into a
directory of that name in the worktree root. Stopped after a minute with `nrpic-run stop`,
the stray directory removed, the run closed as stopped. Resubmitted with `bash -c`, which
expands the variable (as in the lead's HANDOFF command).

## 17:11 Predictions: estimators of `sfa.py` on synthetic fields (`tests/test_sfa.py`)

The criteria are printed in the test file and are fixed now, before the first run.
- T1 (reader, coefficients): a field from known coefficients, written as an 8-MeshBlock
  NRSFDMP1 dump, comes back to round-off (<= 1e-13 of the rms); L, x0, h exact.
- T2 (R^NR of P-c on a slice built nonlinearly from R, psi, E): error of second order in
  the amplitude A (<= 1e-4 of the rms at A = 1e-5; slope 1 of the relative error against
  A). Without the gt term the error is of first order (relative error independent of A,
  of order |k^2 E/3|/R, here set to O(1) on purpose); with <Pi> of the wrong sign the
  relative error is O(1). The SPEC 5.3 slice (delta X = 2 Phi_B, gt = delta) returns R at
  first order exactly. Refuted if the slope is not 1 (an error in a factor of Phi or of
  the field coefficient would make it 0).
- T3 (per-mode ratio, .modes parser, drift): planted deviations recovered to 1e-10;
  header and rows of a record written with the code's printf formats parsed exactly.
- T4 (shell spectrum): Delta0 exactly for unit-modulus amplitudes; with the code's
  Gaussian amplitudes the pooled ratio within 4 sigma of 1.
- T5 (constraints): first differences equal the stencil symbol to 1e-13; [H] per cell
  exact for a known Ricci scalar; [M] of a plane wave equal to its closed form.
Development runs before registration go to scratch/E-stoch-inf/tmp/ and are for
debugging only; the numbers quoted come from the registered run.

17:13 Development run (scratch/E-stoch-inf/tmp/dev_tests, not a result): T2a failed its
absolute threshold with the correct scaling. The relative error is 2.19e-1, 6.91e-2,
2.34e-2, 7.05e-3, 2.35e-3, 7.06e-4, 2.35e-4 at A = 1e-2 ... 1e-5: exactly proportional to A
(second order), with coefficient 23.5, not the <= 10 the threshold assumed. I had not
estimated the factor from taking the maximum over 32^3 cells of a product of two
Gaussian fields (about (4.5 sigma)^2 of the rms) with |d_i d_j E| of order |psi| in this
synthetic slice. The criterion is amended to <= 1e-3 at A = 1e-5 together with the
unchanged slope 1 +- 0.1, which is what separates second from first order (the control
without gt stays at 0.657 for every A). Second bug of the development run: the test's
own .modes writer used the C format %llu, which Python does not know (fixed: %d).

## 17:15 Outcome of the synthetic tests (run E-20261115-171445-36152c4)

All 15 pass (`fig/test_sfa.json`; figures `fig/fig_t2_extraction.png`, `fig_t3_permode.png`,
`fig_t4_spectrum.png`, `fig_t5_momentum_norm.png`, looked at). T2: relative error of R^NR
2.35e-4 at A = 1e-5 with slope 1.00 (second order); without the gt term 0.657 at every A
(first order); flipped <Pi> 9.13; SPEC 5.3 slice 3.6e-10. T4b pooled spectrum ratio
z = 1.25 over 8538 modes. The figures show what the numbers say; in fig_t4 the two lowest
shells (3 and 6 modes) lie at 2.5 and 2.4, inside the Gamma spread of so few modes.

## 17:16 Predictions: constraint estimators on real output (core's plane perturbation)

`scripts/plane_check.py` runs `problems/scalar/plane.athinput` at N = 16 and 32 (mesh
N x N x N/2) with the release processor executable and recomputes the constraint
statistics from the dumps (t = 0, 0.25, 0.5).
- mean |H| and rms H from the dumps equal the history's to <= 1e-10 relative (same cells;
  only the order of summation differs).
- box mean of [H] per cell (sfa.ham_norm_cells, At At left out) equals the code's [H] to
  <= 1e-6 relative (At At is second order; At = 0 at t = 0).
- sqrt(<chi |M|^2>) equals the history's M_rms to <= 1e-6 (gt = delta up to the
  perturbation).
- the ratios rms H/[H] and rms M/rms [M] fall between N = 16 and 32 at t = 0 at order 5 to
  6.5 (the interface reports orders 5.97 for H and 5.66 for M from rms values,
  coord/INTERFACES/scalar_field.md section 10, test 3).
Refuted: any of the four comparisons outside its bound (then the reader or the [H]
reconstruction is wrong), or an order outside 5-6.5.

## 17:18 Outcome of the plane check (run E-20261115-171628-1737ebe): one prediction failed

Passed: mean |H| and rms H from the dumps equal the history to 2.0e-14 and 5.7e-15; box
mean of [H] per cell equals the code's [H] to 5.3e-7; orders of rms H/[H] and rms M/rms [M]
at t = 0 between N = 16 and 32: 5.97 and 5.66 (the interface's 5.97 and 5.66, so the
dump-based ratios reproduce the code's convergence).
Failed: sqrt(<chi |M|^2>) against the history's rms |M|: equal at t = 0 (3e-15 and 5e-15)
but 4.5e-5 to 5.5e-4 apart at t = 0.25 and 0.5, against the bound 1e-6. The bound was
wrong: I treated gt - delta as second order, but in this test the metric perturbation is
first order in A = 0.003, so gt^ab != delta^ab changes the norm of M at relative order
1e-3. Cause not yet shown by a run.

## 17:18 Prediction: the same check with the conformal metric from a `bin` output

`plane_check.py` now adds `<output2> bin, variable = z4c, dt = 0.25` (single precision) and
recomputes the physical norm chi gt^ab M_a M_b and At_ij At^ij from it. If the explanation
above is right, sqrt(<chi gt^ab M_a M_b>) equals the history to <= 1e-6 (float32 gt: an
absolute error of 6e-8 on numbers near 1), and the box mean of [H] with At At included
equals the code's [H] to <= 1e-9. Refuted if the difference stays at 1e-4 (then the
reader's assembly of M or of the bin file is wrong). This also tests `read_bin_metric` on
real output (its first use).

## 17:21 Outcome (run E-20261115-171859-0b34449): explanation confirmed

With gt^ab from the bin output the physical norm of M equals the history to 2.0e-9 (bound
1e-6) and the box mean of [H] with At At equals the code's [H] to 1.0e-14 (bound 1e-9); the
gt = delta form stays 5.5e-4 off, as recorded. So the dump reader, the [H]
reconstruction and `read_bin_metric` agree with the code on real output, and a physical
|M| needs the conformal metric, which the dump does not hold (request to core, README).
The ratio [M] used for |M|/[M] is the flat norm of covariant components, as P1's [M]; it
does not depend on gt. Figure `fig/fig_plane_constraint_ratios.png` (looked at: the
dump-based ratios lie on the history's crosses).

## 17:23 Predictions: slow-roll scouting runs with the release executable, homogeneous start

What the release cannot do: the perturbed initial slice at N* (request R8). What it can:
start from the homogeneous slice (`id = flrw`) dn_pre = 1.5 e-folds before the lowest
mode reaches the window, where W(k_min) = 3.6e-7 (scripts/make_sr_case.py, case.json), and
let the Mukhanov-Sasaki sources bring every mode in. By linearity the NR perturbation then
differs from the papers' (initial slice W(t*) R plus sources) by the free evolution of
the slice W(t0) R, a constraint-satisfying linear solution of relative size W(t0)
[JUDGEMENT: argument, tested by the runs below only through PS2]. Case: quadratic
potential, eps1 = 0.0105 at the start, H ~ 1, geodesic slicing, level 0, stencil
projector, k_max = N k_sigma*/4, amplitude scaled to Delta_R ~ 1e-6, end at ln a = 8;
reference = the code's own lockstep R_q (any mode-equation data are valid).
Disclosure: before writing this, a development run to t = 0.6 (ln a = 0.5, no mode
crossed yet; scratch/E-stoch-inf/tmp/sr16dev) was used to debug analyse_sr.py; it showed
<|H|>/<[H]> = 6.6e-14 and per-mode deviations up to 1.8 percent at that early time, while
W was still about 1e-4.
- PS1 constraints: with the correct sign the largest <|H|>/<[H]> lies between 1e-8 and
  1e-5 (second order, R_rms^2 ~ 1e-6 times a factor 0.01-10); the control with the sign
  of the Pi kick flipped (N = 16) is at least 30 times larger during entry (first order).
- PS2 per mode at the end, modes with k <= k_max/2: |R^NR_n/(L^-3/2 W R alpha) - 1| <= 2
  percent at N = 32 and <= 5 percent at N = 16, with the gt term. Refuted otherwise; a
  common offset of all modes would point to a factor in the kicks or the extraction, a
  k-dependent one to dispersion or the homogeneous start.
- PS3 gt term: rms(gt term)/rms(R^NR) at the end between 1e-4 and 5e-2; the per-mode
  ratios with and without it differ by less than 2 percent.
- PS4 freezing (SPEC 7.3): modes with N_f - N_k >= 5 drift by |d ln|c|^2/dN| <= 2.5e-3
  per e-fold from N_k + 4 on, not by -4 eps1 = -0.042 (the FLRW-lattice behaviour).
- PS5 the code's lockstep R_q agree with SciPy's integration of the same data to <= 1e-3
  at every dump.
- PS6 cost: N = 16 below 5 min per run; N = 32 between 30 and 60 min (one core).

## 17:24 Prediction P3' (same as P3, scaled case on processors, while the card waits)

U6 of the lead's scaled base case (N = 32, 120 steps, `lead/inputs/u_base32.athinput` with
noise_scheme = markov) with the release processor executable (`scripts/u6_scaled.sh`):
with the reference as it is, A1 fails between 1e-11 and 1e-8 of the rms; with the
cancellation-free reference (`scripts/val_cf.py`) every test passes, A1 below 1e-11.

## 17:29 Outcome PS1-PS6 at N = 16 (run E-20261115-172349-0bdb97d, with the control)

All predictions hold (`fig/analyse_sr_N16.json`; figures `fig/fig_sr_permode_N16.png`,
`fig_sr_constraints_N16.png`, `fig_sr_spectrum_N16.png`, looked at).
- PS1: largest <|H|>/<[H]> 2.07e-8 at ln a = 1.52 (R_rms = 8.4e-4 there, 1.55e-3 at the
  end), then decaying to 8.3e-13; control 1.26e-5 at the same time, 610 times larger.
  rms M/rms [M]: at most 2.2e-3 (first order in R, as 2512.14649 PRD_v2.tex:541 and 746 say |M|/[M] should be), control
  0.2-0.4. Not predicted: before the modes enter (ln a = 0.27-0.78, R_rms 1.7e-8 to
  1.9e-6) rms M/rms [M] is already 5e-6 to 5e-5, i.e. not second order in R there; the
  same window in the control is 0.30. Cause not tested; a candidate is the continuum k^2
  of the mode equation against the stencil Laplacian of the evolution (interface 7.4),
  which would leave a first-order residual while the modes are sub-horizon [TO VERIFY].
- PS2: per-mode ratio R^NR_n/(L^-3/2 W R alpha) - 1 at ln a = 7.8 for k <= k_max/2:
  max 8.3e-5 (rms 3.9e-5) with the gt term; all modes max 3.9e-3 (one at |n| = 4).
- PS3: gt term / R^NR at the end 4.9e-3 (rms); without it every mode is low by a common
  -0.48 percent (mean -4.82e-3), i.e. the dump alone gives R^NR to 0.5 percent here.
- PS4: 101 modes with N_f - N_k >= 5: largest |d ln|c|^2/dN| from N_k + 4 on is 3.3e-4 for
  the NR field (with or without gt) and 3.3e-4 for the lockstep W R itself, against the
  2.5e-3 bound and the FLRW-lattice -4 eps1 = -0.042.
- PS5: lockstep R_q against SciPy 7.3e-4 at most (RK4 truncation while the modes are
  sub-horizon; it does not grow afterwards).
- PS6: 2 min per run.

## 17:30 Outcome P3' (run E-20261115-172423-5234cce): the reference, not the code

U6 of the scaled case with the release executable: with the track's reference as it is,
A1 fails at 9.77e-11 of the rms (worst stoch_c2 at cycle 120), every other test passes;
with the cancellation-free increment of `scripts/val_cf.py` A1 is 3.3e-15 and all tests
pass (A2-A8, A10 unchanged to the digits shown). So the release executable's Markov-tanh
noise is exact, and the A1 failure the lead recorded (1.07e-10 with core's 836ac86) now
sits in the reference `noise/ref/noise_ref.py` (W(t) - W(t - dt)), which the noise
package should change to the sinh/cosh form (request in README). Figure
`fig/fig_val_u6_scaled_cf.png` looked at: the shell means scatter inside the band except
the 3-mode shell |n| = 1 at cycle 120 (0.38), which the exact Gamma test of A2 accepts.

## 17:42 Prediction P7: processor U2 of the base case alone (before the card job runs)

The card job is twelfth in the queue. As soon as the processor U2 (64^3, 300 steps, frozen,
8 MeshBlocks) exists, it is validated alone (A0-A10, `validate_noise.py --input
inputs/u64/U2.athinput --run PROC/U2`): every test passes, A1 below 1e-13 of the rms (the
frozen increment has no square root, so the reference's cancellation costs at most one
unit in the last place of dW against values of order 1e-2), A10 below 1e-14. This is the
first validation at the base size (the lead's was at N = 32).

## 17:59 Outcome PS1-PS6 at N = 32 (run E-20261115-172347-a297a96, no control)

- PS1: largest <|H|>/<[H]> 2.14e-8 (at ln a ~ 1.5), decaying afterwards. Holds.
- PS2: per-mode ratio at ln a = 7.8 for k <= k_max/2 with the gt term: max 1.0e-4 (rms
  3.2e-5); all modes max 3.8e-3 (the deviations grow towards |n| = 7-8). Holds (bound 2
  percent).
- PS3: gt term / R^NR 4.9e-3; without it a common -0.49 percent. Holds.
- PS4: 89 modes, largest |drift| 3.4e-4 per e-fold (NR) and 3.3e-4 (lockstep W R). Holds.
- PS5 FAILED: lockstep R_q against SciPy 1.42e-3 > 1e-3 (N = 16: 7.3e-4). The largest
  difference appears at the first dump and stays constant (figure), i.e. it is made while
  the modes are deep inside the horizon; N = 32 carries modes to k/(aH) = 36 at the start
  against 18 at N = 16 with the same omega dt per step. Candidate cause: RK4 truncation of
  the lockstep integration at the step of the mesh [not yet tested; P8 below tests it].
- PS6: 2110 s of processor time. Holds.
Not predicted: in fig_sr_permode_N32 the NR coefficients of |n| = 5.5 and 8 sit at
|c|^2 ~ 1e-21 between ln a = 0.7 and 2, far above L^-3 |W R|^2 (1e-30 to 1e-24), before
these modes reach the window; the level is that of products of the modes already in
(R_rms 1e-5 to 1e-4 there, squared), so mode coupling at second order is the likely
source [JUDGEMENT; harmless once the modes enter, where the curves join].

## 18:00 Prediction P8: is the lockstep difference of PS5 the time step?

N = 16 case of run E-20261115-172349-0bdb97d again with cfl_number = 0.125 (half the step).
If RK4 truncation sets the lockstep-SciPy difference, it falls by about 16 (order 4) from
7.3e-4, i.e. below 1e-4 (refuted if it falls by less than 8). Decision rule for the
per-mode residual (8.3e-5 at k <= k_max/2, no prediction of its cause): if it falls by 8
or more it is temporal; if it changes by less than a factor 2 it is not.

## 18:05 Outcome P8 (run E-20261115-175951-2e2387d): lockstep difference is the time step

With half the step the lockstep-SciPy difference falls from 7.3e-4 to 4.5e-5, a factor
16.1 (RK4, order 4): PS5's failure at N = 32 is the truncation of the lockstep integration
at the mesh's step, not a defect, and the bound 1e-3 I set was simply too tight for the
sub-horizon start. The per-mode residual with the gt term stays at 8.31e-5 (8.31e-5
before), so it is not temporal. Candidate [JUDGEMENT, untested]: the float32 resolution of
gt in the bin output. The gt term is 4.9e-3 of R; one unit in the last place of float32
near 1 (1.2e-7) against gt - delta of about 7.5e-6 is 1.6e-2 of that term, i.e. 8e-5 of R,
the size of the residual. Without the gt term the modes scatter by only 4e-5 about their
common -0.48 percent offset. A double-precision gt in the dump would decide it (request
(a) to core). <|H|>/<[H]> peak 2.138e-8 (2.066e-8 at the full step).

## 18:05 Card job done (run E-20261115-170645-3b21217); predictions P5' and the validations

Slurm 4465 ran at 18:03 by backfill: eight runs, each 1-8 s of card time (U1 5.4 s,
1.46e7 zone-cycles/s; U3 with 64 MeshBlocks 8.0 s), 55 s in all, 0.0153 card-hours. P6
(card part) holds. The validations (`scripts/val_base.sh CARD - OUT`) follow in a
registered run; their predictions are P1, P2, P3 (17:05). The card U2 wrote its restart
files, so U4 can now run on a card too:
- P5' (A12 on the card): U4 = card U2 restarted at cycle 150 on a card
  (`inputs/u64/card_u4.list`) gives dumps at cycles 200 and 300 bit-identical to card U2.

## 18:06 Outcome P1-P3 on the card (validation run E-20261115-180533-24a7781)

- P1 holds: frozen scheme on the card, every test passes; A1 9.8e-14, A8 1.4e-13, A10
  4.8e-15; A11 bit-identical for 1, 8 and 64 MeshBlocks on the card; A13 3.5e-15 (N = 32
  against 64); A15 z = 1.46; A2, A3, A4, A7 inside their bounds (A9 not applicable: the
  power model has no integrated field).
- P2 holds, with little power: Markov-Heaviside (U7) passes, A1 2.6e-15; with dumps every
  100 cycles only the shell |n|^2 = 37 crosses inside a dumped step (figure), so A3, A4, A8
  are not applicable and A2 rests on one shell. The scaled case of the lead (dumps every 40
  cycles) is the stronger test of this scheme.
- P3 holds: Markov-tanh (U6) with the reference as it is fails A1 at 8.5e-10 (inside the
  predicted 1e-11 to 1e-8); with the cancellation-free reference A1 is 4.0e-15 and every
  test passes. Same verdict as P3' on processors.
Figures `fig/fig_val_card_frozen.png`, `fig_val_card_markov_tanh_cf.png`,
`fig_val_card_markov_heaviside.png` looked at.

## 18:27 Note before A14

The processor U2 writes its last dump at about 18:50; U4 follows in the same run until
about 19:40. A14 (P4) is validated as soon as U2 is complete, alone
(`validate_noise.py --input inputs/u64/U2.athinput --run PROC/U2 --card CARD/U2`, which
also gives A0-A10 on the processor U2: P7). `val_base.sh` now looks for U4's dumps rather
than its directory, which the processor script creates at the start.

## 18:48 Outcome P4, P7 (validation run E-20261115-184748-9b010fa)

- P4 holds: U9 (U2 on the card, run E-20261115-170645-3b21217) against U2 on processors
  (run E-20261115-170727-d15df12, 6012 s, 1.31e4 zone-cycles/s): six fields at four
  cycles, largest difference 2.2e-15 of the rms, not bitwise. A14 passes (<= 1e-12).
- P7 holds: the processor U2 passes A0-A10 alone (A9 not applicable); A1 9.8e-14 (bound
  1e-13, just inside; the same value as the card's U1, so it is the reference's increment
  at cycle 300, not the platform), A8 1.4e-13, A10 5.1e-15. The statistical tests give the
  same numbers as the card's U1 to the digits shown (same amplitudes, layout-independent
  synthesis).
- P6 (processor part) holds: 6012 s for U2 against the predicted 80-120 min.
Pending in this package: A12 (U4) on processors (run E-20261115-170727-d15df12 continues
with U4 until about 19:40) and on the card (run E-20261115-180526-6b68c33, Slurm 4479,
queued).

## 18:50 Close of the package (helper)

Done and tested: the estimators (`sfa.py`, 15 synthetic tests, real-output check against
the code's history), the base case on the card (U1-U3, U5a/b, U6-U8) and U9/A14, the
slow-roll scouting case at N = 16 (with control) and 32 with the half-step check. Card
time used: 0.0153 card-hours (plus at most 0.083 reserved for the U4 card job).
Not done, left running or queued: A12 at the base size, U4 on processors (inside run
E-20261115-170727-d15df12, about 19:40; that run must be closed with `nrpic-run finish`)
and on a card (E-20261115-180526-6b68c33, Slurm 4479, queued); predictions P5 and P5'
stand untested. Validation command: `scripts/val_base.sh` (README).
Predictions that failed in this package: the T2a absolute threshold (development run,
amended before registration), the |M| norm with gt = delta (plane check), PS5 (lockstep
vs SciPy at N = 32; explained by P8). Open, untested: the early first-order momentum
residual (README item 5) and the cause of the 8.3e-5 per-mode residual (float32 gt is the
candidate).
