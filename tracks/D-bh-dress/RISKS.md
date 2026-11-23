# RISKS of D-bh-dress

Updated in the lead session of batch 10a (2026-11-22). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust and keeps its horizon mass under lapse_leak (late growth, decision 0025 item 3: mitigation in v0.7, cure later). 1+log leaves the dust off its exact curve (ES-1) but keeps the hole | certain for lapse_leak | the null test runs with 1+log only | core's cure after the usage reset | all G2 runs plain 1+log (g2long); lapse_leak runs wait for the cure |
| R3 Floor of the null test. Vacuum, 1+log, faces +-768 M: F_V(500) = 1.25e-4 at M/8 (V-1L), 1.34e-4 to 300 M at M/16 (V-1L16), set by a step of +1.2e-4 at 240-300 M that both resolutions show alike (not set at the horizon; cause unknown) | certain (measured) | N holds with a 9 per cent margin only; a floor quoted without its cause | M/4 member FV4 (entry 6 P3) | quote the matched control of each run; find the step's origin before G3 (a run that can fail: faces at +-1536 M, or another mesh layout) |
| R13 Late horizon drift. In vacuum with 1+log it was the outer boundary (V-1 -1.37e-4 after 165 M; gone at +-384 M, V-1B). Under lapse_leak it is not the boundary: ES-1GB (+-384 M) equals ES-1G (+-192 M) to 4.2e-9 up to 188 M; the batch-2a reading is withdrawn. ES-1's (-3.4e-4, 1+log, dust) is untested with far faces | low for vacuum 1+log; certain for lapse_leak (R2) | a gauge or boundary effect read as coupling or accretion | ES-1B | every 200 M run with the faces at +-384 M (400 MeshBlocks, 0.78 card-hours at M/8 in vacuum); far faces protect the exterior mass (ES-1GB: Misner-Sharp mass 2.741 kept on R = 119-223 M) |
| R14 Lapse excision idle: the mesh minimum of the lapse is above alpha_exc = 0.05 near t = 6 and 15 M (1+log) and from t = 108 M on under lapse_leak (0.069 at 200 M) | certain | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8 with the finder on; request to core (outbox lapse-excision-criterion) |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) | medium | floor windows limited | none planned | V-1B makes a boundary cause plausible [JUDGEMENT]; D-pre-4 is not the floor of the null test (R3) |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools) is the first matter run into the hole, pre-registered (entry 7) |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R9 Cost of the G2 ladder beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks); the faces at +-384 M add 16 per cent (400 against 344 blocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (V-1B 0.778 card-hours for 200 M on 400 blocks); 29.22 card-hours left toward G2 |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr; orch brief check 2.87: 1903.01490 bounds |k| <= 5.0e-4) | medium | misleading wording | wording review | null test worded for ordinary black holes; design to reach |k| well below 5e-4 with the flux measured separately |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R16 Shared worktree; sessions cut by usage limits leave runs unclosed and files uncommitted (2026-11-20: four runs, three tools, five figures) | certain | lost bookkeeping, index conflicts | git status and `nrpic-run status` at every session start | path-limited commits; close stale runs with `nrpic-run finish` after checking `.nrpic/result.json` |
| R18 Long runs: the finder kept ES-FL's horizon to 500 M (radius 5.30 M); the queue and the sequencer worked (R1-R4 done, R5 at 225.6 M) | low now | runs late | horizon_summary gaps; `$S/g2long_seq/log` | sequencer restarted for the follow-ups (HANDOFF) |
| R19 Set-up data that do not cover a larger mesh (ES-F table to 345 M, exterior = zero, found by smoke S2) | was certain, fixed for ES-FL | constraint jump inside the domain | smoke runs before every new mesh; the table header line | data maker `--rbar_max`; HANDOFF trap 14 |
| R20 Horizon excision ends when the horizon's smallest radius passes 4 x initial_radius (nrpic.cpp:451-455): in ES-FL at 219 M; afterwards removal by the lapse rule, deeper and later, leaving steps in (iii), D3 and the closure | certain for growing holes | growth criteria biased by the removal time (+0.35 per cent in (iii)) | removal reasons in removed.bin | initial_radius_0 = 1.6 (ES-FLK, entry 6); core request ah-excision-growth-guard |
| R21 The z4c history norms skip chi < 0.0625 and measure the inside of the horizon (M/16 100x below M/8; ES-FL steps) | certain | 'constraints behave' not shown for the exterior | constraints_long.png | `<particles> region_*` outside the horizon in the next inputs |
| R22 The finder mass changes sign between M/8 (+9e-4) and M/16 (-2.5e-4): two members give no order | certain | no convergence statement for M_AH | FV4 P2 | three members (M/4 queued); if M/4 is outside the convergent regime, M/32 on +-3 M (~13 card-hours per run) |

Closed:
- R17 (ES-F's faces at +-192 M and executable): ES-F met every criterion except one early finder sample (g2runs entry 10); ES-FL repeats it at +-768 M.
- R15 (G1 waited on the ruling d-pre-3-criterion): decision 0021 item 2 ruled; C7 judged on that wording with Q16 (batch 4a).
- R1 (release card executable mis-pushes massless tracers): an input convention, m = 0 is a null particle
  (D-20261115-172821-f800e34; core dfix-answers); ES-1 tracers (m = 1e-30) follow the exact curve to 2.2e-3.
- R7 (format-2 reader only on core/id-extrinsic): in release core-v0.3; ES-1/V-1 ran on it.
- R8 (outflow boundary not transparent for the Painleve-Gullstrand exterior): measured, it is (V-1 against
  V-1B); handled by placing the faces at +-384 M (R13) until core's faces option is benchmarked.
- R12 (mixed time zones in run ids): nrun.py uses UTC since 5259f48; nrpic-run writes UTC.
