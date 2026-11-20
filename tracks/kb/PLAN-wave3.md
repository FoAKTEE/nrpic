# PLAN of kb for wave 3

Planner sections, one per round (decision 0019 item 3). Each package runs in parallel in the
worktree `wt/kb` in its own directory `tracks/kb/<key>/`, with path-limited commits.

## Round 1 (planned 2026-11-20T22:15Z, planner of kb)

### State found

- kb/main 1cd5c6ee (main d507d774 merged), tree clean, nothing stranded. No PAUSE flag. No kb
  card job (squeue, sacct); kb's card allotment is 0 (decision 0014), all work is on processors.
- Gates: none of kb signed in `coord/GATES.md`. KB-G0: all items PASS except C5, no verifier
  report. KB-G1: complete (10/10 PASS with `VERIFIER.md`), waits for the gate review. KB-G2:
  thresholds met on snapshot kb-20261119-a782f1e (parse ok 684/710; golden paper 28/32) but C8
  FAIL, no verifier; parse success is 94.8 % under the strict reading (11 ok papers without a
  bibliography entry; `stage/KB-G2/OPEN.md`).
- Cut off in wave 2b ("Run next" of `HANDOFF.md`): the bibliography parser for six reference-list
  formats, the claim chunk remap, the re-ingest of the 20 papers.
- Finished but not merged: branch `kb/brief-check` (wave 3a, worktree `wt/kb-brief`, clean,
  pushed): eleven brief-check packages, purely additive (`tracks/kb/brief_check/**`, 33 run
  manifests). Their reports ask the kb lead to ingest 24 fetched sources (in `kb-data/raw`, not
  in the database), to record claims and section-5 defect rows, and to have CHECK.md reviewed.
- Claims layer (a782f1e): 700 claims from the tracks' notes; to_verify 117 (A 15, B 4, C 5,
  D 18, F 52, core 23), judgement 41, background 1, fulltext 541 (39 checked by a person). The
  brief's own labelled statements are not seeded (brief 12.8 item 1). Section-5 rows of
  `coord/BRIEF_ERRATA.md` wait for the claims layer (decision 0016 item 8).
- Open requests to kb: B track-b-key-reference-claims (probably answered by claims 689-695),
  D spike-annotations-run-ids (claims 682/683). kb to core: paper-code-links (open since 11-15).
  Upstream watch not run since kb-20261115-154646-234060c (decision 0015 asks for it each wave).
- core: no release after core-v0.3; `athenak/src` and `problems` on main unchanged since the
  indexed commit 5deee18, so the parameter index is current.

### Gate aimed at

KB-G2 (and the open verifier item of KB-G0) first: an independent verifier and the removal of
the strict-reading doubt on the parse rate. Then KB-G3 (brief 12.10: every statement of the
evidence queue that bears on G1 of the six tracks processed): the tracks' queue, the brief's
statements, the defects of cited papers. Card time: 0 for every package (sum 0 of kb's 0).

### Packages (ordered by value toward the next gate)

| Key | Goal | Deliverables | Why now | Card cap |
|---|---|---|---|---|
| `verify_g2` | Independent verifier of KB-G2 and KB-G0 on the frozen snapshot a782f1e, given artefacts and criteria, not conclusions; writes a blind held-out golden set (24 questions) before it sees the existing one | `stage/KB-G2/VERIFIER.md`, `stage/KB-G0/VERIFIER.md`, `tracks/kb/verify_g2/{heldout.yaml, scripts/, figures/, JOURNAL.md, README.md}` | the only missing item of two gates; the held-out set was requested from orch in wave 2b and nobody wrote it; a fresh verifier has not seen the retrieval tuning | 0 |
| `ingest3` | Bibliography formats (REVTeX-3 references, AASTeX `\reference`, `\bibitem` macros, `\harvarditem`, unreached .tex, review rule), claim-safe chunk remap, re-ingest of the 20 papers; ingest the 24 sources already fetched as additions (then, if time, the 11 frontier papers); QA on the working database | code and tests in `kb/kbtool/{bib_parse,tex_structure,tex_files,papers_ingest,papers_cli,claims_remap}.py`; `kb/manifests/arxiv_additions.tsv`; `tracks/kb/ingest3/**`; outbox to orch (additions) | cut off in wave 2b; the strict parse rate (94.8 %) sits below the 95 % bar; the brief check's evidence cites papers not in the database | 0 |
| `claims_tracks` | Process the tracks' evidence queue (117 to_verify, 41 judgement, 1 background; A and B first), answer D's and B's requests, audit 40 machine-located fulltext claims | `tracks/kb/claims_tracks/{LEDGER.tsv, AUDIT.md, scripts/, figures/, JOURNAL.md, README.md}`; claim updates in kb.sqlite; outbox to tracks with refutations, to orch (KB-G3 counts) | the substance of KB-G3; A and B are past G0 and need their references processed for G1 | 0 |
| `claims_brief` | Seed the brief's labelled statements as claims (brief 12.8 item 1) by code; join the outcomes of the eleven wave-3a brief-check packages, with a second-agent review of 30 of their rows; enter the section-5 defects of cited papers as refuted claims with their corrections | `kb/kbtool/claims_brief.py`, `kb claim seed-brief`, `kb/tests/test_claims_brief.py`; `tracks/kb/claims_brief/{LEDGER.tsv, REVIEW_SAMPLE.md, ...}`; outbox to orch (claim ids for BRIEF_ERRATA section 5) | KB-G3; decision 0016 item 8 waits for it; the brief check of wave 3a asked for a second-agent review and for these claims | 0 |
| `code_kb` | Upstream watch of AthenaK (decision 0015), K7 module descriptions and task-list order (brief 12.7), a test with evidence for each of the 25 paper-code links, the `<z4c> nco` question, parameter index refresh only if a core release reached main | `kb/kbtool/code_modules.py`, `kb code modules`, `kb/tests/test_code_modules.py`, `kb/reports/code_modules.md`, watch report; link statuses; `tracks/kb/code_kb/**`; outbox to core | the watch is due every wave and was skipped in wave 2b; the paper-code-links request has been open since wave 1; RISKS: tracks taking claimed links for verified | 0 |

### Rules that keep the packages independent

- Write paths are disjoint: `ingest3` alone edits the parser and ingest modules and runs `kb
  ingest`, `kb embed`, `kb eq --apply-tags`, `kb resolve-bib`; `claims_brief` alone edits the
  claims modules (`claims_cli.py`, new `claims_brief.py`); `code_kb` alone edits the code modules
  (`code_cli.py`, new `code_modules.py`) and `kb/curated/paper_code_links.tsv`; `claims_tracks`
  and `verify_g2` edit nothing under `kb/`. Nobody edits `kb/README.md`, `kb/QA_REPORT.md` or
  `kb/STATE.json` this round (each package documents its commands in its own README).
- Code under `kb/` is developed in a private copy under `scratch/kb/<key>/dev/` and lands in
  the worktree in one step: copy, run the tests, commit at once. A modified tracked file outside
  `tracks/` makes `nrpic-run` refuse everybody's submit, and the other helpers import `kbtool`
  from the same tree.
- Every database write takes `locks/kb-writer.lock` (the kb commands do; own scripts use
  `kbtool.lock.writer_lock`). Nobody deletes or rebuilds claims; `ingest3` touches only the
  chunk and flat-range columns of claims of the papers it re-ingests. No helper takes a
  snapshot. `verify_g2` reads only the frozen file `kb-data/db/kb-20261119-a782f1e.sqlite`.
- Downloads only through `nrpic-fetch-arxiv`, one call at a time: only `ingest3` fetches.

### Not planned this round, and why

- Working note: no gate of kb asks for one (`nrpic-stage verify` gives a WARN only); the five
  slots go to gate-bearing work.
- Vectors of the 160000 code chunks: hours of processor time for a full-text index that serves
  today; after KB-G2.
- Licences (arXivRaw mode of the fetch command) and the groups of the 26 earlier additions:
  orch's (outbox of wave 2b, still unanswered).

### For the lead after the round

Merge `kb/brief-check` into `kb/main` (additive); review the five packages; `kb snapshot`; QA
on the new snapshot (`kb qa run --hybrid`, `kb/QA_REPORT.md`); bring KB-G0 and KB-G2 up to date
(C5 and C8 from the VERIFIER reports; KB-G2 stays judged on a782f1e, with `ingest3`'s results
as an addendum on the new snapshot); `nrpic-stage verify` and `report`; call KB-G0, KB-G1 and
KB-G2 complete for the gate reviewer if they are; fold the packages' command notes into
`kb/README.md`; STATUS, HANDOFF, JOURNAL, RISKS; the outbox posts.
