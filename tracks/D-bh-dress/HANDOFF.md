# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-27 16:05 PST, lead of batch 34): G0, G1 and G2 SIGNED (G1 and G2 with reservations;
coord/GATES.md; G2 by decision 0045 on 2026-11-26). Toward G3 (60 card-hours allotted): the scope text
`scope/SCOPE_G3.md` is written and committed BEFORE any production run and waits for its independent
review (decision 0045 item 2; outbox `20261127T234818Z__to-orch__g3-scope-ready-for-review.md`). Queue NO
production run until that review is answered. The only card job of this owner: the excision-guard test
EG8 (scouting). Owner D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress && squeue -u $USER`
  then look for the scope review (orchestrator's agent; likely `scope/SCOPE_G3_REVIEW.md` or a decision).

Files to read first: `STATUS.md`; `scope/SCOPE_G3.md` (all of it); `excguard/JOURNAL.md` entries 1-2;
`stage/REVIEW-wave3.md` section 25; `stage/G2/GATE_REVIEW.md` section 5 (the reservations that are G3's
conditions); `coord/INTERFACES/finder_stop.md` (polishing, status file, guard).

## Card job in flight

- EG8 = ES-FL with the guard of core-v0.8: queue entry q0085 (label D-EG8, priority 2), run
  D-20261127-233719-db5be88, job 5536 (pending at 15:48 PST), chain, cap 2.5 card-hours, executable
  `.work/build_gpu_v08/src/athena`, input `excguard/inputs/esflg8.athinput`, output
  `scratch/D-bh-dress/D-20261127-233719-db5be88/` (basename esflg8, finder status file
  esflg8.horizon_status_0.txt). When it ends: `harness/bin/nrpic-run finish D-20261127-233719-db5be88`,
  then judge E1-E8 of excguard entry 1 with registered readers: `g2runs/tools/esf_criteria.py --base esflg8`
  (control V-1L summary, as for FK), `g2long/tools/d4_timing.py` (split 219), `g2long/tools/fk_compare.py`
  or an equivalent comparison against FK D-20261123-022725-a553496 and ES-FL D-20261121-203150-15f2bad,
  the removal reasons from esflg8.removed.bin (fluxio), the status file for every horizon number; figures
  looked at; outcome in excguard entry 3, post it to core (core asked; outbox excguard-eg8-queued).
- If EG8 is cut by preemption: the chain resubmits itself; if it ends FAILED, continue it with
  `g2long/tools/continue_chain.sh`-style wrapper through `nrpic-queue add --cmd` (harness/RULES.md).

## After the scope review

Answer each finding as a dated amendment below SCOPE_G3's text (never rewrite a criterion after a run was
read). Then, in the order of SCOPE_G3 section 10: processor smoke tests of new decks with block counts and
cost (G-12: root 144 cells; G-16: level 8 over +-5.9 M; G-8-16N: data by flux_tools/esf_data.py at lattice
h/2.52), check FL16's block list against its horizon radius (risk R29), then queue G-8 and V-8 first.
Guard factor 10 (8 M) for the 400 M members if EG8's E1 holds; otherwise initial_radius_0 = 1.6 (FK).

## What this session did (batch 34)

- G2's eight corrections of wording applied (REVIEW-wave3 section 25); note v3.1 (build
  D-20261127-234333-5720e3c, checker clean); ladder schematic D-20261127-234652-5b9af43; stage G2 collect,
  verify, report rerun (STAGE_REPORT.md).
- G3 scope written; EG8 designed, predicted, smoke-tested (S1 D-20261127-232517-6111945 held), queued.

## Traps (kept; new ones marked)

(1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES data:
puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball. (4) A non-finite run
exits 3 with `<base>.guard.txt`. (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time
is index 12. (7) The finder writes into `-d`. (8) The finder summary repeats times across restarts: take the LAST
record (fluxio.read_horizon does); with diagnostics, read the status file and drop searches not found.
(9) Never kill by pattern; never remove files through a path built from a shell variable. (10) `nrpic-ctx ack`
renumbers the inbox: ack by file name. (12) Restart numbers are not times. (13) `nrpic-run submit` refuses an
unclean package: commit first. (16) Horizon excision stops once the smallest horizon radius exceeds
ah_exc_max_growth (4 when absent) x initial_radius_0. (17) The unpolished finder sits up to ~6e-5 off the
converged mass; compare masses across builds only with polishing. (18) Removal records of preempted segments:
fluxio.drop_overlaps. (20) Judge each mesh against its own-mesh vacuum control. (21) Closes of 40-90 GB chains
take 2-10 min each. (25) FL16 and V-1L16 end at 299-299.75 M. (26) Background local runs must be closed with
`nrpic-run finish <id>` before note/scripts read them. (27) note/main.pdf is 1.1 MB (above the 1 MB guideline;
pre-commit allows 5 MB). (28) NEW: a serial processor smoke test of the ES-FL decks takes ~20 min for two cycles
(157 s set-up, ~9 min per cycle with the finder). (29) NEW: G2's M/16 decks refine only +-3 M at M/16 (horizon
leaves near 200 M); G3 decks must cover +-6 M at the finest level.
