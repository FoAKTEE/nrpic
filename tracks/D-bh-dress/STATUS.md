# STATUS of D-bh-dress

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with reservations
             (signed 2026-11-26, coord/GATES.md). G3 (growth law, infalling matter, null-test bound):
             scope amended A1-A6 (scope/SCOPE_G3.md section 11); A6 (batch 41) carries out decision 0051
             item 3: mesh leg G-8 and G-12u, G-6u only if it qualifies. 60 card-hours toward G3; 3.72 used
             (EG8 1.47, timing 0.05, G-8 2.20). No G3 stage package yet (one member read).
headline:    G-8 (M/8, N, 400 M, run D-20261128-062142-c5666c4): the horizon mass follows the exact LTB
             growth law to +0.17 to +0.25 per cent in all 45 bins of 10 M from 50 to 492 M of the swallowed
             dust's proper time (G3-G1 bound 0.5), +0.10 to +0.24 per cent with the shells' lead carried;
             slope d ln M / d ln a within 3e-3 of the exact one; all 119848 dust removals by the horizon rule;
             795/795 searches found (reader D-20261128-160553-b500509, g8_read.png).
             M/6 does not qualify on processors: the search at t = 0 is not found (reason 6) in G-6u's deck
             and in the null pair at M/6 (run D-20261128-160418-b618bff). core-v0.9 = core-v0.8 byte for byte
             on the G-8 deck (same run, K3): new members on v0.9.
last-result: g3/amend/JOURNAL.md entries 8-13; REVIEW-wave3 section 28; outbox g3-mesh-leg-m6-not-qualified.
failed:      this session: lead-bias size band (shift 1.05e-4 at its low end against 2e-4); K2 "found at
             t = 0" at M/6 (all three decks); S-4N count (140 tracers left out); S-e1 "identical row"
             (expansion columns at round-off); the first G-8 reader run D-20261128-160544-089d6f8 (syntax).
             Not predicted: G-8 minus FK rises with time (6.5e-5 to 1.6e-4). Batch 40: E2 as written, T-12u
             mass band, T-16u (memory), P-A1. Older: STATUS of batch 35 and stage/G2.
next:        1. Read G-12u (q0111) when it ends: G3-G1, e-bar_12 against e-bar_8 (no order), lead
             2. Processor work of A5 before any G-12u criterion is read: Claim D reader on G2's snapshots
                (D1*), polished re-searches of V-1L4/V-1L/V-1L16, G3-G3 power on measured noise
             3. G-8-e1 (gauge leg, smoke test held) when a D chain ends; then the 16N data
blockers:    none for G-12u; G-6u: the ruling's reading (outbox, confirmation asked); later criteria: A5 work
needs:       orch: g3-mesh-leg-m6-not-qualified (confirm the reading of Q1). core: eg8-read-and-g16u-memory
             (moot for G3 after 0051 item 3; kept for the record)
offers:      g3/amend/tools/g8_read.py (growth law against the exact solution, lead brackets, slope);
             m6_smoke.py (byte identity of two builds on one deck); make_g3_decks.py (all G3 decks)
budget:      G3: 60 card-hours; used 3.72; queued caps 15.2 (q0110 0.2, q0111 11, q0112 4). Processors this session:
             one 4-core run (~20 min), one 2-core run (~20 min), two readers on one core.
card jobs:   q0110 D-T6u (batch), q0111 D-G3-G12u (chain), q0112 D-G3-G8-4N (chain); all waiting, core-v0.9,
             priority 2.
relaxed lapse: no run uses it; G3 states why no other slicing is possible (SCOPE_G3 section 8).
