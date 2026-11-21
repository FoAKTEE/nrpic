# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21, end of the lead session of batch 2a): G0 signed (coord/GATES.md). G1 NOT met: C7 waits
on orch's ruling `d-pre-3-criterion` (asked a third time) or on the run to a/a_i = 30, C16 on the rebuilt
note; everything else of G1 is PASS (stage/G1/CHECKLIST.md). New result: the late horizon drift of the vacuum
control V-1 is the outer boundary (V-1B, faces at +-384 M: within 4.8e-5 over 100-200 M). ES-1G (lapse_leak)
slices the dust exactly but its horizon mass grows by 7e-3 with the exterior leaking through the +-192 M faces.
Owner: D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`. No card job queued or running.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-run status | grep '?'` (a "?" is a run whose session was cut: check
  `scratch/D-bh-dress/<id>/.nrpic/result.json`, then `nrpic-run finish <id>`).

Files to read first: `STATUS.md`; `stage/REVIEW-wave3.md` (sections 1-6 and 8); `stage/G1/STATUS.md`,
  `OPEN.md`, `VERIFIER.md`; `es_runs/README.md` ("ES-1G results", "Gauge for the null test with matter");
  `drift_controls/JOURNAL.md` entries 1-2; `flux_tools/JOURNAL.md` entry 7; `JOURNAL.md` (lead entries
  Z1-Z6 of 2026-11-21).

Packages cut on 2026-11-20 and still open (each writes only its own directory; helpers use
`nrpic-run submit --package tracks/D-bh-dress/<pkg>`):
- `drift_controls`: card run (b) V-1B ran and is closed (D-20261120-222625-63abd72); the lead's first reading
  (Pb1, Pb2, Pb5 held) is in REVIEW-wave3 section 3. Remains: the package's own judgement of Pb1-Pb5 with
  `tools/compare_runs.py` (uncommitted, with `count_blocks.py` and `slice_profiles.py`: untested tools of
  the cut session, left as found), Pb3-Pb4 (Theta at the hole, radius rate), outcome of the finder pre-flight
  D-20261120-222820-94f20b3 (its C1 is refuted as written: 3.1e-8 against 1e-8), part B (slice profiles),
  the G2 cost table, README. Card run (a) (finder from 150 M) is no longer needed for the cause.
- `flux_tools`: ES-F not submitted. Step 3 exactly as pre-registered (entry 7): `harness/bin/nrpic-run submit
  --kind scouting --gate G2 --launcher chain --gpu-hours 1.97 --package tracks/D-bh-dress/flux_tools --exe
  /data/haiyangw/nrpic/scratch/core/exe/core_requests-adf/athena_gpu --purpose 'ES-F: first matter run;
  predictions flux_tools JOURNAL entry 7' -- tracks/D-bh-dress/flux_tools/inputs/esf_dx8.athinput`.
  Then step 4 (finish_esf.sh, esf_analyse.py reading (iii) and D1-D4, synthetic tests), 5-6 (judging in
  entry 8, V-0 control, README pointing to entry 6b). Its faces are at +-192 M: the boundary effect is
  1e-4 against a predicted growth of 0.1-0.25 M, so it may run as registered.
- `secondary_infall`: shells to a/a_i = 30 (four force laws) and R8 (N128Lc rerun on the threaded build,
  D-20261120-222550-e472402) ran and are closed, not analysed (R8 prediction in its JOURNAL, last entry).
  The production run to a/a_i = 30 is not started: `nm_run.py` with the design of the JOURNAL entry of
  2026-11-20T22:25Z (nx 192, L 854, edge 1.1), threaded build, six cores, isolated box (processors, per
  core's correction of 2026-11-21), 0.4-0.8 h; prediction first. It decides C7 if orch keeps the wording.
- `note`: v1 text (c2e0571d) and every figure (runs D-20261120-222413-4a67fa2 ... -223535-24f7f90) are in;
  remains: P11 outcome, compile, `check_manuscript.py --compile` (P12), read every page, commit main.pdf,
  and the verifier's corrections (dress at a/a_i = 2: 0.5-3.3 per cent, within 1.1 from a/a_i = 3; profile
  "about 25 per cent, sensitive to r_ta"; Hernquist a = 0.8 gap in FdRW's curve [JUDGEMENT]; hole mass a
  choice, FdRW say M_BH >~ 4e6 Msun at kerrdm.tex:127; ledger: radius of "wall radius against the closed
  form", table residuals as upper bounds, the seeded self-similar model). Closes C16.

Lead's plan for G2 (REVIEW-wave3 section 8): every 200 M run with the faces at +-384 M (the V-1B mesh: one
  coarser root level, 400 MeshBlocks, ~0.78 card-hours in vacuum at M/8). Card order, one change each:
  ES-1GB (ES-1G with faces at +-384 M; does the 7e-3 growth go away?), V-1GB (its vacuum control), ES-F,
  then the M/16 nest. The tables have a Painleve-Gullstrand exterior (`exterior = pg`), so the larger box
  needs no new data. Release core-v0.4 (`.work/build_gpu_v04/src/athena`) has lapse_leak and the accretion
  diagnostics in one executable. Card-hours: 29.22 left toward G2; at most two D jobs in the queue.

Decisions pending: orch on `outbox/20261121T064131Z__to-orch__d-pre-3-criterion-third.md` and
  `...g1-numbers-errata-reminder.md`, and the waiver of three wave-2 runs (`...waive-three-wave2-runs.md`;
  stage/G1/VERIFY_RESULTS.md check "runs"); core on the four outbox messages of 2026-11-21 (boundary benchmark,
  ES-1G outcome and the shrinking hole, lapse-excision criterion, particle energy and crossing record) and
  the older open ones listed in STATUS.md `needs`.

Traps: (1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES
  data: puncture bare mass m_p = 1.0239688282062387. (3) psi = 1 outside the ES ball: read masses as
  Misner-Sharp or horizon masses. (4) A run that went non-finite ends "successfully" with zero particles:
  check column 3 of `<base>.nrpic.hst`. (5) Tracers carry m = 1e-30 (m = 0 is a null particle on core-v0.3;
  on core-v0.4 m = 0 is a timelike tracer unless `zero_mass = null`). (6) trajmet records have 17 doubles
  (docs/FORMATS.md still says 12); proper time is index 12. (7) The finder writes
  `<base>.horizon_summary_0.txt` into the working directory: run AthenaK with its cwd in scratch. (8) The
  finder summary writes t = 0 twice; use unique times. (9) Never kill by pattern; never remove files through
  a path built from a shell variable. (10) `nrpic-ctx ack <n>` renumbers the inbox after each ack: ack by
  file name. (11) A processor re-search of a card dump differs from the card's finder by ~3e-8.
