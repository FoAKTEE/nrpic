# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 21, wave 3, 2026-11-25
08:56-09:30 PST, processors only: the Newtonian reference compared with both GR gauges; G2
writing without a card). Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md has
each missing item with the queue entry or processor work that serves it). Three card runs wait in
the shared queue (cards held by another partition until about 2026-11-26, decision 0041 item 6).
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-queue list --owner B-emd-gw && harness/bin/nrpic-run status | grep -E "submitted|running"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/REVIEW-wave3.md` (section "Batch
21"); `population/JOURNAL.md` (entries 2026-11-25 08:58 to 09:24: predictions and outcomes of
N2-N4, GN1-GN2, NB1, VC1-VC2, the radiated part of N4).

## Card runs in the shared queue (read nothing partial)

| Queue id | Label | Run id (Slurm) | What | Read by |
|---|---|---|---|---|
| q0007 | pop_s014_gr256 | B-20261125-093500-242d3a3 (5278 done, 5283 pending) | mesh leg: 256^3, one per cell, zero shift, v0.6 chain, ceiling 5 card-h (segment 1 reached t = 4.52 of 21.916); if the cap ends it short, continue as q0042 does (batch restart of its newest rst into a new run) | M1-M4 (population/JOURNAL 2026-11-24 06:10): `analyze_gr.py --run m256:<dir>:0.014`, then `compare_legs.py --leg m256:<json>` |
| q0042 | pop_s014_gr_p8_cont | waiting | batch restart of rst/pop.00008.rst (t = 16) of the cut particle leg B-20261124-223926-33194d9 to t = 21.916, list `population/inputs/batch_p8cont.list`, v0.6 card exe, 0.5 card-h | P8C1-2 (2026-11-25 04:00 entry); then Q1 at a = 141 with the cut run's snapshots to t = 17 and the continuation's after (symlinks in a new analysis run directory) |
| q0044 | pop_s028_gd2 (after q0042) | waiting | batch restart of rst/pop.00004.rst (t = 8) of B-20261123-035002-bcc82bd with the Gamma-driver shift of X2 to t = 21.916, list `population/inputs/batch_s028gd.list`, 0.5 card-h | S1-S3 (04:00 entry): `analyze_gr.py --run s028gd:<dir>/s028_gd:0.028`; S2, S3 against B-20261125-115558-2ab4161/analysis_gr_gd.json at a' = 4a |

The queue never closes runs: `harness/bin/nrpic-run finish <run id>` when `nrpic-queue list`
shows done. Nothing runs on processors for this owner.

## Established this session (run ids in population/JOURNAL.md)

- Newtonian analysis B-20261125-122434-060d53d closed. N2 and N3 hold in both gauges
  (B-20261125-165836-70b17b6 zero shift, -165845-0621554 Gamma driver).
- N4 fails in both parts. Quasi-static part: `analyze_gr.py` `hqs_particles` deposits the GR file's
  rest-mass weight as mass (VC2, B-20261125-170535-84c9ba5). Radiated part: 0.29 against a
  factor 2 (B-20261125-172136-3e920ab), cause not tested.
- GN1 refuted: zero shift gives the masses closer to Newton; the "bracket" statement is withdrawn.
- Note: section VI with fig_pop_gauge, schem_architecture_g2, schem_timeline_g2, ledger Table VIII
  (registered run B-20261125-171148-563a6f0; compiled, checker clean on the new text, pages read).
- stage/G2/REPRODUCE.md (C6). Stage verify --no-checksums: all PASS except 'runs' (q0007 in flight).

## Packages (what remains)

- population: (1) add an equal-mass option to `analyze_gr.py` `hqs_particles` (or divide by the
  weight), write a prediction, rerun it on B-20261123-014847-f295ab4 and B-20261124-210431-6bf48af
  (about an hour on 2 cores), then redo A1-A3 and GD3's particle numbers; (2) the radiated part of
  N4 at one snapshot cadence (re-analyse fidL8 at the 128^3 cadence or the reverse); (3) a
  proper-distance FoF or mass for R23; (4) Q1, S1-S3, M1-M4 when the queue runs end.
- shear: L2 not converged in the mesh (R19); next an amplitude between M2 and L2 without stream
  crossing before t_A at N_y = 64, 128, 256, 4 per cell, prediction first.
- G2 products: C15 (split analyze_b.py, analyze_f.py, analyze_gr.py, analyze.py figures into one
  script each), C17 (C1-C3 results, abstract and summary after the runs; load /paper-writing),
  C18 (fresh verifier on ledger Table VIII and the G2 numbers), the gauge at a second mesh (needs a
  decision: 256^3 shifted, of the size of the mesh leg), a checksum pass of stage verify (`--full`
  once, before the gate review).

Decisions pending: none with orch. Requests open: core (restart parameters, 20261125T121932Z;
Fourier solver threaded, 20261124T173601Z). Posted this session: to all, GR particle mass weight
(20261125T172252Z, info). Inbox: three messages acknowledged (kb claims batch 17: claim 883
applied in scope/REFERENCES.md; orch checksum cache; orch horizon summary, not used by this track).

Traps:
- GR particle files carry the rest-mass weight in their masses (R25): Newtonian estimators deposit
  equal masses.
- FoF halo masses depend on the spatial gauge (R23): state the gauge with every mass.
- A restart accepts on the command line only parameters its stored input has (X3 failed so).
- v0.6 chains count a SIGTERM-cut attempt as a segment; new chains: v0.7 executable and script;
  continuations of v0.6 restart files: v0.6 executable through batch restarts.
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; never sbatch or the
  scripts; temporary files under `scratch/B-emd-gw/tmp/`. A full stage verify hashes tens of GB:
  use `--no-checksums` inside a short session.
