# Journal of work package s5_s6 (brief lines 406-444 and 493-553)

Owner: kb (helper). Worktree `wt/kb-brief`, branch `kb/brief-check`. Times are local (PST)
from `date`.

## Entry 1 (2026-11-19 07:34 PST): set-up, metadata pass, predictions

Done before this entry: merged main into the worktree (already up to date), read CLAUDE.md, the
charter to "Owners", decisions 0010, 0016, 0017, `coord/BRIEF_ERRATA.md`, brief lines 30-68,
406-444 (problems S5 to S10) and 493-553 (section 6, directions M1 to M12).

Rows of `coord/BRIEF_ERRATA.md` that touch these lines and are not repeated here: 1.8 (line 520,
2602.17487 has no collision operator), 3.7 (line 134: NRPIC keeps one global time step; the same
question is the [TO VERIFY] of line 426), 4.3 (line 546, the Fourier-space noise of M11 is
superseded by core's implementation), 1.14 and section 5 (1305.2619 is Schwarzschild only, and
its defects; cited again on line 550).

Overlap: the package `tracks/kb/brief_check/novelty/` of the same worktree (another helper, its
JOURNAL entry 1 at 07:30) covers brief lines 394-444 with novelty searches, so lines 406-444 are
checked twice. I check them anyway, independently (a second check of a statement that matters),
keep my novelty searches short, and leave the full literature search of S5 and S7 to that
package. Lines 493-553 are mine alone.

All 90 papers cited in lines 406-444 and 493-553 are in the store with TeX source
(`/data/haiyangw/nrpic/kb-data/raw/arxiv/<key>/<v>/src`) and an arxiv-api record; nothing needs
fetching for the citations. Titles, authors and abstracts were dumped with
`scripts/meta_dump.py` (copy of the s35 script) into `scratch/kb/tmp/s5_s6/meta_all.txt` and
read. The predictions below are written after that reading and before any check at the TeX
source. A CONFIRMED or CORRECTED verdict needs a TeX locator file:line (the abstract inside the
TeX counts; the metadata abstract alone does not).

Labelled statements in scope: L410 [BACKGROUND]; L414 [TO VERIFY]; L426 [VERIFIED] and
[TO VERIFY] (the latter answered by errata 3.7, not repeated); L437 [TO VERIFY]; L495 (all of
section 6 is [JUDGEMENT]); L512 [BACKGROUND], [VERIFIED] and [TO VERIFY]; L546 [JUDGEMENT] (not
checked: a recommendation). Unlabelled specific claims about cited papers are checked too and
marked "(unl.)", as the sibling packages do; in section 6 these sit under the blanket
[JUDGEMENT] of line 495, but each still says what a paper does.

Predictions (what would refute each in brackets):

P1. L410 [BACKGROUND]. The neutrino share of the radiation energy density is 0.405 after e+e-
    annihilation and 0.488 before (g-counting with the (4/11)^(1/3) temperature ratio), so
    "forty to fifty per cent" holds; decoupling near 1 MeV; a source formula gives a horizon
    mass at T = 1 MeV between 3e4 and 3e5 solar masses. CONFIRMED.
    [Refuted if a source puts M_H(1 MeV) outside [3e4, 3e5] M_sun or the share outside
    [0.35, 0.55].]
P2. L410 (unl.). 1609.02245 and 1202.3848 are supermassive-PBH papers (1202.3848 at masses "of
    the order of 1e5 M_sun", so "above this mass" is loose); 2209.02735 is about the cut-off of
    the matter power spectrum set by relativistic hidden-sector particles in an early matter
    era, not about PBH formation (precision); 1906.08217 changes the threshold through the
    equation of state with a fluid threshold (CONFIRMED).
P3. L414 [TO VERIFY]. A short INSPIRE search finds no full-GR kinetic calculation of PBH
    formation with a free-streaming component. [Refuted by one such paper.]
P4. L416 (unl.). 2409.10384 is AthenaK's GRMHD in dynamical spacetimes. CONFIRMED.
P5. L426 [VERIFIED]. The main text of 2409.16053 says that all levels advance with one time step
    (no subcycling in time). CONFIRMED. [Refuted if it describes subcycling or local time
    stepping, or says nothing.]
P6. L426 (unl.). c/v = 1e2 to 1e3 for v = 300 to 3000 km/s: arithmetic of a [JUDGEMENT]; no
    paper locator expected.
P7. L428 (unl.). All ten key references are about backreaction, timescape, relativistic
    simulations or light propagation in them; 2406.05048 and 2412.15143 are supernova analyses
    that test timescape (precision).
P8. L434 (unl.) "All existing proofs assume U(1) symmetry; the 3+1 case without symmetry is
    open". I expect CORRECTED: I recall a 2024 proof of Burnett's conjecture in generalized wave
    coordinates without symmetry (Huneau and Luk), to be found by an INSPIRE query.
    [Refuted if no such paper is found.]
P9. L435 (unl.). 2509.19769 (GW turbulence), 1011.4920 (traceless effective stress), 1505.02959
    and 1801.08362 (full-NR GW cosmology) CONFIRMED.
P10. L437 [TO VERIFY] "No numerical work was found". CONFIRMED (precision) at best: 1505.02959,
    which the brief itself cites, tests Isaacson's averaged radiation-fluid behaviour of nonlinear
    standing waves numerically in full NR; no comparison with massless Vlasov expected.
    [Refuted if 1505.02959 does not compare with a radiation fluid.]
P11. L441 S8. gr-qc/0512031 states that Vlasov matter gives different dynamics from perfect
    fluids (CONFIRMED); 0904.1546 and 2010.01399 are vacuum spike simulations (CONFIRMED).
P12. L442 S9. 1611.07906 and 1901.04498 spindle collapse of collisionless particles; 2402.10190
    (proof) and 2511.20567 (numerics) Einstein-Maxwell-Vlasov extremal thresholds. CONFIRMED.
P13. L443 S10. 1904.12879 sudden transition enhances the induced GWs (precision: the comparison
    with a gradual transition is a companion paper); 2003.10455 sudden reheating by PBH
    evaporation; 2312.12499 hybrid N-body plus lattice; 2306.14961 N-body only (precision);
    1904.11773 relativistic at linear order only (precision).
P14. L499 M1. 2508.20606 curved geometry; 1305.5576 states an integrability condition on the
    torus (CONFIRMED), 2207.03125 perhaps only implicitly; astro-ph/0602159 treats T^1 x R^2,
    not the three-torus (precision); 2210.11426 is observational (precision).
P15. L500. 1704.04307, 2610.23218, 2207.06376, gr-qc/0210050, 1809.07010, 2001.00394 CONFIRMED.
    "Comoving synchronous gauge converges poorly with particles (1810.05203)": I expect the
    paper to report a problem of synchronous gauge with collisionless matter; CONFIRMED
    (precision). [Refuted if it does not discuss synchronous gauge with particles.]
P16. L501. CTTK and GRTresna are general constraint solvers (scalar fields, fluids), not made
    for particle distributions (precision); 1503.03934, 1702.03221, 2110.11249, 2001.07968
    CONFIRMED; East et al. set particle masses from the constraint solve (CONFIRMED).
P17. L505-508 M2. 2605.15260 high-order shapes (CONFIRMED; filtering perhaps not); sheet papers
    CONFIRMED, with the precision that after shell crossing the tessellation stays accurate only
    with refinement (1501.01959) or a hybrid (1909.00008); "Giblin et al. used a sheet
    representation in BSSN (1810.05203)" CONFIRMED [refuted if no sheet or tetrahedra appear in
    1810.05203]; 2010.07321 delta-f CONFIRMED; discreteness papers CONFIRMED (1801.03906 is about
    neutrino shot noise, precision).
P18. L512 M3. [BACKGROUND] Gauss law from charge-conserving deposition: CONFIRMED at a TeX
    locator in the store (GEMPIC or Entity). [VERIFIED] dGREM suited to Yee grids and
    constrained transport: CONFIRMED. [TO VERIFY] source terms of the matter equation:
    CONFIRMED; hyperbolicity: partly answered by 2211.13659 (symmetric hyperbolic in vacuum for
    the 3+1 pure-tetrad TEGR system).
P19. L516 M4. 1910.12152, 0807.0734, 1801.02378 CONFIRMED; GEMPIC conserves energy well over long
    times and its Casimirs (Gauss law, div B) CONFIRMED.
P20. L524-526 M6. 1801.02378 and 1208.3927 treat null geodesics (CONFIRMED). "Particles + puncture
    black holes: already a capability of Wu and Most": uncertain; I predict the paper has a
    black hole together with particles (CONFIRMED, precision on how it is set up).
P21. L530 M7. The three ray-tracing papers are post-processing tools, none on the fly
    (CONFIRMED, precision).
P22. L534 M8. EBWeyl, aurel, 2306.11810, 2609.03051, 2111.09163, 2408.03049, 2409.00024
    CONFIRMED; BHaHAHA is a general horizon finder (precision); 2304.13284 treats spherical
    symmetry, so "non-spherical" does not fit it (CORRECTED or precision).
P23. L542 M10. 1101.3555, 1505.04756, 2404.02783 CONFIRMED; 1711.06681 is a comparison, not a
    dictionary (precision); 2112.10567 CONFIRMED; 2101.12149 is GPU porting (precision); cyclic
    zoom is implemented in AthenaK (CONFIRMED).
P24. L550 M12. 0710.0879, 0711.1165, 1004.1353 CONFIRMED (1004.1353 compares accurate and
    approximate three-puncture data); upstream AthenaK has one- and two-puncture generators
    (CONFIRMED); conformally flat data for three or more punctures exist in the literature and in
    core-v0.3 (superseded as "new").

Runs planned (processors, one core, seconds):
R1. `scripts/check_numbers.py`: neutrino share of the radiation energy density against
    temperature (g-counting) and horizon mass against temperature from the source formula
    found; figure with the brief's bands. Prediction: share 0.405 and 0.488 inside [0.40, 0.50];
    M_H(1 MeV) inside [3e4, 3e5] M_sun. Refuted outside these.
R2. `scripts/fig_verdicts.py`: tally of CHECK.md against its header, every TeX locator exists
    and its line range lies inside the file. Prediction: no problem. Refuted by any mismatch.

## Entry 2 (2026-11-19 07:46 PST): outcome of R1, first try; prediction for the rerun

Run `kb-20261119-154310-89ca8fb` (processors, one core, seconds) ended with exit 1. The
preregistered numbers held: neutrino share 0.4884 before e+e- annihilation (21/4 over 10.75),
0.40523 after it from (4/11)^(4/3) (equal to f_nu(0) = 0.40523 of astro-ph/0306304
`main.tex:328-329` to 5 digits), the curve for decoupling at 1 MeV between 0.411 and 0.4915,
all inside [0.40, 0.50]; horizon mass at T = 1 MeV 1.498e5 M_sun from 2002.12778
(`CKSY2021.tex:276-291`), 1.499e5 from the Friedmann equation, inside [3e4, 3e5]. P1 holds.
What failed is a sanity check I had put into the script without writing it here: the final
T_nu/T of the 1 MeV curve is 0.7180, not (4/11)^(1/3) = 0.7138 within 2e-3. Figure
`fig_numbers.png` looked at: panel (a) shows the step from 0.488 to 0.41, a small bump to 0.49
near 1 MeV, and the two text labels outside the axes; (b) and (c) as expected; the formula of
astro-ph/0608642 lies a factor 15 below the other two.

Suspected cause (not yet tested): with instantaneous decoupling at 1 MeV the electrons and
positrons are already partly non-relativistic (m_e/T = 0.51), so they hold less entropy at
decoupling and heat the photons less afterwards; the check belongs to decoupling well above
m_e. Prediction for the rerun (sanity check moved to decoupling at 10 MeV, labels moved inside):
T_nu/T at 10 MeV decoupling within 2e-3 of 0.7138; the 2 MeV curve between 0.7138 and 0.7180;
all other numbers unchanged. Refuted if the 10 MeV case also misses 0.7138 (then the integrals
are wrong).
