# OPEN items of E-stoch-inf at G2 (lead of batch 13, 2026-11-24; replaces the list of batch 10a)

What the G2 package lacks, in one list (CHECKLIST item in brackets):

1. The reading of the quarter-amplitude pair (C3, C7): U256qp E-20261123-230004-861aea7 and U256qm
   E-20261123-230507-a6246b1 ran (0.62 card-hours each, finished 2026-11-23 20:06 PST); analysis
   E-20261124-233223-51b52c0 (group g2q, 3 cores) started 15:32 PST this session; Q-a..Q-c of
   `g2prod/JOURNAL.md` entry 3 judged in entry 4 when it has ended. Ruling 0030 item 2: U-A4'(a)
   stays FAIL on record without rewording; a cause of the miss is named only if Q-a holds.
2. A fresh verifier of the g2prod SCOPE 4c numbers (C18, C5): U-A0..U-A4', U-R, U-S, the halving and
   the quarter pair, recomputed with its own reader from the run directories. repro/verify verified
   the reproduction (133 ledger rows), not the SCOPE 4c judgement.
3. Working-note sections for G2 (C17): the SCOPE 4c ladder, its one failure, the third amplitude and
   the common-mode part. The reproduction note (`repro/note/manuscript/main.pdf`, 26 pages) covers
   the reproduction only.
4. Figures (C10, C11, C13, C15, C16): verification-ladder schematic; a note figure of the USR
   resolution pair 256/320 (the analysis figure fig_g2_resolution.png exists); a multi-scale slice
   mosaic with zoom boxes; the G2 update of the architecture schematic and the gate timeline. Mesh
   convergence (fig_specconv) and constraint norms (fig_constraints) exist in the reproduction note.
5. Rerun recipe of g2prod (C6): `g2prod/README.md` without the analysis commands of entry 2 (they
   are in HANDOFF.md).
6. Floor of the SR spectral convergence (C2 context, not a G2 criterion): FL128h q0037, FL256h q0038
   (priority 2, about 0.4-0.65 card-hours), predictions `floor/JOURNAL.md` entry 1; a cause is
   named only if F1 and F3 hold.
7. Observations without a cause, on record: the common-mode part of the odd-part error (-4.1e-5 at
   s = 1, s^2; g2prod 2.3); U-A2' at s = 1/2 14 percent above s = 1; a4res Q6; the one-point width
   factor 3.5-4 against the published figures (repro/note); lockstep sub-stepping (core request).

Can it go to an independent review once the queued runs have ended? Not on the runs alone. After
item 1 is read (a processor analysis, no card), ruling 0030 item 2 allows the review with the
U-A4'(a) failure on record. Items 2 and 3 (verifier, note sections) are products of the package
(C17, C18) and are not made yet; item 4 (figures) and item 5 are small. Item 6 is not required for
G2. Estimate: one verifier session and one note session (processors only), then the review.
