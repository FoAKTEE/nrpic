# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-22, end of the lead session of batch 10a): G0 and G1 signed (G1 with reservations,
coord/GATES.md). G2 in scouting: the long card runs of batch 5 are judged (g2long/JOURNAL.md entry 5):
criterion N (null test) and criterion G (growth against flux and the exact dust solution) both hold
at M/8 to 500 M; the convergence members, exterior constraints and the verifier are missing
(stage/G2/OPEN.md). Four follow-up chains are queued (entry 6, smoke tests entry 9). Owner D-bh-dress,
branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && squeue -u $USER -o '%i %j %T %r' | grep ' D-' && tail -5
  /data/haiyangw/nrpic/scratch/D-bh-dress/g2long_seq2/log && harness/bin/nrpic-run status | grep -E '\?|\*'`
  (a "?" is a run whose session was cut: check `scratch/D-bh-dress/<id>/.nrpic/result.json`, then
  `nrpic-run finish <id>`; a chain's state: `scripts/submit_chain.sh --status <rundir>`).
  `nrpic-run finish` of a long chain checksums ~35 GB of restart files: 5-7 min each; run them in the
  background and do not commit while one runs (it commits).

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 1 (criteria, predictions R1-R5), 5
(outcomes), 6 (follow-up predictions), 8 (constraints), 9 (smoke tests, release order);
`stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` sections 13-14.

## Card runs (all `nrpic-run` chains, release core-v0.6 card executable, plain 1+log, faces +-768 M)

S = /data/haiyangw/nrpic/scratch/D-bh-dress. Run directory = $S/<run id>.

| Run | Run id | Job | State | Reads it |
|---|---|---|---|---|
| R5 ES-1L16 (M/16, 300 M) | D-20261121-203151-59c54fb | 4920 (segment 4) | at 225.6 M, pending | H3 (and H4): rerun judge_long below; then finish |
| FV4 V-1L4 (M/4, 300 M) | D-20261123-022715-ab5d983 | 4933 | pending | P1-P4 (entry 6) |
| FK ES-FLK (initial_radius 1.6, 400 M) | D-20261123-022725-a553496 | 4934 | held, 1st in queue | P7-P11 |
| FE4 ES-1L4 (M/4, 300 M) | D-20261123-022726-1b133af | 4935 | held, 2nd | P5-P6 |
| FF4 ES-FL4 (M/4, 500 M) | D-20261123-022727-1c17e73 | 4936 | held, 3rd | P12-P14 |

- Sequencer: `$S/g2long_seq2/` (copy of `g2long/tools/sequencer.sh`, started with setsid nohup at 18:27
  PST; pid in `pid`, log `log`, queue `queue`, released `released`). It releases FK, FE4, FF4 whenever
  fewer than two D jobs are active, and exits when all are released. See: `ps -p $(cat $S/g2long_seq2/pid)`.
  Stop: `touch $S/g2long_seq2/STOP`. If it died with a job still held: `scontrol release <jobid>` by
  hand, at most two D jobs eligible. The batch-5 sequencer ($S/g2long_seq/) ended normally at 11:14.
- FV4 first: if its finder never finds the horizon after 20 M (P1 refuted: the t = 0 search already
  finds none at M/4, entry 9), cancel FE4 and FF4 (`scancel 4935 4936`, then `nrpic-run stop` or finish
  them as stopped) and say so in the journal; the third mesh member then has to be M/32 on +-3 M.
- Analyses (each registered: `nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1
  --package tracks/D-bh-dress/g2long --purpose "..." -- python3 ...`):
  `g2long/tools/judge_long.py --out '$NRPIC_RUN_DIR' V-1L=$S/D-20261121-203124-a34cf1f:v1l
  ES-1L=$S/D-20261121-203131-8ee2a49:es1l V-1B=$S/D-20261120-222625-63abd72:v1b ES-1=$S/D-20261115-172726-60ba4c2:es
  V-1L16=$S/D-20261121-203151-37e7b2d:v1l16 ES-1L16=$S/D-20261121-203151-59c54fb:es1l16` (add the M/4 pair as
  V-1L4=$S/<FV4>:v1l4 ES-1L4=$S/<FE4>:es1l4 once they exist; the tool plots them but judges only the names
  it knows: extend it for P2, P3, P5); for FK and FF4 `flux_tools/esf_analyse.py` and
  `g2runs/tools/esf_criteria.py --tau_max 650` with `--base esflk|esfl4 --data $S/D-20261121-203042-82deeec
  --control $S/D-20261121-203124-a34cf1f/v1l.horizon_summary_0.txt`; the removal reasons by time as in entry 5
  (fluxio.read_removed). Look at every figure; outcomes into g2long/JOURNAL.md.
- A chain that stops at its cap before tlim shows FAILED "MAX_SEGMENTS reached": resume with
  `MAX_SEGMENTS=<n> ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena scripts/submit_chain.sh
  $S/<run id> tracks/D-bh-dress/g2long/inputs/<name>.athinput` (announce the extra card time in STATUS.md).

## G2: what the next sessions add (stage/G2/OPEN.md)

1. Exterior constraint norms: add `<particles> region_*` (release core-v0.5) with a sphere outside the
   horizon to the next inputs; the z4c history norms skip chi < 0.0625 (entry 8).
2. Particle number: ES-FL at 4N (or N/4), built on esflk (excision kept) with region norms.
3. The vacuum drift step at 240-300 M (V-1L and V-1L16 alike): a run in which a named cause can fail.
4. Verifier for G2 (fresh context), ladder table (C1), schematic (C9), slice mosaic (C12), note text.

## Packages still open (each writes only its own directory)

- `drift_controls` (cut 2026-11-20): its three tools `tools/compare_runs.py`, `count_blocks.py`,
  `slice_profiles.py` are still UNTRACKED and untested, left as found; they make `nrpic-stage verify`
  fail its "clean" check. Remains: judgement of Pb3-Pb4, the finder pre-flight outcome, part B, README.
  Its question is answered elsewhere (vacuum: boundary; lapse_leak: gauge); low priority. A session that
  owns it should commit or delete them.
- `flux_tools`: README pointing to g2runs entry 10 and g2long entry 5; V-0 not run.
- kb's answer of 2026-11-21 (acknowledged): claims 346 and 414 to restate or drop; 699 and 700 need an
  independent recomputation (low priority).

Decisions pending: none from orch for D. core: ah-excision-growth-guard (new) and the older requests in
STATUS.md `needs`.

Traps: (1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`.
  (2) ES data: puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball:
  read masses as Misner-Sharp or horizon masses. (4) A non-finite run exits 3 with `<base>.guard.txt`.
  (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time is index 12. (7) The finder
  writes into `-d`. (8) The finder summary repeats its first line (t = 0 and 0.5 M identical); use unique
  times. (9) Never kill by pattern; never remove files through a path built from a shell variable.
  (10) `nrpic-ctx ack` renumbers the inbox: ack by file name. (11) A processor re-search of a card dump
  differs from the card's finder by ~3e-8. (12) Q16 snapshots fall near, not on, round a/a_i.
  (13) `nrpic-run submit` refuses an unclean worktree: pass `--package <dir>` while drift_controls has
  untracked files. (14) Format-2 tables end where their maker stopped (ES-F: use the 1340 M table of
  D-20261121-203042-82deeec). (15) nrpic-run passes no PROC_NAME: set it in `chain/config.sh` before the
  first segment (done for the four follow-ups). (16) Horizon excision stops once the smallest horizon
  radius exceeds 4 x `initial_radius_0` (nrpic.cpp:451-455). (17) At M/4 the finder finds no surface at
  t = 0. (18) `nrpic-run submit --launcher local` blocks unless `--background`.
