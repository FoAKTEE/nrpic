# Journal of work package s33 (brief lines 164-185, section 3.3)

Owner: kb (helper). Worktree `wt/kb-brief`, branch `kb/brief-check`.

## Entry 1 (2026-11-19 06:40 PST): set-up, metadata pass, predictions

Done before this entry: merged main into the worktree, read CLAUDE.md, the charter to
"Owners", decisions 0010, 0016, 0017, `coord/BRIEF_ERRATA.md` (no row of it is on lines
164-185, so nothing here repeats it), brief lines 30-68 and 160-189.

All 53 papers cited in lines 164-185 are in the store (`/data/haiyangw/nrpic/kb-data/raw/arxiv/
<id>/<v>/src`; gr-qc/0702082 as `gr-qc_0702082`), so no fetch was needed. Titles, authors,
journal references and abstracts were dumped from `kb-data/meta/arxiv-api/` with
`scripts/meta_dump.py` (outputs `scratch/kb/tmp/s33/meta{1,2,3,4}.txt`). The abstracts were
read; the predictions below are written after that reading and before any check at the TeX
source. A CONFIRMED or CORRECTED verdict needs a TeX locator file:line (an abstract alone is
not enough; the abstract text in the TeX counts).

Predictions (what would refute each is in brackets):

P1. Line 166, "In 2016 three groups ... first full-NR cosmological simulations without
    symmetry": the two PRLs (1511.01105, 1511.05124) appeared in 2016 (posted November 2015);
    1611.05447 was posted November 2016 and published in 2017. CONFIRMED with a precision on
    dates. [Refuted if one of the three uses a symmetry reduction or a non-NR method.]
P2. Line 166, 1807.01711: "global backreaction energy density of order 1e-8 of the matter
    energy density" is in the source; the paper calls the result preliminary and says
    "in our chosen gauge"/"under our assumptions"; the simulations start at z = 1000 from CMB
    initial conditions and run to z = 0. CONFIRMED (possibly with precision). [Refuted if the
    run stops before z = 0 or the number differs.]
P3. Line 166, 2408.03049: negligible backreaction on these hypersurfaces "even on very small
    scales", "up to 10%" in Omega_R at radius ~200 Mpc, "up to 5%" density change z = 1 -> 0
    from in- and outflow. CONFIRMED, with the precision that 10 per cent is an upper value
    ("up to"), not a typical value ("about"). [Refuted if the numbers differ in the body.]
P4. Line 168, 1908.05683 introduction says fluids fail at multi-streaming and that
    multi-streaming is generic. CONFIRMED. [Refuted if the introduction does not say it.]
P5. Line 168, "East et al. compared ... particle by particle": the comparison is of quantities
    measured by fiducial observers (density, expansion, velocity), with matched initial
    conditions, not a per-particle comparison. Probability 60 per cent that this is a
    correction. [Refuted if the paper compares individual particle trajectories.]
P6. Line 168, 2409.01939 is a review published in Living Reviews in Relativity; the TeX may not
    say so (the arxiv-api record has no journal reference), then the INSPIRE record decides.
    The "sub-percent" summary: probability 50 per cent that the review says it in these words.
    [Refuted if no sub-percent statement about Einstein-Vlasov vs Newtonian N-body is found.]
P7. Line 168, 1810.05203: the paper's finding is that LINEAR THEORY describes the metric well
    in Newtonian and harmonic gauges and not in comoving-synchronous gauge; "very poor N-body
    convergence in comoving synchronous gauge" is a misreading. Probability 70 per cent of a
    correction. [Refuted if the paper reports poor convergence of its N-body evolution in
    synchronous gauge.] Also: does the paper use BSSN plus N-body particles (CosmoGRaPH)?
    Expect yes.
P8. Line 168, "Other particle-type implementations": 1611.03437 is a perfect-fluid scheme
    (already found by package s31_32, CHECK #30 there, for line 149), 1904.07841 is N-body,
    2307.15194 is SPH (a particle discretisation of a fluid, with shell crossing only through
    the SPH artificial viscosity/pressure). CORRECTED for 1611.03437. [Refuted if 1611.03437
    evolves particles.]
P9. Line 170, 2209.06775 presents a GR ray tracer (mescaline) for NR spacetimes. CONFIRMED.
P10. Lines 172-174: the numbers of 2603.24838 (20 observers, l < 100, 0.05 < z < 3, 3-30 per
    cent, mostly below cosmic variance), 2606.05479 (1 of 20 observers, 2 sigma) and
    2606.18437 (z <~ 0.2, sub-dominant to statistical error) are in the sources. CONFIRMED.
    [Refuted if a number differs.] Dates (2026) CONFIRMED from the metadata.
P11. Line 176, topical attributions of 1807.01714, 2103.11918, 2111.14423, 2402.09659,
    2507.01095 (Hubble-flow anisotropy, local H0), 2010.07274 (curvature), 2404.06242 (redshift
    drift), 2403.15134 (voids): all CONFIRMED.
P12. Line 178, gevolution (1604.06065): six metric degrees of freedom in Poisson gauge,
    canonical momentum valid for relativistic particles. CONFIRMED. 2607.17929 GPU version,
    CONFIRMED. 2603.24179 uses gevolution simulations (expect yes), 2106.01347 and 2505.04731
    use gevolution (abstracts say so). [Refuted if 2603.24179 uses another code.]
P13. Line 180, Green-Wald: traceless effective stress-energy with positive energy density
    under the weak energy condition; precision: the WEC assumption. Buchert et al. dispute
    it. Verweg et al.: averaging gives gauge-dependent backreaction. Reviews: all four are
    reviews/lecture notes. CONFIRMED (Green-Wald with precision).
P14. Line 182, timescape realises Buchert averaging: CONFIRMED (0909.0749 abstract). Pantheon+
    ln B > 5 and ln B > 1 for z > 0.075 come from 2412.15143 only; 2311.01438 reports other
    numbers (weaker evidence). CONFIRMED (precision: the numbers are 2412.15143's).
    [Refuted if 2311.01438 also reports ln B > 5.]
P15. Line 182, 2406.05048 (DES-SN5YR beyond LCDM): timescape is fitted; combined with BAO
    the "Suspiciousness" shows tension and the AIC disfavours timescape relative to flat
    LCDM. Probability 60 per cent CONFIRMED as stated; the BAO data may be "BAO" generally
    (with or without "angular scales"). [Refuted if timescape is not in the combined-probe
    analysis or the AIC prefers it.]
P16. Line 182, 2503.14738 hint of evolving dark energy: CONFIRMED (2.8-4.2 sigma with SNe).
    2601.20633: three toy models; similar magnitude, maybe not the whole deviation. CONFIRMED.
P17. Line 184, 1304.2884, 2009.11292, 2602.03928 as local-void explanations of H0: CONFIRMED,
    with the precision that 2009.11292 needs MOND (the void contradicts LCDM there).
    2606.02712: z0 compatible with zero (-0.4 +0.8/-0.9 per cent for z > 0.5; -0.1 +- 0.7 for
    z > 0.29), BUT the required 0.84 per cent fits almost as well as LCDM (Delta chi^2 < 2),
    and the data are BBN + CMB + BAO + cosmic chronometers, not DESI BAO alone; the paper
    concludes the void "cannot be ruled out". CORRECTED (incomplete). [Refuted if the body
    states that the void model is excluded.]
P18. Line 184, tests of the cosmological principle: 2207.05765 (review), 2009.14826 (quasar
    dipole), 2206.05624 (radio galaxy + quasar dipole), 2302.02028 (CF4 bulk flow), 2510.05340
    (bulk flows review). CONFIRMED.

Expected totals: about 45 rows; 3 to 5 CORRECTED (P5, P7, P8, P17 most likely), the rest
CONFIRMED, several with a precision; NOT FOUND possible for the "Living Review" journal (P6)
if INSPIRE has no record in the store.

## Entry 2 (2026-11-19 06:46 PST): outcomes of the source checks

All 53 rows of `CHECK.md` were checked at the TeX sources (locators in the table; regex specs
in `specs/`, outputs in `scratch/kb/tmp/s33/loc_*.txt`; passages read with `sed -n`).

P1. Partly refuted, in the direction of a precision: 1611.05447 is not independent of the other
    two; it cites them as the simulations "free of these symmetries" that "have only emerged
    within the last year" and follows their approach (`inca_2016a.tex:148-151`). Dates as
    predicted (INSPIRE: PRL 116 (2016) 251301, 251302; PRD 95 (2017) 064028). CHECK #1,
    CONFIRMED (precision).
P2. Partly refuted. Run to z = 0 from z = 1100: confirmed. The number 1e-8 is the abstract's
    only; the body gives Omega_Q + Omega_L ~ 1e-9 for the backreaction and Omega_R ~ 1e-8 for
    the curvature (`INCAPRD2019.tex:524, 644`). I had not expected an abstract-body
    inconsistency. CHECK #3, CONFIRMED (precision); also a defect of the source.
P3. Confirmed as predicted ("up to" 10 per cent; "up to a 5%"), CHECK #4-6. New: EdS model
    with h = 0.45 (`main.tex:216`), and the 5 per cent appears in the abstract only.
P4. Confirmed verbatim (`main.tex:150-151`), CHECK #7.
P5. Refuted as a correction: the paper does compare trajectories, of tracer test particles and
    fiducial observers with consistent initial data (`main.tex:292-296, 429-433, 468-472`),
    and the review calls it an explicit comparison of trajectories (`LRCosmo.tex:1068`). Kept
    as CONFIRMED (precision): tracers, not every particle. CHECK #8.
P6. Confirmed: "sub-percent level ... abs(Psi_N) <= 0.1" (`LRCosmo.tex:1068`); Living Rev. Rel.
    28 (2025) 5 in the INSPIRE record. CHECK #9.
P7. Refuted. The paper does report poor convergence of its N-body system in comoving
    synchronous gauge and switches to a fluid there (`grnbody.tex:287-294`). The brief is
    right; the paper's headline (linear theory fails for the synchronous-gauge metric) is a
    separate point. CHECK #10-11, CONFIRMED.
P8. Confirmed: 1611.03437 is a perfect-fluid scheme (CHECK #12, CORRECTED); 1904.07841 N-body
    (CONFIRMED); 2307.15194 SPH that also handles collisionless matter past shell crossing
    (CONFIRMED (precision)).
P9. Confirmed, CHECK #15.
P10. Confirmed, CHECK #16-21, with precisions on #20 (observer #18 agrees with DESI within
    1 sigma; most observers infer the opposite quadrant) and #21 (the statistical error in the
    body is a forecast for an ideal all-sky survey).
P11. Confirmed, CHECK #22-29.
P12. Confirmed, CHECK #30-35; 2603.24179 uses gevolution (`paper_framedragging.tex:1056`).
P13. Confirmed, CHECK #36-39 (#36 with the precision: weak energy condition; proved, not only
    argued, so the [BACKGROUND] label can become [VERIFIED]).
P14. Confirmed: both numbers are 2412.15143's; 2311.01438 has ln B = 2.93 (full sample,
    z_min = 0) and about 0 beyond z_min = 0.075 for the full sample. CHECK #41.
P15. Confirmed with precision: BAO-theta_perp from SDSS, AIC half-difference +6.3, strong
    tension by the Suspiciousness; with SNe alone timescape is weakly preferred. CHECK #42.
P16. Confirmed, CHECK #43-44.
P17. Confirmed: 2606.02712 is CORRECTED (incomplete; z_0 also consistent with the void value
    0.84 per cent; "cannot be ruled out"), CHECK #48; precisions on 1304.2884 and 2009.11292.
P18. Confirmed, CHECK #49-53.

Totals by hand: 53 rows; 38 CONFIRMED, 13 CONFIRMED (precision), 2 CORRECTED, 0 NOT FOUND.
Expected "3 to 5 CORRECTED" in entry 1: refuted, 2 (P5 and P7 did not become corrections).

## Entry 3 (2026-11-19 06:46 PST): prediction for the tally and locator-check run

Test: `scripts/fig_verdicts.py` parses `CHECK.md`, checks that the header totals equal the
tally of the verdict column and that every TeX locator names an existing file of the store
whose length covers the line numbers given (metadata locators: the file exists), and draws the
verdicts per brief line and per label.

Prediction: 53 rows, tally {CONFIRMED 38, CONFIRMED (precision) 13, CORRECTED 2, NOT FOUND 0}
equal to the header; corrected rows 12 (line 168) and 48 (line 184); no locator problem (about
100 locators). The figure: line 176 the longest bar (8 rows, all CONFIRMED), line 168 with the
one red segment among 8 rows, line 184 with the other among 9 rows; right panel: unlabelled
the largest group (about 28), VERIFIED about 24, BACKGROUND 1.
Refuted if: the tally differs from the header (a miscount by hand), any locator names a
missing file or a line beyond the end of its file, or the parser fails on a row.
