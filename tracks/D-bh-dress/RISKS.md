# RISKS of D-bh-dress

Updated in the lead session of batch 4a (2026-11-21). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust and keeps its horizon mass. 1+log leaves the dust (ES-1). lapse_leak slices the dust on its exact curve (ES-1G) but makes the horizon mass grow late, with dust (+4.2e-3 by 188 M, ES-1GB) and in vacuum (+1.3e-3 by 200 M, V-1GB), not through the faces; the hole shrinks to 0.8-0.9 M in coordinates | dust part retired; hole part certain with lapse_leak | the null test with matter has no gauge yet that holds both the dust and the hole | core-v0.7 (decision 0022 item 3) | null test with 1+log (ES-1B against V-1B) until core's fix; then the lapse_leak pair again (g2runs/inputs) with an M/16 nest; request with the data: outbox lapse-leak-growth-data |
| R3 Floor of the null test in the ES set-up. Vacuum, 1+log, faces at +-384 M, M/8: 4.8e-5 over 100-200 M (V-1B). With lapse_leak the pair ES-1GB minus V-1GB reaches 3.5e-3 at 188 M (gauge at the hole, not the faces) | medium | a floor quoted for the wrong gauge or mesh | ES-1B against V-1B | quote the floor of the matched control of each G2 run, never one of another set-up |
| R13 Late horizon drift. In vacuum with 1+log it was the outer boundary (V-1 -1.37e-4 after 165 M; gone at +-384 M, V-1B). Under lapse_leak it is not the boundary: ES-1GB (+-384 M) equals ES-1G (+-192 M) to 4.2e-9 up to 188 M; the batch-2a reading is withdrawn. ES-1's (-3.4e-4, 1+log, dust) is untested with far faces | low for vacuum 1+log; certain for lapse_leak (R2) | a gauge or boundary effect read as coupling or accretion | ES-1B | every 200 M run with the faces at +-384 M (400 MeshBlocks, 0.78 card-hours at M/8 in vacuum); far faces protect the exterior mass (ES-1GB: Misner-Sharp mass 2.741 kept on R = 119-223 M) |
| R14 Lapse excision idle: the mesh minimum of the lapse is above alpha_exc = 0.05 near t = 6 and 15 M (1+log) and from t = 108 M on under lapse_leak (0.069 at 200 M) | certain | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8 with the finder on; request to core (outbox lapse-excision-criterion) |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) | medium | floor windows limited | none planned | V-1B makes a boundary cause plausible [JUDGEMENT]; D-pre-4 is not the floor of the null test (R3) |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools) is the first matter run into the hole, pre-registered (entry 7) |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R9 Cost of the G2 ladder beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks); the faces at +-384 M add 16 per cent (400 against 344 blocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (V-1B 0.778 card-hours for 200 M on 400 blocks); 29.22 card-hours left toward G2 |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr; orch brief check 2.87: 1903.01490 bounds |k| <= 5.0e-4) | medium | misleading wording | wording review | null test worded for ordinary black holes; design to reach |k| well below 5e-4 with the flux measured separately |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R17 ES-F (queued, Slurm 4806) has its faces at +-192 M (1+log); the boundary effect of V-1 there was 1.4e-4 over 100-200 M against a predicted growth of 0.1-0.25 M, and it runs on core-v0.4 instead of the pre-registered executable (g2runs JOURNAL entry 3) | low | criterion (iii) (1 per cent) marginally affected late | ES-F D1 closure | judge with the pre-registered criteria; if (iii) fails late, rerun with the faces at +-384 M before reading physics into it |
| R16 Shared worktree; sessions cut by usage limits leave runs unclosed and files uncommitted (2026-11-20: four runs, three tools, five figures) | certain | lost bookkeeping, index conflicts | git status and `nrpic-run status` at every session start | path-limited commits; close stale runs with `nrpic-run finish` after checking `.nrpic/result.json` |

Closed:
- R15 (G1 waited on the ruling d-pre-3-criterion): decision 0021 item 2 ruled; C7 judged on that wording with Q16 (batch 4a).
- R1 (release card executable mis-pushes massless tracers): an input convention, m = 0 is a null particle
  (D-20261115-172821-f800e34; core dfix-answers); ES-1 tracers (m = 1e-30) follow the exact curve to 2.2e-3.
- R7 (format-2 reader only on core/id-extrinsic): in release core-v0.3; ES-1/V-1 ran on it.
- R8 (outflow boundary not transparent for the Painleve-Gullstrand exterior): measured, it is (V-1 against
  V-1B); handled by placing the faces at +-384 M (R13) until core's faces option is benchmarked.
- R12 (mixed time zones in run ids): nrun.py uses UTC since 5259f48; nrpic-run writes UTC.
