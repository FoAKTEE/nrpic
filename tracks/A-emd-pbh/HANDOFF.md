# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 5 (wave 3), 2026-11-21 ~12:55 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 (horizon formation of the
spherical expanding ball against the exact solution) has its convergence series (conv_ball) and
its independent check (verify_bh); this batch put the first threshold scan (threshold_ball) and
conv_ball's missing C-R1.25 member on the cards behind an unattended sequencer. The periodic box
has no working relaxed-lapse run (card job 4799 failed; request to core).

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short && squeue -u $USER -o "%.8i %.28j %.8T %.10M" | grep " A-" ; tail -5 /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/sequencer.log; cat /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/done.txt; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112[1-9]"; harness/bin/nrpic-ctx inbox`

Files to read first: `STATUS.md`; `threshold_ball/DESIGN.md` and `threshold_ball/JOURNAL.md`
(predictions T1-T6, entry 1, committed before the first submission); `stage/REVIEW-wave3.md`
section 6; `RISKS.md` rows 23, 27-30; `conv_ball/README.md` (the measures and the scripts the
scan is read with).

## The cards: what runs, how to see it, how to stop it

A sequencer (`threshold_ball/scripts/sequencer.sh`, started 12:41:49 PST with setsid nohup, pid in
`scratch/A-emd-pbh/sequencer_threshold/sequencer.pid`, at start 2666191) reads
`threshold_ball/queue.txt` and, every 5 minutes, submits the next line through
`harness/bin/nrpic-run submit` when fewer than two Slurm jobs named `A-*` of this user are queued
or running. It commits each run manifest on `track/A-emd-pbh` (nrpic-run does). Its record:
`done.txt` (queue line number, time, rc, run id), `sequencer.log`.
- See it: `ps -p $(cat /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/sequencer.pid)`.
- Stop it gracefully: `touch /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/STOP`
  (it exits at its next check); at once: `kill <pid from sequencer.pid>` (numeric PID only).
- Restart it (it skips lines already in done.txt): `cd /data/haiyangw/nrpic/wt/A-emd-pbh && rm -f /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/STOP && setsid nohup tracks/A-emd-pbh/threshold_ball/scripts/sequencer.sh tracks/A-emd-pbh/threshold_ball/queue.txt /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold >> /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_threshold/nohup.out 2>&1 < /dev/null &`
- It is refused (and retries, five times per line, then marks the line skipped) while
  `tracks/A-emd-pbh/threshold_ball/` has uncommitted changes: commit that package promptly.
  A skipped line is submitted by hand: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && eval "harness/bin/nrpic-run submit $(sed -n <N>p tracks/A-emd-pbh/threshold_ball/queue.txt)"`.
- The sequencer also runs while the pause flag exists (card time is not limited by the usage
  window, decision 0025 item 4); stop it if the orchestrator asks.

Queue (`queue.txt` line: member, what it is, model card-hours; data run A-20261121-202812-cae4436):

| line | member | run id / Slurm (12:45 PST) | tlim | model card-h | read by |
|---|---|---|---|---|---|
| 3 | B-d0.42 (delta_c 0.42, M/32, outer 32 M, v0.6) | A-20261121-204149-c48bd33 / 4838 PENDING | 51 | 0.6 | T1, T3 |
| 4 | B-d0.40 | A-20261121-204250-0bf45c7 / 4845 PENDING | 54 | 0.6 | T2, T3 |
| 5 | A-d0.42 + A-d0.40 (batch, M/16) | sequencer | 51, 54 | 0.1 | T4 |
| 6-11 | B-d0.45, B-d0.50, B-d1.00, B-d0.70, B-d0.35, B-d0.20 | sequencer | 47, 42, 23, 31, 62, 70 | 0.25-0.8 each | T1, T2 |
| 12 | C-R1.25 (conv_ball's ball-radius leg on mesh C, core_gauge, deck conv_ball/decks/nest64_L16) | sequencer | 16 | 2.3 | T5 |
| 13 | C-d0.42 (M/64, nestC 4969736 particles) | sequencer | 51 | 8.2 | T4 |

Each line is a chain (`scripts/submit_chain.sh` of core-v0.6; MAX_SEGMENTS = floor(card-hours
requested / 59 min); process name nrc-<hash>, not "athena") except line 5 (a batch job).
nrpic-run cannot pass PROC_NAME, so the default run-specific name holds. Outputs:
`scratch/A-emd-pbh/<run id>/` (chain state in `chain/`, `scripts/submit_chain.sh --status <dir>`).
A chain that stops after its last segment before tlim (cost model off by more than about 2.5)
resumes with `scripts/submit_chain.sh <rundir> <deck> <same args>` from the newest restart; it then
needs a new registration note in the package journal.

When a run ends: `harness/bin/nrpic-run finish <run id>`; then the analysis. threshold_ball has
no analysis script yet: write `threshold_ball/scripts/analyse.py` around conv_ball's
`scripts/compare.py` (copy; `--gauge leak --leak 8 --nest 32:32` for B, `32:16` A, `32:64` C, and
`--prep <data run>/<dc set>/nestB` etc.), register it, compare with T1-T6, record outcomes in
`threshold_ball/JOURNAL.md` entry 3 onward, figures looked at. Also read the step time of the first
B chain (T6: 0.25-0.40 s per cycle) and correct the model in DESIGN.md if it is outside.
Disk: C chains write 5.1 GB per restart; remove superseded restart files after finish and verify
(RISKS row 30).

## Packages and what remains

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | new this batch; on the cards | analysis script, outcomes T1-T6, README with results; then the bisection is done (exact bracket (0.40, 0.42] has ratio 1.05). Next scan after it: the triaxial (Zel'dovich) ball with core-v0.6 `id_solve` on a refined mesh (its vector part stalls at level boundaries, coord/INTERFACES/id_solver2.md test C) |
| `conv_ball/` | done (batch 2b) | second agent on its G2 reading (JOURNAL entry 12); C-R1.25 queued here |
| `verify_bh/` | done (batch 3) | slice-or-finder origin of the first-detection mass excess [TO VERIFY]: read the threshold_ball field dumps at tau_AH and the lines at first detection |
| `periodic_threshold/` | card job 1 failed (journal entry 20:44Z) | wait for core's answer (outbox periodic-relaxed-lapse-blowup); then a deck that runs past t = 10, P0L against the LTB reference, S1L; refinement after that |
| `szekeres/` round 1 | cut 2026-11-20 (journal entry 9) | card series N = 64, 128, 256 to tau = 40 (about 1-1.5 card-hours): add to the queue when the threshold scan has run |
| `runs_ball/`, `g1close/`, G1 review | done | nothing |

## Decisions pending

- core: periodic-relaxed-lapse-blowup; bh1r-inte-deficit-two-levels (both posted 2026-11-21);
  deferred earlier: phase-1 periodic generator for mu >= 0.5, refined-level solve, finder spin.
- kb: szekeres-conformal-flatness (kb acknowledged; waits for its claims package).
- orch: informed of the loaded cards (outbox cards-loaded-threshold-scan).

## Traps

- The conv_ball decks do not declare `<fastflow> diagnostics`: AthenaK refuses a command-line
  parameter that the deck lacks (smoke test A-20261121-203156-d094c56). Use threshold_ball/decks.
- `hmean_tol_0 = 100` in the decks stops the finder at its first iteration (RISKS 23): the queue
  overrides it with 1e30.
- The outcome of the threshold is judged in the shell's proper time (ddet), not in coordinate time
  (RISKS 28).
- Helpers sharing the worktree: commit path-limited, `nrpic-run submit --package <dir>`.
- Kill processes by numeric PID only; never `pkill -f`.
