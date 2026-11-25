# Evidence of the G2 package of D-bh-dress (scouting; started 2026-11-22, batch 10a)

Paths relative to `tracks/D-bh-dress/`; manifests `runs/<run_id>/manifest.json`; outputs
`/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/`. Criteria, predictions and outcomes:
`g2long/JOURNAL.md` entries 1 (criteria N and G, fixed before the runs), 5 (outcomes), 6
(follow-ups), 8 (constraints). L marks figures the lead looked at. Executable of every card run:
release core-v0.6 (`.work/build_gpu_v06/src/athena`); plain 1+log, Gamma-driver shift, cfl 0.25,
no lapse_leak.

## Card runs (chains)

| Run | Input | Run id | Reached | Card-hours |
|---|---|---|---|---|
| V-1L vacuum control, faces +-768 M | `g2long/inputs/v1l.athinput` | D-20261121-203124-a34cf1f | 500 M | 2.24 |
| ES-1L vacuum-bubble null test | `g2long/inputs/es1l.athinput` | D-20261121-203131-8ee2a49 | 500 M | 2.49 |
| ES-FL dust-filled bubble | `g2long/inputs/esfl.athinput` (data D-20261121-203042-82deeec) | D-20261121-203150-15f2bad | 500 M | 2.60 |
| V-1L16 vacuum at M/16 | `g2long/inputs/v1l16.athinput` | D-20261121-203151-37e7b2d | 300 M | 3.00 |
| ES-1L16 null test at M/16 | `g2long/inputs/es1l16.athinput` | D-20261121-203151-59c54fb | 300 M (done) | 3.33 |
| V-1L4 vacuum at M/4 (FV4) | `g2long/inputs/v1l4.athinput` | D-20261123-022715-ab5d983 | 300 M (done) | 0.59 |
| ES-F (first matter run, faces +-192 M) | `g2runs/inputs` | D-20261121-144631-aa7ce9b | 200 M | 0.81 |

## Analyses

| What | Tool | Run | Figures |
|---|---|---|---|
| N, V1-V3, E1-E3, H1-H3 | `g2long/tools/judge_long.py` | D-20261123-020550-f9a3482 | judge_long.png (L) |
| ES-FL growth against removed and sphere flux | `flux_tools/esf_analyse.py` | D-20261123-020606-fa0046c | esf_growth.png (L), esf_bracket.png (L) |
| ES-FL criterion G ((iii) to tau 650 M, D1-D4) | `g2runs/tools/esf_criteria.py --tau_max 650` | D-20261123-020614-7ba5874 | esf_criteria.png (L) |
| Constraint volume norms of the five runs | `g2long/tools/constraints_long.py` | D-20261123-021027-e3af9b8 | constraints_long.png (L) |
| ES-F to 200 M (G1 batch 5) | `flux_tools/esf_analyse.py`, `g2runs/tools/esf_criteria.py` | D-20261121-202137-7bc388e, -202142-ce0f509 | see stage/REVIEW-wave3.md section 11 |

## Processor runs that G2 also uses

| What | Run | Judged in |
|---|---|---|
| Newtonian secondary infall, second resolution Q16-256 | D-20261121-205226-3cfbc20; analyses D-20261123-020626-183c254, -020756-e9922e7 | `secondary_infall/JOURNAL.md` 2026-11-23T02:08Z |
| Smoke tests of the follow-ups (M/4 members, excision kept) | D-20261123-020011-bd47394, -020531-6dbd75c, -020535-dccfd30, -020538-0290d15 | `g2long/JOURNAL.md` entry 9 |

## Added in batch 11 and 11b (2026-11-24; g2long entries 10-15)

| What | Tool | Run | Figures |
|---|---|---|---|
| R5 (H3, H4), FV4 (P1-P4): long-run judgement with R5 complete | `g2long/tools/judge_long.py` | D-20261124-131138-0b8ffc5 | judge_long.png (L) |
| Three vacuum meshes, null tests at M/8, M/16 | `g2long/tools/judge_conv.py` | D-20261124-131149-9f0166d | judge_conv.png (L) |
| Boundary and gauge members | `g2long/tools/boundary_gauge.py` | D-20261124-131657-89cd963 | boundary_gauge.png (L) |
| Exterior plane constraint norms (XC) | `g2long/tools/xc_plane.py` | D-20261124-134211-c6fce88 | xc_plane.png (L) |
| Slice mosaic of ES-FL at 500 M | `g2long/tools/slice_mosaic.py` | D-20261124-134644-2389227 | slice_mosaic_esfl_t500.png (L) |
| Finder re-search of dumps (FP, FP-ext; processors) | `g2long/tools/probe_long.py` | D-20261124-130935-fdca920, D-20261124-140606-286a302 | run logs |
| FP1-FP5, FP-ext judgement | `g2long/tools/fp_analyse.py` | D-20261124-172410-e8afc73, D-20261124-172508-c847ee4 (figure layout only) | fp_analyse.png (L) |
| Ladder schematic (C9) | `g2long/tools/schem_ladder.py` | D-20261124-172838-3a30e48, D-20261124-175505-a1053fa (after FE) | schem_ladder.png (L) |
| Early-dump finder re-search (FE) and its judgement | `g2long/tools/probe_long.py`, `g2long/tools/fe_analyse.py` | D-20261124-173137-f358715, D-20261124-175356-0f40f1a | fe_analyse.png (L) |
| 4N and N/4 dust data (D1); smoke tests S7, S8 | `flux_tools/esf_data.py`; release processor build | D-20261124-130942-29c5de2, -131050-ed0a535; -131123-05e5bfe, -131125-c928380 | entry 11 |

Card runs of the follow-ups (release core-v0.6, chains; continued in place by the shared queue since
2026-11-24, decision 0033):

| Run | Input | Run id | State (2026-11-25 04:25 PST) | Card-hours | Read by |
|---|---|---|---|---|---|
| FK ES-FLK (N; excision to 6.4 M) | `g2long/inputs/esflk.athinput` | D-20261123-022725-a553496 | 400 M, closed by hand | 2.70 | fk_compare D-20261125-115637-7ee26c1, esf_criteria D-20261125-115647-fd2f3f7 (L, L) |
| FF4 ES-FL4 (growth M/4) | `g2long/inputs/esfl4.athinput` | D-20261123-022727-1c17e73 | 500 M, closed | 1.34 | esf_criteria D-20261125-121034-8f82998 (control V-1L), D-20261125-121123-143a007 (control V-1L4, L) |
| FN4 ES-FLK4N (4N) | `g2long/inputs/esflk4n.athinput` | D-20261124-134157-b17938b | 400 M, closed by hand | 3.19 | np_partial D-20261125-115729-011d028 (L), esf_criteria D-20261125-122827-c5735f8, xc_plane D-20261125-122849-43db157 (L) |
| FNQ ES-FLKQ (N/4) | `g2long/inputs/esflkq.athinput` | D-20261124-172725-2f426b6 | running (q0010, job 5279), ~177 M at 04:11 | - | np_partial (partial, cut at 125 M) |
| FE4 ES-1L4 (null test M/4) | `g2long/inputs/es1l4.athinput` | D-20261123-022726-1b133af | 300 M, closed | 0.83 | judge_conv D-20261125-122227-3eb563a (L): P5 refuted |
| FL16 ES-FL16 (growth M/16) | `g2long/inputs/esfl16.athinput` | D-20261124-172745-72472ed | waiting (q0011) | - | L1-L5 |

Analysis tools added in batch 17: `g2long/tools/fk_compare.py`, `g2long/tools/np_partial.py`,
`g2long/tools/close_by_hand.py` (closes chain manifests with `continuations` through nrpic-run's own code).
