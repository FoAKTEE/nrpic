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

## Entry 2 (22:24 UTC): held-out questions written (step 1)

For each drawn paper I read the stored source (raw/arxiv/<id_>/<v>/src, read-only, with
Read/grep only) and wrote one question in my own words whose answer is a specific
passage away from the abstract (a number, a definition, a method statement or the
provenance of a result). Locators are file:line ranges of the source file. File:
`heldout.yaml` (24 questions; kinds: 9 number, 11 method, 2 definition, 1 provenance,
plus 1 number/method mix). Overlap with the golden set unknown (golden file still
unopened). Validated: YAML loads, 24 distinct papers, every locator file exists and the
line ranges lie inside it. Commit of heldout.yaml: see entry 3 (made before any search).

## Entry 3 (22:25 UTC; times of entries 2 and 3 corrected from `date -u`): commit of the held-out set; predictions for retrieval (step 2)

- heldout.yaml committed as **8fb37106** (pushed to origin/kb/main) before any `kb search`
  was run by me and before kb/golden/questions.yaml was opened. Correction of entry 2:
  the kinds are 10 number, 11 method, 2 definition, 1 provenance (24).
- Scoring definitions (fixed now, before the runs): paper hit = expected paper_id among the
  10 hits. Location: my own map from source lines to flat.tex characters (each expected
  line, comment-stripped, located verbatim in flat.tex; ambiguous matches resolved by
  nearness to the unique ones); the expected range is [first anchor, last anchor + line
  length). Location hit (strict) = a hit of the right paper whose [char_start, char_end)
  overlaps the expected range; location hit (slack) = overlap with the range widened by
  200 characters on each side (about two to three source lines). Rank = first rank that
  hits.

Prediction (R1, held-out set, 24 questions; my own words, not tuned):
| mode | paper hit in top 10 | location hit (slack) |
|---|---|---|
| text-only (BM25) | 70 % (17/24), range 55-85 % | 35 %, range 20-55 % |
| hybrid | 80 % (19/24), range 65-92 % | 40 %, range 25-60 % |
| rerank | 83 % (20/24), range 70-95 % | 55 %, range 35-75 % |
Reasoning [JUDGEMENT]: most questions carry a few domain terms (oscillon, Hernquist,
Gauss-Bonnet, tetrahedra, lapse) that BM25 can use; vectors help the paraphrased ones;
the answer passages sit in the body, so the location rate is well below the paper rate.
Refuted if: hybrid paper hit < 60 % or > 96 %; rerank location hit < 30 %; or rerank worse
than hybrid on paper hits by more than 2 questions.

Prediction (R2, golden set, read after the held-out runs): the golden set was written by
the package (decision 0016 asks >= 80 %); I expect hybrid paper hit >= 85 % on it and the
held-out rate 5 to 15 points below the golden rate (a sign of tuning on the golden set if
the gap exceeds 20 points). Refuted if golden hybrid paper hit < 80 % (then C4 fails as
stated) or if the held-out rate is above the golden rate by more than 10 points.

Prediction (R3, side effects): `kb search --db <snapshot>` opens the snapshot read-only
and writes nothing into kb-data (mtimes of db/ and logs/ unchanged by my runs). Refuted by
any new or changed file there attributable to my runs.
