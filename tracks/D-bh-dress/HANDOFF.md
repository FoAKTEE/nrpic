# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-25 08:30 PST, lead of batch 20): G0 and G1 signed (G1 with reservations, coord/GATES.md).
G2 in scouting, package NOT complete (stage/G2/OPEN.md section 1). This session (processors only, no card)
rechecked every G2 horizon number (decision 0040 item 3), read FN4/FNQ's region norms, split D4 at 219 M,
wrote the rerun script (C6) and stated the null test's mesh leg with two members and no order (ruling 0039
item 4). Owner D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress && squeue -u $USER -o '%i %j %T %r' |
  grep ' D-'; harness/bin/nrpic-run status | grep -E '\?|\*'`

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 23-24 (this session), 18-22 (batch 17), 10
(N1-N4, Q1-Q3, L1-L5), 12 (XN), 15 (XQ, L5); `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` sections 21-22.

## Card runs (release core-v0.6 card executable, plain 1+log, faces +-768 M)

S = /data/haiyangw/nrpic/scratch/D-bh-dress; run directory = $S/<run id>.

| Run | Run id | Queue | State (08:30 PST) | Read by |
|---|---|---|---|---|
| FNQ ES-FLKQ (N/4) | D-20261124-172725-2f426b6 | q0010 submitted | chain at 353 M of 400; next job 5293 pending (cards held) | Q1-Q3, XQ (entries 10, 15); np_partial.py, region_norms.py (`--running FNQ` until it ends) |
| FL16 ES-FL16 (growth M/16) | D-20261124-172745-72472ed | q0011 waiting (prio 1 eff.) | never ran | L1-L5 (L3 with Delta M from 20 M); esf_criteria with control V-1L16 |

- Both are continued in place by `g2long/tools/continue_chain.sh` through the queue. If a chain ends "FAILED
  (MAX_SEGMENTS reached)" before tlim: `harness/bin/nrpic-queue add --label D-FNQ-2 --priority 2 --cmd
  'tracks/D-bh-dress/g2long/tools/continue_chain.sh <run id> [new max_segments]'` (dry run first).
- Close each with `harness/bin/nrpic-run finish <run id>` (main accepts `continuations` since 2026-11-25;
  `g2long/tools/close_by_hand.py` is the fallback); start closes in the background, one at a time (40 GB).
- After FNQ ends: rerun `region_norms.py` without `--running`, np_partial, esf_criteria (Q1-Q3), xc_plane (XQ),
  and `hz_check.py` on its summary.
- No queue entry was added or removed this session.

## Next card work (not queued; first when the cards free)

Core's long test of the excision guard (core/restart-finder message, 2026-11-25): ES-FL with `<particles>
ah_exc_max_growth = 8` to 240 M, removals past 219.5 M, with `<fastflow> diagnostics = true`. Only with the
executable of `scratch/core/exe/core_restart-finder/` AFTER core has judged its card check q0049; predictions
first (compare with FK, D4 per bin as in d4_timing.py); post the outcome to core.

## What G2 still lacks (stage/G2/OPEN.md)

C1 G2 verifier; C2 FNQ, FL16; C3 XQ, L5; C5 report; C10 particle and mesh convergence figures (need FNQ,
FL16); C13 closes with the package; C14-C16 note v3 and schematics; C17 fresh-context verifier. Done in
batch 20: C6 (rerun_g2.py), C11 (region_norms.png), horizon recheck in C7/C8. The relaxed lapse is not
used in G2 (OPEN.md section 2).

## Traps (kept from earlier sessions; new ones marked)

(1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES data:
puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball. (4) A non-finite run
exits 3 with `<base>.guard.txt`. (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time
is index 12. (7) The finder writes into `-d`. (8) The finder summary repeats times across restarts: take the LAST
record (fluxio.read_horizon does). (9) Never kill by pattern; never remove files through a path built from a
shell variable. (10) `nrpic-ctx ack` renumbers the inbox: ack by file name. (12) Restart numbers are not times.
(13) `nrpic-run submit` refuses an unclean package: commit first. (16) Horizon excision stops once the smallest
horizon radius exceeds 4 x initial_radius_0 (nrpic.cpp:451-455). (17) The production finder sits up to ~6e-5
off the converged mass. (18) Removal records of preempted segments: fluxio.drop_overlaps. (20) The M/4 finder's
early surfaces fail (FF4 NaN to 3 M): read growth at M/4 from 20 M, judge each mesh against its own-mesh
vacuum control. (21) Closes of 40 GB chains take 10-25 min each. (22) NEW: no D run has a horizon status
file; a failed search shows as NaN or a bit-identical repeat of the line before (hz_check.py); column 1 of the
summary is the integrator stage, not the cycle. New inputs set `<fastflow> diagnostics = true`. (23) NEW:
status files end each line with "# reason": strip comments before parsing. (24) NEW: the region file's
`Hmax_in_h0` is NaN at t = 0 (empty horizon sphere).
