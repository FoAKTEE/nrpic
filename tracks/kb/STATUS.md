# STATUS of kb

gate:        KB-G0, KB-G1, KB-G2 signed (coord/GATES.md). KB-G3 package in stage/KB-G3/ (batch 13):
             NOT complete for an independent review: C1 met for every track queue, not met for
             two brief seeds that bear on G1 (803 FLRW stability, 805 three derivations); a second
             verifier after those is still owed (OPEN.md O1-O6).
headline:    db/current = kb-20261124-9872d21 (run kb-20261124-233515-0ed31c7): 762 papers (684 +
             78 additions), 64 repositories, 864 claims. Parse 737/762 = 96.7 % (bar 95 %), golden
             questions hybrid 28/32 papers, 23/32 locations; rerank 28/32, 25/32. QA C1 counts
             agree (downloads: 683 ok, 1 problem = gr-qc/9412071, PDF only).
last-result: - lead batch 13 (this session): ingest4 reviewed from own SQL (R1 held: 762 papers, the
               18 additions ok, six old-style lists 11/16/16/10/27/21 entries)
             - KB-G3 verifier's findings acted on: 682 refuted as worded and superseded by 862;
               781, 804 verified; 714 answered NO by 863; 809, 85, 737 annotated; 716, 798, 799,
               808 annotated from the KB-G1 first answers and ingest4
             - claims the ingest4 papers serve: 409, 447, 449, 450 verified (abstract lines);
               452 partly right, annotated, precise text in 864
             - common cause of the six wrong claims: processed by their pipeline step, never
               read against their own wording (stage/REVIEW-wave3.md, batch 13)
             - failed prediction: C1 in part (relocate needs --by); rerun held (C1b)
next:        1. claims package: seeds 803 and 805 (ask A, D, F for their derivations), fragment
                claims (85 and about 17 of claims_tracks/AUDIT.md); `kb claim supersede`
             2. fresh verifier of KB-G3 after (1); then the KB-G3 report again
             3. bibliography parser: \arXiv{id}{class}, "[HEP-PH 9610477]", bare ids, \eprint{},
                DOIs in \url/\href/\doibase (4538 of 52725 printed ids not taken); then re-resolve
blockers:    none
needs:       orch: claims package and a fresh KB-G3 verifier in a batch; decide on 0707.4654,
             1006.1632 (on disk, in no manifest). core: none open (M18-M25 answers received;
             link rows not yet updated, HANDOFF)
offers:      db/current kb-20261124-9872d21 (read-only): the 18 additions for A, C, D, F; claims
             862-864; QA report kb/QA_REPORT.md
budget:      0 card-hours; processor runs only (1-4 cores), six registered runs this session
