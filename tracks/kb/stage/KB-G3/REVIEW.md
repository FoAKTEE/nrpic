# KB-G3 review by the lead (batch 13)

The lead's recheck of the packages and of the verifier is in `tracks/kb/stage/REVIEW-wave3.md`,
sections "ingest3 ... code_kb" (batch 9: claims_tracks and claims_brief recounted from own SQL)
and "kb lead batch 13" (ingest4; each finding of VERIFIER.md with what the track did; the common
cause of the six wrong claims; the claims 409, 447, 449, 450, 452).

## Batch 15

Package claims3 (seeds 803 and 805, `kb claim supersede`, the weak class, fragments, downloads
rows) checked from its artefacts in `tracks/kb/stage/REVIEW-wave3.md`, section "kb lead batch
15": ledger against the database, claims changed against snapshot kb-20261124-9872d21, sample
rate recomputed, five claims read at their sources (all verdicts hold; reservation on 877's
mixed label). One defect found and fixed (supersede --to overwrote the successor's
checked_by/checked_at; five rows restored, run kb-20261125-033703-3bd4386).
