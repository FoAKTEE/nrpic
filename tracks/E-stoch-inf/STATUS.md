# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md).
             G2: package complete, ready for independent review (decision 0016 item 4); every
             CHECKLIST item PASS, NA by ruling, or FAIL on record: C3, C7 FAIL (U-A4'(a), one dump
             of M, 3.9245 at cN 6.52) by rulings 0030 item 2 and 0036 item 2. Not passed by me.
reproduction: complete (decision 0028); working note repro/note/manuscript/main.pdf now 32 pages
             with the G2 sections (Sec. IV, Appendix F, ledger Table XVI). Fresh verifiers:
             repro/verify/VERIFIER.md (reproduction), stage/G2/VERIFIER.md (SCOPE 4c).
last-result: Lead batch 15 (2026-11-24 19:32-20:15 PST):
             - Quarter pair judged (g2prod entry 4; judge E-20261125-033357-a608cda, rerun
               E-20261125-033450-4c4a31c): Q-a REFUTED (M factor 4.1275 from s = 1/2, 1/4),
               Q-b HOLDS (-2.07e-6), Q-c HOLDS; agrees with the fresh verifier to its digits.
               Three-amplitude reading (verifier run E-20261125-023427-6fb6400) beside the failure
               as a finding after the data (entry 4.2).
             - Note G2 sections, six figures (ladder, mosaic with zoom boxes, resolution pair,
               even-part scaling, architecture, timeline), ledger rows checked against the G2
               verifier; run_all R11-R16, source R16 E-20261125-035757-340bd1e; checker clean;
               pages read (repro/note/JOURNAL.md entries 19-26). G1 note points to it.
             - Stage G2: CHECKLIST, EVIDENCE, OPEN, REVIEW-wave3 Part F, g2prod README (rerun
               recipe); nrpic-stage verify with --no-checksums and report (see HANDOFF).
             - Outbox to orch: G2 ready for review (+ G3 scope proposal, PDF size); criteria
               proposal for later gates (three-amplitude floor, U-R on the discretisation part).
card plan:   q0037 FL128h, q0038 FL256h waiting in the shared queue (priority 2, since 15:35 PST);
             not part of G2. No other E entry.
runs pending: q0037, q0038 (card; read by floor/JOURNAL.md entry 2).
next:        1. G2 independent review (orch); answer its findings.
             2. Floor runs when they have run: dumppass on FL128h/FL256h, F1-F5 (HANDOFF).
             3. G3 scope after orch's ruling; recompute D1, D2 with the track's reader (R30).
blockers:    the G2 review session (orch).
needs:       core: figstyle PDFs without creation date (minor; outbox 2026-11-24).
offers:      - repro/: the reproduction of both papers (scripts, readers, ledger, verifiers).
             - g2prod/: release ladder, analysis wrapper (analyse_g2.py), SCOPE 4c judge
               (judge_g2.py), quarter-pair judge (judge_q.py).
             - Stochastic delta-N statistics: langevin/, repro/langevin/ (to A). Noise validator: noise/.
budget:      G2 allotment 30 card-hours (decisions 0031, 0032); used 19.32 (unchanged); this
             session 0 card-hours; processors only (2 cores at most).
