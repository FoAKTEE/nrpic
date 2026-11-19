# Work package s35: check of brief lines 196-216 (section 3.5, primordial-black-hole formation)

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: section 3.5 of the brief: the radiation era in spherical symmetry (line 198) and its
recent 3+1 progress (non-spherical collapse, long evolutions, multiple peaks, initial data;
lines 200-203), the analytic picture of the matter-dominated era (lines 205-209), and full
numerical relativity in the matter-dominated era (scalar field, particles against dust, gauge;
lines 213-215).

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (52): brief line, quotation, label, verdict, locator, note |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 1 wrong (s35.1), 10 imprecise (s35.2-11), 2 answered (s35.12-13), 1 defect of a cited source (section 5) |
| `JOURNAL.md` | predictions P1-P15 written before the source checks, the predictions of the four runs, and all outcomes (one failed sub-prediction kept, entry 5) |
| `scripts/meta_dump.py` | titles, authors, abstracts from `kb-data/meta/arxiv-api/` (read-only, standard library; copy of the s33 script) |
| `scripts/locate.py` | regex search of the TeX sources in `kb-data/raw/arxiv/`, printing file:line locators (read-only; nothing in the store is executed; copy of the s33 script) |
| `specs/l198.txt` ... `specs/l215.txt`, `specs/l209_extra.txt` | the searches run with `locate.py`, one file per paragraph of the brief |
| `scripts/check_numbers.py` | recomputes the ratios of lines 201, 208, 214 (94, 19, 2, 10) from numbers printed in the paper bodies, with the analytic criterion of arXiv:2609.14218; bands preregistered in JOURNAL entry 2 |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md against its header, existence and line range of every TeX locator, existence of every metadata file and run manifest named as locator; figure (vendored copy of `harness/style/figstyle.py`) |

Figures are not committed: `scratch/kb/<run_id>/fig_numbers.png` (left: the analytic criterion of
2609.14218 against its dust bound and particle bracket at e = 0.2; right: stated against
recomputed ratios) and `scratch/kb/<run_id>/fig_verdicts.png` (verdicts per brief line and per
label).

## Results in one paragraph

Of 52 statements of lines 196-216, 33 are confirmed as written, 18 confirmed with a precision and
1 corrected; nothing was left unfound, and all 26 cited papers were already in the knowledge base.
Corrected: arXiv:2508.10070 gives a PBH abundance proportional to the fifth power of the r.m.s.
density contrast at horizon entry (sigma, whose square is the variance), not of the variance; the
paper's own loose wording ("the variance") is the source of the error. The numbers of the brief
are right where it quotes them: 94 fewer coarse steps (2608.13206; recomputed 93.8), 19 times the
abundance of Harada et al. 2016 (19.4), and for 2609.14218 at the one ellipticity the body
reports (e = 0.2) a dust factor of at least 2.1 and a particle factor of 9 to 10 against the
Zel'dovich-plus-hoop criterion. Precisions worth carrying: the particle threshold of 2609.14218
comes with "a big caveat" (constraints significantly violated after particles cross) and is
stated conditionally, which matters for Track A's comparison; the 3+1 runs of 2608.13206 are of a
spherical profile only and its Zel'dovich-Novikov "law" is a two-parameter fit; the spin
"disagreement" of line 209 is a sequence of revisions (near-extremal 2017, substantial 2024, very
small 2025) plus one independent small-spin result; the [BACKGROUND] statements of lines 205 and
207 are confirmed at the sources and can become [VERIFIED].

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s35/scripts/meta_dump.py 2508.10070 2609.14218   # metadata
python3 -I tracks/kb/brief_check/s35/scripts/locate.py tracks/kb/brief_check/s35/specs/l208.txt
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s35 \
  --cores 1 --purpose "number check" -- python tracks/kb/brief_check/s35/scripts/check_numbers.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s35 \
  --input tracks/kb/brief_check/s35/CHECK.md --cores 1 \
  --purpose "tally and locator check of CHECK.md" -- python tracks/kb/brief_check/s35/scripts/fig_verdicts.py
```

No source was fetched in this package and no INSPIRE or web query was made: every paper used
(the 26 cited ones and arXiv:2409.00435) was already in the store. Nothing was written to the
knowledge-base database.

## Runs

- `kb-20261119-151804-271859c`: number check; completed, all ratios inside the preregistered
  bands (93.8, 200, 19.4, hhat(0.2,0) = 0.452, dust at least 2.10, particles 9.0 to 10.0).
- `kb-20261119-152248-b27df46`: tally and locator check; completed, 52 rows, 33 / 18 / 1 / 0,
  68 locator spans, no problem (a sub-prediction about label counts failed, my miscount).
- `kb-20261119-152254-b4836fb`: number check after a legend fix; numbers identical to the first.
- `kb-20261119-152449-e225d94`: tally after adding 2409.00435 to row 35; completed, same tally,
  69 locator spans, no problem. Reference run for the tally.

All runs: processors, one core, a few seconds each, output under `scratch/kb/<run_id>/`,
manifests under `tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s35.n`). Rows s35.12 and s35.6 propose the label [VERIFIED] for the [BACKGROUND] statements of
  lines 205 and 207.
- To orch, for Track A (A-emd-pbh): row s35.10. The particle threshold of arXiv:2609.14218
  (mu ≈ 0.045-0.05 at e = 0.2) is stated conditionally by its authors and comes with
  significantly violated constraints after particle crossing (`MDPBH.tex:1145-1149, 1204-1209`);
  a comparison of the threshold line with these data (decision 0016 item 5) should carry that
  caveat, and the dust bound is one number in the body (mu ≤ 0.95 crashes without a horizon).
- To kb lead: the section-5 row (2508.10070 calls a standard deviation "the variance") is for the
  claims layer when it takes rows about cited papers; nothing here was written to the database.
- None to core.
