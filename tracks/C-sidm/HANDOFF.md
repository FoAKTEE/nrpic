# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the batch-27 lead session of
2026-11-26 (11:44-12:45 UTC, processors only): it closed eight ended card runs, judged them with
registered analyses, wrote the G2 section of the note and updated the G2 package.

State in three lines:
1. G0 and G1 are signed. G2 is open and NOT ready for a verifier: 7 of 20 items pass, none fails
   as written, 13 open; `stage/G2/OPEN.md` maps each open item to its queue entry.
2. The threshold is bracketed on M/8 at N = 1e6: 0.344 kin collapses at 252.31 M, 0.324 kin holds
   600 M (C-20261126-121836-c7a76c1); y_max = 0.334032 lies inside; same fates at N = 1e5; the
   0.344 member with shift_eta 1.0 collapses at 252.41 M (C-20261126-123219-f734997).
3. Every t_c is the alpha_min = 0.3 lapse marker; no run of C-sidm ever had the horizon finder.

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && harness/bin/nrpic-queue list --owner C-sidm && squeue -u $USER -o '%i %j %T %M' && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## First thing: A16b344

q0055 A16b344 (C-20261126-043714-8ea1c35, y0 0.344 kin, N = 1e6, M/16) ended at 600 M with all
particles excised (a collapse). This session started `nrpic-run finish` on it in the background
(log `scratch/C-sidm/tmp/finish_a16b344.log`, 80 GB to hash). Check
`python3 -c "import json;print(json.load(open('tracks/C-sidm/runs/C-20261126-043714-8ea1c35/manifest.json'))['status'])"`:
if it is not `completed`, run `harness/bin/nrpic-run finish C-20261126-043714-8ea1c35` (the cache
makes a second pass quick for files already hashed). Then read it, registered:
`harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 1 --purpose "..." -- env OMP_NUM_THREADS=1 python3 tracks/C-sidm/longruns/scripts/nseries.py --out '$NRPIC_RUN_DIR' --band 0.03 --control N1e6_b344kin --title "Mesh leg ..." N1e6_c=C-20261124-221122-928c9eb N1e6_b344kin=C-20261125-224959-d1d4494 N1e6_b344kin_M16=C-20261126-043714-8ea1c35`
and judge B20.2 (JOURNAL 2026-11-25T16:02Z: same fate as N6b344; t_c within 20 per cent of
252.31 M). Look at the figure before writing the outcome.

## Card runs: the shared queue (harness/RULES.md "Shared card queue")

| Queue id | Label | Item / run id | Read with | Prediction |
|---|---|---|---|---|
| q0055 | A16b344 | ENDED, closing (above) | nseries.py beside N6b344 | B20.2 |
| q0057 | A16b324 | C-20261126-121449-1d37e77, job 5382 pending | nseries.py beside N6b324 (`--control N1e6_b324kin`) | B20.1 |
| q0058 | N6b324e1 | waiting (priority 1(2)) | nseries.py beside N6b324 | B20.3 second half |

- Card runs reach Slurm only through `harness/bin/nrpic-queue add`; every C entry runs
  `tracks/C-sidm/longruns/seq/qitem.sh <item>`; the tree must be clean when an entry dispatches.
- Close a run before reading it: `harness/bin/nrpic-run finish <run_id>` (about 10 min per 70 GB;
  do not run two finishes on the same run at once).
- Decks stay on the core-v0.6 card build, cfl_number 0.25, no `dt_gauge` (ruling 0039 item 3).

## Next, in order

1. A16b344 (above), then q0057 and q0058 when they end: judge B20.1-B20.3; update CHECKLIST C1, C2,
   C7, C9 (pass only if the fates repeat on M/16 and with shift_eta 1.0) and the note's Sec. V.
2. G2 figures (C10, C11, C13, C15, C16): one script per figure in `note/scripts/` (convergence in
   N from nseries.json, mesh and gauge from d2.json and the bracket legs; verification-ladder
   schematic with paperfig.py; a slice mosaic needs mesh dumps of one run), a registered
   `run_all.py`, compile with the checker, read the pages.
3. Ask for the fresh G2 verifier (OPEN.md "What a G2 verifier must cover"); then
   `nrpic-stage collect/verify/report`, with one `verify --full` pass before the gate review.

## Packages still in progress (none has uncommitted files)

- longruns: the three legs above. models: paused since 2026-11-20. threshold_scan: block A done
  at N = 1e5 (unfit); seeds 2 and 3 controls (A334s2c+, A334s3c+) closed in this session, not
  read (not needed for the bracket). decisive: D2 complete (ctrl, f1, f2 two seeds, f4, M/16,
  shift_eta 1.0).

## Traps

- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`; nrpic-run commits
  manifests itself (wait while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock` exists).
- History of a run continued in place: later rows replace earlier ones from their first time on
  (all readers in longruns/scripts do this).
- nseries.py parses the particle number from the label prefix `N<m>e<k>`; keep it in every label.
- The note forbids numbers in main-text prose (paper-writing 4.1): numbers go to table VI.
- `nrpic-stage verify` without `--no-checksums` hashes several TB; run the full pass only in a
  session that waits for it, before the gate review.
- Never kill by pattern; at most 6 cores; temporary files in scratch/C-sidm/tmp/.
