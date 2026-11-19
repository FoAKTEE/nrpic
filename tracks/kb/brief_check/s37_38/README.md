# Work package s37_38: check of brief lines 224-238 (sections 3.7 and 3.8), open question 20 and item 6 of section 15

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: section 3.7 of the brief, "Singularities, stability and mathematical results on
Einstein-Vlasov" (lines 224-230: reviews, stability theorems, kinetic phenomena, singularities,
Burnett conjecture); section 3.8, "Dark matter and strong gravity" (lines 232-237: SIDM
gravothermal collapse, dark matter around black holes, PBH dress, cosmologically coupled black
holes); open question 20 (line 583) and item 6 of section 15 (line 1750): the current status of
stability results for matter-dominated FLRW under Einstein-Vlasov.

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (60): brief line, quotation, label, verdict, locator, note; the [JUDGEMENT] of line 230 without verdict; "Answer to item 6 of section 15" (status of FLRW stability results, with locators) |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 1 wrong (s37.1), 10 imprecise or with a label to upgrade (s37.2-6, s38.1-5), 2 [TO VERIFY] answered (s38.6, s7.20) |
| `JOURNAL.md` | predictions P1-P16 written after reading the abstracts and before the source checks, their outcomes; predictions P17-P19 of the registered runs and their outcomes |
| `data/item20_landscape.tsv` | the landscape of FLRW-type stability results (matter model by expansion type), each cell with papers and locators |
| `specs/l226.txt` ... `specs/l237.txt`, `specs/q20.txt`, `specs/q20b.txt` | the searches run with `locate.py`, one file per brief line, plus those for open question 20 |
| `specs/inspire_queries.txt` | the 26 INSPIRE queries used (24 made here), with the file name of each stored result and its number of hits; the two generic web searches |
| `scripts/locate.py`, `scripts/meta_dump.py` | regex search of the TeX store with file:line output; titles and abstracts from the stored metadata (copies of the s34_36 scripts; read-only, standard library) |
| `scripts/inspire_hits.py` | prints the hits (and abstracts with `-a`) of stored INSPIRE query results |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md against its header, existence and line range of every locator (also `iq:` query files), figure (adapted copy of s34_36's script; vendored `harness/style/figstyle.py`, identical by diff) |
| `scripts/fig_item20.py` | locator check of the landscape data and its figure |
| `scripts/check_spans.py` | locator check of every backtick span in ERRATA_ROWS.md and CHECK.md |

Figures are not committed: they are `scratch/kb/<run_id>/fig_verdicts.png` and
`scratch/kb/<run_id>/fig_item20.png` of the runs below (both looked at).

## Results in one paragraph

Of 60 statements, 23 are confirmed as written, 35 confirmed with a precision and 2 corrected;
nothing was left unfound. Corrected: (1) line 230, arXiv:1706.09501 is not a proof of Burnett's
conjecture under U(1) symmetry: under polarized U(1) it constructs the reverse direction for
multiple null dusts and calls both of Burnett's questions open; the proof is 1907.10743 alone (U(1),
elliptic gauge); (2) line 235, "Full NR with a particle-dark-matter environment was not found
[TO VERIFY]": the target paper 2611.12831 itself evolves two clumps that collapse to black holes
inside a common collisionless envelope, inspiral, merge and accrete, with the strain extracted;
what remains unfound is a pre-existing binary in a particle dark-matter spike in full NR. Open
question 20: the massive Einstein-Vlasov Einstein-de Sitter case is still open beyond spatial
homogeneity (Bianchi I: future attractor, 1007.0184), but since June-July 2026 EdS is proven
nonlinearly stable for Einstein-Euler with a polytropic equation of state n > 3 (2607.09326; numerics
2606.16879), dust EdS is unstable, and instability is conjectured for 0 < n < 3; a cold kinetic gas
behaves like n = 3/2 [JUDGEMENT]. Precisions worth carrying: 1306.6223 needs Λ > 0; the two
[BACKGROUND] labels of lines 229-230 can become [VERIFIED]; the 2506.17641 numbers (0.3c,
1e-10..1e-8, ~1 Msun for a 1e9 Msun halo) are in v3 but as a conservative estimate, while the same
paper quotes 200 Msun for a 6.3e9 Msun halo from 2601.17117 (3e-8 of the halo mass); 2411.12007 and
2402.13762 are Newtonian N-body, 2505.09715 is adiabatic-order perturbation theory on Kerr; none of
the numerical singularity studies of line 229 has Vlasov matter; "a 3D full-GR kinetic SIDM
calculation does not exist yet" holds within the searches.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s37_38/scripts/meta_dump.py 1706.09501 2607.09326     # metadata
python3 -I tracks/kb/brief_check/s37_38/scripts/locate.py tracks/kb/brief_check/s37_38/specs/l230.txt
python3 -I tracks/kb/brief_check/s37_38/scripts/inspire_hits.py -a /data/haiyangw/nrpic/kb-data/meta/inspire/query/2ad127a6360ac3bf.json
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s37_38 \
  --input tracks/kb/brief_check/s37_38/CHECK.md --cores 1 \
  --purpose "tally and locator check of CHECK.md" -- python tracks/kb/brief_check/s37_38/scripts/fig_verdicts.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s37_38 \
  --input tracks/kb/brief_check/s37_38/data/item20_landscape.tsv --cores 1 \
  --purpose "landscape figure" -- python tracks/kb/brief_check/s37_38/scripts/fig_item20.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s37_38 \
  --input tracks/kb/brief_check/s37_38/ERRATA_ROWS.md --input tracks/kb/brief_check/s37_38/CHECK.md --cores 1 \
  --purpose "span check" -- python tracks/kb/brief_check/s37_38/scripts/check_spans.py \
  tracks/kb/brief_check/s37_38/ERRATA_ROWS.md tracks/kb/brief_check/s37_38/CHECK.md
```

Fetched with `harness/bin/nrpic-fetch-arxiv` (serially, sources into `kb-data/raw/arxiv/`):
2606.16879, 2607.09326, 2306.17774, 2107.00457, 2012.14241, 2604.14911, 2512.19454, 1402.7085,
1904.13290, 2402.08544, 2609.14755, 1007.0184; metadata (`--meta --service both`) for 2607.09326,
2606.16879, 1208.4231, 2306.17774. Nothing was written to the database.

## Runs

- `kb-20261119-153032-8849222`: tally and locator check of CHECK.md; completed, exit 0: 60 rows,
  23/35/2/0 equal to the header, 97 locator spans valid, corrected rows 23 and 50. Figure
  `fig_verdicts.png` (looked at).
- `kb-20261119-153036-8bc8bee`: landscape of FLRW stability results; completed, exit 0: 15 cells,
  21 locator spans valid; only the two Vlasov cells of the decelerated column are "symmetry only".
  Figure `fig_item20.png` (looked at).
- `kb-20261119-153252-225d6df`: span check of ERRATA_ROWS.md (56 spans) and CHECK.md (126 spans);
  completed, exit 0, no problem; no figure (the script had none then), superseded by:
- `kb-20261119-153316-e14e392`: the same with the figure `fig_spans.png` (looked at); completed,
  exit 0, no problem; the reference.

All runs: processors, one core, seconds each, output under `scratch/kb/<run_id>/`, manifests under
`tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s37.n`, `s38.n`, `s7.20`). Row s38.6 replaces the [TO VERIFY] sentence of line 235; row s7.20
  answers open question 20 and item 6 of section 15 (the item can be closed with that row); rows
  s37.5 and s37.6 propose the label [VERIFIED] for the two [BACKGROUND] statements of lines 229-230.
- To orch (harness): `harness/bin/nrpic-fetch-arxiv --inspire-query ... --size 60` stored only 25
  hits (the request URL carries size=25) without a note; a query with more hits needs date-split
  queries (done here for `refersto:recid:1778926`). A line in the help or a warning would help.
- To kb lead: (a) arXiv:1709.00267 has no INSPIRE record (`meta:inspire/1709.00267`, status
  not-found), consistent with brief item 12 of section 15; (b) the 12 sources fetched here are in
  the raw store but not in the database; 2607.09326, 2606.16879, 2306.17774 and 1007.0184 are the
  ones worth ingesting for open question 20; (c) for the claims layer: 2506.17641 v3 quotes both
  the range 1e-10..1e-8 and a full-GR seed ten times larger (ERRATA_ROWS s38.1).
- For information through the merge, no action asked: row s38.6 bears on Track D's novelty
  statement and on item 5 of section 15 (a full-NR black-hole binary in a collisionless
  environment exists in 2611.12831); rows s38.1 and CHECK #39 on Track C's (seed numbers; no 3D
  full-GR kinetic SIDM collapse found); row s7.20 on Tracks A and B (EdS stability background).
  None to core.

## Not done

- Bodies of the 52 cited papers were not read in full; attributions were checked at the title,
  abstract, introduction and the lines cited.
- Not on arXiv and not read: Ringström's monograph, Burnett 1989, Sachs-Wolfe 1967 (cited through
  1402.7085, 1706.09501, 2607.09326). Used through INSPIRE abstracts or citing papers only, not
  fetched: 2502.08095, 2405.03431, 2301.11191, 1309.3502. The web-search hit gr-qc/9905058 (merging
  clusters of collisionless particles in full GR, 1999) was not read.
- The landscape cells "massless Vlasov" with Λ > 0 or Milne, and polytropic Euler on Milne, were
  not searched (grey in the figure).
- The judgement of CHECK.md "Answer to item 6", point 8 (kinetic gas as an n = 3/2 polytrope) is an
  inference, not checked against a source.
