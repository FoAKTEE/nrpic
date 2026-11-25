# Journal of verify/noise_level2_close

Full text: `tracks/core/JOURNAL-noise-level2.md` entries 16 (predictions, 13:20 PST,
committed b90ce894 before any comparison ran) and 17 (outcomes).

## 2026-11-24 13:12 to 13:21 PST

Predictions (entry 16, written before the runs):
- R1f: 366 of 366 files identical; refuted by one differing or missing file.
- R6: every file identical; refuted by one differing file.
- Publication: sha256sum -c passes in both directories; reviewed checksums 0222e5f0..,
  d7069a4e.., 31210622...
- R5: entry 8 (identity to 6ca93cba at 64^3; cost ratio at most 1.18, refuted above
  1.3); not expected to run within the session.

Outcomes (entry 17):
- R1f 366 of 366 identical (core-20261124-211517-b90ce89). HELD.
- R6 22 of 22 identical (core-20261124-211548-60896c5). HELD.
- Publication: both directories pass sha256sum -c. HELD.
- R5: queued as q0035 at 13:19 PST; not run. OPEN.
- Correction found while looking at the figures: entry 10 gave 5.8e-12 for the rms of
  n.d R in R4; that is the last dump, the largest is 6.6e-12 (still below 1e-11).
