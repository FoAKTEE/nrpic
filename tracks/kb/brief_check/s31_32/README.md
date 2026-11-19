# Work package s31_32: check of brief lines 140-163 and items 3, 4 of lines 1747-1748

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: the ladder of methods (brief §3.1, lines 140-152) and numerical work on collisionless
matter in full GR (§3.2, lines 154-162); §15 items 3 (approximations of GRAMSES) and 4
(hyperbolicity of dGREM).

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (61): brief line, quotation, label, verdict, locator, note; plus the statements left as [JUDGEMENT] |
| `ERRATA_ROWS.md` | 14 rows for `coord/BRIEF_ERRATA.md` in its format (4 wrong or incomplete, 7 imprecise, 3 answered) |
| `JOURNAL.md` | predictions P1-P13 written before the source checks, their outcomes, the prediction of the figure run |
| `scripts/meta_dump.py` | titles, authors, abstracts from `kb-data/meta/arxiv-api/` (read-only, standard library) |
| `scripts/locate.py` | regex search of the TeX sources in `kb-data/raw/arxiv/`, printing file:line locators (read-only; nothing in the store is executed) |
| `specs/*.txt` | the searches run with `locate.py` (id, regex, maximum hits) |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md and its figure (vendored copy of `harness/style/figstyle.py`) |
| `figures/fig_verdicts.png` | the figure of the registered run (left: verdicts per brief line; right: per label) |

## Results in one paragraph

Of 59 statements of lines 144-162, 54 are confirmed at the source (9 with a precision) and 5
are corrected: 1409.5176 is not PIC (line 156); 1611.03437 is a fluid scheme, not
Einstein-Vlasov (line 149); 1901.04498 has prolate data only (line 159); gevolution also
solves a hyperbolic equation for h_ij (line 145); 2003.08014 compares codes across the ladder,
not dust-fluid codes (line 148). GRAMSES: fully constrained formulation, CMC slicing with
minimal distortion, conformal flatness with A_TT = 0 (no gravitational waves, ten elliptic
equations), N-body with half-step velocities in the sources. dGREM: hyperbolicity is shown
only for the equivalent vacuum pure-tetrad TEGR system on the constraint surface with chosen
gauges (2211.13659 v4); with matter it is open, and no dGREM evolution exists, so M3 needs a
hyperbolicity analysis with Einstein-Vlasov sources first.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s31_32/scripts/meta_dump.py 1905.08890 2111.05282   # metadata
python3 -I tracks/kb/brief_check/s31_32/scripts/locate.py tracks/kb/brief_check/s31_32/specs/sec32.txt
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s31_32 \
  --purpose "tally and figure of CHECK.md" -- python tracks/kb/brief_check/s31_32/scripts/fig_verdicts.py
```

The two sources fetched in this package (2602.01830, 2505.00286) came through
`harness/bin/nrpic-fetch-arxiv`; the INSPIRE queries are stored as served under
`kb-data/meta/inspire/query/` (ids in CHECK.md rows 21, 61).

## Runs

- `kb-20261119-143638-79805cd`: the tally and figure of CHECK.md (processors, one core, completed; output `scratch/kb/kb-20261119-143638-79805cd/`).

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s31.n`). Row s31.13 bears on M3 (brief line 512): its "[TO VERIFY]" stays, with the
  first step named.
- To kb lead: when the claims layer takes rows about cited papers, CHECK.md rows 9, 25, 30, 40,
  51 are the corrections of this package; nothing here was written to the database.
- None to core or the tracks.
