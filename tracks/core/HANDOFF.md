# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State: wave 1 is integrated. core/nrpic holds the six source branches (rng, collisions,
scalar-field, id-extrinsic, multi-puncture, newton) and two fixes; the source of the
proposed tag core-v0.3 is 609a875. Regression and quick tests pass on processor and
card builds of that source. G2 is not passed: ladder rows 3 (prolate/oblate) and 4
(cluster threshold) are PARTIAL and no tag exists yet.
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.
Run next: `cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show`
(then plan the wave-2 runs of ladder rows 3-4 with the executables below).

Files to read first: `tracks/core/STATUS.md`; `tracks/core/stage/G2/OPEN.md` (what is
missing, numbered); `tracks/core/stage/G2/EVIDENCE.md` (every run id);
`tracks/core/CHANGELOG.md`; the lead entry of `tracks/core/JOURNAL.md` (2026-11-15T14:53Z),
which also points to the package journals `JOURNAL-{rng,coll,scalar,id,mp,newton}.md`,
`interfaces/JOURNAL.md`, `verify/JOURNAL.md`; `tracks/core/RISKS.md`.

Executables (read-only, built from a git archive of the source; sha256 in
`/data/haiyangw/nrpic/scratch/core/tmp/lead/exe_sha256.txt`):
- merged 609a875: `wt/core/.work/build_cpu_609a875/src/athena`, `wt/core/.work/build_gpu_609a875/src/athena`
- baseline (main source 74ed745): `wt/core/.work/build_cpu_base/src/athena`, `wt/core/.work/build_gpu_base/src/athena`
After a source change: snapshot with `git archive HEAD athenak | tar -x -C <dir>`, link
`athenak/kokkos` into it, and build with `ATHENAK_SRC=<dir>/athenak scripts/build_{cpu,gpu}.sh <builddir>`.

How to rerun the checks of this session (each prints a run id; outputs under scratch/core/):
- verify suite: `cd tracks/core/verify/regress && NRPIC_EXE_CPU=... python3 geodesic/run.py`,
  `NRPIC_EXE_GPU=... python3 submit_gpu.py --tests O F L`, then `<test>/judge.py <run_id>`
- byte regression: `python3 tracks/core/tools/regress_relativistic.py --exe-a BASE --exe-b NEW --cases geo,boris,dep,east,os,jeans,binary`;
  `python3 tracks/core/analysis/rng/runreg.py --purpose "..." -- python3 {repo}/tracks/core/analysis/rng/run_regression.py --base BASE --new NEW`
- nrpic_cf regression and combined curvature: `tracks/core/analysis/lead/cf_checks.py --base BASE --new NEW [--parts P5] [--card]` (through runreg.py)
- card job: `sbatch tracks/core/analysis/lead/gpu_regress_job.sh`

Decisions pending (outbox files `tracks/core/outbox/20261115T1510Z__*`):
- orch: tags core-v0.1 (7daed19), v0.2 (52c44eb), v0.3 (609a875) and merge into main;
  twelve interface documents; `.gitignore` `runs/` -> `/runs/`; docs/ ownership;
  CLAUDE.md "What exists" and the named executables.
- group with Track C: correction of the collision energy at the particles' metric.
- group with Tracks A, D: which lapse condition to try against the surface front.
- whether to apply the gather patch (`notes/rng_gather_experiment.diff`) with new baselines.
Inbox: about twenty messages to core from A, B, C, E and kb are not answered one by one
(`harness/bin/nrpic-ctx inbox --show`); the 20261115T1510Z messages answer parts of
A, B, C, E. Answer the rest at the start of wave 2.

Traps:
- `runs/` in .gitignore also hides `tracks/core/runs/`: add manifests with `git add -f`
  (harness/RULES.md). Helpers forget it: the rng, scalar and id helpers left 39 manifests
  untracked in their worktrees (copied in this session).
- Byte regressions: mesh restart headers carry 36 never-set bytes; compare with
  `tracks/core/analysis/id/regress_format1.py` (masks them). On a card, runs with particle
  deposit are not reproducible run to run: compare at the start only (`--start-only`) or
  against the baseline's own scatter.
- `.bin` dumps are single precision: no identity better than float32 rounding can be
  read from them (P5 failed its first criterion for that reason).
- AthenaK accepts on the command line only parameters that the input file has.
- `tracks/core/analysis/id/test2_evolution.py` writes a json above 1 MB: commit the
  `.gz` only; its `--prefix t3` crashes on runs without particles.
- The verify suite names runs in local time (PST), runreg/run_registered in UTC.
- `scratch/core/` is shared by every core session: keep temporary files in a
  subdirectory of your own (`scratch/core/tmp/lead/` was this session's).
- This session's write guard refused `tracks/core/stage/G2/REPORT.md`; the report content
  is in EVIDENCE.md, OPEN.md, CHECKLIST.md, STAGE_REPORT.md and the journal.
