---
from: orch
to: all
type: info
needs_reply_by: none
refs: [tracks/core/RELEASE-v0.5.md, tracks/core/CHANGELOG.md, scratch/core/exe/core_nrpic_v05/READY, coord/DECISIONS/0019]
---
Release core-v0.5 is tagged and merged into main (release clerk, decision 0019 item 4).

Tag core-v0.5 on c3eb42e0, the source commit of core/nrpic: the four wave-3a branches
scalar-3, build-openmp, cosmo-amr, mpi, on top of core-v0.4. Merge on main: 1e133480.
Byte regression against core-v0.4 on the twelve set-ups of wave 1: PASS for the serial
processor build (run core-20261121-063859-e410ee3, 75 of 75 items identical) and for the
MPI build started without mpirun (run core-20261121-065743-1202666); quick test of every
merged branch, the threaded and the MPI build: PASS (runs core-20261121-065009-29b855c,
judged in core-20261121-065726-bf06a85). NOT YET DONE: the card check of the merged card
executable (run core-20261121-070946-1907f7b, Slurm job 4772, still queued at tagging).
Until core writes its outcome into tracks/core/RELEASE-v0.5.md, no card build of this
source has run on a card; the card executable of core/cosmo-amr, the same deposit, passed
its own card check. Details: tracks/core/RELEASE-v0.5.md.

New options (absent = off, except the guard). All 25 with their defaults:
tracks/core/CHANGELOG.md, section core-v0.5. One example input per option, what is
tested and the known defects:
/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v05/READY (the full description of each
package: branches/READY.<branch> there).
- threaded processor build (scripts/build_cpu_omp.sh; start runs with scripts/cpu_run.sh,
  scripts/README.md "Threaded processor runs"); deposit into one private copy per thread,
  bit for bit at a fixed thread count: <particles> deposit_threads = atomic | private.
  The threaded build is NOT a byte reference (at one thread 44 of 75 regression items
  differ from core-v0.4 at rounding); the serial build stays the reference.
- the particle module on several MPI ranks: no option, mpirun -np N with the MPI build.
  On more than one rank these options stop the run with a message: removal_record,
  acc_nsphere, peri_count, perturb_gamma, id_solve, region_dcycle, deposit_fine_shape,
  pusher = newton, collisions, test_kick, curv_dt.
- adaptive refinement in nrpic_cosmo on particles per cell, lapse and chi:
  <amr_criterion0> method = user with <particles_amr> ppc_refine, ppc_derefine,
  lapse_ratio_<n>, chi_ratio_<n>, hysteresis, max_level, verbose; coarse clouds with their
  shape on fine leaf cells: <particles> deposit_fine_shape (no limiter yet); constraint
  norms inside and outside spheres: <particles> region_dcycle, region_x1..3,
  region_radius1..4, region_horizon, region_horizon_factor
- horizon finder and tracker in a periodic box: <fastflow> diagnostics,
  <z4c> tracker_walk_tol; step limit by the coordinate speed of light: <z4c> dt_lightspeed;
  shifted lattice: <problem> shift_x1..3 (nrpic_cosmo)
- guard: <z4c_guard> stop_nonfinite (default true), stop_chi_nonpositive, stop_dt_below,
  stop_no_particles, check_dcycle
- scalar field: signed constraint means, columns 21 to 27 of <basename>.sf.con.hst:
  <scalar_field> con_signed; the keys of the stochastic modes as named functions
  rng::ModeEntity, rng::StochasticModeStream (Python twins mode_entity,
  stochastic_mode_stream in python/nrpic/rng.py; the keys are those used before); the
  inflection (ultra-slow-roll) example problems/scalar/usr_stochastic.athinput; linear
  twin python/nrpic/sf_lattice.py

Changes that act without an option (read them before you compare with a run on core-v0.4;
none changes a byte of the twelve regression set-ups):
1. a run with Z4c whose evolved fields are not finite now stops with exit status 3 and
   <basename>.guard.txt (before: it ran on to its limit with status 0). A script that
   takes a non-zero status for a crash must know status 3; <z4c_guard>
   stop_nonfinite = false gives the old behaviour.
2. <basename>.horizon_summary_<n>.txt (with the finder's verbose, grid and Ylm files) and
   <basename>.co_<n>.txt are written in the run directory of -d, no longer in the
   directory the executable was started in.
3. on periodic meshes the horizon finder's trial surfaces and the trackers are mapped into
   the box; results change only where a surface or tracker reaches a face.
4. nrpic_cosmo enrols a refinement function (<amr_criterion0> method = user works); its
   restart output writes <name>.rst.amr beside the mesh restart file.
5. more than one MPI rank no longer stops in NrpicInit (see the list of options above).

Release executables of the main checkout, read-only, built from main after the merge
(scripts/build_gpu.sh, scripts/build_cpu.sh), and from your next sync the defaults of the
machine file harness/env/machines/anta.sh (NRPIC_GPU_EXE is the default --exe of nrpic-run
for batch and chain runs; NRPIC_CPU_EXE):
  /data/haiyangw/nrpic/.work/build_gpu_v05/src/athena   (cards)
  /data/haiyangw/nrpic/.work/build_cpu_v05/src/athena   (processors, serial)
Threaded and MPI processor builds of the same source:
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v05/athena_cpu_omp
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v05/athena_cpu_mpi
Older: core-v0.4 at .work/build_gpu_v04 and .work/build_cpu_v04; core-v0.3 at
.work/build_gpu_v03 and .work/build_cpu_v03; core-v0.2 at .work/build_gpu_c3 and
.work/build_cpu_c1. Both release builds finished without error (229 and 225 objects;
logs .work/build_gpu_v05.log, .work/build_cpu_v05.log); sha256 gpu 2512c8d5...6b61ea4,
cpu 222b8fa4...4cd7ac7e. They differ from the candidate's in
scratch/core/exe/core_nrpic_v05/ (other build directories), so compare outputs, not
checksums; no run has yet compared the release builds with the candidate's.

Interfaces: coord/INTERFACES/ holds the documents of core-v0.5 (new: cosmo_amr.md, mpi.md,
scalar_field_3.md, threaded_build.md; changed: rng.md, sections 6 and 6.2). The triage of
Track A's requests: tracks/core/interfaces/REQUESTS_A2.md. Not in this release
(for core-v0.6): core/id-solver-2, core/clump-table, core/newton-2, core/oblate,
core/z4c-faces (tracks/core/stage/G2/OPEN.md, section of core-v0.5).

What every track does now:
1. harness/bin/nrpic-ctx sync in your worktree (brings the tag's source, CLAUDE.md,
   coord/INTERFACES/ and the machine file with the new default executables).
2. Before relying on a new option, read its READY entry and tracks/core/stage/G2/OPEN.md
   (section of core-v0.5): the capability tests ran on each branch's own executable;
   MPI with threads, and adaptive refinement under threads or on several ranks, are
   untested.
3. New runs use the release executables (the paths above; for card runs the default of
   nrpic-run after the sync). Until core has judged job 4772 (RELEASE-v0.5.md), compare a
   card result that depends on a capability new in core-v0.5 with a processor run of the
   same deck before you rely on it. A comparison with a run on core-v0.4
   accounts for the five changes above, above all exit status 3 and the place of the
   horizon files.
4. Acknowledge this message: harness/bin/nrpic-ctx ack <file>.
