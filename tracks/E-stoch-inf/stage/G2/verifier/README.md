# stage/G2/verifier: fresh verifier of gate G2 of Track E (USR case)

Helper package of owner E-stoch-inf, batch 14 (2026-11-24/25). Decision 0016 item 4 and
0035 item 1: a verifier who did not produce the G2 results recomputes, with own readers and
an own reference, the number each criterion of `../../../spec/scope/SCOPE.md` section 4c is
judged by, on the release ladder of package `g2prod`, and states per criterion CONFIRMED,
NOT CONFIRMED or WRONG. Processors only, no card time. The verdict text is
`../VERIFIER.md`; predictions and outcomes are in `JOURNAL.md`.

Not read before the numbers were computed: g2prod JOURNAL entries 2-4,
`stage/REVIEW-wave3.md`, `stage/G2/CHECKLIST.md` and the other files of `stage/G2/`.

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | entry 1: run table, interpretations fixed before any number, predictions V0-V14; later entries: outcomes |
| `scripts/vlib.py` | own reader of the NRSFDMP2 dumps (one variable at a time), record reader (rows deduplicated by cycle), hemisphere modes and coefficients on cell centres, R^NR extraction of TH appendix.tex:515-521 / P1 PRD_v2.tex:524-526 (including the gt_ij term), own background and continuum Mukhanov-Sasaki reference (DOP853, rtol 1e-12), alpha from the track's own Philox re-implementation `noise/ref/philox_ref.py`, the floor of 4c, the run table |
| `scripts/test_reader.py` | V0/V2: synthetic dump with known plane waves; floor formula on synthetic parts; alpha against core's twin |
| `scripts/reference.py` | V1: background, landmarks, modes at every dump time, lattice rms, comparison with `usr/results/usr_reference.json` and the lockstep `.modes` record |
| `scripts/records.py` | U-A0, U-A1, U-A4'(c) from the records of the 11 release runs |
| `scripts/modes_nf.py` | R^NR coefficients on the 548958 band modes at N_f of the 10 runs at 256^3/320^3 and at t = 0 of U256ap/bp (caches) |
| `scripts/judge_modes.py` | V3, U-A2', U-A2n, U-A3, U-R, U-S from the caches |
| `scripts/constraints.py` | U-A4'(a), (b), (d) and the three-amplitude reading of the halving (s = 1, 1/2, 1/4) |
| `scripts/window_check.py` | U-W from the window scan output |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `fig/` | the figures of the registered runs (copies), each looked at |
| `results/` | the JSON results of the registered runs (copies) |

## Registered runs

Listed with their outcome in `JOURNAL.md` and `../VERIFIER.md`; manifests in
`../../../runs/<run id>/manifest.json`, outputs in `scratch/E-stoch-inf/<run id>/`.

## How to rerun

From the worktree root, with the worktree's `.venv`; each line is one registered run
(`P=tracks/E-stoch-inf/stage/G2/verifier`):

    harness/bin/nrpic-run submit --kind production --gate G2 --preregistered $P/JOURNAL.md#entry-1 \
      --package $P --launcher local --cores 1 --purpose "..." -- bash -c \
      'cd tracks/E-stoch-inf/stage/G2/verifier/scripts && export OMP_NUM_THREADS=1 && python3 test_reader.py --out "$NRPIC_RUN_DIR"'
    # likewise: reference.py, records.py, constraints.py, window_check.py (1 core each);
    # modes_nf.py with --cores 2 and VERIFIER_FFT_WORKERS=2;
    # judge_modes.py --ref <reference run dir> --modes <modes_nf run dir> --out "$NRPIC_RUN_DIR"

Costs on anta (2026-11-25): reference 1.3 s of integration; records 1 min; modes_nf about 6
min; constraints about 12 min (I/O bound, 68 GB read sequentially); window 1 min.

## Requests

See `../VERIFIER.md` section "Requests" (none needs card time).
