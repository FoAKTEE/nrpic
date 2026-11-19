# Work package s34_36: check of brief lines 186-195 and 217-223 (sections 3.4 and 3.6)

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: section 3.4 of the brief, "Early universe (problems dominated by scalar fields)": initial
conditions for inflation (line 190), NR stochastic inflation (191), slow contraction and bounces
(192), preheating and oscillons (193), bubble collisions and cosmic strings (194); and section
3.6, "Structure formation and gravitational waves in the early matter-dominated era": physical
background (219), N-body simulations (220), perturbative calculations and gauge (221), the
black-hole-dominated early matter era (222).

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (66): brief line, quotation, label, verdict, locator, note; plus the one judgement statement (line 188), listed without verdict |
| `ERRATA_ROWS.md` | rows for `coord/BRIEF_ERRATA.md` in its format: 4 wrong or incomplete (s34.1, s36.1-3), 9 imprecise (s34.2-5, s36.4-9), 1 answered (s36.10), 1 defect of a cited source (section 5) |
| `JOURNAL.md` | predictions P1-P10 written after reading the abstracts and before the source checks, their outcomes; predictions P11-P13 of the three registered runs and their outcomes |
| `scripts/meta_dump.py` | titles, authors, abstracts from `kb-data/meta/arxiv-api/` (read-only, standard library; copy of the s31_32 script) |
| `scripts/locate.py` | regex search of the TeX sources in `kb-data/raw/arxiv/`, printing file:line locators (read-only; nothing in the store is executed); copy of the s33 script |
| `specs/l190.txt` ... `specs/l222.txt`, `specs/followup.txt` | the searches run with `locate.py`, one file per paragraph of the brief, plus the follow-up searches |
| `scripts/r_of_mu.py` | checks the printed (mu, r) pairs of arXiv:2512.13673 against its Eq. (r) and that each quoted number is on its stated line; figure |
| `scripts/fig_verdicts.py`, `scripts/figstyle.py` | tally of CHECK.md against its header, existence and line range of every locator, figure (adapted copy of s33's script; vendored copy of `harness/style/figstyle.py`, identical by diff) |

Figures are not committed: they are `scratch/kb/<run_id>/fig_r_of_mu.png` and
`scratch/kb/<run_id>/fig_verdicts.png` of the runs below (all looked at).

## Results in one paragraph

Of 66 statements of lines 186-195 and 217-223, 45 are confirmed as written, 17 confirmed with a
precision and 4 corrected; nothing was left unfound, and all 60 cited papers were already in the
knowledge base. Corrected: (1) line 190, arXiv:2512.13673 gives r_crit ≈ 5.6×10⁻⁶ in the body
(a lower bound, assuming 100 e-folds for the homogeneous solution), not "about 10⁻⁶", which is
the abstract's rounding; the paper's own Eq. (r) reproduces every body pair within 1.5 per cent
and shows that its line 276 pairs mu and r in reversed order (run kb-20261119-150703-95bba8b);
(2) line 219, arXiv:1405.7373 finds that free streaming or kinetic decoupling erases the EMD
enhancement in moduli scenarios, a counter-example to microhalo formation rather than support;
(3) line 222, arXiv:1907.08129 simulates PBHs as cold dark matter from the radiation era to
z = 99, not an early black-hole-dominated era; (4) line 222, in arXiv:2505.21885 the EMD is
driven by a bosonic field with subdominant PBHs, and the double GW peak comes from the PBH-forming
curvature peak plus the sudden end of the EMD, not from the accretion. Precisions worth
carrying: "Latest result" on line 190 is superseded by 2607.06441 (July 2026, spherical
symmetry); 2401.08530 is the formulation, not an NR implementation, of stochastic inflation, and
2610.32592 a thesis; 2312.12499's nonlinear enhancement lies above the reheat-scale peak; the
"fitting formulae" faulted by 2605.04487 are those of 2403.15126, listed one sentence earlier;
nu ≈ 3 is 2.85 and 2.98 for sigma = 0.01 and 0.1; 2009.11081 and 2012.14016 temper "the
gauge-dependence problem is sharpest in MD"; the "[title only verified]" claim about 2610.08045
holds in the source (Omega_GW⁽³⁾ ∝ x⁶) and can become [VERIFIED].

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
python3 -I tracks/kb/brief_check/s34_36/scripts/meta_dump.py 2512.13673 2505.21885   # metadata
python3 -I tracks/kb/brief_check/s34_36/scripts/locate.py tracks/kb/brief_check/s34_36/specs/l190.txt
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s34_36 \
  --input /data/haiyangw/nrpic/kb-data/raw/arxiv/2512.13673/v1/src/main.tex \
  --input tracks/kb/brief_check/s34_36/scripts/r_of_mu.py --cores 1 \
  --purpose "check of the (mu, r) pairs of 2512.13673" -- python tracks/kb/brief_check/s34_36/scripts/r_of_mu.py
harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/brief_check/s34_36 \
  --input tracks/kb/brief_check/s34_36/CHECK.md --cores 1 \
  --purpose "tally and locator check of CHECK.md" -- python tracks/kb/brief_check/s34_36/scripts/fig_verdicts.py
```

No source was fetched. Two INSPIRE queries were made through `harness/bin/nrpic-fetch-arxiv
--inspire-query` (generic, nothing about the project): `refersto:arxiv:2512.13673` was not
understood by INSPIRE (25291 unrelated hits; `kb-data/meta/inspire/query/8f96c307305cd2fa.json`,
not used), `refersto:recid:3093098` gave the 2 citing papers
(`kb-data/meta/inspire/query/48e651357ea82ee5.json`). Nothing was written to the database.

## Runs

- `kb-20261119-150703-95bba8b`: (mu, r) pairs of 2512.13673 against Eq. (r); completed; all
  body pairs within 1.5 per cent, :276 reversed, abstract 10⁻⁶ against 5.6×10⁻⁶; no locator
  problem. Figure `fig_r_of_mu.png` (looked at).
- `kb-20261119-151103-4217175`: tally and locator check; completed, no problem (66 rows,
  45/17/4/0, 78 locator spans); the line-221 bar touched the frame.
- `kb-20261119-151240-7a46af7`: the same after a 10 per cent axis margin; completed,
  `verdicts.json` byte-identical to the previous run; the reference. Figure `fig_verdicts.png`
  (looked at).

All runs: processors, one core, a few seconds each, output under `scratch/kb/<run_id>/`,
manifests under `tracks/kb/runs/<run_id>/`. No card was used; no run is pending.

## Requests

- To orch: merge the rows of `ERRATA_ROWS.md` into `coord/BRIEF_ERRATA.md` (provisional numbers
  `s34.n`, `s36.n`). Row s36.10 proposes the label [VERIFIED] for the 2610.08045 statement of
  line 221; row s34.1 replaces "about 10⁻⁶" by "≳ 5.6×10⁻⁶ (assuming 100 homogeneous e-folds)".
- To orch (harness): `harness/bin/nrpic-fetch-arxiv --inspire-query` passes the query unchanged;
  INSPIRE ignores `refersto:arxiv:<id>` and returns everything (25291 hits), while
  `refersto:recid:<control number>` works. A line in the tool's help would save the next user the
  wasted request.
- To kb lead: the section-5 row (2512.13673, abstract against body, and the reversed pairs of
  line 276) is for the claims layer when it takes rows about cited papers.
- None to core or the tracks. For information through the merge: rows s36.5, s36.6 and s36.8
  bear on Track B's literature baseline (S2), s34.4 on Track E's (S11).

## Not done

- Line 188 is a judgement about the field and was not given a verdict.
- The "Latest result" check rests on one INSPIRE citation query (papers citing 2512.13673); a
  broader search for later 3+1 studies of inflationary initial conditions was not made.
- Topical attributions were checked at the abstract, title and introduction of each source and
  at the lines cited; the full bodies of the 60 papers were not read.
