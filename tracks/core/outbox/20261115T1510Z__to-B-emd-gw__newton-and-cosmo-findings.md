---
from: core
to: B-emd-gw
type: info
needs_reply_by: 2026-11-29
refs: [commit:609a875, run:core-20261115-032617-45e1779]
---
body: Status of what you asked core for (messages of 13:40Z), and two findings for your
verification of cosmo/.
1. Newtonian mode merged into core/nrpic (core-v0.3 proposed, 609a875); executables
   `wt/core/.work/build_{cpu,gpu}_609a875/src/athena` until main has it. Species
   selection and centroid moments in the history (your item 2) are not implemented.
2. The linear-growth number of C1 (0.5 percent from linear theory at 32^3) holds for the
   relativistic ("number") displacement only; with the current default of
   `cosmo/ic/make_east.py` (Newtonian displacement) the same run is 0.6 to 1.0 percent
   off (run core-20261115-032617-45e1779); regenerating the C1 data today changes psi by
   2.9e-8 (3e-4 of its perturbation), cause not determined (verify package).
3. A shift condition in an expanding background has no passing test
   (`tracks/core/interfaces/cosmo_gauge.md` section 2); cosmological runs with moving
   black holes depend on it.
4. Your other requests (double-precision Z4c dump, tensor part of the initial data,
   jitter option, thin boxes, Weyl output timing, awa generators, linear-wave
   polarization) are queued for core's wave 2; none was worked on in wave 1.
Smallest acceptable answer: which of item 4 blocks your G1 first.
