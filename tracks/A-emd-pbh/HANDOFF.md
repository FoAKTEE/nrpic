# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 19 (wave 3), 2026-11-25 ~07:30 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 has an interim package (stage/G2: 9 PASS,
10 OPEN, 1 FAIL) that is NOT ready for review; stage/G2/OPEN.md lists what each item lacks and which queue
entry or session serves it. The fresh verifier of C18 is answered; A2 ran from S1L and failed its prediction.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112";
harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` section 9; `threshold_ball/JOURNAL.md`
entries 10 and 12 (outcomes); `periodic_threshold/JOURNAL.md` last two entries (A2).

## Card runs (shared queue only; no sbatch, no scripts, no sequencer)

| queue id | label | prio | run | what | read by |
|---|---|---|---|---|---|
| q0013 | a-p0l6 | 2 | A-20261125-044641-7d5bd16 (t = 138 of 140; segment 7 cut by SIGTERM, resubmitted as Slurm 5296, pending at 07:15 PST; 6 of 7 segments used) | P0L on six static levels | periodic_threshold compare_ltb.py, job2_q.py, line_trapped.py; predictions D1-D5; G2 C1 (ii). The status file already shows a find at t = 118.1 (area mass 562: read it critically) |
| q0040 | a-szk-n64-128 | 2 | at dispatch | Szekeres N = 64, 128 to tau = 40, v0.7 | szekeres/scripts/analyse_code_runs.py; P17-P21 (entry 8); C1 (iii) |
| q0041 | a-szk-n256 | 2 | at dispatch | Szekeres N = 256, chain | same |
| q0015 | a-s1l-cont | 5 | A-20261123-025907-97bab8d | S1L continued from t = 198.7 to 220 | S1-S3 and SCOPE section 7 only; NOT needed for A2 |

If P0L6 is cut again with no segment left: `harness/bin/nrpic-queue add --label a-p0l6-2 --priority 2 --cmd
'tracks/A-emd-pbh/threshold_ball/scripts/continue_chain.sh A-20261125-044641-7d5bd16 9'`. Close every run
with `harness/bin/nrpic-run finish <run id>` once `scripts/submit_chain.sh --status <dir>` says DONE.

## Processor work next (no card)

1. A2 cause (RISKS 39): run the S1 particles of A-20261123-025907-97bab8d under `<particles> pusher = newton`,
   `newton_poisson = fft` (core-v0.6 or later processor build), snapshots every 2-5 time units to t = 90, and
   read the first crossing with `periodic_threshold/scripts/a2_crossing.py`. Write the prediction first
   (Newtonian ellipsoidal collapse leads the Zel'dovich 4.2 t_H; refuted if Newton lags like GR).
2. C3: the smoothed-edge test (prep_bh.py --edge-w on data set 3, meshes A and B, processors, section-3 ratio at
   t = 0 and norms to t = 5; prediction first). Orch was asked to confirm that C3 is judged after it (outbox
   20261125T151524Z c3-smoothed-edge-test).
3. Read P0L6 and the Szekeres series when they end (registered analyses, figures looked at).
4. Package items without cards: VERIFY list (C6), ladder schematic (C10), schematics on v0.7 (C16), note G2
   sections (C17, decision 0039 item 9), then a second verifier pass for C18.

## Packages

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | scan judged; C18 answered (entry 12); K4 judged (entry 10 outcome); README corrected | smoothed-edge test |
| `conv_ball/` | done; README corrected after C18 | A-R1.35 ddet (verifier 0.175, README 0.164) unchecked |
| `periodic_threshold/` | A2 judged (refuted); P0L6 in Slurm | Newtonian control for A2; D1-D5; S1-S3 |
| `szekeres/` | card series queued | analyse when the runs end |
| `stage/G2/verifier-c18/` | the fresh verifier's package (batch 18) | none |

## Traps

- Found or not found is ONLY in `<base>.horizon_status_<n>.txt`; the summary repeats the last surface after a
  failed search, and its time column is printed with %g (decision 0040 item 3).
- The exact mass on the code's slice is known only between two tracked particles: quote brackets
  (threshold_ball/scripts/c18_answer.py), never a median below the bracket width.
- ddet at the core edge depends on the interpolation by 0.02-0.08 M on M/32; dtrap does not.
- The threshold's time is the core edge's proper time; the outer layers read about 2.8 M more at detection.
- S1L's coordinate time is close to cosmic time: t/t_H = (1 + 1.5 t)/6^1.5 (relaxed lapse, reference 1).
- With a Gamma-driver use `<z4c> dt_gauge = 0.9` (v0.7) or keep cfl_number below the printed bound.
- No `<z4c> lapse_leak` around an existing black hole for long runs (decision 0025 item 3).
- Markdown tables: never write `||H||` inside a table row.
