# Work package s7_s8: check of brief lines 554-625 (section 7, open questions; section 8, surprises)

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: the 26 open questions of section 7 (lines 556-592) and the twelve candidates and the
exploration protocol of section 8 (lines 596-622): every [BACKGROUND] and [TO VERIFY]
statement, every specific claim about a cited paper (35 papers), and whether each open question
is still open.

## What is here

| Path | What |
|---|---|
| `CHECK.md` | part A: 42 statement rows (brief line, quotation, label, verdict, locator, note); part B: status of Q1-Q26; part C: status of U1-U12 |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 7 imprecise or relabelled (s78.1-7), 1 [TO VERIFY] answered (s78.8), 1 defect of a source (section 5), and proposed updates of ten open questions (not errata) |
| `JOURNAL.md` | predictions P1-P8 before any source was read, the predictions of the two runs, all outcomes (P4 failed in part; two debugging runs that failed on code faults are on record) |
| `scripts/locate.py`, `scripts/meta_dump.py` | regex search of the TeX sources in `kb-data/raw/arxiv/` with file:line locators; titles and abstracts from `kb-data/meta/arxiv-api/` (copies of the s33/s35 scripts; read-only, standard library) |
| `specs/s*.txt` | the source searches run with `locate.py`, one file per group of lines |
| `scripts/run_inspire.sh`, `specs/inspire_queries*.txt`, `specs/inspire_reused.txt` | INSPIRE queries run one after another through `harness/bin/nrpic-fetch-arxiv --inspire-query`; the first batch (`refersto:arxiv:<id>`) failed as a search and is on record only; `inspire_reused.txt` lists answers other kb sessions had stored the same day |
| `scripts/inspire_summary.py` | prints the stored INSPIRE answers of a spec file (arXiv id, citations, title) |
| `scripts/gem_sign.py` | run 1: the sign of the gravitomagnetic interaction (line 604) in linearized GR, symbolic (sympy) and by finite differences of the full metric, against the EM analogue; figure |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | run 2: tally of the three tables of CHECK.md against their header sentences, existence and line range of every TeX locator, existence of every metadata file, stored INSPIRE answer and run manifest; figure (vendored copy of `harness/style/figstyle.py`) |

Figures are not committed: `scratch/kb/<run_id>/fig_gem_sign.png` and
`scratch/kb/<run_id>/fig_verdicts.png`; both were inspected (JOURNAL entries 3 and 4).

## Results in one paragraph

No statement of lines 554-625 is wrong. Of 42 checked statements 19 are confirmed as written,
22 confirmed with a precision, and 1 corrected: the [TO VERIFY] of line 583 (stability of an
Einstein-de Sitter-type background) now has an answer for fluids, from two 2026 papers already in
the store: nonlinear stability for Einstein-Euler with a polytropic equation of state (n > 3) on
T^3 (arXiv:2607.09326) and Gowdy-symmetric numerics (arXiv:2606.16879), against linear
instability for dust; for massive Vlasov matter nothing was found. The [BACKGROUND] statements
of line 604 are confirmed: the Newtonian instabilities at four store papers, the gravitomagnetic
sign by derivation (run 1; the net force between co-moving masses stays attractive, which a
reader of the brief should know). Of the 26 open questions none is answered, 16 are partly
answered (Q1, Q2, Q5, Q7, Q8, Q11-Q15, Q17, Q19-Q23) and 10 are open (Q3, Q4, Q6, Q9, Q10, Q16,
Q18, Q24-Q26); of the twelve candidates 4 have related work, 6 none, 2 were not searched (U8,
U9).

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s7_s8/scripts/meta_dump.py 2607.09326 2606.16879         # metadata
python3 -I tracks/kb/brief_check/s7_s8/scripts/locate.py tracks/kb/brief_check/s7_s8/specs/sQ20.txt
python3 -I tracks/kb/brief_check/s7_s8/scripts/inspire_summary.py tracks/kb/brief_check/s7_s8/specs/inspire_queries2.txt
# new INSPIRE requests (sequential, through the fetch command only):
bash tracks/kb/brief_check/s7_s8/scripts/run_inspire.sh tracks/kb/brief_check/s7_s8/specs/inspire_queries2.txt <log>
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s7_s8 \
  --cores 1 --purpose "gravitomagnetic sign" -- python tracks/kb/brief_check/s7_s8/scripts/gem_sign.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s7_s8 \
  --input tracks/kb/brief_check/s7_s8/CHECK.md --cores 1 \
  --purpose "tally and locator check of CHECK.md" -- python tracks/kb/brief_check/s7_s8/scripts/fig_verdicts.py
```

Network use of this package, all through `harness/bin/nrpic-fetch-arxiv`, one request at a time:
63 INSPIRE queries (32 in the failed first batch, 31 in the second) and one arXiv API metadata
request for 20 papers found by the searches. No paper source was fetched (all 35 cited papers
and 24 of the papers found were in the store). Nothing was written to the knowledge-base
database.

## Runs

- `kb-20261119-154153-47eb61f`: gravitomagnetic sign (line 604); completed, all six checks
  passed (h_0x part +4 gamma^2 V w, co-moving total -1/gamma^2, finite differences to 1.2e-6).
- Run 2, tally and locator check: see JOURNAL entry 4 for its id and outcome.

All runs: processors, one core, seconds; outputs under `scratch/kb/<run_id>/`, manifests under
`tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s78.n`): s78.8 answers the [TO VERIFY] of line 583; s78.1 and s78.2 propose [VERIFIED] for
  the two [BACKGROUND] statements of line 604. The last table of `ERRATA_ROWS.md` proposes
  updates of ten open questions of section 7; they are not errata and may belong in a note to
  the tracks instead.
- To orch, for Track A (A-emd-pbh) and Track B (B-emd-gw): Q20 matters for the periodic-box
  runs in an early matter era: Einstein-de Sitter is linearly unstable for dust and stable for
  polytropic fluids with n > 3 (2607.09326); whether velocity dispersion of particles stabilises
  it is not known. Nothing to change in their plans; it is context for interpreting long runs.
- To orch, for Track F (F-hills): Q24 is still open in the literature; the closest recent work is
  arXiv:2605.22525 (binary scattering regimes around Kerr in a local inertial frame, with a
  chaotic regime sensitive to the argument of periapsis) and arXiv:2604.27429 (post-Newtonian
  against metric-perturbation benchmark); F may want them in the knowledge base (only their
  metadata are in the store, 2604.27429 has its source).
- To kb lead: the section-5 row (abstract of 2607.09326 omits the n > 3 condition of its
  theorem) is for the claims layer; 20 papers found here have metadata only in the store (the
  `meta:arxiv-api` locators of CHECK.md) and could be ingested if the
  tracks want them; `refersto:arxiv:<id>` does not work at INSPIRE, use `refersto:recid:<n>`
  with the record id from `kb-data/meta/inspire/<id>.json` (worth a line in the fetch help).
- None to core.
