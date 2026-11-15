# JOURNAL of core, work package dfix (branch `core/requests-adf`)

Append-only. Predictions are written before a test runs, outcomes after, also when the
prediction failed. Runs are registered under `tracks/core/runs/<run_id>/manifest.json`
(outputs under `scratch/core/<run_id>/`). Labels: [VERIFIED] read or measured in this
session (with locator), [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 session dfix-1

Read: `CLAUDE.md`, charter to "Owners", brief lines 493-553, 688-706, 834-860, decisions
0010 to 0015, the rulings after wave 1, core's `HANDOFF.md`, `STATUS.md`,
`stage/G2/OPEN.md`, and the eleven requests of tracks D, A and F named in the task
(triage: `tracks/core/interfaces/REQUESTS_ADF.md`).

### T1 The tracer defect (request D `tracer-push-release-build`)

What Track D saw [VERIFIED from the message, run D-bh-dress-20261115-121313-284ec4f]: with
the card executable of release core-v0.2, the six tracers of
`problems/puncture/horizon_calib.athinput` do not follow their geodesics: one is removed
at t = 0.31 M, five leave outward near light speed.

What I read before any run [VERIFIED, file and line of this branch at 3da9086]:
- all six tracers of that input have `p<n>_m = 0.0` (lines 132-179), and the input calls
  them "massless tracers": test particles without sources on timelike geodesics;
- `athenak/src/particles/nrpic.cpp` line 462: `eps = (pr(IPM,p) > 0.0) ? 1.0 : 0.0`, and
  line 502 hands `eps` to `PushMidpoint` in the branch `metric = mesh` only. With
  `eps = 0` the pusher uses `W = sqrt(gamma^ij u_i u_j)` (`nrpic_kernels.hpp`,
  `LorentzFactorEps`): a null geodesic. The analytic-metric branches (lines 505-522) call
  the six-argument `PushMidpoint`, which sets `eps = 1`;
- the rule "no rest mass: null geodesic" entered with commit 4467852 (cosmology C0, null
  particles for light rays); the tracer inputs are older (935da4d). The light rays of
  `cosmo/ic/ray_ic.py` never carry m = 0: their mass is `-max(t_e, 1e-30)` (line 41).

Hypothesis H1: since 4467852 a particle with m = 0 on the mesh metric is pushed as a
photon with momentum k_i = u_i; nothing differs between card and processor builds, and
nothing is wrong with the reading of `p<n>_u<i>`. The tracer at rest (tag 5, u_i = 0) has
W = 0, its velocity alpha u^i/W is 0/0, the state turns non-finite and the particle is
removed in the first step.

Predictions, written before the runs (release executables of core-v0.3, unchanged):
- R1 (processors, `horizon_calib.athinput`, tlim = 1): tag 5 is removed in the first
  cycle (`n_excised = 1` in the first history record after t = 0); tags 0 to 3 move with
  the coordinate speed of light of the initial slice, alpha/psi^2 = psi^-4 with
  psi = 1 + 1/(2 r): 0.7260 at r = 6, 0.7847 at r = 8, 0.8227 at r = 10, measured from
  the first trajectory records (within 2 per cent: the lapse starts to evolve). A
  timelike tracer would move at psi^-4 [u^2/(1 + u^2)]^(1/2), u^2 = u_y^2/psi^4:
  0.3233 at r = 6, 0.2959 at r = 8, 0.2739 at r = 10.
- R2 (the same with `particles/p<n>_m = 1e-300` for n = 0..5 on the command line;
  `deposit = false`, so the mass has no other effect): no particle is removed, tags 0 to
  3 move at the timelike speeds above and keep their coordinate radius to 1e-3 over 1 M.
- R3, R4: the card executable gives the same as R1 and R2 (speeds equal to 1e-6).
H1 is refuted if R2 still shows the outward motion or the removal (then the reading of
the momenta or the push itself is at fault), or if R1 on processors is healthy while the
card run is not (then the defect is in the card build).
