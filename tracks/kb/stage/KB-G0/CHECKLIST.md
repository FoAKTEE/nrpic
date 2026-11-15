# Checklist: kb KB-G0

Collected by `harness/bin/nrpic-stage collect kb KB-G0` on 2026-11-15T18:29:11Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G0 (brief 12.10; charter 9.10)

- [x] **C1** Tools chosen, directories in place
  - status: PASS
  - evidence: Tool choices with reasons: kb/JOURNAL.md (K0 tool choice, K2-K3 tool choices, tool choice for the code index) and kb/EMBEDDING.md (K4 model); environments frozen in kb/requirements-k0.lock, -k4.lock, -k6.lock (kb/.venv, uv). Layout of brief 12.2 in place (kb init, wave 1): kb-data/{raw,meta,build/{tex,code},db,manifests,logs}, checked 2026-11-15T18:30Z.

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [x] **C2** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: PASS
  - evidence: kb opens kb-data/db/current by default (kb/kbtool/cli.py and papers_cli.py: '--db default db/current'); snapshots are written mode 0444 (kb/kbtool/db.py snapshot), db/current -> kb-20261115-3826a68.sqlite is -r--r--r--; harness doctor row kb PASS in wt/kb (coord/digests/harness-wave-2.md: checks that db/current refuses a write).
- [x] **C3** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: PASS
  - evidence: Snapshots at the end of each stage: kb-20261115-f2fcda5 (KB-G1, wave 1, run kb-20261115-141500-b2e57be), kb-20261115-621430e (K4-K5, run kb-20261115-164041-5aca10c), kb-20261115-3826a68 (K8 load, run kb-20261115-182741-7dafdf9) and kb-20261115-44b7406 (runs kb-20261115-182907-3f69615 and kb-20261115-183052-0f8245e) and kb-20261115-a848a06 (run kb-20261115-183921-31d5b77, db/current at the end of the session); the answers posted to the tracks name the snapshot they cite.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C4** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: This directory: SCOPE.md (the scope of kb is brief section 12 and charter 9.10), CHECKLIST.md, EVIDENCE.md, OPEN.md, STAGE_REPORT.md (nrpic-stage report), REVIEW.md (points to the lead reviews: wave 1 JOURNAL L0-L11, wave 2 ../REVIEW-wave2.md).
- [ ] **C5** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md: the package's numbers recomputed from the run manifests and the snapshot
  - status: FAIL
  - evidence: No VERIFIER_REPORT.md: no verifier was assigned to kb in wave 1 or wave 2 (coord/digests/wave-1-plan.md, wave-2-plan.md). The lead's rechecks are the only second check (JOURNAL L0-L11, W1-W9; ../REVIEW-wave2.md). Request to orch: a verifier for the kb packages in wave 3.
- [x] **C6** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed runs kept with manifests: kb-20261115-154858-b0d8c8f (exit 1, IndexError), kb-20261115-164121-5aca10c (exit 1, same cause), kb-20261115-181519-d78b8d4 (output misplaced); refuted predictions recorded (embed E4, E5 v1, E3 equation truncation; claims P5, P6; lead L2, L11, W2) in tracks/kb/JOURNAL.md and the package journals.
- [x] **C7** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: tracks/kb/STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (2026-11-15, kb lead wave 2).
