# verify_g0: independent verifier of the G0 plan of F-hills

Helper package of F-hills, wave 3 round 1. The report is `../stage/G0/VERIFIER.md` (sections 1-3
written before the earlier reviews were read, section 4 after). Predictions and outcomes of every
check: `JOURNAL.md`. No card time; processors only.

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | claims list K1-K20 with predictions (entry 1), plan of the runs, outcomes, failed predictions |
| `scripts/vint.py` | own vectorised Dormand-Prince 5(4) integrator, one step size per trajectory |
| `scripts/restricted.py` | own restricted parabolic three-body problem of arXiv:0911.1136 (prp.tex:224-259, energy 353-357), compared phase by phase with the track's `coplanar.npz` |
| `scripts/threebody.py` | own Newton three-body problem and own HRNA of arXiv:2404.16270 (article.tex:246-261) in Cartesian Schwarzschild form; modes `selftest`, `passages` (the two input files), `scan` (pericentre scan, hand-off and GR-matched starts, `--mu-conv`), `s1` (2404's own set-up) |
| `scripts/closed_forms.py` | plunge bound, marginally bound orbit, Peters time, scales, start states of the inputs and their GR readings, cost from the mesh trees, 2406.11985 table |
| `scripts/kb_novelty.py` | own kb searches (12 queries, hybrid and BM25), corpus citation graph, INSPIRE metadata of the closest papers |
| `scripts/ledger_check.py` | every row of the note's ledger tables 1-2 recomputed from raw run outputs, my runs or the paper source; extras for K8, K14, K18 |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/` | the JSON and markdown summaries of the registered runs (copies; originals with checksums in `scratch/F-hills/<run id>/`) |
| `figures/` | the figures of the runs (copies), each read before it was relied on |

## Rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create --no-kokkos`),
each through `harness/bin/nrpic-run submit --kind scouting --gate G0 --package
tracks/F-hills/verify_g0 --cores 1 --purpose ... -- env OMP_NUM_THREADS=1 python <script> ...
--out '$NRPIC_RUN_DIR'`:

```text
scripts/closed_forms.py                                   # R1, seconds
scripts/threebody.py --mode selftest                      # R2, 30 s
scripts/threebody.py --mode passages                      # R3, 1 min
scripts/threebody.py --mode scan --nphase 180 --cases 10:3:7,10:3:8,10:3:12,10:3:13,4:5:9.82,4:5:16   # R4, long
scripts/restricted.py --nphase 3000                       # R5, 5 min
scripts/kb_novelty.py                                     # R6b, 3 min (2 cores)
scripts/threebody.py --mode s1 --betas 3,10 --nphase 200 --rtol 1e-11   # R7, long
scripts/threebody.py --mode scan --nphase 180 --cases 10:3:7,10:3:8 --mu-conv M   # R8, 1 min
scripts/ledger_check.py --mine R1=<run>,R3=<run>,R4=<run>,R5=<run>,R7=<run>   # R9, 1 min
```

Run ids of this package: `../stage/G0/VERIFIER.md`, section "Runs".

## Requests

To the F-hills lead (owner of SCOPING.md, the note and the errata row), the defects of
`../stage/G0/VERIFIER.md` section 3, with what section 4 added:
- D1: report the GR turning point next to every Newtonian r_p in SCOPING 3 and 6 (q = 10 turns at
  5.77 M with a bound CM in the puncture reading; q = 4 at 9.25 M).
- D2: the V7 numbers (HRNA plunge 0.94 / 0.69 / 0.30 at r_p = 8 / 12 / 13 M; Newton 0.22 at 13 M)
  hold for V7's construction (circular binary released at 4 r_t), not for the plan's start rule
  (state integrated from 10 r_t); near the edge they change by factors 2-10 with the construction
  (runs F-20261121-040103-6b9074c, -040112-d429b4c against -031920-5e6425e, -034434-0113a18). Use one
  start rule for NR and both references; re-quote or drop the 69 percent of errata row 1.5.
- D3: the G2 items sum to 131 card-hours (135 with m/16 at 44.8) before contingency, not "about 120".
- D4: SCOPING 3, 6, 9 still name q = 10 as the first passage (decision 0013).
- D5: 2700 is the slot limit of the input, not the card's capacity (about 3100 by the smoke's
  memory): test q = 4 m/16 (largest tree 2864) on one card with max_nmb_per_rank near 2950.
- D6: errata row 1.5's "needs a_b >= 29.5 r_gb at q = 20" is the condition for D <= 1 encounters
  outside the plunge radius, not for separation (outbox to orch).
- D7: note main.tex:140 ("small against the curvature radius throughout"): alpha reaches 0.2 at
  pericentre in the track's own S1 scan.
- D8: KHSR (1201.4794) is not reproduced; reproduce one result or record the item as dropped.
- D9, D10: precision and wording (ledger 0.9703 and 97.1; D = 0.1 retrograde closed by R5).

To kb: none (the INSPIRE forward-citation lists I lacked exist from the second check of wave 2).
To core: none.
