# JOURNAL of core, work package mpi (branch `core/mpi`)

Append-only. Predictions are written before a test runs, outcomes after, also when the
prediction failed. Runs are registered with `harness/bin/nrpic-run submit --package
tracks/core/analysis/mpi` (manifests under `tracks/core/runs/<run_id>/`, outputs under
`scratch/core/<run_id>/`). Labels: [VERIFIED] read or measured in this session (with
locator), [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Times: `date` on anta (PST).

## 2026-11-19 session mpi-1

### 06:22 Start

Branch `core/mpi` at main 27b2ced (merge: already up to date). Read CLAUDE.md, the
charter to "Owners", decisions 0010, 0016, 0017, brief lines 493-553, 688-706, 834-860,
Track F's request `20261115T1507Z__to-core__two-card-or-larger-blocks.md`, section 3 of
`REQUESTS_ADF.md` on `core/requests-adf`, and the sources: `particles/nrpic*.{cpp,hpp}`,
`particles.{hpp,cpp}`, `particles_tasks.cpp`, `bvals/bvals_part.cpp`,
`bvals/bvals_tasks.cpp`, `bvals/bvals_cc.cpp` (send and receive), `mesh/meshblock.cpp`,
`pgen/nrpic/*.cpp`, the restart hooks in `outputs/restart.cpp` and `pgen/pgen.cpp`.

### 06:25 Entry 1: tool chain (smoke test, not a registered run; no number is taken from it)

- `mpirun --version`: Open MPI 5.0.1 (`/home/emost/codes/openmpi`), built with CUDA
  and UCX-CUDA (`ompi_info`) [VERIFIED]. So the question "is the MPI CUDA-aware" of
  `REQUESTS_ADF.md` section 3 is answered: yes.
- `CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON" scripts/build_cpu.sh .work/build_cpu_mpi` builds
  the unmodified source with MPI (the later `-D` wins); `.work/build_cpu` is the serial
  build. The executable finds the MPI library through its run path (`env -i ldd`).
- Vacuum puncture `problems/tests/z4c_bench.athinput` at 64^3 in 16^3 MeshBlocks, 4
  cycles, unmodified source: runs on 1 rank and on 2 ranks (`scratch/core/tmp/mpi_sanity`).
  The processor build is slow (about 6e3 zone-cycles per second and core with rk4 and
  four ghost cells), so the tests with the spacetime solver must be small.

### 07:10 Design

Written before the code: `tracks/core/interfaces/mpi.md` sections 1 to 4. Main choices
[JUDGEMENT]: no additive ghost exchange; a cloud that reaches MeshBlocks of another rank
is sent there as a deposit packet and the receiving rank adds the cells it holds, so
each cloud cell is added once with the weights of the one-rank run. Rank 0 reads the
particle and restart files and the first ownership pass distributes. Particles of a
rank stay ordered by tag. Files are written by rank 0 in tag order with unchanged
formats. Findings that differ from the earlier assessment: the filter's ghost exchange
needs no change (its `ClearSend`/`ClearRecv` already wait before the unpack,
`bvals_tasks.cpp` 59-97); the upstream particle exchange is not reusable (send list of
a tenth of the particles, `bvals_part.cpp` 68; face-neighbour logic).
