# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-27 18:30 PST, lead of batch 35): G0, G1 and G2 SIGNED (G1 and G2 with reservations;
coord/GATES.md). Toward G3 (60 card-hours): the scope `scope/SCOPE_G3.md` was reviewed independently
(`g3/scope_review/SCOPE_REVIEW.md`: do not queue as written) and is now amended by dated amendments A1-A5
(its section 11; the earlier text is kept). The first step allowed by the amended scope is queued: the
card timing runs of the finer mesh members (q0095) and the production base G-8 (q0100). Owner D-bh-dress,
branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress && squeue -u $USER`

Files to read first: `STATUS.md`; `scope/SCOPE_G3.md` section 11 (A1-A5) and the sections it replaces;
`g3/amend/JOURNAL.md` entries 1-5 (my check of the review, predictions for the queued runs and the amended
criteria); `g3/scope_review/SCOPE_REVIEW.md` sections 1 and 4; `stage/REVIEW-wave3.md` section 26.

## Card jobs in flight (check sacct for every job of a finished entry: the queue lists preempted jobs as done)

- q0085 EG8 (scouting, excguard), run D-20261127-233719-db5be88, chain; preempted four times (jobs 5536,
  5543, 5548, 5554), at 120 M of 260 M at 17:52 PST, next job 5560 pending. Output
  `scratch/D-bh-dress/D-20261127-233719-db5be88/` (base esflg8). When it ends: `harness/bin/nrpic-run finish
  D-20261127-233719-db5be88`, then judge E1-E8 of `excguard/JOURNAL.md` entry 1 with registered readers
  (`g2runs/tools/esf_criteria.py --base esflg8`, `g2long/tools/d4_timing.py`, an FK/ES-FL comparison, removal
  reasons from esflg8.removed.bin, the status file for every horizon number), figures looked at; outcome in
  excguard entry 3; post to core. G3 no longer depends on it (A1: FK's guard in every member).
- q0095 D-T12u16u (scouting, batch, one card job, cap 0.6): G-12u and G-16u to 2 M
  (`g3/amend/decks/timing.list`). Output under `scratch/D-bh-dress/<run_id>/t12u/` and `/t16u/`. Read
  against entry 3: fits a card, block counts 456, t = 0 found with masses 0.9990 +- 0.0007 and 0.99981 +-
  1e-4, seconds per M over G-8's in [2.7, 6.6] and [7.5, 21] (G-8's rate from EG8's segment logs). Then fix
  t_16 by A1 (G-16u capped at 20 card-hours) and write it as a dated note under A1 before G-16u is queued;
  t_16 < 200 M -> ask orch for a ruling first.
- q0100 D-G3-G8 (production, chain, cap 3.5): deck `g3/amend/decks/g3g8.athinput`, to 400 M. Read at its
  end with the amended Claim G criteria (needs the processor work below first for G3-G2's offsets).

## Processor work the amended scope puts before the later members (A5)

1. Claim D reader (A2): per-particle dtau_p = tau_p - tau_LTB(R_p; R0_p) on G2's snapshots (FK, FN4, FNQ,
   FL16 to 190 M), areal radius from the z4c slice at the snapshot time (ES-FL decks: slices every 10 M,
   snapshots every 25 M: use the 50 M multiples); D1* = twice FN4's largest |median dtau|. Prediction P-A2
   in g3/amend entry 4.
2. Polished re-searches of the restart files of V-1L4, V-1L, V-1L16 (vacuum offsets at 4, 8, 16 cells per M;
   A3), processors, at most 6 cores.
3. G3-G3 power on phase-randomised surrogates of FK - FL16 noise (50-190 M) at a signal of 1.2e-3 (A3; P-A3).
Then queue G-16u (to t_16), G-12u, G-8-4N, G-8-16N (data by flux_tools/esf_data.py at lattice h/2.52; smoke
test checks memory), G-8-e1 (shift_eta 1.0) in that order; two D chains at most at once.

## What this session did (batch 35)

- Checked SCOPE_REVIEW B1-B3 with my own tool (run D-20261128-020346-c4079e9): all three confirmed; S1 in part
  (16N costs 5.2 by the matched FK/FN4 pair, 7.6 by the review's pairing). Two predictions of mine failed
  (g12s alignment; C3 spread at 27-30 M).
- Amended SCOPE_G3 (A1-A5), predictions for the amended criteria (g3/amend entry 4), committed and pushed
  before any production entry. Decks and S-G8 smoke test (held). Queued q0095 and q0100.
- Outbox: orch g3-scope-amended-first-step; core g3-decks-memory-question. Acked core's
  restart-parameters-and-finder-check (no G3 deck uses deposit_comp_c).

## Traps (kept; new ones marked)

(1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES data:
puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball. (4) A non-finite run
exits 3 with `<base>.guard.txt`. (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time
is index 12; snapshots carry every particle's proper time after the species array. (7) The finder writes into
`-d`. (8) The finder summary repeats times across restarts: take the LAST record; with diagnostics read the
status file and drop searches not found. (9) Never kill by pattern; never remove files through a path built
from a shell variable. (10) `nrpic-ctx ack` renumbers the inbox: ack by file name. (12) Restart numbers are
not times. (13) `nrpic-run submit` refuses an unclean package: commit first. (16) Horizon excision stops once
the smallest horizon radius exceeds ah_exc_max_growth (4 when absent) x initial_radius_0; G3 uses 4 x 1.6.
(17) The unpolished finder sits up to ~6e-5 off the converged mass. (18) Removal records of preempted
segments: fluxio.drop_overlaps. (20) Judge each mesh against its own-mesh vacuum control. (21) Closes of
40-90 GB chains take 2-10 min. (25) FL16 and V-1L16 end at 299-299.75 M. (26) Close local background runs with
`nrpic-run finish` before reading them. (27) note/main.pdf is 1.1 MB. (28) A serial processor smoke test of an
M/8 ES-FL deck takes ~17 min for two cycles. (30) NEW: AthenaK aligns a refined region to the blocks of the
next coarser level and keeps one block of buffer per level: always count blocks with `athena -m` (g3/amend
tools/check_review.py) before trusting a hierarchy; t = 0 horizon mass of these data is 1 (Schwarzschild),
so the M/8 finder offset is -8.5e-3, M/16 -1.9e-4. (31) NEW: use `date` for journal times (this session first
wrote times 15-30 minutes ahead and corrected them to the commit times).
