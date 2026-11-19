# Work package s33: check of brief lines 164-185 (section 3.3, late universe)

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: section 3.3 of the brief, "Late universe: structure formation, backreaction,
light-cone observables": what full-NR fluid simulations found (line 166), from fluid to
particles (168), light-cone observables (170-176), the weak-field route (178), the
theoretical dispute (180), timescape and DESI (182), local voids and anomalies (184).

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (53): brief line, quotation, label, verdict, locator, note; plus the one [JUDGEMENT] statement (line 178), listed without verdict |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 2 wrong or incomplete (s33.1-2), 11 imprecise (s33.3-13), 2 answered (s33.14-15), 1 defect of a cited source (section 5) |
| `JOURNAL.md` | predictions P1-P18 written before the source checks and their outcomes; predictions and outcomes of the four tally runs (one failed, kept on record) |
| `scripts/meta_dump.py` | titles, authors, abstracts from `kb-data/meta/arxiv-api/` (read-only, standard library; copy of the s31_32 script) |
| `scripts/locate.py` | regex search of the TeX sources in `kb-data/raw/arxiv/`, printing file:line locators (read-only; nothing in the store is executed); accepts "|" inside the regex |
| `specs/l166.txt` ... `specs/l184.txt` | the searches run with `locate.py`, one file per paragraph of the brief |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md against its header, existence and line range of every locator, figure (vendored copy of `harness/style/figstyle.py`) |

Figures are not committed: the figure of the last run is
`scratch/kb/<run_id>/fig_verdicts.png` (left: verdicts per brief line; right: per label).

## Results in one paragraph

Of 53 statements of lines 164-185, 38 are confirmed as written, 13 confirmed with a precision
and 2 corrected; nothing was left unfound, and all 53 cited papers were already in the
knowledge base. Corrected: arXiv:1611.03437 is a perfect-fluid scheme, not a particle
implementation (line 168; the same finding as s31.2 for line 149); arXiv:2606.02712 finds the
redshift offset of local-void models compatible with zero and with the void value 0.84 per
cent, and concludes that the void "cannot be ruled out" (line 184). Precisions worth carrying:
the "10⁻⁸" backreaction of arXiv:1807.01711 is the abstract's, the body has 10⁻⁹ (10⁻⁸ is the
curvature), a defect of the source; the three "2016" papers are two back-to-back PRLs and a
third group's follow-up of 2017; the Pantheon+ numbers ln B > 5 and > 1 are from 2412.15143
only; the one DESI-like observer of 2606.05479 agrees with DESI within 1 sigma while most
observers infer the opposite quadrant; the Green-Wald tracelessness is a theorem under the weak
energy condition, so its [BACKGROUND] label can become [VERIFIED].

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s33/scripts/meta_dump.py 1807.01711 2408.03049      # metadata
python3 -I tracks/kb/brief_check/s33/scripts/locate.py tracks/kb/brief_check/s33/specs/l166.txt
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s33 \
  --input tracks/kb/brief_check/s33/CHECK.md --cores 1 \
  --purpose "tally and locator check of CHECK.md" -- python tracks/kb/brief_check/s33/scripts/fig_verdicts.py
```

No source was fetched in this package and no INSPIRE or web query was made: every paper and
every INSPIRE record used (`kb-data/meta/inspire/`) was already in the store.

## Runs

- `kb-20261119-144642-5ac03b1`: tally and locator check; FAILED (exit 1) on the short locator
  form of CHECK.md row 3 (`:524, :644`), tally right; kept on record (JOURNAL entry 4).
- `kb-20261119-144701-10f10d6`: rerun after writing row 3 in full; completed, no problem
  (71 locator spans); legend of the figure covered two bars.
- `kb-20261119-144723-15a7b14`: legend moved; completed, same numbers; legend still touched a bar.
- `kb-20261119-145757-12b6579` and `kb-20261119-145803-b30688a`: legend above the panels;
  completed, same numbers, identical `verdicts.json`. Two runs because two retry loops (waiting
  for a free core of the kb allotment) were running at once; the second is the reference.
  Figure: `scratch/kb/kb-20261119-145803-b30688a/fig_verdicts.png` (looked at).

All runs: processors, one core, a few seconds each, output under `scratch/kb/<run_id>/`,
manifests under `tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s33.n`); s33.1 and s33.6 repeat for line 168 the findings s31.2 and s31.8 of package s31_32
  (line 149) and can be merged with them. Row s33.14 proposes the label [VERIFIED] for the
  Green-Wald statement of line 180.
- To kb lead: the section-5 row (1807.01711, abstract 10⁻⁸ against body 10⁻⁹) is for the claims
  layer when it takes rows about cited papers; nothing here was written to the database.
- None to core or the tracks.
