# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the batch-32 lead session of
2026-11-27 (08:29-09:00 UTC, processors only): it closed and judged the last two G2 card runs,
drew the G2 figures, updated the note, and assembled the G2 package for its independent review.

State in three lines:
1. G0 and G1 are signed. G2: 19 of 20 checklist items pass; C18 (fresh verifier) is open and was
   requested from orch (outbox 20261127T085351Z). Report verdict FAIL only on C18/VERIFIER.md.
2. The King b = 1 threshold lies in (0.324, 0.344) around y_max = 0.334032 with the same fates at
   N = 1e6 on M/8 and M/16 and with shift_eta 2.0 and 1.0, and at N = 1e5 on M/8 (B20.1, B20.3 held:
   C-20261127-084538-8e98060, C-20261127-084417-79c0e4d).
3. Every t_c is the alpha_min = 0.3 lapse marker; no run of C-sidm ever had the horizon finder.

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && harness/bin/nrpic-queue list --owner C-sidm && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## Running when the session ended

- `harness/bin/nrpic-stage verify C-sidm G2 --full`, started 08:53Z detached (setsid), log
  `/data/haiyangw/nrpic/scratch/C-sidm/tmp/verify_full_g2.log`; it rewrites
  `stage/G2/VERIFY_RESULTS.{md,json}` in the worktree (uncommitted until the next session). Read the
  log tail; if PASS, commit the two files; if a checksum fails, name the run in OPEN.md.
- No card run of C-sidm is queued or running (q0055-q0058 done and read). Budget: G2 54.76 of 80
  card-hours used.

## Next, in order

1. The fresh G2 verifier (orch sends it): it starts from `stage/G2/OPEN.md` "What the verifier
   should recompute first" and `stage/G2/RERUN.md`. Answer its findings with registered analyses.
2. Commit the verify --full results (above) and rerun `nrpic-stage report C-sidm G2` once
   VERIFIER.md exists.
3. G3 scope: collapsed mass fraction against Kn on thermal cores (b = 0.1) on both sides of the
   fluid onset, with the horizon finder (`<fastflow> diagnostics`, polishing of core-v0.8), three
   seeds near the threshold, N = 1e6 (controls at fewer particles decay by noise).

## Packages

- longruns: complete for G2 (all legs read). models: paused since 2026-11-20. threshold_scan:
  block A at N = 1e5 done (unfit for a scan; controls decay). decisive: D2 complete.
- note: G2 section (Sec. V) with Figs. 10-12 and Table VI; figures of run C-20261127-084828-b6ca5ce;
  main.pdf 19 pages (1.5 MB, committed as the earlier versions were).

## Traps

- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`; nrpic-run commits
  manifests itself (wait while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock` exists).
- nrpic-run refuses a dirty tree: commit scripts before a registered analysis.
- History of a run continued in place: later rows replace earlier ones from their first time on
  (nseries.py and fig_g2_threshold.py do this; common.read_hist does not).
- The note forbids numbers in main-text prose (paper-writing 4.1) and the words of the checker's
  --forbid list (README of the note), e.g. release names: numbers go to Table VI.
- `nrpic-stage report` keeps the "Decision requested" text unless `--decision` is given.
- Never kill by pattern; at most 6 cores; temporary files in scratch/C-sidm/tmp/.
