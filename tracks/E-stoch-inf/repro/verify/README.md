# repro/verify: fresh verifier of the reproduction of arXiv:2401.08530 and arXiv:2512.14649

Package of Track E (decision 0028, item 1, "verify"). Verdicts: `VERIFIER.md`. Predictions and
outcomes: `JOURNAL.md` (entry 1 committed before any computation). No card time was used.

## Contents

| Path | What |
|---|---|
| `VERIFIER.md` | claims checked, how, verdicts (CONFIRMED / NOT CONFIRMED / WRONG), what could not be checked, the three weakest points |
| `JOURNAL.md` | predictions (entry 1), outcomes (entries 2, 3) |
| `scripts/onepatch.py` | P0 one patch: background schemes, Ito and Stratonovich readings (50 000 paths), Ito-lemma Monte Carlo, appendix-D amplitude from my Mukhanov-Sasaki solutions |
| `scripts/onepatch_seeds.py` | seed spread of the two readings, clipped moments figure |
| `scripts/lattice.py` | my reader of the NRSFDMP2 dumps (self-test on analytic multi-block fields) and R^NR extraction, constraint statistics |
| `scripts/compare.py` | R^NR against my linear solution of the realisation (own background and MS integration, keys of the code via core's rng twin), lockstep record, records, slow roll |
| `scripts/records.py` | sign-flip pairs, convergence rungs (records and spectra), backreaction levels |
| `scripts/entrywin.py` | window sensitivity of the rungs' entry maxima |
| `scripts/background.py` | box means of the records against my Friedmann solution; one-point widths |
| `scripts/errata.py` | sympy rederivation of six misprints (E1, E3, E6, E7, E8, E10) |
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
- None to core.
