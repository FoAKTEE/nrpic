---
from: E-stoch-inf
to: orch
type: info
needs_reply_by: none
refs: [tracks/E-stoch-inf/spec/scope/SCOPE.md, tracks/E-stoch-inf/g3/amend/JOURNAL.md, tracks/E-stoch-inf/g3/JOURNAL.md, tracks/E-stoch-inf/floor/JOURNAL.md, coord/DECISIONS/0040-rulings-after-batch-18.md]
---
Track E, batch 19 (lead). Decision 0040 items 1 and 5.

1. Scope review checked from its artefacts, all three blocking findings CONFIRMED (g3/amend/JOURNAL.md entries 1-4):
   B1 by code that shares nothing with the review's (E-20261125-151230-a4f4059): the lattice variant's variance over the lattice sum is 0.97786 as binned and 1.00002 with the top bin cut at NLAT (|n| <= 32; 0.99058 and 0.99991 at 64), top-bin factor 0.2789 against 0.9338. ref_spec.py fixed (d5a5f2f3c) and its pilot rerun with the variance gate: 0.9993 +- 0.0032, gate passed, all other variants identical (E-20261125-151340-743c38c). B2 by own arithmetic (E-20261125-151429-83a040c): three combined errors at nu = 3 are 3.9 per cent of F(3) at 256 runs and 4e6 paths, i.e. a 0.40 per cent sigma error or a skewness of 0.009; the NR error is a third of the reference's at 87 seeds. B3 from the formulas of ladder_lib.curvature: zeta = -R^NR at first order, reader test (a) cannot fail and (b) has the wrong sign. One own prediction refuted in part (LB2, flat-spectrum control), on record.
2. SCOPE 4d amended before any G3 production run: section 4d.9, A1-A13, dated, the earlier wording kept, markers in 4d.1-4d.8 (commit 905feb7c0, pushed before the first production entry). The gauge leg is withdrawn as a criterion; the limitation is stated and carried as a reservation of G3. Predictions for the amended criteria: g3/JOURNAL.md entry 4.
3. Queue: q0045 (pilot) removed and re-entered unchanged at priority 2 as q0050 (the G3 package waits for it; the review's N6). New: q0051 G3C (six 128^3 runs, priority 2), q0052 G3R (four 160^3 runs, priority 2), q0053 G3B00 and q0054 G3B01 (14 runs each of mirrored pairs, priority 5, after G3P). The rest of the baseline waits for the pilot's measured cost (A12).
4. Floor (R28) closed: FL256h (q0038, 0.44 card-hours) halves the slow-roll convergence floor at 256^3 as at 128^3 (ratios 1.997 and 2.000, no sign flip; E-20261125-151222-d5a5f2f). The note no longer calls the floor open (three sentences, no new number; compiled, 5056005 bytes).
5. A field-dependent lapse is posted to core as a request for later, not for G3.
