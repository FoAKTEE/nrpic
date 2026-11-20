# Journal of the KB-G2 / KB-G0 verifier (wave 3, round 1, package verify_g2)

Independent verifier: given artefacts and criteria, not conclusions. Until the verdicts
are committed I do not open tracks/kb/stage/**, the lead's STATUS/HANDOFF/JOURNAL/RISKS/
PLAN-wave3, kb/QA_REPORT.md, kb/STATE.json, tracks/kb/{retrieval,pdf_meta,claims}/**, the
outbox of kb or scratch/orch. Database: only the frozen snapshot
`kb-data/db/kb-20261119-a782f1e.sqlite`, opened with `mode=ro&immutable=1`.

## Entry 0 (2026-11-20 22:17 UTC): start

- Worktree clean, branch kb/main at 8b24b590 (main already merged by another helper);
  no earlier state of this package (`git log -- tracks/kb/verify_g2` empty).
- Read: CLAUDE.md, CHARTER to "Gates of the knowledge base", RULES nrpic-run section,
  brief 1218-1461, decisions 0015, 0016, 0019, kb/README.md (commands).
- Snapshot first look (python sqlite, read-only): 710 papers; parse_status ok 684, review 23,
  pdf 3; priority 1/2/3 = 478/185/47; 21 groups G01-G21. [VERIFIED, query in entry 1 run]

## Entry 1: draw of the held-out set (step 1)

Plan: `scripts/draw_heldout.py --seed 20261120`, 24 papers; one slot per group (21) plus 3
slots to groups drawn proportional to size; priority quotas 4 x p3, 7 x p2, 13 x p1. I have
not opened kb/golden/questions.yaml, so the held-out papers may overlap with golden papers;
that is recorded, not avoided.

Prediction (D1): the draw is feasible within a few hundred shuffles and gives 24 distinct
papers covering all 21 groups; one or two of them have parse_status review or pdf (expected
24 x 26/710 = 0.9). Refuted if a group is missing or the assignment is infeasible.

Outcome (D1, run kb-20261120-222100-50182fe, 22:21 UTC): confirmed. 21 assignment
attempts; 24 distinct papers, all 21 groups (G07, G09, G13 twice); priorities 4/7/13;
parse_status ok 23, review 1 (2009.08715), no pdf paper. The ad-hoc preview before the
registered run gave the identical draw (diff of draw.json picks empty). [VERIFIED]

## Entry 2 (22:40 UTC): held-out questions written (step 1)

For each drawn paper I read the stored source (raw/arxiv/<id_>/<v>/src, read-only, with
Read/grep only) and wrote one question in my own words whose answer is a specific
passage away from the abstract (a number, a definition, a method statement or the
provenance of a result). Locators are file:line ranges of the source file. File:
`heldout.yaml` (24 questions; kinds: 9 number, 11 method, 2 definition, 1 provenance,
plus 1 number/method mix). Overlap with the golden set unknown (golden file still
unopened). Validated: YAML loads, 24 distinct papers, every locator file exists and the
line ranges lie inside it. Commit of heldout.yaml: see entry 3 (made before any search).
