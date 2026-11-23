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
| ES-1L16 null test at M/16 | `g2long/inputs/es1l16.athinput` | D-20261121-203151-59c54fb | 225.6 M of 300 (running, job 4920) | 2.51 so far |
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
