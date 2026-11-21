# STATUS of kb

gate:        KB-G1 PASS (signed 2026-11-20, coord/GATES.md). KB-G0 and KB-G2 packages complete for
             the gate review (all items PASS, each with an independent verifier's VERIFIER.md;
             request kb-g0-g2-gate-review). KB-G3 in progress (claims packages cut, not resumed).
headline:    710 papers and 64 repositories ingested; on snapshot kb-20261119-a782f1e an
             independent verifier confirmed parse success 95.6 % under its own definition (96.3 %
             on the recorded status) and the right paper in the top ten for 87.5 % of the golden
             and 91.7 % of its blind held-out questions (hybrid); the lead's recheck held
last-result: - lead check of verify_g2 from its artefacts (run kb-20261121-125746-a03875b; figure
               stage/review_wave3/figures/fig_lead_check_vg2.png): retrieval 21/22/21 of 24 and
               27/28/28 of 32 recounted from raw hits; snapshot counts by own SQL all equal; parse
               definition re-evaluated 679/710 and 670/710; prediction L1 held in all 8 parts
             - verifier findings handled (stage/REVIEW-wave3.md): C6b WRONG (no snapshot id on a
               hit, in kb show or kb cites) recorded, fix after ingest3; two wave-1 manifests with
               exit 1 corrected to failed; tool-choice reasons named in kb/README.md
             - claims_tracks batch B1 ledger rows committed (run kb-20261120-223013-5330e45)
             - upstream watch 2026-11-20 (code_kb): src/z4c changed on two upstream branches,
               nothing in src/particles; message to core 20261120T222130Z
next:        1. ingest3: bibliography formats, old-style headings, abstracts, claim chunk remap,
                re-ingest of 20 papers, the 24 wave-3a sources; then snapshot, QA with the parse
                rate stated against the bar (removes the thin C3 margin)
             2. parameter index at main after core-v0.4 and core-v0.5 (`kb ingest repo --this
                --ref main`, `kb link load/check`, snapshot): stale since 5deee18
             3. KB-G3: claims_tracks (C1, D1, E1 written, not run; F, core; three kb-requests of
                A, B, C) and claims_brief (the brief's statements)
blockers:    the four packages of round 1 other than verify_g2 were cut on 2026-11-20 and need a
             batch (request kb-cut-packages-schedule)
needs:       orch: kb-g0-g2-gate-review, kb-cut-packages-schedule; still open: arxiv-licences,
             additions-groups-and-0608095, brief16-titles-authors; core: paper-code-links (since
             wave 1)
offers:      db/current kb-20261119-a782f1e (read-only); `kb search --rerank`, `kb show`, `kb
             code --kind param --repo local/nrpic` (options as of main 5deee18, before
             core-v0.4); tracks/kb/verify_g2/heldout.yaml (held-out only, never for tuning)
budget:      0 card-hours used of 0 allotted; processor runs only (1 core this session)
