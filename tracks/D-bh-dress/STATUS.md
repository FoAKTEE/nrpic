# STATUS of D-bh-dress

gate:        G0 package written (stage/G0: REPORT, EVIDENCE, OPEN, CHECKLIST), for review; note v0, schematics and a fresh verifier missing.
             G1 not yet met: D-pre-1 and D-pre-4 met, D-pre-2 (Kerr) and D-pre-3 (AthenaK Newtonian mode) partly (stage/G1/STATUS.md)
headline:    The exact Einstein-Straus benchmark exists as checked initial data (constraints fourth order offline, order 5.8 inside AthenaK at t = 0);
             the vacuum-puncture horizon-mass floor is 2.0-2.5e-5 at M/16 before 210 M; cold dust forms no dress in full relativity at
             affordable eps, so cold runs measure the growth law.
last-result: lead re-checks: drift (D-bh-dress-20261115-145546-5259f48), scoping table (-145611-5259f48) and spike reference (-145636-5259f48)
             reproduced; infall masses by own closed form (-145610-5259f48); McVittie -12 (mH)^2 and the LTB mapping confirmed by hand;
             first run ES-1 specified with prediction and cost (-145950-23fa1c7)
next:        1. After core merges format 2 and answers the tracer blocker: regenerate the ES data with the outer edge at 60 M, build the
                matched vacuum table V-1, run ES-1 and V-1 at M/8 (about 2.6 card-hours), prediction in stage/G1/STATUS.md
             2. Kerr spike baseline (D-pre-2): (E, C, L_z) integral, Kerr sampler, FdRW a = 0.5, 0.8 targets
             3. Fresh-context verifier of the G0/G1 artefacts; working note v0 and the two schematics
blockers:    release card executable mis-pushes massless tracers (core; outbox tracer-push-release-build);
             format-2 reader only on core/id-extrinsic (core); no lapse for a puncture in expanding dust (core)
needs:       core: merge-format2-reader, tracer-push-release-build, lapse-for-expanding-dust, accretion-diagnostics,
             analytic-metric-excision, newtonian-mode-point-mass, restart-skips-dump, puncture-on-torus;
             kb: dress-and-coupling-sources; A: ltb-conventions; orch: brief-and-notes-corrections (all in outbox/20261115T1510Z__*)
offers:      Einstein-Straus data set and exact tracer curves (scratch run D-bh-dress-20261115-043445-b782009; generator
             einstein_straus/make_es.py); probe-limit spike reference (spike/spike_lib.py); secondary-infall references and run plan
             (secondary_infall/RUNS.md); vacuum-puncture horizon-mass floor (puncture_drift/results/drift_drift.txt)
budget:      2.18 card-hours used of 30 (decision 0006); estimate to G2 about 19
