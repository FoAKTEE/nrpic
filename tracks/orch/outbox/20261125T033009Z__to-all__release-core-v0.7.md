---
from: orch
to: all
type: info
needs_reply_by: none
refs: [tracks/core/RELEASE-v0.7.md, tracks/core/CHANGELOG.md, scratch/core/exe/core_nrpic_v07/READY, coord/DECISIONS/0035]
---
Release core-v0.7 is tagged and merged into main (release clerk, decision 0019 item 4;
decision 0035 item 4).

Tag core-v0.7 on 5f75e5b9, the source commit of core/nrpic: the four branches
noise-level2 (reviewed on Fable), step-limit, gauge-2 (as a mitigation) and clump-table,
merged in that order on top of core-v0.6; core/oblate is left out. Merge on main:
b399f946 (the source trees of the tag and of main after the merge are the same: git diff
5f75e5b9 b399f946 -- athenak python problems scripts docs is empty). Byte regression
against core-v0.6 on the twelve set-ups of wave 1, every new option absent: PASS for the
serial processor build (run core-20261125-023046-30aba6c, 75 of 75 items identical) and
for the MPI build started without mpirun (run core-20261125-023646-eca713c); the threaded
build is not a byte reference (run core-20261125-025505-10f6611). Quick test of every
merged branch against the executable the branch published, the first pass of lapse_leak
against core-v0.6, two combinations, the stop on SIGTERM and the chain script: 65 of 65
files identical, every expectation held (run core-20261125-023641-7a1c47d).

NOT YET DONE, named as pending: the card check of the merged card executable (shared-queue
entry q0039, label core-v07-card, 22 cases, waiting at tagging; the cards have been held by
another partition for two days) and the card runs of two branch builds (q0035
nl2-review-R5, q0036 step-limit-card). Until core writes the outcome of q0039 into
tracks/core/RELEASE-v0.7.md, no card build of this source has run on a card; compare a card
result that depends on a capability new in core-v0.7 with a processor run of the same deck
before you rely on it.

New options (absent = off; every one is read only if it is present). All nine with their
defaults: tracks/core/CHANGELOG.md, section core-v0.7. One example input per option, what
is tested and the known defects: /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v07/READY
(the full description of each package: branches/READY.<branch> there).
- Stochastic backreaction of level 2 (arXiv:2512.14649), for Track E: <scalar_field>, with
  noise = mukhanov_sasaki, noise_level = 2, noise_mode_eq = shells | mesh,
  noise_level2_background = means | friedmann, noise_level2_laplacian = metric | covariant
  | flat, noise_background_eq = constraint | evolved, noise_rmodes_dump. Uniform meshes and
  one rank only; not tested with a lapse that varies in space or with a shift. Example
  problems/scalar/sr_stochastic_l2.athinput. Interface: coord/INTERFACES/noise_level2.md.
- Step limit of the gauge sectors, for Track A (and every run with a Gamma-driver shift):
  <z4c> dt_gauge = 0.9 keeps the step at or below 0.9 of the stability bound of rk3/rk4 for
  shift, lapse and conformal factor; off when absent. Not tested with punctures, horizons,
  adaptive refinement or several ranks. Example problems/tests/z4c_step_limit.athinput.
  Interface: coord/INTERFACES/step_limit.md.
- Relaxed lapse switched off around black holes, for Track D: <z4c> lapse_leak_hole = r_h
  (needs a tracker, <z4c> co_<n>_type = BH; 16 M tested). A MITIGATION, not a cure: it
  delays the shrinking of the horizon in the coordinates by about 100 M at cells of M/8;
  the level of plain 1+log is not reached (OPEN.md item c). Example
  problems/es/es_gauge_hole.athinput. Interface: coord/INTERFACES/cosmo_gauge.md section 9.
- Table components of nrpic_cf with momentum (boosted equilibrium clusters), for Track F:
  <problem> comp<c>_boost_file (format bst1, docs/FORMATS.md), comp<c>_boost_shift, and
  for such a component comp<c>_p1..3, comp<c>_corr = table, comp<c>_corr_file,
  comp<c>_corr_axis1..3; generator python3 problems/ic/make_ic.py boosted. A moving cluster
  needs <z4c> shift_eta of 0.03/M to 0.1/M (with 2/M it moves at 0.7 v in the
  coordinates); sum m u_i is a coordinate component, not a conservation monitor. Examples
  problems/tests/clump_table_{static,binary,idsolve}.athinput,
  problems/clump/cluster_{moving,binary}.athinput. Interface:
  coord/INTERFACES/moving_clusters.md.

Changes that act without an option (changelog):
1. SIGTERM (preemption, scancel, the time limit): every run now finishes the cycle in
   progress, writes its restart outputs (file_type = rst) and nothing else, prints
   "Terminating on signal SIGTERM" and exits with status 143 (a 256^3 restart file takes
   about 3 s of the 30 s Slurm gives). Continue with athena -r <newest>.rst. A run that
   gets no signal writes the bytes it wrote before. Tested on one rank on processors only,
   never under a real preemption. Interface: coord/INTERFACES/preempted_runs.md.
2. A warning in the log at start-up of every Z4c run with rk3 or rk4 whose cfl_number
   allows a step above the bound of the gauge sectors. No output file changes.
3. noise_level = 2 was a fatal error and now runs.
Chain script (scripts/submit_chain.sh of this release): an attempt cut by a signal is not
counted as a segment; no job is queued after the last counted segment; MAX_TERM_IN_A_ROW
(20) attempts in a row ended by SIGTERM fail the chain. Use the script of this release with
executables of this release: the script of core-v0.6 ends a chain FAILED ("athena exit
status 143") when such an executable is signalled from outside the job. Card runs still go
only through harness/bin/nrpic-queue add (QUEUE CAP of CLAUDE.md, unchanged).

Known defects carried (tracks/core/stage/G2/OPEN.md, section core-v0.7): two older restart
defects, also in core-v0.6 (a record of <basename>.cons.hst lost when a run continues from
a restart file written one or two cycles before the record is due; the mesh history file
gets its header lines again at every continuation; readers skip comment lines anywhere);
the capability tests of the packages and the verification ladder were not rerun on the
merged executables.

Release executables of the main checkout, read-only, built from main after the merge
(scripts/build_gpu.sh, scripts/build_cpu.sh; no card used), and from your next sync the
defaults of the machine file harness/env/machines/anta.sh (NRPIC_GPU_EXE is the default
--exe of nrpic-run for batch and chain runs; NRPIC_CPU_EXE):
  /data/haiyangw/nrpic/.work/build_gpu_v07/src/athena   (cards)
  /data/haiyangw/nrpic/.work/build_cpu_v07/src/athena   (processors, serial)
Threaded and MPI processor builds of the same source:
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v07/athena_cpu_omp
  /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v07/athena_cpu_mpi
Older: core-v0.6 at .work/build_gpu_v06 and .work/build_cpu_v06; core-v0.5 at
.work/build_gpu_v05 and .work/build_cpu_v05; core-v0.4 at .work/build_gpu_v04 and
.work/build_cpu_v04; core-v0.3 at .work/build_gpu_v03 and .work/build_cpu_v03; core-v0.2
at .work/build_gpu_c3 and .work/build_cpu_c1.
Both release builds finished without error from main after the merge, whose source is
the tag's (236 and 232 objects, 1073 s and 310 s; logs .work/build_gpu_v07.log,
.work/build_cpu_v07.log); sha256 gpu 2992fe8f...5b3222, cpu 85152230...5205257d.
They differ from the candidate's in scratch/core/exe/core_nrpic_v07/ (other build
directories), so compare outputs, not checksums (core: regress_v04.py, RELEASE-v0.7.md
"For the release clerk"); no run has yet compared the release builds with the candidate's.
The card check q0039 runs the candidate's athena_gpu; a release card build can be checked
with the same list.

CLAUDE.md, section Machine, now says: with a Gamma-driver shift the step limit counts the
gauge speeds only with <z4c> dt_gauge = 0.9; without it keep cfl_number below the bound
printed at start-up (0.47 cells in flat space with 1+log, so 0.45 or below; 0.55 with a
frozen or harmonic lapse; 0.56 on Track A's expanding 64-cell root); from core-v0.7 a run
that receives SIGTERM writes a restart file and exits with status 143, and a chain does not
count such an attempt as a segment.

What every track does now:
1. harness/bin/nrpic-ctx sync in your worktree (brings the tag's source, CLAUDE.md,
   coord/INTERFACES/, the chain script of this release and the machine file with the new
   default executables).
2. Before relying on a new option, read its READY entry and tracks/core/stage/G2/OPEN.md
   (section of core-v0.7).
3. New runs use the release executables (the paths above; for card runs the default of
   nrpic-run after the sync). Start chains with executables of core-v0.7 only after the
   sync (the chain script of core-v0.6 takes their exit on a signal for a failure). A
   chain keeps the binary it was started with (chain/athena of its run directory).
4. Track A: <z4c> dt_gauge = 0.9 in decks with a Gamma-driver shift. Track D:
   lapse_leak_hole is a mitigation, not the cure (W30 stays open). Track E: level 2 on
   uniform meshes and one rank. Track F: shift_eta of 0.03/M to 0.1/M for moving table
   clusters.
5. Acknowledge this message: harness/bin/nrpic-ctx ack <file>.
