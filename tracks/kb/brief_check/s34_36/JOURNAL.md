# Journal of work package s34_36 (brief lines 186-195 and 217-223, sections 3.4 and 3.6)

Owner: kb (helper). Worktree `wt/kb-brief`, branch `kb/brief-check`.

## Entry 1 (2026-11-19, about 07:02 PST; times of entries 1-2 estimated, `date` read at 07:06): set-up, metadata pass, predictions

Done before this entry: merged main into the worktree (already up to date), read CLAUDE.md,
the charter to "Owners", decisions 0010, 0016, 0017, brief lines 30-68 (evidence labels) and
180-227, and `coord/BRIEF_ERRATA.md` on main: none of its rows is on lines 186-195 or 217-223,
so nothing here repeats it. Sibling packages s31_32 (lines 144-150) and s33 (164-185) do not
overlap these lines; their scripts `locate.py`, `meta_dump.py`, `fig_verdicts.py` and the
vendored `figstyle.py` (identical to `harness/style/figstyle.py`, checked with diff) are copied
into `scripts/`.

All 60 papers cited in lines 186-195 and 217-223 are in the store
(`/data/haiyangw/nrpic/kb-data/raw/arxiv/<id>/<v>/src`, TeX present for each) with arXiv-API
and INSPIRE metadata, so no fetch is needed. Titles, authors, journal references and abstracts
were dumped with `scripts/meta_dump.py` into `scratch/kb/tmp/s34_36/meta{1..6}.txt` and read.
The predictions below are written after reading the abstracts and before any check at the TeX
source. A CONFIRMED or CORRECTED verdict needs a TeX locator file:line (the abstract text in the
TeX counts; the metadata abstract alone does not).

Labels in these lines: [VERIFIED] on lines 190 (2512.13673), 220 (the five N-body papers) and
222 (2505.21885); "[title only verified]" on line 221 (2610.08045), treated as a weak
[VERIFIED] whose content is to be checked. No [BACKGROUND] or [TO VERIFY] label occurs in the
two ranges. Every topical attribution of a cited paper (unlabelled) is checked as a specific
claim about a paper, as in package s33. Line 188 is the author's [JUDGEMENT] and gets no
verdict.

Predictions (what would refute each is in brackets):

P1. Line 190, 2512.13673: mu_crit ≈ 0.02 m_P and r_crit ≈ 1e-6 are in the source, for an
    alpha-attractor T-model with gradient and kinetic inhomogeneities of order unity of the
    inflationary energy scale, ASSUMING 100 e-folds for the homogeneous solution; the authors
    call r_crit a lower bound for that number of homogeneous e-folds. CONFIRMED (precision):
    the brief drops the 100-e-fold assumption and the lower-bound reading. [Refuted if the
    numbers differ in the body or no such assumption is stated.]
P2. Line 190, the eight other papers are all 3+1 NR studies of inflation from inhomogeneous
    initial conditions. 2304.12150 reaches the opposite conclusion (inflation fails its tests)
    with a tetrad code; the list carries no claim about conclusions, so CONFIRMED for all eight.
    [Refuted if one of them is not about initial conditions of inflation.]
P3. Line 191, "NR implementation of stochastic inflation": 2512.14649 is the implementation;
    2401.08530 is the formulation (stochastic sources for ADM/BSSN, validated in uniform-field
    gauge in the long-wavelength limit, not an NR run); 2610.32592 is a PhD thesis that
    contains both. CONFIRMED (precision). [Refuted if 2401.08530 reports 3+1 NR simulations.]
P4. Line 192, slow contraction and bounces: all eight are numerical (NR or nonperturbative)
    studies of ekpyrotic/slow contraction or nonsingular bounces; 2206.08466 is black holes
    through a bounce. CONFIRMED. [Refuted if one is not about contraction or a bounce.]
P5. Line 193, preheating and oscillons: all six are GR simulations of preheating; 2311.01504
    is gauge preheating (pseudoscalar + gauge fields, so not only scalar fields). CONFIRMED,
    at most a precision for 2311.01504. [Refuted if one is not a GR preheating study.]
P6. Line 194, bubble collisions (1112.4487, 1312.1357: 1+1 with hyperbolic symmetry) and
    cosmic strings (1808.06678, 2002.05177: Abelian Higgs loops in 3+1 NR). CONFIRMED.
P7. Line 219, review 2006.16182 covers EMD and microhalos: CONFIRMED. Microhalo papers:
    1106.0536 (enhanced perturbations, microhalos) CONFIRMED; 1311.4034 (structures during
    EMD, survival conditional) CONFIRMED (precision); 1405.7373 finds that in moduli scenarios
    free streaming or kinetic decoupling can erase the enhancement, so it does not support
    "form microhalos" as written: 60 per cent CORRECTED or precision. 2107.10293 (early halos
    and their disruption at reheating) CONFIRMED. Inflaton-halo papers 2011.13333,
    1911.01661, 2110.15109, 1909.11678: CONFIRMED (1909.11678 and 1911.01661 use
    Schrodinger-Poisson / analogy to ultralight axions rather than "halos" as N-body objects).
    [Refuted if a paper is about something else.]
P8. Line 220, "N-body simulations (all Newtonian or semi-relativistic) [VERIFIED]":
    2306.14961 first N-body of formation and evaporation of EMDE halos (gravitational heating):
    CONFIRMED. 2212.00425 N-body + GW from inflaton-halo formation and tidal interactions:
    CONFIRMED. 2312.12499 hybrid N-body + lattice with decay of the metastable species into
    radiation; nonlinearity enhances the GW "significantly": CONFIRMED (precision: the
    enhancement holds up to frequencies of the inverse light-crossing time of the largest
    halos; a fully relativistic treatment is needed beyond). 2403.15126: N-body for the violent
    relaxation stage, pancake treated semi-analytically: CONFIRMED (precision) with 50 per cent.
    2605.04487: semirelativistic N-body, Zel'dovich-deformed homogeneous sphere in EdS,
    quadrupole GW, fitting and Zel'dovich estimates miss post-shell-crossing evolution,
    "nu ≃ 3": CONFIRMED (precision: nu ≃ 3 for the peak-statistics averages at the variances
    considered; a larger variance enhances the signal). [Refuted if a paper's gravity is fully
    relativistic, or a number differs.]
P9. Line 221: 2109.01398 a SIGW review: CONFIRMED. Transition speed: 1904.12878 (gradual),
    1904.12879 (sudden), 2311.12340 (interpolating): CONFIRMED; 2410.17291 treats onset and end
    of EMD from spectator fields: CONFIRMED (precision) with 50 per cent. Gauge dependence
    "sharpest in a matter-dominated era": 1704.03500 and 2009.11081 are about MD explicitly;
    1912.00785 shows gauge independence in RD and says MD differs; 2012.14016 says a particular
    dust-era solution can be gauged away; 1911.09689 is general. CONFIRMED (precision): the
    papers support that the MD case is where the induced tensor depends on the gauge while the
    source is active, but several of them argue that the observable late-time spectrum is gauge
    independent. 2610.08045: secular growth of third-order SIGW in MD (Omega^(3) ∝ x^6): CONFIRMED,
    and the label "[title only verified]" can become [VERIFIED]. [Refuted if the kernels do not
    grow secularly.]
P10. Line 222: 1907.08129 is N-body of PBHs as (part of) the dark matter in Lambda-PBH
    cosmologies, from deep in the radiation era to z = 99 — not a black-hole-dominated EARLY
    matter era. CORRECTED with 70 per cent. [Refuted if it simulates a PBH-dominated era before
    BBN.] 2010.11573 and 2012.08151: GWs induced by the Poisson density fluctuations of a PBH
    gas that dominates and then evaporates: CONFIRMED. 2003.10455: induced GWs from
    (inflationary) scalar perturbations enhanced by the sudden reheating of PBH evaporation,
    not GWs "from a gas of black holes": CONFIRMED (precision) with 60 per cent.
    2505.21885 [VERIFIED]: "up to two orders of magnitude" growth, linear perturbation theory,
    two peaks: CONFIRMED (precision): the high-frequency peak comes from PBH formation in the
    radiation era before the EMD and the low-frequency peak from the sudden EMD-to-RD transition,
    so the double peak is not a result of the accretion; and the EMD is not dominated by the
    black holes (60 per cent). [Refuted if the paper's EMD is driven by the PBHs.]

Tally prediction: about 60 rows, 0 NOT FOUND (all sources present), 1 to 3 CORRECTED
(1907.08129 most likely; 1405.7373, 2505.21885 possible), 10 to 15 CONFIRMED (precision).

## Entry 2 (2026-11-19 07:06 PST): source pass, outcomes of P1-P10, predictions of the two runs

Searches: `specs/l190.txt` ... `specs/l222.txt` and `specs/followup.txt` with `scripts/locate.py`
(outputs `scratch/kb/tmp/s34_36/hits_*.txt`), plus direct reads of the cited line ranges. One
INSPIRE query for the word "Latest" on line 190: `refersto:arxiv:2512.13673` was NOT understood
by INSPIRE (25291 hits, unrelated recent records; `kb-data/meta/inspire/query/8f96c307305cd2fa.json`;
kept on record, not used); `refersto:recid:3093098` (the INSPIRE record of 2512.13673) gave 2
citing papers (`kb-data/meta/inspire/query/48e651357ea82ee5.json`), of which 2607.06441 (posted
2026-07-07, already in the store) is a later numerical-relativity study of starting inflation.

Outcomes:
- P1 partly refuted, in the direction of a correction. The numbers 0.02 m_P and 10^-6 are in the
  abstract (`2512.13673/v1/src/main.tex:80`), with the 100-e-fold assumption and the lower-bound
  reading as predicted. But the body gives r_crit ≈ 5.6e-6 (out-of-phase; :114, :238, :309),
  8.7e-6 (in-phase; :238, :276) and 4.0e-6 (gradient only; :305): the abstract's "≈ 10^-6" is a
  rounding of 5.6e-6, which on a log scale lies nearer 10^-5. Verdict CORRECTED (not just a
  precision). New observation: :276 pairs mu_crit = 0.025, 0.020 (in-phase, out-of-phase,
  "respectively") with r_crit = 5.6e-6, 8.7e-6, the reverse of what Eq. (r) (:135) and the
  caption (:238) give. Tested in run 1 below. "Latest result" is out of date: 2607.06441.
- P2 confirmed: eight inflation-initial-condition studies; 2304.12150 concludes that inflation
  fails (:103, :378).
- P3 confirmed: 2401.08530 is the formulation; its own simulations are long-wavelength
  Stratonovich paths in Mathematica (:836, :879 "we don't need a full Numerical Relativity
  code"); 2512.14649 implements it in GRTeclyn (:480); 2610.32592 is a thesis (`conclusion.tex:8`).
- P4, P5, P6 confirmed (no correction); 2311.01504 is gauge preheating with a pseudoscalar
  and a U(1) field (:98, :144), as predicted.
- P7: 1405.7373 CORRECTED (predicted 60 per cent): its conclusion is that in the moduli
  scenarios free streaming or kinetic decoupling erases the EMD enhancement (`ver2.tex:141,
  476, 508`); it is a counter-example to microhalo formation, not evidence for it. The others
  confirmed, 1311.4034 with the predicted precision (survival needs a nearly degenerate daughter,
  `structure-articlev3jhep.tex:124, 174`).
- P8 confirmed, with the predicted precisions: 2312.12499 finds the enhancement at frequencies
  above the reheat-scale peak, not at the peak (`main.tex:209, 216`), and cautions above the
  inverse light-crossing time (:113, :235); 2403.15126 runs Aarseth's Newtonian Nbody2 on an
  isolated cloud after turnaround (`pII_GW_Vir_C2_Arx.tex:261, 611`); 2605.04487 nu ≃ 3 is
  nu_peak ≃ 2.85 and 2.98 for sigma = 0.01 and 0.1 (`main_v3.tex:2496, 2504`), and the
  "fitting-based procedure" it criticises is that of 2403.15126 (cite key
  DalianisKouvaris2024, :2708) — the paper the brief lists one sentence earlier.
- P9 confirmed with precision: 1912.00785 (:266-269), 2012.14016 (:332-346), 1911.09689 (:1414)
  support "sharpest in MD"; 2009.11081 finds the energy density of the oscillating SIGW gauge
  independent in all seven gauges (:42, :709-712). 2410.17291 treats onset and end of EMD
  without the instantaneous approximation but does not vary the transition speed (:137, :203,
  :566-569). 2610.08045: secular growth confirmed (:80); label can become [VERIFIED].
- P10 confirmed for 1907.08129 (CORRECTED: Lambda-PBH cosmologies, PBHs as (part of) the cold
  dark matter, N-body from deep in the radiation era to z = 99, `ms.tex:43-46`). 2505.21885
  CORRECTED rather than a precision: its EMD is driven by a bosonic field phi with the PBHs
  subdominant (`main.tex:125, 147`), and the double peak is SIGW from the PBH-forming peak
  plus the sudden EMD-to-RD transition (:181, :357), not a result of the accretion. 2003.10455
  precision as predicted (:150-151, :219-226).

Tally so far (before writing CHECK.md): no NOT FOUND, 4 CORRECTED (2512.13673 r value, 1405.7373,
1907.08129, 2505.21885) against the predicted 1 to 3.

Predictions for the runs (written before they run):

P11 (run 1, `scripts/r_of_mu.py`, analysis of the printed numbers of 2512.13673): Eq. (r),
    r = 16 pi mu^2 / (m_P^2 N*^2) with N* = 60 (:135, :138), reproduces every printed (mu, r) pair
    of the paper to within 3 per cent (two-digit rounding) — :114, :238, :273, :287/:305, :301,
    :309 — EXCEPT the two pairs of :276 read with "respectively", which miss by 36 and 56 per
    cent; read swapped they agree. log10(5.6e-6) = -5.25, nearer -5 than -6. Every number the
    script quotes is also found as text on its stated line (locator check). [Refuted if a pair
    other than :276 misses by more than 3 per cent, if :276 agrees as printed, or if a number is
    not on its line.]
P12 (run 2, `scripts/fig_verdicts.py`, tally): the header totals of CHECK.md equal the tally of
    the verdict column; every TeX locator names an existing file and a line inside it; every
    metadata locator names an existing file. [Refuted by any problem listed by the script.]

## Entry 3 (2026-11-19 07:15 PST): outcome of run 1; CHECK.md written

Run kb-20261119-150703-95bba8b (`scripts/r_of_mu.py`, processors, one core, seconds; output
`scratch/kb/kb-20261119-150703-95bba8b/`): completed, exit 0, no locator problem (every quoted mu
and r string is on its stated line of `2512.13673/v1/src/main.tex`).
- P11 CONFIRMED for every pair it named: :114, :238 (both), :273 (both ends), :301 (both ends),
  :305 and :309 agree with Eq. (r) at N* = 60 within 1.5 per cent (largest: :301 upper end,
  -1.5 per cent, two-digit rounding of 2.234e-5); :276 as printed misses by -35.8 and +55.8 per
  cent and agrees to 0.3 per cent when swapped. log10(5.6e-6) = -5.252.
- Not in P11's list, reported as well: the abstract pair (:80, mu = 0.02, r ≈ 1e-6) misses by
  -82 per cent, the factor 5.6 already noted in entry 2.
- Figure `fig_r_of_mu.png` looked at: left, Eq. (r) as a line with the printed pairs (circles
  on the line; the two :276 crosses off it on either side; the abstract cross on the dashed
  10^-6 line); right, the relative differences, only abs, L276a, L276b outside the grey 3 per
  cent band. It shows what the numbers say.

CHECK.md written: 66 rows (45 CONFIRMED, 17 CONFIRMED (precision), 4 CORRECTED, 0 NOT FOUND) and
the line-188 judgement without verdict. Against entry 1: no NOT FOUND as predicted; 4 corrections
against the predicted 1 to 3 (2512.13673 r value and 2505.21885 were predicted as precisions);
17 precisions against the predicted 10 to 15. `scripts/fig_verdicts.py` adapted (label
"[title only verified]", automatic axis limits); its prediction is P12 (entry 2).
