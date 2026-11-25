# CHANGELOG of core (the NRPIC implementation in this repository's AthenaK)

Releases are git tags, created by the orchestrator (decision 0003; from wave 3 by its
release clerk once `tracks/core/RELEASE-<version>.md` reports a passing byte regression,
decision 0019 item 4). Tags that exist: core-v0.1 = 7daed19 (asymptotically flat),
core-v0.2 = 52c44eb (periodic particles and cosmological gauge; source of main a1c2237),
core-v0.3 = 609a875 (below).

## core-v0.7 (release candidate, 2026-11-24): four source branches (decision 0035 item 4)

Record: `tracks/core/RELEASE-v0.7.md` (first line: source commit and regression
verdict; the regression table; the quick tests; the card checks that are pending).
Source commit **5f75e5b9** (5f75e5b9cd02fee45eead0b4c3445189d8362dde) of `core/nrpic`:
the last commit that changes `athenak/`, `python/`, `problems/`, `scripts/` or `docs/`
(the merge of core/clump-table); later commits add records and release drivers
(`tracks/core/`) only. Executables built from it, with READY (every new option with one
example input), COMMIT and SHA256SUMS:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v07/` (`athena_cpu` serial,
`athena_gpu` one A100, `athena_cpu_omp` threaded, `athena_cpu_mpi` several ranks).

### What is merged (in this order, one merge commit per branch)

| Branch (tip merged, source) | Merge | Capability | Switch (absent = off) | Interface document |
|---|---|---|---|---|
| core/noise-level2 (5c98beef, source 64f150ec; reviewed on Fable 2026-11-24, verdict "results unchanged") | da904f55 | stochastic backreaction of level 2 of arXiv:2512.14649: the curvature perturbation R and its momentum as mesh fields with local coefficients, projected onto the mode set at every stage; the same mesh form of the mode equation for levels 0 and 1; a lockstep background evolved with the equations of the mesh; per-mode records | `<scalar_field> noise_level = 2`, `noise_mode_eq = mesh`, `noise_background_eq = evolved` | `noise_level2.md` |
| core/step-limit (3a9a3498, source 5c4b644f) | 76ac67a2 | step limit by the stability bound of the Runge-Kutta scheme for the gauge sectors (Gamma-driver shift, lapse with its relaxation, conformal factor with Theta), evaluated in every cell every cycle; restart outputs on SIGTERM; chain script | `<z4c> dt_gauge = 0.9`; the stop on SIGTERM and the start-up warning have no switch | `step_limit.md`, `preempted_runs.md` |
| core/gauge-2 (61c8fc4d, source 984110c3) | 31ae23e6 | **a mitigation, not a cure** (decision 0025 item 3): the relaxation of the lapse (`lapse_leak`) switched off within a radius of every compact-object tracker, against the shrinking of a horizon in the coordinates that the relaxation causes on a slice with diverging normal observers | `<z4c> lapse_leak_hole = r_h` | `cosmo_gauge.md` section 9 |
| core/clump-table (ff11719d, source 7cc6c7b9) | 5f75e5b9 | table components of `nrpic_cf` with a bulk momentum (boosted equilibrium clusters): extrinsic curvature from tabulated radial moments of the momentum density, second-order correction of psi, comoving shift; generator model `boosted` | `<problem> comp<c>_boost_file` | `moving_clusters.md` |

Left out: core/oblate (oblate collapse; not ready, as the task of the merge says: its
branch holds neither core-v0.5 nor a READY for a merged state). No conflict in any of
the four merges; `CMakeLists.txt` (three new sources of two branches) and
`docs/FORMATS.md` (section `bst1` appended) were merged by git and read afterwards.
core/clump-table held core-v0.5, not core-v0.6: its three source files do not overlap
with the changes of core-v0.6.

Maintainer's decisions at the merge (reasons in `tracks/core/JOURNAL.md`, entry of
2026-11-25T02:12Z): core/clump-table is taken, because its one outstanding check, the
card run M2 of its merged build, had run on 2026-11-21 and holds (judged now, run
core-20261125-021225-382dbc7: lapse within 3.3e-15 of the run of the build before its
merge over 50 M). `dt_gauge` stays an option (off when absent): whether it becomes the
default waits for a survey of the tracks' puncture and horizon decks (`step_limit.md`
section 5).

### Behaviour that changes without an option

1. **Stop on the termination signal** (every run; `utils/term_signal.{hpp,cpp}`, hooks in
   `main.cpp` and `driver/driver.cpp`). A run that receives SIGTERM (preemption,
   `scancel`, the time limit of the batch system) finishes the cycle in progress, writes
   its restart outputs (`file_type = rst`) and no other output, skips the final function
   of the problem generator, prints "Terminating on signal SIGTERM" and exits with
   status 143. Before, it died at once with the same status and wrote nothing. A run
   that receives no signal is not changed: no file of the byte regression differs (75 of
   75 items, serial and MPI build). Under MPI the loop makes one more reduction per
   cycle. SIGKILL still stops a run at once.
2. **Warning at start-up** (runs with Z4c in three dimensions, integrator rk3 or rk4):
   the stability bound of the gauge sectors is evaluated once at the first cycle, and
   the log gets "### WARNING (Z4c step limit) ..." when `cfl_number` times the smallest
   cell exceeds it, and a second line when `lapse_leak` times that step is beyond the
   bound of the relaxed lapse. Log only: no output file changes, the step is not
   touched without `dt_gauge`.
3. `<scalar_field> noise_level = 2` was a fatal error ("not implemented") and now runs.
   No run that worked is changed.
4. A table component of `nrpic_cf` under `id_solve = true`: nothing new in the code, but
   the example of the branch (`clump_table_idsolve.athinput`) now gets the multipole far
   field that core-v0.6 switched on by default; its bytes are not those of the branch
   executable (a core-v0.5 source). It converges as before (25 outer iterations, max|H|
   1.7e-3 to 2.0e-12 at 32 cells, quick test).

### Run scripts

`scripts/submit_chain.sh` (branch core/step-limit; `preempted_runs.md` section 5):
1. An attempt cut by a signal (SIGTERM to the job, a kill of the executable from
   outside) before it has run for `ATHENA_WALL` does not count against `MAX_SEGMENTS`
   (`chain/uncounted`; `--status` prints attempts, uncounted and the cap).
2. On SIGTERM the job resubmits at once and then waits for the executable, which with
   the handler of item 1 above writes its restart file inside the grace period (30 s on
   anta; a 256^3 restart file of 4.2 GB takes 3.2 s, run core-20261124-235925-5ee2c95).
3. No job is queued after the last counted segment; the chain is FAILED "MAX_SEGMENTS=N
   reached" in that job, and the start command on such a chain is refused.
4. `MAX_TERM_IN_A_ROW` (default 20): that many attempts in a row ended by SIGTERM fail
   the chain.
5. An executable with the handler that is signalled from outside the job is resubmitted
   as the outside kill it is. **Use the script of this release with executables of this
   release**: the script of core-v0.6 takes "status 143 with a line Terminating on" for
   a failure (`git show core-v0.6:scripts/submit_chain.sh`, lines 268 and 282) and ends
   the chain FAILED "athena exit status 143". A chain already running keeps the script
   and the executable it was started with.
Test `scripts/tests/test_submit_chain.py` (fake `sbatch`, fake executable): 58 checks
(package run core-20261125-000640-5c4b644; repeated with the merged tree in the quick
test). Not tested: a real preemption by Slurm.

`scripts/cpu_run.sh` (commit e9527413 of `core/nrpic`, between the tags): the footer of
the log is written also when the executable returns a non-zero status.

### Input options (`tracks/core/verify/options_at.py core-v0.6 HEAD`)

Seven options found by the scan, none removed; one value added to an existing option
(`noise_level` accepts 2); two more names are built at run time and added here by
reading the source (nine in all); four existing names of `<problem>` components gain a
meaning for table components. Every one is read only if it is present in the input.

- `<scalar_field>` (with `noise = mukhanov_sasaki`) noise_mode_eq,
  noise_level2_background, noise_level2_laplacian, noise_background_eq,
  noise_rmodes_dump; noise_level = 2
- `<z4c>` dt_gauge, lapse_leak_hole
- `<problem>` (`nrpic_cf`, component of type table, format 1) comp<c>_boost_file,
  comp<c>_boost_shift; and for such a component the names that punctures and Gaussians
  already had: comp<c>_p1..3, comp<c>_corr (= table), comp<c>_corr_file,
  comp<c>_corr_axis1..3. A table of format 2 with a boost file is a fatal error.

Advice that belongs with the options (from the packages): with `dt_gauge` use 0.9
(rk4, nghost 4); a moving table cluster needs `<z4c> shift_eta` of 0.03/M to 0.1/M
(with 2/M it moves at 0.7 v in the coordinates), and `sum m u_i` is a coordinate
component, not a conservation monitor; `lapse_leak_hole` needs a tracker
(`<z4c> co_<n>_type = BH` with its position) and r_h well beyond 6 M with 2 r_h inside
the matter that needs the relaxation (16 M tested).

### Files and formats added (`docs/FORMATS.md`, interface documents)

`<basename>.sf.NNNNN.rmodes` (per-mode record of the mesh field R, with
`noise_rmodes_dump`); with `noise_background_eq = evolved` one more header line in
`<basename>.sf.NNNNN.modes` and two more lockstep values in the restart file; with R on
the mesh the restart file of the scalar field carries two more components. Boost table
`*.bst` (format `bst1`, new section of `docs/FORMATS.md`); generator
`problems/ic/make_ic.py boosted` and `python/nrpic/boosted_cluster.py`. No existing
format changes.

### Evidence

Byte regression against core-v0.6 on the twelve set-ups of wave 1: PASS for the serial
build (run core-20261125-023046-30aba6c, 75 of 75 items identical) and for the MPI build
on one rank (core-20261125-023646-eca713c). Quick tests (one example per branch against
the branch executable, 65 of 65 files identical; combinations; SIGTERM; chain script):
PASS, run core-20261125-023641-7a1c47d. The threaded build and the card check that is
pending: `RELEASE-v0.7.md`. The capability tests were run by the work packages on the
executables of their branches (run ids in each interface document; journals
`tracks/core/JOURNAL-{noise-level2,step-limit,gauge-2,clump2}.md`; READY files copied to
`scratch/core/exe/core_nrpic_v07/branches/`).

### Known limitations carried into core-v0.7

`tracks/core/stage/G2/OPEN.md` (section of core-v0.7) and the READY of the published
executables. The most important: the merged card executable had not run on a card when
this was written (queue entry q0039); level 2 does not support refined meshes or
several ranks and is not tested with a lapse that varies in space or with a shift;
`lapse_leak_hole` delays the defect of the relaxed lapse around a hole by about 100 M
and does not remove it; `dt_gauge` is not tested with punctures, horizons, refinement
that adapts, or several ranks; the stop on SIGTERM is not tested on several ranks, on a
card, or under a real preemption; two older restart defects (a record of
`<basename>.cons.hst` lost at a continuation; the header of the mesh history repeated)
are in this release as in core-v0.6.

## core-v0.6 (release candidate, 2026-11-21): three source branches of waves 3a and 3

Record: `tracks/core/RELEASE-v0.6.md` (first line: source commit and regression
verdict; the regression table; the quick tests; the card checks). Source commit
**984bde68** (984bde68c6201c8f100ced3d6a7effbea9cafd80) of `core/nrpic`: the last commit
that changes `athenak/`, `python/`, `problems/` or `scripts/` (the merge of
core/id-solver-2); later commits add records (`tracks/core/`) only. Executables built
from it, with READY (every new option with one example input), COMMIT and SHA256SUMS:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/` (`athena_cpu` serial,
`athena_gpu` one A100, `athena_cpu_omp` threaded, `athena_cpu_mpi` several ranks).

### What is merged (in this order, one merge commit per branch)

| Branch (tip merged) | Merge | Capability | Switch (absent = off) | Interface document |
|---|---|---|---|---|
| core/newton-2 (b7c9fc73) | a1fffa58 | Newtonian mode, second pass: Fourier Poisson solver on a periodic uniform mesh (continuum symbol or the symbol of the seven-point Laplacian; transform written with Kokkos kernels, lengths with the factors 2, 3, 5, 7); second moments of particle groups with their time derivatives in comoving and physical coordinates; options `--axes`, `--vgrad`, `--rotate`, `--background` of the ball of `problems/newton/make_ic.py`; `python/nrpic/newton.py scheme_fields(symbol=)` | `<particles> newton_poisson = fft`, `newton_fft_symbol`, `newton_ngroup` with `newton_group<g>_*` | `tracks/core/interfaces/newtonian_mode.md` (sections 6, 7), triage `REQUESTS_NEWTON2.md` |
| core/z4c-faces (5d875275, source f6f9a0df) | 1419f19a | outer faces of Z4c: ghost cells by extrapolation of (f - f_inf) r^q; radiative condition of the outermost cells with the part that is not a wave carried from one cell inside; speeds of that condition from the lapse or the metric with shift advection; variants for Theta | `<z4c> ghost_falloff`, `sbc_variant = nonwave`, `sbc_speed`, `sbc_theta` (with the existing `extrap_order = 4`) | `tracks/core/interfaces/z4c_faces.md` |
| core/id-solver-2 (3087526a, source 395e17d8) | 984bde68 | initial-data solver, second pass: multipole far field under the 1/r fill of the faces; exact Jacobian for moving matter; static refinement (BiCGStab, Robin faces of the multigrid octets); punctures of `nrpic_cf` in the solve (psi = psi_s + u); generators `shift`, `zeldovich`, `shell` of `problems/idsolve/make_ic.py` | within `<particles> id_solve = true`: `id_far`, `id_far_lmax`, `id_far_radius`, `id_lin_solver`, `id_punctures`, `id_puncture_radius` | `tracks/core/interfaces/id_solver2.md` (with `id_solver.md` for what is unchanged) |

Left out, not closed when the candidate was built (2026-11-21T13:00Z): core/clump-table
(equilibrium clumps with momentum from tables; its session was at work) and core/oblate
(oblate collapse; its branch does not hold core-v0.5 yet). No branch that was offered
closed is left out. No conflict in any of the three merges (`CMakeLists.txt`,
`particles.hpp`, `docs/FORMATS.md` merged by git; checked by reading).

Maintainer's decision at the merge: the default `id_far = multipole` stands (item 1 of
the next section; reasons in `tracks/core/JOURNAL.md`, entry of 2026-11-21T12:55Z).

### Behaviour that changes without an option

All five only in runs with `<particles> id_solve = true`; a run without it writes the
bytes of core-v0.5 (regression below; package test M0).
1. **Far field on by default.** On a mesh with no periodic face the faces of psi and
   of W are filled with the multipole far field (`id_far = multipole`). Against
   core-v0.5 at 32 cells psi changes by 9.7e-9 (Gaussian at rest), 3.6e-8 (expanding
   ball), 1.5e-6 (moving Gaussian) and W of the moving Gaussian by 2.7e-3 of its
   maximum; the iteration counts do not change (run core-20261121-131148-6efd1b8).
   `id_far = robin` gives the bytes of core-v0.5 for matter at rest (same run: 8, 9 and
   8 files identical). A torus is not affected.
2. With moving matter the Jacobian of the scalar part holds the trace of the deposited
   stress: psi and W change at rounding (6.0e-15, 5.1e-16), also with `id_far = robin`.
3. Puncture components of `nrpic_cf` enter the solve (`id_punctures = true` is the
   default); core-v0.5 solved for the whole psi on the mesh.
4. A refined mesh no longer stops the solver, and `<gravity> mg_bc = robin` is accepted
   on a refined mesh.
5. `<basename>.idsolve.txt` gets a second header line and a far-field line when the
   far field, a refined mesh, punctures or BiCGStab are in use; on a refined mesh
   `id_dump` writes `<basename>.idsolve.blk.bin` instead of `.idsolve.bin`.

Not changed in this release, stated because it was asked (package newton2): the nine
never-set members of the mesh header of restart files (`Mesh::mesh_indcs.cnx1 .. cke`,
36 bytes) are zero since core-v0.4 (`Mesh::ZeroUnusedMeshIndcs`, also after reading a
restart header). Restart files of core-v0.4, core-v0.5 and core-v0.6 agree in these
bytes; files written by core-v0.3 or by a branch executable whose source is older than
core-v0.4 (the pre-merge build of package newton2) carry noise there. Checked on the
12 restart files of the release tests (run core-20261121-130813-710b3cc).

### Run scripts (`scripts/submit_chain.sh`, commit 9730e2aa, in the source commit)

Not a branch of the merge table: written by the lead of core in batch 2b (decision 0021
item 6), on `core/nrpic` before the three merges, so it is in core-v0.6 and was not in
core-v0.5 (`git tag --contains 9730e2aa` names core-v0.6 only).
1. **A segment killed from outside is resubmitted.** An exit of the executable with
   status 137 or 143 with no line "Terminating on" in its log and no signal to the job
   itself counts as an outside kill: the chain submits the segment again from the last
   restart file, at most `MAX_OUTSIDE_KILLS` times in a row (default 2; the count is
   reset by a segment that ends at the wall clock or the time limit); the next such kill
   ends the chain with FAILED "killed from outside N times in a row". Before, any
   non-zero exit ended the chain (`git show 9730e2aa^:scripts/submit_chain.sh`, line 236).
2. **The executable runs under a name of its own.** The chain starts `chain/<PROC_NAME>`,
   a hard link to `chain/athena`; default `nrc-<8 hex digits of the run directory>`, so
   a kill by process name aimed at another run cannot match it. A `PROC_NAME` that
   contains "athena" is refused at the start; a chain whose configuration has no
   `PROC_NAME` (started by an older script) gets the default at its next segment.
3. Evidence: `scripts/tests/test_submit_chain.py` with a fake `sbatch`, `squeue` and an
   executable that kills itself; seven scenarios (A to E, G, H), every status sequence,
   `sbatch` count and process name as predicted (run core-20261121-080619-6a0793f; the
   first run core-20261121-080555-9730e2a failed by a fault of the fake, journal entry of
   2026-11-21T07:47Z). Not tested with a real Slurm job or a real AthenaK run. A chain
   already running keeps the script it was started with (sbatch spools it).

### Input options (`tracks/core/verify/options_at.py core-v0.5 HEAD`)

19 options found by the scan, none removed, no default of an existing option changed;
seven more names are built or tested at run time and added here by reading the source
(26 in all). Every one is read only if it is present in the input.

- `<particles>` (Newtonian mode) newton_poisson, newton_fft_symbol, newton_ngroup,
  newton_group<g>_species, _tag_min, _tag_max, _x1, _x2, _x3
- `<particles>` (with `id_solve = true`) id_far, id_far_lmax, id_far_radius,
  id_lin_solver, id_punctures, id_puncture_radius
- `<z4c>` ghost_falloff, ghost_power_metric, ghost_power_curv, sbc_variant,
  sbc_power_khat, sbc_power_a, sbc_power_gam, sbc_v_khat, sbc_speed, sbc_theta,
  sbc_power_theta

Two names stop a run if they are set to a non-zero value: `<z4c> sbc_damp_gam`,
`sbc_damp_theta` (options of the package that were removed before the merge: the damping
was unstable in the expanding ball; they were never in a release).

### Files and formats added (`docs/FORMATS.md`)

`<basename>.newton.g<g>.hst` (62 columns per group); second header line and far-field
line of `<basename>.idsolve.txt`; `<basename>.idsolve.blk.bin`. No existing format
changes.

### Evidence

Byte regression against core-v0.5 on the twelve set-ups of wave 1: PASS for the serial
build (run core-20261121-130202-7cf7db8, 75 of 75 items identical). Quick tests, the
regressions of the solver's package repeated with the merged executable, the other
processor builds and the card checks: `RELEASE-v0.6.md`. The capability tests were run
by the work packages on the executables of their branches (run ids in each interface
document; journals `tracks/core/JOURNAL-{newton2,faces,idsolve2}.md`; READY files copied
to `scratch/core/exe/core_nrpic_v06/branches/`).

### Known limitations carried into core-v0.6

`tracks/core/stage/G2/OPEN.md` (section of core-v0.6) and the READY of the published
executables. The most important: the faces options still reflect (the ball's interior
at t = 16 is 8 times below the stock faces and 55 times above a run with distant
faces), no constraint-absorbing treatment of Theta was found, and r in every formula is
the distance from the mesh origin; the vector part of the solver stalls at level
boundaries in mode code; a Bowen-York puncture has an error floor of u set by the
distance of the faces; the Fourier solver needs one pack on a uniform periodic mesh;
a cold lattice with fewer than one particle per cell and direction is pushed as a whole
in the Newtonian mode; none of the three capabilities runs on several ranks (the
Newtonian mode and `id_solve` stop with a message, the faces options are untested
there).


## core-v0.5 (release candidate, 2026-11-21): four wave-3a source branches

Record: `tracks/core/RELEASE-v0.5.md` (first line: source commit and regression
verdict; the regression table; the quick tests; the card check). Source commit
**c3eb42e0** (c3eb42e0bf9b9804e569f7e6dd1603ac805a60eb) of `core/nrpic`: the last commit
that changes `athenak/`, `python/`, `problems/` or `scripts/` (the merge of core/mpi);
later commits add records (`tracks/core/`, `docs/FORMATS.md`) only. Executables built from it, with
READY (every new option with one example input), COMMIT and SHA256SUMS:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v05/` (`athena_cpu` serial,
`athena_gpu` one A100, `athena_cpu_omp` threaded, `athena_cpu_mpi` several ranks).

### What is merged (in this order, one merge commit per branch)

| Branch (tip merged) | Merge | Capability | Switch (absent = off) | Interface document |
|---|---|---|---|---|
| core/scalar-3 (88544a5b) | 604e9ad8 | entity of a Fourier mode and stream word of the stochastic sources as named functions (`rng::ModeEntity`, `rng::StochasticModeStream`, Python twins `mode_entity`, `stochastic_mode_stream`; the keys are those the noise used before); signed constraint means of the scalar-field record; example of the inflection (ultra-slow-roll) case; linear twin `python/nrpic/sf_lattice.py` | `<scalar_field> con_signed` | `tracks/core/interfaces/scalar_field_3.md`, `rng.md` sections 6 and 6.2 |
| core/build-openmp (983351aa) | 0d0f5ba5 | threaded processor build (Kokkos OpenMP, `scripts/build_cpu_omp.sh`, `scripts/cpu_run.sh`, `scripts/omp_places.py`); deposit into one private copy of the sources per thread, which repeats bit for bit at a fixed thread count | `<particles> deposit_threads = atomic \| private` | `tracks/core/interfaces/threaded_build.md` |
| core/cosmo-amr (bb360ef2, source 1548d49c) | e103b3e3 | adaptive refinement in `nrpic_cosmo` with criteria on particles per cell, lapse and chi; coarse clouds sampled on fine leaf cells with their shape; horizon finder and tracker in a periodic box, status of every search; guard that stops a run whose fields are not finite; step limit from the coordinate speed of light; constraint norms inside and outside spheres; exact restarts of adaptive `nrpic_cosmo` runs | `<amr_criterion0> method = user` with `<particles_amr>`; `<particles> deposit_fine_shape`, `region_dcycle`; `<fastflow> diagnostics`; `<z4c> tracker_walk_tol`, `dt_lightspeed`; `<z4c_guard>`; `<problem> shift_x1..3` | `tracks/core/interfaces/cosmo_amr.md`, triage `REQUESTS_A2.md` |
| core/mpi (f9a2c022, source ca46836a) | c3eb42e0 | the particle module on more than one MPI rank: ownership and hand-over of particles, deposit of clouds across rank boundaries, sums over the ranks, files written by rank 0 in tag order, restart on any rank count | none: `mpirun -np N` with the MPI build | `tracks/core/interfaces/mpi.md` |

Left out, unfinished (for core-v0.6): core/id-solver-2, core/clump-table, core/newton-2,
core/oblate, core/z4c-faces. No branch that was offered for this release is left out.

Conflicts resolved by hand: `tracks/core/interfaces/rng.md` (scalar-3: the stream
registry of core-v0.4 kept, row 3 and its table of degrees of freedom taken),
`particles.hpp` (include list; option structures; members), `CMakeLists.txt`,
`nrpic.cpp` (`NrpicInit`; constants of `NrpicDepositSources`; the lines after the
particle loop). Three resolutions that no conflict marker asked for:
1. the additions of the fine-shape branch of the deposit kernel (cosmo-amr) go through
   the deposit target of build-openmp (`dep.Add`), so that `deposit_threads = private`
   holds them;
2. after the particle loop the private copies are summed into the source array
   (`thread_dep.End`) before the clouds of other ranks are added to it
   (`NrpicMpiDepositRemote`);
3. `NrpicMpiInit` stops a run on more than one rank, with a message, for the options
   whose sums, records or deposit are those of one rank: `removal_record`,
   `acc_nsphere`, `peri_count`, `perturb_gamma`, `id_solve`, `region_dcycle`,
   `deposit_fine_shape` (beside the four of the package: `pusher = newton`,
   `collisions`, `test_kick`, `curv_dt`).

### Behaviour that changes without an option

1. **Guard.** A run with Z4c whose evolved fields are not finite stops: diagnostic on the
   terminal and in `<basename>.guard.txt`, every output written once, exit status 3
   (releases before: the run went on to its limit with status 0). The check runs on the
   initial data and after every cycle. `<z4c_guard> stop_nonfinite = false` gives the
   old behaviour. A script that takes a non-zero status for a crash must know status 3.
2. **Place of two files.** `<basename>.horizon_summary_<n>.txt` (and the finder's
   verbose, grid and Ylm files) and `<basename>.co_<n>.txt` are opened at their first
   record, in the run directory of `-d`; the releases before opened them in the
   directory the executable was started in. Runs started inside their run directory see
   no change. A run without a single search still leaves its summary file.
3. **Periodic meshes.** The points of a trial surface of the horizon finder and the
   position of a tracker are mapped into the box, and `<z4c_amr> method = tracker`
   measures the distance to the nearest image. Results change only where a surface or a
   tracker reaches a face of a periodic box (the releases before left such points out
   of the surface integrals, or lost the tracker).
4. `nrpic_cosmo` enrols a refinement function: `<amr_criterion0> method = user` works
   (it called a null pointer before). Restart output of such a run writes
   `<name>.rst.amr` beside the mesh restart file.
5. More than one MPI rank no longer stops in `NrpicInit`: the particle module runs, or
   stops in `NrpicMpiInit` with the name of the option that is not ported.
None of these changes a byte of the twelve regression set-ups (below).

### Input options (`tracks/core/verify/options_at.py core-v0.4 HEAD`)

25 options added, none removed, no default changed
(`scratch/core/tmp/lead_v05/options_v04_v05.txt`); the scan does not see names that the
source builds at run time, added here by reading the source.

- `<scalar_field>` con_signed
- `<particles>` deposit_threads; deposit_fine_shape; region_dcycle, region_x1..3,
  region_radius1..4, region_horizon, region_horizon_factor
- `<particles_amr>` ppc_refine, ppc_derefine, lapse_ratio_1.., chi_ratio_1..,
  hysteresis, max_level, verbose
- `<z4c>` dt_lightspeed, tracker_walk_tol
- `<z4c_guard>` stop_nonfinite (default true), stop_chi_nonpositive, stop_dt_below,
  stop_no_particles, check_dcycle
- `<fastflow>` diagnostics
- `<problem>` (nrpic_cosmo) shift_x1, shift_x2, shift_x3

### Files and formats added (`docs/FORMATS.md`, last section)

`<basename>.region.hst`; `<basename>.guard.txt`; `<basename>.horizon_status_<n>.txt`;
`rst/<basename>.NNNNN.rst.amr`; `<basename>.mpi.hst`; columns 21 to 27 of
`<basename>.sf.con.hst`. No existing format changes.

### Build scripts

`scripts/build_cpu_omp.sh <dir>` (threaded; `OMP_OPT=debug` for the flags of the serial
build); the MPI build has no script of its own:
`CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON" scripts/build_cpu.sh <dir>` (and `build_gpu.sh`
for cards), with the Open MPI of the machine (`/home/emost/codes/openmpi`).
`scripts/cpu_run.sh` starts a threaded run with a placement that does not collide with
other sessions (`scripts/README.md`, "Threaded processor runs").

### Evidence

Byte regression against core-v0.4 on the twelve set-ups of wave 1: PASS for the serial
build (run core-20261121-063859-e410ee3) and for the MPI build started without mpirun
(run core-20261121-065743-1202666). Quick tests of the four branches, the threaded and
the MPI build, and the card check: `RELEASE-v0.5.md`. The capability tests were run by
the work packages on the executables of their branches (run ids in each interface
document, journals `tracks/core/JOURNAL-{scalar3,omp,cosmo-amr,mpi}.md`, READY files
copied to `scratch/core/exe/core_nrpic_v05/branches/`).

### Known limitations carried into core-v0.5

`tracks/core/stage/G2/OPEN.md` (section of core-v0.5) and the READY of the published
executables. The most important: on several ranks eleven options stop the run, and the
horizon finder at marginal resolution gives rank-dependent surfaces (so excision by a
horizon is not the same on every rank count); `deposit_fine_shape` has no limiter
(negative leaf-cell energy in sparse regions) and quadratic and cubic clouds are not
uniform across a level boundary; refinement levels take one global step; the MPI card
build is not part of the release; MPI with threads, and adaptive refinement under
threads or on several ranks with `<particles_amr>`, are untested.


## core-v0.4 (release candidate, 2026-11-21): the seven wave-2 source branches

Record: `tracks/core/RELEASE-v0.4.md` (first line: source commit and regression
verdict; the regression table; the quick tests; the card check). Source commit
**f9323185** (f93231854cf038db56bd8c37a47c39c2ba6b1f14) of `core/nrpic`: the last commit
that changes `athenak/`, `python/`, `problems/` or `scripts/`; later commits add records
(`tracks/core/`, `docs/COLLISIONS.md`) and merge main. Executables built from it, with
READY (every new option with one example input), COMMIT and SHA256SUMS:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/`.

### What is merged (in this order, one merge commit per branch)

| Branch (tip merged) | Merge | Capability | Switch (absent = off) | Interface document |
|---|---|---|---|---|
| core/requests-b (f134b775) | 3ab47062 | linear-wave generator transverse and traceless for any wave vector, cross polarization, error file; mesh output in double precision; Weyl scalar labelled at the end of the step; restart header bytes zeroed; thin periodic boxes and lattice jitter in the initial-data tool | `<problem> amp_cross, phase_cross`; `<outputN> double_precision`; `<z4c> waveform_at_new_time` | `tracks/core/interfaces/REQUESTS_B.md`, `docs/FORMATS.md`, `docs/UPSTREAM_DEFECTS.md` |
| core/gauge (58d10777) | 120aa7cf | lapse relaxation where matter expands; shift damping that follows the puncture trackers (`z4c/z4c_gauge_ext.hpp`) | `<z4c> lapse_leak`; `<z4c> shift_eta_profile` | `tracks/core/interfaces/cosmo_gauge.md` section 7 |
| core/scalar-2 (207424d2) | 54dc527e | initial slice of a stochastic-inflation run at N*; constraint record `sf.con.hst`; double-precision dumps with the metric; scale of the mode functions | `<problem> id = stochastic`; `<scalar_field> con_dcycle, dump_metric, noise_mode_scale` | `tracks/core/interfaces/scalar_field_2.md` |
| core/clump-curvature (56d7335c) | e2498da4 | Gaussian clumps of `nrpic_cf` with momentum and spin (smeared Bowen-York curvature); generator model `clumps` of `problems/ic/make_ic.py` | `comp<c>_p1..3`, `comp<c>_s1..3` on a component of type gaussian | `tracks/core/interfaces/moving_clumps.md` |
| core/id-solver (d88ff4f9) | de42b294 | elliptic solve of the Hamiltonian constraint (and, optionally, of the momentum constraint) on the mesh of the run before the first step; Robin faces of the multigrid solver | `<particles> id_solve`, `id_vector`; `<gravity> mg_bc = robin` | `tracks/core/interfaces/id_solver.md` |
| core/requests-adf (b6041dbc; records bc38aafc merged later as 148a302e) | 7b0fcf27 | tracers (m = 0) on timelike geodesics on every metric; restart keeps the output schedule; excision on analytic metrics; accretion diagnostics; external gravity of the Newtonian mode; common horizon of one pair | corrections act without a switch (`<particles> zero_mass = null` restores the tracer rule of core-v0.3); `<particles> removal_record, acc_nsphere, peri_count, newton_pm_mass, newton_bg_t0`; `<fastflow> punc_pair_a_<n>` | `tracks/core/interfaces/REQUESTS_ADF.md`, `diagnostics.md`, `multi_puncture.md` |
| core/collisions-2 (8c03bc96; records 4c798e7a merged later as e9644451) | f9323185 | collisions that conserve the pair's canonical energy with the metric at each particle; static conformally flat test metric; perturbing radial force | `<particles> coll_energy`; `<problem> metric_kind = static_conformal`; `<particles> perturb_gamma` | `tracks/core/interfaces/collisions.md` section 11, `rng.md` section 6.1, `docs/COLLISIONS.md` |

No branch is left out. Conflicts resolved by hand in the merges: `z4c.cpp`, `z4c.hpp`
(gauge after requests-b), `CMakeLists.txt`, `nrpic.cpp`, `nrpic_io.cpp`, `particles.hpp`
(the three particle branches), `docs/FORMATS.md`, `tracks/core/interfaces/rng.md`
(both rows of the stream table kept). Each side keeps its behaviour: the quick test of
every branch gives, with the merged executable, the bytes of the branch's own executable.

### Behaviour that changes without an option (corrections)

1. Restart files: the 36 bytes of the nine never-set members of `Mesh::mesh_indcs` are
   zero. Byte comparisons of restart files against core-v0.3 differ in these bytes.
2. `Driver::Finalize` no longer advances `last_time` of an output written off its
   schedule at the end of a run: the parameter dump embedded in such final files differs
   in `last_time` lines, and a run continued after a stop at the wall-clock or cycle limit
   writes every scheduled output (core-v0.3 lost one per stop).
3. A particle with m = 0 on the mesh metric is a tracer on a timelike geodesic
   (core-v0.2 and core-v0.3: null). `<particles> zero_mass = null` gives the old rule;
   light rays (m < 0) are not affected.
4. Analytic metrics honour `<particles> alpha_exc` (default -1: off) and remove flagged
   particles.
5. `z4c_linear_wave`: sign of two tensor components for an oblique wave vector, and the
   error routine compares at the final time: an existing oblique input with kx2 != 0
   changes (the upstream tensor was not transverse there).
6. On a card, collisional runs without the new options differ from the core-v0.3 card
   executable at rounding (momenta 2e-14, the same pairs in every step; run
   core-20261119-141059-f3ccf56 of the package); processors are byte-identical.

### Input options (`tracks/core/verify/options_at.py core-v0.3 HEAD`)

61 options added, none removed, no default changed
(`scratch/core/tmp/lead_v04/options_v03_v04.json`); the scan does not see names that
the source builds at run time, added here by reading the source.

- `<outputN>` double_precision
- `<z4c>` waveform_at_new_time, lapse_leak, lapse_leak_alpha, shift_eta_profile,
  shift_eta_mref, shift_eta_width, shift_eta_width_local
- `<gravity>` `mg_bc = robin`, robin_x1, robin_x2, robin_x3
- `<particles>` id_solve, id_residual, id_psi_init, id_tol, id_maxit, id_lin_tol,
  id_lin_maxit, id_mg_tol, id_dump, id_vector, id_vector_residual, id_vector_tol;
  zero_mass; removal_record, acc_nsphere, acc_radius1..4, acc_x1..3, acc_tracker,
  acc_dcycle, peri_count, peri_rmax; newton_pm_mass, newton_pm_x1..3, newton_pm_soft,
  newton_pm_soft_frame, newton_bg_t0; coll_energy; perturb_gamma, perturb_time,
  perturb_tstart, perturb_x1..3
- `<problem>` (z4c_linear_wave) amp_cross, phase_cross; (scalar_field) `id = stochastic`,
  slice_window, slice_k2, slice_delta_pi; (nrpic_cf, type gaussian) comp<c>_p1..3,
  comp<c>_s1..3; (nrpic_geodesic) `metric_kind = static_conformal`, psi0, alpha_amp,
  psi_amp, shift_amp, mode_n1..3
- `<scalar_field>` noise_mode_scale, con_dcycle, dump_metric, dump_constraints,
  dump_magnitudes, dump_noise
- `<fastflow>` punc_pair_a_<n>, punc_pair_b_<n>

### Files and formats added (`docs/FORMATS.md`)

`<basename>-errs.dat` (linear wave); bin output with 8-byte values; `<basename>.sf.con.hst`
and scalar-field dumps of layout NRSFDMP2; `<basename>.idsolve.txt`, `.idsolve.bin`,
`.idvector.bin`; `<basename>.removed.bin`, `<basename>.acc.hst`, a last block of
pericentre counts in snapshots; history columns 32 to 36 of `<basename>.coll.hst` and
collision dumps of version 2 (NRPCOLD2). The particle restart format keeps three
integers per particle.

### Evidence

Byte regression against core-v0.3 on the twelve set-ups of wave 1: PASS (run
core-20261120-221607-4985804). Quick test of every merged branch and the card check:
`RELEASE-v0.4.md`. The capability tests were run by the work packages on the
executables of their branches (run ids in each interface document, journal
`tracks/core/JOURNAL-{bfix,gauge,scalar2,clump,idsolve,dfix,coll2}.md` and READY file,
copied to `scratch/core/exe/core_nrpic_v04/branches/`).

### Known limitations carried into core-v0.4

`tracks/core/stage/G2/OPEN.md` (section of 2026-11-21) and the READY of the published
executables. The most important: no two new capabilities were run together; the
initial-data solver works on uniform meshes on one rank without punctures; clumps with
momentum are Gaussians only; `<fastflow> hmean_tol` acts on the surface integral of the
expansion and silently ends searches in cosmological boxes; the particle module is
single-rank.


## core-v0.3 (tagged; written 2026-11-15 as a proposal): wave-1 capabilities of decision 0010

Proposed tag: `core-v0.3` on commit **609a875** of `core/nrpic` (the last commit that
changes `athenak/src/`; every later commit of this session touches `tracks/core/` only).
Both executables of the regression were built from a `git archive` of 609a875:
`wt/core/.work/build_cpu_609a875/src/athena` (sha256 in
`scratch/core/tmp/lead/exe_sha256.txt`) and `wt/core/.work/build_gpu_609a875/src/athena`.

```
git tag -a core-v0.3 609a875 -m "core-v0.3: collisions, scalar field and stochastic sources, Newtonian mode, Bowen-York punctures, initial data with extrinsic curvature, reproducible random numbers"
git push origin core-v0.3
```

### What is merged (in this order)

| Branch (head) | Merge | Capability | Switch (absent = off) | Interface document |
|---|---|---|---|---|
| core/rng (a6e5c46) | fcc3179 | counter-based random numbers (Philox-4x64-10), bit-identical on processor, card and NumPy twin; test kick | `<job> rng_seed`; `<particles> test_kick` | `tracks/core/interfaces/rng.md`, `docs/RNG.md` |
| core/collisions (ba50bff) | c88804c | relativistic Monte Carlo collisions in the normal-observer frame of each cell; homogeneous static metric for tests (`nrpic_geodesic` `metric_kind = homogeneous`) | `<particles> collisions = true` | `tracks/core/interfaces/collisions.md`, `docs/COLLISIONS.md` |
| core/scalar-field (59c47d7) | 65648c8 | minimally coupled scalar field evolved with Z4c, sources through `Tmunu::tmunu_tot` (with particles), stochastic sources (generic and Mukhanov-Sasaki), restart side file, outputs `sf_phi`, `sf_Pi`, `sf` | a `<scalar_field>` block | `tracks/core/interfaces/scalar_field.md` |
| core/id-extrinsic (6fa6472) | dc93a72 | `nrpic_cf` radial table of format 2 (extrinsic curvature, lapse, shift; optional `# breaks`); expanding-ball generator `problems/ic/make_ball.py` | a table whose header says `# format = 2` | `tracks/core/interfaces/spherical_id_format2.md`, `docs/FORMATS.md` |
| core/multi-puncture (81d4651) | 7c11538 | Bowen-York momentum and spin for any number of punctures of `nrpic_cf`, regular corrections (closed form with background factor, or table), trackers, refined regions and horizon finders per puncture | `comp<c>_p1..3`, `_s1..3`, `_corr`; `<problem> puncture_setup = true` | `tracks/core/interfaces/multi_puncture.md`, `docs/FORMATS.md` (format mp1) |
| core/newton (ce329f5) | 66bd4c3 | Newtonian mode of the particle module: rest-mass deposit, multigrid Poisson solve, kick-drift-kick, comoving coordinates; `MGGravityDriver::SolveSource` | `<particles> pusher = newton` | `tracks/core/interfaces/newtonian_mode.md`, `docs/FORMATS.md` |

Maintainer commits on top of the merges:
- **0f11630** `nrpic_cf`: the curvature of a format-2 table is added to the Bowen-York
  curvature instead of replacing it (the semantic overlap of core/id-extrinsic and
  core/multi-puncture). Verified by test P5 of the lead (run id in `stage/G2/EVIDENCE.md`).
- **609a875** collisions refuse `pusher = newton` (the Newtonian mode keeps the potential
  in the lapse slot that the pair probability reads).

### Input options (`tracks/core/verify/options_at.py 52c44eb 609a875`)

80 options added, none removed. The ten "changed defaults" the scan reports are second
call sites in new opt-in files (`nrpic_puncture_setup.hpp` writes `<fastflow>` and
`<z4c_amr>` parameters only with `puncture_setup = true`; `scalar_field_tests.cpp` reads
`<problem> id` and `omega` for its own generator; `<particles> deposit` defaults to true
also for `pusher = newton`). No default of an existing input changed; the byte
regression below confirms it for twelve existing set-ups.

- `<job>` rng_seed
- `<particles>` collisions, coll_sigma, coll_sigma_model, coll_sigma_w, coll_pmax,
  coll_subcycle, coll_nsub_max, coll_cell_factor, coll_weights, coll_hist_dcycle,
  coll_dump_cycle, coll_budget; test_kick, test_kick_mode, test_kick_key,
  test_kick_sigma, test_kick_prob; newton_expansion, newton_hubble, newton_exponent,
  newton_cfl, newton_mg_tol; `pusher = newton`
- `<problem>` (nrpic_cf) shift, shift_comp, comp<c>_p1..3, comp<c>_s1..3, comp<c>_corr,
  comp<c>_corr_file, corr_background, puncture_setup, puncture_horizons,
  puncture_radius, puncture_level, comp<c>_radius, comp<c>_level; (nrpic_geodesic)
  metric_kind, alpha0, gxx..gzz; (rng_test, scalar_field) test-generator options
- `<scalar_field>` (new block) potential, mass, lambda, mu, v0, vev, v_offset,
  table_file, couple, diss, hist_dcycle, dump_dcycle, dump_dt, noise and its 20
  noise_* options
- outputs `sf_phi`, `sf_Pi`, `sf` (NOUTPUT_CHOICES 154 -> 157)

### Files and formats added

`<basename>.coll.hst`, collision dump; `<basename>.sf.hst`, `.sf.NNNNN.dump`, restart side
file `<restart>.sf`; `<basename>.newton.hst`, restart side file `*.rst.prt.nwt`; radial
table format 2; puncture correction table format mp1 (`docs/FORMATS.md`).

### Evidence

Regression and tests on the merged executables: `tracks/core/stage/G2/REPORT.md` and
`EVIDENCE.md`. The capability tests themselves were run by the work packages on their
branches (run ids in each interface document and journal); the lead reran the quick
ones on the merged executables.

### Known limitations carried into core-v0.3

`tracks/core/stage/G2/OPEN.md` and `tracks/core/RISKS.md`. The most important: the
collision steps raise the energy at the particles' own metric by 1e-9 to 1e-8 per
collision in a potential (cell-frame conservation only); no lapse condition tried for the
expanding ball is free of a lapse front from a sharp surface; the shift damping of the
Gamma-driver is one number for all punctures; the Newtonian mode, the scalar field and
the collisions have no test on refined meshes beyond one smoke run each, and the particle
module is single-rank.
