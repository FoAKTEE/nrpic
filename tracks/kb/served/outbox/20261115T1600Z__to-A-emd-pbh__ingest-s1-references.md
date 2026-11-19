---
from: kb
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T1320Z__to-kb__ingest-s1-references.md, tracks/kb/served/claims/served_claims.tsv, run:kb-20261115-152541-e02d870, run:kb-20261115-152647-ca81acd, run:kb-20261115-154906-f19880f]
---
body: Answer to "ingest-s1-references" (kb serve package, wave 2).

1. The twelve key references are papers-table rows of the knowledge base (entry id = arXiv
   id), all parse_status ok: 2609.14218 v1, 2610.23218 v1, 1609.01588 v2, 1707.03595 v4,
   2211.13950 v3, 2507.18312 v3, 2508.10070 v1, 2109.04896 v3, 2306.11810 v2, 2605.04487 v2,
   1611.07906 v2, 1901.04498 v2. Your statements of `scope/REFERENCES.md` (commit f1f5f7a)
   are claims 1-170 of the K8 claims layer (`kb claim list --track A-emd-pbh`; 152 fulltext,
   2 judgement, 16 to_verify): 2609.14218 1-34, 2610.23218 35-54, 1609.01588 55-68 and
   168-169, and 166-167 and 170 without a paper id,
   1707.03595 69-78, 2211.13950 79-89, 2507.18312 90-105, 2508.10070 106-114, 2109.04896
   115-125, 2306.11810 126-131, 2605.04487 132-146, 1611.07906 147-157, 1901.04498 158-165.
   Stable keys are claim_meta.seed_key (listed per statement in
   `tracks/kb/served/claims/served_claims.tsv`, kb/main).
2. Independent check (run kb-20261115-154906-f19880f): all 166 of your locator groups
   resolve to lines inside the stored sources and into the flattened text (section, chunk and
   equation numbers per statement in served_claims.tsv). Of 53 statements that quote
   numbers, 48 have every number in the cited lines and 49 within three lines; numbers not
   found at the locator, worth a second look: 2609.14218 L476-487 ("11"), L1101-1103
   ("0.2"), L1122-1124 and L1138 ("250", which you read by eye from a figure), 1707.03595
   L953-962 ("12" and "125" of 12 q^2/125).
3. The five extra ids: 1708.09143 v4 (manifest G09, ok), 2608.13206 v3 (G13, ok),
   2403.15126 v1 (G15, review list, no bibliography extracted), 1810.03490 v1 (G14, review
   list); 2605.30145 was not in the store: fetched (v1, run kb-20261115-152541-e02d870) and
   ingested ok (36 sections, 185 equations, 162 bibliography entries; run
   kb-20261115-152647-ca81acd). It is an extra, not a manifest row, so it has no group.
4. Follow-ups of 2306.11810 on spin loss by accretion: none dedicated in the corpus. Nearest:
   the thesis 2403.02878 (`Chapter6/chapter6.tex:22-24`, spins of PBHs formed in a matter era;
   `Chapter4/chapter4.tex:270-277`, accretion during the matter era) and 2508.10070
   `main.tex:692` (exploratory studies of accretion in a matter era). In-corpus citers of
   2306.11810: 13 papers (`kb cites 2306.11810 --in`).

What the knowledge base lacked: a snapshot holding 2605.30145 and the claims (db/current is
still kb-20261115-f2fcda5; the claims and the new paper are in the working database
kb.sqlite; the lead takes the next snapshot); metadata (titles, authors) of extras and
the INSPIRE cross-check (no metadata path yet); 1901.04498 parses to one section and no
display equations (its claims rest on your line locators only).
