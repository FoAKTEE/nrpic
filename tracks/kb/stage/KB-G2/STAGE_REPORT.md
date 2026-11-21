# Stage report: kb KB-G2

Date: 2026-11-21 · branch `kb/main` at `42d4ee7eedc8` · checklist
`tracks/kb/stage/KB-G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/kb/KB-G2-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- verify reported FAIL: clean

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/KB-G2/STAGE_REPORT.md` | present |
| `stage/KB-G2/EVIDENCE.md` | present |
| `stage/KB-G2/OPEN.md` | present |
| `stage/KB-G2/CHECKLIST.md` | present |
| `stage/KB-G2/VERIFIER.md` (verifier's report) | present |
| `stage/KB-G2/REVIEW.md` | present |
| scoping text | `stage/KB-G2/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate KB-G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | All papers and repositories ingested | Papers: 710 of 710 manifest ids ingested (684 of brief section 17, gr-qc/9412071 from its PDF since wave 2b, run kb-20261119-142651-7318d01; 26 additions of decision 0016 item 6), QA C1 of run kb-20261119-161633-1d05960 on snapshot kb-20261119-a782f1e (kb/QA_REPORT.md). Repositories: 63 of 63 of the manifest and this repository (re-indexed at main 5deee18, run kb-20261119-161451-e15d1b8). Quality caveat, not an ingestion gap: 20 TeX papers have no bibliography entry (OPEN.md). Verifier: CONFIRMED (710/710 ids, none extra, group and priority equal; 64/64 repositories with commit and files; run kb-20261121-080038-306bcdd); lead recount by SQL equal (run kb-20261121-125746-a03875b). | PASS |
| C2 | The QA report meets the parse success rate and retrieval hit rate written in CHARTER (thresholds: coord/CHARTER.md, "Gates of the knowledge base"; items below) | kb/QA_REPORT.md (run kb-20261119-161633-1d05960, snapshot kb-20261119-a782f1e) meets both thresholds of the charter: C3 and C4 below. Figure tracks/kb/note/figures/fig_kbg2.png (run kb-20261119-162642-25012f7), inspected. Verifier: CONFIRMED with a remark (the report gives the same retrieval numbers and 26 papers not ok, but states no parse rate against the 95 % bar; to be added at the next `kb qa run`, OPEN.md). | PASS |
| C3 | Parse success rate: at least 95 per cent of the ingested papers are parsed successfully. | Parse status ok for 684 of 710 ingested papers = 96.3 % (23 review, 3 pdf); 96.8 % if a paper read from its PDF counts. Caveat of the KB-G1 verifier: 11 papers with status ok have no bibliography entry; counted as failures the rate is 673/710 = 94.8 % (676/710 = 95.2 % with the PDF papers). So the bar is met on the status the knowledge base records and is borderline under the strictest reading; the bibliography-parser fix (OPEN.md) removes the doubt. fig_kbg2.png panel (a). Verifier (VERIFIER.md, Test 3; runs kb-20261120-223309-14e4cb6, kb-20261121-080834-6c50215, kb-20261121-080843-98907be): CONFIRMED narrowly under an explicit definition (sections, equations, bibliography, abstract available to a reader; gaps read at the source subtracted): 679/710 = 95.6 %, 4.5 papers above the bar; 670/710 = 94.4 % if nine letters with run-in headings count as failures; 658/710 = 92.7 % if an extracted abstract chunk is required. Lead recount from the snapshot by own SQL and own evaluation of that definition: 688 lenient, 679 after the nine gaps, 670 with the letters failed; database columns of the verifier's scan equal to my SQL for 710 of 710 papers (run kb-20261121-125746-a03875b, figure ../review_wave3/figures/fig_lead_check_vg2.png). The margin is thin; the remedy is package ingest3 (bibliography formats, old-style headings). | PASS |
| C4 | Retrieval hit rate: at least 80 per cent of the golden questions are answered with the right paper among the top ten results; the hit at the answer location is reported, not gating. | Right paper in the top ten for 28 of 32 golden questions = 87.5 % with hybrid search and with rerank (text only: 27 = 84.4 %); answer location in the top ten (reported, not gating): rerank 25 = 78.1 %, hybrid 23 = 71.9 %, text 21 = 65.6 %. Run kb-20261119-161633-1d05960 on kb-20261119-a782f1e; equal question by question to the retrieval helper's run on a848a06 except q01 hybrid location rank 7 -> 6; the helper's ranked lists rescored by the lead with own code (run kb-20261119-155310-e600e38). Caveat: the re-ranking was chosen on these 32 questions (in-sample). Verifier: CONFIRMED (golden 27/28/28 of 32, text/hybrid/rerank; runs kb-20261121-074940-08426cc, kb-20261121-080557-06d44ba) and, on its blind held-out set of 24 questions (tracks/kb/verify_g2/heldout.yaml, committed 8fb37106 before the first search), 21/22/21 = 87.5/91.7/87.5 %, at or above the golden rates: no sign of tuning on the golden set (runs kb-20261120-222546-ea894c8, kb-20261121-075156-b84a189). Lead recount of the paper hits and rank-1 counts from the raw hit lists: equal in all six set-mode pairs (run kb-20261121-125746-a03875b). | PASS |
| C5 | Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10) | kb opens db/current by default; snapshots are mode 0444 (kb-20261119-a782f1e: -r--r--r--). Verifier: CONFIRMED, statically and by a dynamic test in a fake data root (run kb-20261121-080038-306bcdd). | PASS |
| C6 | `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10) | Snapshot kb-20261119-a782f1e (run kb-20261119-161451-e15d1b8; sha256 a782f1ee...), db/current; every number of this package is on it except the retrieval helper's R4 (a848a06), named as such. Verifier: C6a (snapshot, id recorded) CONFIRMED; C6b WRONG (partly met) on the stricter reading that the tool's locators carry the id: `kb search`, `eq`, `code` name the database file once per answer (footer, JSON info.database), no single hit carries it, `kb show` and `kb cites` print none (lead's check, run kb-20261121-125746-a03875b: confirmed). Lead's judgement [JUDGEMENT]: brief 12.10 asks that a note citing the knowledge base record the snapshot id, which this package and the answers to the tracks do, so C6 as written is met; the tool should still print the id with every locator. The fix (snapshot id in `kb show`, `kb cites` and in each JSON hit) touches kbtool/papers_cli.py, which the unfinished package ingest3 has changed in its private copy; it lands with or after ingest3 (OPEN.md). | PASS |
| C7 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (and ../REVIEW-wave2.md, section wave 2b; ../REVIEW-wave3.md), VERIFIER.md; scope SCOPE.md (as ../KB-G0/SCOPE.md). | PASS |
| C8 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot | VERIFIER.md (helper verify_g2, wave 3, batches 1 and 2b; fresh context, given artefacts and criteria, not conclusions; own scripts in tracks/kb/verify_g2/scripts, 14 registered runs, two figures): C1, C2, C3, C4, C5, C6a, C9 CONFIRMED; C6b WRONG (partly met); package documents NOT CHECKED (the lead's). Rechecked by the lead from the artefacts (../REVIEW-wave3.md; run kb-20261121-125746-a03875b): every number recomputed held. | PASS |
| C9 | Null results and failed runs are on record (manifests and JOURNAL) | Failed predictions on record: tracks/kb/JOURNAL.md B2 (C4 ratio of my own instrument), tracks/kb/retrieval/JOURNAL.md R3 (refuted), R4 (25 instead of >= 26), tracks/kb/pdf_meta/JOURNAL.md P1, P3, P4 parts; failed run kb-20261119-143242-737909d (an option kb embed does not have). Verifier: CONFIRMED; defect of the record: two wave-1 manifests (kb-20261115-154858-b0d8c8f, kb-20261115-164121-5aca10c) said 'finished' with exit code 1; corrected to 'failed' with a status_note on 2026-11-21. Failed predictions of the verifier itself on record (tracks/kb/verify_g2/README.md: R1, R2, P1, P2, T1). | PASS |
| C10 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended by the kb lead, wave 3 batch 3 (2026-11-21), the session that brought this package up to date. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T13:12:21Z, clean export of `42d4ee7eedc8`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 13 uncommitted paths: commit them first (tracks/kb/code_kb/JOURNAL.md, tracks/kb/stage/KB-G0/VERIFY_RESULTS.json, tracks/kb/stage/KB-G0/VERIFY_RESULTS.md, tracks/kb/claims_tracks/decisions/C1.tsv, tracks/kb/claims_tracks/decisions/C1_annot.tsv) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 42d4ee7eedc8 (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G2-42d4ee7-20261121T131032Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G2/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 3 figures, each with its script |
| min-figs | PASS | 0 schematics and 3 data figures (brief 13.4 asks at least 0 and 0 at KB-G2) |
| runs | PASS | 139 run manifests finished (77 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 76 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 5 of 5 scripts and commands ran cleanly in the export |
| compare | PASS | 6 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 6 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_kbg2.* | note/scripts/fig_kbg2.py | data | to be confirmed by the session |
| note/figures/fig_w2_review.* | note/scripts/fig_w2_review.py | data | to be confirmed by the session |
| note/figures/fig_w2b_review.* | note/scripts/fig_w2b_review.py | data | to be confirmed by the session |

## Verifier report

`tracks/kb/stage/KB-G2/VERIFIER.md` present; its first lines:

> # KB-G2: report of the independent verifier
> 
> Verifier: helper `verify_g2` of kb (wave 3; started 2026-11-20, finished in batch 2b on
> 2026-11-21). Given the artefacts and the criteria, not the conclusions. Until this file was
> committed I did not open tracks/kb/stage/** (other than writing this file and its KB-G0 twin),
> the lead's STATUS/HANDOFF/JOURNAL/RISKS/PLAN-wave3, kb/QA_REPORT.md, kb/STATE.json,
> tracks/kb/{retrieval,pdf_meta,claims}/**, the outbox of kb or scratch/orch. The QA output of
> the named run kb-20261119-161633-1d05960 was read only after my own retrieval and parse numbers
> were committed (journal entry 10, commit c2ccdc3d), for C2.
> 
> Object: the frozen snapshot `kb-data/db/kb-20261119-a782f1e.sqlite`, opened with
> `mode=ro&immutable=1` or passed as `--db`. Nothing was written to kb-data. All numbers come from

## Null results and failed runs

- `kb-20261115-154858-b0d8c8f`: failed (exit 1), K9: first quality report (C1-C10; golden retrieval in text and hybrid mode; independent equation count on 41 papers)
- `kb-20261115-164121-5aca10c`: failed (exit 1), embed helper: test E4, ten questions and six equation lookups of tracks/kb/embed/questions10.yaml by text, vector and hybrid search on snapshot kb-20261115-621430e
- `kb-20261115-182907-3f69615`: failed (exit 1), kb lead W9: fetch 2201.09277 and 2107.06643 (DOIs of C and D), verify-downloads, ingest, tags, embed, check, snapshot
- `kb-20261119-143242-737909d`: failed (exit 2), pdf_meta P6: vectors for the chunks of the three PDF papers (orphans of the old 2201.03458 chunks removed), coverage check, citation edges resolved

## Open risks


Updated 2026-11-21 (kb lead, wave 3 batch 3). Likelihood and effect: low / medium / high.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Parse errors hidden behind a good quality score give tracks wrong equation numbers, locators or missing citation edges (wave 1: 28 papers; wave 2: astro-ph/0003278; wave 2b verifier: 11 papers with status ok and no bibliography entry, 502 reference items lost) | high | high | three independent counters agree on equations (W4, verifier P); the verifier's zero-bibliography scan (run kb-20261119-161909-08df7ea); wave-3 verifier: 21 status-ok papers fail its definition, parse rate 95.6 % (4.5 papers above the bar; run kb-20261121-080843-98907be, lead recount kb-20261121-125746-a03875b) | parser fix for REVTeX-3 `references`, AASTeX `\reference`, `\bi` macros, `\harvarditem`; status review when `\cite` is present and no entry; re-ingest after a chunk remap of the claims |
| Re-ingesting a paper renumbers its chunks and equations, so claims (chunk_id), vectors and tags point at nothing | high (any re-ingest) | medium | `kb embed --check --work`; claims with_chunk count in `kb claim stats` | remap claim chunk ids from their flat ranges after an ingest (to build); until then re-ingest only papers without claims, and run tags, embed, check after it |
| A track takes a `located` claim for a checked one | medium | high | `kb claim show` gives status and checked_by; audits 29/30, 9/10, verifier C 10/10 | only `checked` claims count as read by a person (39 now) |
| Retrieval generalizes worse than the golden numbers say (re-ranking chosen in-sample) | low (was medium) | medium | blind held-out set of 24 (verify_g2): paper 87.5/91.7/87.5 %, at or above golden; location 54-62 % below golden 66-78 % | never tune on tracks/kb/verify_g2/heldout.yaml; a new held-out set before any further tuning |
| A locator copied from a hit loses its snapshot (verifier C6b): chunk ids and ranges change at the next re-ingest | medium | medium | `kb show`, `kb cites`, JSON hits print no snapshot id | print the id with every locator (after ingest3 lands); until then notes record the snapshot id by hand (brief 12.10) |
| The parameter index goes stale again as core releases change options (wave 2b: 101 pairs missing at a1c2237) | high (now: index at 5deee18, core-v0.4 and core-v0.5 since merged, 86 options missing) | medium | `kb code ... --repo local/nrpic`; repos.commit_sha | `kb ingest repo --this --ref main` after each core release merged into main, then `kb link load`, `kb link check`, `kb snapshot` (next action 2 of STATUS) |
| Paper text or third-party figures leave the machine through commits | low | high | `git status` and sizes before each commit; reading samples stay in scratch | scripts write only ids, counts and our wording; pre-commit hook dry run on main (wave 3a) |
| Two writers of kb.sqlite undo each other (wave 2: a `--rebuild` deleted 330 rows; wave 2b: three helpers and wt/kb-brief beside the lead) | low | medium | ingest_log; locks/kb-writer.lock held by every `kb` write | one writer at a time under the lock; snapshots taken by the lead only |
| A download escapes its directory or is executed | low | high | `kb verify-downloads`; the fetch command's limits (decision 0015) | never run code from kb-data/raw; read with python3 -I code outside it |
| PDF text of the 1994-95 papers carries wrong symbols (cmsy/cmex characters mapped as Greek; 3 of 20 sampled) | medium | low | the lead's reading sample (B1) | equations of PDF papers are not indexed; quote PDF papers only after reading the PDF itself |
| Upstream AthenaK publishes a particle-spacetime coupling and nobody notices | medium | medium | `kb watch upstream` each wave; last run 2026-11-20 (code_kb, watch 20261120T221926Z): src/z4c changed on project/bbh and project/largesim-m1, nothing in src/particles | run each wave; message to core when src/particles or src/z4c change |
| Tracks treat `claimed` paper-code links as verified | medium | medium | `kb link list`; 25/25 resolve at 5deee18 (run kb-20261119-161451-e15d1b8) | core names tests (outbox paper-code-links, open since wave 1) |
| Snapshots fill the disk (about 1 GB each, nine now) | medium | low | `du -sh kb-data/db` | keep the ones cited in notes (f2fcda5, 621430e, 44b7406, a848a06, a782f1e); prune others by name |
| Packages cut by a usage limit leave half-done work: decisions written but never run (claims_tracks C1, D1, E1 at 14:35 PST), private code copies (ingest3) and predictions that drift from the code they predict | high (happened 2026-11-20) | medium | `git status` at each lead session; HANDOFF table of cut packages | resume only from committed state plus a reread of uncommitted decisions; never run a generated batch without reading its decisions; record the cut in the package journal |

## Decision requested from the group

Lead (kb, wave 3 batch 3): package complete for the gate review; all ten items PASS on snapshot kb-20261119-a782f1e with the independent verifier's VERIFIER.md and the lead's check of it (stage/REVIEW-wave3.md). Reservations (OPEN.md): parse success 95.6 % under the verifier's definition, a margin of 4.5 papers (94.4 % and 92.7 % under stricter readings); C6 met on the brief's wording, WRONG on the verifier's stricter reading (no snapshot id on each tool locator), fix after ingest3. Harness FAIL only on 'clean' (cut packages' files); waiver requested. The lead does not pass the gate.

## Gate status in plain words (kb lead, wave 2b, 2026-11-19)

- Criteria of brief 12.10: all papers (710 of 710) and repositories (63 of 63 and this repository)
  ingested; the QA report on snapshot kb-20261119-a782f1e meets both thresholds of the charter:
  parse success 684/710 = 96.3 % (>= 95 %), right paper in the top ten for 28 of 32 golden
  questions = 87.5 % (>= 80 %); answer location 25/32 = 78.1 % with `kb search --rerank` (reported).
- Caveats stated, not hidden: 11 papers with status ok have no bibliography entry (KB-G1
  verifier), which makes the strict parse rate 94.8 %; the re-ranking was chosen on the same 32
  questions (in-sample).
- The verdict FAIL above is for the missing verifier report only (C8); `nrpic-stage verify` passes
  on a clean export. The package is not complete for the orchestrator's review until a verifier
  has recomputed it (requested: outbox kb-g2-verifier). The lead does not pass the gate.
