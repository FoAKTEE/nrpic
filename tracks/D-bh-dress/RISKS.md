# RISKS of D-bh-dress

Updated in the lead session of batch 2a (2026-11-21). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust. 1+log leaves the dust (ES-1). core's lapse_leak (ES-1G, D-20261119-142633-6f72922) slices the dust on its exact curve (wall within 1.7e-4, dust lapse within 1.3e-2 of the model) but at the hole the horizon shrinks to 0.78 M (6.2 cells of M/8) and its mass grows by +7.0e-3 over 100-200 M | dust part retired by ES-1G; hole part open | the null test with matter has no gauge yet that holds both the dust and the hole | ES-1G with the faces at +-384 M; V-1G; M/16 nest | lapse_leak for G2 runs only with the faces at +-384 M, an M/16 nest and a matched V-1G control (es_runs README "Gauge for the null test"); question to core (outbox es1g-outcome-for-gauge-ready) |
| R3 Floor of the null test in the ES set-up. Now measured in vacuum: V-1B (faces at +-384 M, M/8, 1+log) within 4.8e-5 over 100-200 M (D-20261120-222625-63abd72); with dust and lapse_leak not measured | medium | a floor quoted for the wrong gauge or mesh | V-1G with the faces at +-384 M | quote the floor of the matched control of each G2 run, never one of another set-up |
| R13 Late horizon drift. V-1's (-1.37e-4 after 165 M) is the outer boundary at +-192 M: gone with the faces at +-384 M (V-1B, lead Z3). ES-1's (-3.4e-4) and ES-1G's (+7.0e-3, with the exterior mass lost from the faces inward, es_runs K1) are likely the same, not tested | low for vacuum, medium with dust | a boundary effect read as coupling or accretion | ES-1GB (ES-1G with faces at +-384 M) | every 200 M run with the faces at +-384 M (400 MeshBlocks, 0.78 card-hours at M/8 in vacuum); core's faces option benchmarked on V-1 (outbox boundary-benchmark-v1b) |
| R14 Lapse excision idle: the mesh minimum of the lapse is above alpha_exc = 0.05 near t = 6 and 15 M (1+log) and from t = 108 M on under lapse_leak (0.069 at 200 M) | certain | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8 with the finder on; request to core (outbox lapse-excision-criterion) |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) | medium | floor windows limited | none planned | V-1B makes a boundary cause plausible [JUDGEMENT]; D-pre-4 is not the floor of the null test (R3) |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools) is the first matter run into the hole, pre-registered (entry 7) |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R9 Cost of the G2 ladder beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks); the faces at +-384 M add 16 per cent (400 against 344 blocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (V-1B 0.778 card-hours for 200 M on 400 blocks); 29.22 card-hours left toward G2 |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr; orch brief check 2.87: 1903.01490 bounds |k| <= 5.0e-4) | medium | misleading wording | wording review | null test worded for ordinary black holes; design to reach |k| well below 5e-4 with the flux measured separately |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R15 G1 waits on orch's ruling `d-pre-3-criterion` (asked 2026-11-15, 11-19, 11-21) | certain | G1 not reviewable | coord/REQUESTS.md | if the wording stays: secondary_infall's run to a/a_i = 30 on processors (0.4-0.8 h); even then -9/4 is not reachable (profile resolved only to lambda ~ 0.06) |
| R16 Shared worktree; sessions cut by usage limits leave runs unclosed and files uncommitted (2026-11-20: four runs, three tools, five figures) | certain | lost bookkeeping, index conflicts | git status and `nrpic-run status` at every session start | path-limited commits; close stale runs with `nrpic-run finish` after checking `.nrpic/result.json` |

Closed:
- R1 (release card executable mis-pushes massless tracers): an input convention, m = 0 is a null particle
  (D-20261115-172821-f800e34; core dfix-answers); ES-1 tracers (m = 1e-30) follow the exact curve to 2.2e-3.
- R7 (format-2 reader only on core/id-extrinsic): in release core-v0.3; ES-1/V-1 ran on it.
- R8 (outflow boundary not transparent for the Painleve-Gullstrand exterior): measured, it is (V-1 against
  V-1B); handled by placing the faces at +-384 M (R13) until core's faces option is benchmarked.
- R12 (mixed time zones in run ids): nrun.py uses UTC since 5259f48; nrpic-run writes UTC.
