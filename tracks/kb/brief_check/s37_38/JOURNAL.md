# Journal of work package s37_38 (brief lines 224-238, sections 3.7 and 3.8; open question 20; item 6 of section 15)

Owner: kb (helper). Worktree `wt/kb-brief`, branch `kb/brief-check`.

## Entry 1 (2026-11-19, 07:16 PST from `date`): set-up, metadata pass, predictions

Done before this entry: merged main into the worktree (already up to date), read CLAUDE.md,
the charter to "Owners", decisions 0010, 0016, 0017, brief lines 30-68 (evidence labels),
220-241, 554-595 (open questions; item 20 is line 583) and 1736-1759 (section 15; item 6 is
line 1750), and `coord/BRIEF_ERRATA.md` on main: none of its rows is on lines 224-238. Rows
that touch papers cited here, but on other brief lines, are not repeated: 1.6 (2601.17117, line
384), 1.7 (1901.08528 and 1805.09034 on the r^(-9/4) slope, line 398), 1.14 (1305.2619 treats
Schwarzschild only, sheet D), section 5 (defects of 2108.11967, astro-ph/0110561, 2601.17117,
1305.2619). The sibling package s34_36 (lines 186-195, 217-223) does not overlap. Its scripts
`locate.py`, `meta_dump.py`, `fig_verdicts.py` and the vendored `figstyle.py` (identical to
`harness/style/figstyle.py`, checked with diff) are copied into `scripts/`.

All 52 papers cited in lines 224-238 (and math/0209336 of open question 6, not checked here)
are in the store (`/data/haiyangw/nrpic/kb-data/raw/arxiv/<id>/<v>/src`, TeX present for each)
with arXiv-API metadata, so no fetch is needed for the check of the lines. Titles, authors and
abstracts were read with `scripts/meta_dump.py`. The predictions below are written after
reading the abstracts and before any check at the TeX source. A CONFIRMED or CORRECTED
verdict needs a TeX locator file:line (the abstract in the TeX counts; the metadata alone does
not).

Labels in these lines: [VERIFIED] on 228 (2609.13394), 230 (2506.21779), 234 (2506.17641 and
2601.17117); [BACKGROUND] on 229 (gr-qc/0512031) and 230 (the Burnett conjecture itself);
[TO VERIFY] on 235 ("Full NR with a particle-dark-matter environment was not found"). Every
topical attribution of a cited paper (unlabelled) is checked as a specific claim about a paper,
as in packages s33 and s34_36. The closing sentence of line 234 ("a three-dimensional full-GR
kinetic calculation does not exist yet") is an unlabelled claim about the literature; it is
checked by search, like the [TO VERIFY] of line 235.

Predictions (what would refute each is in brackets):

P1. Line 230, 1706.09501: the abstract proves that small-data polarized-U(1) Einstein-multiple
    null dust solutions are weak limits of vacuum solutions; that is the reverse direction (a
    construction), not a proof of Burnett's conjecture (weak limit => massless Vlasov). The
    brief's "proofs under U(1) symmetry: 1706.09501, 1907.10743" is CORRECTED for 1706.09501.
    1907.10743 proves the conjecture under U(1) symmetry plus an elliptic gauge (CONFIRMED with
    that precision). [Refuted if 1706.09501 claims a proof of the conjecture's direction.]
P2. Line 230, 2506.21779 [VERIFIED]: CONFIRMED; precision: elliptic gauge, small and localized
    data, the approximation goes through multiple null dusts. [Refuted if the source needs
    polarization or states something weaker.]
P3. Line 230, [BACKGROUND] Burnett conjecture statement: CONFIRMED at 1907.10743 (statement
    of the conjecture with its assumptions; Burnett 1989 itself is not on arXiv).
P4. Line 229, gr-qc/0512031 [BACKGROUND]: CONFIRMED (heteroclinic network on the past
    attractor; "quite different" from perfect fluids). [Refuted if the source says the past
    asymptotics coincide with those of a fluid.]
P5. Line 229, the four numerical singularity papers and the review are all vacuum (or
    vacuum plus scalar field), none with Vlasov matter; CONFIRMED as attributions, with the
    precision that no numerical study with Vlasov matter is cited, which bears on open
    question 18. [Refuted if one of them evolves Vlasov matter.]
P6. Line 228, 2609.13394 [VERIFIED]: CONFIRMED (precision): spherical symmetry, matter on
    bounded geodesics, PMC foliation; "up to the timescale expected from the echo mechanism".
P7. Line 228, 2309.00431: CONFIRMED (precision): the formula is proved under stated
    assumptions on a solution close to Minkowski (no-incoming-radiation), not unconditionally.
P8. Line 228, 2510.12429: CONFIRMED (precision): massless Vlasov, double null gauge,
    semi-global large data.
P9. Line 227: the four Minkowski stability papers CONFIRMED (1602.02611 massless, 1707.06141
    and 1707.06079 massive, 2210.00512 massive without compact support); 1709.00267 CONFIRMED
    (massive Vlasov, CMCSH gauge, 3+1 Milne with compact hyperbolic slices); 1306.6223
    CONFIRMED (precision): with a positive cosmological constant, which the brief omits;
    2002.02119 CONFIRMED (precision): Euler on a fixed (non-dynamical) FLRW background with
    a ∝ t, irrotational, 0<K<1/3: not Einstein-coupled and not Vlasov.
P10. Line 226: all five attributions CONFIRMED.
P11. Line 234, 2506.17641 [VERIFIED]: 0.3c and 1e-10..1e-8 occur in the source; "10^9 Msun
    halo -> about 1 Msun seed" may not hold in v3 (abstract: seeds below 10^3 Msun). Predict
    CONFIRMED (precision) or CORRECTED depending on the body; the store has v3 (updated
    2026-09-24), the brief may have read v1/v2. [Refuted if neither number is in the body.]
P12. Line 234, 2601.17117 [VERIFIED]: CONFIRMED; the "spherically symmetric, fluid-type"
    characterisation holds (Misner-Sharp is spherical by construction).
P13. Line 234, the other SIDM attributions CONFIRMED; 2504.00075 is dissipative SIDM.
P14. Line 235 [TO VERIFY] "full NR with a particle-dark-matter environment was not found":
    the NRPIC paper 2611.12831 itself evolves two clumps that collapse to black holes and
    merge inside a collisionless cluster (common horizon), i.e. full NR of a black-hole
    merger in a particle environment, though not an inspiral in a dark-matter spike. Predict
    that a literature search finds no full-NR binary-black-hole inspiral in a particle (N-body
    or Vlasov) dark-matter environment besides that, and that the verdict is CONFIRMED
    (precision) with the 2611.12831 caveat. [Refuted if a search finds such a paper.]
P15. Lines 235-237: attributions CONFIRMED; 2411.12007 is Newtonian N-body (SWIFT); 2402.13762
    is Newtonian N-body; 2306.11588 contains a data test as well as theory.
P16. Open question 20 / item 6 of section 15: predict that no nonlinear stability theorem
    exists for the spatially flat, decelerating (Einstein-de Sitter-type, a ∝ t^(2/3)) FLRW
    solution of the massive Einstein-Vlasov system with Λ = 0; existing results: Λ > 0
    (Ringström's monograph, Andréasson-Ringström T^3-Gowdy), Milne with matter (Andersson-
    Fajman, whose small-matter perturbations include k = -1 matter FLRW solutions at late
    times), Bianchi and other symmetric classes, and results for fluids/dust on decelerating
    or linearly expanding backgrounds. [Refuted if a search finds a stability theorem for the
    EdS-type (k = 0, Λ = 0) Einstein-Vlasov FLRW solution.]

## Entry 2 (2026-11-19, 07:30 PST from `date` at the end of writing): outcomes of the source checks, searches, predictions of the runs

Source checks done with `scripts/locate.py` and the spec files `specs/l226.txt` ... `specs/l237.txt`,
`specs/q20.txt`, `specs/q20b.txt`; outputs read in `scratch/kb/tmp/s37_38_loc{1,2,3}.txt`.
Thirteen sources fetched with `harness/bin/nrpic-fetch-arxiv` (serially; list in CHECK.md header);
26 INSPIRE queries (24 new, 2 read from earlier packages) in `specs/inspire_queries.txt`; two
generic web searches (no project detail). Full results: CHECK.md (60 rows).

Outcomes of P1-P16:

- P1 held: 1706.09501 constructs the reverse direction under polarized U(1) for multiple null
  dusts and calls both of Burnett's questions open (L109, L112): row 23 CORRECTED. 1907.10743
  proves the conjecture under U(1) (not necessarily polarized) plus an elliptic gauge (row 24).
- P2 held (row 25): general (not polarized) U(1), elliptic gauge, compactly supported small data.
- P3 held (row 22). P4 held (row 16; massive and massless both treated, L315-317).
- P5 held with a nuance: gr-qc/9805063 includes magnetic Gowdy (a magnetic field, not pure
  vacuum); none of the five evolves Vlasov matter (rows 17-21).
- P6, P7, P8, P9, P10 held (rows 1-15).
- P11 refuted in part: I expected the "about 1 Msun" seed might be missing from v3; it is there
  (L74, L133, L142, as the conservative estimate). Verdict CONFIRMED (precision), not CORRECTED;
  the same body reports 200 Msun for a 6.3e9 Msun halo from 2601.17117 (L145), and 2601.17117 gives
  3e-8 of the halo mass, above the brief's 1e-10..1e-8 range (rows 34, 35).
- P12 held (rows 37, 38). P13 held, with the precision that 1501.00017 and 1812.05088 treat a
  subdominant SIDM component and 2504.00075 is a semi-analytic population model (rows 28, 29, 36).
- P14 refuted in its verdict: I predicted CONFIRMED (precision) with 2611.12831 as a caveat. At the
  source 2611.12831 does more than I assumed: binary black-hole formation, inspiral, merger and
  ringdown accretion inside a common collisionless envelope, 5e6 particles, strain extracted at
  R = 40 M (L42-44, L1338, L1352, L1360, L1385-1390). That is full NR of a black-hole binary in a
  particle environment, so "not found" is CORRECTED (row 50), with the caveat that the matter is
  generic and the binary forms in place (no pre-existing binary in a dark-matter spike). The search
  part held: no other such paper found.
- P15 held; 2505.09715 is relativistic perturbation theory on a fixed Kerr background (row 46).
- P16 held for Einstein-Vlasov and was incomplete for the field: no stability result for the
  massive Einstein-Vlasov EdS solution beyond spatial homogeneity was found (Bianchi I: 1007.0184),
  but I had not anticipated that in June-July 2026 EdS was shown nonlinearly stable for
  Einstein-Euler with a polytropic equation of state n > 3 (2607.09326 proof; 2606.16879 numerics),
  nor that open k = -1 dust FLRW is proven stable (2107.00457). My prediction that the Milne result
  "includes k = -1 matter FLRW at late times" is not stated in 1709.00267; for dust it is 2107.00457
  L141. Answer written in CHECK.md ("Answer to item 6") and rows 59-60.

Unregistered dry runs (scratch/kb/tmp/s37_38_dry, worktree .venv, to debug the scripts; not
evidence): (a) `fig_verdicts.py` found my hand-written header totals wrong (I had written 19
CONFIRMED / 39 precision; the tally of the verdict column is 23 / 35 / 2 / 0); header corrected.
The check did what it is for. (b) `fig_item20.py`: 21 locators valid; the figure clipped the
row labels and one cell text overflowed; layout fixed (wider left margin, split labels, line
breaks in the dust cell), figure looked at again, readable.

Predictions of the registered runs (made before submitting them):

P17. `fig_verdicts.py` on CHECK.md: 60 rows numbered 1..60, tally 23 / 35 / 2 / 0 equal to the
     header, every locator span valid (97 spans: TeX files exist and are long enough, metadata and
     INSPIRE query files exist), exit status 0; corrected rows 23 (line 230) and 50 (line 235).
     [Refuted if any locator fails or the tally differs from the header.]
P18. `fig_item20.py`: 15 cells, 21 locator spans valid, exit 0; in the decelerated (k = 0) column
     only the two Vlasov cells are "symmetric" (no theorem without symmetry), dust and linear Euler
     "unstable", polytropic Euler "proven". [Refuted if a locator fails.]

## Entry 3 (2026-11-19, 07:32 PST from `date`): outcomes of the registered runs, ERRATA_ROWS, README

- P17 held: run kb-20261119-153032-8849222 completed, exit 0: 60 rows, tally 23 / 35 / 2 / 0 equal to
  the header, 97 locator spans valid, corrected rows 23 (line 230) and 50 (line 235). Figure
  fig_verdicts.png looked at: bars by brief line and by label, legend clear of the bars; the two
  CORRECTED (red) bars on lines 230 and 235.
- P18 held: run kb-20261119-153036-8bc8bee completed, exit 0: 15 cells, 21 locator spans valid; in the
  decelerated column the two Vlasov cells are yellow (theorem with symmetry or homogeneity only),
  dust and linear Euler red, polytropic Euler blue; the cell of open question 20 is outlined.
  Figure fig_item20.png looked at; labels and cell texts readable.

ERRATA_ROWS.md written (1 wrong, 10 imprecise or label upgrades, 2 [TO VERIFY] answered) and
README.md. A span checker (scripts/check_spans.py) was added for the locators of ERRATA_ROWS.md and
the answer section of CHECK.md, which the tally does not read; an unregistered dry run flagged the
two placeholder spans of the CHECK.md header (meta:arxiv-api/<id>), now skipped.

P19. check_spans.py on ERRATA_ROWS.md and CHECK.md: ERRATA_ROWS 56 spans (37 TeX, 4 iq, 15 other),
     CHECK.md 126 spans (73 TeX, 23 iq, 3 meta, 27 other), no problem, exit 0. [Refuted if any TeX
     locator names a missing file or a line beyond its end.]

## Entry 4 (2026-11-19, 07:33 PST from `date`): span check

- P19 held: run kb-20261119-153252-225d6df completed, exit 0, counts exactly as predicted
  (ERRATA_ROWS 56 spans: 37 TeX, 4 iq, 15 other; CHECK.md 126: 73 TeX, 23 iq, 3 meta, 27 other),
  no problem. That run wrote no figure (the script had none), against rule 6; a figure of the span
  kinds per file was added to check_spans.py (dry run looked at, readable) and the check is rerun
  as the reference run with the same prediction (P19 again, plus fig_spans.png written).
- P19 (reference run) held: run kb-20261119-153316-e14e392 completed, exit 0, same counts, no
  problem; fig_spans.png looked at (span kinds per file, "0 problems" on both bars). This run
  supersedes kb-20261119-153252-225d6df as the reference (same result, plus the figure).

Package state at the end: all deliverables written and checked by registered runs; nothing
pending; what is not done is listed in README.md.
