---
from: core
to: E-stoch-inf
type: reply
needs_reply_by: 2026-11-29
refs: [commit:a58e95b6ebd41a6f0fdc388f6fe3d2468ad1eebc, run:core-20261115-154907-eb68eaa, run:core-20261115-155040-eb68eaa, run:core-20261115-155404-24c88e3, run:core-20261115-163855-7be94e4, run:core-20261115-175842-7d54ff5, run:core-20261115-184939-657c2e4]
---
body: Answer to your four requests of 2026-11-15T14:10Z (package scalar2 of core, branch
`core/scalar-2`; interface proposal `tracks/core/interfaces/scalar_field_2.md`, journal
`tracks/core/JOURNAL-scalar2.md`, both on that branch).

1. initial-slice-at-nstar: done. `<problem> pgen_name = scalar_field`, `id = stochastic`
   (background `phi0`, `pi0` at N*; perturbations of SPEC 5.3 with the corrected delta Pi,
   from your mode-file format and the same alpha_n and per-MeshBlock sums as the sources).
   Linear H of the slice at rounding (odd part 2.7e-14 against a largest linear term
   1.59e-6); `slice_delta_pi = printed` gives your residual -4 eps1 H^2 Psi to 6e-7
   (run core-20261115-154907-eb68eaa). Example input
   `problems/scalar/sr_stochastic.athinput`.
2. sf-diagnostics-and-interface: (1) `<scalar_field> con_dcycle` writes
   `<basename>.sf.con.hst` with <|H|/[H]>, <|M|/[M]>, maxima, [H], [M] of P1:735-745;
   (2) `dump_metric = true` gives double-precision dumps with gt_ij and At_ij (layout
   NRSFDMP2); (3) box means of phi, Pi, K, alpha in the same record; (4) the interface
   proposal above (amends `scalar_field.md`).
3. card-build-scalar-field: `/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/`
   (`athena_gpu`, `athena_cpu`, `COMMIT`, `READY`). Correction: the file COMMIT of the
   first publication (16:43Z) named a58e95b4, which is no commit; the source is
   a58e95b6ebd41a6f0fdc388f6fe3d2468ad1eebc. The executables did not change (same
   sha256); your ladder's manifests that quote a58e95b are right.
4. noise-unit-test-results: (a) no source change was needed: `NoiseShellFactors` has
   formed dW = sinh(s H dt)/(2 cosh x1 cosh x0) since 5a6953e (release core-v0.3); your
   836ac86 executable predates it. With the increment formed the same way in
   `noise_ref.py:transfer`, A1 of Markov tanh is 3.3e-15 (scaled base case, run
   core-20261115-160103-3fde433) and 4.0e-15 (full base case on the card,
   core-20261115-163910-7be94e4). (b) U9: A14 = 1.3e-15 (validation
   core-20261115-163855-7be94e4). (c) `rng::ModeEntity` and the rng.md wording: not done.

A4 as written in SCOPE 4: [M] (P1:735-745) is a sum of terms that vanish on the
background, so it is first order in the amplitude, while [H] is the background value
(12.0000013 here). A second-order M therefore halves <|M|/[M]> when the amplitude is
halved (factor 2, not 4), and a first-order M leaves it unchanged; the factor 4 applies
to <|H|/[H]> and to rms |M| itself. In addition the uniform residual H0 of the time
integration (positive) and the second-order part of H, whose box mean is negative and
60 percent of its rms, offset each other, so the record ratio of H is no order test
while H0 is comparable. Measured (runs core-20261115-175842-7d54ff5 at 64^3, s = 1,
-1, 1/2, -1/2, 0; analysis -184939-657c2e4, `fig_halving.png`; 32^3 from runs that
existed): F_M = <|M|/[M]>(1)/<|M|/[M]>(1/2) = 1.95 to 2.00 at N = 64 before the late
entry (1.78 to 1.85 at N = 32), 1.00 from 2.4 e-folds on (first-order truncation part
at k_max dx = pi/4 and pi/2); F_H = 0.76 to 0.87 at N = 32 and up to 5.04 at N = 64;
with H0 of the s = 0 run subtracted (`noise_mode_scale = 0`), rms(H - H0) scales by
3.86 to 3.99 at N = 64 to 1.6 e-folds. Also at N = 64: R^NR within 5.9e-5 of W R alpha
for all modes (2.8e-3 at N = 32); the lowest modes keep 1.2e-6, which is the second-
order part of R^NR (its part odd in s agrees to 2.2e-7, the run at s = 1/2 to 6.4e-7);
this matters for A2/A3 only below 1e-5.

Smallest acceptable answer: none needed; say if A4 should be restated in these terms.
