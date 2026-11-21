# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the lead of batch 5 of
wave 3 ("cards first", decision 0025), 2026-11-21 from 20:19 to about 20:40 UTC.

State in three lines:
1. G0 and G1 are signed (G1 with reservations, `stage/G1/GATE_REVIEW.md`). G2 is open; no
   stage/G2 package exists yet.
2. The cards are loaded: run (v) and a timing job are in Slurm, and 22 more items wait in
   `longruns/seq/queue.txt` behind a sequencer that keeps two C-sidm card jobs eligible.
3. Predictions, criteria, windows and the noise model of every queued run are in
   `JOURNAL.md` entry 2026-11-21T20:25Z (R(v), T, H.1-H.4, D2.1-D2.3, A.1-A.4). Judge each
   run against them when it ends; failed predictions stay on record.

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && tracks/C-sidm/longruns/seq/seq.sh status && squeue -o '%i %j %T %M' && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## The sequencer (read `longruns/README.md` "Operating the sequencer")

- Script: `tracks/C-sidm/longruns/seq/seq.sh` (`run`, `status`, `stop`). State, log, pid:
  `/data/haiyangw/nrpic/scratch/C-sidm/seq/` (`state.tsv`, `seq.log`, `seq.pid`, `nohup.out`).
- See it: `tracks/C-sidm/longruns/seq/seq.sh status`; is it alive: `kill -0 $(cat /data/haiyangw/nrpic/scratch/C-sidm/seq/seq.pid) && echo alive`.
- Stop it: `tracks/C-sidm/longruns/seq/seq.sh stop` (exits at its next poll, at most 5 min;
  running card jobs go on). Never kill by pattern; if you must, `kill <pid from seq.pid>`.
- Restart it (after a stop, a reboot, or a queue edit that you committed):
  `cd /data/haiyangw/nrpic/wt/C-sidm && setsid nohup tracks/C-sidm/longruns/seq/seq.sh run >> /data/haiyangw/nrpic/scratch/C-sidm/seq/nohup.out 2>&1 < /dev/null &`
- It submits only while fewer than two items are active and fewer than two `C-*` jobs are in
  squeue, and nothing while the pause flag exists. So: do not submit card jobs by hand while
  it runs, or it will wait for yours.
- It registers each item with `nrpic-run submit --package tracks/C-sidm/longruns`, and
  `nrpic-run` refuses when the package has uncommitted edits. So commit any edit inside
  `longruns/` at once. A refused item is retried every 5 min, up to 12 times.
- It closes ended runs with `nrpic-run finish` and commits the manifests locally. Push them
  (`git pull --no-rebase --no-edit && git push origin track/C-sidm`).
- It stops itself after the timing job if the M/8 deck runs slower than about 18 s per M.
  Then re-size the chains (`--gpu-hours` in queue.txt), commit, and restart it.
- A chain of a collapsing run can end FAILED by `<z4c_guard>` (exit 3, non-finite after the
  collapse on the static mesh). That is the expected end. Read t_c from the history.

## Runs and what reads them

| Item | Run id / Slurm | Reader | Predictions |
|---|---|---|---|
| run (v) | C-20261121-202459-12183c5 / 4826 (core-v0.3) | `drift/README.md` "Pending runs": `compare.py --tag cc2_N` with `cc2_N1e5=cc2:/data/haiyangw/nrpic/scratch/C-sidm/C-20261115-171059-4b70228/cc2_kninf cc2_N1e4=cc2:<run dir>/cc2_kninf_N1e4 --ratio cc2_N1e4/cc2_N1e5`, and `diffusion.py` | N.1-N.6 (drift/JOURNAL.md entries 5, 11, 14); criterion R(v) |
| timing | C-20261121-203004-c2c14e7 / 4829 | zone-cycles/cpu_second in `<run dir>/T_*/athena*.log` (core-v0.3 on M/8: 7.28e6) | T |
| heat_C1, heat_C2 | queued | `heat/scripts/an_compare.py t8` and `an_mode.py T7` on the batch directories (heat README lines 40-80) | H.1-H.4 |
| D2 (5 chains) | queued | `decisive/scripts/analyze_decisive.py` (t_c, collisions per particle), against D2ctl | D2.1-D2.3 |
| block A (15 chains) | queued | `drift/scripts/compare.py`, pairs `A8_<y0>_s<s>_kin` / `_kout` against `_ctrl`; window means of Delta per 100 M; sigma_w from the three seeds at 0.334032 | A.1-A.4 |

Every analysis is a registered run: `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/<package> --cores 2 --purpose "..." -- python3 ...`, with a figure that you Read.

## Packages still in progress (none has uncommitted files)

- drift: run (v) pending. Runs (ii) and (iv) are dropped.
- models: paused since 2026-11-20. Step 5 is left: the King runs, alpha_coll minus the
  control (predictions K in `models/JOURNAL.md` entry 9).
- threshold_scan: block A is queued in `longruns/`. Blocks B (convergence), C (adaptive mesh
  with horizon finder) and D (collisional bracket) are not written for M/8.
- decisive: D2 is queued in `longruns/`.
- longruns: as above.

## Decisions of this session

- Block A runs at N = 1e5 on M/8, for 600 M (not 1000 M). Every kicked run has its unkicked
  control of the same seed, mesh, N and executable. There are three particle seeds at
  y0 = 0.334032 and one at 0.324 and at 0.344. The restart files every 100 M allow a longer
  continuation later.
- Run (v) keeps core-v0.3, so that only N differs from its N = 1e5 partner. Everything else
  runs on release core-v0.6.
- D2 varies `coll_cell_factor` (1, 2, 4) on M/8 at Kn = 10 in particle mode.

## Traps

- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`. Wait while
  `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock` exists; the sequencer commits too.
- A restarted run writes its `cc.nrpic.hst` without a header line. Read it with
  `drift/scripts/controls.py` join_hst.
- Card runs with deposition are not byte-reproducible. Read effects against a control of the
  same mesh, seed and executable.
- Disk: each M/8 run writes about 8-10 GB (restart files of 1.1 GB every 100 M), so the
  queue writes about 200 GB under `scratch/C-sidm/` (21 TB free at submission).
- Collisions stop on more than one MPI rank. Never kill by pattern. Use at most 6 cores.
