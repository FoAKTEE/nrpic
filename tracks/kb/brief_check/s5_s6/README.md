# Work package s5_s6: check of brief lines 406-444 and 493-553

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: section 5 of the brief, problems S5 (PBH formation with a free-streaming component), S6
(late-time multi-stream regions), S7 (Burnett conjecture and "graviton PIC"), S8 to S10
(exploratory), lines 406-444; section 6, the directions of method innovation M1 to M12, lines
493-553. Every statement with the label [BACKGROUND], [TO VERIFY] or [VERIFIED], and every
specific claim about a cited paper, is checked at the TeX source in the knowledge-base store.

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (69): brief line, quotation, label, verdict, locator, note; plus what is not repeated because `coord/BRIEF_ERRATA.md` has it |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 4 wrong (s5_s6.1-4), 9 imprecise or mislabelled (s5_s6.5-13), 3 [TO VERIFY] answered (s5_s6.14-16), 1 superseded (s5_s6.17), 1 defect of a source (section 5) |
| `JOURNAL.md` | predictions P1-P24 and R1-R2 written before the source checks and runs, and all outcomes (a failed sanity check of the first R1 run is kept, entries 2-3) |
| `scripts/meta_dump.py`, `scripts/locate.py` | titles and abstracts from `kb-data/meta/arxiv-api/`; regex search of the TeX sources printing file:line locators (copies of the s35 scripts; read-only, standard library; nothing in the store is executed) |
| `scripts/inspire_hits.py` | prints stored INSPIRE query results (copy of the s37_38 script) |
| `specs/l410.txt` ... `specs/l550.txt`, `specs/extra.txt` | the searches run with `locate.py`, one file per paragraph of the brief |
| `specs/inspire_queries.txt` | the twelve INSPIRE queries, their result files and what each was for |
| `scripts/check_numbers.py` | line 410: neutrino share of the radiation energy density through e+e- annihilation (Fermi-Dirac integrals, entropy conservation) and horizon mass at 1 MeV from the formula of 2002.12778 and from the Friedmann equation; line 426: c/v |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md against its header; existence and line range of every TeX locator, existence of every github file, INSPIRE query file and run manifest; figure (vendored copy of `harness/style/figstyle.py`) |

Figures are not committed: `scratch/kb/<run_id>/fig_numbers.png` ((a) neutrino share against
temperature for decoupling at 1, 2, 10 MeV; (b) horizon mass against temperature from two
sources and the Friedmann equation; (c) c/v) and `scratch/kb/<run_id>/fig_verdicts.png`
(verdicts per item of the brief and per label).

## Results in one paragraph

Of 69 statements, 32 are confirmed as written, 32 confirmed with a precision and 5 corrected;
nothing was left unfound. Corrected: (1) line 434, "all existing proofs [of Burnett's conjecture]
assume U(1) symmetry": Huneau and Luk (arXiv:2403.03470, 2024) prove it without symmetry in
generalized wave coordinates; (2) line 437, "no numerical work" on S7: 1505.02959, which the brief
itself cites, tests Isaacson's averaged radiation-fluid behaviour in full NR (no massless-Vlasov
comparison exists); (3) line 499, 2508.20606 is not a non-periodic approach (it keeps a periodic
box and embeds a curved cap); (4) line 506, Giblin et al. (1810.05203) did not deposit with a
phase-space sheet in BSSN (particles with cloud-in-cell or a tri-cubic spline); (5) line 534,
2304.13284 is spherical, not a non-spherical compaction. The [BACKGROUND] statements (neutrino
decoupling near 1 MeV, horizon mass 1.5e5 M_sun at 1 MeV, neutrino share 0.488 before and 0.405
after e+e- annihilation; charge-conserving deposition and Gauss's law) are confirmed and can
become [VERIFIED]. The [VERIFIED] statement on AthenaK's single time step is confirmed
("uniform time stepping across levels", 2409.16053). Of the [TO VERIFY] items of M3: the matter
energy-momentum equation of dGREM does have exchange sources, but the total is
source-free; hyperbolicity is shown in vacuum only, and a first vacuum numerical scheme exists
(2505.00286). Useful precisions for the tracks: the three ray tracers of M7 are post-processing
tools; CTTK/GRTresna have only scalar-field matter; 2306.14961 is not a hybrid simulation;
1904.11773 is relativistic at linear order only; the puncture-plus-particles capability is not
in the source paper but is in this repository.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s5_s6/scripts/meta_dump.py 2508.20606 1810.05203   # metadata
python3 -I tracks/kb/brief_check/s5_s6/scripts/locate.py tracks/kb/brief_check/s5_s6/specs/l500.txt
python3 -I tracks/kb/brief_check/s5_s6/scripts/inspire_hits.py \
  /data/haiyangw/nrpic/kb-data/meta/inspire/query/b82510271a2e4f4d.json
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s5_s6 \
  --cores 1 --purpose "number check" -- python tracks/kb/brief_check/s5_s6/scripts/check_numbers.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s5_s6 \
  --input tracks/kb/brief_check/s5_s6/CHECK.md --cores 1 \
  --purpose "tally and locator check of CHECK.md" -- python tracks/kb/brief_check/s5_s6/scripts/fig_verdicts.py
```

Fetched in this package (into the store, with `harness/bin/nrpic-fetch-arxiv`, sources and
arXiv metadata): arXiv:2403.03470 and arXiv:2402.17530 (row 15). Twelve INSPIRE queries
(`specs/inspire_queries.txt`). No web query. Nothing was written to the knowledge-base database.

## Runs

- `kb-20261119-154310-89ca8fb`: number check, first try; failed (exit 1) on a sanity check I had
  added without preregistering it (T_nu/T after annihilation for decoupling at 1 MeV is 0.7180,
  not 0.7138); the preregistered numbers all held. Kept on record (JOURNAL entry 2).
- `kb-20261119-154408-2b35ecd`: number check, rerun with the sanity check at 10 MeV decoupling;
  completed (0.71381 against 0.71377). Reference run for the numbers.
- `kb-20261119-154850-7d01bd3`: tally and locator check of CHECK.md; completed, 69 rows,
  32/32/5/0, 120 TeX, 3 github, 9 INSPIRE and 3 run locators, no problem.

All runs: processors, one core, seconds each, output under `scratch/kb/<run_id>/`, manifests
under `tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s5_s6.n`), after reconciling lines 406-444 with the package `novelty` (row s5_s6.16 is
  provisional and defers to it). Rows s5_s6.5 and s5_s6.10 propose the label [VERIFIED] for the
  [BACKGROUND] statements of lines 410 and 512.
- To the kb lead: (a) package s37_38 states (its note on line 230) that Burnett's conjecture is
  open without symmetry; row s5_s6.1 shows it is proven without symmetry in generalized wave
  coordinates (2403.03470), so that note and open question 19 of the brief (line 582, not read
  here) should be rechecked; (b) arXiv:2403.03470 and arXiv:2402.17530 were fetched into the
  store and need a manifest group; (c) the section-5 row (astro-ph/0608642 horizon-mass
  normalisation) is for the claims layer.
- None to core.
