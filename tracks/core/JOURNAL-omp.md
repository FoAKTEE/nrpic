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

## 2026-11-19 07:10 Entry 4: outcome of P8 (placement at 16 threads)

Run core-20261119-150022-d0d8641 (registered by hand), puncture case, O3 build, 16
threads, four cycles, two rounds interleaved; load average 97 to 116 throughout.
Seconds per step:

| placement | round 1 | round 2 | share of processor time |
|---|---|---|---|
| no binding (`OMP_PROC_BIND` unset) | 15.35 | 14.55 | 0.69, 0.69 |
| `OMP_PROC_BIND=spread OMP_PLACES=cores` | 15.52 | 14.42 | 0.75, 0.67 |
| `OMP_PROC_BIND=close OMP_PLACES=cores` | 15.16 | 14.86 | 0.78, 0.72 |
| `OMP_PROC_BIND=true OMP_PLACES=$(scripts/omp_places.py 16)` | 14.43 | 14.41 | 0.73, 0.68 |

P8 holds in its first part: the automatic placement is the fastest in round 1 (by 5 per
cent) and tied with spread in round 2; no binding is within 6 per cent of it. The
second part (fixed core lists much slower) did not occur in these two rounds: nobody
else was bound to cores 0 to 15 at the time. With every physical core of the machine
already running 1.2 threads of other jobs, the placement changes the step time by at most
7 per cent at 16 threads; the scatter between the rounds is 5 per cent. [VERIFIED:
scaling_*.json of the run] The share of processor time (0.67 to 0.78, setup included)
says the threads waited for a processor a quarter of the time.

## 2026-11-19 07:17 Entry 5: first pass of P0 and P1 on the unchanged source; profiles; the deposit

Run core-20261119-143706-92efe0f (source 92efe0f, the source of release core-v0.3;
stopped after five cases because the source was about to change; its files stay).
Reference R = release executable, one thread everywhere.

| case | S against R | O2, one thread, against R | O3, one thread, against R |
|---|---|---|---|
| geo | 2 files identical | identical | identical |
| boris | identical | identical | trajectory differs, 6.6e-15 of the largest number |
| dep | identical | identical | history differs, 1.7e-15 |
| east | 18 files identical | 14 of 18 files differ, at most 2.4e-12 (restart file 2.2e-14, particles 1.7e-15) | 15 files differ, same size |
| os | 16 files identical | 10 of 16 files differ, at most 4.7e-15 | (not finished) |

P0 holds so far (to be repeated on the final source). P1 FAILED for east and os: the
OpenMP build with the flags of the serial build and one thread does not reproduce the
serial build bit for bit when Z4c runs. The two executables are different programs (the
kernels are compiled inside OpenMP regions with -fopenmp); which difference in the
generated code is responsible was not tested, so no cause is named. Consequence for the
tests: the sharp test for races is not "threads against the serial build" but "N threads
against one thread of the same executable", where only the grouping of the reductions and
the order of the atomic additions can differ. The comparison driver now takes the
one-thread run of each threaded executable as the reference (P2 to P4 are read that way).

Measure of a difference (tracks/core/omp/omplib.py, number_diff): largest difference
over the largest number of the file; for text tables the integer columns are left out of
the scale and must be identical. A history holds sums that cancel (net momentum of a
symmetric state, 1e-13) next to sums that do not: relative to its own column such a sum
differs by order one from rounding alone, which is recorded (rel_column) but not judged.
A lost update of one cloud corner would change the energy integral of the east case by
2e-4 absolute against a scale of 1e3, i.e. 2e-7: above the threshold 1e-8.

Profiles at 16 threads (run core-20261119-150956-abda48c, by hand, O3, automatic
placement, four cycles each, load average 102 to 106):
- cluster, 18.4 s per step: Z4c right-hand side 47.5 s of 85.7 s in kernels,
  constraints 10.2 s, prolongation 6.8 s, zero-filling of new arrays 4.8 s (685 calls,
  on one thread), dissipation 4.0 s; all particle kernels together 2.5 s (push 0.47,
  deposit 0.19, filter 1.8). 1e5 particles are 3 per cent of this case.
- cosmo, 6.9 s per step: deposit 11.9 s of 31.5 s (5 calls of 2.4 s: 2.1e6 particles x 64
  cells x 10 components = 1.3e9 atomic additions each), push 7.7 s, Z4c right-hand side
  7.7 s, constraints 1.7 s.
- newton, 0.75 s per step: deposit 0.96 s of 4.0 s, multigrid 1.4 s (defect 0.56, smoother
  0.20, buffers 0.27, prolongation 0.12, restriction 0.09), kick 0.54 s, push 0.39 s,
  zero-filling 0.36 s; a third of the run time (6.1 s) lies outside kernels (set-up).
[VERIFIED: kernel_timer.txt of the run]

Decision: the deposit gets a second way of adding, chosen by a new option that is read
only if present, `<particles> deposit_threads = private` (OpenMP build only): one copy
of the source array per thread, plain additions, copies summed cell by cell in thread
order (athenak/src/particles/nrpic_threads.hpp; hooks: one include and one member in
particles.hpp, five lines in nrpic.cpp). Default and every other build: the atomic
additions as before. Reason: where the deposit dominates (cosmology box) the atomics are
the cost, and with private copies a threaded run is repeatable. Also fixed: the second
constructor of ParameterInput tested the macro OPENMP_PARALLEL, which does not exist, so
its lock stayed uninitialised in an OpenMP build (the constructor is not used by main).

P9 (private copies), written before the build:
 a. Two runs with `deposit_threads = private` at the same thread count (4, 16) give
    byte-identical files for dep, east, os and newton. Refuted by any differing file.
 b. With one thread, private and atomic give byte-identical files (same executable).
 c. Private at N threads differs from one thread by rounding only (below 1e-8 of the
    largest number of each file), like atomic.
 d. Cost at 16 threads: for cosmo the deposit kernel plus zeroing and summing the copies
    takes less than half the 2.4 s of the atomic kernel and the step is at least 15 per
    cent shorter; for newton (2.3e6 cells x 10 components x 16 copies = 2.9 GiB zeroed
    and summed per deposit, against 4e7 additions) it is no faster, probably slower.
    Refuted for cosmo if the deposit is not faster: then the atomics were not the cost.

## 2026-11-19 07:50 Entry 6: audit of the kernels for threads; predictions P10 to P12

Session resumed (merge of main 6c5cf703: harness and coord only, no source). Builds of the
final source a9c34e7a: S (.work/build_cpu, 07:24), O3 (.work/build_omp, 07:25), card
(.work/build_gpu, rebuilt 07:47 in 127 s). O2 (06:32) is of the earlier source and is not
used again: the sharp test is N threads against one thread of O3 (entry 5).

Audit, read from the source of this branch (athenak/src/particles, scalar_field,
pgen/nrpic, utils/rng.hpp; 10734 lines). Every kernel is a Kokkos `par_for`,
`parallel_reduce` or `parallel_scan` on DevExeSpace; there is no `#pragma omp`, no use of
the Serial space, no TeamPolicy, no static or global state that a kernel writes, no
random-number pool (rng.hpp is a pure counter-based function). [VERIFIED: grep and reading]

| kernels | writes | under threads |
|---|---|---|
| push (`nrpic_push`), Newtonian kick and push, test kick, assign, trajectory metric (`nrpic_trajmet`) | particle p only | race-free; iteration counts by reduction (integers: exact) |
| count, compact (`nrpic_count`, `nrpic_compact`) | reduction; scan writes slot `upd` of particle p | race-free; integer scan exact, order kept |
| deposit (`nrpic_deposit`) | scatter into cells shared by particles | `Kokkos::atomic_add` (correct, order of additions free) or private copies (`deposit_threads = private`); `sum_mW` by reduction |
| filter, compensation, limited compensation, step source, lambda (`nrpic_filter*`, `nrpic_complim*`, `nrpic_stepsrc`, `nrpic_lambda`) | cell (m,n,k,j,i) of a second array (`tm_work`), then a copy | race-free (read tm, write wk, never in place) |
| collision cells (`nrpic_coll_cell`, `_scan`, `_fill`, `nrpic_collide`) | populations by `atomic_add`, list slots by `atomic_fetch_add`; each cell its own segment of the list and its own particles | race-free; the order in which `_fill` puts particles into a cell is free, but each cell sorts its list by key and tag before pairing (nrpic_collide.cpp, the sort inside the cell kernel), so the collisions do not depend on it; statistics by reduction (CollStats `+=`: integer sums exact, real sums by grouping) |
| Newtonian mesh (`_flat`, `_srcnorm`, `_mesh`, `_mean`, `_extrap`, `_store`) | cells; extrapolation per (m, a, b) line | race-free; the mean of Phi and the source norm are reductions that feed back (P5) |
| diagnostics (`nrpic_sums`, `_amin`, `_meshstat`, `_cstat*`, `_zstat`, `_consred`, `_kmax`, `nrpic_probe`, `sf_means`, `sf_hist`) | reductions into history files | race-free; real sums depend on the grouping, i.e. on the thread count |
| line output, conservation arrays (`nrpic_line`, `nrpic_cons*`) | element (m,v,i) or cell | race-free |
| scalar field (`sf rhs`, K-O, tmunu, `sf_syn_{z,y,x}`, `sf_kick`, RK update) | cell, or (f,p,k), (f,x,k,j) of work arrays | race-free |
| problem generators (`nrpic_kerr_schild`, `nrpic_homogeneous`, `nrpic_cosmo*`, `nrpic_cf*`, `sf_tests`) | cell | race-free; tables read on the host before the kernels |

Host-only paths: the outputs copy to host and write serially; DualViews alias in this
build (DevMemSpace = HostSpace), as in the serial build; Kokkos OpenMP kernels return only
when finished, so no fence is missing where the serial build needed none. One host defect
was found and fixed in a9c34e7a: ParameterInput's second constructor tested the macro
`OPENMP_PARALLEL` (never defined) and left its lock uninitialised in an OpenMP build.
Conclusion [VERIFIED by reading, to be tested below]: the only places where threads can
change a result are the order of the atomic additions of the deposit and the grouping of
real reductions; nothing else depends on the schedule.

Predictions for the final regression (run on the same source; P0 to P5 and P9 of entries
2 and 5 stand):
P10 (collisions). coll (no deposit, analytic flat metric): particle snapshots
    byte-identical at 4 and 16 threads to one thread of O3, because each cell sorts its
    list; the collision history keeps its integer columns and differs at most by rounding
    in the real sums. Refuted by any difference in a snapshot.
P11 (Z4c without particles). kg, noise, bench, punc: every output that holds evolved
    fields (restart file, mesh outputs, horizon and tracker files) byte-identical at 4 and
    16 threads to one thread; only history columns that are sums may differ by rounding.
    Refuted by a difference in an evolved field (that would be a schedule-dependent kernel
    in Z4c or the scalar field).
P12 (bounds). A Kokkos debug build of the OpenMP executable (DEBUG=1: View bounds
    checking) runs dep, east, os, newton and coll at 4 threads with atomic and with
    private copies without a bounds error, and gives files that agree with O3 to rounding.
    Refuted by an abort or a difference above 1e-8.

## 2026-11-19 08:04 Entry 7: the measure of a difference; outcome of P12; one thread

Measure. The first runs of this session showed that the measure of entry 5 ("rel_file":
largest difference over the largest magnitude among the numbers that differ) is not the
measure the predictions name: in east, O3:4 against a second O3:4 gave 1.1e-9 from a
particle snapshot whose differing numbers are all below 6e-16 in size (abs 7e-25), i.e.
rounding noise of numbers that are nearly zero. omplib.number_diff now reports
- rel_max (verdict, as the predictions were written): largest |a - b| over the largest
  magnitude in the file (text tables: over the largest number outside integer columns);
- rel_floor (stricter, recorded): largest |a - b|/max(|a|, |b|, 1e-6 x file maximum);
- the conservation identity of the deposit, max over the history of
  |int_E - sum_mW|/sum_mW (recompare.py), which a lost update breaks at the weight of one
  cloud corner (above 1e-6 for 1e4 particles) and rounding leaves near 1e-14.
Two findings forced further changes, neither a defect of this package:
1. AthenaK restart files (outputs/restart.cpp lines 221-229) write RegionSize and
   RegionIndcs as raw structs; their padding bytes are uninitialised memory (bytes 130 to
   160 after `<par_end>` held the text "cfl_number = 0.25 nlim = -1 tl" in one run and
   zeros in another). Byte comparison of restart files is therefore unreliable in
   general; it held between S and R only because the same serial program left the same
   heap. Restart files are now compared on their data (the MeshBlock data after the
   per-MeshBlock size; omplib._rst_data). [VERIFIED: bytes of the two files]
2. The Newtonian mode with `threshold = 0` (V cycles until the defect stops falling)
   decides the number of V cycles from a reduced defect norm; at 4 threads 24 of 41
   records of `mg_cycles` (12 to 15 cycles) differ from one thread by one or two cycles.
   The column and its copy in the `.nwt` restart file are reported apart as "decisions",
   not judged; the particle state differs by 1e-12 (rel_max) either way.

Outcome of P12 (run core-20261119-155830-248f393; debug build `.work/build_omp_dbg`,
DEBUG=1: Kokkos debug mode and View bounds checking, 4 threads, against O3 at one thread;
recompare.py): no abort and no bounds error in dep, east, newton, coll with atomic and
with private deposit; rel_max 3.4e-14 (dep), 3.0e-13 and 5.3e-13 (east, atomic and
private), 9.7e-13 and 1.0e-12 (newton), 9.3e-14 (coll); deposit identity 1.2e-14 (dep),
2.3e-15 and 2.4e-15 (east), 2.8e-13 (newton), the same size as at one thread of O3
(5.5e-14, 1.0e-14, 7.0e-13). P12 holds.

P0 so far (run core-20261119-154940-1c3e906, still running os): S gives the files of R
byte for byte in geo, boris, dep, jeans, east, coll, kg, newton, binary, noise, bench. The
puncture case failed in both R and S (exit 1, "More than one history, event log, or
restart output block": the case appended a restart block to a deck that has one); fixed
in 501ba4f, rerun in core-20261119-155520-0bc529f.

One thread (runs core-20261119-154725-1c3e906 and core-20261119-154729-1c3e906, load
average 122 to 139, processor share 0.98 to 1.00), seconds per step:

| case | O3, 1 thread | S (serial build) | O3 faster by |
|---|---|---|---|
| punc (1.41e6 cells, 6.9e3 zone-cycles/s) | 203.4 | 242.7 | 1.19 |
| cluster (1.64e6 cells, 1e5 particles) | 243.4 | 294 | 1.21 |
| cosmo (2.6e5 cells, 2.1e6 particles) | 94.3 | 113.9 | 1.21 |
| newton (2.1e6 cells, 5.1e5 particles) | 10.6 | 11.6 | 1.09 |

The Z4c benchmark (64^3 uniform, P0 run) gives 6.7e3 zone-cycles/s on one thread for both
S and R, against 2.0e7 on one card (docs/TESTLOG.md, "Z4c throughput"): the card is about
3000 times one processor thread for Z4c. [VERIFIED: run.log of the bench case]
