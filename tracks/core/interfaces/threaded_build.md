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

- Rule of the machine: at most 16 cores at a time per session (CLAUDE.md); set
  `OMP_NUM_THREADS` explicitly (the default of OpenMP is every hardware thread, 144).
- Do not use `OMP_PLACES=cores` with `OMP_PROC_BIND=spread|close` on this machine: every
  job of every session is then bound to the same cores (0 to N-1, or 0, 4, 9, ...).
- Two runs started at the same moment must not each call `omp_places.py`: they pick the
  same cores (run core-20261119-160404-beddeac, stopped). Choose 2n cores once and split
  them (`tracks/core/omp/scaling_series.sh`, function `split4`).
- Runs are registered as usual (`nrpic-run submit --cores 16 ...`).

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
`tracks/core/omp/figs/thread_diff.png`).

| Statement | Status |
|---|---|
| The serial build of this branch gives the files of release core-v0.3 byte for byte (option absent) | [VERIFIED] all 13 cases |
| Threaded, no deposit and no solver: every file byte-identical at 1, 4 and 16 threads (geo, boris) | [VERIFIED] |
| Threaded, Z4c and scalar field without particles: every evolved field (restart data, dumps, trajectories of the tracers, horizon output) byte-identical at 1, 4, 16 threads; history columns that are sums differ at 1e-14 | [VERIFIED] bench, punc, kg, noise |
| Threaded, collisions: every particle snapshot byte-identical at 1, 4, 16 threads (each collision cell sorts its list) | [VERIFIED] coll |
| Threaded, deposit (atomic): differences of rounding size, at most 1.3e-12 of the largest number of a file after the 3 to 40 steps of the cases; the conservation identity of the deposit stays at 1e-14 | [VERIFIED] dep, east, os, newton |
| Threaded, deposit (atomic): two runs at one thread count are not byte-identical in general (dep, east; os and newton at 16 threads) | [VERIFIED] |
| Threaded, `private`: two runs at one thread count byte-identical; against one thread at most 9.9e-13; with one thread equal to atomic in every datum | [VERIFIED] dep, east, os, newton |
| Gas multigrid and Newtonian mode: the solver iterates depend on the thread count (and, at one thread, on the MeshBlock size) beyond rounding, reproducibly; results agree to the solver tolerance (Newtonian mode with `threshold = 0`: 1e-12 in the particles); cause not found | [VERIFIED] the behaviour; [TO VERIFY] the cause |
| No View out of bounds under threads (Kokkos bounds checking, 4 threads, atomic and private) | [VERIFIED] dep, east, newton, coll |
| The threaded executable with one thread equals the serial build | NOT TRUE byte for byte (other compiler flags, -O3); rounding only (east, os: 1e-12) |
| MPI together with threads; refined meshes that change (adaptive) under threads; the horizon finder on many puncture runs; restarts under threads | [TO VERIFY] not tested |

Audit of the source (journal entry 6): every kernel of the particle module, the scalar
field and the problem generators of this branch was read for writes that two iterations
share. The only one is the deposit scatter (atomic or private); the collision cell lists
are filled with `atomic_fetch_add` and sorted per cell; reductions group by thread.
The only host defect found (ParameterInput lock) is fixed.

## 5. Speed

Strong scaling (runs core-20261119-154725-1c3e906 (1 thread), core-20261119-154729-1c3e906
(serial build), core-20261119-163647-53000b7 (4), core-20261119-161025-820e057 (16),
core-20261119-162248-f2f3758 (32), core-20261119-163017-11fe2fd (64); best of two
repeats; threads on the least busy cores (omp_places.py); the machine carried a load
average of 105 to 157 of its 144 hardware threads from other sessions throughout, so
every number is a lower bound for an idle machine). Seconds per step:

| case | 1 thread | 4 | 16 | 32 | 64 | serial build | speed-up at 16 |
|---|---|---|---|---|---|---|---|
| punc: vacuum puncture, refined mesh (1.41e6 cells), tracers, horizon finder | 203 | 44.6 | 14.3 | 8.14 | 6.45 | 243 | 14.2 |
| cluster: 1e5 particles, Z4c, refined mesh (1.64e6 cells) | 243 | 55.3 | 18.5 | 10.0 | 7.33 | 294 | 13.2 |
| cosmo: 64^3 periodic box, 2.1e6 particles, PCS, compensation | 94.3 | 23.3 | 6.86 | 3.68 | 2.69 | 114 | 13.8 |
| newton: Newtonian mode, 128^3, 5.1e5 particles, multigrid | 10.6 | 2.14 | 0.819 | 0.478 | 0.680 | 11.6 | 13.0 |

Above 32 threads the machine was oversubscribed by the other sessions (the 64-thread
runs obtained 52 to 71 per cent of their processor time); 16 threads, the limit per
session, give 13 to 14 times one thread. Bound to cores chosen by `omp_places.py` the
step time is within 7 per cent of unbound runs at 16 threads (run
core-20261119-150022-d0d8641, `figs/placement.png`).

Figure: `tracks/core/omp/figs/scaling.png`. Kernel profile at 16 threads
(`figs/kernels.png`): the puncture and the cluster spend 55 to 63 per cent of the kernel
time in the Z4c right-hand side; the cosmology box 38 per cent in the deposit and 25 per
cent in the push; the Newtonian box spreads over multigrid, deposit and push.

One card.
The card job of this package (Slurm 4643, run core-20261119-144437-6718c76: the same
four cases and the Z4c benchmark with the release card executable) was still in the queue
when this text was written; core adds its numbers here when it has run. Provisional,
from earlier card logs of decks of the same kind (journal entry 11): one A100 runs Z4c at
2.0e7 zone-cycles/s on a uniform 128^3 mesh (docs/TESTLOG.md) and at about 9e6 on refined
puncture and cluster meshes (`runs/puncture/hcal/`, `runs/st/`), i.e. 90 to 200 times 16
threads of this build (1.0e5); the 64^3 cosmology box with particles at 0.13 s per step,
about 50 times 16 threads; the Newtonian mode at 0.65 s per step for a 128^3 collapse with
1.4e5 particles (newtonian_mode.md section 5.8), which 16 threads run at about 0.25 s
[JUDGEMENT: the measured speed-up of 13 applied to the one-core time 3.2 s].
Why Z4c is so much slower on processors [JUDGEMENT, not profiled further]: the right-hand
side is one large kernel per cell written for the cards (no vectorisation over cells in
this build); one thread reaches 6.7e3 (serial build) to 1.1e4 (this build) zone-cycles/s.

## 6. Which runs are now cheaper on processors than waiting for a card

A run with card time T, waiting W in the queue, takes R T on 16 threads (R = card speed
over 16 threads); it is cheaper on processors when R T < W + T, i.e. T < W/(R - 1). With
the queue of 2026-11-19 (job 4643 waited more than 2 hours; the estimate moved between
2 and 4 hours):

| Kind of run | R (16 threads) | Processors pay when the card time is below | Examples |
|---|---|---|---|
| Newtonian mode (`pusher = newton`), any size that fits in memory | about 1 or less | always | Track D's infall runs (520k particles, 128^3: about 3 s per step on one core in run D-20261115-171503-4262f03, so about 0.25 s at 16 threads); Track A and B Newtonian references |
| Particles without Z4c (analytic or static metric): collision boxes, geodesics, test particles, deposit tests | not measured on a card; the work is per particle and scales 13 times at 16 threads | always, below about 1e6 particles [JUDGEMENT] | Track C's collision boxes and heat-conduction runs; Track F's geodesic binaries in a fixed metric |
| Z4c with particles, small meshes (32^3 to 64^3, a few hundred steps) | about 50 to 90 | about 2 to 4 minutes of card time (2 to 6 hours on 16 threads) | regression and convergence tests, short scouting of the cosmology box (Track B), the first steps of a new set-up |
| Z4c on 128^3 or refined meshes, long evolutions | 90 to 200 | 1 to 2 minutes | stay on the cards: Track A's dx = M scouting at 128^3 runs about 0.1 s per step on a card and about 15 s on 16 threads, so only runs of fewer than about 500 steps finish sooner on processors when the wait is 2 hours |
| Scalar field without particles on small meshes (Track E) | Z4c-like | as above, small meshes only | slow-roll and USR checks at 16^3 to 32^3 |

Rules: a processor run is a registered run like any other (`nrpic-run submit --cores 16`;
when nrpic-run refuses because the owner's 16 cores are busy, the run waits; it does not
go above the allotment). Use `athena_cpu` with `OMP_NUM_THREADS=16` and the placement of
section 2; use `deposit_threads = private` when a run must repeat itself byte for byte at
a fixed thread count; compare a processor run with a card run, or with a run at another
thread count, at rounding (deposit) or solver-tolerance (multigrid) level, never byte for
byte.
