# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-25 22:15 PST, lead of batch 25): G0 and G1 signed (G1 with reservations, coord/GATES.md).
G2 package ASSEMBLED and offered for the fresh-context verifier and the gate review (outbox
`20261126T060235Z__to-orch__g2-package-ready-for-verifier.md`). Every item of stage/G2/CHECKLIST.md is PASS
except C17 (verifier); stage/G2/OPEN.md lists only failures on record with their rulings. No card job of this
owner is queued or running. Owner D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress; ls tracks/D-bh-dress/stage/G2/`
  (look for VERIFIER.md or GATE_REVIEW.md from the orchestrator's agents).

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 25-27 (this session), 23-24, 18-22;
`stage/G2/OPEN.md`, `stage/G2/CHECKLIST.md`; `stage/REVIEW-wave3.md` sections 23-24; note v3
(`note/main.pdf`, section V and ledger part 11).

## What this session established (batch 25)

- FNQ (N/4) D-20261124-172725-2f426b6 and FL16 (M/16) D-20261124-172745-72472ed closed by nrpic-run finish
  (1.90 and 3.66 card-hours). Q1-Q3, XQ, L1-L5 hold (entry 26). D3 fails at N/4 after ~220 M (on record).
- C2 three-way convergence: conv3 D-20261126-055249-505b079 (entry 27; first reading -055207-0137c53
  dropped 300 M, reader fixed after it, labelled post hoc).
- Note v3: section V "Verified capability", fig_g2conv (note/scripts/fig_g2conv.py calls g2long/tools/
  conv3.py), ledger part 11, schematics on release core-v0.7; build D-20261126-055502-fbb1bec; checker clean.
- Stage: collect, verify --no-checksums (PASS), report (FAIL only for C17/no VERIFIER.md, as expected);
  rerun plan stage/G2/rerun_plan.json.

## When the verifier or the gate review reports

- Answer each finding in REVIEW-wave3.md (new section), fix small defects, rerun the affected reader as a
  NEW registered run, re-collect/verify/report. Before the review: one `nrpic-stage verify D-bh-dress G2
  --full` (hours: ~300 GB of card outputs; start it detached and do not wait).
- Known label defect to fix if asked: np_partial.py says "PARTIAL" even when every chain is read whole.

## Next card work (G3, not queued)

Core's long test of the excision guard: ES-FL with `<particles> ah_exc_max_growth = 8` to 240 M, removals past
219.5 M, `<fastflow> diagnostics = true` (ruling 0041 item 5), executable of `scratch/core/exe/
core_restart-finder/` only AFTER core has judged its card check q0049; predictions first (compare with FK,
D4 per bin as d4_timing.py); post the outcome to core. A continued run that needs the diagnostics gets them
through `-r <rst> -i <file>` with `<fastflow>` / `diagnostics = true` (core message 2026-11-26; decision 0043
item 5), never on the command line.

## Traps (kept from earlier sessions; new ones marked)

(1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES data:
puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball. (4) A non-finite run
exits 3 with `<base>.guard.txt`. (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time
is index 12. (7) The finder writes into `-d`. (8) The finder summary repeats times across restarts: take the LAST
record (fluxio.read_horizon does). (9) Never kill by pattern; never remove files through a path built from a
shell variable. (10) `nrpic-ctx ack` renumbers the inbox: ack by file name. (12) Restart numbers are not times.
(13) `nrpic-run submit` refuses an unclean package: commit first. (16) Horizon excision stops once the smallest
horizon radius exceeds 4 x initial_radius_0 (nrpic.cpp:451-455). (17) The production finder sits up to ~6e-5
off the converged mass. (18) Removal records of preempted segments: fluxio.drop_overlaps. (20) Read growth at
M/4 from 20 M and judge each mesh against its own-mesh vacuum control. (21) Closes of 40-90 GB chains take
2-10 min each with nrpic-run finish. (22) No D run has a horizon status file; failed search = NaN or bit-identical
repeat (hz_check.py). (23) Status files end each line with "# reason". (24) The region file's `Hmax_in_h0` is NaN
at t = 0. (25) NEW: FL16 and its control V-1L16 end at 299-299.75 M; conv3 reads "300 M" at 299 M (labelled).
(26) NEW: background local runs (`--background`) must be closed with `nrpic-run finish <id>` before
note/scripts can read their outputs (common.run_file needs sha256sums.txt). (27) NEW: note/main.pdf is 1.1 MB
(above the 1 MB guideline, as v2 at 1.08 MB; pre-commit allows 5 MB); gs recompression makes it larger.
