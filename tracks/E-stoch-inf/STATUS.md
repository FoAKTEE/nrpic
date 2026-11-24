# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2 open:
             U-A4'(a) FAIL on record (ruling 0030 item 2: no rewording, review after the quarter pair
             is read); C2 PASS by the same ruling (no gauge variant at G2). Lacks: stage/G2/OPEN.md.
reproduction: complete (decision 0028). Working note tracks/E-stoch-inf/repro/note/manuscript/main.pdf
             (26 pages, REVTeX); verdict per figure and statement: Table IV of the note and the table
             "Verdicts per figure and statement" in repro/note/README.md: of 22 items 12 reproduced,
             6 in part, 1 not reproduced (outliers of order ten: amplitude factor), 1 not matched
             (Stratonovich evolver), 1 corrected (Ito term alpha^5), 1 amplitude differs (USR by
             sigma^2/3). Fresh verifier: repro/verify/VERIFIER.md (two passes). Digest:
             coord/digests/reproduction-state.md. Card time: 8.99 card-hours (repro/scope/CARD_PLAN.md).
last-result: Lead batch 13 (2026-11-24 15:27-16:15 PST):
             - Leftovers of the reproduction closed: RSF256 fourth continuation E-20261124-214913-5956891
               in repro/continue/scripts/conts.json (K2 held, join E-20261124-225720-444aecc); SR span
               N* + 8.10 (ln a = 8.0989 at t = 8.5, joined record) in SETUP_AUDIT item 4; card costs in
               CARD_PLAN.md; S14 names the 99.5th percentile.
             - Floor test queued: FL128h q0037, FL256h q0038 (noise_mode_scale = 0.5, priority 2);
               predictions floor/JOURNAL.md entry 1 (F1: floor halves if second order).
             - Quarter pair U256qp/qm (ran 2026-11-23): analysis E-20261124-233223-51b52c0 (g2q,
               3 cores) started; Q-a..Q-c: g2prod/JOURNAL.md entry 4 (see HANDOFF for its state).
card plan:   q0037 FL128h (ceiling 0.25, expected <= 0.05), q0038 FL256h (ceiling 1.0, expected
             0.35-0.6) in the shared queue. No other E entry waits.
runs pending: q0037, q0038 (card); E-20261124-233223-51b52c0 (processors) if not ended at close.
next:        1. Read the quarter pair (Q-a..Q-c, g2prod entry 4), with figures; update C3/C7 evidence.
             2. G2 verifier (C18) of the g2prod SCOPE 4c numbers, fresh context, processors.
             3. G2 sections of the working note (C17) and figures C10, C13 (orch asked where).
blockers:    orch: where the G2 note sections go; a session for the G2 verifier (outbox 2026-11-24).
needs:       core: figstyle PDFs without creation date (minor; outbox 2026-11-24).
offers:      - repro/: the reproduction of both papers (scripts, readers, ledger, verifier).
             - g2prod/: release ladder, analysis wrapper (analyse_g2.py), SCOPE 4c judge (judge_g2.py).
             - Stochastic delta-N statistics: langevin/, repro/langevin/ (to A). Noise validator: noise/.
budget:      G2 allotment 30 card-hours (decisions 0031, 0032); used 19.32 (manifest of
             E-20261124-214913-5956891); this session 0 card-hours used, 1.25 asked at ceilings.
