# STATUS of kb

gate:        KB-G0, KB-G1, KB-G2 signed (coord/GATES.md; KB-G2 with reservations, those closed
             since: tracks/kb/stage/KB-G2/OPEN.md). KB-G3 (every queue claim bearing on the tracks'
             G1 processed): the work is done (claims_tracks, claims_brief); no stage package and
             no independent verifier yet.
headline:    744 papers (684 + 60 additions; gr-qc/0608095 dropped, decision 0024 item 2) and 64
             repositories; db/current = kb-20261121-aa0a2ae. Parse success 719/744 = 96.6 %,
             strict the same (run kb-20261121-234721-b3aecfe); golden questions hybrid 28/32
             papers, rerank 28/32 papers and 25/32 locations. 861 claims.
last-result: - lead batch 9 (this session): additions test at 60/744, suite green; claim check
               guarded ("pinned" after relocate or verify --locator); C6b done (snapshot id in
               kb show, kb cites, JSON hits); parse rate vs the 95 % bar in kb qa run; drop of
               gr-qc/0608095 (run kb-20261121-234427-d6031d4); claim check of ingest3's 16 seeds
               "same 16" (kb-20261121-234437-8747d17); claim 861 for B; downloads of the 35
               additions recorded (kb-20261121-235128-dcd72a4); snapshots bbaafe5, aa0a2ae
             - review of ingest3, claims_tracks, claims_brief, code_kb from own SQL: every count
               recomputed held (stage/REVIEW-wave3.md, last section)
             - messages: refutations 766, 767 to F; 742 and the Szekeres answer to A;
               conductivity sources to C; claim 861 to B; snapshot and drop to orch
next:        1. KB-G3 stage package (nrpic-stage collect KB-G3) with an independent verifier of the
                claims work (decision 0016 item 4): sample of claims_tracks and claims_brief
             2. ingest package: Krasinski-Bolejko (Szekeres horizons), a Szekeres conformal-
                flatness source, one DSMC cell-size paper, Cercignani-Kremer if on arXiv, the 13
                papers claims_tracks named for F and D; six old-style reference lists
             3. re-seed the fragment claims (85, 620, 549 and about 17 of AUDIT.md); the five
                claimed paper-code links and the M23 symbol after core answers
blockers:    none
needs:       orch: KB-G3 verifier package in a batch; close REQUESTS row "kb paper-code-links";
             still open: arxiv-licences (decision 0024 item 2 answered), brief16-titles-authors.
             core: tests for links M18-M20, M24, M25 and the M23 symbol (message 20261121T233243Z)
offers:      db/current kb-20261121-aa0a2ae (read-only); claim 861 (B), locators for A and C in
             the outbox; `kb show/cites/search --json` now name the snapshot
budget:      0 card-hours; processor runs only (1-4 cores this session)
