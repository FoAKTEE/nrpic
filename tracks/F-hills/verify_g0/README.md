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

- To the F-hills lead (owner of SCOPING.md, the note, the errata row): the defects of
  VERIFIER.md section 3: D1 GR pericentre of the start states not reported (q = 10 turns at
  5.77 M, CM bound in the puncture reading); D2 SCOPING still names q = 10 as the first passage
  against decision 0013; D3 G2 compute items sum to 131 card-hours before contingency, not
  "about 120"; D4 the "2700 slots of one card" is the input's slot limit, not the card's
  capacity (about 3000-3100 by the smoke's measured memory), so the q = 4 m/16 tree may fit one
  card; D5 the plunge-bound correction of brief l. 275 states a condition for D <= 1 encounters,
  not for separation; D6 the note's "the binary stays small against the curvature radius
  throughout" (main.tex:140) is contradicted by the track's own S1 scan (alpha up to 0.2 at
  pericentre); D7 KHSR (1201.4794) is not reproduced although the track sheet asks for it;
  D8 the V7 diagnostic "member inside 4 M" was not reproduced by my independent scan (0.49 and
  0.011 against 0.62 and 0.056 at r_p = 7, 8 M); the construction of the V7 start states should
  be written down.
- To kb: an INSPIRE `refersto:` listing of the papers citing 2406.11985, 2505.03934, 2404.16270
  and 2402.02178 (no citing lists are stored; my novelty check used the corpus graph only).
- To core: none.
