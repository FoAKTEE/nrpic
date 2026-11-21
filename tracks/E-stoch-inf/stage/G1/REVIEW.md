# Leads' re-checks of the helpers (G1 of E-stoch-inf)

- Waves 2 and 2b: `../REVIEW-wave2.md` (lead of 2026-11-19): the ladder's analyses rerun
  bit-identically; the lead's own code on the 32^3 and 64^3 rungs (`scripts/lead_check.py`,
  run E-20261119-150238-b81e33f).
- Wave 3 (batch 2a, 2026-11-21): `../REVIEW-wave3.md`: the packages `g1verify` (the
  fresh-context verifier, `VERIFIER.md` here) and `ladder` (items (a)-(d)); every final
  analysis step of both rerun from the registered inputs (run E-20261121-063551-7957a3d), the
  new ladder results recomputed with the lead's own code (E-20261121-063816-64ac0dc,
  `../review3/scripts/lead3_check.py`), and risk R1 tested on processors against the release
  core-v0.4. Every verifier finding and what the track does about it: section 2 there.
