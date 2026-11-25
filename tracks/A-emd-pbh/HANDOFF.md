# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 20 (wave 3), 2026-11-25 ~09:00 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 has an interim package (stage/G2: 9 PASS, 10 OPEN,
1 FAIL = C3) that is NOT ready for review (stage/G2/OPEN.md). This session ran the smoothed-edge test for C3 (the
floor is the top hat's jumps plus the PCS deposit at refinement boundaries; smooth data with CIC meet the bound at
t = 0) and the Newtonian control of A2 (the reference is right; S1L's lag is not in it). Both have runs still going.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short &&
harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112";
harness/bin/nrpic-ctx inbox; test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` section 10; `threshold_ball/JOURNAL.md`
entry 13 (all parts); `periodic_threshold/JOURNAL.md` last three entries (A2 control).

## Processor runs still going (detached, started by this session; close each with `harness/bin/nrpic-run finish <id>`)

| run | what | cores | read with |
|---|---|---|---|
| A-20261125-161154-62ce3dc | test F: S2 with the CIC cloud; S2c-A (M/16) to t = 5 (1 thread, ~10:00 PST), S2c-B (M/32) to t = 1 (2 threads, ~11:30 PST) | 3 | `threshold_ball/scripts/edge_compare.py --run <A-20261125-160633-594a474 dir> --extra S2c-A=<F dir>/S2c-A --extra S2c-B=<F dir>/S2c-B`; prediction F2 (entry 13) |
| A-20261125-160633-594a474 | PCS twin S2-A (M/16) to t = 5 (2 threads, ~09:00 PST); S1-A and S2-B were stopped by hand (on record) | 2 | same script (it reads S2-A) |
| A-20261125-160633-e38d321 | A2 control: N-z done; N-f (S1L's particle file as it is) then N-z128 (128^3), 1 thread; the script runs a2_crossing on all three at the end | 1 | `periodic_threshold/scripts/a2_compare.py --gr <A-20261125-151629-bb77171>/a2.json --member 'N-z (Newton)=...' --member 'N-f (Newton, GR file)=<run>/N-f/a2/a2.json' --member 'N-z128=<run>/N-z128/a2/a2.json'`; AZ2 and the N-z128 part of AZ1 |

## Card runs (shared queue only; no sbatch, no scripts, no sequencer). No card time used this session.

| queue id | label | prio | run | read by |
|---|---|---|---|---|
| q0013 | a-p0l6 | 2 | A-20261125-044641-7d5bd16 (t = 138 of 140; Slurm 5296 pending since 07:15 PST; chain NOT ended, so the find at t = 118.1 was not read) | periodic_threshold compare_ltb.py, job2_q.py, line_trapped.py; predictions D1-D5; read the find at t = 118.1 only from `horizon_status_*.txt` (decision 0040 item 3) |
| q0040 | a-szk-n64-128 | 2 | at dispatch | szekeres/scripts/analyse_code_runs.py; P17-P21 |
| q0041 | a-szk-n256 | 2 | at dispatch | same |
| q0015 | a-s1l-cont | 5 | A-20261123-025907-97bab8d | S1-S3, SCOPE section 7 |

If P0L6 is cut again with no segment left: `harness/bin/nrpic-queue add --label a-p0l6-2 --priority 2 --cmd
'tracks/A-emd-pbh/threshold_ball/scripts/continue_chain.sh A-20261125-044641-7d5bd16 9'`.

## Next, in order

1. F2: when S2c-A has reached t = 5 (and S2-A), run edge_compare.py (registered) with the extras; judge F2 against entry
   13 (ratio < 0.1 at every output, ||H||_2 at t = 1, 2 at least 3 times below K4-ref and below S2-A); figure looked at.
   Then C3 per 0039 item 2(c) and the orch answer to outbox c3-smoothed-edge-result.
2. A2: AZ2 from N-f, N-z128 from the same run (a2_compare.py, registered). Then the next control that can tell a
   relativistic lag from a coordinate effect (the reader measures coordinate separations; S1L's Gamma-driver shift
   moves the lattice): a gauge-invariant crossing measure (proper separation from the metric dumps, or the sign of
   the Jacobian of the particles' proper volume) or a short GR member with zero shift. Prediction first.
3. Stage: `harness/bin/nrpic-stage verify A-emd-pbh G2 --full` detached once the processor runs above are closed
   (hundreds of GB; it uses up to four hashing processes, so only with cores free); this session ran verify with
   --no-checksums because six cores were in use by the runs.

## Packages

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | entry 13: data S1, S2 (prep_bh.py --profile smooth_tophat), tests D and F1 done | F2; if C3 is judged on smooth members, the scan on the smooth profile (exact threshold from expball first) |
| `periodic_threshold/` | A2 failed as written (0040 item 7); control N-z done (AZ1 narrowly refuted: 4.55 vs band edge 4.5) | AZ2 (N-f), N-z128; P0L6 (q0013) when its chain ends |
| `conv_ball/` | prep_bh.py gained `--profile` | A-R1.35 ddet unchecked |
| `szekeres/` | card series queued | analyse when the runs end |

## Traps

- `prep_bh.py --edge-w` cannot widen data set 3's outer taper beyond 0.204 M (expball: R2 <= R_b - w); smooth members
  are another profile (smooth_tophat; R1 = 0.65 R_b is not admissible at delta_c = 1.5, negative density).
- edge_compare.py's ratio is the x-line version of SCOPE section 3 (weights x^2 dx), as analyse.py; no horizon before
  t = 5 in these members, so the whole line counts.
- a2_newton_ic.py's ic.json "median_u_over_disp" is wrong (lattice offset bias); the particle files are right.
- Found or not found is ONLY in `<base>.horizon_status_<n>.txt` (decision 0040 item 3).
- Quote exact-mass brackets, never a median below the bracket width (threshold_ball/scripts/c18_answer.py).
- With a Gamma-driver use `<z4c> dt_gauge = 0.9` (v0.7) or keep cfl_number below the printed bound.
- At most 6 cores per session: the three runs above use 6 until ~09:00 PST, then 4, then 3.
- Markdown tables: never write `||H||` inside a table row.
