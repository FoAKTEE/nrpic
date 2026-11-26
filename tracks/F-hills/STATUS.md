# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1 NOT met (stage/G1, batch 25): the
             complete vacuum passage (C8: A2 at 133.0 M of the >= 170 M needed) and the rest of
             the verifier's work (C18 PARTIAL: VERIFIER.md checked the passage to 96.23 M)
headline:    The m/16 passage P1b (A + A2) reached 133.0 M at A2's segment cap: the binary is
             disrupted and, unlike Newton from the same deck, m1 falls almost radially into the
             heavy hole (2.49 M from M) while m2 swings by at 8.7 M (tracker data, coordinate
             energies, R24).
last-result: - A2 to 133.0 M (F-20261126-054946-a21f229, fig_b21_a2_state read): join complete
               (one-step gaps, overlaps <= 1.25e-9 M); A2-2 REFUTED (the pair's centre of mass
               did not turn at 8-11 M; 5.42 M and closing at 133 M); heavy hole's mass change
               1.55e-3 > 1e-3 (A2-5 clause refuted; verifier F1); member drifts 3.1e-5 and
               -8.1e-6 (fractions of the mass per M); rms H <= 6.0e-5
             - passage reader F-20261126-054957-6cdb7cf (fig_b11_passage read): two-body energy
               of the pair +1.59 units at 133 M (disrupted between 120 and 133 M; Newton by 100 M);
               m1 deeply bound to M, m2 marginal (+0.08); Newton ejects m1 and binds m2
             - cap forecast of batch 21 met: 133.0 M (125-140), 11.15 card-hours (10-14)
             - verifier requests (a)-(d) applied (README: fractions per M, no convergence order;
               conic 9.81 vs three-body 9.76 M; d_at_112 is at 112.38 M); criterion (iii) met at
               its edge (19.8 percent); F1 open with its plan
             - R25 PASSED (F-20261126-054626-7301561, fig_diag_restart read): a restart with `-i`
               holding `<fastflow> diagnostics = true` on core-v0.5 through A2's wrapper writes
               the status file and leaves every other output byte-identical
decision:    continue A2 in place from 133.0 M through one `--cmd` queue entry at priority 2,
             cap 28 counted segments (9 more, about 7.5 card-hours: 18.7 of A2's 19.5), with the
             finder's status file (prediction C25 in JOURNAL)
card jobs:   A2 continuation q0069 (F-A2c, prio 2, waiting), run F-20261124-210400-902c650 in
             place, 133.0 -> 200 M; read by b21_a2_state.py, b11_passage.py, the status file
             B2 alone m/16 q0002 (submitted, Slurm 5357 pending), 107.85 -> 140 M, G2 5 h;
             read by b11_cards.py
             C2 P1b m/12  q0003 (after B2), 20 -> 200 M, G2 24 h; read by b11_passage.py
next:        1. When A2's continuation has records past 145 M: rerun b21_a2_state.py and
                b11_passage.py (registered); judge C25-1 (m1's merger with M) and F1 from the
                status file
             2. At >= 170 M: judge A2-3 to A2-5, close A2 (nrpic-run finish), C8; ask a verifier
                for the passage from 96.23 M on (verifier/scripts/run_all.sh rerun)
             3. Note v3: the passage and its reversed fates, ledger row 194 without an order
blockers:    preemptions (R20); queue cap of five (the account was at five at 21:40 PST)
needs:       core: a restart that accepts a parameter on the command line (NEXT_SOURCE item 1);
             earlier: HRNA pair-force spec, wave extraction beyond l = 8
offers:      continue_chain.sh (counted segments, extra input file), nrread.py, b21_a2_state.py,
             b21_horizon_recheck.py, b25_diag_restart.py (restart + extra input test)
budget:      A2 11.15 card-hours used of its 19.5; this session 0 card-hours (processors only)
