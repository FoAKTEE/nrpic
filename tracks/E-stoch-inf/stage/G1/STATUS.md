# G1 status of E-stoch-inf (2026-11-15, lead)

G1 is not reached. Criteria: track sheet (brief 798, charter 9.8) and the common G1 row
(charter 9.2), made concrete by the owner's thresholds in `../../spec/scope/SCOPE.md`
section 4. Track E's G1 needs core work (decision 0010): unlike the other tracks it has no
"baseline without new core work" for the NR reproduction itself.

| Criterion | Met? | Evidence | What is missing, and who |
|---|---|---|---|
| Track: the power spectrum of the SR case agrees with the analytic result (A2: every mode k <= k_max/2 within 2 percent of W_k R_k alpha_k at N_f) | no | reference ready: full-MS modes of every lattice shell, run E-stoch-inf-20261115-122806-ef0d039, independently confirmed (run E-20261115-135532-3f958a1) | an NR run of the SR case: core's initial slice at N* (SPEC 5.3) and the per-mode output; Track E's extraction of R^NR (P-c) from AthenaK output (not written) |
| Track: super-horizon modes freeze by the criterion of arXiv:2606.14853 (A3: drift of ln Delta after N_k + 4 below 2.5e-3 per e-fold, per mode, SR) | no | criterion and reference curves: SPEC 7.3, `../../spec/fig/fig_freezing.png`, `fig_drift.png`; lead's check: full-MS slope -5.8e-4, FLRW-lattice slope -0.0519 = -4 eps1 within 1.2 percent | the same SR run, to N_f = N* + 8 |
| Track: the constraints converge (A4 second order with negative control; A5 order 4-6 on N = 32, 64, 128) | no | target levels P1:538-541, 747-773 | core: [H], [M] diagnostics independent of the particle module (DESIGN_REVIEW R6); the single-kick test L5 and the ladder |
| Recommended: background (A1) | partly | core's homogeneous slow-roll test in geodesic and conformal gauge exists (core-20261115-133955-836ac86, read only, not reported by core); Friedmann reference by two integrators | E's own check of core's FLRW output against the reference (A1 at 1e-4) |
| Recommended: temporal order (A6) | no | D4: order 4 at stage times, 1 at step start (run E-stoch-inf-20261115-123936-b2ec5c7); core integrates the mode data in lockstep with the stages (source read) | a run with kicks at theta = 0.25, 0.125, 0.0625 (L6) |
| Recommended / brief 10 row "Reproducible random numbers" (A7) | partly | core's generator on processors, scaled base case: 1, 8, 64 MeshBlocks and restart (run E-20261115-135523-a32c3a6; verdicts of the revalidation: LU3_VERDICT) | U9 on a card; rank count; the 64^3 x 300 base case; A1 of the Markov-tanh scheme (cancellation in W(t) - W(t - dt), request to core) |
| Common: baseline results without the NRPIC coupling | yes | linear MS references (SPEC 6-7); stochastic delta-N references for both potentials (runs E-stoch-inf-20261115-130137/-130139-176cdd6, sigma = 1, 0.1, 0.01, lattice band; end of inflation -130747-1b9bee4); V1, V2 benchmarks of the literature reproduced (-125656/-125658-e3eaef3) | none |
| Common: analysis pipeline validated on them | partly | noise validator: self-test with 15 planted errors caught (run E-stoch-inf-20261115-132950-16a0168, rerun identical), on real AthenaK `bin` output (-131126-8eb199a) and on core's generator (E-20261115-135523-a32c3a6) | the R^NR, per-mode and constraint-ratio analysis of AthenaK output (Track E, after core's output format is fixed) |
| Common: interface proposals submitted | yes (this session) | `../../noise/NOISE_SPEC.md`, `../../noise/RNG_REQUIREMENTS.md`, `../../codebase/DESIGN_REVIEW.md` sections 9, 11, `../../spec/SPEC.md` section 10; outbox messages of 2026-11-15T14:10Z to core, B-emd-gw, kb, A-emd-pbh, orch | replies |

Earliest G1: once core delivers the initial slice and the diagnostics, the SR runs are
about 0.4 card-hours at 256^3 plus < 0.3 for the ladder (SCOPE 8); the analysis code for
R^NR and per-mode amplitudes is Track E's next work item.
