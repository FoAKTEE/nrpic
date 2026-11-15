# Requests of tracks D, A and F that are not gauge: triage and what was done

Work package dfix of core, branch `core/requests-adf`, 2026-11-15. Journal with the
predictions and outcomes of every test: `tracks/core/JOURNAL-dfix.md`. Tests T1 to T6:
scripts and case lists under `tracks/core/analysis/dfix/`, figures under
`tracks/core/analysis/dfix/figs/`, run manifests under `tracks/core/runs/`.
Labels: [VERIFIED] read or measured in this package (locator given), [JUDGEMENT],
[TO VERIFY].

## 1. Triage

| # | Request (outbox file of the track) | Ruling | Reason, and what exists now |
|---|---|---|---|
| D1 | `tracer-push-release-build` (blocker) | ACCEPTED, done | A defect of the released source, not of the card build: section 2.1 |
| D2 | `restart-skips-dump` | ACCEPTED, done | Section 2.2 |
| D3 | `accretion-diagnostics` items 1, 2, 4 | ACCEPTED, done | Section 2.3 |
| D3 | `accretion-diagnostics` item 3 (proper time per particle) | EXISTS for the midpoint pusher on the mesh metric | `IPTAU` is advanced by `PushMidpoint` (`nrpic_kernels.hpp`, `dtau = dt alpha/W`), written in the snapshots (last block of N doubles), in field 13 of `<basename>.trajmet.bin` and in the restart file; now also field 11 of the removal record. Not advanced by the Boris pusher nor on the analytic metrics (their branches call the six-argument `PushMidpoint`): DEFERRED, it changes the snapshots of existing analytic runs and nobody asked for those |
| D4 | `analytic-metric-excision` | ACCEPTED, done | Section 2.3 (lapse threshold and removal on the analytic metrics, counted in the history). Track D's own acceptance run (`spike_lc.nrp`, 1200 particles) is Track D's to run; the equivalent exact test T3 passes |
| D5 | `newtonian-mode-point-mass` item 1 (fixed point mass) | ACCEPTED, done | Section 2.4 |
| D5 | item 2 (card throughput at 256^3, 384^3 with 2e6 particles; multigrid on refined meshes) | DEFERRED to core's verify package | A benchmark, not a source change; the card queue held this package's jobs for the whole session. Multigrid on refined meshes stays "a trial, not verified" (`problems/newton/README.md`) |
| D5 | item 3 (pericentre counter in the Newtonian mode) | ACCEPTED, done | Same counter as D3 item 4, test T4 |
| D6 | `puncture-on-torus` (proposal, wave 3) | DEFERRED to wave 3 | Needs the elliptic solve on the mesh with a puncture in a periodic box (package idsolve of this wave is its base) and the periodic gauge near a hole (package gauge). No source of this package helps or hinders it |
| A1 | `newton-mode-and-ball-ic` item 1: isolated boundary values | EXISTS in core-v0.3 | `<gravity> mg_bc = multipole` (`problems/newton/isolated.athinput`) |
| A1 | item 1: external acceleration of the background | ACCEPTED, done | `newton_bg_t0` (section 2.4): it shares the hook of the point mass |
| A1 | item 1: special-relativistic push | DEFERRED | A change of the kick-drift-kick kernel with its own conservation laws (energy sum, Layzer-Irvine integral) and tests; not needed for the first scan (SCAN.md: 4 to 5 per cent at delta_L = 0.3). Next package of the Newtonian mode |
| A1 | item 1: snapshots at chosen times; second moments per species | PARTLY EXISTS / DEFERRED | Snapshots every `snap_dt` exist; chosen times and per-species moments are output work for the same later package (the history holds the moments of all particles) |
| A2 | item 2: Zel'dovich-deformed ball in `problems/ic/make_ic.py` | DEFERRED, date: next core session after this wave's merge | Python initial-data work of its own size (model, shell species, rotation, metadata); the formulas are in Track A's `newton/SCAN.md` section 4 |
| A3 | item 3: halting tests | Track A runs them | They are acceptance tests of the mode by the track (decision 0010); the mode needs nothing more for them than isolated boundaries, which exist |
| F1 | `pairwise-common-horizon` | ACCEPTED, done | Section 2.5 |
| F2 | `hrna-pair-force-optional` | ACCEPTED FOR A LATER WAVE | Optional by the request; an O(N^2) pair force inside the pusher kernels is a new operator (interface rule 2 of `pusher.md`: between push and deposit) and needs F's four acceptance tests. Nothing in this package blocks it |
| F3 | `two-card-or-larger-blocks` | ASSESSED, not started | Section 3: estimate for more than one rank. Larger MeshBlocks need no source change; the benchmark of 32^3 MeshBlocks was prepared (`cases/card_checks.list`, cases bench16, bench32) but did not run within this package's card hour: Track F can run it with the release |
| F4 | `release-multi-puncture` | ANSWERED | Release `core-v0.3`, tag at 609a875, is merged into main (decision 0011, rulings of 2026-11-15T15:16Z): run that tag or the executables of the main checkout. Interface corrections taken (section 2.6). Memory at `max_nmb_per_rank = 2700` with three finders: 71 GB by the measured 26.3 MB per slot (63.1 GB at 2400, `multi_puncture.md` section 5) [JUDGEMENT, linear in the slots]; the card case that measures it (mem2700) did not run within this package's card hour |

## 2. What was implemented

Each item: files and lines touched (the neighbouring branches change the same
directories), options, test, numbers.

### 2.1 Tracers with m = 0 (D1)

Cause [VERIFIED, test T1]: since commit 4467852 (null particles for the light rays of
the cosmology extension) the mesh-metric branch of `NrpicPush` pushed every particle
with m = 0 as a photon (`eps = 0`, `W = (gamma^ij u_i u_j)^(1/2)`), while the
analytic-metric branches kept pushing it as a massive test particle. The tracer inputs
of `problems/` (seven files, all older) mean a massive test particle without sources.
A tracer at rest has W = 0 and was removed in its first step. Card and processor
builds behave alike; the momenta are read correctly.

Evidence: with the unchanged release executable the tracers of
`problems/puncture/horizon_calib.athinput` start with the coordinate speed of light
psi^-4 of the initial slice (0.72603, 0.78467, 0.82271 at r = 6, 8, 10 M; predicted
0.7260, 0.7847, 0.8227) and the one at rest is removed; with `p<n>_m = 1e-300` on the
command line they start with the timelike speeds (0.32334, 0.29592, 0.27385; predicted
0.3233, 0.2959, 0.2739) and none is removed (run core-20261115-152835-920d573, records
of cycle 4). On a static mesh metric (`problems/tests/tracer_mesh_circular.athinput`,
run core-20261115-154303-da69f6a) the release moves the m = 0 particle of a circular
orbit out of the mesh in 15.6 M; the corrected source keeps r in [7.999998, 8.001151] M
for 300 M with relative errors 2.6e-7 in E and 5.05e-6 in L_z (record of
`docs/TESTLOG.md` "Mesh path": [8.0000, 8.0012], 8.4e-7, 5.1e-6).

Correction: a particle with m = 0 is a tracer on a timelike geodesic for every metric
source; light rays are the particles with m = -t_e < 0, as `cosmo/ic/ray_ic.py` writes
them. `<particles> zero_mass = null` restores the released rule (byte-identical
trajectory to the release in the same test); default `tracer`. The code prints at
start-up how many particles have m = 0 and how they are pushed.

Touched: `particles/particles.hpp` (comment of `NrpicRealIndex`; `NrpicOptions::
zero_mass_null`; `NrpicReportMassless`), `particles/nrpic.cpp` (`NrpicInit`: option;
`NrpicPush`: the line that sets `eps`), `particles/nrpic_io.cpp` (`NrpicReportMassless`
and its call in `NrpicStartup`).

Card: the reproduction R3, R4 (run core-20261115-154030-5ba192a) gives the processor
speeds to five digits; the corrected card executable keeps the circular orbit of the
static-mesh test within the same band, 1.2e-12 M from the processor trajectory (section
4). Open: the 250 M run of `horizon_calib.athinput` with the corrected executable is
Track D's acceptance test (circular orbits within 1 per cent of their areal radius, as
in `runs/puncture/single_v3`); it did not run within this package's card hour.

### 2.2 Output schedule across a restart (D2)

Cause [VERIFIED]: `Driver::Finalize` writes every output once more, and every writer
advances `last_time` by `dt` although the stop is not on the schedule.
Correction: one hook in the loop of `Driver::Finalize` (`driver/driver.cpp`): for a
final output between two scheduled times the interval is zero while the writer runs, so
the stored `last_time` (also in the parameter dump inside the restart file) is
unchanged. A final output on the schedule behaves as before. No writer is touched.
Test T2 (`problems/tests/restart_schedule.athinput`, `t2_restart.py`, run
core-20261115-154901-d8ad7ec): the release loses one restart dump and one table after a
stop at the cycle limit and after a stop at the wall clock; the corrected source loses
none, also when the stop comes before the first interval has passed (the case a first
version of the hook got wrong, run core-20261115-154739-a7a0010); uninterrupted runs
write the same file lists; the continued run ends in the same particle state bit for
bit.

### 2.3 Accretion diagnostics (D3, D4)

New file `particles/nrpic_accretion.cpp`. All off by default; none changes the state
of a run. Options in `<particles>` (read only if present):

| Option | Default | Meaning |
|---|---|---|
| `removal_record` | false | append every removed particle to `<basename>.removed.bin`: header 8 bytes `NRPREM01`, int64 20; records of 20 doubles: time, tag, species, reason (1 left the mesh, 2 lapse below `alpha_exc`, 3 inside a horizon, 4 state not finite), x^i, u_i, rest mass, proper time, alpha, beta^i, W, E = alpha W - beta^i u_i, distance to the centre, pericentre passages. Reasons 2 to 4: state and metric at the start of the step of the removal (the particle was not pushed) |
| `acc_nsphere`, `acc_radius1..4` | 0 | coordinate spheres through which crossings are counted |
| `acc_x1, acc_x2, acc_x3` | 0 | fixed centre |
| `acc_tracker` | -1 | index of the puncture tracker that carries the centre instead (its positions at t^n and t^n+1 bracket the step) |
| `peri_count` | false | count the pericentre passages of every particle about that centre (integer slot `PPERI`; a passage when the distance, having fallen, rises again) |
| `peri_rmax` | -1 | > 0: only passages closer than this |
| `acc_dcycle` | `hist_dcycle` | cycles between records of `<basename>.acc.hst` |

`<basename>.acc.hst` (text): time, cycle, centre, number and rest mass and sum of m E
of the excised particles, number and rest mass of the escaped ones, number and rest
mass of the particles with at least one and at least two passages, and per sphere its
radius, the number and rest mass inside, and the cumulative number, rest mass and
m E of the particles that crossed inwards and outwards. Snapshots end with N int32
(passages per particle) when `peri_count` is on. The particle restart file gets a
block `NRPACC01` only when a diagnostic is on.
Also: `alpha_exc` now acts on the analytic metrics (lapse of the analytic metric at
the particle), and particles flagged for removal are removed and counted for every
metric source (they used to stay in the arrays).

Touched outside the new file: `particles/particles.hpp` (`PPERI`, `NRPIC_NIDATA = 4`,
`NrpicAccOptions`, members and methods), `particles/nrpic.cpp` (`NrpicInit` one call;
`NrpicSaveMetric` one call; `NrpicPush`: two calls, the removal code -2/-3/-4 instead of
-2, the lapse test in the four analytic branches; `NrpicRemoveFlagged` one call;
`NrpicExcise`: removal for the analytic metrics), `particles/nrpic_newton.cpp` (code
-4), `particles/nrpic_io.cpp` (snapshot, restart write and read, start-up, diagnostics:
one call each; the counter slot is set to zero where particles are created),
`CMakeLists.txt` (one line).

Test T3 (`problems/tests/accretion_static.athinput`, `t3_accretion.py`, run
core-20261115-160245-727e96a; Schwarzschild in Kerr-Schild coordinates, three dust
shells and two families of bound orbits, exact references by quadrature): crossings
192 / 84 / 16 as predicted; sums of m E within 7e-8 of the exact values; content of
each sphere equal to in - out - removed to 8e-17 at every record; 192 removal records,
each in the step predicted from the exact infall time, E within 1.2e-5 (mesh) and
3.5e-6 (analytic); pericentre counters (2, 2, 2, 2) and (3, 3, 3, 3) as the exact
orbits; a continued run identical byte for byte in all four output files. In an
evolving spacetime E is the instantaneous value: use a sphere where the gauge has
settled [JUDGEMENT].
Limit of the counter: an orbit whose radial excursion per step is below rounding (a
circular orbit) is counted by noise; it is meant for radial and eccentric motion.
Test T7 (`problems/tests/accretion_tracker.athinput`, `t7_tracker.py`, run
core-20261115-163129-a200caf, re-judged in core-20261115-180101-6d165b4): sphere of
radius 2 on the tracker of a Bowen-York puncture with momentum 0.3, 4000 particles
crossing it both ways (1021 in, 963 out in 0.75 M): content = in - out - removed exactly
at every record, the content counted from the snapshots equals the history, the centre
equals the tracker position of the same time to 5.6e-17. The tracker file
`<basename>.co_<n>.txt` labels the position of t^(n+1) with cycle n and t^n (upstream,
`docs/FORMATS.md`).

### 2.4 External gravity in the Newtonian mode (D5 item 1, A1)

New file `particles/nrpic_external.hpp`; options in `<particles>` (read only if
present), added in both half kicks and in the potential-energy sum of the history
(in full; the mesh potential once per pair):

| Option | Default | Meaning |
|---|---|---|
| `newton_pm_mass` | 0 | mass M of a fixed point mass, potential -G M/(r^2 + s^2)^(1/2) in the variables of the mode, G = four_pi_G/(4 pi); not deposited, not moved; nearest image in periodic directions (an isolated seed: no image sum, no neutralising background) |
| `newton_pm_x1..3` | 0 | its position |
| `newton_pm_soft` | 0 | softening length s |
| `newton_pm_soft_frame` | comoving | `comoving`: s fixed in the coordinates of the run; `physical`: s/a(t) |
| `newton_bg_t0` | 0 | > 0: acceleration -(2/9) x/(t0 + t)^2 of a matter-era background, rho_b = 1/(6 pi G t^2) (Track A's placement "added"; `newton_expansion = none` only) |

Touched: `particles/particles.hpp` (`NrpicExternalOptions`, two methods),
`particles/nrpic_newton.cpp` (`NrpicNewtonInit`: options; new `NrpicNewtonScale`,
`NrpicNewtonExternal`; `NrpicNewtonKick` and `NrpicNewtonPush`: the external term).
Test T4 (`problems/tests/newton_point_mass.athinput`, `..._periodic.athinput`,
`t4_newton.py`, run core-20261115-160805-5d1663f; particles of rest mass 1e-10, step
0.002): two Kepler orbits follow the exact motion to 7e-5 over 20 time units, with the
pericentre counters (3, 4) and 8 / 7 crossings of the sphere r = 1 as the exact orbits
and the sums of m E within 7e-4; circular orbits of the softened potential keep their
radius to 3e-6 and their phase to 5e-5; the background term reproduces r = r0
(1 + t)^(2/3) and (1 + t)^(1/3) to 3e-7; in the expanding periodic box (a from 1 to 4)
orbits around the seed with comoving softening follow an independent ODE solution to
2e-4 and the Layzer-Irvine combination C of the history is constant to 4e-5 of a|W|
while a (K + W) changes by 0.30 of it. With the softening fixed in physical units the
distance to the ODE solution reached 6e-3 at this step; at half the step every
distance and the drift of C fall by 4.00 (second order; run core-20261115-180144-83abe17).
C is a conservation check only for comoving softening (`newtonian_mode.md`).

### 2.5 Common horizon of a pair (F1)

`<fastflow> punc_pair_a_<n>`, `punc_pair_b_<n>`: surface n is the common horizon of
these two punctures; `wait_until_punc_are_close_<n>` compares their distance with
`merger_distance` times the sum of their two masses, `use_puncture_massweighted_
center_<n>` centres the surface on their centre of mass; `merger_distance_<n>` replaces
the common threshold for surface n. With `puncture_setup = true` the single-hole
surfaces are 0 .. npunct-1; a pair surface is an extra block of parameters with
`num_horizons` raised by one (example: `problems/tests/pair_horizon.athinput`).
Touched: `z4c/fastflow.hpp` (two members), `z4c/fastflow.cpp` (constructor: options;
`PuncMaxDistance()`, `PuncSumMasses()`, `PuncWeightedMassCentralPoint()`: the pair).
Test T5 (`t5_pair.py`, run core-20261115-161025-3f75eb8, Brill-Lindquist data of
three punctures of bare mass 0.5 at x = -0.2, 0.2, 12): the surface of the pair (0, 1)
is found at the first call with mass 1.0199 (expected (0.5 + 0.5)(1 + 0.5/24) = 1.0208
less the energy outside the common horizon), mean coordinate radius 0.49; the surface
that waits for all punctures and the surface of the far pair (0, 2) are not searched;
the release, which ignores the new parameters, searches none. Not tested: the surface
appearing during an evolution.

### 2.6 Interface corrections of F4

Taken into `tracks/core/interfaces/multi_puncture.md`: the measured trees of
three-scale Hills meshes hold 1.5 to 2.4 times the "190 leaves per level and hole"
(Track F runs F-hills-20261115-131109-634fb86, -131348-634fb86: 1800 MeshBlocks at
t = 0 for q = 10 at m/8, up to 2332 along the passage); memory per slot 22.75, 24.4,
26.3 MB with one, two, three finders.

## 3. More than one rank: what the particle module lacks, and an estimate

Not started (task). Facts [VERIFIED by reading this branch]:

- `NrpicInit` stops when `global_variable::nranks > 1` (`nrpic.cpp` lines 60-64).
  The build scripts switch MPI off (`scripts/_build.sh`, `-DAthena_ENABLE_MPI=OFF`).
  An OpenMPI installation exists on the machine under another user's home
  (`/home/emost/codes/openmpi/bin/mpicxx`); whether it is CUDA-aware is [TO VERIFY],
  and using it is the group's decision. The Slurm partition gives a job four cores and
  one hour; two cards in one job (`--gres=gpu:2`) is [TO VERIFY].
- Vacuum Z4c with punctures (Track F's request) uses only upstream parts that carry
  MPI code: mesh, boundary exchange, AMR with load balancing, trackers
  (`compact_object_tracker.cpp`, 3 MPI sections), horizon finder (`fastflow.cpp`, 4),
  wave extraction. The initial data of `nrpic_cf` and the Bowen-York curvature are
  local to a cell. What it lacks is an MPI build and a test that one rank and two
  ranks agree: about half a work package, no source change expected [JUDGEMENT]. The
  measured gain is unknown: the two cards exchange ghost zones of every MeshBlock
  face on the cut through host memory unless the MPI is CUDA-aware.
- The particle module is single-rank by construction. What it needs, in the order of
  the cycle:
  1. Ownership and migration: `NrpicAssignBlocks` searches the MeshBlocks of the pack
     (`FindBlock`); with ranks it must find the owner rank from the mesh tree and hand
     the particle over. Upstream has `ParticlesBoundaryValues` (`bvals/bvals_part.cpp`)
     for the cosmic-ray type, which moves particles to face neighbours; it must be
     generalised to the eight real and four integer slots, to refinement boundaries
     and to the periodic wrap. About 300 lines.
  2. Deposit across the cut: a cloud deposits into the MeshBlocks that hold its
     cells (`atomic_add` into the pack). Cells of another rank need a deposit into
     ghost zones followed by an additive ghost-to-owner exchange for the ten source
     components, including the conservative fine/coarse rule of `deposit.md`. The
     boundary classes copy, they do not add: a new exchange. About 500 lines; the
     hardest item, because the conservation identity (mesh integrals equal particle
     sums to rounding) must survive it.
  3. Filter and compensation passes call `InitRecv`, `PackAndSendCC`,
     `RecvAndUnpackCC` in one sequence (`NrpicFilterPass`); with MPI the receive must
     be waited for. About 100 lines.
  4. Reductions: every sum of the histories (`NrpicWriteHistory`, constraint
     statistics, conservation, collisions, Newtonian sums, accretion) needs
     `MPI_Allreduce`; only `NrpicUpdateTimeStep` has it. About 200 lines.
  5. Files: trajectories, snapshots, removal record and the particle restart file are
     written by one rank from its own arrays; they need a gather (or one file per
     rank and a reader that merges), sorted by tag so that files compare across
     decompositions. About 300 lines.
  6. Interpolation near the cut needs nothing new: the metric arrays are filled from
     ADM variables including ghost zones after the Z4c exchange.
  7. Collisions pair particles of one cell, which lives on one rank; the random
     numbers are keyed by tag and step (decomposition-independent by design,
     `rng.md`). Needs item 1 only.
  8. Newtonian mode: the multigrid solver has MPI sections (`multigrid.cpp`), the
     driver hook `SolveSource` and the multipole boundary are [TO VERIFY] under MPI.
  9. AMR load balancing moves MeshBlocks between ranks; the particles in them must
     follow (hook in the redistribution of `mesh_refinement`). About 150 lines.
  Estimate [JUDGEMENT]: 1500 to 2000 lines, two work packages (migration, reductions
  and files first; the additive exchange second), each with the test "one rank equals
  two ranks": identical files on processors for runs without deposit, equal to
  rounding with deposit. The benefit for the program is limited by the machine (two
  cards): at most a factor two in MeshBlocks, and matter runs are bounded by the
  particle number rather than the mesh.
- Larger MeshBlocks (Track F's option 2) need no source: `<meshblock> nx = 32` on the
  three-puncture mesh. The uniform-mesh rate is 2.0e7 zone-cycles/s against 7.7e6 to
  8.8e6 for refined 16^3 meshes (`multi_puncture.md` section 5). The benchmark on the
  three-puncture mesh (MeshBlock-cycles per second, memory) is prepared as cases
  bench16, bench32 of `tracks/core/analysis/dfix/cases/card_checks.list`; it did not run
  (section 4) and needs no source: any owner can run it with the release.
  Recommendation [JUDGEMENT]: option 2 first; it costs minutes and no source, and
  halving the block count at q = 10 brings the m/16 mesh (2654 to 4544 blocks of 16^3,
  i.e. 332 to 568 of 32^3 for the same cells, more with the coarser rounding of the
  refined regions) inside one card.

## 4. Tests of this package and their state

Predictions and outcomes: `tracks/core/JOURNAL-dfix.md`. Scripts and case lists:
`tracks/core/analysis/dfix/`; figures `tracks/core/analysis/dfix/figs/` (each looked at).

| Test | What | Runs | State |
|---|---|---|---|
| T1 | tracer rule: reproduction (release, processors and card), regression on a static mesh | core-20261115-152835-920d573, -154030-5ba192a (card), -154303-da69f6a | passes; one timing guess failed (photon left at 15.6 M, not before 15 M) |
| T2 | output schedule across a stop and continuation | core-20261115-154739-a7a0010 (first hook FAILED in the wall-clock case), -154901-d8ad7ec | passes with the second hook |
| T3 | removal record, spheres, counter, lapse threshold on analytic metrics, restart | core-20261115-160245-727e96a | passes |
| T4 | point mass, softening, background term, expanding box | core-20261115-160805-5d1663f, -162608-113493f, judged -180144-83abe17 | passes; two error bounds at dt = 0.002 failed, second-order convergence shown at half the step |
| T5 | common horizon of a pair among three punctures | core-20261115-161025-3f75eb8 | passes on processors |
| T6 | existing set-ups byte for byte against release core-v0.3 | core-20261115-161129-f905e98 (and its sub-runs) | passes except the stored last_time of final off-schedule outputs (correction 2, by design); prediction "no exception" failed |
| T7 | spheres on a moving puncture tracker | core-20261115-163129-a200caf, re-judged -180101-6d165b4 | passes; the first centre check compared rows one step apart (tracker-file labelling) |
| card | T1, T3, T4 (to t = 18) with the card executable | core-20261115-161528-ff00411 (stopped at its 50-minute limit), judged -180353-7d7116d | passes: counts equal, positions within 1.2e-12 of processors |
| repeat | T1, T2, T3 with the published executables against their first runs | core-20261115-163155/163203/163327-0f014b4, compared -180556-eb25f13, -180814-4652cf3 | identical byte for byte once the run directory in the parameter dump is masked |

Executables published for scouting runs (decision 0013):
`scratch/core/exe/core_requests-adf/{athena_cpu,athena_gpu,COMMIT,READY}`, source
3f75eb8 (athenak/ unchanged to the tip of the branch). Card time of the package: 0.906
card-hours (0.068 reproduction, 0.838 card checks).

Not done in this package (and why):
- card runs of T5, T7, the memory measurement at 2700 slots, the 16^3 against 32^3
  MeshBlock benchmark and the 250 M acceptance run of `horizon_calib.athinput`: the card
  job holding them stopped at its limit inside the Kepler case (0.33 s per step on a
  card, which I had not timed); the card hour of the package was used. The benchmark and
  the acceptance run need no source change: Tracks F and D can run them with the
  published or released executables;
- a merger during an evolution for the pair horizon (T5 tests the trigger at t = 0);
- the deferred items of section 1.

## 5. For the integrator: lines of shared files touched (against main at b7034c9)

New files: `particles/nrpic_accretion.cpp`, `particles/nrpic_external.hpp`, seven inputs
under `problems/tests/`. Hunks in shared files (new-file line numbers of
`git diff -U0 main...core/requests-adf`):
- `CMakeLists.txt` (athenak/src) +140 (the new source file);
- `driver/driver.cpp` +660-673, +676 (`Driver::Finalize`: final off-schedule output);
- `particles/particles.hpp` +12, +22, +36-39, +41-43, +119-123, +163-193, +327,
  +356-379, +381, +404-405 (slot `PPERI`, `NRPIC_NIDATA`, options, members, methods);
- `particles/nrpic.cpp` +152-168 (`NrpicInit`), +292, +384, +397-402, +428, +480-482,
  +488 (`eps`: tracer rule), +494-496, +525-528, +539-547, +550-558, +561-569,
  +574-582 (lapse test on the analytic branches), +591-596, +606, +641-643, +665,
  +700-709 (removal and excision);
- `particles/nrpic_io.cpp` +979-980, +1022, +1057, +1132-1133, +1224-1228,
  +1237-1265, +1275, +1278, +1291, +1329-1332 (snapshot block, restart block,
  start-up report, counter slot set to zero);
- `particles/nrpic_newton.cpp` +172-194, +205-209, +226-259 (options, `NrpicNewtonScale`,
  `NrpicNewtonExternal`), +523-526, +546-550, +561, +617-618, +640-651, +656 (kicks,
  potential-energy sum);
- `z4c/fastflow.hpp` +98-100; `z4c/fastflow.cpp` +136-159 (constructor),
  +1556-1564, +1607-1610, +1627, +1645-1647 (pair distance, masses, centre);
- `docs/FORMATS.md` (rows of `removed.bin`, `acc.hst`, `co_<n>.txt`, the paragraph on
  the optional blocks and the rest-mass rule); `scripts/README.md` (restart caveat).
