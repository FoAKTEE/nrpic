---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-12-10
refs: [run:C-20261115-171058-c26cfad, run:C-20261115-171059-4b70228, run:C-20261115-171059-35441e3]
---
Request from the C-sidm lead: collisions on a refined mesh, and a stop on non-finite state in
nrpic_cf runs.

1. Collisions with static or adaptive refinement: collisions.md section 9 lists them as
   untested on refined meshes; the track's collapse runs need the black hole resolved after
   the collapse (on the static M/4 mesh the state turned non-finite at 162-290 M after the
   collapse, runs C-20261115-171058-c26cfad, -171059-4b70228, -171059-35441e3). Asked: a test
   of the operator on a mesh with refinement (cells of different size in one run; collision
   cells never straddling a level boundary, or the rule if they do), stated in the interface.
2. A run whose state turns non-finite exits with status 0 (core G2 OPEN item 11; seen in
   cc1_kn1, cc2_kn1, cc1_kn10). The cosmo-amr package of wave 3a adds a stop for periodic
   runs; asked: the same stop (non-zero exit, message naming the cycle) for every problem
   generator, nrpic_cf included.

Smallest acceptable answer: the branch and test run ids for each item, or a date.
