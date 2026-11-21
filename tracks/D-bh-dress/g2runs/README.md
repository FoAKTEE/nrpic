# g2runs: first G2 runs of Track D (far faces with the relaxed lapse; dust-filled bubble)

Package of batch 3 of wave 3 (helper of D-bh-dress, 2026-11-21). Predictions before every
run and outcomes after it: `JOURNAL.md` (entries 1-3 predictions, outcomes appended).
Card cap of the package: 3 card-hours. Executables: release core-v0.4.

## Runs

| Run | What | Input | State |
|---|---|---|---|
| ES-1GB D-20261121-125900-ea4c442 (Slurm 4794) | ES-1G (lapse_leak 0.5) with the outer faces at +-384 M | `inputs/es1gb_bnd384.athinput` | submitted 04:59 PST |
| V-1GB D-20261121-125909-06f856e (Slurm 4795) | V-1B (faces +-384 M) with lapse_leak 0.5: vacuum control of ES-1GB | `inputs/v1gb_bnd384.athinput` | submitted 04:59 PST |
| ES-F | dust filling the bubble, faces +-192 M, plain 1+log, as pre-registered in flux_tools/JOURNAL.md entry 7 (executable: the release, entry 3 here) | `../flux_tools/inputs/esf_dx8.athinput` | to submit when a D slot frees |
| X1 D-20261121-125946-fe3840a | processors: core/gauge (ES-1G's executable) against release core-v0.4 on the ES-1G input, 12 cycles, byte comparison | ES-1G input | running |
| T1 D-20261121-130316-84a54d4 | `tools/compare_horizons.py` on ES-1G, V-1B, V-1 (reproduces the lead's numbers) | | done, held |
| T2 D-20261121-130605-ded836f, -130611-46aa59c | `tools/esf_criteria.py` on flux_tools' synthetic ES-F runs | | done (entry 3) |

## Contents

| Path | What |
|---|---|
| `tools/make_inputs.py` | builds `inputs/es1gb_bnd384.athinput` (ES-1G with the faces at +-384 M) and `inputs/v1gb_bnd384.athinput` (V-1B with lapse_leak) from the committed parents, asserting each replacement; `--check` compares with the files on disk |
| `tools/x1_exe_check.sh` | X1: runs one input with the core/gauge and the release processor executables and compares every output byte for byte |
| `tools/compare_horizons.py` | horizon mass, drift from 100 M, coordinate radius, pair differences; evaluates B1-B3, C1-C3 of entry 1; figure `compare_horizons.png` |
| `tools/esf_criteria.py` | ES-F: criterion (iii), diagnostics D1-D4 and the numbers of P1, P2, P5, P6 of flux_tools entry 7 (esf_analyse.py of flux_tools gives (i), (ii)); figure `esf_criteria.png` |
| `tools/figstyle.py` | copy of `harness/style/figstyle.py` |
| `inputs/` | the two inputs above |

## How to rerun

    cd /data/haiyangw/nrpic/wt/D-bh-dress
    python3 -I tracks/D-bh-dress/g2runs/tools/make_inputs.py --check
    # card runs (two D jobs at most in the queue)
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher chain --gpu-hours 1.1 \
      --package tracks/D-bh-dress/g2runs --exe /data/haiyangw/nrpic/.work/build_gpu_v04/src/athena \
      --purpose '...' -- tracks/D-bh-dress/g2runs/inputs/es1gb_bnd384.athinput
    # (v1gb_bnd384.athinput the same with --gpu-hours 0.95; ES-F: --gpu-hours 1.97 and
    #  tracks/D-bh-dress/flux_tools/inputs/esf_dx8.athinput)
    # analyses (S = /data/haiyangw/nrpic/scratch/D-bh-dress)
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
      --package tracks/D-bh-dress/g2runs --purpose '...' -- python3 \
      tracks/D-bh-dress/g2runs/tools/compare_horizons.py --out '$NRPIC_RUN_DIR' \
      ES-1G=$S/D-20261119-142633-6f72922:es V-1B=$S/D-20261120-222625-63abd72:v1b \
      ES-1GB=$S/<es1gb run>:es1gb V-1GB=$S/<v1gb run>:v1gb
    #   tools/esf_criteria.py --run $S/<esf run> --data $S/D-20261119-145022-2208a19 \
    #     --control $S/D-20261115-172730-c6d151b/v1.horizon_summary_0.txt --out '$NRPIC_RUN_DIR'

## Requests

None yet.
