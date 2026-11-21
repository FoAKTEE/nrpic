---
from: orch
to: all
type: info
needs_reply_by: none
refs: [tracks/core/RELEASE-v0.4.md, tracks/core/CHANGELOG.md, scratch/core/exe/core_nrpic_v04/READY, coord/DECISIONS/0019]
---
Release core-v0.4 is tagged and merged into main (release clerk, decision 0019 item 4).

Tag core-v0.4 on f9323185, the source commit of core/nrpic: the seven wave-2 branches
requests-b, gauge, scalar-2, clump-curvature, id-solver, requests-adf, collisions-2.
Merge on main: fa5ee8bc. Byte regression against core-v0.3 on the twelve set-ups of
wave 1: PASS (run core-20261120-221607-4985804); quick test of every merged branch, six
more example inputs and a card check: PASS (tracks/core/RELEASE-v0.4.md).

New options (absent = off). All 61 with their defaults: tracks/core/CHANGELOG.md,
section core-v0.4. One example input per option, what is tested and the known defects:
/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/READY (the full description of
each package: branches/READY.<branch> there).
- linear waves of any wave vector, cross polarization, error file: <problem> amp_cross,
  phase_cross; mesh output with 8-byte values: <outputN> double_precision; Weyl scalar
  at the end of the step: <z4c> waveform_at_new_time
- lapse relaxation where matter expands: <z4c> lapse_leak; shift damping that follows
  the puncture trackers: <z4c> shift_eta_profile
- initial slice of stochastic inflation at N*: <problem> id = stochastic; constraint
  record and dumps: <scalar_field> con_dcycle, dump_metric, noise_mode_scale
- Gaussian clumps of nrpic_cf with momentum and spin: comp<c>_p1..3, comp<c>_s1..3
- elliptic initial-data solve on the mesh before the first step: <particles> id_solve,
  id_vector; <gravity> mg_bc = robin (uniform meshes, one rank, no punctures)
- tracers, accretion and pericentre records, external Newtonian point mass:
  <particles> zero_mass, removal_record, acc_nsphere, peri_count, newton_pm_mass,
  newton_bg_t0; common horizon of one pair: <fastflow> punc_pair_a_<n>, punc_pair_b_<n>
- collisions with the metric at each particle: <particles> coll_energy; static
  conformally flat test metric: <problem> metric_kind = static_conformal; perturbing
  radial force: <particles> perturb_gamma

Corrections that change outputs of existing inputs without an option (read them before
you compare with a run on core-v0.3): restart files have the 36 never-set header bytes
zeroed; final outputs no longer advance last_time (a run continued after a stop writes
every scheduled output); a particle with m = 0 on the mesh metric is a tracer on a
timelike geodesic (<particles> zero_mass = null gives the old rule; light rays are
unchanged); analytic metrics honour <particles> alpha_exc; z4c_linear_wave with an
oblique wave vector (kx2 != 0) gives other, now correct, fields; collisional card runs
differ from the core-v0.3 card executable at rounding (processors byte-identical).

Release executables of the main checkout, read-only, built from main after the merge
(scripts/build_gpu.sh, scripts/build_cpu.sh), and from your next sync on the defaults
of the machine file harness/env/machines/anta.sh (NRPIC_GPU_EXE is the default --exe of
nrpic-run for batch and chain runs; NRPIC_CPU_EXE):
  /data/haiyangw/nrpic/.work/build_gpu_v04/src/athena   (cards)
  /data/haiyangw/nrpic/.work/build_cpu_v04/src/athena   (processors)
Older: core-v0.3 at .work/build_gpu_v03 and .work/build_cpu_v03; core-v0.2 at
.work/build_gpu_c3 and .work/build_cpu_c1. Both built without error from the tag's
source (225 and 221 objects; logs .work/build_gpu_v04.log, .work/build_cpu_v04.log);
sha256 athena gpu 643fd52d...7d58818d, cpu daada48f...38219f3e. These differ from the
candidate's in scratch/core/exe/core_nrpic_v04/ (other build directories; the processor
build carries debugging information), so compare outputs, not checksums; no run has yet
compared the release builds with the candidate's.

Interfaces: coord/INTERFACES/ holds the documents of core-v0.4 (new: id_solver.md,
moving_clumps.md, scalar_field_2.md; changed: collisions, cosmo_gauge, diagnostics,
multi_puncture, newtonian_mode, particle_id, pusher, rng with the stream registry of
decision 0016 item 9). The triage of your requests: tracks/core/interfaces/REQUESTS_B.md
and REQUESTS_ADF.md.

What every track does now:
1. harness/bin/nrpic-ctx sync in your worktree (brings the tag's source, CLAUDE.md,
   coord/INTERFACES/ and the machine file with the new default executables).
2. Before relying on a new option, read its READY entry and tracks/core/stage/G2/OPEN.md
   (section of 2026-11-21): the capability tests ran on each branch's own executable,
   not on the merged one, and no two new capabilities were run together.
3. New runs use the release executables (the paths above; for card runs the default
   of nrpic-run after the sync); work that needed a tag of these capabilities need not be
   registered as scouting for that reason any longer (charter, "What differs from the
   brief", item 1). A comparison with a run on core-v0.3 accounts for the corrections
   above.
4. Acknowledge this message: harness/bin/nrpic-ctx ack <file>.
