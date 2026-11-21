# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the lead of batch 4a,
wave 3, on 2026-11-21 from 15:45 to about 17:00 UTC.

State in three lines:
1. G0 is signed. For G1 every checklist item is met (note v1; VERIFIER.md checked and
   answered), and the independent review is requested from orch. The lead does not pass a
   gate.
2. G2 scouting. The outward drift of the M/4 collisionless controls comes from the mesh.
3. On M/8 the stable King control CC2 contracts steadily to 680 M (run (vi)), so block A of
   the threshold scan waits for drift run (v).

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Run next:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && squeue -u haiyangw -o '%i %j %T %M' && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`
Then, if a batch gives card time, submit drift run (v). The command is in
`drift/README.md` "Pending runs" (`--particles 10000`, 0.3 card-hours). Analyse it with
`compare.py --tag cc2_N` and `diffusion.py` against N.1-N.6 (`drift/JOURNAL.md` entries 5,
11, 14).

Packages still in progress (none has uncommitted files):
- drift. Runs (i), (iii) and (vi) are done and judged (entries 8, 12, 16). Run (v) was never
  submitted. Runs (ii) and (iv) are dropped. Card-hours: 2.25 of the 3.0 cap.
- models (paused 2026-11-20). Step 5 is left: reading the King runs (alpha_coll minus control,
  predictions K in `models/JOURNAL.md` entry 9). It is not needed for G1, since C2 is met.
- decisive: closed. D2 (collision cell size, 2-5 card-hours) has no decks yet.
- heat, verify_g1 and note v1: closed.

Card jobs of this owner: none queued or running at about 16:40 UTC. Run (vi), Slurm 4804,
ended at 16:30 UTC and was closed and analysed by this session.

Files to read first:
- `STATUS.md`
- `stage/REVIEW-wave3.md` sections 9-12
- `stage/G1/OPEN.md` and `CHECKLIST.md`
- `collide/TESTS.md` section 2c
- `drift/JOURNAL.md` entry 16
- `drift/README.md`
- `threshold_scan/SCAN.md` block A
- `JOURNAL.md` last three entries

Key numbers, with their runs:
- T7 at theta 0.003: kappa/kappa_1 = 1.019 +- 0.004 (C-20261119-161930-acd257b) and
  1.0250 +- 0.0025 with the card seeds (C-20261120-223203-b38a7d7).
- King threshold y0 = 0.334032; Juttner onset 0.32143 (C-20261119-151502-cb831a8).
- M/8 over M/4 excursion: CC1 0.138, CC2 0.099 (C-20261121-155049-ecf8893).
- Energy diffusion D: 3.8-4.0e-8 per M on M/4 and 5.8-6.5e-8 on M/8, ratio 1.5-1.7 (same run).
- CC2 on M/8, alpha_c - alpha_c(0): -0.0043 at 300 M, -0.0118 at 400 M, -0.0151 at 500 M,
  -0.0186 at 600 M, -0.0216 at 640-680 M; r50 -6.3 percent (C-20261121-163109-c8fff37).
- Collapse time t_c of CC1 at Kn = 10: sd 3.40 M over three cell seeds
  (C-20261121-075202-1a37fb9).

Decisions pending:
- orch: the G1 review (outbox gate-status-batch4a) and the next batch (outbox
  next-batch-drift-close: run (v), then decisive D2).
- core: the ADM-energy diagnostic and format findings F1-F3 are deferred; collisions on
  several ranks are accepted with no date.
- kb: conductivity and DSMC sources (received; waits for the kb package claims_tracks).

Lead decisions of this session:
- TESTS 2c names the T4 window, the T6(b) temperature (0.015) and the T9 KS temperature
  (final energy). All three were named after the data, and the strict T9 reading stays failed
  on record.
- Block A does not start on M/8 at N = 1e5 before run (v). Every fate is read against a
  control of the same mesh, seed, N and length.
- Lead sessions submit no card job unless their task names card-hours.

Traps:
- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`. Wait while
  `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock` exists.
- `nrpic-run submit --package <dir>` refuses uncommitted edits inside the package, so
  commit first.
- A restarted run writes its `cc.nrpic.hst` without a header line. Use
  `drift/scripts/controls.py` join_hst, or `rv_batch4a.py` read_any.
- `nrpic-stage verify C-sidm G1` checksums the large run outputs and runs for 40 minutes or
  more. Start it in the background. It checks cleanliness at its start on a snapshot of
  HEAD, so later edits do not affect it.
- Card runs with deposition are not byte-reproducible. Compare collapse times with a seed
  scatter, and read collisional effects against a control of the same mesh and seed.
- A continuation needs the executable that wrote its restart (core-v0.3 card build, sha256
  f9f2dc12...).
- Collisions stop on more than one MPI rank. Never kill by pattern. Use at most 6 cores per
  session.
