# Journal of work package s310 (brief lines 257-266, section 3.10)

Owner: kb (helper). Worktree `wt/kb-brief`, branch `kb/brief-check`.

## Entry 1 (2026-11-19 07:31 PST): set-up, metadata pass, predictions

Done before this entry: merged main into the worktree (eeacea6d), read CLAUDE.md, the charter
to "Owners", decisions 0010, 0016, 0017, `coord/BRIEF_ERRATA.md`, brief lines 30-68 and
250-271. Rows of the errata on these lines: 1.4 (line 262, the constraints of 2512.14649 are
satisfied to second order in the noise). Rows 4.2 and 4.4 (sheet E) and the section-5 rows on
2502.06783, 2610.32592, 2512.14649 and 2206.11234 touch papers of these lines but not their
statements; none of them is repeated.

Line 265 carries [JUDGEMENT] and is outside the scope (the task names [BACKGROUND],
[TO VERIFY] and [VERIFIED] with a number or a specific claim about a paper); two factual
sub-claims in it are checked as "(unl.)" rows because they are statements of fact, not
judgements.

All 74 papers cited in lines 257-266 are in the store
(`/data/haiyangw/nrpic/kb-data/raw/arxiv/<id>/<v>/src`, old-style ids with `_`), each with an
arxiv-api record, so no fetch is needed. Titles, authors, journal references and abstracts
were dumped with `scripts/meta_dump.py` (copy of the s35 script) into
`scratch/kb/tmp/s310/meta_all.txt` and read. The predictions below are written after that
reading and before any check at the TeX source. A CONFIRMED or CORRECTED verdict needs a TeX
locator file:line (the abstract inside the TeX counts; the metadata abstract alone does not).

Predictions (what would refute each is in brackets):

P1. Line 259, first sentence [BACKGROUND], astro-ph/9407016 (Starobinsky and Yokoyama 1994):
    the TeX writes a Langevin equation for the coarse-grained field with a noise from the
    short-wavelength modes that cross the coarse-graining scale (k = epsilon a H), white noise
    with amplitude H^3/(4 pi^2). CONFIRMED (precision): the formalism originates in
    Starobinsky 1986 (not on arXiv), which 9407016 cites; 9407016 is about the equilibrium of
    a self-interacting field in de Sitter. [Refuted if no Langevin equation is in the TeX.]
P2. Reviews: 2203.13852 (Cruces) is a review, CONFIRMED; 2009.08715 (Vennin) is a
    habilitation thesis that opens with a review of the formalism, CONFIRMED (precision).
P3. "delta N and the separate-universe approach": six of the seven fit as written; the
    exception is astro-ph/0504508 (Rigopoulos, Shellard, van Tent), a nonlinear
    long-wavelength (gradient-expansion) formalism with stochastic sources rather than delta N,
    CONFIRMED (precision). [Refuted if one of the seven has nothing to do with either.]
P4. "Early comparisons and correlation functions": 0808.1786, 1003.1327, 1506.04732,
    1409.7399 fit; gr-qc/9911029 (Winitzki and Vilenkin) is about the noise correlator for
    smooth windows, not a comparison, CONFIRMED (precision).
P5. Line 260 [BACKGROUND]: the exponential (non-Gaussian) tail and the sensitivity of the
    PBH abundance to it are stated in the TeX of 1912.05399 and 1707.00537; each of the six
    papers is about the tail of P(zeta) or P(R) and PBHs. CONFIRMED, and the label can become
    [VERIFIED]. [Refuted if one of the six does not discuss the tail.]
P6. Clustering 2402.08642, compaction 2312.12911 and 2510.09303, trees 2501.05371: CONFIRMED.
P7. USR background: astro-ph/0101406 gives the enhancement of superhorizon curvature
    perturbations when a phidot/H falls (the mechanism behind USR; the word "ultra-slow-roll"
    probably absent), CONFIRMED (precision); 1911.00057 (bump or dip in the potential) has a
    short USR-like phase, CONFIRMED (precision) or weak; 1910.08487, 2507.04114, 2504.05937
    are stochastic or Hamilton-Jacobi studies of USR, CONFIRMED.
P8. Line 261 [titles VERIFIED]: all descriptors fit. Possible precisions: 2206.11234 solves
    the first-passage problem of the Langevin equation (PyFPT), not the field equation
    itself; 2403.12811 is a lattice study of oscillatory features (non-perturbative), still
    "conventional lattice inflation"; 2302.00655 is a method (cosmological flow) rather than
    a code paper. The arxiv-api record of 2604.03628 carries the journal reference of
    2410.23942 (a metadata defect for kb, not a brief error).
P9. Line 262 [VERIFIED: abstracts]: 2401.08530: the sources depend on the first two time
    derivatives of the window function, the MS mode functions and the slow-roll parameters;
    the brief's "the time derivative" is a precision. BSSN sources derived: CONFIRMED.
    2512.14649 slow-roll and USR tests: CONFIRMED (constraint wording already errata 1.4).
    2610.32592: Keldysh validity criterion, analytic constraint solutions, first look at
    eternal inflation: CONFIRMED. 2502.06783: CONFIRMED. 2412.19731 (Florio and Shellard,
    GRChombo/GRTeclyn): CONFIRMED. 2412.16143: CONFIRMED (precision: a criterion for when
    classical evolution suffices for interaction terms, "quantum interactivity").
    2606.07467: CONFIRMED (single author, Launay).
P10. Line 263 [VERIFIED: abstracts]: (i) CONFIRMED (precision: codes that take an exact FLRW
    background and neglect metric perturbations; the slow-roll spectrum decays as H^4;
    reheating is less sensitive). (ii) CONFIRMED (precision: a transient weakening of the
    shear-free approximation during the USR phase). (iii) CONFIRMED (precision: the bias is
    for a periodic length close to the inflationary scale (G rho_infl)^-1/2).
P11. Line 264 [titles only verified]: all descriptions fit; 2410.17987 (small-noise expansion
    of the non-Markovian system) fits "beyond slow roll" only loosely, CONFIRMED (precision).
P12. Line 265, factual sub-claims: "public AthenaK has no scalar field" holds for the
    upstream clone in the store if one is indexed [TO VERIFY otherwise]; the GRChombo/GRTeclyn
    option is superseded by decisions 0004 and 0010 (as errata row 4.2 for sheet E).

Overall: no CORRECTED verdict among the labelled statements, about two thirds CONFIRMED and
one third CONFIRMED (precision), none NOT FOUND. [Refuted by any CORRECTED verdict or any
paper whose TeX cannot be located.]

## Entry 2 (2026-11-19 07:37 PST): source checks done, outcomes of P1-P12, prediction of the run

Searches: `specs/l259.txt` ... `specs/l264.txt`, `specs/extra.txt` with `scripts/locate.py`
(copy of the s35 script), plus direct reads of the cited lines. astro-ph/9407016 has no TeX
in the store (PostScript source); I read pages 2-6 of its stored `source.pdf` with the Read tool
and extracted its text once with `pdftotext` into `scratch/kb/tmp/s310/pdf/9407016.txt` to find
the reference list (page 20). For line 265: the knowledge base was queried once
(`kb search --text-only`, snapshot `current`) for the inflaton condensate as matter, and the
upstream AthenaK clone `kb-data/raw/github/IAS-Astrophysics__athenak/src` was searched with
grep; `git log -1` was run once inside that clone to read its commit (c5a0d7f9155a; the clone's
git config is written by our own clone, nothing of the repository is executed); no other
command was run there. The metadata of 2604.03628 was read from `kb-data/meta/{arxiv-api,inspire}`.

Outcomes (CHECK.md, 74 rows: 49 CONFIRMED, 25 CONFIRMED (precision), 0 CORRECTED, 0 NOT FOUND):

P1 held in substance, with two misses in detail: the source is PostScript, so the locator is a
   PDF page; and the origin cited by 9407016 is Starobinsky 1982 (ref. [5]) for the idea and
   1984/1986 (refs. [11, 12]) for the Fokker-Planck form, not 1986 alone. The precision found:
   kicks enter at k = epsilon a H (epsilon much less than 1), not at horizon crossing (row 1).
P2 held (rows 2, 3).
P3 held (row 6 is the one precision).
P4 held for gr-qc/9911029 (row 11); not predicted: 1003.1327 and 1409.7399 also only loosely
   fit "comparisons and correlation functions" (rows 13, 15).
P5 partly failed: predicted plain CONFIRMED for the tail statement; it is CONFIRMED (precision)
   because 2406.02417 (line 264) obtains non-Gaussian tails without stochastic inflation, so the
   tail is not a diffusion effect alone (row 16); 2402.12672 is a book chapter (row 22).
P6 held (rows 23-26).
P7 held for astro-ph/0101406 (no "ultra-slow-roll" in the source) and 1911.00057 (it says
   "constant-roll", never USR); failed for 2504.05937, predicted CONFIRMED, found to be a
   limitation result on the Hamilton-Jacobi approach (rows 27, 28, 31).
P8 partly failed: 2206.11234 is plain CONFIRMED (it does simulate the Langevin equation);
   precisions as predicted for 2403.12811 and 2302.00655 (rows 39, 46). The metadata defect of
   2604.03628 holds: arXiv journal_ref = PRD 111, 063518 (2025), the reference of 2410.23942;
   INSPIRE publication_info = Phys.Rev.D 114 (2026) 6, 063530 (row 42).
P9 held for 2401.08530 (first two time derivatives, row 48) and 2412.16143 (row 56); failed for
   2412.19731 (predicted CONFIRMED; its authors are Florio and Shellard, a precision, row 55);
   not predicted: the thesis's "analytic solutions of the constraints" are perturbative,
   leading-order solutions (row 52).
P10 held for all three warnings; numbers: normalised momentum-constraint residual grows to
   O(0.5) during USR (2604.00978 L1141); at least five times the inflationary scale without
   periodic regularity (2607.06441 L369) (rows 58-60).
P11 held for 2410.17987 (row 66); not predicted: 2512.17070's deviation is conditional (row 63).
P12 held: no scalar-field module in upstream AthenaK at c5a0d7f9155a; the GRChombo/GRTeclyn
   alternative is settled by decisions 0004 and 0010 (row 74). Row 73 (inflaton condensate as
   matter) confirmed with the resonance/prompt-reheating caveat.
Overall prediction (no CORRECTED, about a third with a precision) held: 25 of 74.

Prediction of run 1 (`scripts/fig_verdicts.py`, tally, locator and coverage check): 74 rows;
tally 49 / 25 / 0 / 0 equal to the header; every locator span valid (TeX file exists and is long
enough, the PDF has at least 20 pages, metadata, github and repository paths exist); all 74
arXiv identifiers of brief lines 257-266 occur in CHECK.md; exit status 0; the figure shows
line 259 with 15 rows, 260 with 16, 261 with 15, 262 with 11, 263 with 3, 264 with 12, 265
with 2. Refuted by any problem the script lists.

## Entry 3 (2026-11-19 07:39 PST): outcome of the run, deliverables

Run kb-20261119-153817-085d90b (`scripts/fig_verdicts.py`): completed, exit 0; 74 rows, tally
49 / 25 / 0 / 0 equal to the header, 96 locator spans valid (TeX files and lines, the PDF of
astro-ph/9407016 with page 20 within it, metadata, the AthenaK clone path, four repository
files), 74 of 74 arXiv identifiers of brief lines 257-266 present in CHECK.md, no problem.
Prediction held, including the rows per line (15, 16, 15, 11, 3, 12, 2). Looking at the
figure: the x-axes ended exactly at the longest bars (16 and 41), so the bars touched the
frame; fixed with a 10 per cent margin (commit before the rerun). Rerun
kb-20261119-153831-19034bc: identical numbers; figure read again, bars clear of the frame,
legend above both panels, no overlap. Reference run.

Deliverables: CHECK.md (74 rows), ERRATA_ROWS.md (13 rows in section 2, 1 in section 4, 1 in
section 5; nothing in sections 1 and 3), README.md with the requests. Not done: no second agent
has checked the verdicts (the lead's review); nothing was fetched or written to the database.
