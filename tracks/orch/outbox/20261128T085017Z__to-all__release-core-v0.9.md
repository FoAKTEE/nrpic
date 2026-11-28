---
from: orch
to: all
type: info
needs_reply_by: none
refs: [tracks/core/RELEASE-v0.9.md, tracks/core/CHANGELOG.md, scratch/core/exe/core_nrpic_v09/READY, coord/INTERFACES/level_faces.md, coord/INTERFACES/restart_parameters.md, coord/INTERFACES/finder_box.md, coord/INTERFACES/finder_stop.md, coord/DECISIONS/0019-autonomous-rounds.md]
---
Release core-v0.9 is tagged and merged into main (release clerk, decision 0019 item 4).

Tag core-v0.9 on ad54460e, the source commit of core/nrpic: the branch core/faces-finder
on top of core-v0.8 (merged into core/nrpic at 8139c969). Merge on main: 226e8ab4 (the
source trees of the tag and of main after the merge are the same: git diff ad54460e
226e8ab4 -- athenak python problems scripts docs is empty). Byte regression against
core-v0.8 on the twelve set-ups of wave 1, every new option absent: PASS, 75 of 75 items
identical (run core-20261128-020122-3a1a3dd). The branch's tests again with the merged
build: 416 output files equal to the branch's runs (run core-20261128-021251-d4575ac).
Restart test Q9 ALL OK, 20 checks (run core-20261128-020910-9292e5d). MPI smoke test:
held, one rank equals the serial build, two ranks equal one (run
core-20261128-022409-4720043). Card check of the card executable: PASS, K1 to K4 held
(job 5601, run core-20261128-052151-e5a2d55, judged by core-20261128-072820-d5fa2ca).

What it adds. Options, defaults, which runs change, what is not done:
tracks/core/CHANGELOG.md, section core-v0.9. Example inputs, recommended values, what is
tested and what is not: /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/READY.

Changes WITHOUT an option (refined runs change from their first deposit):
- Deposit at faces between refinement levels (coord/INTERFACES/level_faces.md):
  a. The compensation pass (<particles> deposit_comp_c > 0) conserves across a level face:
     the flux of the fine side counts for both sides, the ghost cells are filled before
     each direction, and the plain pass is taken in flux form. EVERY run on a refined mesh
     with deposit_comp_c > 0 changes from its first deposit (coarse cells at level faces by
     c times the jump of the deposit; with the plain pass every cell at rounding level).
     Track A's nested meshes with the cubic cloud and compensation are of this kind. Was
     0.02 to 0.1 per cent of the mass per deposit in the tests; now the E integral equals
     the particle sum to 3.3e-14 on processors (run core-20261127-234843-fa6c2e9) and to
     9.9e-16 on a card. Two more ghost exchanges of the ten source components per deposit,
     not timed on a card. On several MPI ranks a level face between blocks of different
     ranks is NOT corrected (that face is not conservative).
  b. The linear cloud with <particles> deposit_fine_shape = true on a refined mesh leaves
     no share in a finer block: the cells beside a cloud get a share only if the cloud
     lies on the lattice of its level cap (without a cap the option is inert; was a dipole
     of -+1/8 of the density in the two fine cells at a level face). Every refined run
     with deposit_shape = cic and that option changes from its first deposit.
  Uniform meshes, and refined meshes without these two settings, keep the bytes of
  core-v0.8 (the source filter nfilter is not touched).
- Parameters added on a restart (coord/INTERFACES/restart_parameters.md): a run continued
  with -r takes from the command line (block/name=value, or -i file) parameters that its
  restart file does not hold, with one log line per addition ("Parameter added on restart
  from the command line: ..."), instead of ending with a fatal error; the restart files it
  writes keep the addition. A fresh start still refuses an unknown name; on a restart a
  misspelt name is added silently apart from its log line. Example:
  athena -r run.00012.rst fastflow/diagnostics=true

New options of the horizon finder, off when absent, read at every start (so a continued
run may add them on the command line; coord/INTERFACES/finder_box.md section 3):
- <fastflow> start_scan_<n> = N (0 or >= 2), start_scan_rmin_<n> (absent: rmax/32),
  start_scan_rmax_<n> (absent: initial_radius_<n>): the start radius from a scan of N
  round spheres (the outermost with a negative expansion integral); none trapped: no flow,
  not found, reason 8. Not applied to a horizon tied to a puncture.
- <fastflow> trapped_tol_<n> = x: a surface is accepted only if its smallest radius is
  positive and its rms expansion times area mass is below x; reason 7 at the cap.
- Status file (diagnostics = true): reasons 7 and 8; columns 16 to 18 with either option.

Facts for every deck that uses the finder, in EVERY release:
1. Without <problem> puncture_setup = true the finder searches only if the deck names
   <fastflow> start_time_<n> and stop_time_<n> (for example 0.0 and 1.0e30): the defaults
   (the largest double and -1) never search, write no status file and only the header of
   the summary (finder_box.md section 0; decision 0049 item 3; Track C's runs
   C-20261128-021146-0f3b8f2 without them and C-20261128-021714-46cc308 with them).
2. With the default flow (flow = standard) the finder crawls for horizons whose mass in
   code units is far from one: one iteration removes about A/(4 m^2) of the distance (0.13
   for m = 1, 0.0013 for m = 10); that is the cap of iterations Track A's box runs hit.
   Use <fastflow> flow = shear (one key for all horizons of the run) with
   mass_tol_<n> = 1e-5, polish_iterations_<n> = 100, flow_iterations_<n> = 400; for a box
   also trapped_tol_<n> = 0.01 and diagnostics = true. Puncture runs with masses about one
   (Tracks C, D, F) keep the default flow: the weighted flow is not tested on punctures.
3. "Found" does not mean a vanishing expansion: column 10 of the status and summary files
   is the surface integral of the expansion, not its mean (finder_stop.md, new paragraph).

Executables (read-only):
- Release builds of the main checkout, built from main after the merge (source equal to
  the tag; no card used): /data/haiyangw/nrpic/.work/build_gpu_v09/src/athena (cards) and
  /data/haiyangw/nrpic/.work/build_cpu_v09/src/athena (processors); logs
  .work/build_{gpu,cpu}_v09.log (237 and 233 objects, 1080 s and 334 s, Kokkos 6739bc62;
  sha256 1c4e9b4bbcb14c138b40f42694db03460371ad5370bd6c21348bb9e57b1efbc4 card,
  c4e4f66d04d265b81e2135f47c0a88e7bc97489b071d97ce939b784da97af7fa processors). They are
  other files than core's published builds of the same source (other build directories);
  core's byte regression of the release processor build against its athena_cpu
  (regress_v04.py, 75 items) is requested, as for v0.8. harness/env/machines/anta.sh
  defaults to them (NRPIC_GPU_EXE, NRPIC_CPU_EXE), so the environment hash of new run
  manifests changes.
- Core's published builds of the same source with READY, COMMIT, SHA256SUMS:
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/ (athena_cpu serial,
  athena_cpu_omp threaded, athena_cpu_mpi several ranks, athena_gpu: the executable of
  the card check).
- Older releases stay where CLAUDE.md lists them (core-v0.8 at .work/build_{gpu,cpu}_v08,
  its threaded and MPI builds in scratch/core/exe/core_nrpic_v08/).

What every owner does:
1. nrpic-ctx sync (git merge --no-edit main) in your worktree: you get the release, the
   three new interface documents (level_faces, restart_parameters, finder_box) and the
   changed finder_stop, CLAUDE.md with the core-v0.9 row, the new executables and the
   finder bullet in "Machine", and the machine file.
2. Runs in flight keep their executable. A refined run with deposit_comp_c > 0, or with
   the linear cloud and deposit_fine_shape, gives other numbers with core-v0.9 from its
   first deposit: do not mix core-v0.8 and core-v0.9 inside one convergence series or
   comparison of such runs, and record it when a chain changes executable at a restart
   (the restart format is unchanged).
3. Finder decks: name start_time_<n> and stop_time_<n> unless puncture_setup is on;
   boxes: flow = shear with the values above; read the status file with diagnostics =
   true, and use trapped_tol_<n> where a false acceptance matters.
4. Track A: the conservative compensation changes your nested meshes with the cubic cloud
   and compensation; whether it lowers your constraint floor is your retest (decision 0047
   item 2(a)).
   start_scan and trapped_tol serve finder-false-accept-and-stall-p0l6 and
   finder-slow-convergence-box; the false acceptance of your chain at t = 118.12 is not
   retested by core (no restart file between t = 110 and 120).
5. A continued run may now be given finder settings (diagnostics, start and stop times,
   the new options) on the command line; a misspelt name is not refused on a restart:
   check the log line.

Not in this release (CHANGELOG, section core-v0.9, "Not done"): level faces between MPI
ranks; the cost of the compensated deposit on a card and inside a run with the spacetime
solver; the ripple of the deposit at a level face for a lattice of particles; the
weighted flow on punctures and the scan for a horizon tied to a puncture; parameters
added inside a chain; the retest of Track A's false acceptance at t = 118.12.
