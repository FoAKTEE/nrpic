# longruns: the card runs of batch 5 (run (v), heat series, D2, block A), sequenced

Package of the C-sidm lead, batch 5 of wave 3 (2026-11-21, decision 0025 items 3-5: leave
the cards loaded). Predictions, criteria, reference quantities, windows and the noise model
were written before any submission: `../JOURNAL.md`, entry 2026-11-21T20:25Z (R(v), H, D2,
A, T). No run here uses `<z4c> lapse_leak` (no black hole at the start; item 3).

## Files

| File | What |
|---|---|
| `scripts/make_ic_seeds.py` | particle files of the threshold model y0 = 0.334032 for particle seeds 2 and 3 (unkicked, kicked in and out with `threshold_scan/make_scan.kick`); run C-20261121-202552-8f91fb3 |
| `scripts/prep_heat_C.sh` | particle files and lists of the heat series (`heat/scripts/run_mode.py prep`); run C-20261121-202552-883e2c2 |
| `scripts/make_decks.py` | the decks in `inputs/` (block A, D2, timing list) from the threshold_scan, decisive and drift decks; M/8 mesh of drift (`REGION7`) |
| `inputs/` | 15 block A decks `A8_<y0>_s<seed>_<ctrl,kin,kout>`, 5 D2 decks, `timing.list`, `heat_C1.list`, `heat_C2.list` |
| `seq/queue.txt` | the ordered queue (item, launcher, card-hours cap, N, process name, deck or list, purpose) |
| `seq/seq.sh` | the sequencer (at most two C-sidm card jobs eligible; registers each item with nrpic-run; closes finished runs) |

## Batch-11 follow-ups (predictions: ../JOURNAL.md 2026-11-24T13:14Z)

| Item | Deck | What it decides |
|---|---|---|
| N6c | `inputs/A8N_y0p33403_N1e6_s1_ctrl.athinput` | does the M/8 control of the threshold model still collapse at N = 1e6 (NS.1 relaxation against NS.2 scheme)? |
| M16 | `inputs/D2M16_cc2_kn10_f4_s1.athinput` | t_c of CC2 at Kn = 10 on M/16 with collision cells of M/4 (M16.1, M16.2): mesh series 206.64 (M/4), 163.41 (M/8) |
| N4c | `inputs/A8N_y0p33403_N1e4_s1_ctrl.athinput` | the same control at N = 1e4 (NS.3, weak) |

Decks: `scripts/make_decks_b11.py` (run C-20261124-131231-74f067d); particle files of N = 1e6
and 1e4: runs C-20261124-130731-e1d24de, -130732-a383ef5 (`scripts/make_ic_seeds.py --seeds 1
--N ...`); smoke test on the threaded processor build: C-20261124-131249-b06c218.

## How to rerun the analyses (all registered with `--package tracks/C-sidm/longruns`)

    S="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/longruns --cores 1"
    $S -- python3 tracks/C-sidm/longruns/scripts/blockA_delta.py --ripple-tmax 400 --out '$NRPIC_RUN_DIR' <15 block A run ids>
    $S -- python3 tracks/C-sidm/longruns/scripts/d2_analysis.py --out '$NRPIC_RUN_DIR' ctrl=<D2ctl> f1s1=<..> f2s1=<..> f4s1=<..> f2s2=<..>
    $S --cores 2 -- python3 tracks/C-sidm/longruns/scripts/heat_series.py --out '$NRPIC_RUN_DIR' --noise C-20261120-223001-eb81eb7 --group T7_th0.003_e0.2 <heat_C1> <heat_C2>
    $S -- python3 tracks/C-sidm/longruns/scripts/step_time.py --out '$NRPIC_RUN_DIR' --timing <timing run> LABEL=<chain run> ...
    $S -- python3 tracks/C-sidm/longruns/scripts/xcheck_b11.py --out '$NRPIC_RUN_DIR' LABEL=<run> ...

The run ids of the batch-11 analyses are in `../stage/G2/EVIDENCE.md`. The heat cases must be
reduced first (`heat/scripts/run_mode.py reduce <card run> --prep C-20261121-202552-883e2c2`).
Known limit of `blockA_delta.py`: a window that a run covers only in part still enters the
seed standard deviation (fix before seeds 2 and 3 are read).

## Runs (executable: release core-v0.6 card build, except run (v))

| Item | Runs | Length | Expected card-hours | Read with |
|---|---|---|---|---|
| run (v) | C-20261121-202459-12183c5, Slurm 4826 (core-v0.3, pairs with C-20261115-171059-4b70228) | 300 M, M/4, N = 1e4 | 0.3 | `drift/scripts/compare.py --tag cc2_N`, `diffusion.py` (drift README "Pending runs"); N.1-N.6 |
| timing | 4 short segments | 20 M, 10 M | 0.15 | `athena*.log` zone-cycles; prediction T; the loop checks it itself |
| heat_C1, heat_C2 | 8 + 3 cases, 4e6 particles | as heat T8 | 0.5 | `heat/scripts/an_compare.py t8` and `an_mode.py`; H.1-H.4 |
| D2 | D2ctl, D2f2s1, D2f1s1, D2f4s1, D2f2s2 | 300 M, M/8 | 4 | `decisive/scripts/analyze_decisive.py` (t_c, collisions per particle, against D2ctl); D2.1-D2.3 |
| block A | 15 chains (5 model-seeds x ctrl, kin, kout) | 600 M, M/8, N = 1e5 | 21 | `drift/scripts/compare.py` per pair (kicked against ctrl of the same seed); A.1-A.4 |

Total expected about 26 card-hours of the 37.6 left of the allotment (45) toward G2. Each
chain reserves its cap (4 segments for 600 M, 2 for 300 M) only while it runs.

## Operating the sequencer

    S=/data/haiyangw/nrpic/wt/C-sidm/tracks/C-sidm/longruns/seq/seq.sh
    $S status                                  # every item: run id, Slurm job, state
    tail -f /data/haiyangw/nrpic/scratch/C-sidm/seq/seq.log
    $S stop                                    # the loop exits at its next poll (5 min);
                                               # running jobs go on; stop a chain with
                                               # harness/bin/nrpic-run stop <run_id>
    # restart after a stop (or after the machine rebooted):
    cd /data/haiyangw/nrpic/wt/C-sidm && setsid nohup $S run \
      >> /data/haiyangw/nrpic/scratch/C-sidm/seq/nohup.out 2>&1 < /dev/null &

State: `scratch/C-sidm/seq/state.tsv` (item, run id, launcher, Slurm job, SUBMITTED |
CLOSED | RETRY | SUBMIT_FAILED, tries), loop pid in `seq.pid`. To skip an item, add a line
`<item>\t-\t-\t-\tCLOSED\t0` to the state file while the loop is stopped. To change the
queue, edit `queue.txt`, commit it (nrpic-run refuses a dirty package), restart the loop.
Since batch 11 the loop submits while `/data/haiyangw/nrpic/locks/PAUSE` exists and logs that
the flag is there (decision 0026 item 2: a card run uses none of the account's usage), and it
logs why the next item waits whenever the reason changes (decision 0030 item 4). It commits
manifests (nrpic-run) on `track/C-sidm` but never pushes: a session pushes them.

### Preemption and the continuation of cut chains (batch 11)

Jobs of another user in the partition `priority` preempt the `preempt` partition
(PreemptMode CANCEL); AthenaK writes no restart on SIGTERM, so a preempted segment loses the
work since the last restart and still counts as a segment. Ten chains of the batch-5 queue
ended FAILED "MAX_SEGMENTS reached" this way (JOURNAL 2026-11-24T12:59Z). Remedies in place:
- `resume` items in `queue.txt` (`<item> resume <segments to add> <run_id> <proc-name> <deck>
  <athena arg|-> <purpose>`): the loop continues the chain in place from its newest restart
  (`scripts/submit_chain.sh <run dir> <deck> <arg>` with MAX_SEGMENTS raised, JOB_NAME = run
  id), writes a `continuations` entry into the manifest (committed) and closes the run again
  with `nrpic-run finish --status` when the chain ends. All batch-11 continuations pass
  `output2/dt=10` (a restart every 10 M, about 80 s of card time, 1.1 GB each).
- new chain items get MAX_SEGMENTS 20 (`SEG_FLOOR`) right after submission; the harness
  reserves only the gpu-hours of the queue line; sacct gives the card time used at finish.
- the batch-11 decks write a restart every 10 M from the start.
Disk: a 600 M run continued this way writes up to 60 restart files (66 GB). After a run is
closed and analysed, restart files that are not a multiple of 100 M may be removed, by explicit
path, never through a path built from a variable (CLAUDE.md).

A chain that ends with status FAILED because the run turned non-finite after a collapse
(`<z4c_guard>` exit status 3, static mesh) is the expected end of a collapsing run: read
t_c from its history before the guard stopped it.
