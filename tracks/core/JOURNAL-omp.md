# Journal of work package omp (core, wave 3a): a threaded processor build

Branch `core/build-openmp`, worktree `wt/core-omp`. Times are local (PST) from `date`.
Requests answered: track/D-bh-dress `20261115T195036Z__to-core__openmp-cpu-build.md`,
track/A-emd-pbh `20261115T183714Z__to-core__processor-executable-threads.md`.
Package directory (scripts, figures): `tracks/core/omp/`. Interface text:
`tracks/core/interfaces/threaded_build.md`.

## 2026-11-19 06:22 Entry 0: state at the start, plan

- `git merge --no-edit main`: already up to date (27b2ced9). The source of this branch is
  the source of release core-v0.3; core's wave-2 branches are not on main yet, so the
  audit below covers the kernels of core-v0.3 only. [VERIFIED: git log]
- The two processor executables that exist (`.work/build_cpu_v03`, the `athena_cpu` files
  under `scratch/core/exe/`) are Kokkos Serial builds: `scripts/_build.sh` passes
  `-DAthena_ENABLE_OPENMP=OFF -DKokkos_ENABLE_SERIAL=ON`. [VERIFIED: scripts/_build.sh]
- Machine: 2 sockets x 36 cores x 2 hardware threads (Xeon 8360Y), NUMA node 0 = CPUs
  0-35 and 72-107, node 1 = CPUs 36-71 and 108-143 (`lscpu`). At 06:27 the load average
  was 141 (builds and runs of the other sessions): timings have to be taken as the best
  of several repeats and reported with the load at the time. [VERIFIED: lscpu, uptime]
- Rule that binds the runs: 16 cores at a time per owner (decision 0006; `nrpic-run`
  refuses more). The task names 32 and 64 threads for the scaling series; those runs are
  short (a minute or two each), registered by hand with `tracks/core/tools/
  run_registered.py` because `nrpic-run` refuses them, and marked as such.

Build: `scripts/build_cpu_omp.sh [dir]` = `_build.sh omp`: `Athena_ENABLE_OPENMP=ON`
(sets `Kokkos_ENABLE_OPENMP`, `OPENMP_PARALLEL_ENABLED 1` in config.hpp),
`Kokkos_ENABLE_SERIAL=OFF` (so that no kernel can name the Serial space and still
compile), g++ 11.4, `-O3 -DNDEBUG -g`; `OMP_OPT=debug` gives the flags of the serial
build (`-O2 -g`, asserts kept). First build of the unchanged source: 169 s at 16 jobs,
no warning from the particle module. [VERIFIED: .work/build_omp/build.log]

## 2026-11-19 06:30 Entry 1: what Kokkos OpenMP does with the kernels (read from the source)

[VERIFIED: athenak/kokkos/core/src/OpenMP/Kokkos_OpenMP_Parallel_{For,Reduce,Scan}.hpp,
athenak/src/athena.hpp lines 236-362]
- Every `par_for` of AthenaK is a `Kokkos::parallel_for` over a flattened one-dimensional
  `RangePolicy<DevExeSpace>`; with OpenMP the range is cut into one contiguous chunk per
  thread (`schedule(static)`; dynamic only for a policy tagged `Schedule<Dynamic>`, which
  the code never uses).
- `parallel_reduce`: one partial result per thread over its chunk, joined in thread
  order. For a fixed number of threads the result is the same from run to run; it differs
  from the serial sum in the last bits (other grouping of the additions) and so depends
  on the number of threads.
- `parallel_scan`: two passes, order preserved; integer scans (the only ones in the
  particle module) are exact.
- `Kokkos::atomic_add` on a `double` is a compare-and-swap loop: correct under threads,
  but the order in which two threads add to one cell is not fixed. This is the one place
  where a threaded run can differ from itself.
- `DevExeSpace` and `HostExeSpace` are both OpenMP in this build, `DevMemSpace` is
  `HostSpace`: device and host views of a DualView alias, as in the serial build.

## 2026-11-19 06:35 Entry 2: predictions, written before any threaded run

Executables: S = serial build of this branch (`.work/build_cpu`), R = release
`.work/build_cpu_v03`, O3 = threaded build with `-O3 -DNDEBUG`, O2 = threaded build with
the flags of S (`OMP_OPT=debug`). Regression set-ups: the five cases of
`tracks/core/tools/regress_relativistic.py` (geo, boris, dep, east, os) plus the two
gravity cases (jeans, binary) and a Newtonian-mode case and a collision box.

P0 (serial regression). S gives the files of R byte for byte in all cases, whatever is
   changed in the source for the threaded build. Refuted by any differing file.
P1 (one thread). O2 with `OMP_NUM_THREADS=1` gives the files of S byte for byte in all
   cases: same flags, same order of every sum. Refuted by any differing file.
   O3 with one thread may differ from S in the last bits wherever the compiler contracts
   or vectorises differently; expected size of the differences: rounding (below 1e-12
   relative after the 3 to 2000 steps of the cases). Not a prediction of identity.
P2 (threads, no deposit and no reduction that feeds back). geo and boris (one test
   particle in an analytic metric) are byte-identical to S at 4 and 16 threads with O2.
   Refuted by any differing file; a difference would mean a race in the push or in the
   output path.
P3 (threads with deposit). dep (10^4 particles, static flat metric on a refined mesh): the
   particles do not feel the deposit, so trajectories and snapshots are byte-identical;
   the deposited sums in the history (`sum_mW`, `int_E`, `int_S`) differ from S by
   rounding, below 1e-13 relative. east (16^3 periodic box with Z4c, filter,
   compensation, 20 steps) and os (ball on a refined mesh, 3 steps): every output differs
   from S, by an amount that starts at 1e-16 relative and stays below 1e-10 relative in
   fields and particle coordinates over these few steps (the card runs of
   scripts/README.md show 1e-16 growing to 1e-13). Refuted by a difference above 1e-8
   relative (that would be a lost update, not rounding), by NaN, or by a different number
   of particles.
P4 (repeatability). Two runs of O2 at the same thread count: byte-identical for geo,
   boris (no deposit) and for the Z4c benchmark without particles; NOT byte-identical for
   dep, east, os at 4 and 16 threads, because of the order of the atomic additions; the
   two runs differ by the same small amount as in P3. If a deposit that keeps one copy of
   the source array per thread is added (see entry on the deposit below), runs at a fixed
   thread count become byte-identical; they still differ between thread counts.
P5 (reductions that feed back). `dt_expansion > 0` (step from a mesh sum of alpha K),
   the Newtonian mode on a periodic mesh (mean of the potential subtracted) and the
   multigrid defect norm make the evolution depend on the grouping of a sum: such runs
   are repeatable at a fixed thread count but differ between thread counts at rounding
   level even without deposit.
P6 (strong scaling; three cases, threads 1, 4, 16, 32, 64, `OMP_PROC_BIND=spread
   OMP_PLACES=cores`). Speed-up over one thread of the same executable: 3.3 to 3.9 at 4,
   10 to 14 at 16, 16 to 24 at 32, 22 to 40 at 64 threads for the vacuum puncture (the
   Z4c right-hand side is local work per cell; the mesh arrays exceed the caches, so the
   memory bandwidth of two sockets limits the top); 10 to 30 per cent less for the cluster
   (10^5 particles: the push is local work, the deposit pays for atomics, the horizon
   finder and the outputs are serial) and for the 64^3 box (small mesh: 2.6e5 cells,
   several kernels of a few milliseconds where the fork-join cost shows). Without binding
   the 32- and 64-thread runs are slower and scatter more. Refuted by a speed-up below 6
   at 16 threads in any case (then something serial dominates and has to be found), or
   by a threaded run that is slower than the one-thread run.
P7 (against one A100). One A100 is faster than 64 threads for the puncture (by a factor
   1.5 to 4) and for the box; 16 threads reach a quarter to a tenth of one card. So a run
   is cheaper on processors than waiting for a card when its card time is below about
   a tenth to a quarter of the expected queue wait. To be replaced by measured numbers.

## 2026-11-19 06:58 Entry 3: first numbers, the state of the machine, prediction for the placement

Calibration (run core-20261119-143919-24f5e73, registered by hand because `nrpic-run`
refused: 13 of the 16 cores of owner core were busy in other sessions; O3 build, 8
threads, spread over cores, load average 90 to 135 during the run): seconds per step
29.9 (punc, 344 MeshBlocks, 1.41e6 cells), 37.6 (cluster, 400 MeshBlocks, 1.64e6 cells,
1e5 particles), 15.0 (cosmo, 2.6e5 cells, 2.1e6 particles), 1.57 (newton, 2.1e6 cells,
5.12e5 particles). [VERIFIED: scaling_calib.json of that run]

Profile of punc at 16 threads (run core-20261119-145516-7a255c8, tools/kernel_timer.cpp
through the Kokkos tools interface): 15.2 s per step; of 129.6 s in kernels, 81.7 s are
the Z4c right-hand side (32 calls, 2.55 s each for 1.41e6 cells), 13.2 s the constraint
loop, 10.5 s the prolongation, 7.4 s the dissipation, 3.3 s zero-filling of new arrays;
the horizon finder is 0.04 s. From 8 to 16 threads the rate rises by 1.96 (4.71e4 to
9.25e4 zone-cycles per second). [VERIFIED: kernel_timer.txt of that run]

The machine is not idle: `scripts/omp_places.py 16 --verbose` at 06:57 reports a mean
load of 1.22 busy hardware threads per physical core (of 2) over all 72 cores, and 0.94
for the 16 least busy cores of one NUMA node. So every thread of a test shares its core
with another job. All timings below are taken under this load, with the load average
and the share of processor time of each run recorded; absolute rates are lower bounds.

Kokkos zero-fills every new array with one `memset` on the calling thread
(athenak/kokkos/core/src/impl/Kokkos_HostSpace_ZeroMemset.hpp, line 31), so the pages of
the mesh arrays start on the NUMA node of the first thread; the kernel's automatic NUMA
balancing is on (`/proc/sys/kernel/numa_balancing` = 1) and moves pages later. `numactl`
is not installed. [VERIFIED: source, /proc]

P8 (placement at 16 threads, punc, four cycles, two rounds, interleaved): "auto"
(`OMP_PLACES` from scripts/omp_places.py: the 16 least busy cores of one NUMA node,
`OMP_PROC_BIND=true`) is the fastest or within the scatter of the fastest; "close" over
`OMP_PLACES=cores` (cores 0 to 15 for every job of every session) and "spread" (cores 0,
4, 9, ... for every job) are no faster than no binding and may be much slower when
another job is bound to the same cores; no binding lies within 30 per cent of auto.
Refuted if auto is slower than another placement by more than the scatter between the
two rounds.
