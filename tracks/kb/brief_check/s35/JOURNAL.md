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

## Entry 2 (2026-11-19 07:18 PST): what the TeX sources show, in short; prediction for run 1

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

## Entry 3 (2026-11-19 07:22 PST): outcome of run 1 and of predictions P1-P15

Run `kb-20261119-151804-271859c` (completed, exit 0; processors, one core, seconds): steps ratio
93.81, step-size ratio 200.0, abundance ratio 19.44, hhat(0.2, 0) = 0.4517 (0.4221 with the
other convention for E), dust ratio at least 2.10 (2.25), particle ratio 9.03 to 10.04 (8.44 to
9.38). All inside the preregistered bands: prediction CONFIRMED. Figure
`scratch/kb/kb-20261119-151804-271859c/fig_numbers.png` looked at: the analytic line rises from
0.03 at e = 0.005 to 0.48 at e = 1/3, the dust marker sits at 0.95 above it (x2.1), the particle
bracket at 0.045-0.05 below it (/9 to /10); stated and recomputed ratios coincide on the right.
One defect of the figure: the legend said "as stated (abstract)", but the 200 and the 19 are
stated in the bodies (PRD.tex:402, main.tex:659); label changed to "as stated in the paper" and
the figure rerun (entry 4).

Outcomes of the predictions of entry 1 (rows of CHECK.md in brackets):

- P1 CONFIRMED [1-8]: all eight are spherical threshold, critical-scaling or profile studies or
  reviews; 2211.05767 is a general review (precision).
- P2 CONFIRMED [9-12]: three precisions as predicted (2403.11147 spin study with w = 1/3, 1/5;
  2410.03452 also w = 1/10; 2410.03451 a mass-function letter on the companion's thresholds).
- P3 CONFIRMED [13-16], with one precision I did not predict: the 3+1 runs of 2608.13206 are of a
  spherical Gaussian profile only (PRD.tex:507). The Zel'dovich-Novikov law is a two-parameter
  late-time fit (F, M_inf), F foliation-dependent, as predicted.
- P4 CONFIRMED [17-18]: one author; "diagnostic" and "empirical indicator", 0.55-0.56, no exact
  multiplicity criterion.
- P5 CONFIRMED [19-20]: toy model (constant over-density inside a radius), as predicted.
- P6 CONFIRMED [21].
- P7 CONFIRMED [22-24]: the statement is in 1609.01588 (Jeans-criterion threshold tends to zero
  as w goes to 0; delta proportional to a), 2211.13950 and 1810.03490; the [BACKGROUND] label
  can become [VERIFIED].
- P8 CONFIRMED [25-28]: near-extremal spins only for a long matter era; most frequent spin 1 for
  sigma_H ≲ 0.04.
- P9 CONFIRMED [30-31] with the precision predicted ("for a realistic cosmic abundance",
  zeta_rms ~ 0.1).
- P10 CONFIRMED (the predicted correction) [33]: sigma_j^2 = ∫ d ln k k^(2j) P(k)
  (main.tex:767), so sigma_h^* is an r.m.s. amplitude and beta ∝ sigma^5 = variance^(5/2); the
  paper itself calls sigma_0 "the variance" (main.tex:322, 775). The 19 is 1.08/0.05556 (run 1).
- P11 CONFIRMED with a precision I did not predict [35]: the near-extremal estimate was revised by
  overlapping authors (2508.10070 includes Harada, Kohri, Yoo), and 2609.14218 sums up "the
  conclusion has evolved" towards negligible spin effects; the "disagreement" is a revision.
- P12 CONFIRMED [37-40], with the precision that there are two fields (massive phi as the
  matter, massless xi for the perturbation).
- P13 CONFIRMED (precision) [41-42]: the source says "several e-folds" and argues it; the
  simulations follow at most a few e-folds after formation (the 50 per cent case went to
  "precision").
- P14 CONFIRMED (precision) [43-47]: the earlier estimate is the Zel'dovich-plus-hoop criterion of
  Harada et al. 2016; both factors are the abstract's and hold for the one body case e = 0.2
  (run 1); and a precision I did not predict: the particle threshold comes with "a big caveat",
  significantly violated constraints once particles cross (MDPBH.tex:1148-1149), and the authors
  conclude "a large theoretical uncertainty" (MDPBH.tex:1209).
- P15 CONFIRMED [48-52].
- Overall prediction (0-2 CORRECTED, 6-12 precisions, none NOT FOUND): 1 CORRECTED (inside),
  18 precisions (above the predicted 6-12: I underestimated how many statements are abstract
  wording that the bodies qualify), 0 NOT FOUND (inside).

## Entry 4 (2026-11-19 07:22 PST): predictions for run 2 (tally) and run 3 (figure rerun)

Run 2, `scripts/fig_verdicts.py` (copy of the s33 script, now also checking run-id locators
against `tracks/kb/runs/<id>/manifest.json`): predicts 52 rows numbered 1-52, tally 33 CONFIRMED,
18 CONFIRMED (precision), 1 CORRECTED, 0 NOT FOUND equal to the header, every locator span valid
(file exists, highest line within the file), exit 0. By label: [VERIFIED] 31 rows, [BACKGROUND] 4,
unlabelled 17. Refuted by any problem line or exit 1 (then the row is fixed and the run repeated,
the failed run kept on record).

Run 3, `scripts/check_numbers.py` after the legend fix: numbers.json identical in every number
to run 1 (the script is deterministic, only a label changed); the figure differs only in the
legend text.

## Entry 5 (2026-11-19 07:24 PST): outcomes of runs 2 and 3; an addition to row 35; prediction for run 4

Run 2, `kb-20261119-152248-b27df46` (completed, exit 0): 52 rows, tally 33 / 18 / 1 / 0 equal to
the header, 68 locator spans checked, no problem. Prediction CONFIRMED, except one sub-prediction
that FAILED: I predicted 31 [VERIFIED], 4 [BACKGROUND], 17 unlabelled rows; the run counts 35, 4
and 13. Recount by hand: [VERIFIED] rows 9-21, 29-34, 37-52 = 13 + 6 + 16 = 35; unlabelled rows
1-8, 25, 27, 28, 35, 36 = 13. The run is right and my prediction was a miscount; CHECK.md is not
changed by it. Figure `scratch/kb/kb-20261119-152248-b27df46/fig_verdicts.png` looked at: the
one red segment is on line 208, the precisions cluster on lines 200, 201 and 214, line 215 is all
blue; by label, [VERIFIED] 19 / 15 / 1, [BACKGROUND] 3 / 1, no label 11 / 2.

Run 3, `kb-20261119-152254-b4836fb` (completed): numbers.json identical to run 1 (compared with
json equality); the figure shows the new legend text "as stated in the paper", otherwise the
same. Prediction CONFIRMED.

Addition after the runs: arXiv:2409.00435 (Saito, Harada, Koga, Yoo), named by 2609.14218 as the
intermediate spin paper, is in the store and was read for row 35: it does not find small spins
but "substantial values of PBH spins" (main.tex:65). So the sequence is near-extremal (2017),
substantial (2024), very small for small sigma (2025, same group), and very small independently
(2507.18312). My outcome note for P11 in entry 3 ("revised towards small spins") was right for
2025 but skipped the 2024 step; row 35 of CHECK.md and row s35.6 of ERRATA_ROWS.md now say it.
The same paper writes sigma_H as "the square root of the variance" (main.tex:62), the right
wording that 2508.10070 drops (row s35.1, section 5).

Prediction for run 4 (tally after the change of row 35): 52 rows, tally unchanged (33 / 18 / 1 /
0), 69 locator spans (one span added to row 35), no problem, exit 0.

## Entry 6 (2026-11-19 07:25 PST): outcome of run 4; package closed

Run 4, `kb-20261119-152449-e225d94` (completed, exit 0): 52 rows, tally 33 / 18 / 1 / 0, 69
locator spans, no problem. Prediction CONFIRMED. Figure
`scratch/kb/kb-20261119-152449-e225d94/fig_verdicts.png` looked at: identical in content to that
of run 2. ERRATA_ROWS.md now names run 4 as the reference tally run. README.md written
(contents, results, rerun, runs, requests). Nothing is pending: no card job, no fetch, no
database write.
