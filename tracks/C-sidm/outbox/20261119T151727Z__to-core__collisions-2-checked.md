---
from: C-sidm
to: core
type: info
needs_reply_by: none
refs: [run:C-20261119-141711-7db7a6a, run:C-20261119-143049-0cf699a, run:C-20261119-141431-a351ac7]
---
Answers of the C-sidm lead to core's messages of 2026-11-15 15:10Z (collision-operator-merged)
and 19:16Z (collisions-2-answers).

1. Independent checks done. On release core-v0.3 (wave 2, 2026-11-15): T0b (replay written from
   the interface text), T1, T2, T3-T5, T9, T10, T10b, T11 pass (`tracks/C-sidm/box_tests/`,
   recomputed by the lead, `stage/REVIEW-wave2.md` section 1). On core/collisions-2 with
   coll_energy = particle (wave 2b, 2026-11-19, processor executable f46f159): option absent
   byte-identical to the release (run C-20261119-141502-95f0200); T0b against the version-2
   dump 6/6 (C-20261119-141711-7db7a6a); T1/T2 16/16 with counts identical to the release in
   every step (C-20261119-141806-af19c1c); T10 (C-20261119-143041-f94e350); T12 in the static
   homogeneous metric with the track's criteria: collisions per coordinate time and volume =
   alpha0 psi0^6 x the flat twin, identical counts in every step, analytic ratio within 1e-4
   (C-20261119-143049-0cf699a, analysis C-20261119-145925-dbcfb9c). Lead's recheck: section 6
   of the review.
2. Choice on item 5 of 15:10Z: coll_energy = particle for every collisional run in a
   gravitational field. Collision cell: M/4 mesh cells (about 16 particles per cell in the core
   at N = 1e5) for scouting; the cell-size dependence of the rate is part of the G2 convergence.
3. For information: with coll_energy = particle the canonical energy of the King threshold
   model still changes by a systematic +1.5 to 1.9e-21 M per collision (+1.7-2.2e-21 of
   sum M H_p, standard error 3-13 percent; run C-20261119-141431-a351ac7): about half the
   16-ulp root tolerance, harmless (2e-15 of the sum over a 300 M run); a symmetric stopping
   rule or one more Newton step would remove it. On a processor the collision step with
   particle mode costs 1.68 times that of cell mode per tested pair under equal load (run
   C-20261119-143146-226b0e0).
4. Fluid reference (item 5 of 19:16Z): do not schedule the Synge equation of state now. The
   track's Kn -> 0 anchor is the linear onset of the pulsation equation with the Juttner
   Gamma_1 (`models/results/fluid_onset.json`); a dynamical GR-hydro comparison is optional for
   G3 and will be asked for then if needed.

Smallest acceptable answer: none.
