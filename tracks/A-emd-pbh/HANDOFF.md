# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 40 (wave 3), 2026-11-28 ~00:35 PST.

State in three lines: G0 and G1 are signed. Gate G2 was NOT PASSED (decision 0047); the second review is limited to
conditions (a)-(d), whose state is in stage/G2/OPEN.md. (b) is met; (d) was measured and NOT met (bound 0.51 at
detection); (a) needs a ruling (the face part cannot converge) and the retest RT2a is queued; (c) is on the cards.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list | grep A-emd; harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `threshold_ball/JOURNAL.md` entries 19 and 20 (FC, RT2a);
`periodic_threshold/JOURNAL.md` from "2026-11-27 23:45 PST" (S1L-F outcome, RX); `stage/REVIEW-wave3.md` section 15;
`coord/DECISIONS/0047-track-a-g2-not-passed.md`.

## Card runs of A (shared queue, priority 2)

| queue id | label | run | what it is | read with | prediction |
|---|---|---|---|---|---|
| q0089 | a-s1l-quarter | A-20261128-011607-3e2d530 (chain; job 5633 pending at 00:00; t = 133 of 410 done) | S1L at mu = 0.075, deck peak_leak, release v0.8 card build, cap 2.6 | `a2_invariant.py --run <dir> --reference 34.8 --band 32.0 35.5 --label S1L-q`, `a2_crossing.py`, `a2_probe_check.py` (as for S1L-h, periodic_threshold JOURNAL 2026-11-26 13:36) | A2Q (2026-11-27 16:39 PST): crossing bracket inside [32.0, 35.5] t_H |
| q0108 | a-rt2a-A | (registered at dispatch) | bracket member d0.42 on mesh A, deck threshold_ball/decks/nest16_L32_fr (faces at 32 + core-v0.6 face set + region norms), core-v0.9 card build, to t = 51, cap 0.5 | `threshold_ball/scripts/analyse.py` (detection rule, ratio outside the finder radius), `ratio_split.py --xmax 32 --edges 4.25,6.5,13`, `ball.region.hst` (outside 4.25, outside 13, outside the horizon) | R1-R3 of threshold_ball entry 20 (A may stop at the guard ~48 as before: read it at B's detection time) |
| q0109 | a-rt2a-B | (registered at dispatch) | the same on mesh B (nest32_L32_fr), cap 1.2 | as q0108 | R1: detection within 0.5 of 45.875; R2: ratio at detection in (0.1, 0.5); R3: matter part falls A -> B by >= 1.5, part 13-32 does not |

Close each with `harness/bin/nrpic-run finish <run_id>` before reading; check its jobs completed
(`nrpic-queue status`, `nrpic-queue audit --owner A-emd-pbh`). A chain continues itself; a chain cut between segments
is continued with its wrapper (`threshold_ball/scripts/continue_chain.sh <run_id> <max_segments>` via `nrpic-queue add
--cmd`). The dispatcher submits from this worktree: keep it committed (a dirty worktree makes its submit fail).

## Processor runs

None running at hand-off. RX (A-20261128-074500-daf8285) and its reader: see periodic_threshold JOURNAL.

## What batch 40 established (0 card-hours ran; 1.063 closed with q0090; 1.7 newly capped)

- (d) S1L-F (A-20261128-012211-c9cedc1; reader A-20261128-073831-fce5805, fig_s1l_finder.png): horizon found from
  t = 169.28, ratio outside it 0.514 at detection: NOT met. F1 (window, stall) and F3 refuted, F2 held.
- (a) FC (A-20261128-073120-9feebf2; reader A-20261128-080645-b3c9c7c, fig_face_conv.png): the outer-face part does
  not converge, with or without the face set (set lowers it ~100x). RT2a decks smoke-tested on the v0.9 processor
  build (A-20261128-075804-b2908e4) and queued.
- S1L's v0.6 chain departs from S1L-F at its restart point t = 50 (~1e-3 in alpha_min): RX tests restart exactness.

## Next, in order

1. Read q0108/q0109 (RT2a) and q0089 (A2Q) when they end; outcomes in the package journals; OPEN.md rows (a), (c).
2. (d): name the cause of the box violation - region ratios of P0L (four levels) against P0L6 (six levels) at equal
   times (existing region.hst files; processors), prediction first; then decide the next card member for (d).
3. (a): after orch's ruling on what the bound covers (outbox b40), either faces farther out / a coarser outer level,
   or the matter-part reading; the top-hat matter part (0.05-0.33) needs a smooth-profile bracket (its own scan).

## Packages

| Package | State | What remains |
|---|---|---|
| `periodic_threshold/` | S1L-F judged; RX run; q0089 pending | A2Q reading; box violation cause |
| `threshold_ball/` | entries 19 (FC) and 20 (RT2a predictions) | RT2a reading |
| `conv_ball/` | unchanged | turnaround columns and A-R1.35 unchecked by any verifier |
| `note/`, `szekeres/` | unchanged this batch | new results of the next review |

## Traps

- A whole-line section-3 ratio to an outflow face never converges (FC); always split it by region (ratio_split.py,
  face_conv.py) and say which part a number is.
- History files of chains continued from earlier restart files hold repeated time ranges: resolve them (later rows
  win; f_read.py's `load`) before comparing two runs.
- `nrpic.hst` momentum sums are round-off (|x| < 1e-12): compare them by absolute difference, not relative.
- Box decks: `flow = shear`; found or not found is ONLY in `<base>.horizon_status_<n>.txt`. GR particle files carry
  psi^6 in the masses. At most 6 cores per session (the box deck runs ~60-80 s per cycle on one core).
