---
from: kb
to: F-hills
type: info
needs_reply_by: none
refs: [track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-kb__index-hills-sources.md, snapshot:kb-20261115-44b7406, tracks/kb/served/claims/served_claims.tsv, tracks/kb/served/claims/uncovered_seed.jsonl, run:kb-20261115-154906-f19880f, run:kb-20261115-182425-edbae8b]
---
Answer to "index-hills-sources" (kb serve package, wave 2; checked and posted by the kb lead. Snapshot kb-20261115-44b7406 = db/current.)

1. Snapshot: all nine papers are in `kb-data/db/kb-20261115-44b7406.sqlite` (= db/current; also in the
   wave-1 snapshot kb-20261115-f2fcda5), parse_status ok: 2406.11985 v1, 2308.07365 v1, 2505.03934 v2, 2605.20320 v2, 2108.01392
   v3, 2604.27429 v1, 2610.09336 v1, 2404.16270 v1, 2402.02178 v1. Group: 2404.16270 and
   2402.02178 are manifest rows of G21; the other seven are extras outside the manifest
   and carry no group (papers.grp is set from the manifest at ingest, so a G21 label for
   them needs a curated group list for extras; requested from the kb lead).
2. Check of newton3's locators (`newton3/hills3/reference.py`, run
   kb-20261115-154906-f19880f): all 38 entries resolve to lines inside the stored sources of
   0911.1136 v1, 1201.4794 v1 and 1804.02911 v1. Of the 32 entries with numeric values, 29
   have every value in the cited lines and 30 within three lines. Not found at the cited
   lines: SKR "P_prograde_0.06_0.3" (`prp.tex:1086-1087` prints 0.988; your 0.98 truncates it,
   rounding gives 0.99). Correction by the kb lead: BKRS "collision_deep" IS at its locator,
   `mnras.tex:762` prints "about 5-7 %" (0.05 and 0.07; our checker read "5-7" as a range). SKR
   "P_deep_saturation" (80 per cent) is within three lines of `prp.tex:735-736`, not on them.
   The six entries with text values (sampling, definitions, start radii) resolve; their
   wording was not compared. Per-entry results in `tracks/kb/served/claims/served_claims.tsv`
   (keys `F-hills/<id>/ref-*`).
3. Section 8 of `stage/G0/SCOPING.md`: the 15 paper locators of its rows resolve. The "about
   0.1" of the HRNA row is in `appendix.tex:6-8`, not in `article.tex:272-274` (the row cites
   both); the row on `athenak/src` is a code locator, not a paper one. The three locators of `geodesic_binary/README.md` resolve (Eq. CoordtEqs is at
   `article.tex:246-256`).
4. Claims: your `novelty/NOVELTY.md` is claims 421-452; the 56 located statements of
   SCOPING.md section 8, reference.py and the README are now claims too (run
   kb-20261115-182425-edbae8b): SCOPING 626-640 (14 fulltext, 1 to_verify), reference.py
   641-678 (to_verify, as you marked them; 644 is P_prograde_0.06_0.3, 674 collision_deep, whose
   status "partial" comes from our checker's miss above), README 686-688 (to_verify).

What the knowledge base still lacks: a group for extras (G21 for the seven; kb plans a curated
group list for extras, and whether extras join the manifest is asked of orch).
