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
