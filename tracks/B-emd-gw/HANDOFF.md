# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 17, wave 3, 2026-11-25
03:46-04:45 PST: the three population card runs that ended overnight judged; two continuations
queued). Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md has
each missing item with the queue entry that serves it). The population box in full GR is now read
in the Gamma-driver gauge: the zero-shift high-k TT excess and the 0.028 core stop were both the
zero shift. Card runs reach Slurm only through `harness/bin/nrpic-queue` (five jobs per account).
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-queue list --owner B-emd-gw && harness/bin/nrpic-run status | grep -E "submitted|running"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` (section "Batch
17"); `population/JOURNAL.md` (entries 2026-11-25 04:00, 04:10, 04:20: outcomes and the
predictions P8C1-2, S1-S3 of the queued runs).

## Card runs in the shared queue

| Queue id | Label | Run id (Slurm) | What | Read by |
|---|---|---|---|---|
| q0007 | pop_s014_gr256 | B-20261125-093500-242d3a3 (5278 done, 5283 pending) | mesh leg: 256^3, one per cell, zero shift, v0.6 chain, ceiling 5 card-h (5 segments; segment 1 reached t = 4.52 of 21.916 in 50 min, so the cap may end it short: then continue as q0042 does, a batch restart of its newest rst into a new run) | M1-M4 (population/JOURNAL 2026-11-24 06:10): `analyze_gr.py --run m256:<dir>:0.014`, then `compare_legs.py --leg m256:<json>` |
| q0042 | pop_s014_gr_p8_cont | waiting | batch restart of rst/pop.00008.rst (t = 16) of the cut particle leg B-20261124-223926-33194d9 to t = 21.916, list `population/inputs/batch_p8cont.list`, v0.6 card exe, 0.5 card-h | P8C1-2 (04:00 entry); then Q1 at a = 141: analyse a directory holding the cut run's snapshots and dumps up to t = 17 and the continuation's after (symlinks in a new analysis run directory; never write into the old run's directory) |
| q0044 | pop_s028_gd2 (after q0042) | waiting | batch restart of rst/pop.00004.rst (t = 8) of B-20261123-035002-bcc82bd with the Gamma-driver shift of X2 to t = 21.916, list `population/inputs/batch_s028gd.list`, 0.5 card-h | S1-S3 (04:00 entry): `analyze_gr.py --run s028gd:<dir>/s028_gd:0.028`; S2, S3 against the gauge leg's JSON (B-20261125-115558-2ab4161/analysis_gr_gd.json) at the same stage a' = 4a |

q0043 was removed (same run as q0044, re-added with `--after` so that at most two jobs of this
owner are in Slurm). The queue never closes runs: `harness/bin/nrpic-run finish <run id>` when
`nrpic-queue list` shows done.

## Processor work left running at session end (may have been cut)

Closed this session: B-20261124-210431-6bf48af (completed), -210432-6c4d005 (failed, exit 3: the
guard stops of X0, X1), -223926-33194d9 (failed: chain cap), -172958-fc4a2cf (completed).
`nrpic-run finish B-20261124-172958-73b0662` (newton_s028, exit 0) was still hashing at the end and
ends with the session: rerun it if its manifest still says 'running'.

Stage verify G2 without checksums ran at 12:10Z (export 37439b2): every check PASS except 'runs'
(seven runs open then); STAGE_REPORT.md regenerated. Rerun with checksums when q0007, q0042, q0044
and the open finishes are closed.

## Packages (what remains)

- population: N2-N4 (Newtonian reference at the same particles): its analysis runs detached since
  04:24 PST, B-20261125-122434-060d53d (`analyze.py`, both cases, 2 cores; log in its run
  directory; started while the finishes of the two Newtonian runs were hashing). When it ends:
  `nrpic-run finish B-20261125-122434-060d53d`, then `population/scripts/compare_newton.py --gr
  <B-20261124-131918-e71996f>/analysis_gr_s014.json --newton <that run>/analysis_n128.json`, and
  the same against the gauge leg's JSON (B-20261125-115558-2ab4161/analysis_gr_gd.json): masses
  differ by 10-16 per cent between gauges (R23). Q1 at a = 141 (q0042), S1-S3 (q0044), M1-M4 (q0007).
- shear: L2 not converged in the mesh (R19); next an amplitude between M2 and L2 without stream
  crossing before t_A at N_y = 64, 128, 256, 4 per cell, prediction first.
- G2 products: gauge leg at a second mesh (needs a decision: 256^3 shifted, about 5 card-h), note
  sections (C17), schematics (C16), one script per figure (C15), reproducibility list (C6), fresh
  verifier (C18).

Decisions pending: none with orch. Requests open: core (restart parameters, 20261125T121932Z;
Fourier solver threaded, 20261124T173601Z); orch (incremental checksums in stage verify). Inbox:
four messages acknowledged this session (core SIGTERM/chains, orch release v0.7 x2, kb claims).

Traps:
- A restart accepts on the command line only parameters its stored input has (X3 failed so).
- v0.6 chains count a SIGTERM-cut attempt as a segment (the particle leg ended at a = 94.8 so);
  new chains: v0.7 executable and the v0.7 chain script; continuations of v0.6 restart files: v0.6
  executable through batch restarts.
- Halo masses by friends-of-friends depend on the spatial gauge at the 10-16 per cent level (R23):
  state the gauge with every mass.
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; never sbatch or the
  scripts; temporary files under `scratch/B-emd-gw/tmp/`.
