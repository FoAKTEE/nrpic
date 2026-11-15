# Stage report: kb KB-G0

Date: 2026-11-15 · branch `kb/main` at `d8a95bbe6425` · checklist
`tracks/kb/stage/KB-G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/kb/KB-G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C5 FAIL
- verify ran on 7c4bb53; files changed since: tracks/kb/stage/KB-G1/VERIFY_RESULTS.json, tracks/kb/stage/KB-G1/VERIFY_RESULTS.md (run verify again)
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/KB-G0/STAGE_REPORT.md` | written by this command |
| `stage/KB-G0/EVIDENCE.md` | present |
| `stage/KB-G0/OPEN.md` | present |
| `stage/KB-G0/CHECKLIST.md` | present |
| `stage/KB-G0/REVIEW.md` | present |
| scoping text | `stage/KB-G0/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate KB-G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Tools chosen, directories in place | Tool choices with reasons: kb/JOURNAL.md (K0 tool choice, K2-K3 tool choices, tool choice for the code index) and kb/EMBEDDING.md (K4 model); environments frozen in kb/requirements-k0.lock, -k4.lock, -k6.lock (kb/.venv, uv). Layout of brief 12.2 in place (kb init, wave 1): kb-data/{raw,meta,build/{tex,code},db,manifests,logs}, checked 2026-11-15T18:30Z. | PASS |
| C2 | Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10) | kb opens kb-data/db/current by default (kb/kbtool/cli.py and papers_cli.py: '--db default db/current'); snapshots are written mode 0444 (kb/kbtool/db.py snapshot), db/current -> kb-20261115-3826a68.sqlite is -r--r--r--; harness doctor row kb PASS in wt/kb (coord/digests/harness-wave-2.md: checks that db/current refuses a write). | PASS |
| C3 | `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10) | Snapshots at the end of each stage: kb-20261115-f2fcda5 (KB-G1, wave 1, run kb-20261115-141500-b2e57be), kb-20261115-621430e (K4-K5, run kb-20261115-164041-5aca10c), kb-20261115-3826a68 (K8 load, run kb-20261115-182741-7dafdf9) and kb-20261115-44b7406 (runs kb-20261115-182907-3f69615 and kb-20261115-183052-0f8245e); the answers posted to the tracks name the snapshot they cite. | PASS |
| C4 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | This directory: SCOPE.md (the scope of kb is brief section 12 and charter 9.10), CHECKLIST.md, EVIDENCE.md, OPEN.md, STAGE_REPORT.md (nrpic-stage report), REVIEW.md (points to the lead reviews: wave 1 JOURNAL L0-L11, wave 2 ../REVIEW-wave2.md). | PASS |
| C5 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md: the package's numbers recomputed from the run manifests and the snapshot | No VERIFIER_REPORT.md: no verifier was assigned to kb in wave 1 or wave 2 (coord/digests/wave-1-plan.md, wave-2-plan.md). The lead's rechecks are the only second check (JOURNAL L0-L11, W1-W9; ../REVIEW-wave2.md). Request to orch: a verifier for the kb packages in wave 3. | FAIL |
| C6 | Null results and failed runs are on record (manifests and JOURNAL) | Failed runs kept with manifests: kb-20261115-154858-b0d8c8f (exit 1, IndexError), kb-20261115-164121-5aca10c (exit 1, same cause), kb-20261115-181519-d78b8d4 (output misplaced); refuted predictions recorded (embed E4, E5 v1, E3 equation truncation; claims P5, P6; lead L2, L11, W2) in tracks/kb/JOURNAL.md and the package journals. | PASS |
| C7 | STATUS.md, JOURNAL.md and HANDOFF.md are current | tracks/kb/STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (2026-11-15, kb lead wave 2). | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T18:34:40Z, clean export of `7c4bb5326ec5`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 7c4bb5326ec5 (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G0-7c4bb53-20261115T183410Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G0/SCOPE.md; REVIEW.md present |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 1 figures, each with its script |
| min-figs | PASS | 0 schematics and 1 data figures (brief 13.4 asks at least 0 and 0 at KB-G0) |
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

Record KB-G0 of kb as met in substance (tools chosen with reasons, store layout of brief 12.2 in place, read-only snapshots); the package lacks only a verifier report, because no verifier was assigned to kb. The group may accept it on the lead's rechecks or assign a verifier in wave 3.
