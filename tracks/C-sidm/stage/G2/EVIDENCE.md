# C-sidm G2: evidence (artefacts and run ids)

Paths relative to the worktree root `wt/C-sidm`. Manifests `tracks/C-sidm/runs/<run_id>/`;
outputs `scratch/C-sidm/<run_id>/` (untracked). G1 evidence: `../G1/EVIDENCE.md` (signed
2026-11-21, coord/GATES.md). Predictions of every card run below: `tracks/C-sidm/JOURNAL.md`
entry 2026-11-21T20:25Z (batch-5 queue) and 2026-11-24T13:14Z (batch-11 follow-ups);
outcomes: entries 2026-11-24T12:59Z (state, resume rule) and 13:12Z. Executable: release
core-v0.6 card build (`.work/build_gpu_v06/src/athena`) except run (v) (core-v0.3, so that it
differs from its partner only in N).

## Card runs of the batch-5 queue (package `tracks/C-sidm/longruns/`)

| Item | Run id | State on 2026-11-24 13:20Z | Read with |
|---|---|---|---|
| run (v), N = 1e4 on M/4 | C-20261121-202459-12183c5 | completed | C-20261124-130021-5c9c207 (compare), -130222-6a4924d (diffusion) |
| timing | C-20261121-203004-c2c14e7 | completed | C-20261124-131129-e93be29 |
| heat_C1, heat_C2 | C-20261121-210524-36a658e, C-20261122-183030-2f3a471 | completed | reductions C-20261124-130338-43b5ffa, -130338-c4ac85e; series C-20261124-131012-f920f45 |
| D2ctl, D2f2s1, D2f1s1, D2f4s1 | C-20261122-103854-4670b59, -141414-399ad97, -144455-6e0992e, -181011-60baef9 | completed (300 M) | C-20261124-130442-0819c88; recheck -132113-52c2abe |
| D2f2s2 | C-20261124-035054-c06503f | cut at 116.5 M by preemption; continuation queued | same reader |
| A334s1c, A334s1i, A334s1o | C-20261121-214601-40dc927, C-20261122-012719-b14e654, -065807-b302875 | completed (600 M) | C-20261124-130634-3338d9b; recheck -132113-52c2abe |
| A344s1c, A344s1i | C-20261122-213602-729aeed, -220118-ab099ac | completed | same |
| A344s1o | C-20261123-025228-6ecb543 | cut at 420.5 M; continuation queued | same |
| A324s1i | C-20261123-221955-a773578 | completed | same |
| A324s1c, A324s1o | C-20261123-032324-938ecbd, C-20261123-222003-02195a0 | cut at 19.5 and 407.8 M; continued (A324s1c running) | same |
| A334s2c/i/o, A334s3c/i | C-20261124-053105-2fcc8af, -061134-ab6cc0a, -075153-72499e7, -082221-7f03a8e, -091733-b92f4e5 | cut at 249, 245, 190, 0.25, 103.8 M; continuations queued | same |
| A334s3o | C-20261124-120250-9e6a3ba | running (segment cap raised to 24, restart every 10 M) | same |

## Batch-11 follow-ups (queued; predictions JOURNAL 2026-11-24T13:14Z)

| Item | Deck | Inputs made by |
|---|---|---|
| N6c, control of y0 = 0.334032 at N = 1e6 on M/8 | `longruns/inputs/A8N_y0p33403_N1e6_s1_ctrl.athinput` | C-20261124-130731-e1d24de (particles), -131231-74f067d (deck), smoke C-20261124-131249-b06c218 |
| N4c, the same at N = 1e4 | `longruns/inputs/A8N_y0p33403_N1e4_s1_ctrl.athinput` | C-20261124-130732-a383ef5, -131231-74f067d |
| M16, D2 on M/16 (collision cells M/4) | `longruns/inputs/D2M16_cc2_kn10_f4_s1.athinput` | -131231-74f067d, smoke -131249-b06c218 |

## Key numbers (each from the run named)

| Quantity | Value | Run |
|---|---|---|
| H-norm2 ratio N = 1e4 / 1e5 at t = 0, 100-300 M | 9.95, 9.97 | C-20261124-130021-5c9c207 |
| energy diffusion D ratio 1e4 / 1e5 (25-300 M, 25-75 M) | 11.07, 11.41 | C-20261124-130222-6a4924d |
| step time, collisionless / collisional M/8 deck | 8.29 / 8.53-8.57 s per M | C-20261124-131129-e93be29 |
| kappa/kappa_1 at zero cell, k lambda 0.2 and 0.1 | 1.0149 +- 0.0026, 1.0187 +- 0.0026 | C-20261124-131012-f920f45 |
| cell coefficient c of f = f0 + c (dx/lambda)^2, k lambda 0.2 and 0.1 | 0.101 +- 0.017, 0.055 +- 0.017 | same |
| t_c of CC2 at Kn = 10 on M/8, collision cells M/8, M/4, M/2 | 164.01, 163.41, 165.97 M | C-20261124-130442-0819c88 |
| collisions per particle before t_c (f = 1, 2, 4) | 2.23, 2.21, 2.19 | same |
| collision budget max summed dH / sum MH before excision | 2.8e-16, 3.0e-16, 3.2e-16 | same |
| D2 control alpha_c change 280-300 M | -0.0049 | same |
| block A t_c: 0.334032 ctrl / kin / kout | 534.8 / 294.5 / 449.0 M | C-20261124-130634-3338d9b |
| block A t_c: 0.344 ctrl / kin | 549.3 / 229.8 M | same |
| block A controls, alpha_c change at 400 M (0.334032, 0.344) | -0.0188, -0.0076 | same |
