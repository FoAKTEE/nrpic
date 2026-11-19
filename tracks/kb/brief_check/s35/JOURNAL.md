# Journal of work package s35 (brief lines 196-216, section 3.5)

Owner: kb (helper). Worktree `wt/kb-brief`, branch `kb/brief-check`.

## Entry 1 (2026-11-19 07:13 PST): set-up, metadata pass, predictions

Done before this entry: merged main into the worktree (already up to date), read CLAUDE.md,
the charter to "Owners", decisions 0010, 0016, 0017, `coord/BRIEF_ERRATA.md` (no row of it is
on lines 196-216, so nothing here repeats it), brief lines 30-68 and 186-223. Package s34_36
of the same worktree covers lines 186-195 and 217-223; it does not touch 196-216.

All 26 papers cited in lines 196-216 are in the store
(`/data/haiyangw/nrpic/kb-data/raw/arxiv/<id>/<v>/src`; gr-qc/9905064 as `gr-qc_9905064`,
astro-ph/9709072 as `astro-ph_9709072`), each with an arxiv-api and an INSPIRE record, so no
fetch is needed. Titles, authors, journal references and abstracts were dumped with
`scripts/meta_dump.py` (copy of the s33 script) into `scratch/kb/tmp/s35/meta{1,2,3}.txt` and
read. The predictions below are written after that reading and before any check at the TeX
source. A CONFIRMED or CORRECTED verdict needs a TeX locator file:line (the abstract inside the
TeX counts; the metadata abstract alone does not).

Predictions (what would refute each is in brackets):

P1. Line 198 (no label): the eight papers are all spherically symmetric threshold, critical
    scaling or profile studies or reviews of them. gr-qc/9905064 is Shibata-Sasaki 1999 (CMC
    formulation, profile dependence of the threshold), astro-ph/9709072 Niemeyer-Jedamzik
    (critical scaling and the mass function), 1201.2379 Musco-Miller (critical behaviour,
    self-similarity), 1309.4201 Harada-Yoo-Kohri (analytic threshold), 1809.02127 Musco (shape
    dependence), 1907.13311 Escriva-Germani-Sheth (universal threshold); reviews 2111.12693
    (spherical PBH formation) and 2211.05767 (a general PBH book chapter, formation one part
    of it). CONFIRMED, with the precision that 2211.05767 is a general review.
    [Refuted if one of the eight is not about spherical formation or is not a review.]
P2. Line 200, "Non-spherical and ellipsoidal collapse" [VERIFIED]: all four are 3+1
    simulations or built on them. Precisions expected: 2403.11147 is about the spin from a
    misaligned deformation tensor (w = 1/3 and 1/5), 2410.03451 is a mass-function letter
    built on the simulations of 2410.03452, and 2410.03452 also runs w = 1/10, i.e. not
    radiation only. CONFIRMED (precision). [Refuted if one is not a 3+1 nonspherical study.]
P3. Line 201, 2608.13206 [VERIFIED]: GRChombo with flux-conservative relativistic
    hydrodynamics, a cosmologically scaled Gamma-driver with the cosmic-time step growing in
    proportion to the scale factor, a factor of about 94 fewer coarse-level advances "for a
    representative long-term simulation", late-time growth "fitted" to the Zel'dovich-Novikov
    law. CONFIRMED, possibly with the precision that the accretion law is a fit with a free
    efficiency. [Refuted if the factor differs or the body reports a deviation from the law.]
P4. Line 202, 2609.03051 [VERIFIED]: three outcomes CONFIRMED; the paper has one author
    (Escriva), not "the authors"; the Hawking-mass quantity is called a "diagnostic" and an
    "empirical indicator" with a transition near 0.56, not a derived criterion. CONFIRMED
    (precision). [Refuted if the quantity is not built on the Hawking mass.]
P5. Line 203, 2509.26470 [VERIFIED]: non-existence and non-uniqueness, strong- and weak-field
    branches, initial guess deciding the branch: CONFIRMED, with the precision that this is
    shown in a toy model (a model used before in asymptotically flat space) for given
    over-density and mean curvature, not in a PBH simulation. [Refuted if the branches are
    found in a full 3D solve of PBH data.]
P6. Line 203, 2607.21308 [VERIFIED]: parabolic-hyperbolic formulation, no boundary conditions
    needed, perfect-fluid anisotropic perturbations on flat FLRW. CONFIRMED.
P7. Line 205 [BACKGROUND]: zero Jeans length without pressure, growth of perturbations after
    horizon entry (delta proportional to a), and the four effects deciding black-hole
    formation are stated in the introductions of 1609.01588, 1707.03595, 1810.03490 or
    2211.13950. CONFIRMED at a TeX locator; label can become [VERIFIED].
    [Refuted if no source in the store states the zero Jeans length or the growth.]
P8. Line 207: 1609.01588 hoop criterion (with Zel'dovich approximation and Doroshkevich's
    distribution), 1810.03490 inhomogeneity, 2211.13950 velocity dispersion: CONFIRMED.
    1707.03595 [BACKGROUND] near-extremal spins: CONFIRMED (precision): only if the matter era
    lasts long enough, the smaller sigma_H the closer to a* = 1; a finite duration weakens it.
P9. Line 208, 2507.18312 [VERIFIED]: threshold zeta_rms^(2/5) (top hat, Harada et al.) ->
    zeta_rms^(1/10) "for a realistic cosmic abundance", spin a_rms ~ zeta_rms^(7/4) << 1.
    CONFIRMED (precision: the 1/10 holds for a realistic abundance and needs zeta_rms ~ 0.1).
    [Refuted if the exponents differ in the body.]
P10. Line 208, 2508.10070 [VERIFIED]: "abundance varies roughly as the fifth power of the
    variance at horizon entry". Prediction: sigma_h^* is a standard deviation (its square is
    the variance), so beta ~ sigma^5 = (variance)^(5/2): CORRECTED, probability 60 per cent.
    "about 19 times the earlier prediction" for a monochromatic spectrum: CONFIRMED.
    [Refuted (no correction) if sigma_h^* is defined as a variance.]
P11. Line 209 (no label): the spin disagreement (1707.03595 near-extremal; 2507.18312 and
    2508.10070 small) CONFIRMED from the same sources.
P12. Line 213, 2109.04896 [VERIFIED]: matter as a (massive, oscillating) scalar field; two
    mechanisms, direct collapse and post-collapse accretion; the latter without the hoop
    condition; formation time around a Hubble time. CONFIRMED. [Refuted if the matter is a
    dust fluid or the formation time differs.]
P13. Line 213, 2306.11810 [VERIFIED]: accretion of non-rotating matter lowers the spin; final
    spin negligible unless the matter era is short. CONFIRMED; whether "a few e-folds" is in
    the source: probability 50 per cent (the abstract says only "unless the matter era is
    short"). [Precision if the e-fold number is not in the source.]
P14. Line 214, 2609.14218 [VERIFIED]: triaxial data, dust crash unless the singularity is
    well inside the horizon, factor 2 for the dust fluid, particles do not crash, threshold
    an order of magnitude below the earlier analytic estimate. CONFIRMED; precision expected on
    which earlier estimate (Harada et al. 2016) and which amplitude measure.
    [Refuted if a number differs in the body.]
P15. Line 215, 2610.23218 [VERIFIED]: CONFIRMED as stated (abstract already matches).

Overall: of about 40 rows, 0 to 2 CORRECTED (P10 the most likely), 6 to 12 CONFIRMED
(precision), the rest CONFIRMED, none NOT FOUND (all sources are in the store).

## Entry 2 (2026-11-19 07:40 PST): what the TeX sources show, in short; prediction for run 1

All 26 papers were read at the passages found with `scripts/locate.py` (specs `specs/l198.txt`
to `specs/l215.txt`, outputs `scratch/kb/tmp/s35/loc_*.txt`) and around them. The outcomes per
prediction are in entry 4, after the numbers run, and the rows in CHECK.md.

Three statements carry numbers that can be recomputed from numbers printed in the bodies of the
papers (not only quoted from their abstracts). Script `scripts/check_numbers.py` transcribes the
inputs with their locators and recomputes:

- 2608.13206 (line 201): 102436 / 1092 coarse-level advances (PRD.tex:402) and the step growth
  0.520 / 2.60e-3 (same line).
- 2508.10070 (line 208): 1.08 (main.tex:657, beta/sigma_h^5 for a monochromatic spectrum) over
  0.05556 (1609.01588 apj_nonsphericalpbh.tex:764).
- 2609.14218 (line 214): the paper's analytic criterion mu > hhat(e,p) with aH = k/sqrt 6
  (MDPBH.tex:912-916, 987) at e = 0.2, p = 0, against the dust bound "breaks down before horizon
  formation for mu <= 0.95" (MDPBH.tex:1085-1086) and the particle bracket "apparent horizon for
  mu >= 0.05", none for mu <= 0.045 (MDPBH.tex:1101-1102). The argument of E is an eccentricity
  (modulus convention, scipy ellipe(k^2)); the other convention is printed as a bracket.

Prediction for run 1 (bands written into the script before the run; exit 1 outside them):
steps ratio in [90, 98] (expect 93.8); step-size ratio in [190, 210] (expect 200); abundance ratio
in [18, 21] (expect 19.4); hhat(0.2, 0) in [0.40, 0.47] (expect 0.452 by hand: 15/pi x 0.2/1.6^2 x
E(m = 0.75) = 1.211); dust ratio 0.95/hhat in [1.8, 2.5] (expect 2.1, "factor of 2" CONFIRMED);
particle ratio hhat/0.05 to hhat/0.045 in [8, 11.5] (expect 9.0 to 10.0, "order of magnitude"
CONFIRMED). Refuted if the dust ratio is below 1.5 or above 3, or the particle ratio below 5 or
above 20: then the abstract's "factor of 2" or "order of magnitude" does not describe the e = 0.2
case of the body and the brief rows 45 and 47 become CORRECTED or NOT FOUND for the body.
Figure: left, hhat(e,0) with the dust bound and the particle bracket at e = 0.2; right, stated
against recomputed ratios. I will look at the PNG before using any number.
