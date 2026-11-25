# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 17 (wave 3), 2026-11-25 ~05:00 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 has an interim package (stage/G2: 9 PASS,
10 OPEN, 1 FAIL) that is NOT ready for review; stage/G2/OPEN.md lists what each item lacks and which
queue entry serves it. The threshold of the expanding ball holds on M/32 and its upper end on M/64.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112";
harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `threshold_ball/JOURNAL.md` entries 10-11;
`szekeres/JOURNAL.md` entries 8 and 10; `periodic_threshold/JOURNAL.md` entries of 2026-11-24 (D1-D5).

## Card runs (shared queue only; no sbatch, no scripts, no sequencer)

| queue id | label | prio | run | what | read by |
|---|---|---|---|---|---|
| q0013 | a-p0l6 | 2 | A-20261125-044641-7d5bd16 (job 5282 pending at 04:00 PST) | P0L on six static levels, chain to t = 140 | periodic_threshold compare_ltb.py, job2_q.py, line_trapped.py; predictions D1-D5; G2 C1 (ii) |
| q0040 | a-szk-n64-128 | 2 | at dispatch | Szekeres N = 64, 128 to tau = 40, batch, v0.7 | szekeres/scripts/analyse_code_runs.py; P17-P21 (entry 8); G2 C1 (iii) |
| q0041 | a-szk-n256 | 2 | at dispatch | Szekeres N = 256, chain, restart every tau = 5, v0.7 | same; needs the N = 64, 128 members for the orders P19 |
| q0015 | a-s1l-cont | 5 | A-20261123-025907-97bab8d | S1L continued from t = 198.7 of 220 | job2_q.py and analyse_scouting.py --gauge leak (S1-S3); SCOPE section 7 triaxial phase-1 criterion |

Removed: q0014 a-cd040 (C-d0.40 on M/64): no G2 item waits for it; T7 stays untested; data set dc0p4C
(A-20261124-133456-2d00507) kept. Done: q0012 (C-d0.42).
Close each run with `harness/bin/nrpic-run finish <run id>` once `scripts/submit_chain.sh --status
/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>` says DONE (finish checksums every restart file: tens of
minutes for the ball runs; start it early, in the background). A cut chain is continued in place with
`harness/bin/nrpic-queue add --label <label>-2 --priority 2 --cmd
'tracks/A-emd-pbh/threshold_ball/scripts/continue_chain.sh <run_id> <higher MAX_SEGMENTS>'`.

## Processor work left

- G1-G3 of threshold_ball entry 5 judged in batch 17 (A-20261125-120158-b76bfe3; outcome at the end of
  threshold_ball/JOURNAL.md). If `nrpic-run status` still lists A-20261124-132016-ecf12c3 or
  A-20261122-173202-f98c79f as not finished, run `harness/bin/nrpic-run finish <id>` (checksums take minutes).
- K4 (threshold_ball entry 10; prediction written): start command at the end of threshold_ball/JOURNAL.md,
  then k4_compare.py on its directory (registered). This is the next test of C3.

## Packages and what remains

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | scan judged (entries 4, 11); K-K3 refuted; guard-stop test judged (entry 5); README current | K4 |
| `szekeres/` | card series queued (q0040, q0041) | analyse when the runs end; particle-number check P22-P23 on processors |
| `periodic_threshold/` | job 2 judged; P0L6 in Slurm; S1L waits | D1-D5; S1-S3; README table and DESIGN 7.1 |
| `conv_ball/`, `verify_bh/`, `periodic_diag/`, `runs_ball/`, `g1close/` | done | C18 verifier of conv_ball numbers |

## Decisions pending

- orch: ruling on the 0.1 constraint bound of SCOPE section 3 (outbox 20261124T133627Z); whether A must run
  the oblate/prolate row (A2) for G2, and a C18 verifier session (outbox 20261125T115950Z).
- core: dt_gauge = 0.9 is in release v0.7 (decision 0035); new Gamma-driver decks carry it.

## Traps

- Predictions about mesh convergence of first-detection times need bounds above one search interval, and
  mass errors compared on common times (threshold_ball entry 11; scripts/t4_common.py).
- The exact same-slice mass exists only where tracked particles cover the horizon's shells: medians over
  it differ in window between meshes.
- With a Gamma-driver use `<z4c> dt_gauge = 0.9` (v0.7) or keep cfl_number below the printed bound.
- No `<z4c> lapse_leak` around an existing black hole for long runs (decision 0025 item 3).
- The processor build reads card restart files: cheap processor diagnostics from restarts.
- Chain histories repeat times after a restart: readers keep the records written last.
- Markdown tables: never write `||H||` inside a table row.
