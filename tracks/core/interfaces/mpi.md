# Interface: the particle module on more than one MPI rank

Owner: core (branch `core/mpi`, work package mpi, wave 3a, 2026-11-19). For Track F
(request `20261115T1507Z__to-core__two-card-or-larger-blocks.md`: a mesh that does not
fit one card) and for every track whose runs are limited by one card or one processor
rank. Journal: `tracks/core/JOURNAL-mpi.md`. Earlier assessment: section 3 of
`tracks/core/interfaces/REQUESTS_ADF.md` on branch `core/requests-adf`.

Labels: [VERIFIED] read in the source of this tree or measured in a registered run
(locator given), [JUDGEMENT] a design choice of this note, [TO VERIFY] not checked.

Sections 1 to 4 are the design, written before the code. Section 5 lists the lines of
shared files that were touched, section 6 the state reached (what is tested, what is
not), section 7 how to run, section 8 the answer to Track F.

## 1. What exists

| Part | Finding | Locator |
|---|---|---|
| Build | `scripts/_build.sh` passes `-DAthena_ENABLE_MPI=OFF`; a later `-D` on the same command line wins, so `CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON"` gives an MPI build without a change of the scripts | `scripts/_build.sh` lines 60, 125 [VERIFIED: build `.work/build_cpu_mpi`] |
| MPI library | Open MPI 5.0.1 under another user's home, configured `--with-cuda=/usr/local/cuda-12.2 --with-ucx=.../ucx-cuda` (device buffers can be handed to MPI); the executable finds it through its run path | `ompi_info`, `ldd` [VERIFIED] |
| Spacetime solver | Mesh, ghost exchange, refinement, load balancing carry MPI code upstream. A vacuum puncture (`problems/tests/z4c_bench.athinput`, 64^3 in 16^3 MeshBlocks, 4 cycles) runs on one and on two ranks with the unmodified source | smoke test, journal entry 1 [VERIFIED: it runs; agreement of the fields is test T3] |
| Ghost exchange of cell-centred data | Rank-packed buffers; `InitRecv` posts the receives and rebuilds its tables when the mesh changed, `ClearSend` and `ClearRecv` wait (`MPI_Wait`), `RecvAndUnpackCC` tests the requests and unpacks | `bvals/bvals_tasks.cpp` 30-97; `bvals/bvals_cc.cpp` 245-300 [VERIFIED] |
| Upstream particle exchange | `ParticlesBoundaryValues` moves cosmic-ray particles to face, edge and corner neighbours: it assumes at most one MeshBlock crossed per step and periodic mesh boundaries, and sizes its send list to a tenth of the particles of the rank | `bvals/bvals_part.cpp` 51-180 (68: `0.1*npart`; 155-170: periodic reset) [VERIFIED] |
| Particle module | Stops when `nranks > 1` | `particles/nrpic.cpp` 60-64 [VERIFIED] |

## 2. What in the particle module assumes one rank

In the order of a cycle (`nrpic.cpp` 11-18). "Pack" is the set of MeshBlocks of a rank.

| # | Part | What it does today | What fails on several ranks | Locator |
|---|---|---|---|---|
| 1 | Creation | The particle file or the inline list is read into the arrays of the rank; tags are the positions in the file | every rank would hold every particle | `nrpic_io.cpp` 989-1057 |
| 2 | Ownership | `NrpicAssignBlocks` wraps the position and searches the pack (`FindBlock`); not found means "left the mesh" | a particle in a MeshBlock of another rank would count as escaped | `nrpic.cpp` 552-573; `nrpic_mesh.hpp` 26-45 |
| 3 | Removal | `NrpicRemoveFlagged` counts and removes escaped and excised particles and keeps the order of the others | the counters are those of one rank | `nrpic.cpp` 580-627 |
| 4 | Push | per particle, with the metric of its own MeshBlock including ghost cells | nothing, once the particle lives on the rank of its MeshBlock | `nrpic.cpp` 377-545 |
| 5 | Deposit | each cloud cell is added to the leaf cell of the MeshBlock that contains it, found by a search of the pack; a cell that is found nowhere is dropped (outside the mesh); the representation level of a cloud is the finest level among the owners of its cells | cloud cells in MeshBlocks of another rank would be dropped, and their level would not be seen | `nrpic.cpp` 661-904 |
| 6 | Filter, compensation | ghost exchange `InitRecv, PackAndSendCC, ClearSend, ClearRecv, RecvAndUnpackCC` before every pass | nothing: the two `Clear` calls wait for the messages before the unpack (section 1) | `nrpic.cpp` 1035-1046, 1100-1111 |
| 7 | Sums | particle sums, mesh integrals, extrema, counters in the history and the other records | sums of one rank; only the expansion rate is reduced over the ranks | `nrpic_io.cpp` 170-276, 290-445, 619-797; `nrpic.cpp` 1336-1340 |
| 8 | Probes | eight cells around the probe, searched in the pack | cells of another rank are missing | `nrpic_io.cpp` 80-164 |
| 9 | Files | history, constraint statistics, trajectories, snapshots, line and field dumps, the particle restart file: every rank would open the same file and write its own part | | `nrpic_io.cpp` 242, 430, 504, 559, 768, 805, 950, 1068 |
| 10 | Restart | one file `<name>.rst.prt` with all particles, the state of the probes and counters and, with `source_extrap`, the source densities of the coming step as one mesh array | read by every rank; the mesh array is that of one pack | `nrpic_io.cpp` 1067-1226 |
| 11 | Mesh changes | `NrpicInitializeSources` after every regridding: metric arrays, ownership, deposit | with load balancing a MeshBlock and its particles end on different ranks | `mesh/mesh_refinement.cpp` 186-190; `nrpic.cpp` 1381-1416 |
| 12 | Interpolation | metric arrays are filled from the ADM variables of all cells including ghost cells | nothing | `nrpic.cpp` 297-318 |
| 13 | Other parts of the module | Newtonian mode (Poisson solve, sums, own restart file), collisions (statistics, files), curvature records, the test kick | sums and files of one rank; the Poisson solve on several ranks is untested | `nrpic_newton.cpp`, `nrpic_collide.cpp`, `nrpic_curvature.cpp`, `nrpic_kick.cpp` |

All rows [VERIFIED] by reading at commit 27b2ced.

## 3. Design

Rules of the design [JUDGEMENT]:

- R1. With one rank nothing new runs: every hook is behind `nr_multirank`
  (`global_variable::nranks > 1`), in the serial build and in the MPI build started on
  one rank. Results of existing set-ups stay bit-identical (regression, section 4).
- R2. The new code lives in one new file, `particles/nrpic_mpi.cpp`, with a small header
  `particles/nrpic_mpi.hpp` (reductions) and `particles/nrpic_cloud.hpp` (the cloud of
  the deposit as functions, used by the new code). Shared files get one-line hooks,
  placed at the top of a function or directly behind the statement they extend, so that
  the merge with the wave-2 branches is mechanical.
- R3. A run on N ranks is the same computation as on one rank: the same MeshBlocks, the
  same particles with the same tags, the same contributions to every cell. What may
  differ is the order of additions (particle sums, cloud contributions to a cell), i.e.
  rounding. Quantities that involve no such sum must be bit-identical on processors:
  the state of every particle in a fixed metric, counters, extrema.
- R4. Scalar state of the module is the same on every rank at all times (counters of
  removed particles, probe state, output counters): additive counters are reduced when
  they change. Any rank can then write it, and a restart needs no merge.
- R5. Particles of a rank are kept in the order of their tags, as on one rank (where the
  order of creation is kept by the stable removal). Then the order of additions on a
  rank does not depend on the history of arrivals, and a restarted run has the particle
  order of the uninterrupted one.
- R6. Files keep their formats and are written by rank 0 in the order of the tags, so a
  file of an N-rank run can be compared byte by byte with that of a one-rank run, and a
  restart file can be read on a different number of ranks.

### 3.1 Table of all MeshBlocks

`NrpicMpiBuildBlockTable`: device arrays with the extent, the level and the rank of
every MeshBlock of the mesh (`nmb_total` entries), computed from `lloc_eachmb` and
`rank_eachmb` with the formula of the MeshBlock constructor (`mesh/meshblock.cpp`
38-108: `LeftEdgeX`, the mesh edge for the first and last MeshBlock), so that the edges
are those of `mb_size` bit for bit. Rebuilt whenever the mesh changed
(`GetAMRLoadBalanceUpdateSeq`). A point is looked up in the pack first, as today, and in
the table only when the pack does not contain it (`FindBlockGlobal`, a linear search:
[JUDGEMENT] adequate for the block numbers of the tests; a search in Morton order is
the later improvement if it shows in profiles).

### 3.2 Ownership and migration (step 1)

- Creation and restart: rank 0 reads the file and holds all particles; the first
  ownership pass distributes them. One code path serves the start, the restart and the
  redistribution after load balancing. Cost: rank 0 holds all particles once
  ([JUDGEMENT] acceptable: 76 bytes per particle).
- `NrpicAssignBlocks` on several ranks (`NrpicMpiAssignBlocks`): wrap, search the pack,
  then the table; the grid ID becomes the global ID of the owning MeshBlock, or -1.
- `NrpicRemoveFlagged` on several ranks (`NrpicMpiRemoveFlagged`): count escaped and
  excised particles and reduce the counts (R4); pack the particles whose MeshBlock is on
  another rank, by destination; exchange the numbers (`MPI_Alltoall`), then the records
  (all real and integer slots of the module, whatever their number); build the new
  arrays from the particles that stay and those that arrived, merged by tag (R5);
  update the particle numbers of the mesh. The upstream exchange is not used: its
  neighbour logic and its send list do not fit (section 1); a particle may go to any
  rank (start, restart, load balancing).
- Analytic metrics (`metric` other than `mesh`) need no MeshBlock: the particles stay
  on rank 0.

### 3.3 Deposit (step 2)

The deposit of today needs no ghost cells: every cloud cell goes to the leaf cell that
contains it. This is kept. A particle whose cloud reaches MeshBlocks of other ranks is
sent to those ranks as a deposit packet: position, lattice spacing and level of its
cloud, and the ten amounts (m W, m u_i, m u_i u_j / W). The receiving rank runs the
same cloud over the packet and adds the cells that lie in its own MeshBlocks. Every
cloud cell is then added by exactly one rank, the one that holds the leaf, with the
weights of the one-rank run: the conservation identity (mesh integrals equal particle
sums to rounding) holds by construction, also across refinement levels, and no additive
ghost exchange is needed. [JUDGEMENT: this replaces the "deposit into ghost cells and
add back" of the earlier assessment, which would need a new exchange and a rule for
ghost cells at refinement boundaries.]

- Hooks in the kernel of `NrpicDepositSources`: (a) the level of a cloud cell that the
  pack does not contain is taken from the table; (b) the Lorentz factor and the level of
  each cloud are stored for the packet pass. Everything else is behind the kernel:
  `NrpicMpiDepositRemote` finds the ranks each cloud touches (pack, then table), sends
  the packets, receives, and deposits them with `nrpic::CloudDeposit`
  (`nrpic_cloud.hpp`), which repeats steps (2) and (3) of the kernel. The kernel keeps
  its own copy for now so that the one-rank code is untouched; replacing that copy by
  calls of the header is a clean-up for after the merge of wave 2 (with a regression
  run). Until then test T2 guards the two copies against each other: a difference would
  show as a defect of the conservation identity at rank boundaries.
- The sums of the deposit (`sum_mw`, `dep_sum`, `dep_sum_filt`) are reduced where they
  are formed (R4).

### 3.4 Sums, probes, files (steps 1 to 3)

- `nrpic_mpi.hpp`: `nrpic::MpiSum`, `MpiMin`, `MpiMax` over lists of scalars; empty in
  the serial build and on one rank. One call behind each reduction of the records.
- Probe: each rank evaluates the cells it holds of the eight around the probe; the
  products are collected and added in the order of the one-rank loop.
- Files: `NrpicMpiGatherBegin/End` put all particles, ordered by tag, into the arrays of
  rank 0 for the duration of a write (snapshot, restart); the writers stay as they are
  and run on rank 0 only. Per-particle slots added by other branches travel with the
  arrays. Trajectories: the records of each rank are collected on rank 0 and ordered by
  tag. Line and field dumps: every rank fills its cells of the global array, the arrays
  are summed (each cell is set by one rank, so the sum is exact).
- Restart read: rank 0 reads, the scalar state is broadcast, the source densities of
  the coming step are scattered by MeshBlock.

### 3.5 Refined meshes and load balancing (step 5)

Nothing beyond the above is planned: the level rule of the deposit uses the table
(3.3 a), and after a regridding `NrpicInitializeSources` rebuilds the table and runs the
ownership pass, which sends every particle to the rank that now holds its MeshBlock.

### 3.6 Not ported in this package

Newtonian mode, collisions, curvature records, the test kick, and whatever the wave-2
branches add (accretion diagnostics, initial-data solver, perturbations): the module
stops with a message when one of them is switched on with more than one rank
(`NrpicMpiInit`), so that no option runs unported. Horizon excision
(`ah_exc_factor`) reads the horizon finder, which has MPI code upstream: [TO VERIFY].

## 4. Order of work and tests

Every test runs the same input on 1, 2 and 4 ranks of the MPI processor build
(MeshBlocks unchanged) and compares the outputs; the prediction and what would refute
it are in the journal before the run. Figures with `python/nrpic/figstyle.py`.

| Step | Code | Test | Passes if |
|---|---|---|---|
| 0 | none | R0: existing inputs with the serial build of this branch against release `core-v0.3` | output files identical byte for byte |
| 1 | table, ownership, migration, sums, files | T1: test particles on bound and unbound orbits of a Kerr black hole sampled on the mesh (no deposit), crossing rank boundaries, some excised, some leaving; T1p: periodic box with a homogeneous metric | trajectories, the metric at the particles, snapshots and the restart file identical byte for byte; counters equal; particle sums equal to rounding |
| 2 | deposit packets | T2: the same particles with deposit and filter in the fixed metric, clouds cic, tsc, pcs; periodic box | on every rank count: mesh integrals of E, S_i equal the particle sums to rounding (periodic box; open box for clouds inside); source fields equal to those of one rank to rounding |
| 3 | probe, constraint statistics, line and field dumps | T3: a self-gravitating cluster with the spacetime solver on a uniform mesh | histories, constraint statistics and fields agree with one rank to rounding, growing slowly with time |
| 4 | restart write and read | T4: T3 stopped and restarted on the same and on another number of ranks | restarted run equals the uninterrupted one as on one rank |
| 5 | none planned | T5: T2 and T3 on a statically refined mesh; adaptive mesh with load balancing if time remains | as T2, T3 |
| 6 | | card build with MPI, one short run on two cards (one card-hour at most) | runs; agreement with one card within the scatter between two one-card runs |

## 5. Lines of shared files touched (for the merge with the wave-2 branches)

New files (no conflict possible): `athenak/src/particles/nrpic_mpi.cpp` (all code that
runs on several ranks), `nrpic_mpi.hpp` (reductions, search in the table of all
MeshBlocks), `nrpic_cloud.hpp` (the cloud of the deposit as functions). Shared files,
line numbers of this branch (`git diff main...core/mpi`), every hook marked "several
ranks" in a comment:

| File | Lines (branch) | What |
|---|---|---|
| `CMakeLists.txt` | 136 | `particles/nrpic_mpi.cpp` |
| `particles/particles.hpp` | 12; 347-373 | `<cstdio>`; members and declarations of the MPI part (one block after the Newtonian declarations) |
| `particles/particles.cpp` | 113 | `NrpicMpiInit(pin)` after `NrpicInit(pin)` |
| `particles/nrpic.cpp` | 20-22 (comment), 45 (include), 61 (removed: the stop on several ranks), 550, 579 (first lines of `NrpicAssignBlocks`, `NrpicRemoveFlagged`), 708-717, 820-823, 832-835 (deposit kernel: table, level of cloud cells of other ranks, Lorentz factor and level kept), 922 (`NrpicMpiDepositRemote`), 981, 1225-1226 (sums of the deposit and the filter), 1269 (step limit of the whole mesh), 1404 (`NrpicInitializeSources`: particle numbers) |
| `particles/nrpic_io.cpp` | 12 (`<algorithm>`), 32 (include), 42-46 (`NrpicFileWriter`), 143 (probe), 197, 212, 249-264 (history: sums, extrema, numbers of the whole run, rank 0 writes), 288, 291, 326-328 (cells of the whole mesh), 455-459 (constraint statistics), 526-528 (line dump), 591-599, 617-618, 636 (field dump), 810-823 (conservation record), 853-869, 890-892, 958-967, 969, 983-998 (trajectories: rank 0 writes; cells of other ranks asked for), 1010-1011, 1045 (snapshot), 1101-1102 (particle file: rank 0 reads), 1136-1138, 1191-1193, 1202 (restart write), 1211-1212, 1301 (restart read) |

Merge rule [JUDGEMENT]: a wave-2 branch that adds a sum over particles or cells, a file
written per particle, or a mesh array of the module has to add the matching reduction
(`nrpic::MpiSum/MpiMin/MpiMax`), use `NrpicFileWriter`, or be added to the list of
options that stop on several ranks in `NrpicMpiInit` (`nrpic_mpi.cpp`). The kernel of
`NrpicDepositSources` keeps its own copy of the cloud; replacing it by the functions of
`nrpic_cloud.hpp` is a clean-up for after the merge, with a regression run.

## 6. State reached (2026-11-19)

Every number below is from a registered run (manifests under `tracks/core/runs/`,
outputs under `scratch/core/<run_id>/`, `compare.json` in each), with the journal entry
that holds the prediction and the outcome. "Rounding" means differences of the order of
the double-precision rounding of the sums involved.

| Step | Test | Result | Runs (journal entry) |
|---|---|---|---|
| 0 | R0: serial build of this branch against release core-v0.3 (geo, boris, dep, east, os) | identical byte for byte | `tracks/core/analysis/mpi/figs/r0_final_serial.json` (7, 18) |
| 0 | R0: MPI build started on one rank against the release | identical but for 36 bytes of an unset header field of the mesh restart files (uninitialised memory in the release's files) | `figs/r0_final_mpi_one_rank.json` (11, 18) |
| 1 | T1: 2000 test particles in Kerr sampled on the mesh, midpoint and Boris; T1p: periodic box | trajectories, metric at the particles, snapshots, particle restart files identical byte for byte on 2 and 4 ranks; counters exact; sums to 3e-13; 2e3 to 1e4 hand-overs | core-20261119-145615/145630/145644-4c98c59 (3) |
| 2 | T2: deposit and filter in a fixed metric, cic, tsc, pcs, compensated; periodic box and Kerr | mesh integral = particle sum to 1e-14 on 1, 2, 4 ranks; E, S_i at every particle equal to one rank to 8e-16; 6e4 to 4e5 deposit packets | core-20261119-152233/152306/152347/152416/152553/152736-8f245d7 (5, 6) |
| 3 | T3: self-gravitating cluster (4000 particles, Z4c, 8 MeshBlocks meeting at its centre), plain and with extrapolated step sources | positions 4e-15, history 5e-13, field dumps 6e-12 (t = 7.5 M), identity 1e-15; no feature at the planes between ranks | core-20261119-154814-ca46836, core-20261119-155306-ee6c92c (9, 10) |
| 4 | T4: restart at cycle 20 on 1:1, 2:2, 4:4, 1:4, 4:1, 2:4 ranks; restart without a step for all nine pairs | particle restart file written after reading equals the one read byte for byte for all nine pairs; the state after reading is the same for every reader count; restarted runs agree with each other as in T3 | core-20261119-155721/155950-89ebf16, -160825-0e90ab7, -161023-9421947, -161159-421d7e3 (10-13) |
| 4 | caveat, one rank | a restart of this set-up is not exact on one rank either (release too): the mesh restart path refills the ghost cells on the outer boundary, 1e-9 there, 1e-10 in the history after one step | core-20261119-160230-a2f1cf7, -160823-0e90ab7 (11, 12) |
| 5 | T5: deposit on a statically refined mesh (176 MeshBlocks, 3 levels, 10^4 particles), cic, tsc with level cap, pcs | particles identical byte for byte; sources at particles 4e-16; identity 1e-14 on 1, 2, 4 ranks | core-20261119-161206/161208-421d7e3, -161349-896e22c (14) |
| 5 | T5: cluster with Z4c on a statically refined mesh (26 + 8 MeshBlocks) | 2 ranks (all particles on one rank): identical to one rank byte for byte in the particle files; 4 ranks: positions 1e-15, history 3e-13, identity 3e-15 | core-20261119-161503-32b23c0 (16) |
| 5 | T5: refined-mesh deposit with `deposit_adaptive` (cloud level from the last deposit) | particle files identical, sources at particles 5e-16, identity 1e-13 on every rank count | core-20261119-163639-ddb47b0 (20) |
| 5 | T5b: adaptive mesh, refinement at cycle 8 with particles (centred cluster) | same mesh on all rank counts, history 2e-13, positions 1e-15, identity 1e-14; no MeshBlock changed rank | core-20261119-161351-896e22c (15) |
| 5 | T5b: adaptive mesh with MeshBlocks moved by load balancing (cluster in one octant) | 14 (2 ranks) and 45 (4 ranks) MeshBlocks moved at the refinement, 2832 particles handed over with them; history 7e-14, positions 1e-15, identity 6e-15 | core-20261119-161801-9d336d6 (17) |
| 6 | T6: periodic cosmology with Z4c (regression case east at 16^3, 4096 particles, filter, compensation, conformal-time lapse, density sources, field initial data) | positions 1.6e-14, sources at particles 1.3e-14, identity 1e-14 on 1, 2, 4 ranks | core-20261119-163641-ddb47b0 (20) |
| 6 | card build with MPI on two cards | queued (Slurm job 4663, run core-20261119-160452-582824b); not run at the time of writing | (9) |

Not ported (the module stops with a message on more than one rank): Newtonian mode
(`pusher = newton`), collisions, the test kick, curvature records (`curv_dt`). Not tested
on several ranks: horizon excision (`ah_exc_factor`; the horizon finder and the puncture
tracker have their own MPI code upstream, but whether the finder's result is the same on
every rank was not checked), the probes 1 to nprobe (only probe 0; the same function
serves all), the analytic metrics with more than one rank (particles stay on rank 0;
nothing is distributed), load balancing by cost (AthenaK balances
MeshBlocks by number; particles do not enter the cost). Not done: replacing the copy of the
cloud in the deposit kernel by `nrpic_cloud.hpp` (section 5).

Found on the way (not of this package): the one-rank restart departure above; the
conservation record `cons.hst` prints values of order 1e290 in its last two columns for
an isolated cluster (|C^E|/D with D = 0 outside the matter), on one rank already.

## 7. How to run on several ranks

Processors (MPI build; Open MPI 5.0.1 of the machine, found through the run path):

    mpirun --bind-to none -np 4 athena_cpu -i problems/tests/mpi_cluster.athinput \
        -d RUN particles/particle_file=/abs/path/cluster.nrp \
        problem/comp0_file=/abs/path/cluster.tab

- Nothing in the input changes. The same input runs on any number of ranks; the
  MeshBlocks must be at least as many as the ranks.
- Paths of particle files and tables must be absolute (AthenaK works in the output
  directory). An option can be changed on the command line only if the input file has it.
- Files: every file of the module keeps its format and is written by rank 0, particles
  in tag order. New: `<basename>.mpi.hst` (time, cycle, particles handed over and deposit
  packets since the last record, particles on each rank).
- Restart: `mpirun -np M athena_cpu -r RUN/rst/<name>.NNNNN.rst -d RUN2` with any M; rank 0
  reads `<name>.NNNNN.rst.prt` and the first ownership pass distributes the particles.
- Results agree with one rank to rounding, not byte for byte, once the particles act on
  the spacetime (order of additions in cells shared by clouds of several ranks); with a
  fixed metric the particle files are identical byte for byte.
- Cost on processors (wall time of the run on 1 / 2 / 4 ranks, from the logs, on a
  machine loaded to about 90 of 144 cores): cluster T3 (Z4c, 32^3, 4000 particles)
  205 / 127 / 63 s, speed-up 1.6 and 3.2; Kerr swarm T2 (fixed metric, 4000 particles,
  pcs) 155 / 95 / 52 s; refined-mesh deposit T5 (10^4 particles, 176 MeshBlocks) 27 / 15
  / 11 s; adaptive cluster in one octant 118 / 91 / 60 s (the particles crowd onto one or
  two ranks: AthenaK balances MeshBlocks, not particles). The hand-over and the deposit
  packets are host-side MPI messages. 16 cores at most per session on this machine.

Cards: `mpirun -np 2 tracks/core/analysis/mpi/gpu_bind.sh athena_gpu ...` inside a Slurm job
with `--gres=gpu:2` (the wrapper gives each rank its own card); example
`tracks/core/analysis/mpi/card_job.sh`. The particle exchange goes through host memory;
the mesh exchange of AthenaK passes device buffers to the CUDA-aware Open MPI.

## 8. Answer to Track F (request `two-card-or-larger-blocks`)

Option (1), two cards with MPI, is built and published (`scratch/core/exe/core_mpi/athena_gpu`,
with `gpu_bind.sh`), but not yet measured: the card test (job 4663) is queued. It runs
exactly Track F's case D205_m16_r1.8_t+0090.5 of run F-hills-20261115-131348-634fb86
(4502 MeshBlocks of 16^3, twelve levels, here static, three vacuum punctures of masses
0.05, 0.05, 0.5 at the centres of its refined regions:
`problems/tests/mpi_two_card_triple.athinput`) on two cards for ten cycles, and the m/8
mesh of the same case (2332 MeshBlocks) on one and on two cards, and writes the
MeshBlock-cycles per second and the peak memory of each card
(`tracks/core/analysis/mpi/card_analysis.py <output directory>`). The predictions are in
the journal (entry 9, P6c, P6d). On processors the code path is the one tested above;
vacuum Z4c on several ranks is upstream AthenaK code (the smoke test of journal entry 1
ran it on two processor ranks). What Track F can do now: run its mesh-count inputs with
`athena_cpu -m 2` to see the split over two ranks (no allocation), and plan with
`max_nmb_per_rank` per card; the measured rate and memory follow when the job has run.
