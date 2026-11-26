# G1 of F-hills: what the gate still lacks (2026-11-25, lead, batch 25)

G1 is NOT met. Item by item.

1. **A complete vacuum Hills passage (T4, CHECKLIST C8).** P1 (m/8) merged its binary at 48.8 M.
   P1b at m/16: A (F-20261121-203144-b2cf16b, 0-61.8 M) + A2 (F-20261124-210400-902c650, queue
   q0001, ended at its segment cap: 21 attempts, 11.15 card-hours) reach 133.0 M, joined without a
   gap (batch 25, F-20261126-054946-a21f229). State at 133 M (F-20261126-054957-6cdb7cf): the pair
   is disrupted (two-body energy +1.59 units; separation 6.91 M and rising); m1 falls almost
   radially into M (2.49 M from M, deeply bound); m2 is near its closest approach (8.74 M,
   energy +0.08 units). Newton from the same deck gives the reverse fates (m1 ejected, m2 bound).
   Missing: the outcome (C25: m1's merger with M expected before 145 M; m2's fate) and the
   trackers to at least 170 M. Continuation: one `--cmd` entry of the shared queue at priority 2
   (HANDOFF.md names it), cap 28 counted segments (9 more, about 7.5 card-hours; A2 stays within
   its 19.5, up to 5 more from G1's allotment only if preemptions eat the margin, ruling 0042
   item 2), with `<fastflow> diagnostics = true` by `-i` if the processor test R25 holds.
2. **Verifier of the G1 material (C18): PARTIAL.** VERIFIER.md (batch 22) recomputed with its own
   readers the Newtonian reference, the passage to 96.23 M, the mesh members, P1 to 280 M, H1-H4,
   criterion (iii) and four KHSR points. Requests (a)-(d) applied in batch 25 (REVIEW-wave3.md);
   (e) = finding F1 open (below); (f) in note v3. Still for a verifier: the passage from 96.23 M to
   its end (rerun `verifier/scripts/run_all.sh` on the completed passage; its section 7 says how
   each A2 prediction is read), F-pre-1 (0911.1136, 1804.02911), F-pre-2, eih, the rest of the
   note ledger.
3. **Note v3.** The passage section (A2 to its end, the reversed fates), the junk at P1b's spheres
   (T3 reservation), ledger row 194 without an "order" (verifier F2), "5.5e-7 raw" instead of
   "4.9e-7" and "+0.32 percent from the search at 4 M" (verifier f), the duplicated legend of
   fig_elliptic, floats after Sec. VI, the reviewer step of the paper-writing procedure.
4. **Reservations on T3 (C7).** Criterion (iii) is met at its edge: the four radii agree within
   19.8 percent against 20 (verifier F4). The junk is measured with P1's m/8 binary; most of the
   window's energy is a steady emission of unidentified source; extraction stops at l = 8. To be
   remeasured at P1b's spheres (A2's waveforms, complete to 132.75 M).
5. **Finding F1 (verifier): the heavy hole's horizon mass on two branches from 86.6 M.** Open.
   Plan: the continuation's status file (finder 2's found, reason, iterations, mean expansion per
   search) decides which branch is the converged surface from 133 M on; rows before 133 M stay
   "made without the diagnostics". A2-5's clause "heavy hole changes by less than 1e-3" is
   already refuted as written (1.55e-3 by 133 M, F-20261126-054946-a21f229).
6. **Wording (done in batch 25 unless named).** Fractional drifts "per M" labelled as fractions of
   the mass (binary_conv README, CHECKLIST); m/8 member drift 0.9-1.7e-3; P1's heavy hole within
   0.7 percent after 1 M; the Newtonian centre-of-mass pass 9.76 M at 104.34 M (three-body), 9.81 M
   the conic; p1_280.json's `d_at_112` is the distance at 112.38 M (p1_280.py line 63).
7. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass after a
   run's end in `m_at`; binary_conv's README "Results" row for 20 M at m/16 is out of date;
   geodesic_binary S4 (Kerr, chart 'cks') carries the slicing pump (rerun in 'bks').
8. **For G2 (not G1).** B2 (q0002, submitted, Slurm 5357 pending) and C2 (q0003, waits after B2);
   g2mesh G2M-2/3; the gauge leg; C's member drift above A4's bound. New runs that use the finder
   set `<fastflow> diagnostics = true`; continued runs get it by `-i <file>` (decision 0043 item 5).
