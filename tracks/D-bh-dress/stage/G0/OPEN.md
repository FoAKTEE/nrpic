# What the G0 package of D-bh-dress still lacks

State after the lead session of wave 2b (2026-11-19). Every checklist item is PASS or NA
(`CHECKLIST.md`); the verifier's report on the plan is `VERIFIER.md`, the accepted name
(decision 0016 item 1), so the package is complete for the orchestrator's review under
decision 0016 item 4. The lead does not pass the gate. Open points that do not block G0:

1. Corrections that the verifier and the note's claims check found in wave-1 documents are
   carried into `../G1/STATUS.md` and `../REVIEW-wave2.md` sections 5 and 8; `REPORT.md` of
   wave 1 is kept as it is (decision 0012), so its section 3 (tracer arrival 15.0 and
   34.6 M: exact 14.83 and 34.44 M), the G1 numbers ("3", "15 percent": exact 2.59 and
   9.2 per cent), the capture speeds (0.221 at 16.1 M, 0.113 at 33.4 M) and line 101 (cite
   analysis run D-bh-dress-20261115-125739-a18d74d) are superseded by those files. The
   errata rows are requested from orch (`g1-numbers-errata`, open).
2. The M/32 and M/64 cost of `REPORT.md` section 7 is too low by about ten (verifier C8:
   3200, 4712 or 7848 MeshBlocks); measured at M/8 on the ES mesh: 0.769 and 0.672
   card-hours for 200 M on 344 MeshBlocks. G2 is re-costed before any M/16+ submission.
3. The plan's assumption that 1+log slices the expanding dust (REPORT.md, ES-1 prediction 4)
   was refuted by ES-1 (K ~ 0 in the dust within 30 M); the gauge for the null test with
   matter is decided by ES-1G (core's lapse_leak), queued.
4. References not obtainable here: Bertschinger 1985, Fillmore-Goldreich 1984,
   Einstein-Straus 1945 (records only, kb answer of 2026-11-15T18:37Z); no dust-lattice or
   Swiss-cheese stability paper in the corpus.
