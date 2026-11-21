# Build and Slurm helpers

Machine: `anta` (2x A100 80 GB, reachable only through Slurm partition `preempt`:
1 h limit, 4 CPUs in total, preemption cancels jobs). No MPI. Processor runs: serial
(`build_cpu.sh`) or threaded with OpenMP (`build_cpu_omp.sh`, section "Threaded processor
runs").

| Script | Purpose |
|---|---|
| `build_gpu.sh [dir]` | Kokkos CUDA build for one A100 (sm_80), default `build_gpu/` |
| `build_cpu.sh [dir]` | serial CPU build, `-O2 -g`, asserts on, default `build_cpu/` |
| `build_cpu_omp.sh [dir]` | threaded CPU build (Kokkos OpenMP), `-O3 -DNDEBUG -g`, default `build_omp/` |
| `cpu_run.sh <rundir> <athinput or .rst> [args]` | one threaded processor run with placement and a log |
| `omp_places.py N` | `OMP_PLACES` of the N least busy cores of one NUMA node |
| `gpu_run.sh <rundir> <athinput or .rst> [args]` | one GPU run through `srun` (blocking) or `sbatch` |
| `submit_chain.sh <rundir> <athinput> [args]` | self-resubmitting run across the 1 h limit |
| `_build.sh`, `_athena_job.sh` | internals of the scripts above |

## Building

```
scripts/build_gpu.sh                                  # built-in pgens -> build_gpu/src/athena
PROBLEM=z4c/z4c_one_puncture scripts/build_gpu.sh     # -> build_gpu-z4c_one_puncture/
DEBUG=1 scripts/build_cpu.sh                          # bounds checking -> build_cpu-debug/
scripts/build_cpu.sh                                  # -> build_cpu/src/athena (gdb-friendly)
```

- Toolchain: CUDA 12.6 (`CUDA_HOME` overrides), host `g++` 11.4, `Kokkos_ARCH_AMPERE80`
  and `Kokkos_ARCH_ICX` (Xeon 8360Y). Kokkos 4.7.02 also accepts CUDA 13.0
  (`CUDA_HOME=/usr/local/cuda-13.0` builds cleanly). 12.6 stays the default because it
  is the toolkit all the smoke tests were run with, and it needs no minor-version
  compatibility with the 580 driver (CUDA 13.0). `/usr/local/cuda-12.8` has no nvcc. The build directory gets a small compiler wrapper,
  `nvcc_wrapper_pinned`, that pins the toolkit, so a bare `make` in the build directory
  never picks up the default `nvcc` (13.2) from `PATH`.
- Re-running a script is an incremental rebuild (`cmake --build -j16`). cmake is re-run
  only when the options change; edits to `athenak/src/CMakeLists.txt` are picked up by
  make itself. Inside a build directory, `make -j16` works as well.
- `PROBLEM` and `DEBUG` select separate default directories, because `config.hpp`
  (included by every source file) changes with `PROBLEM`, and so does Kokkos's
  configuration with `DEBUG`.
- Other knobs: `JOBS` (capped at 16), `HOST_ARCH`, `CMAKE_EXTRA`, `RECONFIGURE=1`, and
  `ATHENAK_SRC` (build another source tree, e.g. a `git archive` snapshot).
- The last line printed is the executable path. The full log is `<dir>/build.log`.
- A full GPU build takes about 190 s at `-j16`; a CPU build takes about 60 s.

Problem generators: a file compiled with `-DPROBLEM=<path under src/pgen>` defines
`ProblemGenerator::UserProblem()`, and `<problem>/pgen_name` is then ignored. A
built-in pgen is listed in `src/CMakeLists.txt`, declared in `src/pgen/pgen.hpp`, and
dispatched by name in `ProblemGenerator::CallProblemGenerator()` in `src/pgen/pgen.cpp`.
Every pgen must return early when `restart == true`, after re-enrolling its function
pointers; otherwise it overwrites the state just read from the restart file (the stock
`z4c_one_puncture.cpp` does exactly that).

## Single GPU runs

```
scripts/gpu_run.sh runs/test1 problems/foo/foo.athinput time/nlim=100
scripts/gpu_run.sh runs/test1 runs/test1/rst/foo.00002.rst          # restart
BATCH=1 TIME=00:50:00 scripts/gpu_run.sh runs/test2 foo.athinput    # sbatch, returns
```

- athena runs with its working directory set to `<rundir>` and with `-d <rundir>`, so
  all outputs land there. Relative paths in the input file are relative to `<rundir>`.
- The log is `<rundir>/athena.<timestamp>.log` (`athena.log` links to the latest). It
  starts with a header (host, job, GPU) and ends with a footer giving the exit status,
  the baseline GPU memory and the peak GPU memory (sampled every 0.5 s into
  `*.gpumem.csv`). The input file is copied into `<rundir>`.
- `ATHENA_EXE` selects the executable (default `build_gpu/src/athena`). With `BATCH=1`
  the executable is first copied into `<rundir>`, so rebuilding while the job waits in
  the queue does not change what runs.
- Inside an existing allocation that already sees a GPU, the script runs athena
  directly without a new `srun`.
- One job takes 1 GPU and 1 CPU; up to 4 such jobs fit the partition's CPU limit.

## Long runs: `submit_chain.sh`

```
ATHENA_EXE=build_gpu/src/athena scripts/submit_chain.sh runs/os_collapse problems/os/os.athinput
scripts/submit_chain.sh --status runs/os_collapse
scripts/submit_chain.sh --stop   runs/os_collapse      # cancel, never resubmit
```

Each segment is one sbatch job (1 GPU, 1 CPU, Slurm `-t 00:59:00`) that runs
`athena ... -t 00:50:00`. The first segment uses `-i <input>`; later segments use
`-r <newest rst/*.rst>`. Extra arguments are passed to every segment, so for example
`time/tlim=200` extends a run. The chain is driven by AthenaK's own termination
messages:

| Segment ends with | Action |
|---|---|
| `Terminating on time limit` / `... cycle limit` | DONE |
| `Terminating on wall clock limit` (a restart file was written by Finalize) | resubmit |
| SIGTERM: preemption, Slurm time-out, `scancel` | resubmit from the newest restart (not after `--stop`) |
| restart read error ("restart file is broken", truncated `.prt`, ...) | rename it `*.rst.bad`, retry with the next-newest |
| nonzero exit, no termination message, no progress, NaN/Inf in the last history line, a history `Volume` column below half its initial value, `CHECK_CMD` failing | FAILED, no resubmission |

Requirements and behaviour:
- The input must contain a restart output block, for example
  `<output9>` with `file_type = rst` and `dcycle = 2000` (or `dt = ...`). Preemption
  loses the work done since the last dump. The script refuses inputs without one.
- The executable is copied to `<rundir>/chain/athena` at start, so rebuilding does not
  change the binary that reads the chain's restart files. To change the binary or the
  arguments, `--stop`, then run the start command again: it resumes from the newest
  restart. The same command resumes a FAILED chain after a fix.
- State is in `<rundir>/chain/`: `STATUS`, `events.log`, per-segment athena logs
  `segNNN.job<id>.aN.log` (`latest.log`), `slurm-<id>.out`, `config.sh`.
- Environment at start: `ATHENA_WALL` (default 00:50:00), `SLURM_TIME` (00:59:00),
  `CPUS` (1), `MAX_SEGMENTS` (100), `JOB_NAME`, `SLURM_EXTRA`, and `CHECK_CMD`
  (a shell command run after each normally ended segment, with `$1` = rundir; a
  nonzero exit marks the chain FAILED).
- Z4c NaNs do not show up as `nan` in the history: `HistoryOutput` sums only cells with
  `chi >= excise_chi`, so NaN cells drop out, the norms go to 0, and `Volume` collapses.
  That is why the `Volume` check exists. Use `CHECK_CMD` for anything problem-specific.

## Restart caveats found in the smoke tests (`runs/smoke/`)

- Every wall-clock stop writes all outputs once at the stop time, and advances each
  `dt`-based output's `last_time` by `dt`, so the next scheduled output of each kind
  is skipped (outputs at t = 34.625 instead of t = 35, for example).
- History files are appended to. After a preemption, the lines between the last
  restart dump and the kill appear twice, and every restart adds a new header block.
  When analysing, de-duplicate by time and keep the last occurrence.
- The history file of a Z4c run is called `<basename>.z4c.user.hst` (a missing `break`
  in `outputs/history.cpp`).
- A Z4c restart is not bitwise reproducible. It agrees with an uninterrupted run to
  about 1e-12 relative after one cycle. Uninterrupted GPU runs without particle
  deposit are bitwise reproducible; with deposit they are not: the order of the
  atomic additions changes from run to run, and two runs of one executable differ from
  the first step on (1e-16 growing to 1e-13; runs core-20261115-033115-b7b431d and
  core-20261115-033228-b7b431d, and cases c3-c5 of core-20261115-135312-a6e5c46). A
  byte regression on a card therefore compares only runs without deposit, or compares
  the difference between two executables with the scatter between two runs of one.
- Default parameters are stored in the restart file as text with 6 significant digits
  (`ParameterInput::GetOrAddReal`), so a default real with more digits comes back
  rounded after a restart. Put such values in the input file explicitly.

## Threaded processor runs (`build_cpu_omp.sh`, `cpu_run.sh`)

```
scripts/build_cpu_omp.sh                         # -> build_omp/src/athena (Kokkos OpenMP)
OMP_OPT=debug scripts/build_cpu_omp.sh build_omp_o2   # flags of the serial build (-O2 -g)
DEBUG=1 scripts/build_cpu_omp.sh                 # Kokkos debug mode, View bounds checks
THREADS=6 scripts/cpu_run.sh runs/x problems/foo/foo.athinput time/nlim=100
```

- The build is `_build.sh omp`: `Athena_ENABLE_OPENMP=ON`, Kokkos OpenMP as the default
  and host space, Serial not compiled in, g++ 11.4, `-O3 -DNDEBUG -g`, `Kokkos_ARCH_ICX`.
  The serial build (`build_cpu.sh`) is unchanged and stays the reference for byte
  comparisons with earlier processor runs.
- Set the thread count explicitly (`OMP_NUM_THREADS`; the OpenMP default is all 144
  hardware threads) and keep within six cores per session (decision 0019, CLAUDE.md);
  `cpu_run.sh` defaults to `THREADS=6`.
- Placement: `cpu_run.sh` (default `PLACES=auto`) binds the threads to the least busy
  physical cores of one NUMA node, chosen by `omp_places.py` when the run starts
  (`OMP_PROC_BIND=true`). Do not use `OMP_PLACES=cores` with `OMP_PROC_BIND=spread|close`:
  every job of every session is then bound to the same cores. Two runs started at the
  same moment must not each call `omp_places.py` (they pick the same cores): choose 2n
  cores once and split them (`tracks/core/omp/scaling_series.sh`, function `split4`).
- Reproducibility (tracks/core/interfaces/threaded_build.md, section 4): without deposit a
  threaded run repeats itself byte for byte and equals one thread of the same executable
  in every evolved field; with deposit (atomic additions) it repeats only to rounding,
  like a card run; `<particles> deposit_threads = private` makes it repeat byte for byte
  at a fixed thread count. The threaded executable with one thread is a different program
  from the serial build (other flags) and agrees with it to rounding, not byte for byte.
  Restarts are exact under threads: a continued run equals the uninterrupted one datum
  for datum at one thread and with `private` (with atomic additions to rounding). The
  gas multigrid depends on the thread count through the rounding of the plain sum of its
  volume mean (no race); results agree to the solver tolerance.
- Speed (tracks/core/interfaces/threaded_build.md, sections 5 and 6): six threads are 4.4
  to 5.8 times one thread; one A100 is 72 to 90 times six threads for runs with Z4c and
  11.9 times for the periodic Newtonian mode; the Newtonian mode with isolated
  boundaries is 1.6 times faster on six threads than on a card.
