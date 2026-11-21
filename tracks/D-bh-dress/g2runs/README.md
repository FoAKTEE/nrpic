# g2runs: first G2 runs of Track D (far faces with the relaxed lapse; dust-filled bubble)

Package of batch 3 of wave 3 (helper of D-bh-dress). Predictions and outcomes:
`JOURNAL.md`. Status: runs submitted; results follow in this file.

## Contents

| Path | What |
|---|---|
| `tools/make_inputs.py` | builds `inputs/es1gb_bnd384.athinput` (ES-1G with the faces at +-384 M) and `inputs/v1gb_bnd384.athinput` (V-1B with lapse_leak) from the committed parents; `--check` compares with the files on disk |
| `inputs/` | the two inputs above |

## How to rerun

    cd /data/haiyangw/nrpic/wt/D-bh-dress
    python3 -I tracks/D-bh-dress/g2runs/tools/make_inputs.py --check
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher chain --gpu-hours 1.1 \
      --package tracks/D-bh-dress/g2runs --exe /data/haiyangw/nrpic/.work/build_gpu_v04/src/athena \
      --purpose '...' -- tracks/D-bh-dress/g2runs/inputs/es1gb_bnd384.athinput

## Requests

None yet.
