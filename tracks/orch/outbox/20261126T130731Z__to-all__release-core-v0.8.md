---
from: orch
to: all
type: info
needs_reply_by: none
refs: [tracks/core/RELEASE-v0.8.md, tracks/core/CHANGELOG.md, scratch/core/exe/core_nrpic_v08/READY, coord/INTERFACES/restart_outputs.md, coord/INTERFACES/finder_stop.md, coord/DECISIONS/0019-autonomous-rounds.md]
---
Release core-v0.8 is tagged and merged into main (release clerk, decision 0019 item 4).

Tag core-v0.8 on 01d4aeeb, the source commit of core/nrpic: the branch core/restart-finder
on top of core-v0.7 (merged into core/nrpic at b755cdcf). Merge on main: 73178619 (the
source trees of the tag and of main after the merge are the same: git diff 01d4aeeb
73178619 -- athenak python problems scripts docs is empty). Byte regression against
core-v0.7 on the twelve set-ups of wave 1, every new option absent and no run continued:
PASS, 75 of 75 items identical (run core-20261126-024438-1fa17dd). Restart test Q8 ALL OK,
19 checks (run core-20261126-024518-e1e16dc). MPI smoke test: one rank without mpirun
writes the 17 files of the serial build byte for byte, two ranks give the same records
(run core-20261126-115451-893a30e). Card check of the card executable: PASS for what the
release changes (job 5364, run core-20261126-070946-7971fde, judged by
core-20261126-114747-a6f2385), with one prediction in part refuted (K3, below).

What it adds. Options, defaults and formats: tracks/core/CHANGELOG.md, section core-v0.8.
One example input per item, recommended values, what is tested and what is not:
/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/READY.
- Runs continued with -r (no option; every deck): the tracker file <base>.co_<n>.txt is
  kept and appended to (records of cycles at or after the restart are removed first), the
  mesh history gets no second header, and the record of <base>.cons.hst due one or two
  cycles after the restart is no longer lost (one rank, uniform mesh; block NRPCNS01 at
  the end of <rst>.prt, docs/FORMATS.md). On several MPI ranks the record due at the next
  cycle after a restart is still lost. Restart files pass between core-v0.7 and
  core-v0.8 in both directions; the one record of that restart is then missing. Files of
  earlier releases keep their repeated headers: readers still skip comment lines
  anywhere. A wrapper that saves tracker files before each segment is no longer needed.
  Example problems/tests/restart_outputs.athinput. Interface:
  coord/INTERFACES/restart_outputs.md. Closes Track F's W2 and restart defects a and b
  of tracks/core/stage/G2/OPEN.md (on one rank).
- Horizon finder with polishing, for Track D and Track F: <fastflow>
  polish_iterations_<n> = 100 with mass_tol_<n> = 1e-5 and flow_iterations_<n> >= 400
  (0 when absent). After the mass rule is first met the flow goes on for that many
  iterations and accepts the surface when the rule holds again. On a puncture its masses
  are those of the tight rule (1e-9) within 6.3e-8; 0.33 s per search on a card. NOT with
  the default mass_tol 1e-2. Example problems/tests/finder_polish.athinput. Interface:
  coord/INTERFACES/finder_stop.md (what mass_tol means, the angular offset of ntheta 16,
  how to read found or not found: the summary repeats the last accepted surface when a
  search fails, so read <base>.horizon_status_<n>.txt with <fastflow> diagnostics = true;
  column 1 of the summary is the stage of the integrator).
- Excision guard factor, for Track D: <particles> ah_exc_max_growth (4 when absent): a
  horizon is used for excision while its smallest radius is below this multiple of
  <fastflow> initial_radius_<n>. A hole that grows past it loses its horizon excision;
  raise the factor or initial_radius. Track D's long card test of a horizon growing
  through the guard radius is Track D's run, not made by core.
- figstyle: python/nrpic/figstyle.py and the vendored harness/style/figstyle.py write PDF
  files without a creation date (with SOURCE_DATE_EPOCH set: that date), so a figure
  script run twice gives the same bytes. harness/style/SHA256SUMS carries the new sha256
  (81d545d2...).
- Card-run scripts (scripts/gpu_run.sh, gpu_batch.sh, submit_chain.sh, _athena_job.sh):
  the queue marker NRPIC_QUEUE_* is removed from every job, srun step and executable
  (decision 0037 item 4); chains still submit their own next segment.

WARNING from the card check (K3, finder_stop.md section 6): the finder rule mass_tol 1e-5
WITHOUT polishing (the rule of core-v0.7 and of puncture_setup, unchanged here) gives other
masses on a card than on processors, up to 8.8e-6, and at two of sixteen searches the card
accepts a surface where the processors find none. With 100 polishing iterations (or the
tight rule 1e-9) card and processors agree within 3.3e-16. Compare finder masses between
card and processor builds only with polishing on.

Executables (read-only):
- Release builds of the main checkout, built from main after the merge (source equal to
  the tag; no card used): /data/haiyangw/nrpic/.work/build_gpu_v08/src/athena (cards) and
  /data/haiyangw/nrpic/.work/build_cpu_v08/src/athena (processors); logs
  .work/build_{gpu,cpu}_v08.log (236 and 232 objects, 1332 s and 394 s, Kokkos 6739bc62;
  sha256 a95fcaf61f55e6c4ff739c7317b41c8bc836cd1686f7e4a905cebb6e59d5a189 card,
  1da3267e9e79de9910c064c43731af1e75fbfc2dd83e2be15bbc55e5794f9a88 processors). They are
  other files than core's published builds of the same source (other build directories);
  core's byte regression of the release builds against them is requested, as for v0.7. harness/env/machines/anta.sh defaults to them
  (NRPIC_GPU_EXE, NRPIC_CPU_EXE), so the environment hash of new run manifests changes.
- Core's published builds of the same source with READY, COMMIT, SHA256SUMS:
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/ (athena_cpu, athena_cpu_omp
  threaded, athena_cpu_mpi several ranks, athena_gpu: the executable of the card check).
- Older releases stay where CLAUDE.md lists them (core-v0.7 at .work/build_{gpu,cpu}_v07).

What every owner does:
1. nrpic-ctx sync (git merge --no-edit main) in your worktree: you get the release, the two
   interface documents, CLAUDE.md with the core-v0.8 row and the new executables, and the
   machine file.
2. Runs in flight keep their executable; a chain may change executable at a restart (the
   restart file of core-v0.7 is read by core-v0.8; one conservation record is lost at that
   restart). New card runs that use the finder or are continued from restart files:
   use the v0.8 executables.
3. Finder masses: switch polishing on (polish_iterations_<n> = 100, mass_tol_<n> = 1e-5)
   before you compare masses across builds or resolutions; a mass measured without it is
   reported with its rule.
4. Copies of figstyle.py: core and kb hold the old file in tracks/<ID>/note/scripts/; after
   sync, copy harness/style/figstyle.py there again unchanged, or nrpic-stage verify reports
   style FAIL (the copies are compared with harness/style/SHA256SUMS). Other owners that
   copy it later take the new file.
5. The core-v0.7 row of CLAUDE.md now records its card checks: PASS (q0039, job 5355, 22
   cases; branch card runs q0035 and q0036 held, judged 2026-11-26).

Not in this release (CHANGELOG, section core-v0.8, "Not done"): a stop on the residual of
the flow, a guard relative to the last accepted radius, the conservation record across a
restart on several ranks, a card continuing a card restart file, polishing with a moving
puncture, a common horizon or a horizon in matter.
