# STATUS of D-bh-dress

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with reservations
             (signed 2026-11-26, coord/GATES.md). G3 (growth law, infalling matter, null-test bound):
             scope amended (A1-A5, scope/SCOPE_G3.md section 11) and a dated note under A1 (batch 40):
             G-16u does not fit one card, the full mesh leg as designed ends, ruling asked of orch.
             60 card-hours allotted toward G3; 1.52 used (EG8 1.47, timing 0.05).
headline:    EG8 (core's guard factor 8 with initial_radius_0 = 0.8, to 260 M): removals by the horizon
             rule continue past 219.5 M to the end (all 76696 dust removals by reason 3, 13352 after
             219.5 M); criterion (iii) in [+0.175, +0.250] per cent in 33 of 34 bins, no step.
             Timing: G-12u fits one card (69.0 of 80 GiB), 73.8 s per M, 9.4 card-hours to 400 M;
             G-16u needs about 133 GiB (1.66 cards): no M/16 member of the uniform family on one card.
last-result: readers D-20261128-074210-aa0a37a (EG8) and D-20261128-074128-24b2565 (timing), figures
             looked at; excguard/JOURNAL.md entry 4; g3/amend/JOURNAL.md entry 7; REVIEW-wave3 section 27.
failed:      this session: E2 as written (first bin +0.056 per cent below the band's 0.10; band built from
             FK's late bins only); T-12u mass band (0.99975 against 0.9990 +- 0.0007); T-16u (does not fit
             a card); P-A1 (t_16 undefined); first timing reader run D-20261128-074025-07d95a4 (parse
             defect, rerun). Batch 35: g12s block count; C3 spread. Older ones: STATUS of batch 35 and
             stage/G2 (P5, P6, P11, P13, D3 at N/4 and M/4, FP4, FE1, FE2, XC2, R1 as written).
next:        1. Orch's ruling on the mesh leg (options a-d in SCOPE_G3 note under A1); if (b): a 2 M timing
                run of G-6u first
             2. Processor work before later members (A5): Claim D reader on G2 snapshots (D1*), polished
                re-searches of V-1L4/V-1L/V-1L16 restart files (core-v0.9 adds finder parameters on
                restart), G3-G3 power on measured noise
             3. Read G-8 (q0100) at 400 M with the amended criteria once 2 is committed
blockers:    G3 mesh leg: the ruling (memory, not card-hours); later members: the processor work (A5)
needs:       orch: g3-mesh-leg-ruling (new), g3-scope-amended-first-step. core: eg8-read-and-g16u-memory
             (two-card build or lower memory, only after the ruling), g3-decks-memory-question
offers:      excguard/tools/eg8_read.py (status-filtered finder view + criteria); g3/amend/tools
             (timing_read.py: card memory and s per M from logs; check_review.py; make_g3_decks.py)
budget:      G3: 60 card-hours; used 1.52; q0100 G-8 cap 3.5 waiting. Processors this session: three
             reader runs on one core (seconds each).
card jobs:   q0100 D-G3-G8, run D-20261128-062142-c5666c4, at 17.5 M, preempted three times,
             next job 5639 PENDING; production base,
             read at 400 M (SCOPE_G3 section 4 with A3; needs the vacuum offsets first).
relaxed lapse: no run uses it; G3 states why no other slicing is possible (SCOPE_G3 section 8).
