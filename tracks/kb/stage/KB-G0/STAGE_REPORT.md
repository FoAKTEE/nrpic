# Stage report: kb KB-G0

Date: 2026-11-21 · branch `kb/main` at `42d4ee7eedc8` · checklist
`tracks/kb/stage/KB-G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/kb/KB-G0-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- verify reported FAIL: clean

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/KB-G0/STAGE_REPORT.md` | present |
| `stage/KB-G0/EVIDENCE.md` | present |
| `stage/KB-G0/OPEN.md` | present |
| `stage/KB-G0/CHECKLIST.md` | present |
| `stage/KB-G0/VERIFIER.md` (verifier's report) | present |
| `stage/KB-G0/REVIEW.md` | present |
| scoping text | `stage/KB-G0/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate KB-G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Tools chosen, directories in place | Tool choices with reasons: kb/JOURNAL.md (K0 tool choice, K2-K3 tool choices, tool choice for the code index) and kb/EMBEDDING.md (K4 model); environments frozen in kb/requirements-k0.lock, -k4.lock, -k6.lock (kb/.venv, uv). Layout of brief 12.2 in place (kb init, wave 1): kb-data/{raw,meta,build/{tex,code},db,manifests,logs}, checked 2026-11-15T18:30Z. Verifier (VERIFIER.md, run kb-20261121-080038-306bcdd): C1a tools chosen CONFIRMED, C1c directories CONFIRMED, C1b reasons NOT CHECKED (journal closed to it). Lead, 2026-11-21: the reasons are in kb/JOURNAL.md lines 24-36 (K0), 205 ff. (K2-K3), 231 ff. (code index) and kb/EMBEDDING.md 'Why this model'; now also named in kb/README.md, section 'Tool choices and departures from the layout of brief 12.2', which records the two departures the verifier found (uv.lock replaced by requirements-k0/k4/k6.lock; curated/seed_claims.jsonl replaced by `kb claim seed` from the tracks' notes; the brief's own statements not seeded yet). | PASS |
| C2 | Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10) | kb opens kb-data/db/current by default (kb/kbtool/cli.py and papers_cli.py: '--db default db/current'); snapshots are written mode 0444 (kb/kbtool/db.py snapshot), db/current -> kb-20261115-3826a68.sqlite is -r--r--r--; harness doctor row kb PASS in wt/kb (coord/digests/harness-wave-2.md: checks that db/current refuses a write). | PASS |
| C3 | `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10) | Snapshots at the end of each stage: kb-20261115-f2fcda5 (KB-G1, wave 1, run kb-20261115-141500-b2e57be), kb-20261115-621430e (K4-K5, run kb-20261115-164041-5aca10c), kb-20261115-3826a68 (K8 load, run kb-20261115-182741-7dafdf9) and kb-20261115-44b7406 (runs kb-20261115-182907-3f69615 and kb-20261115-183052-0f8245e) and kb-20261115-a848a06 (run kb-20261115-183921-31d5b77, db/current at the end of the session); the answers posted to the tracks name the snapshot they cite. Verifier: CONFIRMED (9 snapshots 0444, sha256 prefix equal to the name; ids recorded in the snapshot runs; run kb-20261121-080038-306bcdd); not checked by it: whether each was taken at the end of a stage. Lead recount of the KB-G2 snapshot a782f1e: run kb-20261121-125746-a03875b. | PASS |
| C4 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | This directory: SCOPE.md (the scope of kb is brief section 12 and charter 9.10), CHECKLIST.md, EVIDENCE.md, OPEN.md, STAGE_REPORT.md (nrpic-stage report), REVIEW.md (points to the lead reviews: wave 1 JOURNAL L0-L11, wave 2 ../REVIEW-wave2.md, wave 3 ../REVIEW-wave3.md), VERIFIER.md. | PASS |
| C5 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot | VERIFIER.md (helper verify_g2, wave 3, fresh context, given artefacts and criteria; runs kb-20261121-080038-306bcdd, kb-20261121-081226-a4025cf): C1a, C1c, C2, C3, C6 CONFIRMED; C1b NOT CHECKED (checked by the lead, C1); three minor defects (two absent layout files, raw source.bin mode 0664, reasons not in the tool's README). Rechecked by the lead from the artefacts: ../REVIEW-wave3.md (run kb-20261121-125746-a03875b). | PASS |
| C6 | Null results and failed runs are on record (manifests and JOURNAL) | Failed runs kept with manifests: kb-20261115-154858-b0d8c8f (exit 1, IndexError), kb-20261115-164121-5aca10c (exit 1, same cause), kb-20261115-181519-d78b8d4 (output misplaced); refuted predictions recorded (embed E4, E5 v1, E3 equation truncation; claims P5, P6; lead L2, L11, W2) in tracks/kb/JOURNAL.md and the package journals. Verifier: CONFIRMED, with a defect of the record: the first two manifests carried the status word 'finished' with exit code 1, read as completed by nrpic-run; corrected to 'failed' with a status_note on 2026-11-21 (lead, ../REVIEW-wave3.md). kb-20261115-181519-d78b8d4 exited 0; its failure (misplaced output) is in the journal only, as stated. | PASS |
| C7 | STATUS.md, JOURNAL.md and HANDOFF.md are current | tracks/kb/STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended by the kb lead, wave 3 batch 3 (2026-11-21), the session that brought this package up to date. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T13:10:32Z, clean export of `42d4ee7eedc8`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 11 uncommitted paths: commit them first (tracks/kb/code_kb/JOURNAL.md, tracks/kb/claims_tracks/decisions/C1.tsv, tracks/kb/claims_tracks/decisions/C1_annot.tsv, tracks/kb/claims_tracks/decisions/D1.tsv, tracks/kb/claims_tracks/decisions/D1_annot.tsv) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 42d4ee7eedc8 (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G0-42d4ee7-20261121T130704Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G0/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 3 figures, each with its script |
| min-figs | PASS | 0 schematics and 3 data figures (brief 13.4 asks at least 0 and 0 at KB-G0) |
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

`tracks/kb/stage/KB-G0/VERIFIER.md` present; its first lines:

> # KB-G0: report of the independent verifier
> 
> Verifier: helper `verify_g2` of kb (wave 3; batch 2b, 2026-11-21), the same session that
> verified KB-G2 (tracks/kb/stage/KB-G2/VERIFIER.md; method and independence rules there). Until
> this file was committed I did not open tracks/kb/stage/** (other than writing the two
> VERIFIER.md files), the lead's STATUS/HANDOFF/JOURNAL/RISKS/PLAN-wave3, kb/QA_REPORT.md or
> kb/STATE.json. Evidence: run kb-20261121-080038-306bcdd (checks.json; script
> tracks/kb/verify_g2/scripts/checks_c1_c5_c6.py), journal entries 7-8 of
> tracks/kb/verify_g2/JOURNAL.md.
> 
> ## Verdicts
> 

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

Lead (kb, wave 3 batch 3): package complete for the gate review; all seven items PASS with the independent verifier's VERIFIER.md and the lead's check of it (stage/REVIEW-wave3.md, run kb-20261121-125746-a03875b). Harness FAIL only on 'clean': eleven uncommitted files of the cut packages claims_tracks and code_kb, left in place on purpose (HANDOFF.md); waiver requested. The lead does not pass the gate.
