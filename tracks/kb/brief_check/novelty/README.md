# Work package "novelty": check of brief lines 394-444 and the novelty searches of line 1749

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: every labelled statement, and every specific claim about a cited paper, of brief lines
394-444 (problems S4 to S10), and four of the six novelty searches of line 1749 (section 15 item
5): S5 (black-hole formation with a free-streaming component), S7 (a 3+1 numerical test of the
Burnett conjecture), the null test of S4 (NR test of the cosmological coupling of black holes),
and full-NR binary black holes in a particle dark-matter environment. S11 and S12 are covered by
Tracks E and F.

## What is here

| Path | What |
|---|---|
| `NOVELTY.md` | the four novelty searches: queries, closest papers with locators, verdict and its limits |
| `CHECK.md` | one row per checked statement (33): brief line, quotation, label, verdict, locator, note |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 2 wrong (nov.1-2), 6 imprecise (nov.3-8), 2 answered (nov.9-10) |
| `JOURNAL.md` | predictions P1-P7 written before any source was read, predictions of every run, all outcomes (P5 and P6 failed and are kept) |
| `search/SEARCH_LOG.md` | how the searches were made: INSPIRE batches, web queries, knowledge-base searches, fetched sources |
| `search/queries_1.txt` ... `queries_4.txt` | the INSPIRE query lists (label and query) |
| `search/query_log.tsv` | one line per INSPIRE request: label, UTC, total hits, status, record path, query (61 requests) |
| `specs/*.txt` | regular-expression searches of the TeX sources run with `scripts/locate.py` |
| `scripts/run_queries.py` | runs a query list serially through `harness/bin/nrpic-fetch-arxiv --inspire-query` and logs it |
| `scripts/inspire_list.py` | prints the hits (and abstracts) of INSPIRE query records |
| `scripts/locate.py`, `scripts/meta_dump.py` | read-only search of the TeX sources and metadata (copies of the s35/s33 scripts) |
| `scripts/check_numbers.py` | horizon mass and neutrino share at decoupling (line 410); bound on the coupling index k from the NR lattice of 1903.01490 (line 400); figure |
| `scripts/check_package.py` | tally of CHECK.md, every locator, every arXiv id and 22 quoted phrases of the three documents; verdict figure and the landscape of closest papers |
| `scripts/figstyle.py` | vendored copy of `harness/style/figstyle.py` |

Figures and numbers are not committed; they are in `scratch/kb/<run_id>/`:
`fig_numbers.png` and `numbers.json` (runs kb-20261119-154605-3ee42d2, -155605-d5dbd0d,
-155658-4acf70b, identical numbers), `fig_verdicts.png`, `fig_landscape.png` and `check.json`
(run kb-20261119-155610-7573cf0 and the final run kb-20261119-160005-PENDING, see the journal).

## Results in one paragraph

S5 is open: no full-GR kinetic calculation of black-hole formation with a free-streaming
component exists, and the leading fluid group says in 2023 and 2025 that only such a simulation can
decide whether neutrino free streaming suppresses or enhances formation in the e+e- epoch
(2303.07980, 2406.11417; add both to the key references). S7 is open as a numerical test, but
its premise (line 434, "all proofs assume U(1) symmetry; 3+1 without symmetry is open") is wrong:
Huneau and Luk proved Burnett's conjecture without symmetry in generalized wave coordinates (2024),
so S7 is a first quantitative demonstration, and its closest numerical predecessor, 1505.02959 (a
3+1 test of Isaacson's radiation average), is more than "related" work. The S4 null test is partly
done: an NR lattice of vacuum black holes keeps horizon masses constant to 0.1 per cent over a
growth of e^2 in the scale factor (1903.01490), i.e. abs(k) <= 5e-4, against the claimed k = 3.11;
what remains new is the ambient expanding matter and the separate accretion flux. The binary item
is done in its broad form by the target paper itself: 2611.12831 evolves in full NR a binary that
forms, inspirals and merges inside a collisionless envelope; open is a pre-existing quasi-circular
binary in a light dark-matter particle distribution with its dephasing against vacuum. Line 410's
[BACKGROUND] numbers hold (decoupling 1-2 MeV; horizon mass 1.50e5 M_sun at 1 MeV; neutrino share
0.488 before and 0.409 after e+e- annihilation) and can become [VERIFIED]. Of 33 statements, 15
are confirmed, 16 confirmed with a precision, 2 corrected (lines 434 and 1749), none unfound.

## Cross-check with the sibling package s5_s6

Lines 406-444 were also checked, independently and at the same time, by `../s5_s6` (its rows
1-27). Compared after both were finished (journal entry 5): the facts agree everywhere, including
the only correction of these lines (line 434, both CORRECTED on 2403.03470) and the numbers of line
410 (both 1.50e5 M_sun at 1 MeV; neutrino share after annihilation 0.405 there with N_eff = 3,
0.409 here with N_eff = 3.045). The verdict classes differ on eight statements, seven of them between CONFIRMED and
CONFIRMED (precision) (lines 410 twice, 414, 435 twice, 442, 443), and one more: line 437 ("No numerical work was found"), CORRECTED in s5_s6
because of 1505.02959, CONFIRMED (precision) here because the statement is about a test of the
Burnett correspondence, which 1505.02959 is not. The lead chooses; the substance (1505.02959 must be
cited as the closest prior) is the same in both. Coverage differs too: s5_s6 also rates lines 422,
426 (the c/v estimate) and 428, which this package leaves out as judgements or reference lists;
this package also covers lines 398-404 and 1749.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/novelty/scripts/inspire_list.py --abstracts \
  /data/haiyangw/nrpic/kb-data/meta/inspire/query/5fa211fb35281865.json     # any logged record
python3 -I tracks/kb/brief_check/novelty/scripts/locate.py tracks/kb/brief_check/novelty/specs/l432_437.txt
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/novelty \
  --cores 1 --purpose "number check" -- python tracks/kb/brief_check/novelty/scripts/check_numbers.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/novelty \
  --cores 1 --purpose "package check" -- python tracks/kb/brief_check/novelty/scripts/check_package.py
# repeating the searches (network; one INSPIRE request at a time, through the fetch command only):
python3 -I tracks/kb/brief_check/novelty/scripts/run_queries.py \
  tracks/kb/brief_check/novelty/search/queries_1.txt /data/haiyangw/nrpic/scratch/kb/tmp/novelty/rerun_log.tsv
```

Nothing in this package writes the knowledge-base database. Seven arXiv sources were fetched
into the store with `harness/bin/nrpic-fetch-arxiv` (2403.03470, 2009.08968, 2404.07659,
2406.11417, 2606.26532, 2607.09285, 2508.13294); the kb lead may want to ingest them. No card
was used; all runs are single-core processor runs of a few seconds.

## Requests

- To the orchestrator (via the kb lead): merge `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md`
  (reconciling lines 406-444 with `../s5_s6/ERRATA_ROWS.md`); in section 5 of the brief or the
  charter, narrow the binary-in-dark-matter item of line 1749 to the open configuration of
  NOVELTY.md section 4, and restate S7 without the line-434 premise.
- To Track D (S4 null test): design the run to measure the accretion flux through the horizon
  separately and to reach abs(k) well below 5e-4, the bound an NR vacuum lattice already gives
  (1903.01490); cite that lattice and 2302.07878's own expectation k = 0 for Kerr.
- To the kb lead: ingest the seven fetched sources; record the claims "Burnett's conjecture is
  proven without symmetry in generalized wave coordinates (2403.03470:143)" and "horizon masses of
  an NR black-hole lattice constant to 0.1 per cent over a growth e^2 (1903.01490:653-657)" in
  the claims layer; the brief-check package that covers brief line 235 (a black hole in a particle
  environment, [TO VERIFY], named in Track D's request to kb) should take NOVELTY.md section 4 into
  account.
- To whoever takes S5 (no track yet): start from 2303.07980 :343-368 and 2406.11417 :485-508; the
  calculation must cover the gradual decoupling between 2 and 1 MeV, not only the two limits.
