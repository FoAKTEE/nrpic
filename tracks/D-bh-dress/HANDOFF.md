# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21, end of the lead session of batch 4a): G0 signed (coord/GATES.md). G1: every item PASS
in the lead's judgement; the package `stage/G1/` is complete for the orchestrator's independent review
(decision 0016 item 4) and is NOT passed. G2 in scouting. Owner: D-bh-dress, branch `track/D-bh-dress`,
worktree `wt/D-bh-dress`. Two card jobs of D are queued (below); do not submit a third.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && squeue -u $USER && harness/bin/nrpic-run status | grep -E '\?|\*'` (a "?" is a run whose
  session was cut: check `scratch/D-bh-dress/<id>/.nrpic/result.json`, then `nrpic-run finish <id>`).

Files to read first: `STATUS.md`; `stage/REVIEW-wave3.md` sections 9-10 (this session; sections 1 and 3 hold
  a reading of ES-1G that section 9.1 withdraws); `stage/G1/STATUS.md`, `OPEN.md`; `g2runs/README.md` and
  `JOURNAL.md`; `secondary_infall/README.md` "Wave 3"; `JOURNAL.md` lead entries of 2026-11-21 15:47Z on.

What is established this round (run ids in REVIEW-wave3 section 9):
- D-pre-3 under decision 0021 item 2: Q16 (D-20261121-085652-7e189a2) follows the cell-centre shells within
  0.8 per cent to a/a_i = 16; profile within 16 per cent of the self-similar solution on lambda = 0.075-0.3
  (two references agree). P192 (run to a/a_i = 30) failed past a/a_i ~ 12 for a set-up reason (edge layer).
- lapse_leak makes the horizon mass grow late, with dust and in vacuum, not through the faces (ES-1GB,
  V-1GB). Decision 0022 item 3: the null test without lapse_leak until core-v0.7 fixes it.
- Note v1 (`note/main.pdf`, 18 pages) compiled and checked; it names ES-1G, ES-F, drift controls and the
  late Newtonian run only as pending work.

Card jobs queued (both chains under scripts/submit_chain.sh; read by package g2runs):
- Slurm 4805 = run D-20261121-125900-ea4c442, ES-1GB segment 2 (t = 188-200 M). When DONE:
  `tracks/D-bh-dress/g2runs/tools/finish_g2.sh es1gb` (closes the run, reruns compare_horizons and the slice
  mass); judge B1 at 199.5 M (already refuted at 188 M), B3, B5 in g2runs/JOURNAL.md.
- Slurm 4806 = run D-20261121-144631-aa7ce9b, ES-F (dust filling the bubble, 1+log, faces at +-192 M,
  release core-v0.4 card executable; 1.97 card-hours reserved). When DONE: `finish_g2.sh esf`, then judge
  P1-P7, (i)-(iii), D1-D4 as pre-registered in flux_tools/JOURNAL.md entry 7 (deviation of the executable:
  g2runs JOURNAL entry 3). If its chain needs a third segment (above ~1.3 card-hours more than planned),
  stop it with `scripts/submit_chain.sh --stop <rundir>`.

Packages still open (each writes only its own directory; helpers use `nrpic-run submit --package
tracks/D-bh-dress/<pkg>`):
- `drift_controls` (cut 2026-11-20): V-1B ran and is closed (D-20261120-222625-63abd72). Remains: its own
  judgement of Pb1-Pb5 (lead found Pb1, Pb2, Pb5 held; Pb3-Pb4, Theta at the hole and the radius rate, not
  computed), using `tools/compare_runs.py`, `count_blocks.py`, `slice_profiles.py` (UNTRACKED, untested,
  left as found; they make `nrpic-stage verify` fail "clean" until the package commits or drops them); the
  finder pre-flight outcome (its C1 refuted: 3.1e-8 against 1e-8); part B (slice profiles); the G2 cost
  table; README. Its question (cause of the late drift) is answered for vacuum (boundary) and for lapse_leak
  (gauge, g2runs); what remains is bookkeeping and Pb3-Pb4.
- `flux_tools`: ES-F is submitted (above); remains the judging (shared with g2runs' finish script), the V-0
  control and its README pointing to entry 6b.
- `note` v2 (not started): add ES-1G, ES-1GB/V-1GB, Q16, ES-F with run ids; journal data of the references
  from kb's message `tracks/kb/outbox/20261119T162127Z__to-D-bh-dress__spike-annotations-and-journal-data.md`;
  WRITING_GUIDE exception 1 now covers data keys of registered outputs (P14 hits).

Lead's plan for G2 (REVIEW-wave3 section 10): null test with 1+log and the faces at +-384 M: ES-1B (es_runs
  ES-1 input with the root level of drift_controls/inputs/v1b_bnd384.athinput) against V-1B (floor 4.8e-5),
  prediction first, ~0.9 card-hours; then the M/16 nest of the pair; lapse_leak runs only after core-v0.7.
  Card-hours: G2 1.56 used, 2.95 reserved, 25.49 left (`nrpic-run budget`).

Decisions pending: orch, the G1 gate review (outbox `g1-complete-for-review`) and closing `d-pre-3-criterion`
  in coord/REQUESTS.md; core, `lapse-leak-growth-data` and `newtonian-mode-edges` (this session) and the
  older open requests listed in STATUS.md `needs`.

Traps: (1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES
  data: puncture bare mass m_p = 1.0239688282062387. (3) psi = 1 outside the ES ball: read masses as
  Misner-Sharp or horizon masses. (4) A run that went non-finite ends "successfully" with zero particles on
  core-v0.3/v0.4 (core-v0.5 on: exit status 3 and `<base>.guard.txt`): check column 3 of `<base>.nrpic.hst`.
  (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time is index 12. (7) The finder
  writes its files into the working directory before core-v0.5 (into `-d` from v0.5): run AthenaK with its
  cwd in scratch. (8) The finder summary writes t = 0 twice; use unique times. (9) Never kill by pattern;
  never remove files through a path built from a shell variable. (10) `nrpic-ctx ack <n>` renumbers the
  inbox after each ack: ack by file name. (11) A processor re-search of a card dump differs from the card's
  finder by ~3e-8. (12) Q16/P192 snapshots fall near, not on, a/a_i = 4 and 12 (3.976, 12.020): compare
  with shells at the same a, not with tabulated values at round a. (13) `nrpic-run submit` refuses an
  unclean worktree: pass `--package <your directory>` while another package has untracked files.
