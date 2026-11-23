# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md). G2 in scouting: both track criteria met once (C7, C8 of
             stage/G2/CHECKLIST.md); convergence, exterior constraints, verifier missing.
headline:    To 500 M with the faces at +-768 M (release core-v0.6, plain 1+log, M/8) the
             vacuum-bubble horizon mass stays within the vacuum control's drift: the largest
             difference is 2.28e-4 against the threshold 2.51e-4 fixed before the runs. With dust
             filling the bubble the horizon grows from 0.99 to 1.61 M and follows the exact LTB
             mass to within 0.62 per cent at every 10 M bin of shell proper time up to 650 M.
             The vacuum floor (1.25e-4) is a step at 240-300 M that M/8 and M/16 share; the
             finder mass changes sign between M/8 and M/16 (+9e-4, -2.5e-4).
last-result: g2long/JOURNAL.md entries 5-9: judge_long D-20261123-020550-f9a3482, esf_criteria
             D-20261123-020614-7ba5874, esf_analyse -020606-fa0046c, constraints -021027-e3af9b8;
             Q16-256 (secondary_infall) D-20261123-020626-183c254, -020756-e9922e7: QR1, QR2,
             QR5 hold, QR3 per-bin and QR4 slope fail narrowly.
failed:      V3 floor > 1e-4; E2 sharp bounds; V3/E3 radii; F2 at 400 and 500 M; F3 median
             (+0.52 %) and D1 (+9.4e-3); F4 "all reason 3" (horizon excision ends at 219 M,
             nrpic.cpp:451-455); H1 (sign), H2 (M/16 floor not lower); QR3 bins, QR4 slope.
next:        1. Read FV4 (job 4933) first: P1 (finder finds the horizon at M/4); cancel FE4/FF4
                (held, jobs 4935/4936) if it never does; then FK (4934), FE4, FF4 (entry 6)
             2. R5 ES-1L16 to 300 M (job 4920): rerun judge_long, close H3
             3. G2 gaps (stage/G2/OPEN.md): exterior constraint norms (region_*), ES-FL at 4N,
                the cause of the vacuum step, G2 verifier, ladder table
blockers:    none for queued runs; core request ah-excision-growth-guard (workaround in use)
needs:       core: ah-excision-growth-guard (new); older: lapse-leak-growth-data,
             newtonian-mode-edges, lapse-excision-criterion, particle-energy-and-crossing-record
             item 2, accretion-diagnostics item 3, spike-mass-refinement (outbox/)
offers:      long-run inputs and builders (g2long/tools/make_inputs.py, make_followups.py);
             judge_long.py, constraints_long.py; esf_criteria.py --tau_max; ES-F data with the
             table to 1340 M (D-20261121-203042-82deeec); held-job sequencer
budget:      card-hours toward G2 (nrpic-run budget at 18:16 PST): used 13.53, reserved 5.90,
             left 10.57 before the follow-ups. Batch-5 chains used 12.84 h by Slurm elapsed
             (R5 2.51 so far). This session registered four chains with caps 2.0 + 3.0 + 2.0 +
             2.0 = 9.0 card-hours (expected ~4.5), announced here (decision 0014). Processors:
             four 1-core smoke tests (16-19 min), analyses on 1-2 cores.
card jobs:   R5 ES-1L16 4920 (pending); FV4 4933 (pending); FK 4934, FE4 4935, FF4 4936 held,
             released in that order by the sequencer in scratch/D-bh-dress/g2long_seq2/.
