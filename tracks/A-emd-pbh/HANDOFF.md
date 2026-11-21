# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 7 (wave 3), 2026-11-21 ~15:30 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 (horizon formation of the
spherical expanding ball against the exact solution) has its convergence series (conv_ball) and
its independent check (verify_bh); the threshold scan (threshold_ball) is on the cards behind an
unattended sequencer. The periodic box's failure (job 4799) is explained (Gamma-driver step
instability above dt/dx 0.685, package periodic_diag, decision 0027); the deck now runs
cfl_number 0.5 and its second card job (P0L, S1L) is queued behind the scan (lines 14-15).

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short && squeue -u $USER -o "%.8i %.28j %.8T %.10M" | grep " A-" ; tail -5 /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/sequencer.log; cat /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/done.txt; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112[1-9]"; harness/bin/nrpic-ctx inbox`

Files to read first: `STATUS.md`; `threshold_ball/DESIGN.md` and `threshold_ball/JOURNAL.md`
(predictions T1-T6, entry 1); `periodic_threshold/JOURNAL.md` entries 13:20Z (P1-P4, S1-S3) and
2026-11-21 23:15Z (Q1-Q3, the remedy test); `periodic_diag/README.md` (cause, margin, costs);
`stage/REVIEW-wave3.md` section 6; `RISKS.md` rows 23, 27-30; `conv_ball/README.md`.

## The cards: what runs, how to see it, how to stop it

A sequencer (`threshold_ball/scripts/sequencer.sh`, started 12:41:49 PST with setsid nohup, pid in
`scratch/A-emd-pbh/sequencer_threshold/sequencer.pid`, 2666191) re-reads `threshold_ball/queue.txt`
every 5 minutes and submits the next line through `harness/bin/nrpic-run submit` when fewer than
two Slurm jobs named `A-*` of this user are queued or running; nrpic-run commits each manifest.
Record: `done.txt` (queue line number, time, rc, run id), `sequencer.log`.
- See it: `ps -p $(cat /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/sequencer.pid)`.
- Stop gracefully: `touch /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/STOP`; at
  once: `kill <pid from sequencer.pid>` (numeric PID only).
- Restart (skips lines in done.txt): `cd /data/haiyangw/nrpic/wt/A-emd-pbh && rm -f /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/STOP && setsid nohup tracks/A-emd-pbh/threshold_ball/scripts/sequencer.sh tracks/A-emd-pbh/threshold_ball/queue.txt /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold >> /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/nohup.out 2>&1 < /dev/null &`
- TRAP: done.txt keys on LINE NUMBERS. Add queue lines at the END only; never insert or delete
  a line above an unsubmitted one (it shifts the numbers and resubmits or skips runs).
- A submission is refused (retried five times, then marked skipped) while the line's package
  (`--package`) has uncommitted changes: lines 3-13 need `threshold_ball/` committed, lines 14-15
  `periodic_threshold/`. A skipped line by hand: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && eval "harness/bin/nrpic-run submit $(sed -n <N>p tracks/A-emd-pbh/threshold_ball/queue.txt)"`.
- It runs while the pause flag exists (decision 0025 item 4); stop it if the orchestrator asks.

| line | member | run id / Slurm (15:15 PST) | tlim | card-h asked / model | read by |
|---|---|---|---|---|---|
| 3 | B-d0.42 (delta_c 0.42, M/32, outer 32 M, v0.6) | A-20261121-204149-c48bd33 / 4838 PENDING | 51 | 2.0 / 0.6 | T1, T3 |
| 4 | B-d0.40 | A-20261121-204250-0bf45c7 / 4845 PENDING | 54 | 2.0 / 0.6 | T2, T3 |
| 5 | A-d0.42 + A-d0.40 (batch, M/16) | sequencer | 51, 54 | 0.67 / 0.1 | T4 |
| 6-11 | B-d0.45, B-d0.50, B-d1.00, B-d0.70, B-d0.35, B-d0.20 | sequencer | 47, 42, 23, 31, 62, 70 | 1-2 / 0.25-0.8 each | T1, T2 |
| 12 | C-R1.25 (conv_ball's ball-radius leg, mesh C, core_gauge) | sequencer | 16 | 4 / 2.3 | T5 |
| 13 | C-d0.42 (M/64) | sequencer | 51 | 14 / 8.2 | T4 |
| 14 | periodic P0L (peak mu 0.3, 4 static levels, cfl 0.5, v0.6) | sequencer | 140 | 2.0 / 0.7 | Q1-Q3, P1-P4 |
| 15 | periodic S1L (S1 data mu 0.3, e 0.2, cfl 0.5, v0.6) | sequencer | 220 | 3.0 / 1.1 | Q1-Q3, S1-S3 |

Each line is a chain (`scripts/submit_chain.sh` of core-v0.6; MAX_SEGMENTS = floor(card-hours /
59 min); athena -t 50 min per segment) except line 5 (a batch job). A chain's outputs land in
`scratch/A-emd-pbh/<run id>/` itself (chain state in `chain/`); `scripts/submit_chain.sh --status
<dir>`. A chain that stops after its last segment before tlim resumes with
`scripts/submit_chain.sh <rundir> <deck> <same args>` from the newest restart (needs a note in the
package journal). Disk: C chains write 5.1 GB per restart (RISKS row 30).

## Reading the threshold scan (lines 3-13)

`harness/bin/nrpic-run finish <run id>`; then the analysis. threshold_ball has no analysis script
yet: write `threshold_ball/scripts/analyse.py` around conv_ball's `scripts/compare.py` (copy;
`--gauge leak --leak 8 --nest 32:32` for B, `32:16` A, `32:64` C; `--prep <data run>/<dc set>/nestB`,
data run A-20261121-202812-cae4436), register it, judge T1-T6 in `threshold_ball/JOURNAL.md`
entry 3 onward, figures looked at. Read the step time of the first B chain (T6: 0.25-0.40 s per
cycle) and correct the model in DESIGN.md if it is outside.

## Reading periodic job 2 (lines 14-15): exact commands

From the worktree root, once `done.txt` has lines 14 and 15 and their chains are out of squeue:
```
cd /data/haiyangw/nrpic/wt/A-emd-pbh
S=/data/haiyangw/nrpic/scratch/A-emd-pbh
P0L=$(awk '$1==14{print $4}' $S/sequencer_threshold/done.txt); S1L=$(awk '$1==15{print $4}' $S/sequencer_threshold/done.txt)
scripts/submit_chain.sh --status $S/$P0L; scripts/submit_chain.sh --status $S/$S1L
grep -h "Terminating\|guard\|exit" $S/$P0L/chain/*.log $S/$S1L/chain/*.log | tail   # tlim reached, wall stop or guard (exit 3)
harness/bin/nrpic-run finish $P0L; harness/bin/nrpic-run finish $S1L
# Q1 (the remedy): card_onset.py expects <job>/P0L and <job>/S1L; give it a directory of links
mkdir -p $S/tmp/job2 && ln -sfn $S/$P0L $S/tmp/job2/P0L && ln -sfn $S/$S1L $S/tmp/job2/S1L
R="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/periodic_threshold --launcher local --cores 1"
$R --parent $P0L --parent $S1L --purpose "job 2 Q1: onset and step against Test B" -- bash -c 'python -I tracks/A-emd-pbh/periodic_diag/scripts/card_onset.py --job /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/job2 --vn /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-212800-d7f31a4 --out "$NRPIC_RUN_DIR"'
# P1-P4: P0L against the exact LTB reference B
$R --parent $P0L --purpose "job 2 P0L vs LTB" -- bash -c 'python -I tracks/A-emd-pbh/periodic_threshold/scripts/compare_ltb.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/'$P0L' --ref /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-130103-e007f42 --label P0L --out "$NRPIC_RUN_DIR"'
# S1-S3: S1L in the relaxed gauge (S1 of the E1 gauge needs a separate call without --gauge leak)
$R --parent $S1L --purpose "job 2 S1L" -- bash -c 'python -I tracks/A-emd-pbh/periodic_threshold/scripts/analyse_scouting.py --gauge leak --run S1L=/data/haiyangw/nrpic/scratch/A-emd-pbh/'$S1L' --out "$NRPIC_RUN_DIR"'
```
card_onset.py was written for job 4799's batch layout (files `peak.*` in each member directory,
which a chain also writes); if it reads a file name a chain does not have, adapt a copy in
periodic_threshold/scripts, not periodic_diag's. Read every figure, judge Q1-Q3 first
(`periodic_threshold/JOURNAL.md` entry 23:15Z), then P1-P4 and S1-S3 (entry 13:20Z), and post the
outcome of Q1 to core (it informs their gauge-speed step limit). If Q1 fails: no further periodic
card job until core's step limit exists; the zero-shift deck at cfl 1.0 (periodic_diag R2) is the
fallback, with its gauge consequences in a collapse.

## Packages and what remains

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | on the cards (lines 3-13) | analysis script, outcomes T1-T6, README with results; next scan after it: the triaxial (Zel'dovich) ball with core-v0.6 `id_solve` on a refined mesh |
| `periodic_threshold/` | job 2 queued (lines 14-15) | judge Q1-Q3, P1-P4, S1-S3 (commands above); README table, DESIGN 7.1; adaptive-refinement run only after Q1 holds |
| `periodic_diag/` | done (batch 6), request posted | R0 and R1 on processors not run (cost); core's answer |
| `conv_ball/` | done | second agent on its G2 reading (JOURNAL entry 12); C-R1.25 queued (line 12) |
| `verify_bh/` | done | slice-or-finder origin of the first-detection mass excess [TO VERIFY]: read threshold_ball's field dumps |
| `szekeres/` round 1 | cut 2026-11-20 (journal entry 9) | card series N = 64, 128, 256 to tau = 40 (about 1-1.5 card-hours): append to the queue when the scan has run |
| `runs_ball/`, `g1close/`, G1 review | done | nothing |

## Decisions pending

- core: periodic-gamma-driver-step (posted batch 7; closes periodic-relaxed-lapse-blowup),
  bh1r-inte-deficit-two-levels; deferred earlier: phase-1 periodic generator for mu >= 0.5,
  refined-level solve, finder spin.
- kb: szekeres-conformal-flatness (acknowledged; waits for its claims package).
- orch: informed of the loaded cards (outbox cards-loaded-threshold-scan); periodic job 2 adds 4.9
  card-hours requested (STATUS budget line).

## Traps

- With a Gamma-driver keep cfl_number <= 0.6 (decision 0027); lapse_leak x dt above ~2.5 is also
  unstable (periodic_diag U8/U9): on a coarse root mesh lower lapse_leak.
- The conv_ball decks do not declare `<fastflow> diagnostics`: AthenaK refuses a command-line
  parameter that the deck lacks (smoke test A-20261121-203156-d094c56). Use threshold_ball/decks.
- `hmean_tol_0 = 100` in the old decks stops the finder at its first iteration (RISKS 23): the
  queue overrides it with 1e30; peak_leak has 1e30.
- The threshold outcome is judged in the shell's proper time (ddet), not coordinate time (RISKS 28).
- Helpers sharing the worktree: commit path-limited, `nrpic-run submit --package <dir>`.
- Kill processes by numeric PID only; never `pkill -f`.
