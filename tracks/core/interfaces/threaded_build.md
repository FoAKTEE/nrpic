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
| Threaded, `private`: two runs at one thread count byte-identical; against atomic at most PRIVMAX | [VERIFIED] dep, east, os, newton |
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
(serial build), T4RUN (4), core-20261119-161025-820e057 (16),
core-20261119-162248-f2f3758 (32), core-20261119-163017-11fe2fd (64); best of two
repeats; threads on the least busy cores (omp_places.py); the machine carried a load
average of 105 to 157 of its 144 hardware threads from other sessions throughout, so
every number is a lower bound for an idle machine). Seconds per step:

SCALINGTABLE

Figure: `tracks/core/omp/figs/scaling.png`. Kernel profile at 16 threads
(`figs/kernels.png`): the puncture and the cluster spend 55 to 63 per cent of the kernel
time in the Z4c right-hand side; the cosmology box 38 per cent in the deposit and 25 per
cent in the push; the Newtonian box spreads over multigrid, deposit and push.

One card. CARDTEXT

## 6. Which runs are now cheaper on processors than waiting for a card

ADVICE
