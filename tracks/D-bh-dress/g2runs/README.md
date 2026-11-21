# g2runs: first G2 runs of Track D (far faces with the relaxed lapse; dust-filled bubble)

Package of batch 3 of wave 3 (helper of D-bh-dress, 2026-11-21). Predictions before every
run and outcomes after it: `JOURNAL.md` (entries 1-3 predictions, outcomes appended).
Card cap of the package: 3 card-hours. Executables: release core-v0.4.

## Results (JOURNAL entries 5, 6; every number with its run id there)

**ES-1G's late horizon growth is not the outer boundary.** ES-1GB (ES-1G with the faces
moved from +-192 M to +-384 M) gives the horizon mass of ES-1G to 2.9e-15 up to t = 90 M
and to 4.2e-9 up to t = 188 M (run D-20261121-144657-cf510fc); its drift from 100 M is
ES-1G's to the last digit ([-4.17e-4, +9.47e-4] on 100-165 M, +4.16e-3 at 188 M), while
the exterior keeps its mass (Misner-Sharp m = 2.7406-2.7414 on R = 119-223 M at 188 M,
run D-20261121-142005-52adf6d; ES-1G had lost it from the faces inward). The extra slice
mass at 188 M sits at the hole (m = 1.0054 at R ~ 2 M falling to 1.002 at R ~ 40 M).

**The relaxed lapse produces it, and the dust makes it larger.** The matched vacuum control
V-1GB (V-1B with lapse_leak, faces +-384 M) also shrinks its horizon in coordinates (1.40 ->
0.875 M; V-1B with plain 1+log grows to 2.20 M) and grows late: drift [-5.6e-4, +1.27e-3]
on 100-199.5 M, against [-4.8e-5, +2.0e-5] for V-1B. The null test ES-1GB minus V-1GB is
at rounding to t ~ 12 M, below 1e-4 to 90 M, above 2e-4 from 137.5 M and 3.5e-3 at 188 M.
[JUDGEMENT] The growth is the gauge and resolution at a hole that the relaxed lapse makes
small (6-7 cells of M/8 by 200 M), faster with the dust outside the bubble; an M/16 nest of
ES-1GB and V-1GB would test this (not run).
On the axis (run D-20261121-145907-f76095b, entry 7) the relaxed lapse keeps the lapse
near 1 outside the hole (V-1B: up to 1.43), raises it at the hole (0.43 against 0.19 at
x = 1 M, t = 180 M), weakens the outward shift there (0.16 against 0.39) and lets the
conformal factor chi of the bubble fall (x = 5 M: 0.68 -> 0.49 from 50 to 180 M; V-1B
0.87 -> 1.02); with the dust chi falls faster (x = 20 M: 0.35 against 0.45 at 180 M).

| Prediction (entry 1, 4) | Outcome | Verdict |
|---|---|---|
| B1 ES-1GB drift within [-6e-4, +1e-3], refuted if D(199.5) >= 3.5e-3 | D(188) = +4.16e-3 (ES-1G's curve) | REFUTED (growth not from the boundary) |
| B2 ES-1GB = ES-1G within 5e-5 to 90 M; separation > 2e-4 after 130 M | 2.9e-15 to 90 M; never above 4.2e-9 | first part HELD; the separation HB expected did not come |
| B3 radius 0.78 +- 0.05 M at 199.5 M | 0.795 M at 188 M (ES-1G 0.776 at 199.5) | pending the last segment |
| B4' exterior mass kept; bubble M_H within 1.0005-1.0030 | m_inf 2.7397, 2.7398 at 50, 100 M; 2.741 on R 119-223 M at 188 M; M_H 1.00136 (150 M), 1.00539 (188 M) | (a), (b) HELD; (c) FAILED at 188 M |
| B5 finite, 28 tracers removed, 400 MeshBlocks, 0.92 card-h | finite, 28, none escaped, 400; segment 1 0.83 card-h | pending the last segment |
| C1 V-1GB drift within [-6e-4, +1e-3] | [-5.6e-4, +1.265e-3] | FAILED |
| C2 null test ES-1GB - V-1GB <= 2.5e-4 on 30-199.5 M | 1e-4 to 90 M, 3.5e-3 at 188 M | REFUTED |
| C3 V-1GB radius 0.78 +- 0.08 M, M(100) - 1 = (1.1 +- 0.2)e-3 | 0.875 M; 1.186e-3 | radius FAILED, mass HELD |
| C4 V-1GB 0.78 card-h, finite | 0.781 card-h, finite, 28 removed | HELD |
| X1 release = core/gauge bytes on processors | identical except the two documented corrections | HELD |

## Runs

| Run | What | Input | State |
|---|---|---|---|
| ES-1GB D-20261121-125900-ea4c442 (Slurm 4794, 4805) | ES-1G (lapse_leak 0.5) with the outer faces at +-384 M | `inputs/es1gb_bnd384.athinput` | segment 1 to t = 188 M (0.83 card-h); segment 2 (188-200 M) queued |
| V-1GB D-20261121-125909-06f856e (Slurm 4795) | V-1B (faces +-384 M) with lapse_leak 0.5: vacuum control of ES-1GB | `inputs/v1gb_bnd384.athinput` | done, 0.781 card-h, closed |
| ES-F D-20261121-144631-aa7ce9b (Slurm 4806) | dust filling the bubble, faces +-192 M, plain 1+log, as pre-registered in flux_tools/JOURNAL.md entry 7 (executable: the release, entry 3 here) | `../flux_tools/inputs/esf_dx8.athinput` | queued 06:46 PST |
| X1 D-20261121-125946-fe3840a, -141529-2664b51 | processors: core/gauge (ES-1G's executable) against release core-v0.4 on the ES-1G input, 12 cycles, byte comparison and its locator | ES-1G input | done, held |
| T1 D-20261121-130316-84a54d4 | `tools/compare_horizons.py` on ES-1G, V-1B, V-1 (reproduces the lead's numbers) | | done, held |
| T2 D-20261121-130605-ded836f, -130611-46aa59c | `tools/esf_criteria.py` on flux_tools' synthetic ES-F runs | | done (entry 3) |
| D-20261121-141419-b9f1089 | ES-1GB segment 1 against ES-1G, V-1B, V-1 | | done (entry 5) |
| D-20261121-142005-52adf6d | slice mass of ES-1GB (t = 0-188 M) | | done (entry 5, B4') |
| D-20261121-144657-cf510fc | ES-1G, ES-1GB, V-1B, V-1GB together | | done (entry 6) |
| D-20261121-145907-f76095b | lapse, shift, chi on the axis of V-1B, V-1GB, ES-1GB (`tools/axis_profiles.py`) | | done (entry 7) |
| D-20261121-150025-05937b2 | slice mass of V-1GB (t = 0-200 M) | | done (entry 8): the late growth is in the slice at the hole in vacuum too (M_H 1.00266 at 200 M, finder 1.00245) |

## Contents

| Path | What |
|---|---|
| `tools/make_inputs.py` | builds `inputs/es1gb_bnd384.athinput` (ES-1G with the faces at +-384 M) and `inputs/v1gb_bnd384.athinput` (V-1B with lapse_leak) from the committed parents, asserting each replacement; `--check` compares with the files on disk |
| `tools/x1_exe_check.sh` | X1: runs one input with the core/gauge and the release processor executables and compares every output byte for byte |
| `tools/compare_horizons.py` | horizon mass, drift from 100 M, coordinate radius, pair differences; evaluates B1-B3, C1-C3 of entry 1; figure `compare_horizons.png` |
| `tools/esf_criteria.py` | ES-F: criterion (iii), diagnostics D1-D4 and the numbers of P1, P2, P5, P6 of flux_tools entry 7 (esf_analyse.py of flux_tools gives (i), (ii)); figure `esf_criteria.png` |
| `tools/axis_profiles.py` | lapse, radial shift and chi on the +x axis of the z4c slices, finest level at each x; figure `axis_profiles.png` |
| `tools/x1_locate.py` | X1 follow-up: where two outputs differ (header lines or data) |
| `tools/finish_g2.sh` | `es1gb` or `esf`: closes the card run once its chain is DONE and starts its registered analyses (compare_horizons and slicemass; esf_analyse and esf_criteria). Guards tested (exit 2 while QUEUED) |
| `tools/figstyle.py` | copy of `harness/style/figstyle.py` |
| `inputs/` | the two inputs above |

## Pending (state at the end of this session)

- ES-1GB segment 2 (t = 188 -> 200 M, Slurm 4805) and ES-F (Slurm 4806) are queued behind
  jobs of other owners. When a chain's `STATUS` is DONE:
  `tracks/D-bh-dress/g2runs/tools/finish_g2.sh es1gb` (or `esf`), look at the figures, and
  write the outcomes of B1, B3, B5 (ES-1GB) and of P1-P7, (i)-(iii), D1-D4 (ES-F,
  flux_tools/JOURNAL.md entry 7) into JOURNAL.md.

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

1. D-bh-dress lead: the reading "ES-1G's late growth comes through the outer boundary"
   (stage/REVIEW-wave3.md sections 1 and 3, HANDOFF.md, STATUS.md) is refuted by ES-1GB
   (entry 5): the faces cost the exterior its mass but not the hole. The G2 null-test floor
   with lapse_leak at M/8 is set by the gauge at the hole (3.5e-3 over 100-188 M between
   ES-1GB and V-1GB), not by the faces. Next card runs that would decide the cause: ES-1GB
   and V-1GB with an M/16 nest (does the growth fall with resolution?).
2. core (cosmo_gauge.md section 7.3, a puncture inside expanding dust): with
   `lapse_leak = 0.5` the horizon of a vacuum-bubble puncture shrinks in coordinates to
   0.88 M (vacuum) and 0.78 M (dust outside the bubble) by t = 200 M, where plain 1+log
   keeps it at 2.2 M, and the horizon mass then grows late (V-1GB +1.27e-3, ES-1GB
   +4.2e-3 by 188 M; V-1B within 5e-5). The option acts only where alpha > alpha_0, so the
   shrinking comes through the lapse and shift profile of the bubble. Requested: a
   reading of the mechanism and a variant that keeps the trumpet size (or the resolution
   it needs); inputs and outputs of the three runs are listed above. What the axis slices
   show (entry 7): under lapse_leak the conformal factor chi of the bubble falls by ~30 per
   cent from 50 to 180 M and the Gamma-driver shift at the hole drops from 0.25 to 0.16
   (plain 1+log: chi ~ 1, shift ~ 0.4).
