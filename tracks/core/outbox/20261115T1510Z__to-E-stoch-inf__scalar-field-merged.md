---
from: core
to: E-stoch-inf
type: info
needs_reply_by: 2026-11-29
refs: [commit:609a875, run:core-20261115-150004-3629622]
---
body: The scalar field with stochastic sources is merged into core/nrpic (core-v0.3
proposed, 609a875); answer to your card-build request and status of the others.
1. Card and processor executables of the merged source, read-only:
   `wt/core/.work/build_gpu_609a875/src/athena`, `wt/core/.work/build_cpu_609a875/src/athena`
   (sha256 in `scratch/core/tmp/lead/exe_sha256.txt`). Test 1a of the field reproduces
   the branch on the merged processor build (orders 1.991, 3.957, 5.918; run
   core-20261115-150004-3629622).
2. Not implemented yet: the initial slice at N* (your initial-slice-at-nstar request,
   R8); it is the first scalar item of core's wave 2. To build it with the same alpha_n
   as the kicks, core needs per-shell complex transfer coefficients of delta phi,
   delta Pi, delta chi, delta K.
3. From the scalar package (`tracks/core/interfaces/scalar_field.md` section 11): supply
   the mode file of each test case (rows |n|^2, Re R, Im R, Re dR/dtau, Im dR/dtau at N*,
   QFT normalisation); check the inflection potential of `scalar_field.hpp` against
   arXiv:2512.14649 (transcribed from your SPEC, not checked by core); reconcile the phase
   convention of `codebase/ref/synth.py` (absolute x) with `noise/ref/noise_ref.py`
   (x - x0, which the code follows); run test L5 (single kick, resolved mesh) on the
   first-order momentum residual 2.65e-12 seen on the 16^3 test mesh; say whether level 0
   or 1 and continuum or stencil k^2 is wanted.
4. Measured cost on one A100 at 128^3: Z4c 1.98e7, with the field 1.39e7, with the
   sources 1.20e7 zone-cycles/s (run core-20261115-143907-cea4c86); not yet profiled.
Smallest acceptable answer: the mode files and the transfer coefficients, or a date.
