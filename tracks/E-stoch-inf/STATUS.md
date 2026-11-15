# STATUS of E-stoch-inf

gate:        G0 package submitted 2026-11-15 (stage/G0: CHECKLIST, EVIDENCE, OPEN; scoping in
             spec/scope/SCOPE.md v1); group decision requested; G1 not reached (stage/G1/STATUS.md)
headline:    Specification, code-base assessment and compute estimate are complete and checked
             independently; core's scalar field with the stochastic hook (core/scalar-field 836ac86)
             follows the spec and its noise generator passes the validation; the lead recommends
             to continue (about 2 card-hours to G2, 0.4-0.5 per 256^3 realisation).
last-result: - Reruns of all four helper packages reproduce their numbers (runs E-20261115-135531-0c4e629,
               -135532-5ec2b09, -140116-87c1cc5, -140502-f70b223); independent background,
               freezing and delta-N checks agree (E-20261115-135532-3f958a1).
             - Core's generator, U1-U8 on processors (E-20261115-135523-a32c3a6, validation
               E-20261115-140502-2957846): frozen and Markov-Heaviside pass everything (bitwise across
               1/8/64 MeshBlocks and restart); Markov-tanh fails only A1 (1.07e-10 vs 1e-11), a
               cancellation in W(t)-W(t-dt) (diagnostic E-20261115-140553-0b75e1e).
             - delta-Pi erratum of 2502.06783 eq. (17) re-derived from its own dictionary (SPEC 5.3).
next:        1. When core delivers the initial slice at N* and the diagnostics: SR case at 32^3-128^3
                (ladder) and 256^3 on a card; A1-A7 of SCOPE 4.
             2. Write the analysis of AthenaK output: R^NR extraction (P-c), per-mode amplitudes,
                constraint ratios, freezing check against spec/ref (needs core's output layout).
             3. G0 products still open: REVTeX working note v0, two schematics, verifier report
                (stage/G0/OPEN.md).
blockers:    G1 needs core: initial slice at N* with the corrected delta Pi, [H]/[M] and double
             dumps of the Z4c fields, a card build of core/scalar-field (outbox 20261115T1410Z).
             The G0 decision is the group's (outbox to orch).
needs:       core: initial-slice-at-nstar; sf-diagnostics-and-interface; noise-unit-test-results
             (cancellation-free window increment, U9, rng ModeEntity/stream 3); card-build-scalar-field.
             B-emd-gw: nrcosmo2-and-diagnostics. kb: errata-s11-references.
             orch: g0-decision-requested; harness-and-brief-notes.
offers:      - Reproduction spec with errata: spec/SPEC.md (track/E-stoch-inf).
             - Linear MS references and freezing curves for both cases: spec/ref/ms_reference.py.
             - Stochastic delta-N solvers and reference statistics: langevin/ (to A-emd-pbh).
             - Noise validator for core's generator (A0-A15) and its self-test: noise/validate/.
             - Noise unit-test driver for core's executable: analysis/lead/u_runs.py, lu_validate.sh.
budget:      0 of 10 GPU-hours used (decision 0006); processor runs only.
