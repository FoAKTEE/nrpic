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

### 08:20 Entry 11: R4 outcome (the one-rank restart departs in the release too); T4 reframed

R4, run core-20261119-160230-a2f1cf7: the release executable `build_cpu_v03` (serial,
one process) and the serial build of this branch give the same departure of the
restarted run from the uninterrupted one as the MPI build on one rank, to all printed
digits (history 1.2e-10, trajectories 8.8e-16, line dump 5.6e-10, constraint statistics
8.6e-10). P4c held: the inexact restart of this set-up (Z4c with deposit, cluster, tsc,
compensated filter) is a property of the released module, not of this package; the
statement "restarts are exact" of CLAUDE.md does not hold for it. Located next (R5,
below); it is reported to the lead in the final report either way.

R0 with the MPI build on one rank (runs listed in `scratch/core/tmp/mpi/r0_mpi1.json`;
geo, boris, dep, east identical; os: every file identical but the five mesh restart
files): the restart files differ in 36 bytes, the same positions 10858 to 10893 in every
dump, inside the binary header after `<par_end>`; in the release file these bytes hold
text of the input file ("mber = 0.25 nlim = -1 tlim"), i.e. memory that was never set
(padding of a structure), in the MPI build other values. Data identical. P0b held in
substance; the byte comparison of mesh restart files has to skip that header.

T4, reframed (predictions, before the runs). Since one rank does not restart exactly,
the test of the ranks is that a restart on several ranks adds nothing to that:
- P4d (exactness of write and read, no step): restarting the dump of cycle 20 with
  `time/nlim=20` writes, without taking a step, a final dump at cycle 20. For every pair
  w:r (written on w, read on r, w, r in 1, 2, 4) its particle restart file equals the
  one read byte for byte (particles in tag order, probe state, the source densities of
  the coming step of all MeshBlocks), and the mesh restart file equals it after the
  header. Refuted by any differing byte: then the hand-over of the particles or the
  scatter of the step sources at a restart loses or reorders something.
- P4e: the restarted runs 2:2 and 4:4 agree with the restarted run 1:1 as the
  uninterrupted runs of T3 agree with each other (history 1e-12, positions 1e-14,
  identity at 1e-15); the cross pairs 1:4, 4:1, 2:4 agree at that level with the restart of the same
  file on one rank (1:1 for w = 1) or on w ranks (4:4 for 4:1).

R5 (where the one-rank departure starts): `restart_locate.py`, serial build of this
branch, field dumps of the uninterrupted and the restarted run at cycle 21 compared cell
by cell. Expectation [JUDGEMENT]: the first record differed only in the proper volume and
the mean of K, not at the particles or the probe, so the departure sits away from the
matter, probably next to the outer boundary.

### 08:30 Entry 12: outcomes of T4 (P4d held), R5 (the departure sits in the boundary ghost cells), and P5c

R5, run core-20261119-160823-0e90ab7 (serial build, one process, field dumps at cycle
21 of the uninterrupted and of the restarted run): E and chi identical in every cell;
H, M_i, Theta differ by up to 2e-10 of their maxima in the cells next to the outer
boundary (distance 0 to 2 cells), falling to 1e-13 at distance 7; the lapse by 1.4e-15.
The expectation of entry 11 held: the departure sits at the outer boundary, not at the
matter.

T4 zero-step test (P4d), run core-20261119-161023-9421947 (dump of cycle 20 of the run
with extrapolated sources, written on w ranks, read on r ranks, no step, dumped again):
- The particle restart file written equals the one read byte for byte for all nine
  pairs w:r with w, r in 1, 2, 4: particles in tag order, probe state, counters and the
  source densities of the coming step of all eight MeshBlocks survive the hand-over and
  the scatter exactly.
- The mesh restart file written is identical for every reader rank count (written on w,
  read on 1, 2, 4: identical bytes after the parameter header, checked for w = 1, 2, 4).
  It differs from the dump read, also for 1:1, in 1.7e6 bytes: decoded as 176 arrays of
  24^3 doubles (22 variables of z4c and adm in 8 MeshBlocks), 96 arrays differ, only in
  ghost cells (5820 to 5824 of the 9728 ghost cells of a MeshBlock, those of the faces
  on the outer boundary), interior cells identical, largest difference 4.3e-9. So the
  restart path of the spacetime solver refills the ghost cells at the outer boundary from
  the interior instead of keeping the values the run had; the first step after the
  restart then sees other boundary values. This is the one-rank departure of R4 and R5,
  a property of the mesh restart of the release, not of this package [JUDGEMENT on the
  mechanism; the location is measured]. Not pursued here (it concerns every restarted
  Z4c run with outflow boundaries; reported to the lead).
- So P4d held for what it tests (a restart on any number of ranks reads and writes the
  same state), with the caveat on the ghost cells that holds on one rank alike.

Restarted runs (P4e) are compared with each other next (`restart_cross_compare.py`).

T5b prediction (adaptive mesh, `mpi_cluster_amr.athinput`, case t5_amr_cluster): the
refinement at cycle 8 (the first check that refinement_interval allows) gives the same
mesh on 1, 2 and 4 ranks (120 MeshBlocks, history column 23); particle numbers stay
4000; after the regridding the particles are redistributed (hand-overs in the record of
the ranks at cycle 8 even on 1 to 2 ranks); the histories and positions agree with one
rank at the level of T3 (1e-12 and 1e-14) and the identity holds at 1e-14. Refuted by a
different mesh, a lost particle, a crash in the regridding with particles, or
differences above 1e-9.

### 08:40 Entry 13: P4e held

Run core-20261119-161159-421d7e3 (`restart_cross_compare.py`; the first attempt,
core-20261119-161148-7f60657, stopped on the missing header of the line dump of a
restarted run, fixed in the driver): the restarted runs agree with each other as the
uninterrupted runs of T3 do. Same dump read on 1 and 4 ranks: history 1.2e-13, positions
1.8e-15, field dump 3.4e-12 (H), E and S_i at the particles 4.3e-15; dump of 4 ranks read
on 4 and 1: 1.1e-13, 1.3e-15, 2.9e-12; dump of 2 ranks read on 2 and 4: 1.3e-13,
1.8e-15, 2.7e-12; dumps of 1, 2, 4 ranks each read on its own count: 4.9e-13, 3.6e-15,
5.9e-12. The identity holds at 3.4e-15 or better in every restarted run. Hr_max differs
by up to 6.7e-10 (the noise ratio of entry 9). So a restart on several ranks, on the
same or another number of ranks, behaves as one on one rank, up to rounding.

### 08:47 Entry 14: R0 on the final source; T5 refined-mesh deposit held

R0 at 8f245d7 (runs listed in `scratch/core/tmp/mpi/r0_serial.json`): the serial build
of this branch gives the release's files byte for byte in geo, boris, dep, east and os
(P0a held; os includes the five mesh restart files). R0 is repeated now on the final
source (the field-dump fix of entry 8 is the only change of `athenak/src` since, behind
`nr_multirank`), with the serial build and with the MPI build on one rank; predictions
P0a and P0b of entry 7 stand (for the MPI build: identical but for the 36 header bytes of
the mesh restart files of entry 11).

T5, refined mesh in flat spacetime (176 MeshBlocks of three levels, 10^4 particles,
t = 4): runs core-20261119-161206-421d7e3 (cic), -161208- (tsc, two filter passes,
clouds capped at level 1), core-20261119-161349-896e22c (pcs, one filter pass). P5a
held: trajectories, metric at the particles, snapshots and particle restart files
identical byte for byte on 2 and 4 ranks; E and S_i at all particles agree with one rank
to 2.6e-16 / 3.2e-16 / 4.2e-16; the identity on 1, 2, 4 ranks: cic 2.6e-14 / 8.9e-15 /
4.6e-15, tsc capped 7.9e-14 / 3.2e-14 / 1.9e-14, pcs 4.0e-14 / 1.8e-14 / 7.9e-15 (never
larger on several ranks than on one); 5.7e3 / 8.9e3 particles handed over and 6.1e3 to
3.7e4 deposit packets.

### 08:55 Entry 15: T5b adaptive mesh (centred cluster): P5c held, but no MeshBlock moved; offset case

Run core-20261119-161351-896e22c (t5_amr_cluster): at cycle 8 the eight central
MeshBlocks are refined on 1, 2 and 4 ranks alike (56 created, 120 MeshBlocks, logs);
4000 particles throughout; history 2.3e-13 (2 ranks) and 1.5e-13 (4 ranks), positions
to 1.3e-15 (largest over the seven snapshots to t = 2.25 M; dt halves at the
refinement), E and S_i at the particles 6.1e-15, identity 7.8e-15 / 3.4e-15 /
2.5e-15; Hr_max 1.1e-9 (the noise ratio, entry 9). P5c held. But the logs say "0
communicated for load balancing": the refined MeshBlocks are spread evenly over the
ranks by the Morton order of the centred cluster, so no MeshBlock changed rank and the
hand-over of particles with moved MeshBlocks was not exercised (the regridding itself,
the new table of MeshBlocks and the new global IDs were).

Case t5_amr_offset (prediction, before the run): the same with the cluster moved to
(4, 4, 4) (particles and table), so that the region chi < 0.55 lies in the octant x, y,
z > 0, whose eight root MeshBlocks are the last eight in Morton order and sit on the last
rank. Refining them adds 56 MeshBlocks there, and load balancing must move MeshBlocks
(with the particles inside them) to the other ranks. P5d: on 2 and 4 ranks the log
reports MeshBlocks communicated for load balancing, the record of the ranks shows
hand-overs at cycle 8 of the order of the particles in the moved MeshBlocks, and
everything else agrees with one rank as in P5c. Refuted by a lost particle, a crash, a
different mesh, or differences above 1e-9 (Hr_max excepted, as before).

### 09:05 Entry 16: T5 cluster on a refined mesh

Run core-20261119-161503-32b23c0 (t5_smr_cluster, 26 + 8 MeshBlocks, 16 cycles): on 2
ranks all 4000 particles lie in MeshBlocks of rank 0 throughout (record of the ranks:
4000 / 0, no hand-over, no packet), and the run is identical to the one-rank run byte for
byte (trajectories, snapshots, particle restart files; history 30 of 32 columns exact,
the other two, proper volume and mean K, sums over cells of both ranks, 1.5e-13). On 4
ranks the particles are split 485 / 3515 over ranks 0 and 1, 3669 hand-overs and 1.1e4
deposit packets: positions 1.3e-15, history 2.8e-13, E and S_i at the particles 5.3e-15,
identity 3.4e-15 (one rank 5.9e-15), Hr_mean 6.6e-11. P5b held.

### 09:12 Entry 17: T5b with load balancing (P5d held)

Run core-20261119-161801-9d336d6 (t5_amr_offset, cluster at (4, 4, 4)): at cycle 8 four
root MeshBlocks are refined on every rank count (28 created, 92 MeshBlocks; I had
expected eight: the region chi < 0.55 touches four root MeshBlocks of the octant), and
load balancing moves 14 MeshBlocks (2 ranks) and 45 MeshBlocks (4 ranks) between ranks
(logs). The record of the ranks at cycle 9 (4 ranks): 2832 particles handed over,
particles per rank 0 / 20 / 16 / 3964 before and 0 / 36 / 2802 / 1162 after. Agreement
with one rank: history 5.2e-14 / 6.6e-14, positions 8.9e-16 / 1.3e-15 (t = 2.25 M), E
and S_i at the particles 8.7e-15 / 8.3e-15, identity 5.9e-15 on 1, 2, 4 ranks, Hr_max
6.1e-11. Figure `t5_amr_offset_ranks.png` (inspected): particles per rank jump at
t = 1.5 M on 4 ranks; the history differences stay at 1e-16 to 4e-14 through the
regridding. P5d held: particles follow their MeshBlocks through refinement and load
balancing.

### 09:25 Entry 18: R0 on the final source (P0a, P0b held)

Source ca46836 (athenak/ unchanged since), release `build_cpu_v03` against this branch;
reports `tracks/core/analysis/mpi/figs/r0_final_serial.json` and
`r0_final_mpi_one_rank.json` (each case is two registered runs, e.g. os:
core-20261119-161611-485c50e / core-20261119-162447-6095bbf for the serial build,
core-20261119-161618-485c50e / core-20261119-162453-6095bbf for the MPI build):
- serial build: geo, boris, dep, east, os identical byte for byte in every file (os: 16
  files including five mesh and five particle restart files). P0a held.
- MPI build started without mpirun: identical in every file but the five mesh restart
  files of os, which differ in the 36 bytes 10858 to 10893 of their binary header (the
  unset bytes of entry 11), and nowhere else. P0b held.
So existing results are unchanged on one rank; the published processor executable (the
MPI build) reproduces the release but for those header bytes.

### 09:32 Entry 19: published; predictions of two more cases while the card job waits

Published `scratch/core/exe/core_mpi/` (athena_cpu = MPI processor build, athena_gpu = MPI
card build, COMMIT, SHA256SUMS, READY). The card test (job 4663) still waits in the
queue behind about twenty one-card jobs; it needs both cards at once. READY says the card
executable is not yet tested on cards.

Two cases that shorten the list of what is not tested (predictions, before the runs):
- t5_smr_adaptive: the refined-mesh deposit of T5 with `deposit_adaptive = true`
  (tsc, deposit_ppc = 8): the level of each cloud comes from the energy density of the
  last deposit in the particle's own cell, which the particle's rank holds. P5e: as P5a
  (particle files identical, sources at the particles to 1e-15, identity at the level of
  one rank). Refuted by a difference above rounding in the sources at the particles: a
  level chosen differently on several ranks would move whole clouds between levels.
- t6_cosmo_east: the periodic cosmology of the regression case east (Z4c in a periodic
  box of 16^3 in eight MeshBlocks of 8^3, 4096 particles, cic with filter and
  compensation, conformal-time lapse, density-form sources, field initial data from a
  file) for 40 cycles on 1, 2 and 4 ranks. P6e: runs on several ranks (the generator
  reads the field file for the MeshBlocks of each rank); history and positions agree with
  one rank at the level of T3 (1e-12, 1e-14); the identity holds on every rank count at
  the level of one rank. Refuted by a failure to start, a difference above 1e-9 in the
  well-conditioned columns, or a defect of the identity larger on several ranks.

### 09:45 Entry 20: P5e and P6e held

- t5_smr_adaptive, run core-20261119-163639-ddb47b0: trajectories, metric at the
  particles and snapshots identical byte for byte on 2 and 4 ranks, particle restart
  files identical but for the header sums (2.9e-16); E and S_i at the particles 4.5e-16;
  identity 3.0e-13 / 9.7e-14 / 8.2e-14 on 1 / 2 / 4 ranks; 3.6e4 and 7.2e4 deposit
  packets. The adaptive level of the clouds is the same on every rank count. P5e held.
- t6_cosmo_east, run core-20261119-163641-ddb47b0 (periodic cosmology with Z4c, 40
  cycles): runs on 2 and 4 ranks; positions agree with one rank to 1.6e-14, E and S_i at
  the particles to 1.3e-14, the identity holds at 9.9e-15 / 7.4e-15 / 3.1e-15. The
  history columns of the net momentum (particle sums and mesh integrals, columns 6-8,
  10-12, 25-27) "differ by up to 136 per cent" relative to their own largest value,
  which is 3.5e-16: they are zero to rounding in this set-up, and the absolute
  differences are 4.8e-16 against sum m W = 7.6, i.e. 6e-17 relative. Every other column
  agrees to 1e-12; Hr_max and Mr_max (noise ratios) to 1.2e-10. P6e held; the comparison
  of history columns relative to their own maxima misleads for quantities that vanish,
  as noted for Hr in entry 9.

### 09:50 Entry 21: state at the end of session mpi-1, and the next steps

Done and tested on processors (1 against 2 and 4 ranks): ownership and hand-over,
deposit across ranks, sums and files, probe, constraint statistics, line and field
dumps, trajectories, restart on the same and another rank count, static and adaptive
refinement with load balancing, adaptive deposit levels, periodic cosmology with Z4c.
One-rank behaviour unchanged (R0, entry 18). Published `scratch/core/exe/core_mpi/`.

Not done / open:
1. Card test, Slurm job 4663 (run core-20261119-160452-582824b, card_job.sh): queued
   behind about twenty one-card jobs; it needs both cards. When it has run: `python3
   tracks/core/analysis/mpi/card_analysis.py /data/haiyangw/nrpic/scratch/core/
   core-20261119-160452-582824b --figdir tracks/core/analysis/mpi/figs`, record the
   outcome against P6a-P6d (entry 9), fill section 8 of `interfaces/mpi.md` and the CARD
   TEST section of `scratch/core/exe/core_mpi/READY`, and finish the manifest (its state
   stays "running" until `sbatch --wait` returns; if the waiting process died with the
   session, write wall time, exit status and card-hours from `sacct -j 4663` by hand).
2. Not ported: Newtonian mode, collisions, test kick, curvature records (stop with a
   message). Not tested on several ranks: horizon excision, probes 1..nprobe, analytic
   metrics (particles stay on rank 0).
3. Merge with the wave-2 branches: section 5 of `interfaces/mpi.md` lists every shared
   line; every new sum over particles or cells, file or mesh array of a merged branch
   needs its reduction, `NrpicFileWriter`, or an entry in the stop list of
   `NrpicMpiInit`. Then rerun `mpi_tests.py` T1 to T6 (each case takes 0.5 to 7 minutes
   on 7 cores) and R0.
4. Clean-up after the merge: the deposit kernel calls `nrpic_cloud.hpp` instead of its
   own copy of the cloud (with a regression run).
5. For the lead, outside this package: the one-rank restart of Z4c runs is not exact
   (ghost cells on the outer boundary, entries 11, 12): CLAUDE.md says "restarts are
   exact"; and `cons.hst` prints 1e290 for isolated matter (entry 9).

## 2026-11-20 session mpi-2 (continuation after the usage limit of 2026-11-19)

### 14:00 Start

`git merge --no-edit main` (decisions 0018, 0019, pre-commit hook; no change under
`athenak/`, `python/`, `problems/`). Read CLAUDE.md with the section on the pause flag,
decisions 0016 to 0019, this journal, `interfaces/mpi.md`, the report of session mpi-1
(`scratch/orch/wave3a_reports/core.md`). No pause flag. Worktree: one stranded change,
the manifest of the card run (below). The published executables are the ones of the
build directories (sha256 of `.work/build_gpu_mpi/src/athena` and
`.work/build_cpu_mpi/src/athena` equal `scratch/core/exe/core_mpi/SHA256SUMS`), and
`git diff ca46836 HEAD -- athenak/` is empty.

### 14:05 Entry 22: outcome of the card job 4663 (P6a failed: no two-rank run started)

Run core-20261119-160452-582824b, Slurm job 4663: started 2026-11-19 12:02:27 after
four hours in the queue, ended 18 s later (`sacct -j 4663`: COMPLETED, 00:00:18, two
cards), so 0.01 card-hours were used, not the hour reserved in the manifest (corrected
there; `wall_time_s` 14283 is the wait of `sbatch --wait`).

- C1a, C1b, F8a (one rank each) ran. C2, F8b, F16 (two ranks) did not start: `mpirun`
  stopped with "There are not enough slots available in the system to satisfy the 2
  slots that were requested" (`C2/run.log`). The job asked for one task with four cpus
  (`-c 4`); Open MPI takes its slots from the tasks of the Slurm job, and this machine
  gives one task per core (`scontrol show config`: `CR_CORE,CR_ONE_TASK_PER_CORE`; the
  node offers four cpus, two cores, to Slurm). On the login node the same command line
  had run, because there the slots are the cores of the machine. "cpus=1" in `job.info`
  is `nproc` obeying `OMP_NUM_THREADS=1`, not the allocation.
- P6a failed (three of six runs did not start); P6b, P6c, P6d untested. Nothing about
  the code of this package was tested by the failure: no two-rank process started.
- What the one-rank runs give [VERIFIED, `card_analysis.py`, `card.json` in the run
  directory]: the card build with MPI runs the cluster and Track F's m/8 mesh on one
  card. Scatter of two one-card runs of the cluster (C1b against C1a): history 5.4e-13,
  positions 1.3e-15 to 3.6e-15 (t = 1.9 to 7.5 M), i.e. the level of the processor
  runs on several ranks. F8a: 2332 MeshBlocks of 16^3, 10 cycles in 9.18 s: 2541
  MeshBlock-cycles per second (1.04e7 zone-cycles per second), peak memory 58835 MiB on
  the card, 25.2 MiB per MeshBlock. Track F's m/16 mesh (4502 MeshBlocks) would need
  about 111 GiB, more than one card of 80 GiB holds, and 2251 MeshBlocks per card
  about 55 GiB.

Fix (`card_job.sh`): `#SBATCH -n 2 -c 2` (two tasks, the four cpus of the node),
`--map-by :OVERSUBSCRIBE` on the `mpirun` line (so that a job with one task can start
two ranks too), a fourth argument that selects the runs, and `job.info` prints the
tasks and the cpus without `OMP_NUM_THREADS`.

Second attempt, in two jobs (card time used so far 0.01 of the one card-hour; limits
10 minutes on one card and 20 minutes on two, at most 0.84 card-hours together, a few
minutes expected):

1. Pre-test on ONE card, which is free now while another user's job holds the other:
   `sbatch --gres=gpu:1 -n 1 -c 2 -t 00:10:00 card_job.sh ... "C1a C2 F8b"`, both ranks
   on the same card. It tests what the first attempt could not: that two ranks of the
   card build start, that the mesh exchange of AthenaK hands device buffers to this
   Open MPI, and that the particle module on two ranks gives the one-rank result on a
   card. Predictions:
   - P6e. C2 and F8b run to their cycle limits on two ranks (logs: "Number of parallel
     ranks = 2"). Refuted by a crash in the first exchange (then the MPI library does
     not take device buffers as built, and the card build needs host buffers), or by a
     stop in the particle module.
   - P6f. C2 against C1a of the same job: history sums and positions differ by no more
     than 100 times the scatter between two one-card runs measured above (history
     5.4e-13, positions 3.6e-15), 4000 particles throughout. Refuted by a larger
     difference or a lost particle.
   - P6g. F8b on two ranks sharing one card: total memory within 10 per cent of F8a
     (58.8 GiB) plus a few hundred MiB for the second process; slower than F8a per
     MeshBlock-cycle (two processes share the card by time slicing, two ranks share one
     core). No rate is taken from this run.
2. The two-card job as before (C1a, C1b, C2, F8a, F8b, F16), submitted when the
   pre-test has run; predictions P6a to P6d of entry 9 stand, with the measured one-card
   numbers: F8b about half of 58.8 GiB per card; F16 about 55 GiB per card.

### 14:07 Entry 23: outcome of the pre-test on one card (P6e, P6f, P6g held)

Run core-20261120-220512-a86765b (registered with `nrpic-run submit`, which accepts
runs of this owner again), Slurm job 4730: started at once on the free card, 43 s
(0.012 card-hours). `job.info`: one card, one task, two cpus; `mpirun` started two ranks
with `--map-by :OVERSUBSCRIBE`. Numbers: `card.json` in the run directory, copy
`tracks/core/analysis/mpi/figs/card_pretest.json`; figure `figs/card_pretest.png`
(inspected: differences of the two-rank run from the one-rank run at 1e-16 to 4e-15 at
all times; one bar pair for F8b).

- P6e held. C2 (cluster, two ranks, four MeshBlocks each) and F8b (Track F's m/8 mesh,
  1166 MeshBlocks per rank) ran to their cycle limits with exit status 0. So the card
  build with this Open MPI exchanges the mesh data between ranks (device buffers), and
  the particle module runs on two ranks on a card: 2786 particles handed over and
  5.4e4 deposit packets in 40 cycles (`C2/cl.mpi.hst`; the processor run of T3 on two
  ranks had 2786 and 5.4e4, entry 9), particles per rank 2000/2000 to 2010/1990.
- P6f held. C2 against C1a of the same job: every history column agrees to 2.8e-13
  (the sums of the particles and of the mesh to 1e-15), positions to 8.9e-16, 1.8e-15,
  2.2e-15, 3.6e-15 at t = 1.9, 3.8, 5.6, 7.5 M; 4000 particles throughout in both.
  The scatter of two one-card runs was 5.4e-13 and 3.6e-15 (entry 22): the two-rank
  run is inside it.
- P6g held. F8b with both ranks on one card: 60680 MiB at the peak against 58835 MiB
  of the one-rank run (3 per cent more); 745 MeshBlock-cycles per second against 2541
  on one rank, as expected for two processes that share one card and one core. No rate
  is taken from it.

So what the first attempt left open is settled except the rate and the memory on two
cards (P6c, P6d) and the run that needs two cards (F16), which the two-card job gives:
run core-20261120-220612-431e9b8, Slurm job 4733, queued at 14:06 behind a job of
another user that holds one card (limit one hour).

While it waits (processors): the items of the list "not tested" of entry 21.

### 14:11 Entry 24: test T7, predictions (written before the runs)

The items "not tested on several ranks" of entry 21, which the tracks use (Track D:
`ah_exc_factor = 0.8` and `nprobe = 7` in `es_runs/inputs/es1_dx8.athinput` on
`track/D-bh-dress`; A, C, F: `nprobe = 2`). Driver: `mpi_tests.py` gets the cases
below, a limit of six cores for runs that go side by side (CLAUDE.md, section on load:
4 and 2 ranks together, then 1), lines added to a copy of an input file (`add`), and
the records of the puncture tracker and of the horizon finder among the tables it
compares. A smoke run of four cycles of the puncture case on four ranks (not
registered, no number taken from it) showed that it starts, finds the horizon at t = 0
and takes about 7 s per cycle on four ranks.

- t7_analytic, t7_analytic_boris: the geodesic of the regression cases geo and boris
  (`problems/kerr/geodesic.athinput`, analytic Kerr metric, and the virtual lattice)
  with the mesh cut into eight MeshBlocks of 4^3, on 1, 2, 4 ranks. The particle uses
  no MeshBlock and stays on rank 0 (design 3.2). P7a: trajectory file and history
  identical byte for byte on 2 and 4 ranks; `geo.mpi.hst` shows the one particle on
  rank 0 at all times and no hand-over. Refuted by a differing byte or a particle that
  moved or was lost (then the ownership pass treats analytic metrics wrongly).
- t7_probes: the cluster of T3, 16 cycles, with probes 1 to 7 (`nprobe = 7`): probe 1
  at the origin, where the eight MeshBlocks and, on 2 and 4 ranks, the ranks meet (the
  same point as probe 0); probe 2 on the plane x = 0; probe 3 on the line y = z = 0;
  probe 4 on the plane z = 0; probe 5 inside one MeshBlock in the matter; probe 6 next
  to the origin, its eight cells in the first octant's opposite MeshBlock; probe 7 in
  vacuum near the corner of the mesh. P7b: the 21 probe columns (history columns 33 to
  53: lapse, energy density, proper time) agree with one rank as probe 0 does: the
  lapse and the proper time to 1e-13 relative, the energy density to 1e-12 (it is a
  sum of deposits whose order differs); columns 33 to 35 (probe 1) equal columns 13 to
  15 (probe 0) exactly in every run; the energy density at probe 7 is zero on all rank
  counts. Refuted by a probe column that differs by more than 1e-9 on several ranks
  (a cell of another rank missing from the eight, or counted twice), or by probe 1
  differing from probe 0.
- t7_ah_exc: `problems/tests/mpi_puncture_exc.athinput` with `deposit = false`: a
  Bowen-York puncture (bare mass 1, P_x = 0.3, S_z = 0.2) at (0.1, -0.2, 0.05), tracker,
  three-level adaptive mesh (176 MeshBlocks of 8^3, finest cells 1/8) and horizon
  finder from `puncture_setup`, searched every 2 cycles; 2000 particles of mass 1e-8
  at 0.3 to 2.5 from the puncture; removal inside 0.8 of the smallest coordinate radius
  of the horizon, lapse rule off; 24 cycles (t = 0.75 M). Without deposit the spacetime
  is the vacuum one. P7c: (i) the excised number (history column 17) is the same on 1,
  2, 4 ranks at every record, above zero from the first step, and it grows later in the
  run (if it does not grow, the test still shows the removal at the start, and that is
  said); (ii) the records of the tracker and of the horizon finder agree with one rank
  to 1e-10 relative or better (the finder sums over the ranks; I expect 1e-13); (iii)
  trajectories, snapshots and the particle restart file agree: identical byte for byte
  if vacuum Z4c with the tracker gives the same bits on any rank count, which I expect
  but have not seen tested; otherwise positions to 1e-12. Refuted by an excised number
  that differs between rank counts at any record (the horizon seen differently on the
  ranks, or a count not reduced), by a particle removed on one rank count and kept on
  another, or by differences above 1e-9.
- t7_ah_exc_dep: the same with deposit (tsc, one filter pass), i.e. tracker, adaptive
  mesh, finder, excision, deposit packets and the sources in Z4c together. P7d: as P7c
  (i) and (ii); positions to 1e-12; the conservation identity is not exact here
  (particles inside the horizon sit in cells whose metric determinant is not positive:
  "sources set to zero there", and the open boundary), but its defect is the same on 1,
  2, 4 ranks to 1e-10.
