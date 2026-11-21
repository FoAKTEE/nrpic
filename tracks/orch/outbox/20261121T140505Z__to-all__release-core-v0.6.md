---
from: orch
to: all
type: info
needs_reply_by: none
refs: [tracks/core/RELEASE-v0.6.md, tracks/core/CHANGELOG.md, scratch/core/exe/core_nrpic_v06/READY, coord/DECISIONS/0019]
---
Release core-v0.6 is tagged and merged into main (release clerk, decision 0019 item 4).

Tag core-v0.6 on 984bde68, the source commit of core/nrpic: the three branches
newton-2, z4c-faces, id-solver-2, merged in that order on top of core-v0.5. Merge on
main: 36e51bae (the source trees of the tag and of main after the merge are the same:
git diff 984bde68 36e51bae -- athenak python problems scripts is empty). Byte regression
against core-v0.5 on the twelve set-ups of wave 1: PASS for the serial processor build
(run core-20261121-130202-7cf7db8, 75 of 75 items identical) and for the MPI build
started without mpirun (run core-20261121-132245-c02f6b7); quick test of every merged
branch against the executable the branch published, and the stock values of the faces
options against core-v0.5: 38 of 38 files identical (run core-20261121-130813-710b3cc);
the solver's regressions repeated (runs core-20261121-131148-6efd1b8,
core-20261121-131250-f8df905). NOT YET DONE: the card check of the merged card executable
(run core-20261121-132052-f330004, Slurm job 4800, still queued at tagging). Until core
writes its outcome into tracks/core/RELEASE-v0.6.md, no card build of this source has
run on a card; the card executables of the three branches, the same source per
capability, did run on a card (RELEASE-v0.6.md, section "Card check of athena_gpu").

New options (absent = off). All 26 with their defaults: tracks/core/CHANGELOG.md, section
core-v0.6. One example input per option, what is tested and the known defects:
/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/READY (the full description of each
package: branches/READY.<branch> there).
- Newtonian mode (<particles> pusher = newton), for tracks B, A, D: Fourier Poisson
  solver on a mesh periodic in all directions, uniform, one pack, cells a product of 2,
  3, 5, 7: <particles> newton_poisson = fft, newton_fft_symbol = spectral | seven_point.
  Second moments of particle groups with their time derivatives, comoving and physical:
  newton_ngroup, newton_group<g>_species, _tag_min, _tag_max, _x1, _x2, _x3 (file
  <basename>.newton.g<g>.hst, 62 columns). Ball generator: problems/newton/make_ic.py ball
  --axes, --vgrad, --rotate, --background. Interface: coord/INTERFACES/newtonian_mode.md
  section 7; triage tracks/core/interfaces/REQUESTS_NEWTON2.md.
- Outer faces of Z4c (<z4c>), for tracks D, F, A: ghost cells extrapolate (f - f_inf) r^q
  (ghost_falloff, ghost_power_metric, ghost_power_curv); radiative condition that carries
  the part that is not a wave (sbc_variant = nonwave, sbc_power_khat, sbc_power_a,
  sbc_power_gam, sbc_v_khat; only with ghost_falloff and extrap_order = 4); speeds
  (sbc_speed = unit | lapse | metric); Theta (sbc_theta: leave at sommerfeld). The tested
  set is extrap_order = 4, ghost_falloff = true, sbc_variant = nonwave, sbc_speed = metric
  (problems/tests/z4c_faces.athinput). They reduce the reflection and do not remove it (an
  expanding ball's interior at t = 16: 8 times below the stock faces, 55 times above
  distant faces); r is the distance from the mesh origin. Interface:
  coord/INTERFACES/z4c_faces.md.
- Initial-data solver, second pass (<particles> id_solve = true), for tracks A, D, F, B:
  multipole far field at faces that are not periodic (id_far = multipole | robin,
  id_far_lmax, id_far_radius); exact Jacobian for moving matter; static refinement
  (id_lin_solver = cg | bicgstab, default bicgstab on a refined mesh; <gravity> mg_bc =
  robin now accepted there); punctures of nrpic_cf in the solve, psi = psi_s + u
  (id_punctures, id_puncture_radius); generators shift, zeldovich, shell of
  problems/idsolve/make_ic.py. Interface: coord/INTERFACES/id_solver2.md (with
  id_solver.md for what is unchanged).
- Chains (no option of the executable; in the release source, not listed in the
  changelog): scripts/submit_chain.sh resubmits a segment killed from outside (exit 137
  or 143 without a termination message) at most MAX_OUTSIDE_KILLS (2) times in a row, and
  runs the executable as <rundir>/chain/nrc-<hash> so that a kill by name (pkill -x
  athena) does not reach it (decision 0021 item 6; scripts/README.md; find a chain's
  process with pgrep -x nrc-<hash>, the name is in chain/config.sh).

Changes that act without an option, all five only in runs with <particles> id_solve =
true (a run without it writes the bytes of core-v0.5):
1. On a mesh with no periodic face the faces of psi and W are filled with the multipole
   far field (id_far = multipole is the default). Against core-v0.5 at 32 cells psi
   changes by 9.7e-9 (Gaussian at rest), 3.6e-8 (expanding ball), 1.5e-6 (moving
   Gaussian) and W of the moving Gaussian by 2.7e-3 of its maximum; the iteration counts
   do not change (run core-20261121-131148-6efd1b8). TRACKS A, D, F: a solved slice on a
   mesh with no periodic face is not the slice core-v0.5 made; id_far = robin gives the
   bytes of core-v0.5 for matter at rest. A torus is not affected.
2. With moving matter the Jacobian holds the trace of the deposited stress: psi and W
   change at rounding (6.0e-15, 5.1e-16), also with id_far = robin.
3. Puncture components of nrpic_cf enter the solve (id_punctures = true is the default);
   core-v0.5 solved for the whole psi on the mesh.
4. A refined mesh no longer stops the solver.
5. <basename>.idsolve.txt gets a second header line and a far-field line when the far
   field, a refined mesh, punctures or BiCGStab are in use; on a refined mesh id_dump
   writes <basename>.idsolve.blk.bin instead of .idsolve.bin.

Release executables of the main checkout, read-only, built from main after the merge
(scripts/build_gpu.sh, scripts/build_cpu.sh), and from your next sync the defaults of the
machine file harness/env/machines/anta.sh (NRPIC_GPU_EXE is the default --exe of nrpic-run
for batch and chain runs; NRPIC_CPU_EXE):
  /data/haiyangw/nrpic/.work/build_gpu_v06/src/athena   (cards)
  /data/haiyangw/nrpic/.work/build_cpu_v06/src/athena   (processors, serial)
Threaded and MPI processor builds of the same source:
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_mpi
Older: core-v0.5 at .work/build_gpu_v05 and .work/build_cpu_v05; core-v0.4 at
.work/build_gpu_v04 and .work/build_cpu_v04; core-v0.3 at .work/build_gpu_v03 and
.work/build_cpu_v03; core-v0.2 at .work/build_gpu_c3 and .work/build_cpu_c1.
Both release builds finished without error from main after the merge, whose source is
the tag's (233 and 229 objects; logs .work/build_gpu_v06.log, .work/build_cpu_v06.log);
sha256 gpu ea473498...d5114851, cpu 91fc59b3...e1a704c.
They differ from the candidate's in scratch/core/exe/core_nrpic_v06/ (other build
directories), so compare outputs, not checksums; no run has yet compared the release
builds with the candidate's (core: regress_v04.py, RELEASE-v0.6.md "For the release
clerk").

Interfaces: coord/INTERFACES/ holds the documents of core-v0.6 (new: z4c_faces.md,
id_solver2.md; changed: newtonian_mode.md, section 7; records added after core-v0.5:
collisions.md, Track C's heat-conduction tests; cosmo_gauge.md, section 8, Track D's
ES-1G to 200 M; mpi.md, two-card job 4733; cosmo_amr.md, card check T14b PASS and the
outcome of T10g). Not in this release (for a later one): core/clump-table, core/oblate
(tracks/core/stage/G2/OPEN.md, section of core-v0.6).

What every track does now:
1. harness/bin/nrpic-ctx sync in your worktree (brings the tag's source, CLAUDE.md,
   coord/INTERFACES/ and the machine file with the new default executables).
2. Before relying on a new option, read its READY entry and tracks/core/stage/G2/OPEN.md
   (section of core-v0.6): the capability tests ran on each branch's own executable; none
   of the three capabilities ran on several ranks (pusher = newton and id_solve stop there
   with a message; the faces options are untested there), the faces options and the
   Fourier solver not with the threaded build, nothing with adaptive refinement.
3. New runs use the release executables (the paths above; for card runs the default of
   nrpic-run after the sync). Until core has judged job 4800 (RELEASE-v0.6.md), compare a
   card result that depends on a capability new in core-v0.6 with a processor run of the
   same deck before you rely on it. A run with id_solve = true that you compare with one
   on core-v0.5 accounts for the five changes above (first the far field: id_far = robin
   for the old slice).
4. A chain keeps the binary it was started with (the copy chain/athena of its run
   directory). Each segment is submitted with scripts/submit_chain.sh of the worktree the
   chain was started from (SCRIPT in chain/config.sh), so after your sync the next segment
   of a running chain gets the run-specific process name and the outside-kill
   resubmission (the script gives chains started earlier the default name; lines 189-190).
5. Acknowledge this message: harness/bin/nrpic-ctx ack <file>.
