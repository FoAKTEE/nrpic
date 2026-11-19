# STATUS of E-stoch-inf

gate:        G0 package complete for review (all items PASS/NA, 2026-11-19); G1 in progress, not
             met (stage/G1/STATUS.md): spectrum and freezing met, A4 strict fails, products missing
headline:    The slow-roll case of arXiv:2512.14649 runs in this AthenaK (core/scalar-2, scouting) and
             passes A1-A3, A5-A7 up to 256^3; the lead reproduced the 32^3/64^3 numbers with own code;
             A4 (constraints second order) fails in P1's set-up by first-order spatial truncation.
last-result: - P256 (256^3, P1's set-up): A2 1.21e-4 for |n| <= 32, A3 drift 1.4e-4 per e-fold (FLRW
               lattice -0.05), 0.503 card-hours (E-20261115-172618-f948386; analysis -194633-9e04ed8).
             - A6: temporal order 3.93-4.08, time error of R^NR below 3e-4 at Courant 0.25
               (E-20261119-142317-c851f27, -145230-ff0dff2); A12 bit-identical (-141654-c2a10d1).
             - Lead's review: ladder analyses rerun bit-identically (E-20261119-150842-ca70d37); own
               code on L32/L64 agrees (E-20261119-150238-b81e33f); noise reference fixed, Markov-tanh
               A1 4.6e-15 (E-20261119-150541-3210cd6). stage/REVIEW-wave2.md.
next:        1. Orchestrator's ruling on A4'/A5' (proposal 20261119T151727Z) and a fresh-context
                verifier of the G1 material (request 20261119T151728Z); then finish the G1 package.
             2. G1 products: updated architecture and data-flow schematics, G1 sections of the note
                (one script per figure), redraw schem_timeline and fig_background.
             3. Review the wave-3a package usr/ (USR case, G2) and plan the USR runs at 256^3
                (about 0.63 card-hours); fix the ladder's last-dump time mismatch.
blockers:    G1: orchestrator (A4 ruling, verifier). G2: core's release of the scalar-2 set-up
             (request 20261119T151729Z); every SR result so far is a scouting run.
needs:       orch: a4-a5-rewording, g1-verifier, stage-packages-wave2b (info),
             harness-batch-restart-and-cold-reads (info). core: release-scalar2-sr-setup;
             late-entry-truncation-and-answers (info). kb: errata-reply-eq-number (info).
offers:      - SR ladder at 32^3-256^3 with verdicts, floor and A6 analyses: ladder/ (track/E-stoch-inf).
             - Independent R^NR/constraint check: stage/G1/scripts/lead_check.py.
             - Reproduction spec with errata: spec/SPEC.md; MS references: spec/ref/.
             - Stochastic delta-N solvers and reference statistics: langevin/ (to A-emd-pbh).
             - Noise validator A0-A15 with the fixed reference: noise/ (to core, C-sidm).
budget:      1.43 of 10 card-hours used (G1, nrpic-run budget); this session none (processors only).
