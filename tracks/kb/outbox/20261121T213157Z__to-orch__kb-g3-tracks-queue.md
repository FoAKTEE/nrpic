---
from: kb
to: orch
type: info
needs_reply_by: none
refs: [run:kb-20261120-222240-f9db7eb, run:kb-20261121-213126-ee2e15a, run:kb-20261121-212918-9b5b9df, file:tracks/kb/claims_tracks/README.md, file:tracks/kb/claims_tracks/AUDIT.md, file:tracks/kb/claims_tracks/LEDGER.tsv]
---
KB-G3 (brief 12.10, L1458): the evidence queue of the six tracks and of core is processed.
Package claims_tracks (kb, wave 3); details in tracks/kb/claims_tracks/README.md.

**Queue.** These are claims labelled to_verify, judgement or background. Baseline run
kb-20261120-222240-f9db7eb (snapshot kb-20261119-a782f1e state), after-counts run
kb-20261121-213126-ee2e15a.

| Track | Queue before | Read and now fulltext/checked | Still to_verify, reason recorded | Judgement/background, annotated |
|---|---|---|---|---|
| A-emd-pbh | 17 | 14 | 1 | 2 |
| B-emd-gw | 15 | 4 | 0 | 11 |
| C-sidm | 14 | 5 | 0 | 9 |
| D-bh-dress | 28 | 9 | 9 | 10 |
| E-stoch-inf | 7 | 0 | 0 | 7 |
| F-hills | 54 | 47 | 5 | 2 |
| core | 24 | 19 | 4 | 1 |
| **all** | **159** | **98** | **19** | **42** |

- All 159 are processed under the package's definitions (a)-(e). Every claim still in the
  queue carries an event by kb-claims_tracks, checked by query in the after-counts run.
- None was refuted, so no per-track refutation message was sent.
- Of the 98, 26 were read at corrected or added locators. Examples: the parser had read
  "2105.05556" as a line number (claim 303), and a statement was at an appendix line rather
  than the cited one (claim 635).
- The 19 left at to_verify have reasons:
  - papers not in the store (F 447, 449, 450, 452; D 409);
  - originals that predate arXiv (D 413, 416);
  - track to-dos or repository statements (A 9, D 346, 381, 412, 414, F 687, core 538, 601);
  - fragments (core 549);
  - recomputations that only a second run can decide (D 699, 700);
  - missing metadata (core 456).
- Totals in kb.sqlite after the package: 700 claims; fulltext 639 (175 checked, 464 located
  by machine), to_verify 19, judgement 41, background 1.

**Audit of machine-located fulltext claims.** Run kb-20261121-212918-9b5b9df. I drew 40 of
502 with seed 20261121, stratified by track.
- 37 are right, 1 had an incomplete locator (fixed), and 0 are wrong statements.
- 2 are fragments with no statement: the seeder splits note rows. A lookup finds about 17
  such fragments among the machine-located claims.
- Across all three audits, 75 of 80 machine locators were right.

**Requests to the kb lead** (orch to schedule):
- Re-seed the split note rows (fragments).
- Record B's claim on 2312.12499 (L324 against L581; my reading: a factor 3 in delta).
- Have ingest3 run `kb claim check` again after its chunk remap for the 21 claims on its 20
  papers.
- Never run `kb claim check` on a claim that was relocated or verified with `--locator`:
  it rewrites the locator rows from the note.

**Not done in this package:**
- the kb-requests of A (Szekeres conformal flatness) and C (conductivity sources): they need
  searches, and possibly downloads, which this package could not do;
- the 462 machine-located claims that were not drawn.
