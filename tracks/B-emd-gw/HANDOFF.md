# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 23, wave 3, 2026-11-25
18:17-19:15 PST: the three ended queue entries judged, the gauge at a second mesh queued).
Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md
maps each missing item to q0060 or to a running analysis). One card run waits in the shared
queue (q0060); three processor analyses were still running at the end of the session.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-queue list --owner B-emd-gw && harness/bin/nrpic-run status | grep -E "submitted|running"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` (section "Batch
23"); `population/JOURNAL.md` entries 2026-11-25 18:35 (how each prediction is judged; the
header times "18:35" and "18:50" are labels, see the 18:30 entry), 18:50 (GM1-GM4), 18:30 (N2e,
GN1e), 18:51 (outcomes).

## Processor analyses still running (registered; close with `nrpic-run finish <id>` first)

| Run id | What | Then |
|---|---|---|
| B-20261126-022356-52c2460 | `analyze_gr.py --equal-mass` on the 256^3 zero-shift run at t = 2-18 (halos t = 14-18), 3 workers, about 30 GB each | M2 (halo counts and largest mass against the base's equal-mass catalogue B-20261126-022407-87e8803 at a = 64-100), M3 (band strain to a = 50; high-k part at a = 81-100): `compare_legs.py --base B-20261124-131918-e71996f/analysis_gr_s014.json --leg m256:<its analysis_gr_m256.json>` |
| B-20261126-022403-82f6e69 | the 0.028 shifted box, all dumps and snapshots | `judge_s028gd.py <its analysis_gr_s028gd.json> B-20261126-022407-87e8803/analysis_gr_gd.json B-20261125-115558-2ab4161/analysis_gr_gd.json $NRPIC_RUN_DIR` (S2, S3 at the same stage a' = 2a; as-written a' = 4a beside) |
| B-20261126-022838-27fab1b | the 8-per-cell leg joined (cut run + continuation), t = 13-21.75, no halos | Q1 high-k part (Omega_cor above 16 k_f against the base after a = 50) with `compare_legs.py --leg p8u:<json>` |

If a run died, its run.log says so; rerun with fewer workers (the 256^3 one needs about 100 GB).

## Card run in the shared queue

| Queue id | Label | What | Read by |
|---|---|---|---|
| q0060 | pop_s014_gr256_gd | 256^3, one per cell, Gamma-driver shift (0.75, eta 1, advection 1), to t = 21.916, dumps and restarts every 1.0, v0.7 card exe and chain, ceiling 6 card-h, priority 2 | GM1-GM4 (population/JOURNAL 2026-11-25 18:50): `analyze_gr.py --equal-mass --times 2,4,...,21 --halo-times 14,...,21 --run m256gd:<dir>:0.014`, against the 128^3 gauge leg B-20261124-210431-6bf48af |

The queue never closes runs: `harness/bin/nrpic-run finish <run id>` when `nrpic-queue list` shows done.

## Established this session (run ids in population/JOURNAL.md)

- M1 refuted: 256^3 zero shift stops at a = 102 (K_max > 0 from a = 80); run closed as failed,
  3.23 card-h. M4 not judgeable at a = 141, fails at a = 36-100. Zero shift is not usable at
  finer meshes (R26).
- P8C1, P8C2, Q1 (constraint part), S1, N2e, GN1e hold. With equal masses the Gamma driver is
  the gauge closer to Newton; batch 21's GN1 refutation was the rest-mass weight (R25).
- Note section VI, fig_pop_gauge (b) and ledger updated (B-20261126-025137-7686b91), compiled;
  checker not rerun.

## Packages (what remains)

- population: the three analyses above; strain parts of A1-A3 and GD3 with equal masses; N4's
  radiated part at one cadence; a proper-distance halo mass (R23).
- shear: L2 not converged in the mesh (R19); an amplitude without stream crossing at N_y = 64,
  128, 256, 4 per cell, designed and predicted first.
- G2 products: C15 (split analyze_b.py, analyze_f.py, analyze_gr.py, analyze.py figures), C17
  (checker, abstract and summary after q0060; load /paper-writing), C18 (fresh verifier), a
  `nrpic-stage verify --full` once before the gate review.

Decisions pending: none with orch. Requests open: core (restart parameters, 20261125T121932Z;
Fourier solver threaded, 20261124T173601Z). Inbox: empty at the start of this session.

Traps:
- GR particle files carry the rest-mass weight in their masses (R25): use `--equal-mass`.
- FoF halo masses depend on the spatial gauge (R23): state the gauge with every mass.
- The 256^3 chain wrote dumps every 0.5 plus extra ones at segment ends: read times from headers.
- A restart accepts on the command line only parameters its stored input has (X3 failed so).
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; at most 6 cores; a
  full stage verify hashes hundreds of GB (the 256^3 run alone 292 GB).
