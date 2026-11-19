# JOURNAL of core, work package cosmo-amr (refined meshes and horizons in periodic runs)

Append-only, newest at the bottom. Predictions are written before a test runs, outcomes
after, also when a prediction failed. Labels: [VERIFIED] read at a locator or measured in
a registered run, [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Run outputs live under
`scratch/core/<run_id>/`, manifests under `tracks/core/runs/<run_id>/`. Times UTC.
Worktree `wt/core-cosmo-amr`, branch `core/cosmo-amr`, wave 3a.

## 2026-11-19 14:25  start, reading, design

Merged `main` (27b2ced9, already up to date). Read: `CLAUDE.md`; charter to the end of
"Owners"; decisions 0010, 0013, 0016, 0017; brief lines 493-553, 688-706, 834-860; the
requests of `track/A-emd-pbh` (`outbox/20261115T1837{10,11,13,15,16,17,20}Z__to-core__*`);
the track's `periodic_threshold/DESIGN.md` and `JOURNAL.md` (what broke in S1 and S2);
the source: `pgen/nrpic/nrpic_cosmo.cpp`, `nrpic_cf.cpp` (refinement hook),
`particles/nrpic.cpp`, `nrpic_io.cpp` (history, constraint statistics, start-up),
`nrpic_mesh.hpp`, `particles.hpp`, `z4c/z4c_amr.cpp`, `z4c_newdt.cpp`, `z4c_tasks.cpp`,
`fastflow.{hpp,cpp}`, `compact_object_tracker.{hpp,cpp}`, `utils/inline_interpolator.hpp`,
`mesh/mesh_refinement.cpp` (adaptive driver), `driver/driver.cpp` (main loop), `main.cpp`.
Branch survey for the merge [VERIFIED, `git diff --stat main...<branch> -- athenak/src`]:
`core/requests-adf` changes `fastflow.cpp` (constructor near the puncture options, the
`Punc*` functions), `driver.cpp` (`Finalize`), `nrpic.cpp` (`NrpicInit`, `NrpicPush`,
`NrpicRemoveFlagged`, `NrpicExcise`), `nrpic_io.cpp`, `particles.hpp`; `core/gauge` adds
lines to `z4c.cpp`, `z4c.hpp`, `z4c_calcrhs.cpp`; `core/requests-b` changes `z4c.cpp`,
`z4c.hpp`, `z4c_tasks.cpp`, `mesh.cpp`; `core/id-solver` and `core/collisions-2` add one to
five lines to `nrpic.cpp` and members to `particles.hpp`. My changes sit in new files with
small hooks elsewhere (list in `interfaces/cosmo_amr.md`, section "Lines touched").

Facts from the code that shaped the design [VERIFIED by reading]:
- `MeshRefinement::CheckForRefinement` calls `pgen->user_ref_func` for
  `<amr_criterion0> method = user` (`mesh_refinement.cpp:243`); `nrpic_cf` sets it
  (`nrpic_cf.cpp:175-177, 392`), `nrpic_cosmo` did not: the null call Track A found.
- After a mesh change the adaptive driver calls `Particles::NrpicInitializeSources`
  (`mesh_refinement.cpp:186-190`): ownership, metric arrays, two deposits, filter, step,
  density-form sources without extrapolation for the first step. So refinement with
  particles is wired; core's G2 `OPEN.md` item 18 says no test exercised it.
- The deposit represents a cloud on one level; where the leaf cells are finer than the
  cloud (level cap, adaptive cloud level) "its density is spread uniformly over the leaf
  cells inside each lattice cell" (`nrpic.cpp`, kd > 0 branch). That is the staircase of
  E on refined levels that Track A measured (8 to 18 per cent of the perturbation in H at
  t = 0, their T2b and S0).
- The finder evaluates `IndicesAndWeights(pos)` with the raw surface point
  (`fastflow.cpp`, `MetricInterp`); a point outside every MeshBlock gets `havepoint = 0`
  and is silently left out of the surface integrals. Its summary file is opened in the
  constructor, which runs in `Mesh::AddCoordinatesAndPhysics`, before `ChangeRunDir`
  (`main.cpp:384`): hence the file in the start directory. `ah_prop` keeps the values of
  the last success, so after a failed search the summary repeats old numbers (or NaN).
- The tracker (`compact_object_tracker.cpp`) advances `pos += dt (-beta)` and stops the
  run with "couldn't find the compact object" when the position leaves every MeshBlock:
  in a periodic box that is the first crossing of a face. `Z4c_AMR::RefineTracker` uses
  the distance to the unshifted position. Mode `walk` takes the first of equal neighbours
  (strict `<` from the corner of the 3^3 neighbourhood), so in a uniform lapse it drifts
  one cell per step along (-1,-1,-1).
- `Z4c::NewTimeStep` returns the smallest cell size; `Mesh::NewTimeStep` multiplies by
  the Courant number: a coordinate light speed of one is built in.
- `Driver::Execute` loops while `time < tlim`; nothing looks at the fields. The pusher
  removes particles whose state is not finite, so a non-finite metric empties the run.

Design (details and options: `interfaces/cosmo_amr.md`; triage: `interfaces/REQUESTS_A2.md`):
1. `nrpic_cosmo` enrols `nrpic::CosmoRefine` (new `particles/nrpic_refine.cpp`): the
   criteria of `<z4c_amr>` as in `nrpic_cf`, then those of a new block `<nrpic_amr>`:
   particles per cell (`ppc_refine`: the mesh is refined only where the particles support
   it), ladders `lapse_ratio_<l>` and `chi_ratio_<l>` relative to the mean over the box
   (the cosmological form of the `chi` criterion; neither refines the homogeneous
   universe).
2. `<particles> deposit_fine_shape`: a cloud coarser than the leaf cells is sampled on
   them with its own shape (differences of the cumulative distribution of the B-spline at
   the leaf-cell edges). The weights inside one lattice cell sum to the lattice weight,
   so the conservation identity is untouched; the staircase goes.
3. Finder: surface points mapped into the box in periodic directions; files opened at
   the first search (in the run directory); `<fastflow> diagnostics` writes a status file
   with the reason of every search. Tracker: position mapped into the box, nearest image
   in `RefineTracker`, optional `tracker_walk_tol`; its file also opened lazily.
4. Guard (new `particles/nrpic_guard.cpp`, hooks in `Driver::Execute` and `main`): after
   every cycle count the non-finite values of the Z4c state; stop with a diagnostic, the
   final outputs, exit status 3. Default on (it changes nothing in a finite run).
5. `<z4c> dt_lightspeed = f`: `dtnew = min(dx, f min(dx_d / c_d))`,
   `c_d = alpha sqrt(gamma^dd) + |beta^d|` from the evolved fields. Off by default.
6. `<particles> region_dcycle` (new `particles/nrpic_region.cpp`): proper-volume-weighted
   norms of H and 16 pi E inside and outside spheres (fixed, and one on a horizon), means
   of K and of the lapse; any mesh.
7. `<problem> shift_x1..3` in `nrpic_cosmo`: a uniform shift, for tests (the homogeneous
   universe in moving coordinates: lattice, tracker and refined patch cross the faces).
Everything is read only if present in the input, so parameter dumps do not change.

## 2026-11-19 14:45  predictions of the tests (written before any of them ran)

Unregistered so far: the two builds (processor 51 s, card 138 s) of the edited source.
No executable has run. Scripts: `tracks/core/analysis/cosmo_amr/`; figures there under
`figs/`. Processor runs unless stated; `REL` = release processor executable
`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`, `NEW` = this branch.

**T0, regression (options absent).** NEW against REL on: the homogeneous universe
(`problems/cosmo/flrw.athinput`), the plane-wave mode (`daverio_mode.athinput` with
`make_east.py --ratios 1,0,0` data), `problems/tests/deposit_smr.athinput`,
`problems/tests/regress_cf.athinput`, and a puncture with the horizon finder on a
statically refined periodic mesh. Prediction: every history, table, particle and field
file is byte-identical; the horizon summary has the same bytes but lies in the `-d`
directory with NEW and in the start directory with REL; restart files agree outside the
36 never-set header bytes (core G2 `OPEN.md` item 15). Refuted by any differing byte in
a physics output.

**T1, deposition identity on a refined periodic mesh.** 4096 particles at random
positions with random momenta (|u| up to 0.5) and masses in the homogeneous box
[0, 1)^3, root 16^3, static level 1 in the interior, level 2 inside it, and a level-1
slab on both sides of the x1 face (so clouds straddle the periodic face between levels);
4 cycles (particles cross faces and level boundaries). Cases: cloud cic, tsc, pcs; cloud
level finest, capped at the root, adaptive; `deposit_fine_shape` off and on; filter off.
Measure from `.nrpic.hst`: |int_E / sum_mW - 1| and |int_S_i - sum_mu_i| / sum m|u|.
Prediction: at most 1e-13 in every case (round-off of 4096 terms), with and without the
fine shape. With two filter passes on the refined mesh the filtered integrals differ from
the particle sums by up to 1e-2 (the filter is not conservative across levels: comment
in `NrpicFilterSources`), on a uniform mesh by at most 1e-13. Refuted for the identity
by any unfiltered case above 1e-12: then a cloud loses or duplicates weight at a level
boundary or at the periodic face.

**T2, homogeneous universe with a refined patch.** Box [-2, 2)^3, root 16^3 (blocks
8^3), one particle per root cell unless stated, conformal-time lapse, all cases at the
same step (`<particles> dt` = 0.25 of the level-1 cell), to t = 1:
U uniform; S static level-1 patch in the interior, adaptive cloud level; Sf the same
with `deposit_fine_shape`; P static patches across a face and a corner of the box;
A adaptive, patch created by `<z4c_amr> radius_0_rad` at the first check and kept;
L adaptive with `method = lohner` and the criteria of `<nrpic_amr>` (ppc, lapse and chi
ladders) that must not refine; D8 static patch, eight particles per root cell on the
level-1 lattice, clouds on the finest level; D8s the same with a uniform shift 0.5 (the
lattice drifts through the patch and the faces).
Predictions: (i) U, S, Sf, P, A, L stay homogeneous: chi_max/chi_min - 1 and
E_max/E_min - 1 at most 1e-12 at every record, H_max = H_mean to 1e-10 relative; (ii)
their alpha_max(t) equals that of U to 1e-12 relative (same steps, same arithmetic up
to the order of sums); (iii) L: no MeshBlock is created (Track A's requested test: the
homogeneous universe stays uniform to 1e-14 with refinement on); (iv) A: the patch
appears after the first check, the history shows the block number change, homogeneity
holds across the regrid. (v) D8 at t = 0: uniform to 1e-12 (fine clouds of a lattice
with the fine spacing tile space; my one-dimensional calculation of the transition
between cloud sizes one coarse cell outside the patch gives exact uniformity for any
offset of the lattice). D8s: [TO VERIFY] the transition is not a tensor product at the
edges and corners of the patch; I predict uniformity to 1e-12 on the faces and allow a
departure at the 12 edges, to be measured. Refuted for (i) by any structure at a level
boundary above 1e-10.

**T3, linear plane wave with a refined patch.** Test B of arXiv:1904.07841 as in
`cosmo/TESTLOG.md` 316-338 (delta = 1e-7 sin(2 pi x/L), L = 1.35085, 32 cells per
wavelength, eight particles per cell, quadratic cloud, no filter), cut down to a
thin box if the tool allows, to t = 4 (a = 9); all cases at the step of the fine level:
U uniform; S static level 1 on L/4 < x < 3L/4, clouds capped at the root
(`deposit_max_level = 0`); Sf the same with `deposit_fine_shape`; Sx clouds on the
finest level; P as Sf with the patch across the x face.
Measure: a sine fit of chi and of E along x (AthenaK tables) at the end; amplitude
ratio to U, phase, rms residual of the fit over the amplitude; Hamiltonian constraint
over 16 pi times the density amplitude at t = 0 inside the patch.
Predictions: amplitudes of chi within 1 per cent of U in all patch cases, phase shift
below 1e-2 rad, residual of chi below 1 per cent; density: S shows the staircase,
residual of E of the order k h_coarse/4 = 5 per cent of the amplitude inside the patch,
Sf and P below 1.5 per cent; H/(16 pi dE) at t = 0 on the patch: S 0.05 to 0.1 (Track A:
0.077 to 0.085 for the peak), Sf at least three times smaller. Refuted for "unchanged by
a refined patch" if the chi amplitude differs from U by more than 3 per cent or the
patch across the face (P) differs from the interior patch (Sf) by more than their
difference from U.

**T4, horizon finder in a periodic box.** A lattice of unit punctures through
`nrpic_cosmo` (file data: psi = 1 + 1/(2 r_min), r_min the distance to the nearest image,
K = 0, alpha = 1), box [-4, 4)^3, uniform 64^3 (dx = 1/8), one cycle, finder with
`metric_drvts = interpolant`, initial radius 0.6. Cases: a hole at the box centre, finder
at (0,0,0); b the same, finder centred one period away at (8,0,0); c hole on the face,
finder at (4,0,0); d hole at the corner, finder at (4,4,4); e as d, finder at
(-4,-4,-4); and b, c with REL.
Predictions: a = 0.99152 (calibration 0.991521 of `docs/TESTLOG.md` for dx = M/8;
Track A's periodic value 0.9915211031 on a refined mesh; the near field is the same, I
expect agreement to 1e-6); b, c, d, e equal a to 1e-10 relative (the data of c, d, e are
those of a translated by 32 cells; only the order of sums and the image arithmetic
differ); REL: b and c report no horizon. The summary file lies in the `-d` directory.
`diagnostics = true`: one status line per search, `found = 1` here. In the homogeneous
universe (T2-U with a finder) the status says why no horizon exists; I expect the flow
to shrink the surface to a point (reason 5 or 4), the expansion being positive.
Refuted by a mass in c, d, e that differs from a beyond 1e-8: then stencils through the
periodic ghost cells or the mapping are wrong.

**T5, tracker in a periodic box and refinement that follows it.** Homogeneous universe
with a uniform shift beta^x = -0.5 (`<problem> shift_x1`), box [-2, 2)^3, root 16^3, one
particle per root cell, tracker of type BH at (1.5, 0, 0) in mode ode,
`<z4c_amr> method = tracker` (radius 0.6, level 1), `dt_lightspeed = 1`, to t = 2.5.
Predictions: the tracker moves as x = 1.5 + 0.5 t, crosses the face at t = 1.0 and
continues at -2 + 0.5 (t - 1), to 1e-12; no "couldn't find the compact object"; refined
blocks exist on both sides of the face while the tracker is within 0.6 of it; the
universe stays homogeneous to 1e-12 through every regrid and the crossing; alpha_max(t)
equals the run without shift at the same steps to 1e-10; the step is 0.25 dx_1 / 1.5
(coordinate light speed 1 + |beta| = 1.5), to 1e-12. With REL the run stops at the
crossing. Refuted by a jump of the tracker, a fatal error, or structure above 1e-10.

**T6, stop on non-finite fields.** The homogeneous universe at a Courant number of 4
(unstable with RK4). Predictions: NEW stops by itself within a few cycles of the first
non-finite value, prints the diagnostic, writes `<basename>.guard.txt` (variables, first
cell), writes the final outputs and exits with status 3; REL runs to `nlim` with status
0; NEW with `<nrpic_guard> stop_nonfinite = false` behaves as REL (status 0);
`stop_chi_nonpositive = true` stops earlier or at the same cycle. Refuted if NEW exits
with 0 or hangs.

**T7, step limit from the coordinate light speed.** (a) homogeneous universe,
conformal-time lapse: the step with `dt_lightspeed = 1` equals the step without to 1e-12
(c = alpha sqrt(chi) = 1); (b) lapse d_t alpha = -(2/3) alpha^2 K (`lapse_harmonic =
0.6667`), for which alpha = a^2 and c = a: dt = 0.25 dx / a(t), i.e.
dt alpha_max sqrt(chi_max) / (0.25 dx) = 1 to 1e-6 at every step after the first
(the limit is evaluated at the end of the previous step); without the option the step
stays 0.25 dx; (c) T5 gives the shift part; (d) T4 a (puncture, c <= 1): the step is
unchanged. Refuted by a step above 0.25 dx / c_max.

**T8, region norms.** On T2 (U, S) and T9: V_in + V_out = V to 1e-13; V equals
`.nrpic.hst` column 28 and mean_K column 29 to 1e-13; max(Hmax_in, Hmax_out) equals
`.cstat.hst` column 9 exactly; on the refined mesh V = L^3 a^3 to 1e-12 (every leaf cell
once); V_in of a sphere of radius 6 root cells within 3 per cent of (4 pi/3) r^3 a^3.

**T9, adaptive refinement on Track A's peak (processors, 32^3 root).** Data built with
the track's `make_peak_ic.py` (mu = 0.3, e = 0.2, eps_i = 1, 32^3), blocks 8^3, up to
two levels, 8 cycles: (1) `<z4c_amr> method = lohner` as in the track's
`peak_amr.athinput`: no crash at the first check (the request); (2) `chi_ratio_1` and
`lapse_ratio_1` chosen from the initial ratios: the blocks at the centre are refined at
the first check, none at the box corners; (3) `ppc_refine` just above one: the blocks
whose cells hold more than that are refined; `deposit_fine_shape` on. Predictions: no
crash; particle number and rest mass unchanged through the regrid; the relative
Hamiltonian constraint on the new blocks after the regrid is below Track A's 0.047 of
the static start (the fine blocks start from prolonged evolved data and fine-sampled
clouds); deposition identity to 1e-13 after the regrid.

**T10, scouting run on a card (at most one card-hour).** Track A's S1 (mu = 0.3,
data of run A-emd-pbh-20261115-155802-9a6596f, 64^3 root, E1 gauge), adaptive refinement
toward the peak by the lapse ladder and the particle number, `deposit_fine_shape`,
`dt_lightspeed = 1`, guard with `stop_chi_nonpositive`, finder with status file, region
norms. Predictions [JUDGEMENT]: (1) at t = 0 the mesh is uniform and Hr_max is below
1e-3 (S1 with four static levels: 0.047); (2) fine levels appear only as the lapse
falls (tau > 5); the run costs less than S1's 0.18 card-hours up to tau = 10; (3) the
gauge is S1's, so the end is S1's: the conformal factor turns non-positive or the
fields non-finite between tau = 10 and 12.5 on the finest level within 0.6/k of the
centre, without a horizon; this time the run stops there with status 3 and a
diagnostic; (4) every failed search of the finder has a reason in the status file. A
horizon would refute (3) and would be the first of this set-up: its area mass must then
be below the mass inside r_m.
