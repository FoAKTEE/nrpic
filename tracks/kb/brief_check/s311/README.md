# Work package s311: check of brief lines 267-278 (section 3.11, Hills mechanism, tidal separation, strong-field three-body dynamics)

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: section 3.11 of the brief, the background of Track F: the classic Hills picture (line
269), restricted and full three-body work (270), gravitational-wave channels (271), the
relativistic treatments (272), related full numerical relativity and the novelty statement
[TO VERIFY] (273), the cosmological connection (274) and the scale estimate (275; re-derived by
Track F, already row 1.5 of `coord/BRIEF_ERRATA.md`, cited here, not redone).

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (66): brief line, quotation, label, verdict, locator, note |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 2 wrong (s311.1-2), 6 imprecise (s311.3-8), 1 answered [TO VERIFY] (s311.9), 1 metadata divergence of a cited source (section 5) |
| `JOURNAL.md` | predictions P1-P11 written before the source checks, the predictions of the three runs, and all outcomes (one failed sub-prediction, P8, kept) |
| `scripts/meta_dump.py` | titles, authors, abstracts from `kb-data/meta/arxiv-api/` (read-only, standard library; copy of the s35 script) |
| `scripts/locate.py` | regex search of the TeX sources in `kb-data/raw/arxiv/`, printing file:line locators (read-only; nothing in the store is executed; copy of the s35 script) |
| `specs/l269.txt` ... `specs/l274.txt` | the searches run with `locate.py`, one file per brief line |
| `scripts/novelty_update.py` | compares the INSPIRE answers of 2026-11-19 with Track F's raw answers of 2026-11-15, record by record (JSON parsed as data, run with `python3 -I`) |
| `scripts/check_numbers.py` | recomputes, from numbers printed in the sources, Hills' ejection prefactor k (Yu and Tremaine), 2404.16270's r_t = 101.3 r_g and beta_max = 25.3, and the Peters coefficient and 6.0e3 Gyr of 1805.09593; bands preregistered in JOURNAL entry 3 |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md against its header and check of every locator (TeX lines, metadata and query files, kb and F-hills run manifests, files on `main` and `track/F-hills`); figure (vendored copy of `harness/style/figstyle.py`) |

Figures are not committed: `scratch/kb/kb-20261119-153659-4688c5b/fig_numbers.png` (left:
recomputed against stated numbers; right: v_ej / v_b against q, the k = 1 line of 0911.1136 and
Hills' band k = 1.10-1.35) and `scratch/kb/kb-20261119-154140-0c9116d/fig_verdicts.png`
(verdicts per brief line and per label). Both were read before the results were written down.

## Results in one paragraph

Of 66 statements of lines 269-275, 45 are confirmed as written, 18 confirmed with a precision and
3 corrected (one of them line 275's parameter box, already row 1.5 of the errata); nothing was
left unfound, and all 52 cited papers were already in the knowledge base. Corrected: arXiv:0704.2612
(listed under waveform effects for binaries near a massive black hole) has no binary, it treats
bursts of a single compact object; arXiv:1411.5022 (listed under single-star tidal disruptions)
is about stars ejected by massive-black-hole binaries. The [BACKGROUND] Hills picture of line 269
is confirmed at 0911.1136 and astro-ph/0309084 and can become [VERIFIED], with three precisions
that matter for Track F: separation inside r_t is probable, not certain (exchange in about 80 and
50 per cent of Hills' encounters at 0.38 and 1.26 r_t; about 20 per cent of deep planar
penetrators survive); v_ej = k v_b q^(1/6) with k = 1.10-1.35 from Hills' own numbers; each
member is ejected with probability one half. The "about 100 r_g" of 2404.16270 is a rule of thumb
it quotes from Tejeda et al. 2017 (order 1 per cent), not its own estimate; "including spin"
applies to 2601.04870 only. The [TO VERIFY] novelty statement of line 273 holds as of
2026-11-19 (Track F's search; its four key INSPIRE queries repeated, same records), stated
narrowly: full-NR binaries with a heavier third hole exist (2406.11985, q = 4 and 9, bound, not
separated), and a binary is broken up in full NR by equal or lighter holes (0711.1165,
2505.03934). Line 275's algebra is confirmed again at the sources (Peters 5/64 from the formula
quoted in 1805.09593; 2404.16270's own r_t and beta_max from the brief's formula).

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s311/scripts/meta_dump.py 0911.1136 2404.16270      # metadata
python3 -I tracks/kb/brief_check/s311/scripts/locate.py tracks/kb/brief_check/s311/specs/l272.txt
# novelty queries (one at a time; the fetch command holds the machine-wide lock):
python3 -I harness/bin/nrpic-fetch-arxiv --inspire-query 'refersto:recid:2799952' --size 50
python3 -I harness/bin/nrpic-fetch-arxiv --inspire-query 'refersto:recid:2919080' --size 50
# then the comparison, numbers and tally (registered):
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s311 --cores 1 \
  --purpose "..." -- python3 -I tracks/kb/brief_check/s311/scripts/novelty_update.py '$NRPIC_RUN_DIR' \
  <label>=<new query json>:<Track F response.json> ...      # exact arguments in the manifest of kb-20261119-153345-ed7ee04
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s311 --cores 1 \
  --purpose "number check" -- python tracks/kb/brief_check/s311/scripts/check_numbers.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s311 \
  --input tracks/kb/brief_check/s311/CHECK.md --cores 1 \
  --purpose "tally and locator check of CHECK.md" -- python tracks/kb/brief_check/s311/scripts/fig_verdicts.py
```

No source was fetched. Four INSPIRE queries were made (generic physics queries, nothing about the
project or the user), stored by the fetch command under `kb-data/meta/inspire/query/`
(`9016c78742b1a3b7`, `152b0ae13c79f8c7`, `83ada7349ec463b7`, `d1c89deb2a285952`). No web query.
Nothing was written to the knowledge-base database.

## Runs

- `kb-20261119-153345-ed7ee04`: novelty update; completed; the four queries return the same
  records as on 2026-11-15 (9, 8, 22, 19), none new, none dropped.
- `kb-20261119-153659-4688c5b`: number check; completed, every number inside its preregistered
  band (k = 1.095-1.348; r_t 1.0001; beta_max 1.0011; Peters 5/64 exact, 0.991; brief's 6e3 is
  6328).
- `kb-20261119-154140-0c9116d`: tally and locator check; completed, 66 rows, 45 / 18 / 3 / 0, 97
  locator spans, no problem.
- `kb-20261119-154346-78256f1`: the same check on the final CHECK.md (after a precision in the
  note of row 2); identical tally, no problem. Reference run for the tally.

All runs: processors, one core, seconds each, output under `scratch/kb/<run_id>/`, manifests
under `tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s311.n`); row s311.3 proposes the label [VERIFIED] for the [BACKGROUND] item of line 269.
  Optional, for row 1.5: Track F's passage times (163, 223, 285 GM/c^3 from 3, 4, 5 r_t;
  `tracks/F-hills/novelty/scope/SCOPE.md:93-97` on `track/F-hills`) show that "a few hundred
  GM/c^3 of one passage" holds for starts within about 5 r_t; row 1.5 does not say so.
- To F-hills: (1) `novelty/scope/SCOPE.md:98-99` writes v_ej ~ v_b q^(1/6) = 0.27 c at q = 10,
  a_b = 30 r_gb with k = 1; Hills' own numbers give k = 1.10-1.35 (run
  kb-20261119-153659-4688c5b), i.e. 0.30-0.36 c, and the locator of the scaling in 0911.1136 is
  `prp.tex:106-116` (lines 92-106 hold the energy estimates). (2) `NOVELTY.md:107` cites
  1203.6185 as "Bai et al. 2011": arXiv lists Cao first under another title; both titles belong
  to one record (ERRATA_ROWS section 5). (3) arXiv:1411.5022 (stars ejected by massive-black-hole
  binaries at up to 0.3 c) is a Hills-type ejection with a heavy second body, possibly worth a
  line in the novelty background. (4) The four citation and title queries were repeated today
  with no change; the other queries of the search log were not.
- To the kb lead: the metadata divergence of arXiv:1203.6185 (two titles, two author orders) for
  the citation resolver; the four new INSPIRE query files listed above.
