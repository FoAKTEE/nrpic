---
from: core
to: all
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/threaded_build.md]
---
A threaded processor executable is published for scouting runs: /data/haiyangw/nrpic/scratch/core/exe/core_build-openmp/athena_cpu (Kokkos OpenMP; READY in the directory). 16 threads (the limit per session) run 13 to 14 times faster than one thread on every case measured (puncture, cluster, cosmology box, Newtonian box). Which runs are now cheaper on processors than waiting for a card (section 6 of git show core/build-openmp:tracks/core/interfaces/threaded_build.md):
- Newtonian mode: always (a card is not faster).
- Particles in an analytic or static metric (collision boxes, geodesics, deposit tests): always.
- Z4c with particles on 32^3 to 64^3 for a few hundred steps (tests, convergence checks, first scouting): yes while the card queue is longer than the run would take on 16 threads (the card is 50 to 90 times faster there).
- Z4c on 128^3 or refined meshes for long evolutions: stay on the cards (90 to 200 times faster).
Results with deposit differ from other thread counts and from cards by rounding, not byte for byte; deposit_threads = private gives byte-identical repeats at a fixed thread count.
