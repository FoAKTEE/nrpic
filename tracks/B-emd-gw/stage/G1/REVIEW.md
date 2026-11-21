# Lead's recheck of the helpers for G1 (B-emd-gw)

Decision 0012 asks for `REVIEW.md` where the lead rechecked helpers. The rechecks are:

- `../REVIEW-wave2.md` (2026-11-15, with an erratum of 2026-11-20): first_source, newton_tests,
  note v0, the wave-2 verifier; runs B-20261115-190007-e09a0d2, -190015-4dd3416,
  -190019-b5f5eb6, -190433-2d1d185; journal `../review_wave2/JOURNAL.md`.
- `../REVIEW-wave3.md` (2026-11-20, batch 2a): verifier3, waves, note v1 and v2, verifier2,
  population; runs B-20261121-063617-6183015, B-20261121-063835-826c461; journal
  `../review_wave3/JOURNAL.md` (predictions L1-L3 before the runs; L2, L2b and L3 failed and are
  on record).

Main finding of the wave-3 recheck: the one disputed number of criterion 1 (the plus amplitude
of test X at N >= 48) is a difference of definition between the two readings (modulus of the
complex mode amplitude against its part in phase with the exact solution), not an error of
either; the truncation error is the cross value and the x10 value of both polarizations.
