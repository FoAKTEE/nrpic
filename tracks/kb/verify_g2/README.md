# verify_g2: independent verifier of KB-G2 and KB-G0 (kb, wave 3)

The verifier recomputes the numbers of the knowledge-base gates KB-G2 and KB-G0 on the frozen
snapshot `kb-data/db/kb-20261119-a782f1e.sqlite`, with its own code and a blind held-out
question set, and writes the verdicts into `tracks/kb/stage/KB-G2/VERIFIER.md` and
`tracks/kb/stage/KB-G0/VERIFIER.md`. Nothing is written to kb-data.

## Contents

| Path | What |
|---|---|
| `heldout.yaml` | blind held-out set: 24 questions in the verifier's words, expected paper and answer locator (file:lines of the source); committed 8fb37106 before any search. Nobody tunes retrieval on it |
| `JOURNAL.md` | predictions and outcomes, entries 0-14 |
| `scripts/vg2common.py`, `locmap.py` | read-only snapshot access; own map from source lines to flat.tex characters |
| `scripts/draw_heldout.py` | seeded stratified draw of the held-out papers |
| `scripts/run_search.py`, `score_search.py` | `kb search` in three modes; own scorer (paper rank, location rank strict and with 200-char slack) |
| `scripts/parse_scan.py`, `draw_parsecheck.py`, `lenient_check.py`, `tally.py` | own parse scan of 710 papers, the 15-paper source-check draw, the leniency check, the final C3 tally |
| `scripts/checks_c1_c5_c6.py` | C1 counts, read-only default (static and in a fake data root), snapshot sha and modes, locators, directories, failed runs |
| `scripts/compare.py` | counts for the comparison with the package (after the verdicts) |
| `scripts/make_figures.py`, `figstyle.py` | figures (figstyle copied unchanged from harness/style) |
| `figures/fig_ranks.png` | rank of the right paper and of the answer location per question, 3 modes, held-out and golden |
| `figures/fig_parse.png` | parse components by recorded status; own counts of equations and bibliography entries against the database |

## Results (runs registered under tracks/kb/runs/, outputs in scratch/kb/<run_id>/)

| Item | Result | Run |
|---|---|---|
| C1 papers, repositories | 710/710 ids, 64/64 repositories with commit and files | kb-20261121-080038-306bcdd |
| C3 parse success | status ok 684/710 = 96.3 %; own definition 679/710 = 95.6 % (strict abstract test 658/710 = 92.7 %) | kb-20261120-223309-14e4cb6, kb-20261121-080834-6c50215, kb-20261121-080843-98907be |
| C4 golden retrieval | paper in top 10: text 84.4 %, hybrid 87.5 %, rerank 87.5 % (32 questions) | kb-20261121-074940-08426cc, kb-20261121-080557-06d44ba |
| held-out retrieval | text 87.5 %, hybrid 91.7 %, rerank 87.5 % (24 questions) | kb-20261120-222546-ea894c8, kb-20261121-075156-b84a189 |
| C5, C6, KB-G0 | snapshots 0444 with matching sha; default db/current, read-only; locators carry the id only in the answer footer | kb-20261121-080038-306bcdd |
| figures | fig_ranks, fig_parse | kb-20261121-080624-467030c |

Verdicts: KB-G2 C1, C2, C3, C4, C5, C6a, C9 CONFIRMED; C6b WRONG (partly met); package documents
NOT CHECKED. KB-G0 C1a, C1c, C2, C3, C6 CONFIRMED; C1b (reasons) NOT CHECKED. Details and defects
in the two VERIFIER.md files.

## Failed predictions

- R1 (held-out retrieval): within its refutation bars, but the point estimates were too low
  (text-only 87.5 % against 55-85 % expected).
- R2 (golden vs held-out): "held-out 5-15 points below golden" refuted; held-out equals or
  exceeds golden.
- P1 (parse scan): "bibliography the weakest component" refuted; the abstract chunk is.
- P2 (15-paper source check): refuted on component verdicts (my S and B too lenient for two
  plain-TeX papers); confirmed that every failure verdict is a real gap.
- T1 (tally): refuted in substance; my leniency check had examined only strict successes and
  missed five review papers (fixed, T2 confirmed).

## How to rerun

From /data/haiyangw/nrpic/wt/kb, each through `harness/bin/nrpic-run submit --kind scouting
--gate G2 --package tracks/kb/verify_g2 --cores N --allow-no-venv --purpose '...' -- bash -c
'kb/.venv/bin/python -I tracks/kb/verify_g2/scripts/<script> ... > "$NRPIC_RUN_DIR/out.txt"'`
(the exact commands are in the manifests):
1. `draw_heldout.py --seed 20261120`; 2. `run_search.py --set heldout --questions
tracks/kb/verify_g2/heldout.yaml --threads 4` and `--set golden --questions
kb/golden/questions.yaml`; 3. `score_search.py --set <set> --questions <file> --raw
<run dir>/raw/<set>`; 4. `parse_scan.py`; `draw_parsecheck.py --seed 20261121 --scan <scan.json>`;
`lenient_check.py --scan <scan.json>`; `tally.py --scan ... --lenient ... --gaps ... --letters
...` (lists in the manifest of kb-20261121-080843-98907be); 5. `checks_c1_c5_c6.py`;
6. `make_figures.py --heldout ... --golden ... --scan ... --out "$NRPIC_RUN_DIR"`, then copy the
PNGs into figures/. A search costs about 1 s (text), 7 s (hybrid), 22 s (rerank) per question.

## Open

- Done after the verdicts (commit ef9d2d34): the C9 journal part and the comparison with the
  package, appended to both VERIFIER.md files (run kb-20261121-081226-a4025cf; no verdict
  changed). The package's counts agree with mine (C1, C3 status and bibliography counts, C4);
  they differ in the parse definition, the held-out check, C6b and the status words of two
  failed wave-1 runs.
- Not checked (see the VERIFIER.md files): fidelity of the manifest to brief section 17 beyond
  ids, bibliography resolution and the citation graph, equation content, code-index content,
  the working database, the 26 raw directories outside the snapshot.

## Requests

To the kb lead (details in tracks/kb/stage/KB-G2/VERIFIER.md, Requests):
1. Count "bibliography missing or under half of the source" and "citation rows without
   entries" as parse failures, and parse the four bibliography forms found here.
2. Recognise old-style headings and numbered reference lists without `\cite`.
3. Print the snapshot id in `kb show`, `kb cites` and in every JSON hit.
4. State the parse rate and its definition against the 95 % bar in the QA report.
5. Name the reasons for the K0 tool choices in kb/README.md; say what replaced
   `curated/seed_claims.jsonl`.
