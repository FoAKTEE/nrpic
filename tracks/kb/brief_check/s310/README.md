# Work package s310: check of brief lines 257-266 (section 3.10, stochastic and lattice inflation)

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: section 3.10 of the brief, the background of Track E: what stochastic inflation is,
reviews, delta N and separate universes, early comparisons (line 259); non-Gaussian tails and
primordial black holes (line 260); numerical implementations outside numerical relativity (line
261); the numerical-relativity implementation of Launay, Rigopoulos and Shellard (line 262); the
three warnings (line 263); foundational questions (line 264); and two factual sub-claims of the
[JUDGEMENT] bullet of line 265.

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (74): brief line, quotation, label, verdict, locator, note |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 13 imprecise or relabelled (s310.1-13), 1 superseded (s310.14), 1 defect of a source record (section 5); none wrong |
| `JOURNAL.md` | predictions P1-P12 written after the metadata pass and before the source checks, their outcomes (several sub-predictions failed, kept), the prediction and outcome of the run |
| `scripts/meta_dump.py` | titles, authors, abstracts from `kb-data/meta/arxiv-api/` (read-only, standard library; copy of the s35 script) |
| `scripts/locate.py` | regex search of the TeX sources in `kb-data/raw/arxiv/`, printing file:line locators (read-only; nothing in the store is executed; copy of the s35 script) |
| `specs/l259.txt` ... `specs/l264.txt`, `specs/extra.txt` | the searches run with `locate.py`, one file per paragraph of the brief, plus absence checks and abstract lines |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md against its header; every locator span (TeX file and line, PDF page, metadata file, repository-clone path, file of this repository); coverage of all arXiv identifiers of brief lines 257-266; figure (vendored copy of `harness/style/figstyle.py`) |

Figures are not committed: `scratch/kb/<run_id>/fig_verdicts.png` (verdicts per brief line and
per evidence label).

## Results in one paragraph

All 74 papers cited in lines 257-266 are in the store and were read at their sources; of 74
statements, 49 are confirmed as written and 25 confirmed with a precision; nothing is wrong and
nothing was left unfound. The two [BACKGROUND] statements of substance (line 259: Langevin
equation with kicks from short modes, astro-ph/9407016; line 260: the non-Gaussian tail and the
sensitivity of the PBH abundance to it) are confirmed and can carry [VERIFIED] with the
locators given. Precisions that matter for Track E: the kicks enter at the coarse-graining
scale k = epsilon a H with epsilon much less than 1, not at horizon crossing (9407016 Eqs. 6,
9-11); the Langevin sources of 2401.08530 depend on the first two time derivatives of the window
and on the slow-roll parameters; Launay's "analytic solutions of the constraints" are
perturbative, leading-order solutions (2610.32592, as 2502.06783), so a nonlinear initial slice
still needs a solve or a measured residual; warning (i) concerns codes with a rigid FLRW
background and no metric perturbations (not numerical relativity), (ii) is a transient O(0.5)
rise of a normalised residual during USR, and (iii) is a bias toward inflation for a periodic
length close to the inflationary scale 1/sqrt(G rho_infl), about whether inflation starts at all.
Attributions to sharpen: 2009.08715 is a habilitation thesis; astro-ph/0504508 is not a delta N
paper; three of the "early comparisons" are not comparisons; astro-ph/0101406 and 1911.00057 do
not speak of USR; 2412.19731 is by Florio and Shellard; 2302.00655 is a method Letter, not the
code paper. Line 265's "public AthenaK has no scalar field" holds for upstream c5a0d7f9155a;
its GRChombo/GRTeclyn alternative is settled by decisions 0004 and 0010. One metadata defect:
the arXiv journal reference of 2604.03628 belongs to 2410.23942.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s310/scripts/meta_dump.py 2401.08530 2606.14853   # metadata
python3 -I tracks/kb/brief_check/s310/scripts/locate.py tracks/kb/brief_check/s310/specs/l263.txt
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s310 \
  --input tracks/kb/brief_check/s310/CHECK.md --cores 1 \
  --purpose "tally, locator and coverage check of CHECK.md" \
  -- python tracks/kb/brief_check/s310/scripts/fig_verdicts.py
```

astro-ph/9407016 has only a PostScript source in the store; its pages were read from
`kb-data/raw/arxiv/astro-ph_9407016/v1/source.pdf` (Read tool, and `pdftotext` once into
`scratch/kb/tmp/s310/pdf/` for the reference list). No source was fetched, and no INSPIRE or
web query was made: every paper used (the 74 cited ones and, for line 265, 1909.11678,
1911.01661, 2212.00425, found with one `kb search --text-only` on the snapshot `current`) was
already in the store. Nothing was written to the knowledge-base database.

## Runs

- `kb-20261119-153817-085d90b`: tally, locator and coverage check; completed, 74 rows,
  49 / 25 / 0 / 0 equal to the header, 96 locator spans valid, 74 of 74 brief identifiers
  covered. The figure's x-axis ended at the longest bar.
- `kb-20261119-153831-19034bc`: the same after a margin fix of the figure; identical numbers.
  Reference run.

Both: processors, one core, a few seconds each, output under `scratch/kb/<run_id>/`, manifests
under `tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s310.n`). Rows s310.1 and s310.3 propose the label [VERIFIED] for the two [BACKGROUND]
  statements of lines 259 and 260; s310.14 extends the supersession of row 4.2 to line 265.
- To orch, for Track E (E-stoch-inf): rows s310.1 (noise enters at k = epsilon a H, the choice
  of epsilon or sigma is a parameter of the noise), s310.7 (the published initial data satisfy
  the constraints to leading order only) and s310.9-11 (scope of the three warnings) bear on
  E's specification; nothing here changes a number E uses.
- To kb lead: the section-5 row (arXiv journal reference of 2604.03628) is for the metadata or
  claims layer; nothing here was written to the database.
- None to core.
