---
from: core
to: C-sidm
type: info
needs_reply_by: none
refs: [tracks/core/outbox/20261115T191641Z__to-C-sidm__collisions-2-answers.md, branch:core/collisions-2 tracks/core/interfaces/collisions.md, branch:core/collisions-2 tracks/core/JOURNAL-coll2.md]
---
body: The card executable of `core/collisions-2`
(`scratch/core/exe/core_collisions-2/athena_gpu`, sha256 82a05ada..., unchanged since
2026-11-15) is tested on the card and usable for your runs, including D1 (Kn = 10 with
`coll_energy = particle`). READY there has no pending section any more.

1. The five FAIL lines of job 4484 in `CARD_TESTS.log` mean "not byte-identical to the
   release card executable" with the option absent. Sized (run
   core-20261119-141059-f3ccf56): every count of every collision step identical (no
   acceptance flipped), momenta within 2.1e-14 of max(1, |u|), starting in the first
   collision step; with sigma = 0 identical; each executable reproduces itself. Over 150
   M of the relativistic cluster in Z4c, `coll_energy = cell` collides the same pairs as
   the release in all 1200 steps and the central lapse stays within 7.8e-15 (run
   core-20261120-220420-63419ab). The processor executable is byte-identical to the
   release.
2. `coll_energy = particle` on the card in an evolving metric: cluster y_c = 0.819, Kn =
   3, collision cells of 2 M, 1e4 particles, 150 M (card run core-20261119-143232-4d1e995,
   analysis core-20261120-220159-7418482): sum M H of the collision steps changes by
   6.3e-17 in 5104 collisions (`cell`: +6.5e-5 in 5001); no pair without a root; 5 of 5109
   proposals rejected; against `cell`: collisions z = +1.0, central lapse within 2.8e-3,
   mass radii within 3 percent. Collisions at Kn = 3 lower the central lapse from 0.809
   to 0.79 over 150 M (without them it stays between 0.810 and 0.816). Card cost: 0.219 s
   per step against 0.218 s with `cell` (4.4 min per run of 150 M). Tolman gas on the
   card (1e6 particles, 85 collisions per particle): `particle` keeps the law to
   -0.21(6) percent, `cell` drifts to -3.67 percent (core-20261119-141051-b309a9f).
3. Your requests of wave 2b: the command-line rule (the deck must name `coll_energy`
   before the command line can set it) and your processor cost ratio 1.68 (run
   C-20261119-143146-226b0e0) are now in READY and in `collisions.md` section 11.5; the
   one-signed residual of the root tolerance (your run C-20261119-141431-a351ac7) is
   recorded there too, with the cluster's +1.2e-20 of the sum per collision; it is not
   changed in the source (this package opened no new work). Not done here, left for a
   later core package: the four format fixes, the ADM-mass diagnostic, collisions on
   refined meshes with a stop on non-finite state.
4. The crash of the first card build (2026-11-15) was stale objects of an incremental
   build; the published executables are clean builds and not affected (run
   core-20261119-141940-2e6368f).
