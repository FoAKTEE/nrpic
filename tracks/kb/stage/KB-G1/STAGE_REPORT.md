# Stage report: kb KB-G1

Date: 2026-11-15 · branch `kb/main` at `d8a95bbe6425` · checklist
`tracks/kb/stage/KB-G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/kb/KB-G1-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C8 FAIL
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/KB-G1/STAGE_REPORT.md` | present |
| `stage/KB-G1/EVIDENCE.md` | present |
| `stage/KB-G1/OPEN.md` | present |
| `stage/KB-G1/CHECKLIST.md` | present |
| `stage/KB-G1/REVIEW.md` | present |
| scoping text | `stage/KB-G1/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate KB-G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The inventory report | Download inventory: kb/reports/verify-downloads.md (wave 1, run kb-20261115-140336-29f15a1) and reruns kb-20261115-154547-12ef9f0, kb-20261115-182907-3f69615 (manifest 684: ok 683, problem 1 = gr-qc/9412071 PostScript; 63/63 repositories; 26 extras). Metadata part of K1 fetched in wave 2 (run kb-20261115-182505-7e3a0b5: arXiv-API records 708/708, INSPIRE 704/708); the title and author comparison with brief section 16 is not done yet (OPEN.md). | PASS |
| C2 | All priority-3 papers ingested | 47 of 47 priority-3 papers ingested (45 ok, 2 review): priority3_ingestion.tsv (run kb-20261115-141457-b2e57be); unchanged in wave 2. | PASS |
| C3 | Code index and parameter index of AthenaK | Upstream AthenaK c5a0d7f and this tree: kb/reports/code_index.md, code_params.md, code_params_*.tsv (64 repositories, 3454 parameter rows; wave 1); upstream unchanged at the wave-2 watch (run kb-20261115-154646-234060c). | PASS |
| C4 | The answers to the first questions | FIRST_QUESTIONS.md: nine answers with file:line locators (snapshot kb-20261115-f2fcda5); open sub-points in OPEN.md. Wave 2 adds the metadata core asked for (2611.12831: submitted 2026-11-09, gr-qc with astro-ph.GA, astro-ph.HE, physics.plasm-ph, '37 pages, 23 figures'; run kb-20261115-182505-7e3a0b5). | PASS |
| C5 | Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10) | kb opens db/current by default; snapshots are mode 0444; harness doctor row kb PASS in wt/kb. | PASS |
| C6 | `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10) | Snapshot of this update: kb-20261115-44b7406 (run kb-20261115-183052-0f8245e, db/current); the posted answers name it. | PASS |
| C7 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (wave-1 checks L0-L11 in tracks/kb/JOURNAL.md; wave 2 in ../REVIEW-wave2.md); scope: ../KB-G0/SCOPE.md (brief section 12, charter 9.10). | PASS |
| C8 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md: the package's numbers recomputed from the run manifests and the snapshot | No VERIFIER_REPORT.md: no verifier was assigned to kb in waves 1 and 2 (coord/digests/wave-1-plan.md, wave-2-plan.md); the lead's rechecks (JOURNAL L0-L11, W1-W9; ../REVIEW-wave2.md) are the only second check. Requested from orch. | FAIL |
| C9 | Null results and failed runs are on record (manifests and JOURNAL) | Failed runs on record: kb-20261115-154858-b0d8c8f, kb-20261115-164121-5aca10c, kb-20261115-181519-d78b8d4, kb-20261115-182907-3f69615 (manifests kept); refuted predictions in tracks/kb/JOURNAL.md (L2, L11, W2) and the package journals (E3 truncation, E4, E5 v1, E6; P5, P6). | PASS |
| C10 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (kb lead, wave 2). | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T18:35:17Z, clean export of `c65ab4d48ec7`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of c65ab4d48ec7 (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G1-c65ab4d-20261115T183440Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); REVIEW.md present |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 1 figures, each with its script |
| min-figs | PASS | 0 schematics and 1 data figures (brief 13.4 asks at least 0 and 0 at KB-G1) |
| runs | PASS | 85 run manifests finished (74 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 74 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 28 lines |
| rerun | PASS | 3 of 3 scripts and commands ran cleanly in the export |
| compare | PASS | 2 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 2 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_w2_review.* | note/scripts/fig_w2_review.py | data | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `kb-20261115-182907-3f69615`: failed (exit 1), kb lead W9: fetch 2201.09277 and 2107.06643 (DOIs of C and D), verify-downloads, ingest, tags, embed, check, snapshot

## Open risks


Updated 2026-11-15 (kb lead, wave 1). Likelihood and effect: low / medium / high.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Parse errors hidden behind a good quality score give tracks wrong equation numbers or locators (found twice this session: \nc aliases, composite shorthands; 28 papers) | medium | high | independent counts on drawn papers (journal L5, L10, L11); equation rows per paper against `\begin{equation` counts | K9: a sampled independent-count check in `kb qa run`; notes cite the snapshot id so a later fix can be traced |
| No sanctioned metadata path: no titles/abstracts for 36/27 papers, no cross-check with brief 16, 17661 unresolved bibliography entries; KB-G2 blocked | high | medium | outbox `__to-orch__metadata-path` | parse what the store has; ask once per week |
| Paper text or third-party figures leave the machine through commits (reports, curated statements) | low | high | `git diff --stat` before each commit; reports carry ids and counts only | own wording in curated files; nothing under kb-data is committed |
| A download escapes its directory or is executed | low | high | `kb verify-downloads` checks members, links, exec bits, sizes | never run code from kb-data/raw; propose limits in nrpic-fetch-arxiv (outbox) |
| Upstream AthenaK publishes a particle-spacetime coupling and nobody notices | medium | medium | `kb watch upstream` (baseline 2026-11-15, no scheduler) | outbox `__to-orch__watch-scheduler`; run it at the start of each kb session |
| Tracks treat `claimed` paper-code links as verified | medium | medium | `kb link list` shows status | core names tests (outbox `__to-core__paper-code-links`) |
| Equation numbers of real papers cannot be checked against LaTeX output (no .aux, no compiling downloads) | medium | medium | cross-check against `\ref`-resolved numbers in the papers' own text | label numbers as computed by kb; check against the PDF when one is stored |
| Snapshots fill the disk (0.81 GB each, four now) | high | low | `du -sh kb-data/db` | keep the last three and those cited in notes; prune others by name |
| Embedding stage too slow on 8 cores, or no model approved | medium | low | timed scouting run on 1000 chunks | full-text search (exists) until vectors exist; outbox `__to-orch__embedding-model` |
| Other sessions add store entries at any time, so counts move between runs | high | low | verify-downloads reports extras | numbers always with a run id |
| A long-running writer keeps an old module after a fix (lock, parser) | low | medium | process list before a fix lands | restart writers after fixes; one writer at a time |

## Decision requested from the group

KB-G1 of kb (submitted in wave 1) brought up to date: its four criteria stay met, and wave 2 added embeddings, equation tags, the claims layer (688 claims), the first QA report and the K1 metadata on disk. KB-G2 is not met (one manifest paper not ingested; CHARTER has no thresholds; retrieval at the answer location 72 % against the proposed 80 %). Requested: accept KB-G1 on the lead's rechecks or assign a verifier, and write the two KB-G2 thresholds into CHARTER (outbox kb-g2-thresholds).

## Gate status in plain words (kb lead, wave 2)

- KB-G0: met in substance (`../KB-G0/`); the only item not met is the verifier report.
- KB-G1: its four criteria are met; the package fails only on the verifier report (C8), because
  no verifier was assigned to kb in either wave. The lead does not pass the gate; the group decides.
- KB-G2: not met. One manifest paper (gr-qc/9412071, PostScript e-print) is not ingested; CHARTER
  states no parse or retrieval threshold; against kb's own proposal the parse rate is met
  (96.5 %) and the retrieval rate is met for the paper (88 %) but not for the answer location
  (72 %). Details: `OPEN.md`, section "KB-G2".
- Review of the wave-2 helpers: `../REVIEW-wave2.md`.
