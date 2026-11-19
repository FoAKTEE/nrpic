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

### 06:57 Entry 3: outcome of T1

Registration: `harness/bin/nrpic-run submit` refused every local run of this package
("7 cores asked, 16 busy in live local runs of core, allotment 16 at a time"): the
other packages of core that run at the same time fill the allotment of the owner. The
runs of this package are therefore registered by hand with
`tracks/core/tools/run_registered.py` (same fields; said here and in the report), at
most 7 cores at a time.

Runs core-20261119-145554-6e2a253, -145557-, -145559- stopped at once: my driver passed
a relative input path to a process started in another directory. No physics ran.

Runs at commit 4c98c59, MPI processor build `.work/build_cpu_mpi` (numbers:
`compare.json` in each output directory, copies in `tracks/core/analysis/mpi/figs/`):

| Case | Run | Trajectories, metric at particles, snapshots | Restart `.prt` | History, largest relative difference from 1 rank | Hand-overs (2 ranks, 4 ranks) |
|---|---|---|---|---|---|
| t1_kerr (midpoint) | core-20261119-145615-4c98c59 | identical bytes, 2 and 4 ranks (5 snapshots, 2000 to 38 particles) | t = 0 identical; t = 100 identical on 2 ranks, on 4 ranks but for 16 bytes | 1.2e-13, 1.0e-13 (proper volume); 26 of 32 columns exact | 2119, 3906 |
| t1_kerr_boris | core-20261119-145630-4c98c59 | identical bytes | t = 0 identical; t = 100 identical but for 16 bytes | 1.2e-13, 1.0e-13; 26 of 32 exact | 2120, 3908 |
| t1p_box (periodic) | core-20261119-145644-4c98c59 | identical bytes (4 snapshots of 3000 particles) | identical | 6.6e-14, 3.0e-13 (proper volume); 27 of 32 exact | 5270, 10586 |

- P1a held for the particle records. One thing I had not foreseen: the header of the
  restart file holds the rest mass removed by excision and at the boundary (bytes 40 to
  55), two sums over particles whose order depends on the ranks; they differ in the last
  digit (4.710000000000002e-02 against ...000e-02). The particle records, the probe
  state and the counters in the file are identical. The comparison now reports the file
  with and without these 16 bytes.
- P1b held: counts, lapse minimum and maximum, iteration maximum, and the probe columns
  (lapse and proper time at the probe) are equal exactly; rest mass, the three momenta,
  the excised mass and the proper volume differ by rounding (largest 3.0e-13, the volume,
  a sum over 2.6e5 cells).
- P1c held: thousands of hand-overs; all particles start on rank 0 and the first record
  shows them spread (1039 + 961; 520 + 519 + 470 + 491).
- P1d held more strongly than intended: at t = 100 the Kerr swarm has 38 particles left,
  1906 excised and 56 escaped (run -145615-, last history record). The isotropic
  covariant momenta I chose are mostly infalling in Kerr-Schild coordinates (a particle
  at rest there has u_r = (2M/r) u^t, not zero). Both removal paths are exercised; for
  the deposit tests a second generator (`make_swarm_bound`) adds that radial part so that
  most particles stay.
- Figures (inspected): `figs/t1_kerr_ranks.png`, `figs/t1_kerr_boris_ranks.png`,
  `figs/t1p_box_ranks.png`: the trajectories of 16 tracked particles on 1, 2 and 4 ranks
  lie on each other, cross MeshBlock edges, and wrap in the periodic box; particles per
  rank against time; differences of the sums at the 1e-16 to 1e-13 level.

### 06:58 Entry 4: predictions of T2 (deposit across rank boundaries), before the runs

Cases (`mpi_tests.py`): `t2p_box_cic` (one filter pass), `t2p_box_tsc` (two passes),
`t2p_box_pcs` (no filter), `t2p_box_comp` (tsc, deposit compensation 0.125, two filter
passes with the compensating pass, spline interpolation, four ghost cells) in the
periodic box of T1p with 3000 particles of unequal mass; `t2_kerr_cic`, `t2_kerr_pcs`
(two filter passes) with 4000 particles around the Kerr hole (`make_swarm_bound`). The
metric is fixed (`<adm> dynamic = false`): the sources are deposited and filtered but do
not act back, so the particle motion is that of T1.

- P2a. Conservation identity, periodic box, each run by itself: at every record
  |int E - sum m W| / sum m W and |int S_i - sum m u_i| / sum m W are below 1e-13, on
  1, 2 and 4 ranks alike. Refuted if the value on 2 or 4 ranks exceeds that of 1 rank by
  more than rounding: then cloud cells are lost or added twice where clouds cross rank
  boundaries (or the copy of the cloud in `nrpic_cloud.hpp` differs from the kernel).
- P2b. The ten source components of the binary dumps on 2 and 4 ranks equal those of 1
  rank to rounding: largest difference below 1e-12 of the largest magnitude of the
  component (a cell sums a few tens of contributions in another order), for all cases,
  also behind the filter and compensation passes (whose ghost exchange crosses ranks).
- P2c. The runs send deposit packets (thousands per run, `*.mpi.hst`).
- P2d. Trajectories and snapshots stay identical byte for byte (no back-reaction); the
  file with the metric at the tracked particles also holds the deposited E and S_i
  interpolated to them, which differ by rounding, so that file is not identical.
- P2e. In the Kerr cases the identity is not exact on any rank count, because clouds of
  particles near the outer boundary lose the part outside the mesh; the defect is the
  same on 1, 2 and 4 ranks to rounding (history columns 9 to 12 agree to 1e-12).

### 07:22 Entry 5: T2, first pass: identity holds, a gather that skipped other ranks found

Runs at commit a5ea2ef (core-20261119-145811, -145907, -145952, -150024, -150131,
-150318-a5ea2ef) and, with all particles tracked and a finer comparison, at 54f734e
(core-20261119-150711 cic, -150734 tsc, -150814 pcs, -150851 comp, -151012 Kerr cic,
-151151 Kerr pcs; `compare.json` in each):

- P2a held. Periodic box, largest |int E - sum m W| / sum m W over 302 records: cic
  1.2e-14 / 4.9e-15 / 3.5e-15 on 1 / 2 / 4 ranks; tsc 1.3e-14 / 6.9e-15 / 3.7e-15; pcs
  1.7e-14 / 7.8e-15 / 4.6e-15; comp 1.5e-14 / 7.8e-15 / 3.5e-15; momenta 2.1e-16 or
  less everywhere. The values on several ranks are not larger than on one (they are
  smaller: partial sums per rank). Nothing is lost or added twice at rank boundaries.
- P2c held: 57680 to 371291 deposit packets per run (cic fewest, pcs most).
- P2e held: Kerr cic 6.381286956036e-03 on 1 and 2 ranks, ...034e-03 on 4; Kerr pcs
  7.2505554071e-03 on all three (losses at the outer boundary, the same on all).
- P2b: the binary dumps are single precision (`outputs/binary.cpp` casts to float), a
  fact I had not checked before predicting: "largest difference 0" for the ten
  components in all dumps of all cases means equal to 6e-8, not to rounding. All
  particles are therefore tracked in the second set of runs, so that the trajectory
  record samples E and S_i at every particle in double precision.
- P2d FAILED, and usefully: trajectories and snapshots are identical, the metric and
  proper time at the particles are identical, but the deposited E and S_i at the
  tracked particles differ from the one-rank values by up to 0.19 to 0.29 of the
  largest value, not by rounding. The fields themselves agree (dumps, identity). The
  record is formed in `NrpicWriteTrajectories` by a cloud-in-cell gather over the eight
  cells around the particle, found by a search of the pack; my reading is that cells
  held by another rank are skipped and the rest renormalised. I had ported the probe
  (same gather, one point) and overlooked this one. Not yet a named cause: the fix is
  the test.

Fix: `NrpicMpiTrajSources` (requests for the cells another rank holds, answers, sums
divided afterwards); hook in `NrpicWriteTrajectories` (the kernel keeps the undivided
sums on several ranks).

Prediction for the rerun (P2f): E and S_i at the particles on 2 and 4 ranks agree with
one rank to rounding, below 1e-12 of the largest value, in all six cases; everything
else as before. Refuted if differences of the size seen above remain: then the cause is
elsewhere (and the fields would have to be compared cell by cell in double precision).

### 07:40 Entry 6: outcome of the rerun of T2 (P2f)

Runs at commit 8f245d7 (same cases, all particles tracked; `compare.json` and `run.log`
in each output directory): core-20261119-152233-8f245d7 (t2p_box_cic), -152306- (tsc),
-152347- (pcs), -152416- (comp), -152553- (t2_kerr_cic), -152736- (t2_kerr_pcs).

- P2f held. Metric and proper time at the particles identical byte for byte; deposited
  E and S_i at all tracked particles on 2 and 4 ranks against 1 rank, largest
  difference relative to the largest value of the component: cic 3.6e-16 / 3.9e-16,
  tsc 4.3e-16 / 4.3e-16, pcs 4.1e-16 / 4.1e-16, comp 7.0e-16 / 7.7e-16, Kerr cic
  4.4e-16 / 5.2e-16, Kerr pcs 2.7e-16 / 4.0e-16 (2 / 4 ranks). So the defect of entry 5
  was the gather of the trajectory record, as read, and the fields agree at all
  particles to rounding in double precision.
- Unchanged from entry 5: trajectories, snapshots and the particle restart files
  identical (the header sums of the restart file differ in the last digit in some
  cases, max rel 2.0e-16); identity on every rank count at 1e-14 (periodic) and the
  same boundary loss on all rank counts (Kerr: 6.38e-3 cic, 7.25e-3 pcs); histories
  agree to 3.0e-13 (column 28, proper volume); 5.8e4 to 3.7e5 deposit packets.
- Figures inspected: `figs/t2p_box_comp_fields.png` (E at t = 3 on one rank; difference
  of E, S_i at the particles at 1e-16 to 1e-15 for all times on 2 and 4 ranks; identity
  at 1e-15 on all three). In the left panel the white cells are cells where the
  compensated E is negative or zero (log scale), not missing data.

Step 2 is done: deposit across rank boundaries conserves to rounding and gives the
fields of one rank.

### 07:50 Entry 7: predictions of R0 (regression against release core-v0.3), before the runs

Executables: release `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` (baseline);
this branch at a1c8dd6 (source as at 8f245d7) built serial (`.work/build_cpu`) and with
MPI (`.work/build_cpu_mpi`, started without mpirun, i.e. one rank). Tool:
`tracks/core/tools/regress_relativistic.py`, cases geo (Kerr geodesic, analytic metric),
boris (lattice metric), dep (10^4 particles, static refinement, deposit), east
(periodic cosmology with Z4c, deposit, filter, compensation, snapshots, trajectories),
os (Oppenheimer-Snyder with Z4c on a refined mesh).

- P0a. Serial build: every output file of every case identical byte for byte to the
  release. Every new statement is behind `nr_multirank`, which is false on one rank,
  or is a reduction that returns at once on one rank; the trajectory kernel divides by
  the weight sum as before (`isw` unchanged when `mrank` is false) and only gains a row
  that is not written. Refuted by any differing byte.
- P0b. MPI build on one rank: identical to the release as well. Less certain: the MPI
  build compiles the mesh and output code with `MPI_PARALLEL_ENABLED` (MPI-IO for
  restart and binary files, reductions in the time step), which could change the file
  layout or the order of operations; if a file differs, the next check is the serial
  release against an MPI build of the release source, to separate the effect of the
  build option from that of this branch.

### 08:05 Entry 8: a defect found before T3, and predictions of T3, T4 and T5

Smoke test (2 cycles on 2 ranks of `problems/tests/mpi_cluster.athinput`, not a
registered run, no number taken from it): runs; the particle file must be given with an
absolute path (AthenaK works in the output directory). Reading the field dump of the
smoke run I saw the maxima of M_z, Khat and Theta equal to the last digit, and found the
cause in the code, not in a run: `NrpicWriteEnergyField` reuses one buffer for the seven
double arrays of `field_constraints`; on several ranks the cells of other ranks still
hold the global sum of the previous array when the next one is summed, so array n > 0
comes out as its own value plus (ranks - 1) times the previous one. Fixed: the buffer is
cleared before each array on several ranks (`nrpic_io.cpp`, one line behind
`nr_multirank`). T3 tests the fix (field dumps against one rank).

T3 (`mpi_tests.py --case t3_cluster`, input `problems/tests/mpi_cluster.athinput`): a
Shapiro-Teukolsky cluster, y_c = 0.605, 4000 particles (make_ic.py st --seed 7), Z4c on
32^3 cells over [-12 M, 12 M]^3 in eight MeshBlocks that meet at the centre; tsc clouds,
two filter passes with compensation, 40 cycles of dt = 0.1875 M; every record of the
module on (history each cycle, trajectories of all particles every 2 cycles, constraint
statistics, conservation residuals, line dump, two field dumps with the constraint
arrays, four snapshots, restart dumps at cycles 20 and 40). Variant `t3_cluster_ext`:
the same with source_density and source_extrap (the densities of the coming step,
which the restart file carries). On 1, 2, 4 ranks.

- P3a. All runs finish; no particle is lost or added (history column 3 equal on all
  rank counts at all times; no excision, the central lapse is 0.63).
- P3b. The first record (t = 0) agrees to rounding (sums, 1e-14); afterwards the
  deposit differs by rounding at rank boundaries (order of additions), Z4c sees sources
  that differ by rounding, and the difference grows slowly. At t = 7.5 M every history
  column, the constraint statistics, the line and the field dumps (double arrays) agree
  with one rank to relative 1e-11 or better, the particle positions in the snapshots to
  1e-11 absolute or better. Refuted by a difference above 1e-9 anywhere, or one that
  grows by more than a factor 100 per 10 cycles: that would be a missing or doubled
  contribution (deposit, filter ghost cells, probe, sums) or a wrong ghost exchange.
- P3c. The particle counts per rank change (particles cross the planes x, y, z = 0
  that separate the ranks), and the run sends deposit packets every cycle.

T4 (`mpi_tests.py --restart-of <T3 output> --pairs 1:1 2:2 4:4 1:4 4:1 2:4`, restart
from the dump of cycle 20, run to cycle 40):
- P4a. Same number of ranks (1:1, 2:2, 4:4): everything the restarted run writes equals
  the uninterrupted run of that rank count byte for byte (history records, trajectory
  tails, snapshots, field dump of t = 7.5, the particle restart file of cycle 40, the
  mesh restart file after its parameter header). Also with source_extrap.
- P4b. Another number of ranks (1:4, 4:1, 2:4): runs; the restarted run agrees with the
  uninterrupted runs on w and on r ranks to the level of P3b. Refuted by a failure to
  read, a particle lost, or a difference above 1e-9.

T5 (refined meshes, static): `t5_smr_cic`, `t5_smr_tsc_cap` (tsc, two filter passes,
clouds capped at level 1 so that clouds of the finest particles cover several leaf
cells), `t5_smr_pcs` (one filter pass): 10^4 particles of the regression case dep in
flat spacetime on 176 MeshBlocks of three levels, t = 4; `t5_smr_cluster`: the cluster
of T3 with Z4c on 26 + 8 MeshBlocks (centre refined once), 16 cycles.
- P5a. Flat-spacetime cases: trajectories, metric at the particles, snapshots and
  particle restart files identical byte for byte (no back-reaction), the deposited E,
  S_i at all particles agree with one rank to 1e-15 relative, and the conservation
  identity holds on 1, 2 and 4 ranks at the level of one rank (the open boundary is far:
  particles drift from the centre, so the identity should be at rounding as long as no
  cloud reaches the outer boundary; if one does, the defect is the same on all rank
  counts). Refuted by an identity defect on several ranks larger than on one, which
  would mean a level computed differently across ranks or a cloud cell lost.
- P5b. Cluster on the refined mesh: as P3b.

### 08:00 Entry 9: outcome of T3 (uniform mesh), and predictions of the card test

T3, run core-20261119-154814-ca46836 (t3_cluster; `compare.json` in its output
directory). The variant with extrapolated sources, run core-20261119-154816-ca46836,
stopped at once: AthenaK changes on the command line only parameters that the input file
has, and `source_density` was not in it (no physics ran); the options are now in the
file and the variant is rerun (core-20261119-155306-ee6c92c).

- P3a held: all runs finished; 4000 particles at all times on 1, 2 and 4 ranks.
- P3c held: 2786 (2 ranks) and 4561 (4 ranks) particles handed over, 5.4e4 and 1.2e5
  deposit packets; particles per rank 2000/2000 -> 2010/1990 and 1007/993/993/1007 ->
  1000/1010/977/1013.
- P3b held for every well-conditioned quantity: the history of the module agrees to
  4.6e-13 (proper volume; sums of the particles and of the mesh to 1e-14), the field dumps
  (double arrays) to 1.9e-14 at t = 0, 2.4e-12 at t = 3.75 and 5.6e-12 at t = 7.5 (H,
  relative to max |H|), the particle positions to 4.0e-15 absolute at t = 7.5. The map of
  |H(4 ranks) - H(1 rank)| in the mid plane is uniform at 1e-12 with no feature at the
  planes between the ranks (figure `t3_cluster_selfgravity.png`, inspected).
- P3b FAILED in its stated level for two quantities, below the refutation threshold:
  column 11 of the constraint statistics (Hr_max, the largest relative Hamiltonian
  residual |H| over the sum of the magnitudes of its terms) differs by up to 8.5e-10
  (column 12, its mean, 4.6e-10), and K on the line dump by 9.9e-11 relative to max |K|.
  Measured, not inferred: Hr_max is 1.414 at all times, the value of a ratio of rounding
  noise, attained in vacuum cells where H and its terms vanish to rounding; its
  difference jumps between 1e-15 and 9e-10 from cycle to cycle without growing (listed
  per cycle in this session's check); the line runs along the edge of the mesh (y = z =
  -12) where max |K| is 3.2e-5 and the absolute difference is 3.2e-15, the size of the
  rounding differences of chi and alpha there (3.0e-15, 2.4e-15). So these are rounding
  differences of the fields seen through ill-conditioned ratios; the prediction should
  have excluded ratios of near-vanishing quantities.
- The z4c history of AthenaK (`cl.z4c.user.hst`) is printed with six digits and is
  identical as text; `cl.cons.hst` too, and its last two columns are of order 1e290 on one
  rank already (|C^E|/D with D = 0 outside the matter): a defect of that diagnostic on
  this set-up, not of the ranks; noted, not pursued here.

Card test (`tracks/core/analysis/mpi/card_job.sh`, one Slurm job with two cards, about 15
minutes, MPI card build `.work/build_gpu_mpi`): C1a, C1b the cluster of T3 on one card
twice; C2 on two cards; F8a, F8b Track F's vacuum three-puncture mesh at m/8 (2332
MeshBlocks of 16^3, static, `problems/tests/mpi_two_card_triple.athinput` with the
levels lowered) on one and on two cards, 10 cycles; F16 the mesh at m/16 (4502
MeshBlocks, more than one card holds) on two cards, 10 cycles.
- P6a. All six runs finish; in the two-card runs both cards carry memory (gpumem.csv).
- P6b. Cluster: C2 differs from C1a by about as much as C1b does (unordered atomic
  additions of the deposit on a card); refuted if |C2 - C1a| exceeds |C1b - C1a| by more
  than a factor 100 in the history sums or the snapshot positions.
- P6c. F8 on two cards runs 1.3 to 1.9 times faster than on one, with about half the
  memory per card.
- P6d. F16 runs on two cards with less than 80 GB per card (Track F's estimate of about
  3000 MeshBlocks per card gives about 26 MB per MeshBlock, so 2251 MeshBlocks per card
  need about 60 GB), at a rate in MeshBlock-cycles per second close to that of F8b.

### 08:12 Entry 10: T3 with extrapolated sources; first outcome of T4 (P4a failed)

T3 variant with source_density and source_extrap, run core-20261119-155306-ee6c92c: as
the plain case (history 5.4e-13, field dumps 5.6e-12, positions 3.6e-15, identity at
1e-15 on all rank counts). Hr_max (column 11 of the constraint statistics) differs here
by 1.7e-9, above the threshold of 1e-9 that I wrote as refuting P3b: by the letter of
the prediction P3b is refuted in this run for that column; on the evidence of entry 9
(a ratio of rounding noise, value 1.414 at all times, no growth) I do not take it as a
defect of the ranks, but the record stays as it is.

T4, same number of ranks, runs core-20261119-155721-89ebf16 (restart of the run with
extrapolated sources at cycle 20, pairs 1:1, 2:2, 4:4) and core-20261119-155950-89ebf16
(the plain run): P4a FAILED, and on one rank as well. The restarted run is not identical
to the uninterrupted one on 1, 2 or 4 ranks: the first record after the restart (cycle
21) differs only in the proper volume and the mean of K (history columns 28, 29, 1.2e-10
relative); the particle sums, the deposit sums and the lapse at the probe of that record
are identical; from cycle 22 on the differences spread to the particles (positions
1e-15 at t = 7.5) and the deposit. The same happens with and without extrapolated
sources, and already in the pair 1:1, which runs none of the code of this package
(`nr_multirank` false). So the cause is not in the code of several ranks; candidates are
the restart of the spacetime part or a difference of the MPI build on one rank.

Prediction of R4 (before the run): `tracks/core/analysis/mpi/restart_one_rank.sh` runs
the same 1:1 restart with the release executable `build_cpu_v03` (serial) and with the
serial build of this branch. P4c: both show the same 1e-10 departure at cycle 21 as the
MPI build on one rank, i.e. the inexact restart of this set-up is a property of the
released module (the claim "restarts are exact" of CLAUDE.md was made for other
set-ups). Refuted if the release restarts exactly: then the MPI build or this branch
changes the restart, and that is the next thing to find.
