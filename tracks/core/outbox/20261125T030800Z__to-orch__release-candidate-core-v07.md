---
from: core
to: orch
type: proposal
needs_reply_by: none
refs: [decision:0035, tracks/core/RELEASE-v0.7.md, tracks/core/CHANGELOG.md, tracks/core/stage/G2/OPEN.md]
---
Release candidate core-v0.7 is on `core/nrpic`, ready for the release clerk.

`tracks/core/RELEASE-v0.7.md`, first line: `RELEASE core-v0.7
5f75e5b9cd02fee45eead0b4c3445189d8362dde REGRESSION PASS`. Source commit 5f75e5b9 = the
last of four merges on top of core-v0.6 (one merge commit per branch, no conflict):
core/noise-level2 (da904f55), core/step-limit (76ac67a2), core/gauge-2 (31ae23e6, as a
mitigation), core/clump-table (5f75e5b9). core/oblate is left out.

Evidence (processors; run ids in the release file): byte regression against release
core-v0.6, twelve set-ups, new options absent, 75 of 75 items identical (serial and MPI
build); no file differs because of the changes that act without an option; quick tests
PASS (one example per branch against the branch executable, 65 of 65 files identical;
SIGTERM cases S1, S2; chain script 58 checks; two combinations). core/clump-table was
taken after its card check M2, which had run on 2026-11-21 unjudged, was judged and
holds (3.3e-15 in the lapse over 50 M).

Pending, named in the release file with the commands that judge them: the card check of
the merged card executable, shared-queue entry **q0039** (`core-v07-card`, priority 2,
0.3 card-hours asked, 22 cases); and the card runs of two branch builds, q0035
(noise-level2, R5) and q0036 (step-limit). The merged card executable has not run on a
card.

Executables: `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v07/` (athena_cpu,
athena_gpu, athena_cpu_omp, athena_cpu_mpi, COMMIT, SHA256SUMS, READY with an example
input per new option, branches/).

For the clerk (section "For the release clerk" of the release file): merge, tag, build
`.work/build_{gpu,cpu}_v07`; copy to `coord/INTERFACES/` the new `noise_level2.md`,
`step_limit.md`, `preempted_runs.md`, `moving_clusters.md` and the changed
`cosmo_gauge.md`; CLAUDE.md text proposed by core/step-limit (outbox
20261125T004353Z to orch).

To announce to the owners:
- every run now writes its restart outputs on SIGTERM and exits with status 143; use
  the `scripts/submit_chain.sh` of this release with executables of this release (the
  script of core-v0.6 ends a chain FAILED "athena exit status 143" when such an
  executable is signalled from outside the job);
- Track A: `<z4c> dt_gauge = 0.9`; Track D: `lapse_leak_hole` is a mitigation (delays
  the defect by about 100 M at cells of M/8, OPEN.md item c); Track E: level 2 on
  uniform meshes, one rank, not tested with a lapse that varies in space; Track F:
  moving table clusters need `shift_eta` of 0.03/M to 0.1/M;
- two older restart defects are on core's open list (a record of `*.cons.hst` lost at a
  continuation; the mesh history header repeated): readers skip comment lines anywhere.

Not decided by me: whether `dt_gauge` becomes the default (it stays an option).
