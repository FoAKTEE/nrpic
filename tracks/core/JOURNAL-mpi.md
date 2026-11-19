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

### 06:38 Design

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

### 06:52 Entry 2: code of steps 1 and 2, predictions of T1 (written before the first run)

Code: `particles/nrpic_mpi.cpp` (table of all MeshBlocks, ownership, hand-over, deposit
packets, probe, gathered files, restart state), `nrpic_mpi.hpp` (sums over ranks),
`nrpic_cloud.hpp` (the cloud as functions), hooks in `nrpic.cpp`, `nrpic_io.cpp`,
`particles.{hpp,cpp}`, `CMakeLists.txt`. New record of a run on several ranks:
`<basename>.mpi.hst` (particles handed over and deposit packets since the last record,
particles per rank), so that a test can show it did cross rank boundaries.

Test T1 (`problems/tests/mpi_kerr_swarm.athinput`, driver
`tracks/core/analysis/mpi/mpi_tests.py --case t1_kerr`): 2000 particles, radii 3 to 12
around a Kerr black hole (a = 0.5) whose Kerr-Schild metric is sampled on a 64^3 mesh of
64 MeshBlocks of 16^3 (fixed metric, no deposit), midpoint pusher, 400 steps of 0.25;
lapse threshold 0.6; one particle in twelve fast enough to leave the box. Variant
`t1_kerr_boris` (Boris pusher). T1p (`mpi_box_periodic.athinput`, `--case t1p_box`):
3000 particles streaming through a periodic unit box (32^3, 64 MeshBlocks of 8^3,
homogeneous non-diagonal metric), 300 steps. Each on 1, 2 and 4 ranks of the MPI build.

Predictions:
- P1a. Trajectory file, metric-at-particle file, every snapshot and the particle part of
  the restart files are identical byte for byte on 1, 2 and 4 ranks: a particle sees the
  same MeshBlock data whatever rank holds the block, the push is per particle, and the
  files are written in tag order. Refuted by any differing byte: then a particle was
  lost, duplicated, reordered, or pushed with another MeshBlock's data.
- P1b. In the history the counts (particles, excised, escaped), the lapse minimum and
  the iteration maximum are equal exactly; the particle sums (rest mass, momenta) agree
  to rounding, relative 1e-13 or better, since only the order of the sum differs. The
  probe columns are equal exactly if the compiler forms the eight-term sum the same way
  in both places; otherwise they differ in the last digit (I expect exact, not sure).
  Refuted by a difference above 1e-12 in any column.
- P1c. The run does cross rank boundaries: `swarm.mpi.hst` of the 2- and 4-rank runs
  shows hundreds of hand-overs or more (orbits of period about 140 at r = 8 against a
  run time of 100), and all particles start on rank 0 and spread in the first record.
  If it showed none, the test would not test the hand-over.
- P1d. Excision and escape occur (both counters above zero at the end), so both removal
  paths are exercised. If not, the particle file is changed and the test repeated.
