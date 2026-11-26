# stage/G2/verifier: fresh verifier of gate G2 (Track D, checklist item C17)

Batch 26 (2026-11-25 night), decision 0044 item 1. The report is `../VERIFIER.md`; the
predictions before every run and the outcomes after are in `JOURNAL.md`.

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | entries 0-6: sources read, criteria as fixed before the runs, predictions V1-V7, outcomes |
| `tools/vio.py` | own readers (docs/FORMATS.md): particle file, removal record (dedupe by last record per tag), finder summary (last record per time, failure signature: NaN or bit-identical repeat of columns 3-12), snapshot, trajectories, text histories |
| `tools/ltb.py` | exact reference: cycloid of shells with E = -M/R0 (crossing of R = 2m, radius at tau), mass inside a particle from the lattice (inclusive, half-weight) and from the evolved table (m = M + R^3 K_T^2/2, outside the throat) |
| `tools/v1_reference.py` | V1: closed-form tests, reference for the N, 4N, N/4 lattices |
| `tools/v2_null.py` | V2: criterion N at M/8, M/16, M/4; failure signature of 13 summaries |
| `tools/v3_growth.py` | V3, V5, V6a: criterion G ((iii), D2), D1, D3, D4, removal reasons, tracers' removal |
| `tools/v6_tracers.py` | V6b: tracer clock (alpha/W integral) and areal radius against the cycloid |
| `tools/v4_conv.py` | V4: particle-number and mesh convergence, shell norms |
| `tools/v7_checks.py` | V7: FF4's D2 past its control's end, +-25 M windows, P9, FK vs ES-FL, end mass |
| `tools/figstyle.py` | copy of python/nrpic/figstyle.py |

Outputs (json, npz, figures) are in `scratch/D-bh-dress/<run id>/`, run ids in `../VERIFIER.md`
section 7 and the manifests under `tracks/D-bh-dress/runs/`.

## How to rerun (processors, one core each, seconds to a minute)

    cd /data/haiyangw/nrpic/wt/D-bh-dress
    S=/data/haiyangw/nrpic/scratch/D-bh-dress
    V=tracks/D-bh-dress/stage/G2/verifier/tools
    R="harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --package tracks/D-bh-dress/stage/G2/verifier"
    $R --purpose "V1" -- python3 $V/v1_reference.py --data $S/D-20261121-203042-82deeec \
        --data4n $S/D-20261124-130942-29c5de2 --dataq $S/D-20261124-131050-ed0a535 --out '$NRPIC_RUN_DIR'
    $R --purpose "V2" -- python3 $V/v2_null.py --scratch $S --out '$NRPIC_RUN_DIR'
    $R --purpose "V3" -- python3 $V/v3_growth.py --scratch $S --ref $S/<V1 run> --out '$NRPIC_RUN_DIR'
    $R --purpose "V6b" -- python3 $V/v6_tracers.py --scratch $S --ref $S/<V1 run> --out '$NRPIC_RUN_DIR'
    $R --purpose "V4" -- python3 $V/v4_conv.py --scratch $S --out '$NRPIC_RUN_DIR'
    $R --purpose "V7" -- python3 $V/v7_checks.py --scratch $S --v3 $S/<V3 run> --out '$NRPIC_RUN_DIR'

Runs of record: V1 D-20261126-061848-ed8f297 (earlier D-20261126-061541-31e3b4e; failed
D-20261126-061734-6b49970, name clash; D-20261126-061754-1089797 with the throat defect of
the table reader), V2 D-20261126-062005-99c2399, V3 D-20261126-062152-b7144de, V6b
D-20261126-062436-72c04d3, V4 D-20261126-062609-bb28de7 and D-20261126-062637-6fbe1c9, V7
D-20261126-062830-e947a9a.

## Requests

- To the lead of D: (1) word the early removals (R28, the [TO VERIFY] of C8) as early arrival
  of the shells (evolution ahead of exact LTB by ~0.2 per cent of proper time at R0 = 28 M,
  converging with mesh and N; VERIFIER.md 4.1), not as removal outside the horizon; (2) the
  ledger row "M/4: D2 480 samples (all hold)" uses V-1L4 held constant after its end at 299 M:
  say so, or quote 280 samples to 299 M; (3) quote envelopes beside the single-sample
  convergence numbers (mesh difference up to 1.0e-3, mean +5.8e-4 over 250-299 M); (4) N at
  M/4 fails its pass condition by 16 per cent against its own floor and does not meet N's
  refutation clause: the "factor 20" is relative to M/8.
- To core: none required; for G3 the lattice point-counting noise in the mass inside a
  particle (0.44 M rms in crossing time at N) argues for comparing crossing times with the
  continuum reference only in bins.
