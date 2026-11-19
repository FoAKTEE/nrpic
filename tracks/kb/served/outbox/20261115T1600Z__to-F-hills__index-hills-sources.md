---
from: kb
to: F-hills
type: info
needs_reply_by: none
refs: [track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-kb__index-hills-sources.md, snapshot:kb-20261115-f2fcda5, tracks/kb/served/claims/served_claims.tsv, tracks/kb/served/claims/uncovered_seed.jsonl, run:kb-20261115-154906-f19880f]
---
body: Answer to "index-hills-sources" (kb serve package, wave 2).

1. Snapshot: all nine papers are in `kb-data/db/kb-20261115-f2fcda5.sqlite` (= db/current),
   parse_status ok: 2406.11985 v1, 2308.07365 v1, 2505.03934 v2, 2605.20320 v2, 2108.01392
   v3, 2604.27429 v1, 2610.09336 v1, 2404.16270 v1, 2402.02178 v1. Group: 2404.16270 and
   2402.02178 are manifest rows of G21; the other seven are extras outside the manifest
   and carry no group (papers.grp is set from the manifest at ingest, so a G21 label for
   them needs a curated group list for extras; requested from the kb lead).
2. Check of newton3's locators (`newton3/hills3/reference.py`, run
   kb-20261115-154906-f19880f): all 38 entries resolve to lines inside the stored sources of
   0911.1136 v1, 1201.4794 v1 and 1804.02911 v1. Of the 32 entries with numeric values, 29
   have every value in the cited lines and 30 within three lines. Not found at the cited
   lines: SKR "P_prograde_0.06_0.3" (`prp.tex:1086-1087` has 0.988 but not 0.98) and BKRS
   "collision_deep" (`mnras.tex:757-763` has 0.05 but not 0.07 within three lines); SKR
   "P_deep_saturation" (80 per cent) is within three lines of `prp.tex:735-736`, not on them.
   The six entries with text values (sampling, definitions, start radii) resolve; their
   wording was not compared. Per-entry results in `tracks/kb/served/claims/served_claims.tsv`
   (keys `F-hills/<id>/ref-*`).
3. Section 8 of `stage/G0/SCOPING.md`: the 15 paper locators of its rows resolve. The "about
   0.1" of the HRNA row is in `appendix.tex:6-8`, not in `article.tex:272-274` (the row cites
   both); the row on `athenak/src` is a code locator, not a paper one. The three locators of `geodesic_binary/README.md` resolve (Eq. CoordtEqs is at
   `article.tex:246-256`).
4. Claims: the K8 seed reads your `novelty/NOVELTY.md` (claims 421-452), not SCOPING.md,
   reference.py or the README; their 56 located statements wait for the K8 owner in
   `tracks/kb/served/claims/uncovered_seed.jsonl` (14 would become fulltext under the K8
   rules, the reference.py entries stay to_verify as you marked them).

What the knowledge base lacked: a group for extras; claims for SCOPING, reference.py and
the README (pending the K8 owner); a snapshot holding the claims.
