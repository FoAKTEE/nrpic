# Interface: threaded processor build (Kokkos OpenMP)

Owner: core (branch `core/build-openmp`, work package omp of wave 3a). Answers the requests
track/D-bh-dress `20261115T195036Z__to-core__openmp-cpu-build.md` and track/A-emd-pbh
`20261115T183714Z__to-core__processor-executable-threads.md`. Journal with predictions and
outcomes: `tracks/core/JOURNAL-omp.md`; scripts and figures: `tracks/core/omp/`.

Labels: [VERIFIED] read in the source of this tree or measured in a registered run (run id
given), [JUDGEMENT] a choice of this note, [TO VERIFY] not checked.

## 1. What exists

| Item | Where |
|---|---|
| Build script (the serial build `build_cpu.sh` is unchanged) | `scripts/build_cpu_omp.sh [dir]` = `scripts/_build.sh omp`: `Athena_ENABLE_OPENMP=ON`, `Kokkos_ENABLE_OPENMP=ON`, `Kokkos_ENABLE_SERIAL=OFF` (no kernel can fall back to the Serial space), g++ 11.4, `-O3 -DNDEBUG -g`, `Kokkos_ARCH_ICX`; `OMP_OPT=debug` gives the flags of the serial build (`-O2 -g`, asserts), `DEBUG=1` Kokkos debug mode with View bounds checking |
| Run helper | `scripts/cpu_run.sh <rundir> <athinput or .rst> [args]`: threads `THREADS` (default 16), placement `PLACES=auto` (default), a log like `gpu_run.sh` with the load of the machine and the share of processor time the run obtained |
| Placement | `scripts/omp_places.py N`: an `OMP_PLACES` list of the N least busy physical cores of one NUMA node, used with `OMP_PROC_BIND=true` |
| New option | `<particles> deposit_threads = atomic \| private` (section 3); read only if present |
| Published executables | `scratch/core/exe/core_build-openmp/` (`athena_cpu` threaded, `athena_cpu_serial`, `athena_gpu`; `COMMIT`, `SHA256SUMS`, `READY`) |

Source changes [VERIFIED: `git diff main..core/build-openmp -- athenak/src`]:
`particles/nrpic_threads.hpp` (new, 161 lines: the deposit target); `particles/particles.hpp`
(one include, one member `thread_dep`); `particles/nrpic.cpp` (one call in `NrpicInit`,
`Begin` before and `End` after the deposit kernel, the two `atomic_add` of the deposit
replaced by `dep.Add`); `parameter_input.cpp` (the second constructor initialised its
lock under a macro that does not exist, `OPENMP_PARALLEL`; now `OPENMP_PARALLEL_ENABLED`).
Without the option every build adds atomically exactly as before; the serial build gives
the files of release core-v0.3 byte for byte (section 4).

## 2. How to run

```text
OMP_NUM_THREADS=16 OMP_PROC_BIND=true OMP_PLACES=$(scripts/omp_places.py 16) \
    scratch/core/exe/core_build-openmp/athena_cpu -i deck.athinput
# or, with a log:
ATHENA_EXE=scratch/core/exe/core_build-openmp/athena_cpu THREADS=16 scripts/cpu_run.sh RUNDIR deck.athinput
```

- Rule of the machine: at most six cores per session (decision 0019; CLAUDE.md, section
  "Pause flag, restarts, load"), within the 16 at a time of the owner (decision 0006); set
  `OMP_NUM_THREADS` explicitly (the default of OpenMP is every hardware thread, 144). The
  examples above and the tables of 2026-11-19 below were written under the earlier limit
  of 16; `cpu_run.sh` now defaults to `THREADS=6`.
- Do not use `OMP_PLACES=cores` with `OMP_PROC_BIND=spread|close` on this machine: every
  job of every session is then bound to the same cores (0 to N-1, or 0, 4, 9, ...).
- Two runs started at the same moment must not each call `omp_places.py`: they pick the
  same cores (run core-20261119-160404-beddeac, stopped). Choose 2n cores once and split
  them (`tracks/core/omp/scaling_series.sh`, function `split4`).
- Runs are registered as usual (`nrpic-run submit --cores 6 --wait 1800 ...`: when the
  owner's cores are busy the run waits; it is not registered by hand).

## 3. The new option `deposit_threads`

`<particles> deposit_threads = atomic | private` (read only if present; absent gives the
behaviour and the parameter dump of release core-v0.3).

- `atomic` (default; the only way in the serial and card executables): every cloud corner
  is added with `Kokkos::atomic_add`. Correct under threads; the order of additions to one
  cell is free, so with deposition a threaded run repeats itself only to rounding.
- `private` (threaded executable only): every thread adds without atomics into its own copy
  of the source array; the copies are summed cell by cell in thread order after the
  deposit (`particles/nrpic_threads.hpp`). A run repeats itself byte for byte at a fixed
  thread count (east at 16 threads, run core-20261119-155057-57325bc/priv; example run
  core-20261119-160548-c46c55f). Cost [VERIFIED, run core-20261119-160710-c46c55f, 16
  threads]: the cosmology box (2.1e6 particles, PCS, 64^3) steps 10 to 14 per cent faster
  than with atomics (deposit 0.66 to 0.69 of its atomic time); the Newtonian box (5.1e5
  particles on 2.1e6 cells) steps 40 per cent slower (zeroing and summing 16 copies of the
  mesh). Memory: one source array (10 components, all cells with ghosts) per thread; the
  run prints its size (0.42 GiB at 4 threads for the 176-MeshBlock deposit test).
- The serial and card executables accept the option, print a note and add atomically.
- Example input: `problems/tests/deposit_threads.athinput` (the deposit test of
  `deposit_smr.athinput` with the option; particle file in its header).

## 4. What is tested, and what stays bit-identical

Regression set: 13 cases of `tracks/core/omp/omplib.py` (geodesics with two pushers, the
deposit on a refined mesh, the cosmology box with Z4c, Oppenheimer-Snyder collapse on a
refined mesh, gas with multigrid self-gravity on a uniform and on a refined mesh, the
Newtonian mode, Monte Carlo collisions, the scalar field with and without stochastic
sources, the Z4c benchmark, the vacuum puncture with tracers and horizon finder). Measure:
the largest difference over the largest number of each file (restart files on their data:
their headers hold uninitialised struct padding; mesh outputs on their data). Runs:
core-20261119-154940-1c3e906, core-20261119-155520-0bc529f, core-20261119-155057-57325bc,
core-20261119-155830-248f393 (journal entries 7 to 10; figure
`tracks/core/omp/figs/thread_diff.png`). Later tests: the card executable (run
core-20261119-164717-b187f36 analysed in core-20261120-220500-c759cdc, entry 16,
`figs/card_diff.png`), the cause of the multigrid's thread dependence (runs
core-20261120-223248-8a370f3 and core-20261121-030052-6acdca9, entries 18, 24, 27,
`figs/mg_cause.png`), restarts (run core-20261121-030132-89a7c84, entries 19, 27,
`figs/restart_threads.png`).

| Statement | Status |
|---|---|
| The serial build of this branch gives the files of release core-v0.3 byte for byte (option absent) | [VERIFIED] all 13 cases |
| Threaded, no deposit and no solver: every file byte-identical at 1, 4 and 16 threads (geo, boris) | [VERIFIED] |
| Threaded, Z4c and scalar field without particles: every evolved field (restart data, dumps, trajectories of the tracers, horizon output) byte-identical at 1, 4, 16 threads; history columns that are sums differ at 1e-14 | [VERIFIED] bench, punc, kg, noise |
| Threaded, collisions: every particle snapshot byte-identical at 1, 4, 16 threads (each collision cell sorts its list) | [VERIFIED] coll |
| Threaded, deposit (atomic): differences of rounding size, at most 1.3e-12 of the largest number of a file after the 3 to 40 steps of the cases; the conservation identity of the deposit stays at 1e-14 | [VERIFIED] dep, east, os, newton |
| Threaded, deposit (atomic): two runs at one thread count are not byte-identical in general (dep, east; os and newton at 16 threads) | [VERIFIED] |
| Threaded, `private`: two runs at one thread count byte-identical; against one thread at most 9.9e-13; with one thread equal to atomic in every datum | [VERIFIED] dep, east, os, newton |
| Gas multigrid and Newtonian mode: the solver iterates depend on the thread count (and, at one thread, on the MeshBlock size), reproducibly at a fixed count; results agree to the solver tolerance (Newtonian mode with `threshold = 0`: 1e-12 in the particles) | [VERIFIED] jeans, binary, newton |
| The cause of that dependence is the rounding of the plain sum of the volume mean (`Multigrid::CalculateAverage`, multigrid.cpp 763 to 815), which is subtracted from the source; there is no race in the solver. With the sum taken in a fixed order (a diagnostic executable outside the tree) every printed defect is the same at 1, 2, 4 and 6 threads and the 20-cycle Jeans case is byte-identical between 1 and 4 threads; with a compensated sum the two MeshBlock sizes also agree to seven digits and the Jeans solve no longer stagnates (defect falls 17.1 times per V cycle to 2.3e-11 after five, against floors of 6.6e-11 to 4.3e-9) | [VERIFIED] Jeans deck, MeshBlocks 8^3 and 32^3; not tested on the refined gas case or beyond six threads. The tree is unchanged (section 7) |
| Restarts under threads: a run continued from a restart file written half way equals the uninterrupted run in every datum (particle restart files, Newtonian state, snapshots byte for byte; MeshBlock data of the mesh restart files; history records) at one thread and at four threads with `private`; with atomic additions at four threads within 4.0e-15 of the largest number of a file | [VERIFIED] east (Z4c, 16^3), newton (32^3); not tested: refined meshes, collisions, a restart at another thread count |
| The card executable of this branch against one thread of the threaded executable: at most 5.8e-13 of the largest number of a file, deposit identity 1e-15 | [VERIFIED] dep, east (the only cases the card executable of this branch has run) |
| No View out of bounds under threads (Kokkos bounds checking, 4 threads, atomic and private) | [VERIFIED] dep, east, newton, coll |
| The threaded executable with one thread equals the serial build | NOT TRUE byte for byte (other compiler flags, -O3); rounding only (east, os: 1e-12) |
| MPI together with threads; refined meshes that change (adaptive) under threads; the horizon finder on many puncture runs | [TO VERIFY] not tested |

Audit of the source (journal entry 6): every kernel of the particle module, the scalar
field and the problem generators of this branch was read for writes that two iterations
share. The only one is the deposit scatter (atomic or private); the collision cell lists
are filled with `atomic_fetch_add` and sorted per cell; reductions group by thread.
The only host defect found (ParameterInput lock) is fixed.

## 5. Speed

Two series; every time is the step loop over the cycles, best of the repeats; threads on
the least busy cores of one NUMA node (`omp_places.py`). Table
`tracks/core/omp/scaling_table.md`, figure `tracks/core/omp/figs/scaling.png`.

Series of 2026-11-19, loaded machine (runs core-20261119-154725-1c3e906 (1 thread),
core-20261119-154729-1c3e906 (serial build), core-20261119-163647-53000b7 (4),
core-20261119-161025-820e057 (16), core-20261119-162248-f2f3758 (32),
core-20261119-163017-11fe2fd (64); load average 97 to 157 of 144 hardware threads from
other sessions throughout). Seconds per step:

| case | 1 thread | 4 | 16 | 32 | 64 | serial build | speed-up at 16 |
|---|---|---|---|---|---|---|---|
| punc: vacuum puncture, refined mesh (1.41e6 cells), tracers, horizon finder | 203 | 44.6 | 14.3 | 8.14 | 6.45 | 243 | 14.2 |
| cluster: 1e5 particles, Z4c, refined mesh (1.64e6 cells) | 243 | 55.3 | 18.5 | 10.0 | 7.33 | 294 | 13.2 |
| cosmo: 64^3 periodic box, 2.1e6 particles, PCS, compensation | 94.3 | 23.3 | 6.86 | 3.68 | 2.69 | 114 | 13.8 |
| newton: Newtonian mode, 128^3 periodic, 5.1e5 particles, multigrid | 10.6 | 2.14 | 0.819 | 0.478 | 0.680 | 11.6 | 13.0 |

The ratios of that day stand (13 to 14 at 16 threads, 22 to 26 at 32); its absolute times
do not describe a quiet machine: the one-thread runs of 2026-11-20 are 1.5 to 2.6 times
faster. Above 32 threads the machine was oversubscribed (the 64-thread runs obtained 52
to 71 per cent of their processor time). Bound to cores chosen by `omp_places.py` the
step time is within 7 per cent of unbound runs at 16 threads (run
core-20261119-150022-d0d8641, `figs/placement.png`).

Series of 2026-11-20, quieter machine (load average 11 to 56), one and six threads, six
being the limit per session since decision 0019 (runs core-20261120-220756-0eaaf74,
core-20261121-025720-29ecba0, core-20261121-030310-46d891c, core-20261121-031150-04a2d5b;
journal entries 21, 26, 28, 29). Seconds
per step, and one A100 for the same decks (run core-20261119-144437-6718c76, Slurm 4643,
release card executable, best of two; the isolated collapse from the card log of run
core-20261115-120028-fee90ca):

| case | 1 thread | 6 threads | six over one | one A100 | card over six threads | card memory (MiB) |
|---|---|---|---|---|---|---|
| punc | 90.8 | 15.7 | 5.8 | 0.175 (8.07e6 zone-cycles/s) | 90 | 9191 |
| cluster | 115.9 | 20.1 | 5.8 | 0.279 (5.88e6 zone-cycles/s) | 72 | 12295 |
| cosmo | 48.6 | 8.86 | 5.5 | 0.119 (1.76e7 particle updates/s) | 74 | 1787 |
| newton, periodic | 4.11 | 0.929 | 4.4 | 0.0779 | 11.9 | 1563 |
| collapse: Newtonian mode, isolated boundaries, 128^3, 137 376 particles | 2.23 | 0.409 | 5.4 | 0.650 | 0.63 | not logged |

- Every time is the best of that day's runs. One thread: four runs side by side on one
  socket in the afternoon (131.9, 115.9, 49.05, 4.61) and each case alone in the evening
  (90.8, 116.1, 48.6, 4.11). With the afternoon's one-thread run the Newtonian box is 5.0
  times faster at six threads, with the evening's 4.4. Ratios between runs hours apart
  carry the change of the load (11 to 56 over the day).
- The afternoon's six-thread run of the puncture case was 7.9 times its one-thread run,
  more than the number of threads. Measured again in the evening, alone and back to
  back, one thread needs 90.8 s per step and six threads 15.7 and 17.2: 5.3 to 5.8. The
  7.9 came from a one-thread run that was held back in the afternoon (131.9 s per
  step), not from the case (run core-20261121-030310-46d891c, journal entry 28). What
  held it back is not known: the cluster case, measured the same way, is as fast alone
  as side by side (116.1 against 115.9; run core-20261121-031150-04a2d5b), so it is not
  a general cost of running one-thread jobs side by side.
- One A100 against 16 threads of the loaded day: 82 (punc), 66 (cluster), 57 (cosmo),
  10.5 (newton); the Z4c benchmark (uniform 128^3) runs at 1.85e7 zone-cycles/s on the
  card (0.113 s per step, 4373 MiB).
- The Newtonian mode splits. Periodic box: the card is 11.9 times six threads. Isolated
  boundaries: six threads are 1.6 times faster than the card's logged 0.65 s per step,
  because the multipole sums of the boundary run on the host
  (`tracks/core/interfaces/newtonian_mode.md`, section 2); the card was not run again on
  the same day and the steps here took 10 to 12 V cycles against the 13 logged there.

Kernel profile at 16 threads (`figs/kernels.png`, run core-20261119-150956-abda48c): the
puncture and the cluster spend 55 to 63 per cent of the kernel time in the Z4c right-hand
side; the cosmology box 38 per cent in the deposit and 25 per cent in the push; the
Newtonian box spreads over multigrid, deposit and push. Why Z4c is so much slower on
processors [JUDGEMENT, not profiled further]: the right-hand side is one large kernel per
cell written for the cards (no vectorisation over cells in this build); one thread
reaches 6.7e3 (serial build) to 1.1e4 (this build) zone-cycles/s on the loaded machine.

## 6. Which runs are now cheaper on processors than waiting for a card

A run of N steps is done sooner on six threads than on a card it has to wait W for when
N t6 < W + N tc, i.e. N < W/(t6 - tc), with t6 and tc the seconds per step on six threads
and on one card. The two card jobs of this package waited 2 h 11 min and 3 h 15 min
(Slurm 4643 and 4666); with W = 2 h and 3 h and the times of section 5:

| Kind of run (measured deck) | t6 (s) | tc (s) | Sooner on six threads below | Card time of that run |
|---|---|---|---|---|
| Z4c in vacuum on a refined mesh of 1.4e6 cells (puncture, tracers, horizon finder) | 15.7 | 0.175 | 460 to 700 steps | 1.4 to 2.0 min |
| Z4c with 1e5 particles on a refined mesh of 1.6e6 cells (cluster) | 20.1 | 0.279 | 360 to 540 steps | 1.7 to 2.5 min |
| Z4c with 2.1e6 particles on 64^3 (cosmology box, PCS, compensation) | 8.86 | 0.119 | 820 to 1240 steps | 1.6 to 2.5 min |
| Newtonian mode, periodic, 128^3, 5.1e5 particles | 0.929 | 0.0779 | 8500 to 12 700 steps | 11 to 17 min |
| Newtonian mode, isolated boundaries, 128^3, 1.4e5 particles | 0.409 | 0.650 | any length | (six threads are faster) |

What follows for the tracks:
- Runs with Z4c: only short ones (tests, convergence checks at 16^3 to 64^3, the first
  few hundred steps of a new set-up) belong on processors; anything longer stays on the
  cards, which are 72 to 90 times six threads. Track A's dx = M scouting at 128^3:
  about 23 s per step on six threads [JUDGEMENT: the zone-cycle rate of the puncture
  case, 9.0e4 per second, applied to 2.1e6 cells] against about 0.1 s on a card, so
  fewer than about 310 to 470 steps.
- Newtonian mode, periodic (Track D's infall runs are of the measured size; Track A's and
  B's Newtonian references): a long run belongs on a card, which is 11.9 times six
  threads; runs below about a quarter of an hour of card time (about 10^4 steps at
  128^3) are done sooner on six threads. The statement of 2026-11-19 "Newtonian mode:
  always on processors, a card is not faster" was WRONG for periodic boxes (it rested on
  the card log of the isolated case and on a transferred speed-up) and is withdrawn.
- Newtonian mode with isolated boundaries: processors, at any length.
- Particles in an analytic or static metric (collision boxes, geodesics, deposit tests)
  and the scalar field without particles were NOT measured on a card. The statement of
  2026-11-19 "always on processors" for them is withdrawn as unmeasured; the cosmology
  box, where push and deposit are most of the processor time, is 74 times faster on a
  card than on six threads. Use the rule: time a few steps on six threads; if the whole run then takes less
  than the wait in the queue, run it on processors.

Rules: a processor run is a registered run like any other (`nrpic-run submit --cores 6
--wait S`; when nrpic-run refuses because the owner's cores are busy, the run waits; it
is not registered by hand and does not go above the allotment). Use `athena_cpu` with
`OMP_NUM_THREADS=6` and the placement of section 2; use `deposit_threads = private` when
a run must repeat itself byte for byte at a fixed thread count; compare a processor run
with a card run, or with a run at another thread count, at rounding (deposit) or
solver-tolerance (multigrid) level, never byte for byte.

## 7. Open, and proposed to core's lead

- Not tested: MPI together with threads; adaptive refinement under threads; restarts
  of refined meshes or of runs with collisions under threads; unbound placement at 32
  and 64 threads; the card executable of this branch beyond the two deposit cases.
- Proposal (not done; it changes results at rounding level, so it needs a decision): an
  option that makes `Multigrid::CalculateAverage` sum in a fixed order with compensation
  (the diagnostic patch `tracks/core/omp/tools/mg_average_diag.patch` shows the change: about
  70 added lines in `multigrid.cpp`, one helper and one branch in that function). It would make gas self-gravity and the Newtonian mode with the
  multigrid solver independent of the thread count and of the MeshBlock size in the
  Jeans test, and remove the stagnation of that solve.
- AthenaK restart files hold uninitialised padding bytes in their header
  (outputs/restart.cpp 225 to 229): compare restart files on their data
  (`tracks/core/omp/omplib.py`, `_rst_data`), never byte for byte across processes.

## 8. In release candidate core-v0.5 (lead of core, 2026-11-21)

Merged into `core/nrpic` as 0d0f5ba5; the threaded executable of the release is
`scratch/core/exe/core_nrpic_v05/athena_cpu_omp` (source c3eb42e0, built with
`scripts/build_cpu_omp.sh`). Added by the merges that followed:

- The fine-shape branch of the deposit kernel (`<particles> deposit_fine_shape` of
  core/cosmo-amr) adds through the deposit target as the two other branches do. Tested
  with the refined deposit test (run core-20261121-065009-29b855c, judged in
  core-20261121-065726-bf06a85): two runs at 4 threads with `private` byte-identical;
  4 threads against 1: 1.1e-18 (history) and 2.1e-16 (source dump in double precision)
  of the largest number; atomic at 4 threads 3.6e-16; identity 3.0e-14.
- With several MPI ranks the private copies are summed before the clouds of other ranks
  are added. Not run.
- The threaded build at ONE thread does not give the bits of the serial build: source
  dump 1.1e-14 of its largest number in the deposit test (the two builds differ in
  optimisation level). On the twelve regression set-ups at one thread 31 of 75 items
  are identical to release core-v0.4 and 44 differ at rounding (module histories
  1.2e-15; run core-20261121-070623-077b056). Built with the flags of the serial build
  (`OMP_OPT=debug`), 53 of 75 are identical: the nine set-ups without Z4c agree byte
  for byte, the three with Z4c do not (run core-20261121-071842-f5a8b56). Byte
  comparisons against a release need the serial executable (or the MPI one started
  without mpirun); no threaded build is a byte reference.
- The kernels that release core-v0.4 added (accretion diagnostics, initial-data solver,
  perturbing force, collisions with the metric at each particle) have not been run
  under threads; they run on cards [JUDGEMENT: no host-only state].
