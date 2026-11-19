# STATUS of D-bh-dress

gate:        G0 package complete for the orchestrator's review (stage/G0: every item PASS or NA, VERIFIER.md
             on the plan; decision 0016 item 4); not passed. G1 NOT met and not complete for review: D-pre-3
             criterion (ruling at orch), architecture schematic, fresh-context verifier of the G1 material open
             (stage/G1/STATUS.md, OPEN.md)
headline:    The Einstein-Straus benchmark runs in AthenaK: at M/8 the wall tracers follow the exact curve to
             2.2e-3 and the inner tracers cross R = 2M within 6e-3 M of the exact proper times, but the
             horizon-mass drift is 3.4e-4 (1.4e-4 without dust) over 100-200 M, not the predicted 3e-5, and
             1+log stops slicing the expanding dust within 30 M; core's lapse_leak (ES-1G) runs since 15:36 UTC.
last-result: ES-1 / V-1 (D-20261115-172726-60ba4c2, -172730-c6d151b; analysis D-20261119-141839-8686bd7,
             -142929-bb375ff, -143413-bce5e71, -143444-8a9949c): wall and crossings held; 3e-5 drift, +1.5e-3
             level, 1+log plateau model failed; ES-1 within 1.49 x V-1's drift (refutation needs 3);
             late common drift after t ~ 165 M of open cause. Lead's independent recheck Y1-Y6 held
             (D-20261119-151039-b2ce968). ES-1G pre-flight on processors passed (D-20261119-150329-d1d8f03).
next:        1. When Slurm 4636 (ES-1G, D-20261119-142633-6f72922; running since 15:36 UTC, about 50 min) is DONE: es_runs/tools/finish_es1g.sh,
                look at figs/es1g/, judge G1-G7 of es_runs/JOURNAL.md entry 5 as written (G1 on R0 = 40
                and 48 M, R0 = 48 M reported separately; REVIEW-wave2.md section 6)
             2. Late-drift controls (after ES-1G): V-1 with the outflow boundary at 384 M (~0.8 card-hours),
                then V-1 at M/16 near the hole (~1.5); predictions first; then state the ES null-test floor
             3. G1: redraw the architecture schematic (C9); get the verifier slot and the D-pre-3 ruling
                from orch; review flux_tools (wave 3a) and the ES-F input before any matter run
blockers:    orch: ruling on d-pre-3-criterion and a fresh-context verifier for G1 (outbox
             20261119T152700Z); core: the ES test outcome in core_gauge/READY (outbox 20261119T152701Z);
             a lapse that slices expanding dust (ES-1G decides whether lapse_leak does)
needs:       orch: g1-verifier-and-rulings, d-pre-3-criterion, g1-numbers-errata; core:
             es-outcome-and-gauge-ready, lapse-for-expanding-dust (boundary for the PG exterior),
             finder-summary-outdir, trajmet-format-doc, newton-selfforce-doc, openmp-cpu-build,
             spike-mass-refinement, accretion-diagnostics item 3, newtonian-mode-point-mass (card
             throughput); kb: spike-annotations-run-ids (all in outbox/)
offers:      Einstein-Straus data with the outer dust edge at 60 M and the matched vacuum control V-1
             (scratch run D-20261115-170213-d2c2131; generator es_runs/make_data.py, exact references
             es_runs/results/predictions.json); ES-1 / V-1 outputs as a vacuum-bubble benchmark of the
             1+log gauge (es_runs/README.md); Kerr spike reference (spike/kerr_lib.py); Newtonian-mode
             infall references (secondary_infall/nm_shells.py); D-pre-4 floor (puncture_drift/)
budget:      3.62 card-hours used of 30 to the next gate (2.18 wave 1, 1.44 wave 2); 0.98 reserved (ES-1G);
             25.40 left (nrpic-run budget, 2026-11-19)
