# g2prod: USR production ladder of gate G2 on the release card build (E-stoch-inf)

Started 2026-11-21 by the lead of batch 5. Criteria: `../spec/scope/SCOPE.md` section 4c (fixed
before the runs). Predictions per run: `JOURNAL.md` entry 1. Executable: release core-v0.6,
`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena` (cards), `.work/build_cpu_v06/src/athena`
(processor restart check).

Files:
- `inputs/usr_prod.athinput`: the deck of the scouting pair U256/U256m plus a restart output.
- `inputs/timing.list`: 40-step timing at 256^3, 320^3, 384^3.
- `queue.txt`: the runs the sequencer submits, in order (label, card-hours ceiling of the chain,
  purpose | athena arguments).
- `scripts/sequencer.sh`: keeps at most two card jobs of E eligible, submits the next queue line
  through `harness/bin/nrpic-run` (chain launcher, kind production, gate G2), closes finished
  runs with `nrpic-run finish`, retries submissions refused by the allotment every 15 min.
  State, log and pid in `/data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/`.
- `scripts/restart_check.sh`: processor check R0 that a restart of this deck is exact.

The sequencer is retired (decision 0033: card runs go through `harness/bin/nrpic-queue` only).

## Runs (release card build core-v0.6; all finished)

U256ap/am E-20261121-211214-0377aab / -214629-da64fb7 (seed A, s = +-1); U320ap/am
E-20261122-023427-0ac3f0b / E-20261122-110042-ffcb4b3; U256bp/bm E-20261122-033244-564627b /
-071038-d9f933b (seed B); U256hp/hm E-20261122-113320-9bbb52b / -152116-0542096 (s = +-1/2);
U256nc E-20261122-190341-0419be6 (control, momentum source flipped); U256qp/qm
E-20261123-230004-861aea7 / -230507-a6246b1 (s = +-1/4). P256v6 (SR) E-20261121-202935-31520bc.

## Analyses and how to rerun them

Every analysis is a registered run; its exact command (cwd = worktree root) is the `command` field
of `../runs/<run_id>/manifest.json`. To rerun one, from the worktree root:

```text
harness/bin/nrpic-run submit --kind production --gate G2 --preregistered "tracks/E-stoch-inf/g2prod/JOURNAL.md#entry-<k>" \
  --purpose "rerun of <run_id>" --launcher local --package tracks/E-stoch-inf/g2prod --cores 3 -- \
  $(python3 -c "import json,shlex,sys; print(' '.join(map(shlex.quote, json.load(open(sys.argv[1]))['command'])))" tracks/E-stoch-inf/runs/<run_id>/manifest.json)
```

(replace `$NRPIC_RUN_DIR`-relative outputs as the command does; 256^3 readers take 25-60 min on 3
cores, disk-bound; read cold dumps sequentially).

| Run | What | Entry |
|---|---|---|
| E-20261123-015014-b4ecd4e | T (timing) and P256v6 (SR on the release) | 2.1 |
| E-20261123-014858-8e72d4c | seed A, s = +-1 and +-1/2 (analyse_g2.py, group g2a) | 2.3 |
| E-20261123-021730-a421438 | seed B (group g2b) | 2.2 |
| E-20261123-020751-0baf597 | 320^3 pair (group g2r) | 2.2 |
| E-20261123-024359-5dc3213 | judge_g2.py: SCOPE 4c as written, figures fig_g2_* | 2.3 |
| E-20261123-024806-3c0e139 | check of the judge | 2.3 |
| E-20261124-233223-51b52c0 | quarter pair s = +-1/2, +-1/4 (group g2q) | 4 |
| E-20261125-033357-a608cda, E-20261125-033450-4c4a31c | judge_q.py: Q-a..Q-c (second run: figure fix) | 4.1 |

Fresh verifier of the package (own readers; 0 card-hours): `../stage/G2/VERIFIER.md` and
`../stage/G2/verifier/` (runs E-20261125-0221* to -023609-01d8feb).

## Results (JOURNAL entries 2-4; SCOPE 4c as written)

U-A0, U-A1, U-A2', U-A3 (both seeds), U-A4'(b)-(d), U-R, U-S, U-W: PASS. U-A4'(a): FAIL at one
dump of M (3.9245 at cN 6.52; bar 3.95-4.05), on record without rewording (rulings 0030 item 2,
0036 item 2). Quarter pair: Q-a REFUTED (4.1275 from s = 1/2, 1/4), Q-b and Q-c hold. The
three-amplitude reading of the verifier (E-20261125-023427-6fb6400: per-run part of equal size at
every s; with it every judged factor within 4 +- 0.005) stands beside the failure as a finding
made after the data. Note: `../repro/note/manuscript/main.pdf` Sec. IV and ledger Table XVI.
