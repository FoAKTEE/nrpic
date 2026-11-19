# RISKS of D-bh-dress

Updated in the lead session of wave 2b (2026-11-19). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust. Measured in ES-1 (1+log, D-20261115-172726-60ba4c2): K at the plateau tracer falls to 0.1-0.2 of -3H within 30-40 M and changes sign at 40-90 M, the lapse settles at 1.3-1.4 out to the boundary, the dust ages 280 M by t = 200 M; a lapse pulse from the dust moves the horizon mass by up to 3e-4 during t = 25-50 M | certain for 1+log; open for lapse_leak | the null test in expanding dust is not defined by 1+log; transients at the hole | ES-1G (D-20261119-142633-6f72922): G1-G3 of es_runs/JOURNAL.md entry 5 | core's lapse_leak (core_gauge); outbox lapse-for-expanding-dust and es-outcome-and-gauge-ready |
| R3 The floor of the null test in the ES set-up is not the D-pre-4 floor. V-1 on the ES mesh: 4.2e-5 over 100-165 M, 1.4e-4 over 100-200 M (D-20261119-151039-b2ce968), against 2.8e-5 for D-pre-4 | certain | a floor quoted too low | V-1 and its controls | floor stated only after R13 is explained, from t0 after the step at t ~ 30 M |
| R13 Common late drift of the horizon mass after t ~ 165 M in ES-1 and V-1 (to -3.4e-4 and -1.4e-4 at 200 M) and late axis/diagonal split of the tracer errors (from tau ~ 130 M); the boundary hypothesis failed its probe tests (D-20261119-143413-bce5e71, -143444-8a9949c) | certain (seen), cause unknown | the null-test window ends near 165 M at M/8; a slicing or finder effect would bias G2 | V-1 controls | V-1 with the boundary at 384 M, then V-1 at M/16 near the hole (lead's decision, after ES-1G) |
| R14 Lapse excision idle: the mesh minimum of the lapse rose above alpha_exc = 0.05 near t = 6 and 15 M in ES-1/V-1 | certain under 1+log | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8; check in ES-1G and ES-F |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) untested | medium | floor windows limited | boundary control | joins R13: the V-1 run with the boundary at 384 M |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools, wave 3a) is the first matter run into the hole |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R8 Outer boundary with K_ij ~ r^(-3/2) (Painleve-Gullstrand exterior): outflow is not transparent | medium | reflections reach the hole | R13 controls | boundary at 384 M; core request (lapse-for-expanding-dust, boundary part) |
| R9 Cost: G2 ladder priced about ten times too low beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (ES-1 0.769, V-1 0.672 card-hours for 200 M on 344 blocks); 25.4 of 30 card-hours left |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr) | medium | misleading wording | wording review | SCOPE.md 3.5-3.6 wording; second-agent review requested |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R15 G1 waits on others: a fresh-context verifier (0016 item 4) and orch's ruling on the D-pre-3 criterion | certain | G1 not reviewable | outbox g1-verifier-and-rulings | if the wording stays: Newtonian-mode run to a/a_i = 30-100 (two to four card-hours [JUDGEMENT]) |
| R16 Shared worktree: a wave-3a helper (flux_tools) commits in this worktree beside the lead; a wave-2b helper removed a directory through a shell-variable path | medium | index conflicts; rule breaks | git status before each commit | path-limited commits; rule repeated in HANDOFF traps |

Closed:
- R1 (release card executable mis-pushes massless tracers): an input convention, m = 0 is a null particle
  (D-20261115-172821-f800e34; core dfix-answers); ES-1 tracers (m = 1e-30) follow the exact curve to 2.2e-3.
- R7 (format-2 reader only on core/id-extrinsic): in release core-v0.3; ES-1/V-1 ran on it.
- R12 (mixed time zones in run ids): nrun.py uses UTC since 5259f48; nrpic-run writes UTC.
