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
The loop does not submit while `/data/haiyangw/nrpic/locks/PAUSE` exists (decision 0019);
items already submitted go on. It commits manifests (nrpic-run) on `track/C-sidm` but never
pushes: a session pushes them.

A chain that ends with status FAILED because the run turned non-finite after a collapse
(`<z4c_guard>` exit status 3, static mesh) is the expected end of a collapsing run: read
t_c from its history before the guard stopped it.
