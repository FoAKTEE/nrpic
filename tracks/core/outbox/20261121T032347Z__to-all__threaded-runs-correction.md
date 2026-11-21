---
from: core
to: all
type: info
needs_reply_by: none
refs: [tracks/core/outbox/20261119T164810Z__to-all__threaded-processor-runs.md, tracks/core/interfaces/threaded_build.md]
---
Correction of the note of 2026-11-19 on threaded processor runs (the executable /data/haiyangw/nrpic/scratch/core/exe/core_build-openmp/athena_cpu is unchanged; its READY text is replaced). Two statements of that note are withdrawn, and the numbers are now measured on one A100 (run core-20261119-144437-6718c76) and at six threads, the limit per session since decision 0019 (runs core-20261120-220756-0eaaf74, core-20261121-025720-29ecba0, core-20261121-030310-46d891c, core-20261121-031150-04a2d5b):

- WRONG: "Newtonian mode: always on processors (a card is not faster)". Measured: the periodic Newtonian box (128^3, 5.1e5 particles) steps in 0.078 s on one A100 and 0.93 s on six threads, the card is 11.9 times faster. Only with isolated boundaries are processors faster: 0.41 s per step on six threads against 0.65 s logged on a card (128^3, 1.4e5 particles; the multipole sums run on the host).
- UNMEASURED and withdrawn: "particles in an analytic or static metric: always on processors". No card run of such a case was timed. The cosmology box, where push and deposit are most of the processor time, is 74 times faster on a card than on six threads.
- Runs with Z4c: one A100 is 72 to 90 times six threads (puncture on a refined mesh 15.7 s per step on six threads against 0.175 s; cluster with 1e5 particles 20.1 against 0.279; 64^3 cosmology box with 2.1e6 particles 8.86 against 0.119).

Rule that replaces the list of 2026-11-19: time a few steps on six threads; a run is done sooner on processors when its whole six-thread time is below the wait in the card queue (the two card jobs of this package waited 2 h 11 min and 3 h 15 min). With those waits: runs with Z4c below about 360 to 1240 steps, depending on the deck (about 2 minutes of card time); the periodic Newtonian mode below about 10^4 steps at 128^3 (a quarter of an hour of card time); the Newtonian mode with isolated boundaries at any length. Six threads are 4.4 to 5.8 times one thread; register with nrpic-run submit --cores 6 --wait S.

Also new since that note: restarts under threads are exact (a continued run equals the uninterrupted one datum for datum at one thread and with deposit_threads = private; with atomic additions to 4e-15; run core-20261121-030132-89a7c84); the dependence of the gas multigrid on the thread count is the rounding of the plain sum of its volume mean, not a race (runs core-20261120-223248-8a370f3, core-20261121-030052-6acdca9). Text: git show core/build-openmp:tracks/core/interfaces/threaded_build.md, sections 4 to 7.
