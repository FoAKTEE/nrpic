# Stage report: kb KB-G3

Date: 2026-11-25 · branch `kb/main` at `34fce4045eff` · checklist
`tracks/kb/stage/KB-G3/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**PASS**. Tag: `stage/kb/KB-G3-pass-20261125` (created and pushed by the orchestrator after review, decision 0003).

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/KB-G3/STAGE_REPORT.md` | present |
| `stage/KB-G3/EVIDENCE.md` | present |
| `stage/KB-G3/OPEN.md` | present |
| `stage/KB-G3/CHECKLIST.md` | present |
| `stage/KB-G3/VERIFIER.md` (verifier's report) | present |
| `stage/KB-G3/REVIEW.md` | present |
| scoping text | `stage/KB-G3/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate KB-G3 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Every statement in the evidence queue that bears on G1 of the six tracks has been processed | (batch 15) Every to_verify claim of A, D, F, core and of the brief carries a processing event except 806, 807, 810, 811, 812, which decision 0035 item 5 rules do not bear on G1. 803 answered by claim 869, 805 annotated with the tracks' derivations (package claims3, runs kb-20261125-023541-5ae96e9, kb-20261125-023915-2822f6f); 20 fragments closed (run kb-20261125-023542-f420d93). Count on snapshot kb-20261125-2f97258: run kb-20261125-034227-58fc4e0, figure lead_b15/figures/fig_g3_queue.png (read). Lead's check of claims3: REVIEW-wave3.md section "kb lead batch 15". Known limit, not a C1 item: 543 unread weak-class claims, est. 86.5 % right as worded (OPEN.md O7). | PASS |
| C2 | Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10) | `kb` opens kb-data/db/current by default (kb status: snapshot kb-20261125-2f97258.sqlite, run kb-20261125-033718-3405697 status_current.json); every `kb show` view ends with the snapshot id (C6b of KB-G2, met since batch 9). | PASS |
| C3 | `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10) | (batch 15) `kb snapshot` after claims3 and the lead's repair: kb-20261125-2f97258 (sha256 2f97258c...; run kb-20261125-033718-3405697, with verify-downloads and QA); EVIDENCE.md names it for every number; the messages of batch 15 carry it. | PASS |
| C4 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md, SCOPE.md in tracks/kb/stage/KB-G3/. | PASS |
| C5 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot | VERIFIER.md of a fresh helper session (batch 11): 54/60 sampled claims right; its numbers recomputed from its own runs on snapshot kb-20261121-aa0a2ae. VERIFIER2.md of a second fresh helper session (batch 15; decision 0036 item 3) on snapshot kb-20261125-2f97258: 60/61 changed claims right, new stratified sample of 40 (P 12/14, M 10/13, Q 12/13), C1-C7 met with reservations, recomputed the C1 table, the weak-class count and the snapshot hash (runs kb-20261125-041310-20371de, kb-20261125-042240-6c19d72). Note: this item was marked PASS before VERIFIER2.md existed (VERIFIER2 C5); it rests on both reports since batch 17. Gate signed, pass with reservations (coord/GATES.md 2026-11-24). | PASS |
| C6 | Null results and failed runs are on record (manifests and JOURNAL) | Failed run kb-20261124-233445-89478ae (three relocates without --by) on record; batch 15: prediction V1 failed in two places (weak class 548 outside 520-543; five claims outside the ledger changed: a tool defect, fixed), outcomes V1, V2, R2, S2 in tracks/kb/JOURNAL.md; claims3/JOURNAL.md entries 1-5. | PASS |
| C7 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md rewritten in the lead session of batch 15. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-25T12:50:29Z, clean export of `34fce4045eff`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 34fce4045eff (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G3-34fce40-20261125T125018Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G3/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 3 figures, each with its script |
| min-figs | PASS | 0 schematics and 3 data figures (brief 13.4 asks at least 0 and 0 at KB-G3) |
| runs | PASS | 239 run manifests finished (77 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 76 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 41 lines |
| rerun | WARN | re-run skipped (--no-rerun) |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_kbg2.* | note/scripts/fig_kbg2.py | data | to be confirmed by the session |
| note/figures/fig_w2_review.* | note/scripts/fig_w2_review.py | data | to be confirmed by the session |
| note/figures/fig_w2b_review.* | note/scripts/fig_w2b_review.py | data | to be confirmed by the session |

## Verifier report

`tracks/kb/stage/KB-G3/VERIFIER.md` present; its first lines:

> # VERIFIER report: gate KB-G3 of the knowledge base (kb), 2026-11-24
> 
> Verifier: a fresh kb helper session (batch 11) that did not write any of the packages checked.
> Gate criterion (brief 12.10): "every statement in the evidence queue that bears on G1 of the
> six tracks has been processed". Material checked: the claims of packages `claims_tracks` and
> `claims_brief`, ingest3's bibliography, the code index (`code_kb`), and the parse rate, all on
> the frozen snapshot `kb-data/db/kb-20261121-aa0a2ae.sqlite` (the target of `db/current` on
> 2026-11-24). Own code in `verifier/scripts/`, predictions committed before any draw
> (`verifier/JOURNAL.md` entry 1, commit 2e05c967, seed 20261124), registered runs listed per item.
> Verdict words: CONFIRMED (my own reading or computation agrees), NOT CONFIRMED (I could not
> reproduce it, or it holds only in part), WRONG (my reading contradicts it), NOT CHECKED.
> Independence: I read the lead's batch-9 review section (REVIEW-wave3.md from L105) for the

## Null results and failed runs

- `kb-20261115-154858-b0d8c8f`: failed (exit 1), K9: first quality report (C1-C10; golden retrieval in text and hybrid mode; independent equation count on 41 papers)
- `kb-20261115-164121-5aca10c`: failed (exit 1), embed helper: test E4, ten questions and six equation lookups of tracks/kb/embed/questions10.yaml by text, vector and hybrid search on snapshot kb-20261115-621430e
- `kb-20261115-182907-3f69615`: failed (exit 1), kb lead W9: fetch 2201.09277 and 2107.06643 (DOIs of C and D), verify-downloads, ingest, tags, embed, check, snapshot
- `kb-20261119-143242-737909d`: failed (exit 2), pdf_meta P6: vectors for the chunks of the three PDF papers (orphans of the old 2201.03458 chunks removed), coverage check, citation edges resolved
- `kb-20261124-233445-89478ae`: failed (exit 1), kb lead b13: claims of the KB-G3 verifier (682 superseded, 781, 714, 809, 804) and the ingest4 claims (409, 447, 449, 450, 452); prediction C1
- `kb-20261125-041256-d4741a7`: failed (exit 1), kb verifier2 item 2: strata of the live supported claims on snapshot kb-20261125-2f97258, seeded draw of 40 (seed 20261126), item-1 list; C1 recount and snapshot sha256

## Open risks


Updated 2026-11-24 (kb lead, wave 3 batch 13). Likelihood and effect: low / medium / high.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Parse errors hidden behind a good quality score give tracks wrong equation numbers, locators or missing citation edges (wave 1: 28 papers; wave 2: astro-ph/0003278; wave 2b verifier: 11 papers with status ok and no bibliography entry, 502 reference items lost) | high | high | three independent counters agree on equations (W4, verifier P); the verifier's zero-bibliography scan (run kb-20261119-161909-08df7ea); wave-3 verifier: 21 status-ok papers fail its definition, parse rate 95.6 % (4.5 papers above the bar; run kb-20261121-080843-98907be, lead recount kb-20261121-125746-a03875b) | parser fix for REVTeX-3 `references`, AASTeX `\reference`, `\bi` macros, `\harvarditem`; status review when `\cite` is present and no entry; re-ingest after a chunk remap of the claims |
| Re-ingesting a paper renumbers its chunks and equations, so claims (chunk_id), vectors and tags point at nothing | high (any re-ingest) | medium | `kb embed --check --work`; claims with_chunk count in `kb claim stats` | remap claim chunk ids from their flat ranges after an ingest (to build); until then re-ingest only papers without claims, and run tags, embed, check after it |
| A track takes a `located` claim for a checked one, or a `checked` claim for right as worded | medium | high | `kb claim show` gives status and checked_by; audits 29/30, 9/10, verifier C 10/10; KB-G3 verifier S2 17/18; VERIFIER2 P stratum 12/14 (pooled P 29/32 = 90.6 %) | only `checked` claims count as read by a person; even those are read at the locator before citing (223, 574 were a pointer and a fragment that audits passed; superseded in batch 17) |
| A claim labelled as supported is wrong as worded (KB-G3 verifier: 682, 6/60; claims3 weak class: 4/30 wrong; VERIFIER2: machine-located 10/13, pooled with claims3's WA 28/35 = 80 %, CP 63-92 %, about 86 of 529 unread expected wrong) | high (machine-located class) | high | stratified samples of fresh verifiers; claims3/scripts/weak_class.py (exclude kb-claims3 annotations before reuse); starts with 'and', 'i.e.', 'which', 'see' | supersede, never verify a wrong text; the seven of VERIFIER2 superseded in batch 17 (882-888); a second weak-class pass on WA (about 400 claims) |
| fulltext label on abstract-level readings (448, 753, 765; 409, 447, 449, 450) is read as more than it is | medium | low | evidence texts say "abstract lines" | a person-set label or flag for abstract readings (KB-G3 OPEN O4) |
| Retrieval generalizes worse than the golden numbers say (re-ranking chosen in-sample) | low (was medium) | medium | blind held-out set of 24 (verify_g2): paper 87.5/91.7/87.5 %, at or above golden; location 54-62 % below golden 66-78 % | never tune on tracks/kb/verify_g2/heldout.yaml; a new held-out set before any further tuning |
| A locator copied from a hit loses its snapshot (verifier C6b) | low (was medium) | medium | since batch 9 `kb show`, `kb cites` and every JSON hit carry the snapshot id | cite the id with the locator; remap claims at every re-ingest |
| The parameter index goes stale again as core releases change options | medium (index at main 47ab19ab after core-v0.6, run kb-20261121-231826-3b32fc1; db/current aa0a2ae carries it) | medium | `kb code --kind param` against the newest READY | re-index with `kb ingest repo --this` after each release, then snapshot |
| Paper text or third-party figures leave the machine through commits | low | high | `git status` and sizes before each commit; reading samples stay in scratch | scripts write only ids, counts and our wording; pre-commit hook dry run on main (wave 3a) |
| Two writers of kb.sqlite undo each other (wave 2: a `--rebuild` deleted 330 rows; wave 2b: three helpers and wt/kb-brief beside the lead) | low | medium | ingest_log; locks/kb-writer.lock held by every `kb` write | one writer at a time under the lock; snapshots taken by the lead only |
| A download escapes its directory or is executed | low | high | `kb verify-downloads`; the fetch command's limits (decision 0015) | never run code from kb-data/raw; read with python3 -I code outside it |
| PDF text of the 1994-95 papers carries wrong symbols (cmsy/cmex characters mapped as Greek; 3 of 20 sampled) | medium | low | the lead's reading sample (B1) | equations of PDF papers are not indexed; quote PDF papers only after reading the PDF itself |
| Upstream AthenaK publishes a particle-spacetime coupling and nobody notices | medium | medium | `kb watch upstream` each wave; last run 2026-11-20 (code_kb, watch 20261120T221926Z): src/z4c changed on project/bbh and project/largesim-m1, nothing in src/particles | run each wave; message to core when src/particles or src/z4c change |
| Tracks treat `claimed` paper-code links as verified | low (was medium) | medium | 19 verified, 5 claimed, 1 refuted (code_kb; header of kb/curated/paper_code_links.tsv states it) | core names tests for M18-M20, M24, M25 (message 20261121T233243Z) |
| Snapshots fill the disk (about 1 GB each, thirteen now; /data at 85 % on 2026-11-25) | medium | low | `du -sh kb-data/db`; `df -h /data` | keep the ones cited in notes (f2fcda5, 621430e, 44b7406, a848a06, a782f1e, bbaafe5, aa0a2ae, 9872d21, 2f97258); prune others by name |
| Packages cut by a usage limit leave half-done work: decisions written but never run (claims_tracks C1, D1, E1 at 14:35 PST), private code copies (ingest3) and predictions that drift from the code they predict | high (happened 2026-11-20) | medium | `git status` at each lead session; HANDOFF table of cut packages | resume only from committed state plus a reread of uncommitted decisions; never run a generated batch without reading its decisions; record the cut in the package journal |

| An automatic check or re-seed overwrites a locator a person set (claims_tracks request) | low (guarded since batch 9) | medium | `kb claim check` prints "pinned N" | the guard keys on relocate events; a person who edits a locator by SQL bypasses it: use `kb claim relocate` |
| The manifest count in decisions and the store disagree (decision 0027 says 745; the store has 744 after the drop of gr-qc/0608095) | medium | low | test_meta_papers counts 60/744 | message to orch 20261121 batch 9 |
| Citation edges missing where references print ids in formats the parser does not take (4538 of 52725 printed ids; verifier KB-G3 item 3) | high | medium | the verifier's whole-snapshot tally (run kb-20261124-132849-3ebad97) | parser formats listed in HANDOFF, then re-resolve and snapshot |
| A tool step rewrites provenance it did not create (batch 15: supersede --to replaced the successor's checked_by/checked_at; five rows) | low (fixed, test added) | medium | lead review: diff of claims, claim_meta and locators against the last snapshot, every changed id must be in the package ledger (lead_b15/scripts/review_claims3.py) | run that diff in every lead review of a claims package |
| The label set has no class for a repository or tool fact nor a locator form for a metadata record, so such claims are stored as to_verify or abstract without a locator and read as weaker or stronger than they are (892-895; 709, 844) | medium | low | KB-G3 OPEN.md O9 | a schema change (label 'repository', locator forms 'repo:' and 'meta:') proposed in service mode |

## Decision requested from the group

Signed 2026-11-24 by the orchestrator, pass with reservations (coord/GATES.md; decision 0037 item 1). Batch 17: the seven claims of VERIFIER2.md superseded (882-888), the twelve abstract claims without a locator processed (OPEN.md O8), the machine-located rate 28/35 written beside the mixed rate (O7); snapshot kb-20261125-56c4b53.
