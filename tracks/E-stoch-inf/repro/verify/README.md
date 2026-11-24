# repro/verify: fresh verifier of the reproduction of arXiv:2401.08530 and arXiv:2512.14649

Package of Track E (decision 0028, item 1, "verify"). Verdicts: `VERIFIER.md` (sections 1-7: first
pass; section 8: update pass on the five continued runs, 2026-11-24). Predictions and outcomes:
`JOURNAL.md` (entries 1 and 5 committed before any computation of their pass). No card time was used.

## Contents

| Path | What |
|---|---|
| `VERIFIER.md` | claims checked, how, verdicts (CONFIRMED / NOT CONFIRMED / WRONG), what could not be checked, the three weakest points |
| `JOURNAL.md` | predictions (entries 1, 5), outcomes (entries 2, 3, 4, 6) |
| `scripts/onepatch.py` | P0 one patch: background schemes, Ito and Stratonovich readings (50 000 paths), Ito-lemma Monte Carlo, appendix-D amplitude from my Mukhanov-Sasaki solutions |
| `scripts/onepatch_seeds.py` | seed spread of the two readings, clipped moments figure |
| `scripts/lattice.py` | my reader of the NRSFDMP2 dumps (self-test on analytic multi-block fields) and R^NR extraction, constraint statistics |
| `scripts/compare.py` | R^NR against my linear solution of the realisation (own background and MS integration, keys of the code via core's rng twin), lockstep record, records, slow roll |
| `scripts/records.py` | sign-flip pairs, convergence rungs (records and spectra), backreaction levels |
| `scripts/entrywin.py` | window sensitivity of the rungs' entry maxima |
| `scripts/background.py` | box means of the records against my Friedmann solution; one-point widths |
| `scripts/errata.py` | sympy rederivation of six misprints (E1, E3, E6, E7, E8, E10) |
| `scripts/cont.py` | update pass: joins of the continued runs (records, dumps, seams), SR sign flip over its full span, constraint ratios from the dumps against their magnitudes, Fig. 8 records 32-256, Fig. 7 at 256 against the lockstep record and my MS solution plus reference-free rung differences, level 2 against level 0 at N_f (SR, USR) under P1:520's 1e-4 |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |

Outputs (figures, JSON) are in the run directories `scratch/E-stoch-inf/<run_id>/` of the runs
listed in `VERIFIER.md` section 0; nothing from the papers is committed.

## How to rerun (processors, from the worktree root, through `harness/bin/nrpic-run submit
--package tracks/E-stoch-inf/repro/verify ...`)

```
python3 tracks/E-stoch-inf/repro/verify/scripts/onepatch.py --out "$NRPIC_RUN_DIR"          # ~1 min
python3 tracks/E-stoch-inf/repro/verify/scripts/onepatch_seeds.py --out "$NRPIC_RUN_DIR"    # ~1 min
python3 tracks/E-stoch-inf/repro/verify/scripts/errata.py --out "$NRPIC_RUN_DIR"
python3 tracks/E-stoch-inf/repro/verify/scripts/lattice.py run --tag sr --workers 3 --nmax2 4096 \
    --out "$NRPIC_RUN_DIR" --dumps scratch/E-stoch-inf/E-20261121-202935-31520bc/P256/sr.sf.000*.dump   # ~6 min
python3 tracks/E-stoch-inf/repro/verify/scripts/compare.py --case sr --lat <lattice run dir> \
    --deck scratch/E-stoch-inf/E-20261121-202935-31520bc/P256/sr_base.athinput \
    --modes tracks/E-stoch-inf/ladder/inputs/modes_n4096.txt --run <run dir> --out "$NRPIC_RUN_DIR"
# USR: dumps of E-20261123-021204-2f573ec, deck chain/input.athinput, modes usr/inputs/modes_usr_n4096.txt
python3 tracks/E-stoch-inf/repro/verify/scripts/records.py --out "$NRPIC_RUN_DIR"           # ~5 min
python3 tracks/E-stoch-inf/repro/verify/scripts/entrywin.py --out "$NRPIC_RUN_DIR"
python3 tracks/E-stoch-inf/repro/verify/scripts/background.py --out "$NRPIC_RUN_DIR" --latsr <dir> --latusr <dir>
```

Update pass (section 8; about 2 min for the records, 10 min for the dumps on 3 cores):

```
python3 tracks/E-stoch-inf/repro/verify/scripts/cont.py --only joins signflip convrec --out "$NRPIC_RUN_DIR"
python3 tracks/E-stoch-inf/repro/verify/scripts/cont.py --only signflip convspec backreact constraints \
    --workers 3 --out "$NRPIC_RUN_DIR"
```

RSF256's fourth continuation (q0034, E-20261124-214913-5956891) is already in `RUNS["RSF256"]`
(it ended during the pass; `--only joins signflip constraints`, run E-20261124-222800-49ab461).

Read 256^3 dumps sequentially (the reader seeks per variable); 3 cores and about 2 GB of memory
per dump.

## Requests

- To the lead of Track E (repro/note, repro/figs): state in the ledger the definition behind
  each number that `VERIFIER.md` section 4 lists as not confirmed (entry window of the rungs'
  constraint maxima, bins of the spectra, which linear reference, the 68 per cent band); repair
  the cut values of ledger rows 32, 77, 78; say in the note that the Ito skewness (1.04) and the
  alpha^3 -> 1 skewness (-0.96) were not reproduced by an independent integrator (1.116 +- 0.012,
  -0.74) and that the paper's flipped-sign H/[H] (~1e-5) is 100 times above ours.
- To the lead: the one-point amplitude factor against P1 Figs. 2 and 4 (3.5-4) remains the
  main open point; a check of P1 Fig. 2 against P1 Fig. 3 by Parseval (my reading: inconsistent
  by that factor) belongs in the note as [JUDGEMENT], or in a question to the authors (the
  group's step; nobody here contacts them).
- To the lead (update pass, VERIFIER.md section 8): P1:520 is per ten thousand (confirmed); my
  section-2 per-mille verdict is replaced by 8.5 (SR meets 1e-4; USR exceeds it in 24 per cent of the
  shells, mostly above abs(n) = 32). Name the window of row 48 (0.5 <= N <= ln 64; over the flipped
  run's full span the smallest ratio is 2.7e2 at N = 4.39) and the shell count of rows 77, 81, 82
  (more than 10 independent modes). State the definition behind rows 68-71 (256 member of Fig. 7):
  against the lockstep record and against my MS solution I get 2.0e-7 (not 3.7e-7), order 2.3-3.5
  (not 1.48), per-mode 3.3e-7 amplitude or 4.4e-7 power (not 6.7e-7). The floor itself holds and is
  now shown independent of dx, dt and the linear reference (8.3); the note may use that.
- To the lead (repro/figs, repro/note): RSF256 ended at 14:23 PST (q0034, run
  E-20261124-214913-5956891) and joins bit-exactly (VERIFIER.md 8.1, 8.6). Row 56 and the constraint
  panels of P1 Fig. 2 have no values yet; once the figs package fills them, a later verifier pass
  can check them against the dumps 17-34 (my reader handles them).
- None to core.
