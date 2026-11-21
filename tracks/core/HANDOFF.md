# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21, batch 4a, session core-lead-6): release core-v0.6 is on main (tag on
984bde68) and closed except one card job. Its merged card executable PASSED the card check
(job 4800, prediction K6 held); the release processor build of main
(`.work/build_cpu_v06`) is byte-identical with the candidate (75 of 75). The G2 package of
core is brought to the state after core-v0.6: G2 is NOT met (`stage/G2/OPEN.md`, first
section). No source was changed in this session.
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.
Run next: `cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main && harness/bin/nrpic-run status core-20261121-154654-d3ec487`

ONE RUN IS PENDING: the release card build `.work/build_gpu_v06/src/athena` on the fifteen
cases of `analysis/release/card_v06.list`, run core-20261121-154654-d3ec487, Slurm job
4810 (0.1 card-hours asked; queued at 15:47Z). Prediction G6 is in the journal (entry of
2026-11-21T15:46Z). To close it (the worktree must be clean for `nrpic-run submit`): the
four commands in `tracks/core/RELEASE-v0.6.md`, section "Release builds against the
candidate"; look at the three figures (`fig_card_v06.png`, `fig_card_v05.png`,
`fig_card_pair.png`); write the outcome into that section (replace PENDING), into the
line `athena_gpu` of `scratch/core/exe/core_nrpic_v06/READY` (it says "queued as job
4810") and into the journal; commit, push. In `fig_card_v06.png` the dashed bounds run
across all cases although each applies to its own cases: g_smr1's constraint-statistics
bar (Hr_max, a ratio of rounding-level residuals, 8.8e-4 in job 4800) is bounded by
nothing.

Files to read first: `tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md`;
`tracks/core/stage/G2/OPEN.md` (first section: is G2 met, what is missing, defects p-t);
`tracks/core/interfaces/REQUESTS_WAVE3.md` section 5 (order of work for core-v0.7).

Decided in this session:
- core-v0.7 holds W24 (relaxed-lapse fix, first), W26 core/clump-table, W27 core/oblate;
  E's lockstep sub-steps (W25) go to core-v0.8 [maintainer's judgement; E's reply-by is
  2026-12-05].
- The release card check ran the whole fifteen-case list for the release build (46 s on
  a card), not one case.

G2 (CHECKLIST.md, 18 items): PASS C3, C4, C5, C8, C9, C10, C11, C13, C17, C18; FAIL C1,
C2, C6 (unless `VERIFY_RESULTS.md` says otherwise; see STAGE_REPORT.md), C7, C12, C14,
C15, C16. What closes it: ladder row 4 on M/8 against a collisionless control (Track C's
drift package shows M/4 pushes clusters outward), the oblate collapse after W27, a
coupled set-up converged three ways, a redrawn architecture schematic
(`verify/figscripts/schem_architecture.py`), a working note, a fresh-context verifier,
REVIEW.md/SCOPE.md in the stage directory.

W24, what is known (do not rediscover): `<z4c> lapse_leak` adds
`-(alpha/T) max(ln(alpha/alpha_0), 0)` to d_t alpha wherever alpha > alpha_0
(`athenak/src/z4c/z4c_gauge_ext.hpp` line 19), matter or not; Track D's V-1GB (vacuum,
faces +-384 M, M/8) grows its horizon mass by 1.27e-3 over 100-200 M against 5e-5 without
the option; inputs and runs in `git show track/D-bh-dress:tracks/D-bh-dress/g2runs/README.md`.

Executables (read-only): release core-v0.6 `.work/build_{gpu,cpu}_v06` (main checkout);
candidate `scratch/core/exe/core_nrpic_v06/` (four, READY with the card check);
`wt/core/.work/build_*_v06rc` build directories of the candidate.

Open with other owners:
- orch: outbox message of this session (gate status of core G2, release closed).
- Track D: G2 null tests without `lapse_leak` until W24 is released (decision 0022).
- Track C: its run (vi) (Slurm 4804, M/8 control to 1000 M) decides whether the M/8
  contraction turns; core's row-4 bisection on M/8 should read it first.
- Branches core/clump-table (tip ff11719d, holds core-v0.5 not v0.6) and core/oblate (tip
  4f01a81f, does not hold core-v0.5): both merge main before the next release.

Traps:
- `nrpic-ctx ack` commits by itself (inbox_acks.txt).
- `nrpic-stage verify` exports the committed tip and checks every run manifest; it writes
  VERIFY_RESULTS.{json,md} into the stage directory (commit them with the report).
- A full commit hash is copied from `git rev-parse`; exit status 3 of an AthenaK run is
  the guard's stop; `athena_cpu_omp` is not a byte reference; `runs/` in .gitignore hides
  `tracks/core/runs/` (a hand-written manifest needs `git add -f`).
- The clock: `date -u`. Temporary files of the lead: `scratch/core/tmp/lead_b4a/`.
