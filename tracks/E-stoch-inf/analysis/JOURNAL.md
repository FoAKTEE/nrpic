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

## 17:20 Outcome of the plane check (run E-20261115-171628-1737ebe): one prediction failed

Passed: mean |H| and rms H from the dumps equal the history to 2.0e-14 and 5.7e-15; box
mean of [H] per cell equals the code's [H] to 5.3e-7; orders of rms H/[H] and rms M/rms [M]
at t = 0 between N = 16 and 32: 5.97 and 5.66 (the interface's 5.97 and 5.66, so the
dump-based ratios reproduce the code's convergence).
Failed: sqrt(<chi |M|^2>) against the history's rms |M|: equal at t = 0 (3e-15 and 5e-15)
but 4.5e-5 to 5.5e-4 apart at t = 0.25 and 0.5, against the bound 1e-6. The bound was
wrong: I treated gt - delta as second order, but in this test the metric perturbation is
first order in A = 0.003, so gt^ab != delta^ab changes the norm of M at relative order
1e-3. Cause not yet shown by a run.

## 17:20 Prediction: the same check with the conformal metric from a `bin` output

`plane_check.py` now adds `<output2> bin, variable = z4c, dt = 0.25` (single precision) and
recomputes the physical norm chi gt^ab M_a M_b and At_ij At^ij from it. If the explanation
above is right, sqrt(<chi gt^ab M_a M_b>) equals the history to <= 1e-6 (float32 gt: an
absolute error of 6e-8 on numbers near 1), and the box mean of [H] with At At included
equals the code's [H] to <= 1e-9. Refuted if the difference stays at 1e-4 (then the
reader's assembly of M or of the bin file is wrong). This also tests `read_bin_metric` on
real output (its first use).
