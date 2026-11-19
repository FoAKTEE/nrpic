# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) has a complete G0 package
(every item PASS or NA, verifier report present) and is working on G1. The slow-roll (SR)
case of arXiv:2512.14649 runs in this AthenaK with core's tested-branch executable
`core/scalar-2` (scouting) and passes A1-A3, A5-A7 up to 256^3; G1 is not met because the
owner's A4 fails in its strict form in P1's set-up (ruling asked of orch) and four G1 products
are missing (two schematics, the note's G1 sections, a G1 verifier).

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show

Then, depending on the answers:
- orch ruled on A4'/A5' (`outbox/20261119T151727Z__to-orch__a4-a5-rewording.md`): update
  `spec/scope/SCOPE.md` section 4/4b and `stage/G1/STATUS.md`, `CHECKLIST.md` item C6;
  `harness/bin/nrpic-stage collect E-stoch-inf G1`, `verify`, `report`.
- A verifier of the G1 material is to be run (request `20261119T151728Z__to-orch__g1-verifier`):
  give it `stage/G1/EVIDENCE.md`, not the conclusions.
- G1 products: updated `note/scripts/schem_architecture.py` (most "new" boxes now exist) and a
  data-flow schematic (paperfig.py), G1 sections of `note/main.tex` with one script per data
  figure under `note/scripts/` (data from the registered ladder runs), checker with
  `--compile`; then `nrpic-stage verify E-stoch-inf G1`.
- Review the wave-3a package `usr/` (USR case toward G2; its runs E-20261119-143905-f2bcde3,
  -144116-8aa7c22, -145835-67cde45; journal `usr/JOURNAL.md`), as this session reviewed the
  others (`stage/REVIEW-wave2.md`).

Files to read first: `STATUS.md`; `stage/G1/STATUS.md` (each G1 criterion, met or not);
`stage/G1/OPEN.md`; `stage/REVIEW-wave2.md`; `ladder/README.md` and `ladder/JOURNAL.md`
entries 1, 8-11; `spec/scope/SCOPE.md` sections 4, 4b, 8; `RISKS.md`; `JOURNAL.md` (last
entry).

Decisions pending: A4'/A5' (orch); a G1 verifier (orch); release of the scalar-2 set-up
(core, `outbox/20261119T151729Z__to-core__release-scalar2-sr-setup.md`).

Traps:
- The executables of the SR ladder are core's published branch executables
  `/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/athena_{cpu,gpu}` (a58e95b); the
  release core-v0.3 (`.work/build_*_v03`) has no `id = stochastic`, no constraint record and no
  NRSFDMP2 dump.
- Cold 128^3-256^3 dumps read through the ladder's numpy memory map crawl (3.6 MB/s against
  124 MB/s sequential): analyse right after the card job, or read sequentially
  (`stage/G1/scripts/lead_check.py` reads per variable with seek + fromfile). The full rerun
  E-20261119-145853-ef835c2 was stopped for this reason.
- Pairs of runs with different `tlim` compare different times at the last dump (t = 4.500
  against 4.504-4.516); the ladder's verdicts drop those dumps, `fig_a4_paper.png` still shows
  the spike.
- `nrpic-run` refuses a submit above 16 busy cores of the owner: the wave-3a `usr/` package
  shares this worktree and its runs count.
- Commit path-limited (`git commit -- <paths>`): other helpers (usr/) commit in this worktree
  at the same time; never commit their uncommitted files.
- The langevin scripts write into `langevin/results/` and `langevin/fig/` as well as the run
  directory; check `git status` after any langevin run.
- `$NRPIC_RUN_DIR` in a command: single quotes or inside `bash -c '...'` (RULES.md).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  context protocol 957-1004, M11 544-547.
