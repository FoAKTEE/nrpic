# Stage report: kb KB-G2

Date: 2026-11-19 · branch `kb/main` at `72bce805da7e` · checklist
`tracks/kb/stage/KB-G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/kb/KB-G2-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C8 FAIL
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/KB-G2/STAGE_REPORT.md` | written by this command |
| `stage/KB-G2/EVIDENCE.md` | present |
| `stage/KB-G2/OPEN.md` | present |
| `stage/KB-G2/CHECKLIST.md` | present |
| `stage/KB-G2/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/KB-G2/REVIEW.md` | present |
| scoping text | `stage/KB-G2/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate KB-G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | All papers and repositories ingested | Papers: 710 of 710 manifest ids ingested (684 of brief section 17, gr-qc/9412071 from its PDF since wave 2b, run kb-20261119-142651-7318d01; 26 additions of decision 0016 item 6), QA C1 of run kb-20261119-161633-1d05960 on snapshot kb-20261119-a782f1e (kb/QA_REPORT.md). Repositories: 63 of 63 of the manifest and this repository (re-indexed at main 5deee18, run kb-20261119-161451-e15d1b8). Quality caveat, not an ingestion gap: 20 TeX papers have no bibliography entry (OPEN.md). | PASS |
| C2 | The QA report meets the parse success rate and retrieval hit rate written in CHARTER (thresholds: coord/CHARTER.md, "Gates of the knowledge base"; items below) | kb/QA_REPORT.md (run kb-20261119-161633-1d05960, snapshot kb-20261119-a782f1e) meets both thresholds of the charter: C3 and C4 below. Figure tracks/kb/note/figures/fig_kbg2.png (run kb-20261119-162642-25012f7), inspected. | PASS |
| C3 | Parse success rate: at least 95 per cent of the ingested papers are parsed successfully. | Parse status ok for 684 of 710 ingested papers = 96.3 % (23 review, 3 pdf); 96.8 % if a paper read from its PDF counts. Caveat of the KB-G1 verifier: 11 papers with status ok have no bibliography entry; counted as failures the rate is 673/710 = 94.8 % (676/710 = 95.2 % with the PDF papers). So the bar is met on the status the knowledge base records and is borderline under the strictest reading; the bibliography-parser fix (OPEN.md) removes the doubt. fig_kbg2.png panel (a). | PASS |
| C4 | Retrieval hit rate: at least 80 per cent of the golden questions are answered with the right paper among the top ten results; the hit at the answer location is reported, not gating. | Right paper in the top ten for 28 of 32 golden questions = 87.5 % with hybrid search and with rerank (text only: 27 = 84.4 %); answer location in the top ten (reported, not gating): rerank 25 = 78.1 %, hybrid 23 = 71.9 %, text 21 = 65.6 %. Run kb-20261119-161633-1d05960 on kb-20261119-a782f1e; equal question by question to the retrieval helper's run on a848a06 except q01 hybrid location rank 7 -> 6; the helper's ranked lists rescored by the lead with own code (run kb-20261119-155310-e600e38). Caveat: the re-ranking was chosen on these 32 questions (in-sample); a held-out set is requested from orch. | PASS |
| C5 | Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10) | kb opens db/current by default; snapshots are mode 0444 (kb-20261119-a782f1e: -r--r--r--). | PASS |
| C6 | `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10) | Snapshot kb-20261119-a782f1e (run kb-20261119-161451-e15d1b8; sha256 a782f1ee...), db/current; every number of this package is on it except the retrieval helper's R4 (a848a06), named as such. | PASS |
| C7 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (and ../REVIEW-wave2.md, section wave 2b); scope SCOPE.md (as ../KB-G0/SCOPE.md). | PASS |
| C8 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot | No verifier report for KB-G2. The KB-G1 verifier of wave 2b did not check retrieval, embeddings, metadata or parse rates (VERIFIER.md of KB-G1, 'Not checked'). The second checks so far are the lead's own (B1, B2: helper numbers reproduced exactly). Requested from orch (outbox, kb-g2-verifier). | FAIL |
| C9 | Null results and failed runs are on record (manifests and JOURNAL) | Failed predictions on record: tracks/kb/JOURNAL.md B2 (C4 ratio of my own instrument), tracks/kb/retrieval/JOURNAL.md R3 (refuted), R4 (25 instead of >= 26), tracks/kb/pdf_meta/JOURNAL.md P1, P3, P4 parts; failed run kb-20261119-143242-737909d (an option kb embed does not have). | PASS |
| C10 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (kb lead, wave 2b, 2026-11-19). | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T16:34:40Z, clean export of `72bce805da7e`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 72bce805da7e (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G2-72bce80-20261119T163335Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G2/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 3 figures, each with its script |
| min-figs | PASS | 0 schematics and 3 data figures (brief 13.4 asks at least 0 and 0 at KB-G2) |
| runs | PASS | 117 run manifests finished (77 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 76 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 38 lines |
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

MISSING: the verifier subagent has not reported (`stage/KB-G2/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `kb-20261115-182907-3f69615`: failed (exit 1), kb lead W9: fetch 2201.09277 and 2107.06643 (DOIs of C and D), verify-downloads, ingest, tags, embed, check, snapshot
- `kb-20261119-143242-737909d`: failed (exit 2), pdf_meta P6: vectors for the chunks of the three PDF papers (orphans of the old 2201.03458 chunks removed), coverage check, citation edges resolved

## Open risks


Updated 2026-11-19 (kb lead, wave 2b). Likelihood and effect: low / medium / high.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Parse errors hidden behind a good quality score give tracks wrong equation numbers, locators or missing citation edges (wave 1: 28 papers; wave 2: astro-ph/0003278; wave 2b verifier: 11 papers with status ok and no bibliography entry, 502 reference items lost) | high | high | three independent counters agree on equations (W4, verifier P); the verifier's zero-bibliography scan (run kb-20261119-161909-08df7ea) | parser fix for REVTeX-3 `references`, AASTeX `\reference`, `\bi` macros, `\harvarditem`; status review when `\cite` is present and no entry; re-ingest after a chunk remap of the claims |
| Re-ingesting a paper renumbers its chunks and equations, so claims (chunk_id), vectors and tags point at nothing | high (any re-ingest) | medium | `kb embed --check --work`; claims with_chunk count in `kb claim stats` | remap claim chunk ids from their flat ranges after an ingest (to build); until then re-ingest only papers without claims, and run tags, embed, check after it |
| A track takes a `located` claim for a checked one | medium | high | `kb claim show` gives status and checked_by; audits 29/30, 9/10, verifier C 10/10 | only `checked` claims count as read by a person (39 now) |
| Retrieval generalizes worse than the golden numbers say: the re-ranking was chosen on the 32 questions the helper inspected; the ten held-out share passages with them | medium | medium | paper hit 28/32, answer location 25/32 (rerank) on a782f1e (Q1) | a held-out set of 20 or more questions by someone who has not seen R3/R4 (requested from orch) before any further tuning |
| KB-G2 judged on the lead's own QA run without a second agent | medium | medium | CHECKLIST C8 of KB-G2 | verifier for KB-G2 requested from orch |
| The parameter index goes stale again as core releases change options (wave 2b: 101 pairs missing at a1c2237) | high | medium | `kb code ... --repo local/nrpic`; repos.commit_sha | `kb ingest repo --this --ref main` after each core release merged into main, then `kb link load`, `kb link check`, `kb snapshot` |
| Paper text or third-party figures leave the machine through commits | low | high | `git status` and sizes before each commit; reading samples stay in scratch | scripts write only ids, counts and our wording; pre-commit hook dry run on main (wave 3a) |
| Two writers of kb.sqlite undo each other (wave 2: a `--rebuild` deleted 330 rows; wave 2b: three helpers and wt/kb-brief beside the lead) | low | medium | ingest_log; locks/kb-writer.lock held by every `kb` write | one writer at a time under the lock; snapshots taken by the lead only |
| A download escapes its directory or is executed | low | high | `kb verify-downloads`; the fetch command's limits (decision 0015) | never run code from kb-data/raw; read with python3 -I code outside it |
| PDF text of the 1994-95 papers carries wrong symbols (cmsy/cmex characters mapped as Greek; 3 of 20 sampled) | medium | low | the lead's reading sample (B1) | equations of PDF papers are not indexed; quote PDF papers only after reading the PDF itself |
| Upstream AthenaK publishes a particle-spacetime coupling and nobody notices | medium | medium | `kb watch upstream` each wave; last run kb-20261115-154646-234060c | run it at the start of the next kb session (not run in wave 2b) |
| Tracks treat `claimed` paper-code links as verified | medium | medium | `kb link list`; 25/25 resolve at 5deee18 (run kb-20261119-161451-e15d1b8) | core names tests (outbox paper-code-links, open since wave 1) |
| Snapshots fill the disk (about 1 GB each, nine now) | medium | low | `du -sh kb-data/db` | keep the ones cited in notes (f2fcda5, 621430e, 44b7406, a848a06, a782f1e); prune others by name |

## Decision requested from the group

Review of KB-G2 by the orchestrator after a verifier report (CHECKLIST C8 FAIL until then): the two thresholds of decision 0016 item 6 are met on snapshot kb-20261119-a782f1e (parse ok 684/710 = 96.3 %, 94.8 % if the 11 status-ok papers without bibliography count as failures; right paper in the top ten 28/32 = 87.5 %). Assign a KB-G2 verifier (outbox kb-g2-verifier). The lead does not pass the gate.

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
