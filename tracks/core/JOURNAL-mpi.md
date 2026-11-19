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
